"""Вкладка «Меры поддержки»: основные меры РФ и Ленобласти, «!» открывает подробности."""
import html as _h
import json
from urllib.parse import quote

E = _h.escape
LEVEL = {'rf': 'РФ', 'lo': 'Ленобласть'}


def _facts(x):
    lines = [x['title'] + ': ' + x['short'] + '.'] + [w + '.' for w in x.get('what', [])]
    lines.append('Кому: ' + x.get('who', '') + '.')
    lines += ['Условие: ' + c + '.' for c in x.get('conditions', [])]
    if x.get('how'):
        lines.append('Как получить: ' + x['how'] + '.')
    if x.get('status'):
        lines.append('Статус: ' + x['status'] + '.')
    return '\n'.join(l.replace('..', '.') for l in lines)[:2400]


def build(dm):
    items = dm.get('items', [])
    cards = []
    for x in items:
        cards.append(
            f'<article class="ix ms-card" data-level="{x["level"]}" data-id="{E(x["id"])}">'
            f'<div class="ms-top"><span class="ms-lv ms-{x["level"]}">{LEVEL[x["level"]]}</span><span class="ms-cat">{E(x["cat"])}</span>'
            f'<button type="button" class="ms-info" data-id="{E(x["id"])}" aria-label="Подробнее: {E(x["title"])}" title="Подробнее">!</button></div>'
            f'<h3 class="ms-title">{E(x["title"])}</h3><p class="ms-short">{E(x["short"])}</p>'
            f'<div class="ms-key">{E(x.get("key", ""))}</div>'
            + (f'<div class="ms-status">⏸ {E(x["status"])}</div>' if x.get('status') else '') +
            '</article>')
    data = {x['id']: {k: x.get(k) for k in ('level', 'cat', 'title', 'short', 'key', 'what', 'who', 'conditions', 'how', 'operator', 'law', 'status', 'url')} for x in items}
    for x in items:
        data[x['id']]['write'] = ('post.html?topic=' + quote('Мера поддержки для бизнеса: ' + x['title'] + ' — кому подходит, что даёт и как получить')
                                  + '&rubric=' + quote('Меры поддержки') + '&facts=' + quote(_facts(x)))
    js_data = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    n_rf = sum(1 for x in items if x['level'] == 'rf')
    return f'''<section class="lx-page" id="support" hidden>
 <div class="ms-head">
  <div class="ms-filters" role="group" aria-label="Уровень">
   <button type="button" class="ms-f on" data-f="all">Все <b>{len(items)}</b></button>
   <button type="button" class="ms-f" data-f="rf">РФ <b>{n_rf}</b></button>
   <button type="button" class="ms-f" data-f="lo">Ленобласть <b>{len(items) - n_rf}</b></button>
  </div>
  <p class="ix-sub">Основные меры для бизнеса и инвесторов. Нажмите <span class="ms-info demo">!</span>, чтобы открыть подробности. Условия на {E(dm.get("updated", "")[8:10])}.{E(dm.get("updated", "")[5:7])}.{E(dm.get("updated", "")[:4])} — перед подачей уточняйте у оператора.</p>
 </div>
 <div class="ms-grid">{"".join(cards)}</div>
 <dialog class="ms-dlg" aria-labelledby="ms-dlg-t"><div class="ms-dlg-in">
  <button type="button" class="ms-x" aria-label="Закрыть">×</button>
  <div class="ms-top"><span class="ms-lv"></span><span class="ms-cat"></span></div>
  <h3 id="ms-dlg-t" class="ms-title"></h3><p class="ms-short"></p><div class="ms-key"></div>
  <div class="ms-body"></div>
  <div class="ms-act"><a class="cp-write ms-write" href="#">✎ Написать пост об этой мере</a><a class="ms-src" target="_blank" rel="noopener">Источник ↗</a></div>
 </div></dialog>
 <script type="application/json" id="ms-data">{js_data}</script>
</section>'''


