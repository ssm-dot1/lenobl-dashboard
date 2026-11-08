"""Читабельность сайта: второстепенное — в «Подробнее», таблицы под графиками — по кнопке, нефть убрана.

Работает поверх собранного HTML (BeautifulSoup), саму страницу дашборда в Claude не меняет.
"""
from bs4 import BeautifulSoup

REMOVE = ['rf-oil']  # нефть / «бензин» — убрать полностью

# что убрать в «Подробнее» в конце раздела
MORE = {
    'tg': ['tg-quarters', 'tg-format', 'tg-heat', 'tg-topics-r', 'tg-above', 'tg-below', 'tg-sources'],
    'max': ['max-weekday', 'max-heat', 'max-speed', 'max-mention-in', 'max-mention-out'],
    'cmp': ['cmp-vk', 'cmp-goal-charts', 'cmp-quarters', 'cmp-programs', 'cmp-cross'],
    'rf': ['rf-calendar', 'rf-tone', 'rf-credit', 'rf-bankrupt'],
    'lo': ['lo-orgs', 'lo-housing', 'lo-ports', 'lo-asi', 'lo-tone'],
    'co': ['co-own', 'co-tone', 'co-jobs', 'co-growth', 'co-media'],
}
# что поднять наверх раздела (сразу после плиток с цифрами), в этом порядке
FIRST = {
    'rf': ['rf-rate', 'rf-infl', 'rf-gdp'],
    'lo': ['lo-trends', 'lo-grp'],
    'tg': ['tg-monthly-med'],
}
# у этих карточек таблицу под графиком прячем за кнопку
TABLES = ['rf-fx', 'rf-gdp', 'lo-grp', 'lo-neighbors', 'lo-budget', 'cmp-goals', 'cmp-three', 'co-fin', 'co-map']


def _unwrap_empty(el):
    p = el.parent
    el.extract()
    while p is not None and p.name == 'div' and 'lx-grid' in (p.get('class') or []) and not p.find(True):
        q = p.parent
        p.decompose()
        p = q


SLIDES = {  # группы карточек, которые листаются стрелками
    'tg-dyn': ('Динамика просмотров Telegram', ['tg-monthly-med', 'tg-views', 'tg-monthly']),
}


def _slider(soup, title, slides, per=1, cls=''):
    wrap = soup.new_tag('div', attrs={'class': ('lx-slider ' + cls).strip(), 'data-per': str(per)})
    head = soup.new_tag('div', attrs={'class': 'lx-sl-head'})
    if title:
        t = soup.new_tag('b', attrs={'class': 'lx-sl-title'})
        t.string = title
        head.append(t)
    nav = soup.new_tag('div', attrs={'class': 'lx-sl-nav'})
    prev = soup.new_tag('button', attrs={'type': 'button', 'class': 'lx-sl-btn prev', 'aria-label': 'Назад'})
    prev.string = '‹'
    nxt = soup.new_tag('button', attrs={'type': 'button', 'class': 'lx-sl-btn next', 'aria-label': 'Вперёд'})
    nxt.string = '›'
    dots = soup.new_tag('div', attrs={'class': 'lx-sl-dots'})
    nav.append(prev); nav.append(dots); nav.append(nxt)
    head.append(nav)
    track = soup.new_tag('div', attrs={'class': 'lx-sl-track'})
    for sl in slides:
        box = soup.new_tag('div', attrs={'class': 'lx-sl-slide'})
        h = sl.find(['h3', 'b'])
        box['data-label'] = h.get_text(strip=True)[:40] if h else ''
        sl.extract()
        box.append(sl)
        track.append(box)
    wrap.append(head)
    wrap.append(track)
    return wrap


