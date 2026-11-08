"""Инфографика для шапки и обзорной части сайта.

Строит статичный HTML (карточки, кольца, столбики, полосы) из data/*.json при каждой сборке,
поэтому цифры обновляются вместе с данными. Никаких внешних библиотек.
"""
import html as _h
import math

E = _h.escape
MONTHS = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
MONTHS_FULL = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']

ICON = {
    'users': '<path d="M16 19v-1.5a3.5 3.5 0 0 0-3.5-3.5h-5A3.5 3.5 0 0 0 4 17.5V19"/><circle cx="10" cy="7.5" r="3.5"/><path d="M20 19v-1.5a3.5 3.5 0 0 0-2.6-3.4M15.5 4.2a3.5 3.5 0 0 1 0 6.6"/>',
    'eye': '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    'spark': '<path d="M4 17l5-5 4 4 7-8"/><path d="M15 8h5v5"/>',
    'percent': '<path d="M19 5 5 19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
    'ruble': '<path d="M8 20V4h6a4 4 0 0 1 0 8H6M6 16h8"/>',
    'drop': '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
    'bank': '<path d="M3 10h18L12 4 3 10zM5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18"/>',
    'factory': '<path d="M3 20V10l6 3V10l6 3V6h6v14H3z"/><path d="M7 17h2M12 17h2M17 17h1"/>',
    'target': '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r=".8"/>',
    'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.8 3.8 5.8 3.8 9s-1.3 6.2-3.8 9c-2.5-2.8-3.8-5.8-3.8-9S9.5 5.8 12 3z"/>',
    'wallet': '<path d="M4 7h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a1 1 0 0 1-1-1V7z"/><path d="M4 7l11-3v3M16 13.5h2"/>',
    'chat': '<path d="M4 5h16v11H9l-5 4V5z"/>',
}


def icon(name):
    return f'<span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg></span>'


def num(v, d=0):
    if v is None:
        return '—'
    s = f'{v:,.{d}f}'.replace(',', ' ').replace('.', ',')
    return s


def signed(v, d=1):
    if v is None:
        return '—'
    return ('+' if v > 0 else ('−' if v < 0 else '')) + num(abs(v), d)


def pill(text, tone=''):
    return f'<span class="pill {tone}">{E(text)}</span>'


def card(cls, inner):
    return f'<div class="ix {cls}">{inner}</div>'


def spark(vals, w=120, h=30):
    vals = [v for v in vals if v is not None]
    if len(vals) < 3:
        return ''
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1
    pts = [(i * w / (len(vals) - 1), h - 3 - (v - lo) / rng * (h - 6)) for i, v in enumerate(vals)]
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    up = vals[-1] >= vals[0]
    return (f'<svg class="spark {"up" if up else "down"}" viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true">'
            f'<path d="{d} L{w},{h} L0,{h} Z" class="sp-a"/><path d="{d}" class="sp-l"/><circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="2.6" class="sp-d"/></svg>')


def kpi(title, value, sub, ic, tone='', note='', sp=''):
    return card('kpi-card ' + tone, f'<div class="ix-top"><span class="ix-t">{E(title)}</span>{icon(ic)}</div>'
                f'<div class="ix-big">{value}</div><div class="ix-sub">{sub}</div>' + sp + (f'<div class="ix-note">{E(note)}</div>' if note else ''))


def donut(parts, size=150, w=22):
    """parts: [(label, value, colorClass)]"""
    tot = sum(p[1] for p in parts) or 1
    r = (size - w) / 2
    c = 2 * math.pi * r
    off = 0
    segs = []
    for label, val, col in parts:
        ln = c * val / tot
        segs.append(f'<circle r="{r:.1f}" cx="{size/2}" cy="{size/2}" fill="none" class="{col}" stroke-width="{w}" '
                    f'stroke-dasharray="{max(ln-2,0):.1f} {c:.1f}" stroke-dashoffset="{-off:.1f}" transform="rotate(-90 {size/2} {size/2})"/>')
        off += ln
    return f'<svg class="donut" viewBox="0 0 {size} {size}" width="{size}" height="{size}"><circle r="{r:.1f}" cx="{size/2}" cy="{size/2}" fill="none" class="d-track" stroke-width="{w}"/>{"".join(segs)}</svg>'


