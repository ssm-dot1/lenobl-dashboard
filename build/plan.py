"""Вкладка «Контент-план» (план по дням + резерв тем) для сайта."""
import datetime as _dt
import html as _h
from urllib.parse import quote

E = _h.escape
WD = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']


def _kind(item):
    t = item['text']
    if item.get('holiday'):
        return 'Праздник', 'k-hol'
    if t.startswith('Дайджест'):
        return 'Дайджест + тема', 'k-dig'
    if t.startswith('Цифра дня'):
        return 'Цифра дня', 'k-num'
    if t.startswith(('Международная', 'Выставка', 'Форум')):
        return 'Событие', 'k-ev'
    return 'Пост', 'k-post'


def _write(text):
    return f'<a class="cp-write" href="post.html?topic={quote(text)}" title="Открыть в генераторе постов">✎ Написать</a>'


def _pl(n, a='просмотр', b='просмотра', c='просмотров'):
    n = int(n or 0); m = n % 100
    w = c if 11 <= m <= 14 else a if n % 10 == 1 else b if 2 <= n % 10 <= 4 else c
    return f'{n:,}'.replace(',', ' ') + ' ' + w


def _plink(post, label):
    u = post.get('url')
    return f'<a href="{E(u)}" target="_blank" rel="noopener">{label}</a>' if u else label


def _status(m):
    st = m['status']
    if st == 'done':
        bits = [_plink(x['post'], _pl(x['post'].get('views'))) for x in m['parts']]
        return 'st-done', '✓ Вышел · ' + ' + '.join(bits)
    if st == 'partial':
        bits = [(_plink(x['post'], f'«{E(x["part"][:40])}…» — {_pl(x["post"].get("views"))}') if x['post'] else f'«{E(x["part"][:40])}…» — нет') for x in m['parts']]
        return 'st-part', '◐ Вышло частично: ' + '; '.join(bits)
    if st == 'other':
        o = m['other']
        return 'st-other', '↺ Вместо него вышел ' + _plink(o, f'«{E(str(o.get("text", ""))[:60])}…»') + f' · {_pl(o.get("views"))}'
    if st == 'missed':
        return 'st-miss', '✕ Не вышел — постов в этот день не было'
    return '', ''


KIND = {'tax': ('Отчётность', 'dl-tax'), 'pay': ('Платёж', 'dl-pay'), 'grant': ('Конкурс / грант', 'dl-grant')}


def deadlines(dl, today):
    items = [x for x in dl.get('items', []) if x['date'] >= today.isoformat()]
    items = [x for x in items if (_dt.date.fromisoformat(x['date']) - today).days <= 60]
    month = [x for x in items if (_dt.date.fromisoformat(x['date']) - today).days <= 31]
    facts = '\n'.join(f'{_dt.date.fromisoformat(x["date"]):%d.%m} — {x["text"]} ({x["who"]}).' for x in month)
    topic = 'Дедлайны месяца для бизнеса: какие сроки по налогам, отчётности и конкурсам нельзя пропустить в ближайшие 30 дней'
    allbtn = (f'<a class="cp-write dl-all" href="post.html?topic={quote(topic)}&rubric={quote("Дедлайны месяца")}&facts={quote(facts)}">✎ Собрать пост «Дедлайны месяца»</a>' if month else '')
    rows = []
    for x in items:
        d = _dt.date.fromisoformat(x['date'])
        lab, cls = KIND.get(x['kind'], ('Срок', 'dl-tax'))
        days = (d - today).days
        left = 'сегодня' if days == 0 else 'завтра' if days == 1 else f'через {days} дн.'
        t = f'{x["text"]}. Кому: {x["who"]}. Срок — {d:%d.%m.%Y}'
        rows.append(f'<li class="dl-row {cls}" data-date="{x["date"]}"><div class="cp-date"><b>{d.day:02d}.{d.month:02d}</b><span>{WD[d.weekday()]}</span></div>'
                    f'<div class="cp-body"><span class="cp-kind">{lab}</span><span class="dl-left">{left}</span><div class="cp-text">{E(x["text"])}</div>'
                    f'<div class="dl-who">{E(x["who"])} · <a href="{E(x["src"])}" target="_blank" rel="noopener">источник</a></div></div>'
                    f'<a class="cp-write" href="post.html?topic={quote("Напоминание о сроке: " + t)}&rubric={quote("Дедлайны месяца")}&facts={quote(t)}">✎ Написать</a></li>')
    note = (f'<p class="dl-note">ℹ️ {E(dl["note"])} <a href="{E(dl.get("note_url", ""))}" target="_blank" rel="noopener">График отборов 2026</a></p>' if dl.get('note') else '')
    return (f'<div class="lx-card ix cp-card dl-card"><div class="ix-top"><span class="ix-h">Сроки для бизнеса · ближайшие 60 дней</span>{allbtn}</div>'
            f'<p class="ix-sub" style="margin:0">Налоги, отчётность, конкурсы и гранты — готовые поводы для постов. Сроки сверены с налоговым календарём и сайтами организаторов на {_dt.date.fromisoformat(dl.get("updated", today.isoformat())):%d.%m.%Y}; перед публикацией проверьте их ещё раз.</p>'
            f'{note}<ul class="cp-list dl-list">{"".join(rows) if rows else "<li class=ix-sub>Ближайших сроков в календаре нет — пора обновить список.</li>"}</ul></div>')