def apply(html):
    soup = BeautifulSoup(html, 'lxml')
    pl = soup.select_one('#cmp-platforms [data-source="platforms"]')
    if pl:
        pl['data-source'] = 'platforms_last'
    for cid in REMOVE:
        el = soup.find(id=cid)
        if el:
            _unwrap_empty(el)

    for sid, ids in FIRST.items():
        sec = soup.find('section', id=sid)
        if not sec:
            continue
        anchor = sec.find('div', class_='lx-tiles') or sec.find('p', class_='lx-note') or sec.find('div')
        for cid in ids:
            el = soup.find(id=cid)
            if el and anchor:
                _unwrap_empty(el)
                anchor.insert_after(el)
                anchor = el

    # карусели
    for key, (title, ids) in SLIDES.items():
        els = [soup.find(id=c) for c in ids]
        els = [e for e in els if e]
        if len(els) < 2:
            continue
        anchor = els[0]
        ph = soup.new_tag('div')
        anchor.insert_before(ph)
        for e in els:
            if e is not anchor:
                _unwrap_empty(e)
        ph.replace_with(_slider(soup, title, els, 1, 'lx-sl-cards'))
    tr = soup.select_one('#lo-trends .lx-grid3')
    if tr:
        subs = tr.find_all('div', class_='lx-sub', recursive=False)
        for sub in subs:
            ch = sub.find(attrs={'data-h': True})
            if ch:
                ch['data-h'] = '210'
        sl = _slider(soup, '', subs, 3, 'lx-sl-inner')
        tr.replace_with(sl)

    for cid in TABLES:
        card = soup.find(id=cid)
        if not card:
            continue
        for box in card.find_all('div', class_='lx-tablebox', recursive=True):
            if not card.select('[data-draw]:not(table):not(tbody):not(tr)') or box.find_parent('details'):
                continue
            det = soup.new_tag('details', attrs={'class': 'lx-tbl-more'})
            sm = soup.new_tag('summary')
            sm.string = 'Показать таблицу'
            box.wrap(det)
            det.insert(0, sm)

    for sid, ids in MORE.items():
        sec = soup.find('section', id=sid)
        if not sec:
            continue
        els = [soup.find(id=c) for c in ids]
        els = [e for e in els if e]
        if not els:
            continue
        titles = [(e.find(['h3', 'h2']).get_text(strip=True) if e.find(['h3', 'h2']) else '') for e in els]
        det = soup.new_tag('details', attrs={'class': 'lx-more'})
        sm = soup.new_tag('summary')
        b = soup.new_tag('b')
        b.string = f'Подробнее · ещё {len(els)} {"блок" if len(els) == 1 else ("блока" if len(els) < 5 else "блоков")}'
        sm.append(b)
        sp = soup.new_tag('span')
        sp.string = ', '.join(t for t in titles if t)
        sm.append(sp)
        det.append(sm)
        inner = soup.new_tag('div', attrs={'class': 'lx-more-in'})
        det.append(inner)
        for e in els:
            _unwrap_empty(e)
            inner.append(e)
        sec.append(det)
    return str(soup)


