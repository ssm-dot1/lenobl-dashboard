"""Генератор постов для сайта «Экономика Ленобласти» — функция Yandex Cloud Functions (Python 3.12).

Сайт отправляет сюда тему и параметры, функция обращается к YandexGPT от имени своего
сервисного аккаунта (роль ai.languageModels.user) и возвращает готовый текст.
Ключей в коде и на сайте нет: IAM-токен функция получает из контекста вызова.

Переменные окружения функции:
  FOLDER_ID   — идентификатор каталога Yandex Cloud (обязательно)
  MODEL       — модель, по умолчанию yandexgpt/latest (можно yandexgpt-lite/latest — дешевле)
  ALLOW_ORIGIN — откуда разрешены запросы, по умолчанию * (можно https://ssm-dot1.github.io)
"""
import base64
import json
import os
import urllib.error
import urllib.request

API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

RUBRICS = {
    "Без рубрики", "Инструкция для инвестора", "Земля: шаг за шагом", "Деньги для проекта", "Сравниваем",
    "Вопрос — ответ", "Мифы об инвестициях", "Дедлайны месяца", "Словарь инвестора", "История успеха",
    "Крутая Локация", "Цифра дня", "Меры поддержки",
}
FORMATS = {
    "telegram": "пост для Telegram-канала: короткий цепляющий заголовок первой строкой, 2–4 абзаца, списки с эмодзи-маркерами там, где перечисление, в конце призыв обратиться в Агентство экономического развития и 2–3 хэштега (#Ленобласть и по теме)",
    "vk": "пост для ВКонтакте: заголовок, вводный абзац, основная часть с подзаголовками или списком, вывод и призыв, 3–5 хэштегов",
    "cards": "текст для карусели из 5–7 карточек: для каждой карточки строка «Карточка N» и под ней заголовок (до 6 слов) и 1–3 коротких предложения; первая карточка — обложка с вопросом или обещанием пользы, последняя — что сделать и куда обратиться",
    "short": "короткий анонс до 400 знаков: одна мысль, польза для бизнеса и призыв",
}
LENGTHS = {"short": "примерно 500–700 знаков", "medium": "примерно 900–1300 знаков", "long": "примерно 1500–2200 знаков"}
AUDIENCES = {
    "all": "предприниматели и инвесторы Ленинградской области",
    "msp": "малый и средний бизнес, индивидуальные предприниматели",
    "investors": "инвесторы, которые выбирают площадку и запускают проект",
    "industry": "производственные компании и промышленные предприятия",
}

SYSTEM = """Ты — редактор Telegram-канала «Экономика Ленобласти» (@lenoblinvest). Канал ведут Комитет экономического развития и инвестиционной деятельности и Агентство экономического развития Ленинградской области (АЭРЛО).
Аудитория — предприниматели и инвесторы. Задача каждого поста — практическая польза для бизнеса: что изменилось, кому это нужно, что конкретно сделать, сроки, куда обратиться.

Правила:
1. Пиши по-русски, деловым, но живым языком, без канцелярита и воды. Короткие предложения и абзацы.
2. Начинай с пользы или проблемы читателя, а не с «В Ленинградской области…».
3. Объясняй термины и аббревиатуры при первом упоминании.
4. Не выдумывай цифры, даты, суммы, названия законов, программ и компаний. Используй только факты из запроса. Если для поста нужна конкретика, которой нет, поставь в тексте пометку [уточнить: что именно].
5. Не обещай гарантированных результатов, не давай юридических и налоговых гарантий; формулируй «можно», «стоит проверить», «специалисты Агентства помогут».
6. Призыв в конце — обратиться за консультацией в Агентство экономического развития Ленинградской области.
7. Без политики, без оценок власти и конкурентов, без кликбейта.

Формат ответа — строго два блока:
ПОСТ:
<готовый текст>
ПРОВЕРИТЬ ПЕРЕД ПУБЛИКАЦИЕЙ:
<2–5 пунктов: какие факты, цифры и ссылки нужно сверить>"""