def build(cp, posts=None, today=None, dl=None):
    import planmatch as _pm
    match, summ = _pm.match(cp.get('plan', []), posts or [], today)
    rows = []
    for idx, it in enumerate(cp.get('plan', [])):
        d = _dt.date.fromisoformat(it['date'])
        lab, cls = _kind(it)
        rows.append(
            f'<li class="cp-row {cls}" data-date="{it["date"]}"><div class="cp-date"><b>{d.day:02d}.{d.month:02d}</b><span>{WD[d.weekday()]}</span></div>'
            f'<div class="cp-body"><span class="cp-kind">{lab}</span><span class="cp-badge"></span><div class="cp-text">{E(it["text"])}</div>'
            + (lambda c, t: f'<div class="cp-st {c}">{t}</div>' if t else '')(*_status(match[idx])) + '</div>'
            f'{_write(it["text"])}</li>')
    sm = summ
    if sm['past']:
        cmp = ''
        if sm['plan_median'] and sm['other_median']:
            cmp = f'<div class="cp-sum-i"><b>{sm["plan_median"]} / {sm["other_median"]}</b><span>медиана просмотров: посты по плану / остальные в эти дни</span></div>'
        sumhtml = (f'<div class="cp-sum"><div class="cp-sum-i"><b>{sm["done"]} из {sm["past"]}</b><span>дней плана выполнено полностью</span></div>'
                   f'<div class="cp-sum-i"><b>{sm["partial"]}</b><span>частично</span></div><div class="cp-sum-i"><b>{sm["missed"]}</b><span>не вышло или заменено</span></div>{cmp}'
                   f'<div class="cp-sum-i"><b>{sm["future"]}</b><span>впереди</span></div></div>')
    else:
        sumhtml = f'<div class="cp-sum"><div class="cp-sum-i"><b>{sm["future"]}</b><span>публикаций впереди. Сверка с вышедшими постами Telegram появится, как только наступит первый день плана.</span></div></div>'
    res = ''.join(f'<li><span class="cp-n">{i}</span><span class="cp-rt">{E(t)}</span>{_write(t)}</li>'
                  for i, t in enumerate(cp.get('reserve', []), 1))
    return f'''<section class="lx-page" id="plan" hidden>
 <div class="cp-wrap">
  <div class="lx-card ix cp-card"><div class="ix-top"><span class="ix-h">План публикаций · {E(cp.get("month", ""))}</span><span class="ix-sub cp-legend"><i class="k-hol"></i>праздник <i class="k-dig"></i>дайджест <i class="k-post"></i>пост</span></div>
   {sumhtml}<ul class="cp-list">{''.join(rows)}</ul></div>
  <div class="lx-card ix cp-card"><div class="ix-top"><span class="ix-h">Резерв тем</span><span class="pill">{len(cp.get("reserve", []))}</span></div>
   <p class="ix-sub" style="margin:0">Темы без даты — берите, когда в плане появляется окно или срывается запланированный пост.</p>
   <ol class="cp-res">{res}</ol></div>
 </div>
 {deadlines(dl, today or _dt.date.today()) if dl else ''}
</section>'''