CSS = '''
.ms-head{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px;margin-bottom:12px}
.ms-head .ix-sub{margin:0;max-width:640px}
.ms-filters{display:flex;gap:6px;flex-wrap:wrap}
.ms-f{font:inherit;font-size:14px;font-weight:600;border:1px solid rgba(123,77,219,.3);background:var(--glass);color:var(--color-fg);border-radius:999px;padding:7px 14px;cursor:pointer}
.ms-f b{font-weight:700;color:var(--color-fg-muted);margin-left:4px}
.ms-f.on{background:var(--ac);border-color:var(--ac);color:#fff}.ms-f.on b{color:rgba(255,255,255,.8)}
.ms-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
@media (max-width:1000px){.ms-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:640px){.ms-grid{grid-template-columns:1fr}}
.ms-card{padding:18px 20px;gap:8px}
.ms-card[hidden]{display:none}
.ms-top{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.ms-lv{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.04em;border-radius:999px;padding:3px 9px}
.ms-rf{background:#e3e9fb;color:#153F9B}.ms-lo{background:var(--ac-3);color:var(--ac-deep)}
.ms-cat{font-size:12px;color:var(--color-fg-muted);font-weight:600}
.ms-info{margin-left:auto;flex:none;width:30px;height:30px;border-radius:50%;border:0;background:var(--yellow);color:#2a1b00;font:800 16px/1 var(--font-head);cursor:pointer;display:inline-flex;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(253,188,22,.45)}
.ms-info:hover{transform:scale(1.08)}
.ms-info:focus-visible{outline:3px solid var(--ac);outline-offset:2px}
.ms-info.demo{display:inline-flex;width:20px;height:20px;font-size:12px;margin:0 2px;vertical-align:-4px;box-shadow:none;cursor:default}
.ms-title{font-family:var(--font-head);font-size:18px;font-weight:800;line-height:1.25;margin:2px 0 0}
.ms-short{margin:0;font-size:14px;line-height:1.45;color:var(--color-fg-muted)}
.ms-key{margin-top:auto;align-self:flex-start;font-family:var(--font-head);font-weight:800;font-size:15px;color:var(--ac-deep);background:rgba(123,77,219,.09);border-radius:10px;padding:6px 10px}
.ms-status{font-size:12.5px;color:#8a5a00;background:rgba(253,188,22,.16);border-radius:10px;padding:5px 9px}
.ms-dlg{border:0;border-radius:22px;padding:0;max-width:640px;width:calc(100% - 32px);background:var(--color-panel,#fff);color:var(--color-fg);box-shadow:0 30px 80px rgba(20,10,60,.35)}
.ms-dlg::backdrop{background:rgba(20,12,50,.45);-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px)}
.ms-dlg-in{position:relative;padding:26px 28px 22px;display:flex;flex-direction:column;gap:10px;max-height:min(84vh,780px);overflow:auto}
.ms-x{position:absolute;top:12px;right:14px;width:34px;height:34px;border-radius:50%;border:0;background:rgba(123,77,219,.1);color:var(--color-fg);font-size:22px;line-height:1;cursor:pointer}
.ms-dlg .ms-title{font-size:22px;padding-right:36px}
.ms-dlg .ms-key{margin-top:2px}
.ms-body h4{margin:12px 0 4px;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.04em;color:var(--ac)}
.ms-body ul{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:5px;font-size:14.5px;line-height:1.45}
.ms-body p{margin:0;font-size:14.5px;line-height:1.45}
.ms-act{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:8px;padding-top:12px;border-top:1px solid rgba(123,77,219,.15)}
.ms-src{font-size:13px;font-weight:600;color:var(--ac)}
.ms-write{font-size:13px;padding:8px 14px;background:linear-gradient(135deg,var(--ac),var(--ac-2));color:#fff!important;border:0}
[data-theme="dark"] .ms-rf{background:rgba(127,164,255,.18);color:#bcd0ff}[data-theme="dark"] .ms-lo{background:rgba(179,155,245,.18);color:#e6dcff}
[data-theme="dark"] .ms-key{color:#e6dcff;background:rgba(179,155,245,.14)}
[data-theme="dark"] .ms-status{color:#ffd36b}
[data-theme="dark"] .ms-dlg{background:#1b1636}
'''

JS = r'''
(function(){var D;try{D=JSON.parse(document.getElementById('ms-data').textContent)}catch(e){return}
var cards=document.querySelectorAll('.ms-card'),dlg=document.querySelector('.ms-dlg');
document.querySelectorAll('.ms-f').forEach(function(b){b.addEventListener('click',function(){var f=b.getAttribute('data-f');
 document.querySelectorAll('.ms-f').forEach(function(x){x.classList.toggle('on',x===b)});
 cards.forEach(function(c){c.hidden=!(f==='all'||c.getAttribute('data-level')===f)});});});
function esc(s){var d=document.createElement('div');d.textContent=s==null?'':String(s);return d.innerHTML}
function list(a){return a&&a.length?'<ul>'+a.map(function(x){return'<li>'+esc(x)+'</li>'}).join('')+'</ul>':''}
var last=null;
function open(id,btn){var x=D[id];if(!x||!dlg)return;last=btn;
 var lv=dlg.querySelector('.ms-lv');lv.textContent=x.level==='rf'?'РФ':'Ленобласть';lv.className='ms-lv ms-'+x.level;
 dlg.querySelector('.ms-cat').textContent=x.cat;dlg.querySelector('.ms-title').textContent=x.title;
 dlg.querySelector('.ms-short').textContent=x.short;dlg.querySelector('.ms-key').textContent=x.key||'';
 var h='<h4>Что даёт</h4>'+list(x.what)+'<h4>Кому</h4><p>'+esc(x.who)+'</p>'+(x.conditions&&x.conditions.length?'<h4>Условия</h4>'+list(x.conditions):'')+
  '<h4>Как получить</h4><p>'+esc(x.how)+'</p><h4>Кто оператор</h4><p>'+esc(x.operator)+(x.law?' · '+esc(x.law):'')+'</p>'+(x.status?'<h4>Статус</h4><p>'+esc(x.status)+'</p>':'');
 dlg.querySelector('.ms-body').innerHTML=h;dlg.querySelector('.ms-write').href=x.write;
 var s=dlg.querySelector('.ms-src');s.href=x.url;
 if(dlg.showModal){dlg.showModal()}else{dlg.setAttribute('open','')}dlg.querySelector('.ms-x').focus();}
document.querySelectorAll('.ms-card .ms-info').forEach(function(b){b.addEventListener('click',function(){open(b.getAttribute('data-id'),b)})});
if(dlg){dlg.querySelector('.ms-x').addEventListener('click',function(){dlg.close?dlg.close():dlg.removeAttribute('open')});
 dlg.addEventListener('click',function(e){if(e.target===dlg)dlg.close()});
 dlg.addEventListener('close',function(){if(last)last.focus()});}
})();
'''
