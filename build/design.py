"""Дизайн-доработки сайта: компактная шапка в разделах, таблицы со шкалами, подсказки терминов,
ровная сетка плиток, мобильная навигация снизу, экспорт раздела в PDF, мини-графики в карточках."""

PDF_BTN = ('<button class="nav-pdf" type="button" title="Скачать текущий раздел в PDF" aria-label="Скачать раздел в PDF">'
           '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
           '<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/></svg><span>PDF</span></button>')

CSS = r'''
/* ---------- мини-графики в карточках шапки ---------- */
.kpi-card .spark{display:block;width:100%;height:30px;margin:6px 0 2px}
.spark .sp-l{fill:none;stroke:var(--ac);stroke-width:2;vector-effect:non-scaling-stroke}
.spark .sp-a{fill:var(--ac);opacity:.10}
.spark .sp-d{fill:var(--ac)}
[data-theme="dark"] .spark .sp-l{stroke:#B39BF5}[data-theme="dark"] .spark .sp-a,[data-theme="dark"] .spark .sp-d{fill:#B39BF5}

/* ---------- компактная шапка во всех разделах, кроме «Обзора» ---------- */
body:not([data-tab="overview"]) .site-head.big .hero-title,
body:not([data-tab="overview"]) .site-head.big .hero-sub,
body:not([data-tab="overview"]) .site-head.big .hero-cta,
body:not([data-tab="overview"]) #globe3d{display:none!important}
body:not([data-tab="overview"]) .site-head.big .hero-main{min-height:0!important;padding:0!important;margin-top:6px}
body:not([data-tab="overview"]) .site-head.big .hero-band{padding-bottom:84px!important}
body:not([data-tab="overview"]) .site-head.big .kpi-card .ix-note{display:none}
body:not([data-tab="overview"]) .site-head.big .kpi-card .spark{height:22px;margin:4px 0 0}

/* ---------- кнопка PDF ---------- */
.channels .nav-pdf{display:inline-flex;align-items:center;gap:6px;font:inherit;font-size:14px;font-weight:600;cursor:pointer;border-radius:999px;padding:8px 14px;
 border:1px solid rgba(255,255,255,.35);background:rgba(255,255,255,.12);color:#fff}
.channels .nav-pdf svg{width:16px;height:16px}
.channels .nav-pdf:hover{background:rgba(255,255,255,.22)}

/* ---------- плитки с цифрами: ровная сетка по 4 ---------- */
.lx-tiles{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:12px!important}
.lx-tiles>.lx-tile{min-height:104px;display:flex;flex-direction:column;justify-content:space-between;gap:6px;box-sizing:border-box}
@media (max-width:900px){.lx-tiles{grid-template-columns:repeat(2,minmax(0,1fr))!important}}

/* ---------- описания под заголовками: одна строка, полностью — по нажатию ---------- */
.lx-card>p.lx-muted.clamp{display:-webkit-box;-webkit-line-clamp:1;-webkit-box-orient:vertical;overflow:hidden;cursor:pointer;position:relative;padding-right:52px}
.lx-card>p.lx-muted.clamp::after{content:"ещё";position:absolute;right:0;bottom:0;font-weight:700;color:var(--ac);background:inherit}
.lx-card>p.lx-muted.clamp.open{display:block;-webkit-line-clamp:unset;padding-right:0}
.lx-card>p.lx-muted.clamp.open::after{content:none}

/* ---------- подсказки к терминам ---------- */
abbr.tip{text-decoration:underline dotted;text-underline-offset:3px;text-decoration-color:var(--ac);cursor:help;position:relative;outline:none}
abbr.tip:hover::after,abbr.tip:focus::after{content:attr(data-tip);position:absolute;left:50%;bottom:calc(100% + 8px);transform:translateX(-50%);z-index:60;
 width:max-content;max-width:260px;white-space:normal;text-align:left;font:500 12.5px/1.4 var(--font-anthropic-sans);letter-spacing:0;text-transform:none;
 color:#fff;background:#2a1d55;padding:8px 11px;border-radius:10px;box-shadow:0 10px 26px rgba(20,10,60,.3);pointer-events:none}
abbr.tip:hover::before,abbr.tip:focus::before{content:"";position:absolute;left:50%;bottom:calc(100% + 2px);transform:translateX(-50%);border:6px solid transparent;border-top-color:#2a1d55;z-index:60}

/* ---------- таблицы ---------- */
.lx-tablebox{max-height:560px;overflow:auto;border-radius:12px}
.lx-page table{border-collapse:separate;border-spacing:0;width:100%}
.lx-page table th{position:sticky;top:0;z-index:2;background:#efe9fd;color:#3d2a7a;font-size:12.5px;font-weight:700;text-transform:none}
.lx-page table td,.lx-page table th{padding:8px 10px}
.lx-page table tbody tr:nth-child(even) td{background:rgba(123,77,219,.035)}
.lx-page table tbody tr:hover td{background:rgba(123,77,219,.08)}
.lx-page table .num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.lx-page table td.bar{background-repeat:no-repeat!important}
.lx-page table td.best{font-weight:800;color:var(--ac-deep)}
.lx-page table td.pos{color:#0d8f7b}.lx-page table td.neg{color:#c2412d}
[data-theme="dark"] .lx-page table th{background:#2d2552;color:#e6dcff}
[data-theme="dark"] .lx-page table td.best{color:#d4c6ff}
[data-theme="dark"] .lx-page table td.pos{color:#3fd1b5}[data-theme="dark"] .lx-page table td.neg{color:#ff7a66}

/* ---------- телефон: разделы внизу экрана, крупные кнопки ---------- */
@media (max-width:700px){
 .lx-tabs{position:fixed!important;top:auto!important;bottom:0;left:0;right:0;margin:0!important;z-index:80;border-radius:18px 18px 0 0!important;
  padding:8px 10px calc(8px + env(safe-area-inset-bottom))!important;box-shadow:0 -10px 30px rgba(40,20,90,.18)!important;
  background:color-mix(in srgb,var(--color-bg) 92%,transparent)!important;-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px)}
 .lx-tab{padding:10px 16px!important;font-size:14.5px!important}
 body{padding-bottom:76px}
 .lx-sl-btn{width:46px;height:46px;font-size:26px}
 .lx-more>summary{padding:18px 18px}
 .lx-more>summary b{font-size:17px}
 .lx-tbl-more>summary{padding:10px 16px;font-size:14px}
 .channels .nav-pdf span{display:none}
}

/* ---------- печать / PDF ---------- */
.print-head{display:none}
@media print{
 @page{size:A4;margin:12mm}
 html,body{background:#fff!important;color:#111!important}
 .bg-anim,#bg3d,.lx-tabs,.channels,.hero-cta,#globe3d,.lx-sl-nav,.lx-showall,.vd-hint,.site-foot,.lx-more>summary span,.lx-tbl-more>summary,#lx-nav-anchor{display:none!important}
 .print-head{display:block;font:700 13px/1.4 var(--font-anthropic-sans);color:#555;margin-bottom:8px}
 .site-head.big .hero-band{background:none!important;color:#111!important;padding:0!important;box-shadow:none!important}
 .site-head.big .hero-title,.site-head.big .hero-sub{display:none!important}
 .site-head.big .eyebrow,.topbar{display:none!important}
 .site-head::before,.site-head::after,.hero-band::before,.hero-band::after,.hero-inner::before,.hero-inner::after{display:none!important}
 .site-head.big .hero-band{background-image:none!important}
 .site-head.big .kpi-grid{margin-top:8px!important}
 .ix,.lx-card,.lx-tile,.kpi-card,.vd{box-shadow:none!important;background:#fff!important;border:1px solid #ddd!important;break-inside:avoid;-webkit-backdrop-filter:none!important;backdrop-filter:none!important}
 .lx-sl-track{display:block!important;overflow:visible!important}
 .lx-sl-slide{margin-bottom:12px}
 .lx-tablebox{max-height:none!important;overflow:visible!important}
 .lx-page table th{position:static}
 .lx-more{border:0!important;background:none!important}
 .lx-more>summary b{color:#111!important}
 a{color:#111!important;text-decoration:none!important}
 .lx-card>p.lx-muted.clamp{display:block!important;-webkit-line-clamp:unset!important;padding-right:0!important}
 .lx-card>p.lx-muted.clamp::after{content:none!important}
}
'''