def ring(pct, label, size=112, w=12, col='c1'):
    r = (size - w) / 2
    c = 2 * math.pi * r
    ln = c * max(0, min(pct, 100)) / 100
    return (f'<div class="ring"><svg viewBox="0 0 {size} {size}" width="{size}" height="{size}"><circle r="{r:.1f}" cx="{size/2}" cy="{size/2}" fill="none" class="d-track" stroke-width="{w}"/>'
            f'<circle r="{r:.1f}" cx="{size/2}" cy="{size/2}" fill="none" class="{col}" stroke-width="{w}" stroke-linecap="round" stroke-dasharray="{ln:.1f} {c:.1f}" transform="rotate(-90 {size/2} {size/2})"/></svg>'
            f'<div class="ring-c"><b>{num(pct)}%</b><span>{E(label)}</span></div></div>')


def bars(items, h=150, fmt=lambda v: num(v)):
    """items: [(label, value, highlight)] — вертикальные скруглённые столбики."""
    mx = max([v for _, v, _ in items if v is not None] or [1]) or 1
    out = []
    for lab, v, hi in items:
        ph = 0 if v is None else max(6, round(h * v / mx))
        out.append(f'<div class="vb{" hi" if hi else ""}"><span class="vb-v">{fmt(v)}</span><span class="vb-b" style="height:{ph}px"></span><span class="vb-l">{E(lab)}</span></div>')
    return f'<div class="vbars" style="--h:{h}px">{"".join(out)}</div>'


def hbars(items, fmt=lambda v: num(v, 1), unit=''):
    """items: [(label, value, highlight)] — горизонтальные полосы, ноль посередине, если есть отрицательные."""
    vals = [v for _, v, _ in items if v is not None]
    neg = any(v < 0 for v in vals)
    mx = max([abs(v) for v in vals] or [1]) or 1
    out = []
    for lab, v, hi in items:
        if v is None:
            continue
        wpct = abs(v) / mx * (50 if neg else 100)
        left = (50 - wpct if v < 0 else 50) if neg else 0
        out.append(f'<div class="hb{" hi" if hi else ""}"><span class="hb-l">{E(lab)}</span><span class="hb-track">'
                   f'<span class="hb-b{" neg" if v < 0 else ""}" style="left:{left:.1f}%;width:{wpct:.1f}%"></span>'
                   + ('<span class="hb-zero"></span>' if neg else '') + f'</span><span class="hb-v">{fmt(v)}{unit}</span></div>')
    return f'<div class="hbars">{"".join(out)}</div>'


def progress(label, cur, target, col='c1', note=''):
    pct = 0 if not target else min(100, cur / target * 100)
    return (f'<div class="prog"><div class="prog-h"><span>{E(label)}</span><b>{num(cur)} <i>/ {num(target)}</i></b></div>'
            f'<div class="prog-t"><span class="prog-b {col}" style="width:{pct:.1f}%"></span></div>'
            f'<div class="prog-n">{num(pct)}% цели' + (f' · {E(note)}' if note else '') + '</div></div>')


def last(rows, key):
    rows = [r for r in rows if r.get(key) is not None]
    return rows[-1] if rows else {}


