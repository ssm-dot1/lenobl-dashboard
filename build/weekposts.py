"""«Посты недели»: три лучших и три худших поста за последнюю полную неделю (пн–вс) с причинами.

Причины не выдуманы: для каждого признака (рубрика, формат, репост, загрузка дня, время, день недели)
сравнивается медиана просмотров постов с этим признаком и без него по всей истории канала.
"""
import datetime as _dt
import html as _h
import re

E = _h.escape
WD = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
WDL = ['понедельник', 'вторник', 'среду', 'четверг', 'пятницу', 'субботу', 'воскресенье']


def _pl(n):
    n = int(n); m = n % 100
    w = 'просмотров' if 11 <= m <= 14 else 'просмотр' if n % 10 == 1 else 'просмотра' if 2 <= n % 10 <= 4 else 'просмотров'
    return f'{n} {w}'


def _med(a):
    a = sorted(a)
    return a[len(a) // 2] if a else None


def _title(t, n=95):
    t = re.sub(r'\s+', ' ', str(t or '')).strip()
    t = re.sub(r'([а-яё])([А-ЯЁ])', r'\1. \2', t, count=1)  # «новостейВладимир» → «новостей. Владимир»
    t = re.sub(r'([.!?])([А-ЯЁA-Z«])', r'\1 \2', t)
    if len(t) <= n:
        return t
    cut = t[:n].rsplit(' ', 1)[0]
    return cut.rstrip(',.:;—- ') + '…'


def _feats(p, per_day):
    t = str(p.get('text', '')).lower()
    f = {}
    if 'дайджест' in t[:60]:
        f['digest'] = 'дайджест'
    if re.search(r'поздрав|с днём|с днем|годовщин|лет на стороне|-летием|летием', t[:200]):
        f['congrats'] = 'поздравление'
    if 'крут' in t[:200] and 'локац' in t[:200]:
        f['location'] = '«Крутая Локация»'
    if re.search(r'форум|выставк|пмэф', t[:150]):
        f['forum'] = 'пост о форуме или выставке'
    if p.get('fwd'):
        f['fwd'] = 'репост из другого канала'
    if p.get('type') == 'Видео':
        f['video'] = 'видео'
    if per_day.get(str(p.get('posted', ''))[:10], 0) >= 5:
        f['busy'] = 'день с 5+ постами'
    h = int(str(p.get('posted', '00T00'))[11:13] or 0)
    if h >= 19:
        f['late'] = 'вечерняя публикация (после 19:00)'
    elif 10 <= h <= 12:
        f['morning'] = 'публикация в 10–12 часов'
    if p.get('len') and p['len'] > 2000:
        f['long'] = 'длинный текст (2000+ знаков)'
    return f


def _effects(posts, key):
    per_day = {}
    for p in posts:
        d = str(p.get('posted', ''))[:10]
        per_day[d] = per_day.get(d, 0) + 1
    allm = _med([p[key] for p in posts if p.get(key) is not None])
    groups = {}
    for p in posts:
        if p.get(key) is None:
            continue
        for k in _feats(p, per_day):
            groups.setdefault(k, []).append(p[key])
    eff = {}
    for k, v in groups.items():
        if len(v) >= 4 and allm:
            eff[k] = (_med(v) / allm - 1, _med(v), len(v))
    return eff, allm, per_day


def _reasons(p, eff, allm, per_day, positive, key):
    out = []
    f = _feats(p, per_day)
    for k, lab in f.items():
        if k not in eff:
            continue
        e, m, n = eff[k]
        if positive and e >= 0.05:
            out.append((e, f'{lab}: такие посты в среднем набирают {_pl(m)}, на {round(e * 100)}% выше обычного'))
        elif not positive and e <= -0.05:
            out.append((-e, f'{lab}: такие посты в среднем набирают {_pl(m)}, на {round(-e * 100)}% ниже обычного'))
        elif k == 'busy' and not positive:
            out.append((0.01, f'в этот день вышло {per_day[str(p["posted"])[:10]]} постов — они конкурируют за внимание'))
        elif k == 'fwd' and not positive:
            out.append((0.01, 'репост из другого канала — свои посты обычно читают лучше'))
    out.sort(key=lambda x: -x[0])
    r = [t for _, t in out[:2]]
    if not r:
        tags = [lab for k, lab in f.items() if k in ('congrats', 'location', 'digest', 'video', 'forum')]
        if tags:
            return [f'{", ".join(tags).capitalize()} — по статистике канала это само по себе не даёт заметной разницы, '
                    + ('сработал повод и тема' if positive else 'тема зашла слабее')]
        r = ['по формату и времени это обычный пост — сработала тема' if positive else
             'по формату и времени это обычный пост — тема зашла слабее']
    return r


def _last_week(today):
    mon = today - _dt.timedelta(days=today.weekday() + 7)
    return mon, mon + _dt.timedelta(days=6)


def _block(name, posts, key, mon, sun, has_url):
    wk = [p for p in posts if mon.isoformat() <= str(p.get('posted', ''))[:10] <= sun.isoformat() and p.get(key) is not None]
    if len(wk) < 4:
        return f'<div class="ix wp"><div class="ix-top"><span class="ix-h">{name}</span></div><p class="ix-sub">За эту неделю мало данных о постах.</p></div>'
    eff, allm, per_day = _effects(posts, key)
    wk.sort(key=lambda p: -p[key])
    k = min(3, len(wk) // 2)
    top, bot = wk[:k], wk[-k:][::-1]
    wmed = _med([p[key] for p in wk])

    def item(p, positive):
        dt = str(p['posted'])
        d = _dt.date.fromisoformat(dt[:10])
        t = E(_title(p.get('text')))
        if has_url and p.get('url'):
            t = f'<a href="{E(p["url"])}" target="_blank" rel="noopener">{t}</a>'
        rs = ''.join(f'<li>{E(x)}</li>' for x in _reasons(p, eff, allm, per_day, positive, key))
        return (f'<li class="wp-i"><div class="wp-v">{p[key]}</div><div class="wp-b"><div class="wp-m">{WD[d.weekday()]}, {d:%d.%m} · {dt[11:16]}'
                f'{" · " + E(p["type"]) if p.get("type") else ""}</div><div class="wp-t">{t}</div><ul class="wp-r">{rs}</ul></div></li>')
    note = 'просмотры за первые 24 часа' if key == 'views_24h' else 'просмотры на сегодня'
    return (f'<div class="ix wp"><div class="ix-top"><span class="ix-h">{name}</span><span class="ix-sub">{len(wk)} постов · медиана {wmed} · {note}</span></div>'
            f'<div class="wp-cols"><div><div class="wp-h up">▲ Лучшие</div><ol class="wp-l">{"".join(item(p, True) for p in top)}</ol></div>'
            f'<div><div class="wp-h down">▼ Слабые</div><ol class="wp-l">{"".join(item(p, False) for p in bot)}</ol></div></div></div>')


def build(data, today):
    mon, sun = _last_week(today)
    tg = data.get('tg_posts_history', [])
    mx = data.get('max_posts_full', [])
    mkey = 'views_24h' if mx and all(p.get('views_24h') is not None for p in mx) else 'views'
    return (f'<section class="wp-sec"><div class="wp-head"><h2 class="ix-sec-h">Посты недели · {mon:%d.%m}–{sun:%d.%m}</h2>'
            f'<p class="ix-sub">Обновляется каждый понедельник. Причины — сравнение с медианой просмотров постов канала с тем же признаком.</p></div>'
            f'<div class="wp-grid">{_block("Telegram", tg, "views", mon, sun, True)}{_block("MAX", mx, mkey, mon, sun, False)}</div></section>')


CSS = '''
.wp-sec{display:flex;flex-direction:column;gap:10px}
.wp-head .ix-sub{margin:4px 0 0}
.wp-grid{display:grid;grid-template-columns:1fr;gap:14px}
.wp{padding:20px 22px;gap:12px}
.wp-cols{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media (max-width:800px){.wp-cols{grid-template-columns:1fr}}
.wp-h{font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.04em;margin-bottom:8px}
.wp-h.up{color:#0d8f7b}.wp-h.down{color:#c2412d}
.wp-l{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}
.wp-i{display:flex;gap:12px;align-items:flex-start;padding:12px;border-radius:14px;background:rgba(255,255,255,.5);border:1px solid rgba(123,77,219,.12)}
.wp-v{flex:none;min-width:52px;font-family:var(--font-head);font-weight:800;font-size:22px;line-height:1.1}
.wp-b{min-width:0;display:flex;flex-direction:column;gap:3px}
.wp-m{font-size:12px;color:var(--color-fg-muted)}
.wp-t{font-size:14.5px;font-weight:600;line-height:1.35}
.wp-t a{color:inherit;text-decoration:none}.wp-t a:hover{color:var(--ac);text-decoration:underline}
.wp-r{margin:2px 0 0;padding-left:16px;font-size:13px;color:var(--color-fg-muted);line-height:1.4}
.wp-r li::marker{color:var(--ac)}
[data-theme="dark"] .wp-i{background:rgba(255,255,255,.05);border-color:rgba(179,155,245,.18)}
[data-theme="dark"] .wp-h.up{color:#3fd1b5}[data-theme="dark"] .wp-h.down{color:#ff7a66}
'''