JS = r'''
(function(){
var B=document.body;
function curTab(){var s=document.querySelector('.lx-tab[aria-selected="true"]');return s?s.getAttribute('data-tab'):'overview'}
function setTab(){B.setAttribute('data-tab',curTab())}
setTab();
document.querySelectorAll('.lx-tab').forEach(function(t){t.addEventListener('click',function(){setTimeout(function(){setTab();enhance()},40)})});

/* подсказки терминов */
var TIPS={'ERR':'Доля подписчиков, увидевших пост: просмотры ÷ подписчики','ER':'Вовлечённость: реакции ÷ просмотры',
'PMI':'Индекс деловой активности: выше 50 — рост, ниже 50 — спад','г/г':'К тому же периоду прошлого года',
'МОТ':'По методологии Международной организации труда','ВРП':'Валовой региональный продукт — аналог ВВП для региона',
'МСП':'Малое и среднее предпринимательство','АСИ':'Агентство стратегических инициатив — составляет национальный рейтинг инвестклимата регионов',
'ПМЭФ':'Петербургский международный экономический форум','ИЖС':'Индивидуальное жилищное строительство'};
var RE=/(^|[^A-Za-zА-Яа-яЁё\/])(ERR|ER|PMI|г\/г|МОТ|ВРП|МСП|АСИ|ПМЭФ|ИЖС)(?![A-Za-zА-Яа-яЁё\/])/;
var SEL='.lx-page h2,.lx-page h3,.lx-page .lx-muted,.lx-page th,.lx-tile span,.lx-sub>b,.vd-l,.ix-t,.ix-h,.ix-sub';
function tipify(root){(root||document).querySelectorAll(SEL).forEach(function(el){if(el.closest('abbr,script,svg'))return;
 var w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT,null),n,list=[];while(n=w.nextNode()){if(!n.parentNode.closest('abbr')&&RE.test(n.nodeValue))list.push(n)}
 list.forEach(function(t){var m,v=t.nodeValue,f=document.createDocumentFragment(),guard=0;while((m=RE.exec(v))&&guard++<5){var i=m.index+m[1].length;
  f.appendChild(document.createTextNode(v.slice(0,i)));var a=document.createElement('abbr');a.className='tip';a.tabIndex=0;a.setAttribute('data-tip',TIPS[m[2]]);a.textContent=m[2];f.appendChild(a);v=v.slice(i+m[2].length)}
  f.appendChild(document.createTextNode(v));t.parentNode.replaceChild(f,t)})})}

/* описания в одну строку */
function clamp(){document.querySelectorAll('.lx-page:not([hidden]) .lx-card>p.lx-muted:not([data-cl])').forEach(function(p){if(!p.offsetParent)return;p.setAttribute('data-cl','1');
 var h=p.clientHeight,lh=parseFloat(getComputedStyle(p).lineHeight)||19;if(h>lh*1.6){p.classList.add('clamp');p.title='Нажмите, чтобы прочитать полностью';p.addEventListener('click',function(){p.classList.toggle('open')})}})}

/* таблицы: числа вправо, шкалы, лучшие значения, цвет знака */
function val(t){t=(t||'').replace(/[\s  ]/g,'').replace('−','-').replace('–','-').replace(',','.').replace(/(₽|%|млн|млрд|тыс\.?|руб\.?|п\.п\.|\$)$/,'');return /^[+\-]?\d+(\.\d+)?$/.test(t)?parseFloat(t):null}
function tables(){document.querySelectorAll('.lx-page:not([hidden]) table').forEach(function(tb){var rows=[].slice.call(tb.querySelectorAll('tbody tr'));if(rows.length<2)return;
 var sig=rows.length+'|'+(rows[0].textContent||'').length;if(tb.getAttribute('data-enh')===sig)return;tb.setAttribute('data-enh',sig);
 var hdr=[].slice.call(tb.querySelectorAll('thead th, tr:first-child th')),nc=Math.max.apply(null,rows.map(function(r){return r.children.length}));
 for(var c=1;c<nc;c++){var cells=rows.map(function(r){return r.children[c]}).filter(Boolean),vs=cells.map(function(td){return val(td.textContent)}),ok=vs.filter(function(v){return v!==null});
  if(ok.length<Math.max(2,cells.length*.6))continue;
  if(hdr[c])hdr[c].classList.add('num');var signed=cells.some(function(td){return /^[+\-−]/.test(td.textContent.trim())}),ht=hdr[c]?hdr[c].textContent:'';
  var pctCol=/%|г\/г|к прошл|измен|прирост|рост/i.test(ht);var mx=Math.max.apply(null,ok.map(Math.abs))||1;
  cells.forEach(function(td,i){td.classList.add('num');var v=vs[i];if(v===null)return;
   if(signed){if(!td.querySelector('.lx-up,.lx-down')){td.classList.toggle('pos',v>0);td.classList.toggle('neg',v<0)}}
   else if(!pctCol&&ok.every(function(x){return x>=0})){var p=Math.round(v/mx*100);td.classList.add('bar');td.style.backgroundImage='linear-gradient(270deg, rgba(123,77,219,.18) '+p+'%, transparent '+p+'%)'}
   if(!signed&&v===mx&&ok.length>2)td.classList.add('best')})}})}

var tm;function enhance(){clearTimeout(tm);tm=setTimeout(function(){try{tables();tipify();clamp()}catch(e){console.error(e)}},120)}
enhance();setTimeout(enhance,1500);
new MutationObserver(function(ms){for(var i=0;i<ms.length;i++){if(ms[i].target.closest&&ms[i].target.closest('.lx-page')){enhance();return}}}).observe(document.querySelector('.lx')||B,{childList:true,subtree:true});
document.querySelectorAll('details').forEach(function(d){d.addEventListener('toggle',enhance)});

/* PDF: печать текущего раздела */
var openSaved=[];
function prep(){var tab=document.querySelector('.lx-tab[aria-selected="true"]'),name=tab?tab.textContent.trim():'Обзор',ey=document.querySelector('.eyebrow');
 var ph=document.querySelector('.print-head');if(!ph){ph=document.createElement('div');ph.className='print-head';var h=document.querySelector('.site-head');h.parentNode.insertBefore(ph,h)}
 ph.textContent='Экономика Ленобласти · аналитика — раздел «'+name+'»'+(ey?' · '+ey.textContent.trim():'');
 openSaved=[].filter.call(document.querySelectorAll('.lx-page:not([hidden]) details:not([open])'),function(d){d.open=true;return true});
 document.__t=document.title;document.title='Экономика Ленобласти — '+name;window.dispatchEvent(new Event('resize'))}
function done(){openSaved.forEach(function(d){d.open=false});openSaved=[];if(document.__t)document.title=document.__t;window.dispatchEvent(new Event('resize'))}
window.addEventListener('beforeprint',prep);window.addEventListener('afterprint',done);
document.querySelectorAll('.nav-pdf').forEach(function(b){b.addEventListener('click',function(){prep();setTimeout(function(){window.print()},500)})});
})();
'''