CSS = '''
/* ---- читабельность ---- */
.site-head.big .hero-band{padding-bottom:96px}
.site-head.big .hero-title{font-size:clamp(34px,4.6vw,62px)!important;line-height:1.02}
.site-head.big .hero-sub{font-size:clamp(14px,1.2vw,17px)!important}
#globe3d{max-height:300px}
.lx-page>div:first-child h2{font-family:var(--font-head);font-size:clamp(24px,2.4vw,32px);font-weight:800;letter-spacing:-.01em;margin:0 0 6px}
.lx-page>div:first-child p{font-size:17px;line-height:1.5;max-width:920px;margin:0}
.lx-page>div:first-child p b{color:var(--ac-deep);font-weight:800}
[data-theme="dark"] .lx-page>div:first-child p b{color:#d4c6ff}
.lx-note{font-size:12px!important;opacity:.75}
.lx-card h3{font-family:var(--font-head);font-size:18px;font-weight:800;letter-spacing:-.005em}
.lx-card .lx-muted,.lx-card>p{font-size:13px;line-height:1.45}
.lx-tile .lx-big{font-size:clamp(26px,2.4vw,34px);font-weight:800;font-family:var(--font-head)}
.lx-tile .lx-muted{font-size:12.5px}
.lx-up{color:#0d8f7b!important}.lx-down{color:#c2412d!important}
[data-theme="dark"] .lx-up{color:#3fd1b5!important}[data-theme="dark"] .lx-down{color:#ff7a66!important}
.lx-tbl-more{margin-top:10px}
.lx-tbl-more>summary{cursor:pointer;display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:600;color:var(--ac);list-style:none;padding:6px 12px;border-radius:999px;background:rgba(123,77,219,.08)}
.lx-tbl-more>summary::-webkit-details-marker{display:none}
.lx-tbl-more>summary::before{content:"▸";transition:transform .2s}
.lx-tbl-more[open]>summary::before{transform:rotate(90deg)}
.lx-tbl-more[open]>summary{margin-bottom:10px}
.lx-more{margin-top:8px;border-radius:20px;border:1px dashed rgba(123,77,219,.35);background:rgba(123,77,219,.04)}
.lx-more>summary{cursor:pointer;list-style:none;padding:16px 20px;display:flex;flex-direction:column;gap:3px}
.lx-more>summary::-webkit-details-marker{display:none}
.lx-more>summary b{font-family:var(--font-head);font-size:16px;font-weight:800;color:var(--ac)}
.lx-more>summary b::after{content:"  ▾";font-size:13px}
.lx-more[open]>summary b::after{content:"  ▴"}
.lx-more>summary span{font-size:13px;color:var(--color-fg-muted);line-height:1.4}
.lx-more-in{display:flex;flex-direction:column;gap:22px;padding:4px 14px 18px}
/* фон блоков в «Подробнее» */
.lx-more-in .lx-card{background:#f3eefe!important;border:1px solid rgba(123,77,219,.2)!important;box-shadow:none!important}
.lx-more-in .lx-card table th{background:rgba(123,77,219,.10)}
.lx-more-in .lx-card table tr:nth-child(even) td{background:rgba(255,255,255,.55)}
[data-theme="dark"] .lx-more-in .lx-card{background:rgba(179,155,245,.09)!important;border-color:rgba(179,155,245,.22)!important}
[data-theme="dark"] .lx-more-in .lx-card table th{background:rgba(179,155,245,.14)}
[data-theme="dark"] .lx-more-in .lx-card table tr:nth-child(even) td{background:rgba(255,255,255,.03)}
/* карусели со стрелками */
.lx-slider{display:flex;flex-direction:column;gap:10px;min-width:0}
.lx-sl-head{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.lx-sl-title{font-family:var(--font-head);font-size:20px;font-weight:800}
.lx-sl-nav{display:flex;align-items:center;gap:8px;margin-left:auto}
.lx-sl-btn{width:38px;height:38px;border-radius:50%;border:1px solid rgba(123,77,219,.3);background:var(--glass);color:var(--ac);font:800 22px/1 var(--font-head);cursor:pointer;display:inline-flex;align-items:center;justify-content:center;box-shadow:var(--glass-shadow)}
.lx-sl-btn:hover:not(:disabled){background:var(--ac);color:#fff}
.lx-sl-btn:disabled{opacity:.35;cursor:default}
.lx-sl-dots{display:flex;gap:6px;flex-wrap:wrap}
.lx-sl-dot{font:inherit;font-size:12.5px;font-weight:600;border:1px solid rgba(123,77,219,.25);background:transparent;color:var(--color-fg-muted);border-radius:999px;padding:5px 11px;cursor:pointer}
.lx-sl-dot.on{background:var(--ac);border-color:var(--ac);color:#fff}
.lx-sl-dot.num{width:10px;height:10px;padding:0;border-radius:50%;background:rgba(123,77,219,.25);border:0}
.lx-sl-dot.num.on{background:var(--ac)}
.lx-sl-track{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;scroll-behavior:smooth;scrollbar-width:none;padding:2px 2px 10px}
.lx-sl-track::-webkit-scrollbar{display:none}
.lx-sl-slide{flex:0 0 100%;scroll-snap-align:start;min-width:0}
.lx-slider[data-per="3"] .lx-sl-slide{flex-basis:calc((100% - 28px)/3)}
@media (max-width:1000px){.lx-slider[data-per="3"] .lx-sl-slide{flex-basis:calc((100% - 14px)/2)}}
@media (max-width:640px){.lx-slider[data-per="3"] .lx-sl-slide{flex-basis:100%}.lx-sl-dot:not(.num){padding:4px 9px;font-size:12px}}
.lx-sl-inner .lx-sl-slide{background:rgba(123,77,219,.05);border-radius:16px;padding:12px}
.lx-sl-inner .lx-sl-head{justify-content:flex-end}
.lx-sl-cards .lx-sl-slide>.lx-card{height:100%;box-sizing:border-box}
/* «Главное сейчас» */
.vd-sec .ix-sec-h{font-size:clamp(22px,2vw,28px)}
.vd-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
@media (max-width:1000px){.vd-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:600px){.vd-grid{grid-template-columns:1fr}}
.vd{display:flex;flex-direction:column;gap:4px;padding:18px 20px;border-radius:20px;text-decoration:none;color:var(--color-fg);background:var(--glass);border:1px solid var(--glass-border);box-shadow:var(--glass-shadow);border-left:6px solid #8a84a3;transition:transform .15s}
.vd:hover{transform:translateY(-2px)}
.vd-l{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--color-fg-muted)}
.vd-v{font-family:var(--font-head);font-size:clamp(30px,3vw,40px);font-weight:800;line-height:1.1;display:flex;align-items:center;gap:8px}
.vd-v i{font-style:normal;font-size:.5em}
.vd-t{font-size:14px;line-height:1.45}
.vd-good{border-left-color:#12AA9E}.vd-good .vd-v i{color:#12AA9E}
.vd-bad{border-left-color:#d24b3a}.vd-bad .vd-v i{color:#d24b3a}
.vd-warn{border-left-color:#FDBC16}.vd-warn .vd-v i{color:#e0a400}
.vd-neutral{border-left-color:var(--ac)}.vd-neutral .vd-v i{color:var(--ac)}
.vd-hint{font-size:12.5px;color:var(--color-fg-muted);margin:8px 0 0}
/* «Главное за месяц»: первые 4 пункта, остальное по кнопке */
#summary .lx-list:not(.all)>li:nth-child(n+5){display:none}
.lx-showall{margin-top:10px;font:inherit;font-size:13px;font-weight:600;color:var(--ac);background:rgba(123,77,219,.08);border:0;border-radius:999px;padding:6px 12px;cursor:pointer}
'''