CSS = '''
.dl-card{margin-top:14px}
.cp-list.dl-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
@media (max-width:900px){.cp-list.dl-list{grid-template-columns:1fr}}
.dl-row{display:flex;gap:14px;align-items:flex-start;padding:12px 14px;border-radius:16px;background:rgba(255,255,255,.5);border:1px solid rgba(123,77,219,.12);border-left:4px solid var(--blue)}
.dl-row.dl-pay{border-left-color:var(--pink)}.dl-row.dl-grant{border-left-color:var(--yellow);background:rgba(253,188,22,.08)}
.dl-left{font-size:11px;font-weight:700;border-radius:999px;padding:2px 8px;background:var(--ac-3);color:var(--ac-deep)}
.dl-who{flex-basis:100%;font-size:12.5px;color:var(--color-fg-muted)}.dl-who a{color:var(--ac)}
.dl-note{margin:0;font-size:13.5px;background:rgba(123,77,219,.07);border-radius:12px;padding:10px 12px;line-height:1.45}.dl-note a{color:var(--ac)}
.dl-all{font-size:13px;padding:8px 14px;background:linear-gradient(135deg,var(--ac),var(--ac-2));color:#fff!important;border:0}
[data-theme="dark"] .dl-row{background:rgba(255,255,255,.05);border-color:rgba(179,155,245,.18)}
.cp-wrap{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:14px;align-items:start}
@media (max-width:900px){.cp-wrap{grid-template-columns:1fr}}
.cp-card{padding:20px;display:flex;flex-direction:column;gap:12px}
.cp-list,.cp-res{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}
.cp-row{display:flex;gap:14px;align-items:flex-start;padding:12px 14px;border-radius:16px;background:rgba(255,255,255,.5);border:1px solid rgba(123,77,219,.12);border-left:4px solid var(--ac-2)}
.cp-row.k-hol{border-left-color:var(--yellow);background:rgba(253,188,22,.10)}
.cp-row.k-dig{border-left-color:var(--sea)}
.cp-row.k-num,.cp-row.k-ev{border-left-color:var(--blue)}
.cp-st{flex-basis:100%;font-size:13px;font-weight:600;border-radius:10px;padding:5px 10px;margin-top:2px}
.cp-st a{color:inherit}
.st-done{background:#dcf5ef;color:#0d6f60}.st-part{background:#fff1cf;color:#8a5a00}.st-other{background:#ece6fb;color:#4a2a9e}.st-miss{background:#fde4e0;color:#a5321f}
[data-theme="dark"] .st-done{background:rgba(63,209,181,.15);color:#7fe6d2}[data-theme="dark"] .st-part{background:rgba(253,188,22,.15);color:#ffd36b}[data-theme="dark"] .st-other{background:rgba(179,155,245,.15);color:#d4c6ff}[data-theme="dark"] .st-miss{background:rgba(255,122,102,.15);color:#ff9e8f}
.cp-sum{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:8px}
.cp-sum-i{background:rgba(123,77,219,.07);border-radius:14px;padding:10px 12px;display:flex;flex-direction:column;gap:2px}
.cp-sum-i b{font-family:var(--font-head);font-size:22px;font-weight:800}
.cp-sum-i span{font-size:12px;color:var(--color-fg-muted);line-height:1.35}
.cp-row.is-today{outline:2px solid var(--ac);background:rgba(123,77,219,.08)}
.cp-date{flex:none;width:52px;text-align:center;font-family:var(--font-head)}
.cp-date b{display:block;font-size:18px;font-weight:800}
.cp-date span{font-size:12px;color:var(--color-fg-muted);text-transform:uppercase}
.cp-body{flex:1;min-width:0;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.cp-kind{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--color-fg-muted)}
.cp-badge:empty{display:none}
.cp-badge{font-size:11px;font-weight:700;border-radius:999px;padding:2px 8px;background:var(--ac);color:#fff}
.cp-text{flex-basis:100%;font-size:15px;line-height:1.4}
.k-hol .cp-text{font-weight:700}
.cp-write{flex:none;align-self:center;font-size:12px;font-weight:600;text-decoration:none;color:var(--ac);border:1px solid rgba(123,77,219,.35);border-radius:999px;padding:5px 10px;white-space:nowrap}
.cp-write:hover{background:var(--ac);color:#fff}
.cp-res li{display:flex;gap:10px;align-items:flex-start;padding:10px 12px;border-radius:14px;background:rgba(255,255,255,.5);border:1px solid rgba(123,77,219,.12)}
.cp-n{flex:none;width:24px;height:24px;border-radius:50%;background:var(--ac-3);color:var(--ac-deep);font-size:12px;font-weight:700;display:inline-flex;align-items:center;justify-content:center}
.cp-rt{flex:1;font-size:14px;line-height:1.4}
.cp-legend{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.cp-legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-left:6px;background:var(--ac-2)}
.cp-legend i.k-hol{background:var(--yellow)}.cp-legend i.k-dig{background:var(--sea)}
[data-theme="dark"] .cp-row,[data-theme="dark"] .cp-res li{background:rgba(255,255,255,.05);border-color:rgba(179,155,245,.18)}
[data-theme="dark"] .cp-n{background:rgba(179,155,245,.2);color:#e6dcff}
'''

JS = r'''
(function(){var t=new Date(),z=function(n){return(n<10?'0':'')+n},td=t.getFullYear()+'-'+z(t.getMonth()+1)+'-'+z(t.getDate()),tm=new Date(t.getTime()+864e5),tmr=tm.getFullYear()+'-'+z(tm.getMonth()+1)+'-'+z(tm.getDate());
document.querySelectorAll('.cp-row').forEach(function(r){var d=r.getAttribute('data-date'),b=r.querySelector('.cp-badge');
 if(d===td){r.classList.add('is-today');b.textContent='сегодня';}else if(d===tmr)b.textContent='завтра';});
var t0=Date.UTC(t.getFullYear(),t.getMonth(),t.getDate());document.querySelectorAll('.dl-row').forEach(function(r){var p=r.getAttribute('data-date').split('-'),n=Math.round((Date.UTC(+p[0],p[1]-1,+p[2])-t0)/864e5),l=r.querySelector('.dl-left');
 if(n<0){r.hidden=true;return;}l.textContent=n===0?'сегодня':n===1?'завтра':'через '+n+' дн.';});})();
'''
