"""Бот важных новостей экономики РФ и Ленобласти — Yandex Cloud Function (Python 3.12).

Раз в час (таймер-триггер) функция читает RSS-ленты, отбирает свежие новости, просит YandexGPT
оценить их важность для бизнеса и присылает в Telegram только важные (оценка 4–5 из 5).
Ночью (00–08 МСК) не пишет: в 08:00 присылает важное за ночь.

Переменные окружения:
  BOT_TOKEN  — токен бота от @BotFather (обязательно)
  CHAT_IDS   — кому отправлять: ID через запятую (личные чаты и/или канал, например -1001234567890)
  FOLDER_ID  — ID каталога Yandex Cloud (для YandexGPT)
  SECRET     — любой длинный пароль: защищает служебные вызовы и вебхук
  MODEL      — по умолчанию yandexgpt-lite/latest (можно yandexgpt/latest — точнее, но дороже)
  MIN_SCORE  — порог важности, по умолчанию 4
  TG_API     — адрес Bot API или ретранслятора (если api.telegram.org недоступен из облака)
Функции нужен сервисный аккаунт с ролью ai.languageModels.user.
"""
import datetime as dt
import email.utils
import html
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

MSK = dt.timezone(dt.timedelta(hours=3))
UA = {"User-Agent": "Mozilla/5.0 (compatible; LenoblNewsBot/1.0)"}

# (название, url, регион по умолчанию, брать все новости или только по ключевым словам)
FEEDS = [
    ("Банк России", "https://www.cbr.ru/rss/eventrss", "РФ", True),
    ("Интерфакс", "https://www.interfax.ru/rss.asp", "РФ", False),
    ("ТАСС", "https://tass.ru/rss/v2.xml", "РФ", False),
    ("РИА Новости", "https://ria.ru/export/rss2/archive/index.xml", "РФ", False),
    ("РБК", "https://rssexport.rbc.ru/rbcnews/news/30/full.rss", "РФ", False),
    ("Коммерсантъ", "https://www.kommersant.ru/RSS/section-economics.xml", "РФ", True),
    ("Ведомости", "https://www.vedomosti.ru/rss/rubric/economics", "РФ", True),
    ("Правительство ЛО", "https://lenobl.ru/rss/", "ЛО", True),
    ("47news", "https://47news.ru/rss/", "ЛО", False),
]
ECON = re.compile(r"эконом|ставк|налог|бизнес|предпри|инфляц|рубл|курс|банк|инвест|ввп|бюджет|промышл|завод|производ|экспорт|импорт|"
                  r"санкц|\bмсп|закон|минфин|минэк|минпром|кредит|ипотек|\bцен[аыуе]\b|тариф|нефт|\bгаз|зарплат|занятост|субсид|льгот|"
                  r"ленобласт|ленинградск|дрозденко|аэрло|\bпорт[аыу]?\b|логист", re.I)
SKIP = re.compile(r"украин|всу\b|\bсво\b|беспилот|\bбпла|обстрел|удар[аы]? по|ракет|погиб|ранен|теракт|войн|фронт|армия|военн|нато|убийств|задержан|суд приговор|дтп|пожар", re.I)
LO = re.compile(r"ленобласт|ленинградск|дрозденко|аэрло|47 ?регион|гатчин|всеволожск|выборг|кириш|тихвин|луг[аи]|сосновый бор|"
                r"кингисепп|усть-луг|волхов|приозерск|тосно|кировск|ломонос|пикал|бокситогор|подпорож|лодейнопол|сланц", re.I)


def _get(url, timeout=15):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def _text(el, tag):
    x = el.find(tag)
    return (x.text or "").strip() if x is not None and x.text else ""


def read_feed(name, url, region, take_all, since):
    out = []
    root = ET.fromstring(_get(url))
    for it in root.iter("item"):
        title = html.unescape(re.sub(r"<[^>]+>", " ", _text(it, "title"))).strip()
        link = _text(it, "link")
        desc = html.unescape(re.sub(r"<[^>]+>", " ", _text(it, "description")))
        desc = re.sub(r"\s+", " ", desc).strip()[:280]
        pd = _text(it, "pubDate")
        try:
            when = email.utils.parsedate_to_datetime(pd)
            if when.tzinfo is None:
                when = when.replace(tzinfo=MSK)
        except Exception:
            continue
        if when < since or not title or not link:
            continue
        blob = title + " " + desc
        if SKIP.search(blob) or (not take_all and not ECON.search(blob)):
            continue
        reg = "ЛО" if (region == "ЛО" or LO.search(blob)) else "РФ"
        out.append({"src": name, "title": title, "desc": desc, "url": link, "when": when, "reg": reg})
    return out