JS = r'''
(function(){
document.querySelectorAll('details.lx-more,details.lx-tbl-more').forEach(function(d){d.addEventListener('toggle',function(){if(d.open)setTimeout(function(){window.dispatchEvent(new Event('resize'))},30)})});
document.querySelectorAll('a[data-tab-link]').forEach(function(a){a.addEventListener('click',function(e){var t=document.querySelector('.lx-tab[data-tab="'+a.getAttribute('data-tab-link')+'"]');if(t){e.preventDefault();t.click();var n=document.getElementById('lx-nav-anchor');if(n)window.scrollTo({top:n.getBoundingClientRect().top+window.scrollY,behavior:'smooth'});}})});
document.querySelectorAll('.lx-slider').forEach(function(w){var tr=w.querySelector('.lx-sl-track'),sl=[].slice.call(tr.children),per=+w.getAttribute('data-per')||1,dots=w.querySelector('.lx-sl-dots'),pv=w.querySelector('.prev'),nx=w.querySelector('.next');
 function perNow(){var a=tr.clientWidth,b=sl[0].getBoundingClientRect().width;return (a&&b)?Math.max(1,Math.round(a/b)):per}
 function pages(){return Math.max(1,Math.ceil(sl.length/perNow()))}
 function cur(){var w0=sl[0].getBoundingClientRect().width+14;return w0>14?Math.round(tr.scrollLeft/(w0*perNow())):0}
 function go(i){var p=Math.max(0,Math.min(pages()-1,i));var w0=sl[0].getBoundingClientRect().width+14;tr.scrollTo({left:p*w0*perNow()})}
 function draw(){dots.innerHTML='';var n=pages(),labels=per===1;for(var i=0;i<n;i++){var b=document.createElement('button');b.type='button';b.className='lx-sl-dot'+(labels?'':' num');if(labels)b.textContent=sl[i].getAttribute('data-label')||String(i+1);b.setAttribute('aria-label','Слайд '+(i+1));(function(k){b.addEventListener('click',function(){go(k)})})(i);dots.appendChild(b)}upd()}
 function upd(){var c=cur(),n=pages();[].forEach.call(dots.children,function(d,i){d.classList.toggle('on',i===c)});pv.disabled=c<=0;nx.disabled=c>=n-1}
 pv.addEventListener('click',function(){go(cur()-1)});nx.addEventListener('click',function(){go(cur()+1)});
 var t;tr.addEventListener('scroll',function(){clearTimeout(t);t=setTimeout(upd,80)});window.addEventListener('resize',function(){clearTimeout(t);t=setTimeout(draw,120)});document.querySelectorAll('.lx-tab').forEach(function(x){x.addEventListener('click',function(){setTimeout(draw,60)})});draw();});
var s=document.querySelector('#summary .lx-list');if(s){var b=document.createElement('button');b.type='button';b.className='lx-showall';b.textContent='Показать все выводы';
 b.addEventListener('click',function(){var on=s.classList.toggle('all');b.textContent=on?'Свернуть':'Показать все выводы'});s.parentNode.appendChild(b);
 setTimeout(function(){if(s.children.length<=4)b.remove()},3000);}
})();
'''