CSS2 = r'''
/* ===== 4. Ритм и типографика ===== */
.lx{gap:28px!important}
.lx-page{display:flex;flex-direction:column;gap:22px}
.lx-grid,.lx-grid3{gap:18px!important}
.lx-card{padding:22px 24px!important;border-radius:20px!important}
.lx-card h3{margin:0 0 4px!important;line-height:1.25;min-height:0}
.lx-card>p.lx-muted{margin:0 0 14px!important}
.ix-sec{margin-top:6px}
.ix-sec-h{font-family:var(--font-head);font-weight:800;letter-spacing:-.015em;margin:0 0 14px}
body{font-feature-settings:"tnum" 1,"cv11" 1;-webkit-font-smoothing:antialiased}
p,li,td{font-weight:400}
.lx-page b,.lx-page strong{font-weight:600}
.lx-page>div:first-child p b{font-weight:800}
.lx-tile .lx-muted,.ix-t,.vd-l,.lx-sub>b{font-weight:600!important;letter-spacing:.01em}
.lx-big,.ix-big,.vd-v,.kpi-card .ix-big{letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.ix-note,.lx-note,.vd-hint{letter-spacing:.005em}
h2,h3{text-wrap:balance}
p{text-wrap:pretty}

/* ===== 6. Фирменная ночная тема ===== */
[data-theme="dark"]{
  --ac:#A98BFF; --ac-2:#C6B2FF; --ac-3:rgba(169,139,255,.16); --ac-deep:#E4DAFF;
  --color-fg:#F1EDFF; --color-fg-muted:#A9A0D0; --color-bg:#0B0720; --color-panel:#150F33;
  --cds-chart-grid:rgba(169,139,255,.10); --cds-chart-axis:rgba(169,139,255,.28);
  --glass:linear-gradient(150deg,rgba(43,30,96,.72),rgba(20,13,50,.66)); --glass-border:rgba(169,139,255,.18);
  --glass-shadow:0 18px 44px rgba(0,0,0,.45),inset 0 1px 0 rgba(198,178,255,.10)}
[data-theme="dark"] body,[data-theme="dark"] html{background:#0B0720}
[data-theme="dark"] .bg-anim{background:radial-gradient(90% 60% at 15% 0%,#2a1670 0%,transparent 60%),radial-gradient(70% 50% at 100% 30%,#3d1a6e 0%,transparent 60%),radial-gradient(80% 60% at 50% 100%,#0a3a4a 0%,transparent 65%),#0B0720!important}
[data-theme="dark"] .hero-band{background:linear-gradient(120deg,#12082f,#2b1470,#5b2fd0,#1aa79b,#12082f)!important;background-size:300% 300%!important;box-shadow:0 30px 80px rgba(91,47,208,.35)!important}
[data-theme="dark"] .lx-card,[data-theme="dark"] .ix,[data-theme="dark"] .lx-tile,[data-theme="dark"] .vd{border-color:rgba(169,139,255,.18)!important}
[data-theme="dark"] .lx-big,[data-theme="dark"] .ix-big,[data-theme="dark"] .vd-v,[data-theme="dark"] .kpi-card .ix-big{color:#fff;text-shadow:0 0 18px rgba(169,139,255,.55),0 0 2px rgba(169,139,255,.6)}
[data-theme="dark"] .vd-good .vd-v{text-shadow:0 0 18px rgba(63,209,195,.45)}
[data-theme="dark"] .vd-bad .vd-v{text-shadow:0 0 18px rgba(255,122,102,.45)}
[data-theme="dark"] .lx-tab[aria-selected="true"]{background:linear-gradient(135deg,#7B4DDB,#A98BFF)!important;box-shadow:0 0 0 1px rgba(198,178,255,.35),0 8px 26px rgba(169,139,255,.45)!important}
[data-theme="dark"] .lx-tab{background:rgba(43,30,96,.55)!important;border-color:rgba(169,139,255,.2)!important;color:#E4DAFF!important}
[data-theme="dark"] .lx-tabs{background:color-mix(in srgb,#0B0720 82%,transparent)!important}
[data-theme="dark"] .lx-card h3::before{box-shadow:0 0 10px #A98BFF}
[data-theme="dark"] a{color:#C6B2FF}
[data-theme="dark"] .lx-sl-btn{background:rgba(43,30,96,.7);color:#C6B2FF;border-color:rgba(169,139,255,.3)}
[data-theme="dark"] .lx-sl-dot.on{box-shadow:0 0 14px rgba(169,139,255,.6)}
[data-theme="dark"] .spark .sp-l{stroke:#C6B2FF;filter:drop-shadow(0 0 4px rgba(169,139,255,.7))}
[data-theme="dark"] .lx-more{background:rgba(169,139,255,.05);border-color:rgba(169,139,255,.3)}
[data-theme="dark"] ::selection{background:#7B4DDB;color:#fff}

/* ===== 8. Живые цифры и графики ===== */
.lx-chart svg rect,.lx-chart svg path,.lx-chart svg circle{transition:filter .15s,opacity .15s}
.lx-chart svg rect:hover{filter:brightness(1.15) saturate(1.2)}
.lx-chart svg:hover rect:not(:hover){opacity:.85}
.lx-chart svg circle:hover{filter:drop-shadow(0 0 6px var(--ac))}
.vbars .vb:hover .vb-b,.hbars .hb:hover i{filter:brightness(1.12)}
@keyframes lxGrow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes lxGrowX{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes lxFade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.lx-anim .lx-chart svg rect{transform-box:fill-box;transform-origin:50% 100%;animation:lxGrow .7s cubic-bezier(.2,.8,.2,1) both}
.lx-anim .lx-chart svg path{animation:lxFade .7s ease both}
.lx-anim .vbars .vb-b{transform-origin:50% 100%;animation:lxGrow .7s cubic-bezier(.2,.8,.2,1) both}
.lx-anim .hbars i,.lx-anim .prog i{transform-origin:0 50%;animation:lxGrowX .8s cubic-bezier(.2,.8,.2,1) both}
.lx-page:not([hidden]){animation:lxFade .35s ease both}
@media (prefers-reduced-motion:reduce){.lx-anim *,.lx-page{animation:none!important}}
'''

JS2 = r'''
(function(){
var RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
/* рост графиков при первом показе раздела */
function anim(sec){if(RM||!sec||sec.__an)return;sec.__an=1;sec.classList.add('lx-anim');setTimeout(function(){sec.classList.remove('lx-anim')},1600)}
function cur(){return document.querySelector('.lx-page:not([hidden])')}
setTimeout(function(){anim(cur())},300);
document.querySelectorAll('.lx-tab').forEach(function(t){t.addEventListener('click',function(){setTimeout(function(){anim(cur())},120)})});
})();
'''
