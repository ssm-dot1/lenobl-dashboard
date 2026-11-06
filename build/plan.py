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


def build(cp):
    rows = []
    for it in cp.get('plan', []):
        d = _dt.date.fromisoformat(it['date'])
        lab, cls = _kind(it)
        rows.append(
            f'<li class="cp-row {cls}" data-date="{it["date"]}"><div class="cp-date"><b>{d.day:02d}.{d.month:02d}</b><span>{WD[d.weekday()]}</span></div>'
            f'<div class="cp-body"><span class="cp-kind">{lab}</span><span class="cp-badge"></span><div class="cp-text">{E(it["text"])}</div></div>'
            f'{_write(it["text"])}</li>')
    res = ''.join(f'<li><span class="cp-n">{i}</span><span class="cp-rt">{E(t)}</span>{_write(t)}</li>'
                  for i, t in enumerate(cp.get('reserve', []), 1))
    return f'''<section class="lx-page" id="plan" hidden>
 <div class="cp-wrap">
  <div class="lx-card ix cp-card"><div class="ix-top"><span class="ix-h">План публикаций · {E(cp.get("month", ""))}</span><span class="ix-sub cp-legend"><i class="k-hol"></i>праздник <i class="k-dig"></i>дайджест <i class="k-post"></i>пост</span></div>
   <ul class="cp-list">{''.join(rows)}</ul></div>
  <div class="lx-card ix cp-card"><div class="ix-top"><span class="ix-h">Резерв тем</span><span class="pill">{len(cp.get("reserve", []))}</span></div>
   <p class="ix-sub" style="margin:0">Темы без даты — берите, когда в плане появляется окно или срывается запланированный пост.</p>
   <ol class="cp-res">{res}</ol></div>
 </div>
</section>'''


CSS = '''
.cp-wrap{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:14px;align-items:start}
@media (max-width:900px){.cp-wrap{grid-template-columns:1fr}}
.cp-card{padding:20px;display:flex;flex-direction:column;gap:12px}
.cp-list,.cp-res{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}
.cp-row{display:flex;gap:14px;align-items:flex-start;padding:12px 14px;border-radius:16px;background:rgba(255,255,255,.5);border:1px solid rgba(123,77,219,.12);border-left:4px solid var(--ac-2)}
.cp-row.k-hol{border-left-color:var(--yellow);background:rgba(253,188,22,.10)}
.cp-row.k-dig{border-left-color:var(--sea)}
.cp-row.k-num,.cp-row.k-ev{border-left-color:var(--blue)}
.cp-row.is-past{opacity:.5}
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
 if(d<td)r.classList.add('is-past');else if(d===td){r.classList.add('is-today');b.textContent='сегодня';}else if(d===tmr)b.textContent='завтра';});})();
'''