def collect(since):
    items, status = [], {}
    for name, url, region, take_all in FEEDS:
        try:
            got = read_feed(name, url, region, take_all, since)
            status[name] = len(got)
            items += got
        except Exception as e:  # лента недоступна — пропускаем
            status[name] = "ошибка: " + type(e).__name__
    seen, uniq = set(), []
    for x in sorted(items, key=lambda x: x["when"], reverse=True):
        key = re.sub(r"\W+", "", x["title"].lower())[:60]
        if key in seen:
            continue
        seen.add(key)
        uniq.append(x)
    return uniq[:70], status


PROMPT = """Ты — редактор деловых новостей для предпринимателей и инвесторов Ленинградской области.
Оцени каждую новость по важности для бизнеса от 1 до 5:
5 — напрямую меняет условия для бизнеса: ключевая ставка, налоги и законы для бизнеса, новые меры поддержки, крупные решения правительства РФ или Ленобласти по экономике, крупные инвестпроекты и заводы в Ленобласти;
4 — заметно влияет на бизнес: важная статистика (инфляция, ВВП, промышленность), курс рубля и цены на сырьё при сильных движениях, крупные сделки, тарифы, решения по отраслям;
3 и ниже — рядовые новости, происшествия, политика без экономических последствий, курьёзы, спорт, отдельные компании без значения для региона.
Новости Ленобласти оценивай чуть мягче: региональные инвестпроекты, меры поддержки и решения областного правительства — минимум 4.
Ответь строго JSON-массивом без пояснений: [{"i": номер, "s": оценка, "r": "РФ" или "ЛО", "t": "суть в одном предложении до 160 знаков, своими словами, без выдумок"}]. Включи только новости с оценкой 4 и 5."""


def _rate_chunk(chunk, base, folder, token):
    lines = [f'{base + i}. [{x["src"]}] {x["title"]} — {x["desc"]}' for i, x in enumerate(chunk)]
    model = os.environ.get("MODEL", "yandexgpt-lite/latest")
    body = {"modelUri": f"gpt://{folder}/{model}", "completionOptions": {"stream": False, "temperature": 0.1, "maxTokens": "1500"},
            "messages": [{"role": "system", "text": PROMPT}, {"role": "user", "text": "\n".join(lines)}]}
    req = urllib.request.Request("https://llm.api.cloud.yandex.net/foundationModels/v1/completion", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}", "x-folder-id": folder})
    with urllib.request.urlopen(req, timeout=60) as r:
        text = json.loads(r.read())["result"]["alternatives"][0]["message"]["text"]
    rate.raw = (getattr(rate, "raw", "") + " || " + text[:400])[-1500:]
    m = re.search(r"\[.*\]", text, re.S)
    try:
        return json.loads(m.group(0)) if m else []
    except ValueError:
        return []


def rate(items, folder, token):
    rate.raw = ""
    res = []
    for k in range(0, len(items), 12):  # небольшими пачками: если модель откажется от одной новости, остальные не пропадут
        try:
            res += _rate_chunk(items[k:k + 12], k, folder, token)
        except Exception as e:
            print("rate error", repr(e))
    out = []
    for r in res:
        try:
            i, s = int(r["i"]), int(r["s"])
        except (KeyError, ValueError, TypeError):
            continue
        if 0 <= i < len(items) and s >= int(os.environ.get("MIN_SCORE", "4")):
            x = dict(items[i])
            x.update(score=s, reg=r.get("r") if r.get("r") in ("РФ", "ЛО") else x["reg"], summary=str(r.get("t") or "")[:220])
            out.append(x)
    return sorted(out, key=lambda x: (-x["score"], x["reg"] != "ЛО"))[:6]


def tg(method, **params):
    token = os.environ["BOT_TOKEN"]
    base = os.environ.get("TG_API", "https://api.telegram.org").rstrip("/")
    last = None
    for attempt in range(3):  # ретранслятор иногда отвечает 403/5xx — повторяем
        req = urllib.request.Request(f"{base}/bot{token}/{method}", data=json.dumps(params).encode(),
                                     headers={"Content-Type": "application/json", "User-Agent": UA["User-Agent"],
                                              "X-Relay-Key": os.environ.get("SECRET", "")})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 400:
                raise
        except Exception as e:
            last = e
        time.sleep(1.5 * (attempt + 1))
    raise last


def fmt(news, night=False):
    head = "🌅 <b>Важное за ночь</b>" if night else "🔔 <b>Важные новости экономики</b>"
    parts = [head]
    for x in news:
        flag = "📍 Ленобласть" if x["reg"] == "ЛО" else "🇷🇺 Россия"
        fire = " 🔥" if x["score"] >= 5 else ""
        parts.append(f'{flag}{fire}\n<b>{html.escape(x["title"])}</b>\n{html.escape(x["summary"] or x["desc"][:200])}\n'
                     f'<a href="{html.escape(x["url"], quote=True)}">{html.escape(x["src"])}</a>')
    return "\n\n".join(parts)


def chats():
    return [c.strip() for c in os.environ.get("CHAT_IDS", "").split(",") if c.strip()]