def _resp(code, body, origin):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json; charset=utf-8",
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "86400",
        },
        "body": json.dumps(body, ensure_ascii=False),
        "isBase64Encoded": False,
    }


def _clean(s, n):
    s = str(s or "").strip()
    return s[:n]


def handler(event, context):
    origin = os.environ.get("ALLOW_ORIGIN", "*")
    method = (event or {}).get("httpMethod", "POST")
    if method == "OPTIONS":
        return _resp(204, {}, origin)
    if method != "POST":
        return _resp(405, {"error": "Нужен POST-запрос"}, origin)

    raw = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(raw).decode("utf-8", "replace")
    try:
        req = json.loads(raw)
    except ValueError:
        return _resp(400, {"error": "Некорректный запрос"}, origin)

    topic = _clean(req.get("topic"), 600)
    if len(topic) < 5:
        return _resp(400, {"error": "Опишите тему поста хотя бы в нескольких словах"}, origin)
    facts = _clean(req.get("facts"), 2500)
    rubric = req.get("rubric") if req.get("rubric") in RUBRICS else "Без рубрики"
    fmt = FORMATS.get(req.get("format"), FORMATS["telegram"])
    length = LENGTHS.get(req.get("length"), LENGTHS["medium"])
    audience = AUDIENCES.get(req.get("audience"), AUDIENCES["all"])

    user = (f"Тема: {topic}\n"
            f"Рубрика: {rubric}{' (укажи рубрику хэштегом в начале или в конце)' if rubric != 'Без рубрики' else ''}\n"
            f"Формат: {fmt}\n"
            f"Объём: {length}\n"
            f"Для кого: {audience}\n"
            + (f"Факты, которые можно использовать (других цифр не добавляй):\n{facts}\n" if facts else "Конкретных фактов не дано — не придумывай цифры, ставь пометки [уточнить].\n"))

    folder = os.environ.get("FOLDER_ID", "")
    if not folder:
        return _resp(500, {"error": "Функция не настроена: не задан FOLDER_ID"}, origin)
    token = getattr(context, "token", None) or {}
    if isinstance(token, dict):
        token = token.get("access_token")
    if not token:
        return _resp(500, {"error": "Функции не назначен сервисный аккаунт"}, origin)

    model = os.environ.get("MODEL", "yandexgpt/latest")
    payload = {
        "modelUri": f"gpt://{folder}/{model}",
        "completionOptions": {"stream": False, "temperature": 0.5, "maxTokens": "1800"},
        "messages": [{"role": "system", "text": SYSTEM}, {"role": "user", "text": user}],
    }
    http = urllib.request.Request(API_URL, data=json.dumps(payload).encode("utf-8"), method="POST",
                                  headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}",
                                           "x-folder-id": folder})
    try:
        with urllib.request.urlopen(http, timeout=55) as r:
            res = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        print("YandexGPT error", e.code, detail)
        return _resp(502, {"error": "Нейросеть не ответила, попробуйте ещё раз через минуту",
                           "detail": f"{e.code}: {detail}"}, origin)
    except Exception as e:  # сеть, таймаут
        print("YandexGPT request failed", repr(e))
        return _resp(502, {"error": "Нейросеть не ответила, попробуйте ещё раз через минуту",
                           "detail": repr(e)[:300]}, origin)

    try:
        text = res["result"]["alternatives"][0]["message"]["text"]
    except (KeyError, IndexError, TypeError):
        return _resp(502, {"error": "Не удалось получить текст, попробуйте переформулировать тему"}, origin)

    post, check = text, ""
    if "ПРОВЕРИТЬ ПЕРЕД ПУБЛИКАЦИЕЙ:" in text:
        post, check = text.split("ПРОВЕРИТЬ ПЕРЕД ПУБЛИКАЦИЕЙ:", 1)
    post = post.replace("ПОСТ:", "", 1).strip()
    return _resp(200, {"post": post, "check": check.strip(), "model": model}, origin)