def build(data):
    g = lambda k: data.get(k, []) or []
    plat = {}
    for r in g('platforms'):
        plat[r['platform']] = r
    tg = plat.get('Telegram', {}).get('subscribers')
    mx_ = plat.get('MAX', {}).get('subscribers')
    vk = plat.get('ВКонтакте', {}).get('subscribers')
    ms = last(g('max_summary'), 'subscribers')
    subs_d = sorted(g('tg_subs_daily'), key=lambda r: r['day'])
    tg_week = (subs_d[-1]['subscribers'] - subs_d[0]['subscribers']) if len(subs_d) > 1 else None
    tm = sorted(g('tg_monthly'), key=lambda r: r['month'])
    full = [r for r in tm if not r.get('partial')]
    med_last = full[-1]['median_views'] if full else None
    med_prev = full[-2]['median_views'] if len(full) > 1 else None
    med_ch = (med_last / med_prev - 1) * 100 if med_last and med_prev else None
    macro = {m['indicator']: m for m in g('macro')}
    fx = sorted(g('fx'), key=lambda r: r['date'])
    fx_l = fx[-1] if fx else {}
    y0 = next((r for r in fx if r['date'] >= fx_l.get('date', '')[:4] + '-01-01'), {}) if fx_l else {}
    usd_ytd = (fx_l['usd'] / y0['usd'] - 1) * 100 if y0 else None
    oil = last(g('oil'), 'brent')
    grp = [r for r in g('grp_lo') if not r.get('est')]
    grp_l = grp[-1] if grp else {}
    gdp_y = [r for r in g('gdp_rf') if r.get('kind') == 'год' and not r.get('est')]
    gdp_l = gdp_y[-1] if gdp_y else {}
    gdp_q = ([r for r in g('gdp_rf') if r.get('kind') == 'квартал'] or [{}])[-1]
    pmi_l = (sorted(g('rf_pmi'), key=lambda r: r['period']) or [{}])[-1]
    bud = next((r for r in g('lo_budget') if r.get('est')), {})
    lo_ser = g('lo_series')

    def lo_last(ind):
        rs = sorted([r for r in lo_ser if r.get('indicator') == ind and r.get('value') is not None], key=lambda r: r['period'])
        return rs[-1] if rs else {}

    infl_lo = lo_last('infl')
    prom_lo = lo_last('prom')
    loans_lo = lo_last('loans_biz')

    sp_tg = spark([r.get('subscribers') for r in subs_d])
    sp_mx = spark([r.get('subscribers') for r in sorted(g('max_daily'), key=lambda r: r['day'])])
    sp_vk = spark([r.get('subscribers') for r in sorted([r for r in g('platforms') if r.get('platform') == 'ВКонтакте'], key=lambda r: str(r.get('at')))])
    sp_kr = spark([r.get('rate') for r in sorted(g('key_rate'), key=lambda r: r['date'])])
    sp_fx = spark([r.get('usd') for r in fx[-90:]])
    sp_in = spark([r.get('yoy') for r in sorted(g('rf_infl_month'), key=lambda r: r['period'])])

    # ---------- Шапка: тёмная «геро»-карточка + KPI ----------
    hero_kpis = ''.join([
        kpi('Telegram', num(tg), 'подписчиков', 'users', note=(f'{signed(tg_week, 0)} за неделю' if tg_week is not None else ''), sp=sp_tg),
        kpi('MAX', num(mx_), 'подписчиков', 'users', note=(f'{signed(ms.get("growth30"), 0)} за 30 дней' if ms.get('growth30') is not None else ''), sp=sp_mx),
        kpi('ВКонтакте', '≈' + num(vk), 'подписчиков', 'users', sp=sp_vk),
        kpi('Ключевая ставка', num(macro.get('key_rate', {}).get('value')) + '%', 'Банк России', 'bank', note=E(macro.get('key_rate', {}).get('note', '')), sp=sp_kr),
        kpi('Доллар', num(fx_l.get('usd'), 2) + ' ₽', 'курс ЦБ', 'ruble', note=(f'{signed(usd_ytd)}% с начала года' if usd_ytd is not None else ''), sp=sp_fx),
        kpi('Инфляция', num(macro.get('ru_infl', {}).get('value'), 2) + '%', 'годовая, Россия', 'spark', note=E(macro.get('ru_infl', {}).get('note', '')), sp=sp_in),
    ])

    # ---------- «Главное сейчас»: выводы одной строкой ----------
    def verdict(label, value, text, tone, link):
        arrow = {'good': '▲', 'bad': '▼', 'warn': '●', 'neutral': '●'}[tone]
        return (f'<a class="vd vd-{tone}" href="#{link}" data-tab-link="{link}"><span class="vd-l">{E(label)}</span>'
                f'<span class="vd-v"><i>{arrow}</i>{value}</span><span class="vd-t">{text}</span></a>')
    vds = []
    if med_last is not None and med_ch is not None:
        vds.append(verdict('Telegram: охват поста', num(med_last),
                           f'просмотров у типичного поста, <b>{signed(med_ch, 0)}%</b> к прошлому месяцу'
                           + (' — охват падает' if med_ch <= -5 else (' — охват растёт' if med_ch >= 5 else ' — без изменений')),
                           'bad' if med_ch <= -5 else ('good' if med_ch >= 5 else 'neutral'), 'tg'))
    if ms.get('growth30') is not None:
        g30 = ms.get('growth30')
        vds.append(verdict('MAX: рост', signed(g30, 0), f'подписчиков за 30 дней, всего {num(mx_)}; пост видят <b>{num(ms.get("err"), 0)}%</b> подписчиков',
                           'good' if g30 > 0 else 'bad', 'max'))
    kr, nm = macro.get('key_rate', {}), macro.get('next_meeting', {})
    if kr.get('value') is not None:
        nmd = str(nm.get('date') or '')
        nmd = (nmd[8:10] + '.' + nmd[5:7]) if len(nmd) >= 10 else ''
        vds.append(verdict('Ключевая ставка', num(kr.get('value')) + '%', E(kr.get('note') or 'решение Банка России')
                           + (f'; следующее решение — <b>{nmd}</b>' if nmd else ''), 'neutral', 'rf'))
    ri = macro.get('ru_infl', {}).get('value')
    if ri is not None:
        vds.append(verdict('Инфляция в России', num(ri, 2) + '%', 'годовая' + (f' ({E(macro["ru_infl"].get("note", ""))})' if macro['ru_infl'].get('note') else '')
                           + ('; цель ЦБ — 4%, цены растут быстрее' if ri > 4.5 else '; близко к цели ЦБ 4%'), 'warn' if ri > 4.5 else 'good', 'rf'))
    if prom_lo.get('value') is not None:
        pv = prom_lo['value']
        vds.append(verdict('Промышленность Ленобласти', signed(pv, 1) + '%', f'к прошлому году ({prom_lo["period"][5:7]}.{prom_lo["period"][:4]})'
                           + (' — производство снижается' if pv < 0 else ' — производство растёт'), 'bad' if pv < 0 else 'good', 'lo'))
    if loans_lo.get('value') is not None:
        lv = loans_lo['value']
        vds.append(verdict('Кредиты бизнесу в Ленобласти', signed(lv, 1) + '%', f'к прошлому году ({loans_lo["period"][5:7]}.{loans_lo["period"][:4]})'
                           + (' — бизнес активно берёт кредиты' if lv > 5 else ''), 'good' if lv > 0 else 'bad', 'lo'))
    verdicts = (f'<section class="ix-sec vd-sec"><h2 class="ix-sec-h">Главное сейчас</h2><div class="vd-grid">{"".join(vds)}</div>'
                '<p class="vd-hint">▲ хорошо · ▼ стоит обратить внимание · ● к сведению. Нажмите на карточку, чтобы открыть подробности.</p></section>')

    # ---------- Инфографика «Каналы» ----------
    aud = [('Telegram', tg or 0, 'c1'), ('ВКонтакте', vk or 0, 'c2'), ('MAX', mx_ or 0, 'c3')]
    tot = sum(a[1] for a in aud) or 1
    legend = ''.join(f'<li><i class="dot {c}"></i>{E(l)}<b>{num(v / tot * 100)}%</b></li>' for l, v, c in aud)
    donut_card = card('span2 glass', f'<div class="ix-top"><span class="ix-h">Аудитория по площадкам</span>{icon("globe")}</div>'
                      f'<div class="donut-wrap">{donut(aud)}<div class="donut-c"><b>{num(tot)}</b><span>всего</span></div><ul class="legend">{legend}</ul></div>')

    goals = g('goals')
    gl = ''.join(progress(r['platform'], r.get('current') or 0, r.get('target') or 0, ['c1', 'c3', 'c2'][i % 3],
                          'к 31.12') for i, r in enumerate(goals))
    goals_card = card('span2 glass', f'<div class="ix-top"><span class="ix-h">Цели по подписчикам</span>{icon("target")}</div>{gl}'
                      '<div class="ix-note">Цели заданы для примера — их можно поменять в дашборде.</div>')

    mb = [(MONTHS[int(r['month'][5:7]) - 1], r.get('median_views'), r is tm[-1]) for r in tm[-12:]]
    views_card = card('span2 glass', f'<div class="ix-top"><span class="ix-h">Медиана просмотров поста в Telegram</span>{icon("eye")}</div>'
                      f'<div class="ix-row"><div class="ix-big sm">{num(med_last)}</div>'
                      + (pill(f'{signed(med_ch, 0)}% к прошлому месяцу', 'bad' if med_ch < 0 else 'ok') if med_ch is not None else '')
                      + f'</div>{bars(mb, 120)}<div class="ix-note">Последний столбец — текущий неполный месяц.</div>')

    peers = sorted(g('tg_peers'), key=lambda r: -(r.get('median_views') or 0) / max(r.get('subscribers') or 1, 1))
    pb = [(('Мы' if p.get('ours') else p.get('name', p.get('handle', ''))[:22]), (p.get('median_views') or 0) / max(p.get('subscribers') or 1, 1) * 100, p.get('ours')) for p in peers]
    peers_card = card('span2 glass', f'<div class="ix-top"><span class="ix-h">Охват поста, % от подписчиков</span>{icon("spark")}</div>'
                      f'{hbars(pb, unit="%")}<div class="ix-note">Медиана просмотров к числу подписчиков за 30 дней — у маленьких каналов доля выше.</div>')

    mx_card = card('dark span2', f'<div class="ix-top"><span class="ix-t">MAX: вовлечённость</span>{icon("chat")}</div>'
                   f'<div class="ix-big">{num(ms.get("err"), 1)}%</div><div class="ix-sub">ERR — доля подписчиков, увидевших пост</div>'
                   f'<div class="mini-row"><div><b>{num(ms.get("posts30"))}</b><span>постов за 30 дней</span></div><div><b>{num(ms.get("avg_views_post"))}</b><span>просмотров на пост</span></div></div>')

    channels = (f'<section class="ix-sec"><h2 class="ix-sec-h">Каналы в цифрах</h2><div class="bento">'
                f'{donut_card}{goals_card}{views_card}{peers_card}{mx_card}'
                + card('span2 glass', f'<div class="ix-top"><span class="ix-h">Постов в Telegram по месяцам</span>{icon("chat")}</div>'
                       + bars([(MONTHS[int(r['month'][5:7]) - 1], r.get('posts'), r is tm[-1]) for r in tm[-12:]], 90)
                       + f'<div class="ix-note">За {MONTHS_FULL[int(full[-1]["month"][5:7]) - 1]} — {num(full[-1]["posts"])} постов</div>' if full else '')
                + '</div></section>')

    # ---------- Инфографика «Экономика» ----------
    struct = sorted(g('grp_structure'), key=lambda r: -r['share'])[:6]
    st = hbars([(r['branch'], r['share'], i == 0) for i, r in enumerate(struct)], unit='%')
    grp_card = card('span2 glass', f'<div class="ix-top"><span class="ix-h">ВРП Ленобласти — {E(str(grp_l.get("year", "")))}</span>{icon("factory")}</div>'
                    f'<div class="ix-row"><div class="ix-big sm">{num((grp_l.get("grp") or 0) / 1000, 1)} трлн ₽</div>{pill("1,3% ВРП России", "ac")}</div>'
                    f'<div class="ix-sub">Крупнейшие отрасли, % ВРП</div>{st}')

    nb = {}
    for r in g('lo_neighbors'):
        nb.setdefault(r['ind'], {})[r['region']] = r
    def nbrow(ind, label):
        rows = nb.get(ind, {})
        items = [(('Ленобласть' if k.startswith('Ленинград') else k.replace(' область', '')), v['value'], k.startswith('Ленинград')) for k, v in rows.items()]
        return f'<div class="nb-h">{E(label)}</div>' + hbars(items, unit='%')
    nb_card = card('span2 glass', f'<div class="ix-top"><span class="ix-h">Ленобласть и соседи</span>{icon("globe")}</div>'
                   + nbrow('invest', 'Инвестиции, % г/г') + nbrow('loans', 'Кредиты компаниям, % г/г'))

    bud_card = card('glass', f'<div class="ix-top"><span class="ix-h">Бюджет области {E(str(bud.get("year", "")))}</span>{icon("wallet")}</div>'
                    f'<div class="rings">{ring(bud.get("income_pct") or 0, "доходы", col="c1")}{ring(bud.get("expense_pct") or 0, "расходы", col="c2")}</div>'
                    f'<div class="ix-note">{num(bud.get("income"), 1)} из {num(bud.get("income_plan"), 1)} млрд ₽ доходов</div>')

    eco_dark = card('dark span2', f'<div class="ix-top"><span class="ix-t">Экономика России</span>{icon("spark")}</div>'
                    f'<div class="big-grid">'
                    f'<div><b>{signed(gdp_l.get("growth"))}%</b><span>ВВП за {E(str(gdp_l.get("period", "")))} год</span></div>'
                    f'<div><b>{num(macro.get("key_rate", {}).get("value"))}%</b><span>ключевая ставка</span></div>'
                    f'<div><b>{num(macro.get("ru_infl", {}).get("value"), 2)}%</b><span>годовая инфляция</span></div>'
                    f'<div><b>{num(macro.get("cbr_infl_low", {}).get("value"), 1)}–{num(macro.get("cbr_infl_high", {}).get("value"), 1)}%</b><span>прогноз ЦБ на год</span></div>'
                    f'<div><b>{signed(gdp_q.get("growth"))}%</b><span>ВВП, {E(str(gdp_q.get("period", "")))}</span></div>'
                    f'<div><b>{num(pmi_l.get("mfg"), 1)}</b><span>PMI промышленности ({"рост" if (pmi_l.get("mfg") or 0) >= 50 else "спад"})</span></div>'
                    f'</div>')

    lo_card = card('glass', f'<div class="ix-top"><span class="ix-h">Ленобласть сейчас</span>{icon("factory")}</div>'
                   f'<div class="stack"><div><b>{num(infl_lo.get("value"), 1)}%</b><span>инфляция</span></div>'
                   f'<div><b class="{"neg" if (prom_lo.get("value") or 0) < 0 else "pos"}">{signed(prom_lo.get("value"))}%</b><span>промпроизводство г/г</span></div>'
                   f'<div><b class="pos">{signed(loans_lo.get("value"))}%</b><span>кредиты бизнесу г/г</span></div></div>')

    economy = (f'<section class="ix-sec"><h2 class="ix-sec-h">Экономика в цифрах</h2><div class="bento">'
               f'{eco_dark}{grp_card}{lo_card}{bud_card}{nb_card}</div></section>')

    return hero_kpis, verdicts + channels + economy
