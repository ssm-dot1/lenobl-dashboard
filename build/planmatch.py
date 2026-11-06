"""Сверка контент-плана с вышедшими постами Telegram (и MAX для справки).

Каждый пункт плана делится на части по « + » (например «Дайджест … + тема»), для каждой части
ищется пост в тот же день (или на следующий) с наибольшим совпадением по основам слов.
"""
import datetime as _dt
import re

STOP = set('''этот этого этой чтобы который которые какие какой каких такой также более можно нужно нужна
почему зачем сколько когда через после перед между будет может могут если только очень всего свой своих
ленинградской ленинградская области область ленобласти ленобласть региона регион россии российской
новостей новости новость дайджест федеральных региональных пост поста посты для как что где это или про'''.split())


def stems(text):
    out = set()
    for w in re.findall(r'[а-яёa-z0-9]+', str(text).lower().replace('ё', 'е')):
        if len(w) < 4 or w in STOP:
            continue
        out.add(w[:5] if len(w) > 5 else w)
    return out


def _parts(text):
    ps = [p.strip() for p in re.split(r'\s\+\s', text) if p.strip()]
    return ps


def _is_digest(part):
    return part.lower().startswith('дайджест')


def _score(part, post):
    a = stems(part)
    if not a:
        return 0.0
    b = stems(post.get('text', ''))
    hit = len(a & b)
    return hit / len(a) if hit >= 2 or (hit == 1 and len(a) <= 2) else 0.0


def match(plan, tg_posts, today=None):
    """Возвращает список статусов для каждого пункта плана и сводку."""
    today = today or _dt.date.today()
    by_day = {}
    for p in tg_posts:
        by_day.setdefault(str(p.get('posted', ''))[:10], []).append(p)
    covered_from = min(by_day) if by_day else None
    res = []
    used = set()
    for it in plan:
        d = _dt.date.fromisoformat(it['date'])
        day_posts = by_day.get(it['date'], []) + by_day.get(str(d + _dt.timedelta(days=1)), [])
        parts = []
        for part in _parts(it['text']):
            best, bs = None, 0.0
            for p in day_posts:
                if p.get('id') in used:
                    continue
                if _is_digest(part):
                    s = 1.0 if 'дайджест' in str(p.get('text', '')).lower()[:60] and (
                        ('федерал' in part.lower()) == ('федерал' in str(p.get('text', '')).lower()[:60])) else 0.0
                else:
                    s = _score(part, p)
                if s > bs:
                    best, bs = p, s
            ok = best is not None and bs >= 0.34
            if ok:
                used.add(best.get('id'))
            parts.append({'part': part, 'post': best if ok else None})
        if d > today:
            status = 'future'
        elif d == today and not any(x['post'] for x in parts):
            status = 'today'
        elif covered_from and it['date'] < covered_from:
            status = 'nodata'
        elif all(x['post'] for x in parts):
            status = 'done'
        elif any(x['post'] for x in parts):
            status = 'partial'
        elif by_day.get(it['date']):
            status = 'other'
        else:
            status = 'missed'
        other = None
        if status in ('other', 'partial', 'missed'):
            od = [p for p in by_day.get(it['date'], []) if p.get('id') not in used]
            if od:
                other = max(od, key=lambda p: p.get('views') or 0)
        res.append({'status': status, 'parts': parts, 'other': other})
    # сводка
    past = [r for r, it in zip(res, plan) if r['status'] not in ('future', 'today', 'nodata')]
    done = [r for r in past if r['status'] == 'done']
    partial = [r for r in past if r['status'] == 'partial']
    pv = [x['post']['views'] for r in past for x in r['parts'] if x['post'] and x['post'].get('views') is not None]
    plan_ids = {x['post'].get('id') for r in past for x in r['parts'] if x['post']}
    past_days = {it['date'] for r, it in zip(res, plan) if r in past}
    ov = [p['views'] for dd in past_days for p in by_day.get(dd, []) if p.get('id') not in plan_ids and p.get('views') is not None]
    med = lambda a: sorted(a)[len(a) // 2] if a else None
    summary = {'total': len(plan), 'past': len(past), 'done': len(done), 'partial': len(partial),
               'missed': sum(1 for r in past if r['status'] in ('missed', 'other')),
               'future': sum(1 for r in res if r['status'] in ('future', 'today')),
               'plan_median': med(pv), 'other_median': med(ov)}
    return res, summary