def run_digest(context, window_hours=None, dry=False):
    now = dt.datetime.now(MSK)
    if window_hours is None:
        if now.hour < 8:
            return {"skipped": "ночь"}
        window_hours = 9 if now.hour == 8 else 1.05
    since = now - dt.timedelta(hours=window_hours)
    items, status = collect(since)
    result = {"window_h": window_hours, "candidates": len(items), "feeds": status}
    if not items:
        return result
    token = (getattr(context, "token", None) or {}).get("access_token")
    news = rate(items, os.environ.get("FOLDER_ID", ""), token)
    result["important"] = [{"s": x["score"], "r": x["reg"], "t": x["title"]} for x in news]
    if dry:
        result["gpt_raw"] = getattr(rate, "raw", "")
    if news and not dry:
        text = fmt(news, night=(window_hours >= 8))
        for c in chats():
            try:
                tg("sendMessage", chat_id=c, text=text, parse_mode="HTML", disable_web_page_preview=True)
            except Exception as e:
                result.setdefault("send_errors", []).append(f"{c}: {type(e).__name__}")
        result["sent_to"] = len(chats())
    return result


def on_update(upd):
    """Вебхук Telegram: отвечаем прямо в ответе на вебхук (без исходящего запроса из облака)."""
    msg = upd.get("message") or upd.get("channel_post")
    if msg and msg.get("chat"):
        cid = str(msg["chat"]["id"])
        sub = cid in chats()
        text = ("✅ Вы подписаны: сюда приходят важные новости экономики РФ и Ленобласти (раз в час, если есть важное; ночью — тишина)."
                if sub else f"👋 Это бот важных новостей экономики РФ и Ленобласти.\n\nВаш ID: <code>{cid}</code>\n"
                            "Чтобы получать новости, добавьте этот ID в переменную CHAT_IDS функции в Yandex Cloud.")
        return {"method": "sendMessage", "chat_id": cid, "text": text, "parse_mode": "HTML"}
    mcm = upd.get("my_chat_member")
    if mcm and mcm.get("chat", {}).get("type") == "channel" and mcm.get("new_chat_member", {}).get("status") == "administrator":
        cid = str(mcm["chat"]["id"])
        if cid not in chats():
            return {"method": "sendMessage", "chat_id": cid, "parse_mode": "HTML",
                    "text": f"ID этого канала: <code>{cid}</code> — добавьте его в CHAT_IDS, чтобы сюда приходили новости."}
    return None


def _resp(code, body):
    return {"statusCode": code, "headers": {"Content-Type": "application/json; charset=utf-8"},
            "body": json.dumps(body, ensure_ascii=False, default=str), "isBase64Encoded": False}


def handler(event, context):
    event = event or {}
    # 1) таймер-триггер
    if "messages" in event and "httpMethod" not in event:
        return run_digest(context)
    # 2) HTTP: вебхук Telegram или служебные команды
    secret = os.environ.get("SECRET", "")
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    if event.get("httpMethod") == "POST" and secret and headers.get("x-telegram-bot-api-secret-token") == secret:
        raw = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            import base64
            raw = base64.b64decode(raw).decode("utf-8", "replace")
        try:
            reply = on_update(json.loads(raw))
        except Exception as e:
            print("update error", repr(e))
            reply = None
        return _resp(200, reply or {"ok": True})
    q = event.get("queryStringParameters") or {}
    if not secret or q.get("key") != secret:
        return _resp(403, {"error": "нет доступа"})
    if q.get("setup"):  # подключить вебхук: ?key=...&setup=1&url=<ссылка на эту функцию>
        url = q.get("url") or ("https://functions.yandexcloud.net/" + getattr(context, "function_name", ""))
        r = tg("setWebhook", url=url, secret_token=secret, allowed_updates=["message", "channel_post", "my_chat_member"])
        me = tg("getMe")
        return _resp(200, {"webhook": r, "bot": me.get("result", {}).get("username"), "chats": chats()})
    if q.get("info"):  # состояние вебхука: ?key=...&info=1
        return _resp(200, {"webhook": tg("getWebhookInfo").get("result"), "chats": chats(), "relay": os.environ.get("TG_API", "")})
    if q.get("check"):  # проверить ленты: ?key=...&check=1
        items, status = collect(dt.datetime.now(MSK) - dt.timedelta(hours=float(q.get("hours", "6"))))
        return _resp(200, {"feeds": status, "candidates": len(items), "sample": [x["src"] + ": " + x["title"] for x in items[:10]]})
    if q.get("test"):  # прогон с отправкой (или dry=1 без отправки): ?key=...&test=1&hours=12
        return _resp(200, run_digest(context, window_hours=float(q.get("hours", "12")), dry=bool(q.get("dry"))))
    return _resp(200, {"ok": True, "help": "check=1 | test=1[&dry=1][&hours=12] | setup=1&url=..."})
