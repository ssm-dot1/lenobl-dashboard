"""Страница «Рекомендации по каналам»: выводы из данных сайта + конкретные шаги."""
import datetime as _dt
import html as _h

E = _h.escape


def _n(x, d=0):
    s = f'{x:,.{d}f}'.replace(',', ' ').replace('.', ',')
    return s


def _goal(goals, plat):
    return next((g for g in goals if g.get('platform') == plat), None)


def build(data):
    tm = [m for m in data.get('tg_monthly', []) if not m.get('partial')]
    peak = max(tm, key=lambda m: m['median_views']) if tm else None
    last = tm[-1] if tm else None
    drop = round((1 - last['median_views'] / peak['median_views']) * 100) if peak and last else None
    peers = data.get('tg_peers', [])
    ours = next((p for p in peers if p.get('ours')), {})
    mx = (data.get('max_summary') or [{}])[0]
    goals = data.get('goals', [])
    plat = {p['platform']: p for p in data.get('platforms', [])}
    src = (data.get('tg_sources_sum') or [{}])[0]
    mix = {m['type']: m for m in data.get('max_content_mix', [])}
    gaps = data.get('peer_gaps', [])
    today = _dt.date.today()

    def need(p):
        g = _goal(goals, p)
        if not g:
            return ''
        cur = plat.get(p, {}).get('subscribers') or g['current']
        dl = _dt.date.fromisoformat(g['deadline'])
        weeks = max(1, (dl - today).days / 7)
        left = g['target'] - cur
        if left <= 0:
            return f'Цель {_n(g["target"])} к {dl:%d.%m} уже достигнута.'
        return f'До цели {_n(g["target"])} к {dl:%d.%m.%Y} не хватает {_n(left)} подписчиков — это ≈{_n(left / weeks)} в неделю.'

    max_pace = ''
    if mx.get('growth30') is not None:
        g = _goal(goals, 'MAX')
        if g:
            days = (_dt.date.fromisoformat(g['deadline']) - today).days
            proj = (plat.get('MAX', {}).get('subscribers') or g['current']) + mx['growth30'] / 30 * days
            max_pace = f' При нынешнем темпе (+{mx["growth30"]} за 30 дней) к концу года будет ≈{_n(proj)}.'

    recs = [
        ('Telegram', 'high', 'Вернуть охват постов',
         (f'Медианный пост набирал {_n(peak["median_views"])} просмотров в {peak["month"][5:]}.{peak["month"][:4]}, '
          f'а в {last["month"][5:]}.{last["month"][:4]} — {_n(last["median_views"])} (−{drop}%).') if peak else '',
         ['Меньше репостов и длинных дайджестов: свои полезные посты стабильно набирают больше.',
          'Дайджест — не больше 3 новостей, каждая с выводом «что это значит для бизнеса».',
          'Раз в неделю — формат с вовлечением: опрос, тест, «вопрос — ответ» от подписчиков.',
          'Закрепить приветственный пост с полезными ссылками (тема из резерва) — он работает для новых подписчиков.']),
        ('Telegram', 'high', 'Публиковать в лучшие часы',
         'Лучшие часы в Telegram — 11:00, 12:00 и 15:00, но в них выходит только около трети постов. В MAX — 10:00, 13:00 и 16:00.',
         ['Ставить главный пост дня на 11:00–12:00 через отложенную публикацию.',
          'Второй пост — на 15:00; дайджесты не ставить на утро понедельника, когда лента перегружена.',
          'В MAX публиковать с 10:00 и 13:00, а не одновременно с Telegram.']),
        ('Telegram', 'mid', 'Не больше 3–4 постов в день',
         'В дни с 5 и более постами медианный пост набирает заметно меньше просмотров, чем в дни с 1–4 постами.',
         ['Если поводов больше — объединять их в одну подборку или переносить на следующий день.',
          'Держать в резерве готовые посты, чтобы равномерно закрывать «пустые» дни.']),
        ('Контент', 'mid', 'Делать больше того, что заходит',
         'Лучше всего работают «Крутая Локация» и поздравления: по ним в 2–3 раза больше реакций. Дайджесты и посты о форумах — на 20–25% ниже нормы.',
         ['«Крутая Локация» — минимум раз в неделю, с фото площадки и цифрами (площадь, мощность, расстояние до КАД).',
          'Поздравления — с лицами и короткой историей человека или компании, а не открыткой.',
          'Посты о форумах — не анонс, а итог: какие соглашения, какие компании, что это даст области.']),
        ('Контент', 'mid', 'Закрыть темы, которые есть у коллег, но нет у нас',
         'Похожие каналы получают на этих темах в 2–4 раза больше реакций, чем обычно.',
         [f'{g["topic"]}: {g["idea"][:1].lower()+g["idea"][1:]}' for g in gaps]),
        ('Telegram', 'mid', 'Рост подписчиков',
         need('Telegram') + (f' Канал уже упоминали {_n(src.get("channels", 0))} каналов — это база для взаимного продвижения.' if src.get('channels') else ''),
         ['Договориться о взаимных упоминаниях с «МойБизнес47» и муниципальными каналами — тематика пересекается.',
          'Ссылка и QR-код на канал — на сайте lenoblinvest.ru, в подписи писем и в раздаточных материалах на мероприятиях.',
          'После консультаций Агентства — предлагать подписаться на канал, где выходят разборы мер поддержки.']),
        ('MAX', 'high', 'Ускорить рост MAX',
         (f'MAX растёт и вовлекает лучше Telegram: ERR {_n(mx.get("err", 0), 1)}%. ' if mx else '') + need('MAX') + max_pace,
         ['Анонсировать MAX в Telegram и ВКонтакте: «дублируем всё в MAX» раз в 1–2 недели.',
          'Публиковать в MAX лучшие посты Telegram, адаптируя первую строку.',
          ('Чаще использовать видео: в MAX оно набирает в среднем ' + _n(mix['VIDEO']['reach_avg']) + ' просмотров против ' + _n(mix['PHOTO']['reach_avg']) + ' у фото.') if 'VIDEO' in mix and 'PHOTO' in mix else 'Чаще использовать видео и короткие ролики.']),
        ('ВКонтакте', 'low', 'Подтянуть ВКонтакте',
         need('ВКонтакте') + ' Подробной статистики по ВКонтакте на сайте пока нет — без неё сложно понять, что работает.',
         ['Дать доступ к статистике сообщества, чтобы добавить её на сайт.',
          'Публиковать не копию Telegram, а адаптацию: заголовок, абзацы, карусель карточек.',
          'Пробовать VK Клипы с короткими объяснениями мер поддержки.']),
    ]
    pr = {'high': ('Сделать в первую очередь', 'r-high'), 'mid': ('Важно', 'r-mid'), 'low': ('Можно позже', 'r-low')}
    cards = []
    for area, p, title, why, todo in recs:
        lab, cls = pr[p]
        cards.append(f'<article class="ix rc {cls}"><div class="rc-top"><span class="pill">{E(area)}</span><span class="rc-pr">{lab}</span></div>'
                     f'<h3 class="rc-h">{E(title)}</h3>' + (f'<p class="rc-why">{E(why)}</p>' if why else '') +
                     '<div class="rc-sub">Что сделать</div><ul class="rc-todo">' + ''.join(f'<li>{E(t)}</li>' for t in todo) + '</ul></article>')
    stats = [
        ('Telegram', _n(plat.get('Telegram', {}).get('subscribers', 0)), 'подписчиков'),
        ('Медиана просмотров TG', _n(last['median_views']) if last else '—', f'{last["month"][5:]}.{last["month"][:4]}' if last else ''),
        ('ER Telegram', (_n(ours.get('er', 0), 1) + '%') if ours else '—', 'вовлечённость'),
        ('MAX', _n(plat.get('MAX', {}).get('subscribers', 0)), f'+{mx.get("growth30", 0)} за 30 дней'),
        ('ERR MAX', _n(mx.get('err', 0), 1) + '%', 'охват от подписчиков'),
    ]
    st = ''.join(f'<div class="ix rs"><div class="ix-t">{E(a)}</div><div class="ix-big sm">{b}</div><div class="ix-sub">{E(c)}</div></div>' for a, b, c in stats)
    return f'<div class="rs-grid">{st}</div><div class="rc-grid">{"".join(cards)}</div>'


CSS = '''
.rs-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}
@media (max-width:900px){.rs-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.rc-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
@media (max-width:900px){.rc-grid{grid-template-columns:1fr}}
.rc{padding:20px 22px;gap:8px;border-top:4px solid var(--ac-2)}
.rc.r-high{border-top-color:var(--ac)}.rc.r-low{border-top-color:var(--sea)}
.rc-top{display:flex;justify-content:space-between;align-items:center;gap:8px}
.rc-pr{font-size:12px;font-weight:700;color:var(--color-fg-muted)}
.r-high .rc-pr{color:var(--ac)}
.rc-h{font-family:var(--font-head);font-size:20px;font-weight:800;margin:4px 0 0;line-height:1.25}
.rc-why{margin:0;font-size:14.5px;line-height:1.5;color:var(--color-fg-muted)}
.rc-sub{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;margin-top:6px}
.rc-todo{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:6px;font-size:14.5px;line-height:1.45}
.rc-todo li::marker{color:var(--ac)}
.rs{padding:16px}
'''
