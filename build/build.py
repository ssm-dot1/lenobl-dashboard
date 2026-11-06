import json
ids_unused=['rf_infl_week','rf_infl_month','rf_pmi','rf_rates','rf_loans','rf_bankrupt','lo_orgs','lo_housing','lo_neighbors','lo_ports','lo_asi','lo_budget','lo_budget_struct','tg_sources','tg_sources_sum','peer_gaps','content_calendar','gdp_rf','grp_lo','grp_structure','content_ideas','rubric_ideas','abbr_ideas','oil','tg_subs_daily','company_tenders','lo_districts','company_geo','media_programs','vk_posts','tg_monthly','platforms','goals','fx','lo_series','company_fin','company_jobs','programs','insights','tg_posts','tg_history','tg_posts_history','max_summary','max_daily','max_posts','max_heatmap','max_content_mix','max_posts_full','max_mentions','macro','key_rate','news_rf','news_lo','companies','events','tg_peers']
import os
B=os.path.dirname(os.path.abspath(__file__)); RT=os.path.dirname(B)
ids=[l.strip() for l in open(os.path.join(B,'datasets.txt')) if l.strip()]
data={i:json.load(open(os.path.join(RT,'data',i+'.json'))) for i in ids}
body=open(os.path.join(B,'page_body.html')).read(); scripts=open(os.path.join(B,'page_scripts.js')).read()
head='''<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Аналитика: каналы, экономика РФ и Ленобласти</title>
<script src="d3.min.js"></script>
<style>
:root{--font-anthropic-sans:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;--font-anthropic-serif:Georgia,"Times New Roman",serif;
--color-fg:#1f1e1c;--color-fg-muted:#6b6862;--color-bg:#faf9f6;--color-panel:#ffffff;--color-border-line:#e4e1da;--color-ok:#2e7d4f;--color-warn:#a86a12;--color-bad:#c2412d;
--cds-font-size-caption:12.5px;--cds-font-size-body:15px;--cds-font-size-heading:18px;--cds-font-size-title:28px;--cds-font-weight-medium:600;
--cds-gap-xs:4px;--cds-gap-sm:8px;--cds-gap-md:12px;--cds-gap-lg:20px;--cds-pad-xs:4px;--cds-pad-sm:8px;--cds-pad-md:12px;--cds-pad-lg:16px;--cds-radius:8px;
--cds-chart-muted:#cfcac0;--cds-chart-grid:#ece9e3;--cds-chart-axis:#bdb8ae;--cds-surface-popover:#fff;--cds-border:#e4e1da;--cds-shadow-popover:0 4px 16px rgba(0,0,0,.12);--cds-text-secondary:#6b6862;--cds-dur-slow:.3s}
@media (prefers-color-scheme: dark){:root{--color-fg:#ecebe7;--color-fg-muted:#a5a29b;--color-bg:#1d1c1a;--color-panel:#262523;--color-border-line:#3a3936;--color-ok:#6cc58f;--color-warn:#e0a54a;--color-bad:#ef7d6a;--cds-chart-muted:#55534e;--cds-chart-grid:#33322f;--cds-chart-axis:#55534e;--cds-surface-popover:#2e2d2a;--cds-border:#3a3936;--cds-text-secondary:#a5a29b}}
html,body{margin:0;background:var(--color-bg);color:var(--color-fg)}
.wrap{max-width:1200px;margin:0 auto;padding:24px clamp(12px,3vw,32px) 48px}
.dash-skeleton:empty{background:linear-gradient(90deg,var(--color-panel),var(--cds-chart-grid),var(--color-panel));background-size:200% 100%;animation:sk 1.4s infinite;border-radius:var(--cds-radius)}
@keyframes sk{0%{background-position:200% 0}100%{background-position:-200% 0}}
</style>
<script>
window.__DATA = __DATA__;
(function(){
  const calcs = {}, draws = {}, cache = {};
  const data = (id) => {
    if (id in window.__DATA) return {status: 'ok', data: window.__DATA[id]};
    if (calcs[id]) { if (!(id in cache)) { try { cache[id] = calcs[id].fn(...calcs[id].inputs.map(i => data(i).data)); } catch (e) { console.error(id, e); cache[id] = null; } }
      return cache[id] ? {status: 'ok', data: cache[id]} : {status: 'error', data: []}; }
    return {status: 'missing', data: []};
  };
  const run = () => { for (const [n, f] of Object.entries(draws)) document.querySelectorAll('[data-draw="' + n + '"]').forEach(el => { if (el.closest('[hidden]')) return; try { f(el); } catch (e) { console.error(n, e); } }); };
  window.dash = {data, calc: (id, o) => { calcs[id] = o; }, draw: (n, f) => { draws[n] = f; }, onData: () => {}, colors: ['#3a6fd8', '#d9822b', '#2e9e6b', '#9b59b6', '#c2412d', '#1f9bb3', '#b8860b', '#7f8c8d'],
    setLink: (id) => { try { history.replaceState(null, '', '#' + id); } catch (e) {} setTimeout(run, 0); }, params: () => ({}), setParams() {}, resetParams() {}, refresh() {}, loader() {}};
  window.addEventListener('load', run);
  let rt; window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(run, 150); });
})();
</script>
</head><body><div class="wrap">
'''.replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
html=head+body+'\n<script>\n'+scripts+'\n</script>\n</div></body></html>\n'

# ---- Оформление публичного сайта (фирменный стиль АЭРЛО) ----
import re, html as _h
def _last(rows, key):
    rows=[r for r in rows if r.get(key) is not None]
    return rows[-1] if rows else {}
def _fmt(v, d=0):
    s=f"{v:,.{d}f}".replace(',', ' ').replace('.', ',')
    return s
plat={}
for r in data.get('platforms', []): plat[r['platform']]=r
fx=_last(data.get('fx', []), 'usd'); oil=_last(data.get('oil', []), 'brent')
ms=_last(data.get('max_summary', []), 'at'); _at=str(ms.get('at',''))
upd=(_at[8:10]+'.'+_at[5:7]+'.'+_at[:4]+', '+_at[11:16]+' МСК') if len(_at)>=16 else ''
kr=next((m for m in data.get('macro', []) if m.get('indicator')=='key_rate'), {})
def _kpi(k, v, d=''):
    return f'<div class="kpi"><div class="k">{_h.escape(k)}</div><div class="v">{v}</div><div class="d">{_h.escape(d)}</div></div>'
kpis=''.join([
  _kpi('Telegram', _fmt(plat.get('Telegram',{}).get('subscribers',0)), 'подписчиков'),
  _kpi('MAX', _fmt(plat.get('MAX',{}).get('subscribers',0)), 'подписчиков'),
  _kpi('ВКонтакте', '≈'+_fmt(plat.get('ВКонтакте',{}).get('subscribers',0)), 'подписчиков'),
  _kpi('Ключевая ставка', _fmt(kr.get('value',0), 0)+'%', 'Банк России'),
  _kpi('Доллар', _fmt(fx.get('usd',0), 2)+' ₽', 'курс ЦБ на '+'.'.join(reversed(str(fx.get('date','')).split('-')))),
  _kpi('Нефть Brent', _fmt(oil.get('brent',0), 2)+' $', 'Мосбиржа'),
])
import sys; sys.path.insert(0, B)
import overview as _ov
_hero_kpis, _overview = _ov.build(data)
import postgen as _pg
_cfg=json.load(open(os.path.join(B,'config.json'))) if os.path.exists(os.path.join(B,'config.json')) else {}
header=f"""<header class="site-head big">
  <div class="hero-band">
    <div class="hero-inner">
      <div class="topbar"><div class="brand"><span class="brand-dot"></span>Экономика Ленобласти · аналитика</div>
  <div class="channels"><a href="https://t.me/lenoblinvest" target="_blank" rel="noopener">Telegram</a><a href="https://max.ru/id4703059140_gos" target="_blank" rel="noopener">MAX</a><a href="https://vk.com/lenoblinvest" target="_blank" rel="noopener">ВКонтакте</a><a href="post.html" class="nav-post">✎ Написать пост</a><a href="recs.html" class="nav-recs" title="Рекомендации по улучшению каналов" aria-label="Рекомендации по улучшению каналов">!</a><button class="theme-toggle" type="button" aria-label="Переключить тему" title="Светлая / тёмная тема"><svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2.5M12 19.5V22M4.2 4.2l1.8 1.8M18 18l1.8 1.8M2 12h2.5M19.5 12H22M4.2 19.8 6 18M18 6l1.8-1.8"/></svg><svg class="moon" viewBox="0 0 24 24" fill="currentColor"><path d="M20.5 14.6A8.5 8.5 0 0 1 9.4 3.5a8.5 8.5 0 1 0 11.1 11.1z"/></svg></button></div></div>
        <div class="hero-main">
        <div class="hero-text"><span class="eyebrow">Обновляется каждый час{(' · ' + upd) if upd else ''}</span>
          <h1 class="hero-title">Каналы, экономика России и&nbsp;Ленобласти</h1>
          <p class="hero-sub">Telegram, MAX и ВКонтакте «Экономика Ленобласти», макроэкономика, регион и предприятия области — в одном месте.</p>
          <div class="hero-cta"><a href="#tg" class="cta-main" onclick="document.querySelector('.lx-tabs').scrollIntoView({{behavior:'smooth'}});return false;">Смотреть дашборд</a><a href="post.html" class="cta-ghost">✎ Написать пост</a></div>
        </div>
        <canvas id="globe3d" aria-hidden="true"></canvas>
      </div>
    </div>
  </div>
  <div class="kpi-grid">{_hero_kpis}</div>
</header>
{_overview}"""
html=re.sub(r'<header>.*?</header>', lambda m: header, html, count=1, flags=re.S)
import plan as _plan
_cp=json.load(open(os.path.join(RT,'data','content_plan.json')))
html=html.replace('<button class="lx-tab" role="tab" data-tab="ideas" aria-selected="false">Идеи для постов</button>','<button class="lx-tab" role="tab" data-tab="plan" aria-selected="false">Контент-план</button>\n    <button class="lx-tab" role="tab" data-tab="ideas" aria-selected="false">Идеи для постов</button>',1)
html=html.replace('<section class="lx-page" id="ideas" hidden>', _plan.build(_cp, data.get('tg_posts_history', []), (__import__('datetime').datetime.now(__import__('datetime').timezone.utc)+__import__('datetime').timedelta(hours=3)).date(), json.load(open(os.path.join(RT,'data','biz_deadlines.json'))))+'\n  <section class="lx-page" id="ideas" hidden>',1)
html=html.replace('<p class="lx-note">Данные обновляются автоматически раз в час из открытых источников.</p>', '', 1)
html=re.sub(r'@media \(prefers-color-scheme: dark\)\{.*?\}\}', '', html, count=1)
html=html.replace("colors: ['#3a6fd8', '#d9822b', '#2e9e6b', '#9b59b6', '#c2412d', '#1f9bb3', '#b8860b', '#7f8c8d']", "colors: ['#7B4DDB', '#12AA9E', '#153F9B', '#FDBC16', '#E0679E', '#d24b3a', '#0e8f84', '#8a84a3']", 1)
css=open(os.path.join(B,'site.css')).read()+'.site-head .channels a.nav-post,.channels a.nav-post{background:linear-gradient(135deg,var(--ac),var(--ac-2));color:#fff;border-color:transparent;font-weight:600}.site-head .channels a.nav-post:hover,.channels a.nav-post:hover{color:#fff;filter:brightness(1.08)}.site-head.big .channels a.nav-post{background:#fff;color:#4a2a9e;border-color:#fff}.site-head.big .channels a.nav-post:hover{color:#4a2a9e}.channels a.nav-recs{width:38px;height:38px;padding:0;display:inline-flex;align-items:center;justify-content:center;font-family:var(--font-head);font-weight:800;font-size:19px;background:var(--yellow)!important;color:#2a1b00!important;border-color:var(--yellow)!important;position:relative}.channels a.nav-recs::after{content:"";position:absolute;inset:-4px;border-radius:50%;border:2px solid var(--yellow);opacity:.6;animation:recsPulse 2.2s ease-out infinite}@keyframes recsPulse{0%{transform:scale(.85);opacity:.7}100%{transform:scale(1.35);opacity:0}}@media (prefers-reduced-motion:reduce){.channels a.nav-recs::after{animation:none}}'+_plan.CSS
html=html.replace('</head>','<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap">\n</head>',1)
i=html.find('</style>', html.find('<div class="wrap">'))
html=html[:i+8]+'\n<style>\n'+css+'\n</style>\n'+html[i+8:]
foot='<footer class="site-foot"><span>Агентство экономического развития Ленинградской области · <a href="https://lenoblinvest.ru" target="_blank" rel="noopener">lenoblinvest.ru</a></span><span>Источники: TGStat, Telemetr, MXStat, Банк России, Росстат, Минэкономразвития, открытые данные</span></footer>'
html=html.replace('\n<script>\n'+scripts, '\n'+foot+'\n<script>\n'+scripts, 1)
html=html.replace('<body><div class="wrap">','<body><script>(function(){var t=\'light\';try{t=localStorage.getItem(\'lxTheme\')||t}catch(e){}document.documentElement.setAttribute(\'data-theme\',t);var P={light:[\'#153F9B\',\'#12AA9E\',\'#FDBC16\',\'#804F80\',\'#666FB4\',\'#c2412d\',\'#0e8f84\',\'#7f8c8d\'],dark:[\'#6f9bff\',\'#2fd3c4\',\'#FDBC16\',\'#d08fd0\',\'#a3abf0\',\'#ff7a66\',\'#3fd1c3\',\'#aab4c8\']};window.__lxPal=P;if(window.dash&&window.dash.colors){var c=P[t];for(var i=0;i<c.length;i++)window.dash.colors[i]=c[i];}})();</script><div class="bg-anim" aria-hidden="true"><i></i><i></i><i></i><i></i></div><canvas id="bg3d" aria-hidden="true"></canvas><div class="wrap">',1)
html=html.replace('</body></html>','<script>'+_plan.JS+'</script>\n<script src="site.js" defer></script>\n</body></html>',1)
open(os.path.join(RT,'index.html'),'w').write(html); print(len(html))

# ---- отдельные страницы: генератор постов и рекомендации ----
import recs as _recs
import weekposts as _wp
_theme=re.search(r'<script>\(function\(\)\{var t=.*?</script>', html).group(0)
_toggle=re.search(r'<button class="theme-toggle".*?</button>', html, re.S).group(0)
def subpage(fn, title, h1, lead, body, extra_css='', js=''):
    page=f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Экономика Ленобласти</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap">
<style>:root{{--font-anthropic-sans:"Inter",system-ui,Arial,sans-serif;--color-bad:#c2412d}}*{{box-sizing:border-box}}body{{margin:0}}.wrap{{max-width:1200px;margin:0 auto;padding:24px clamp(12px,3vw,32px) 48px;position:relative;z-index:1;display:flex;flex-direction:column;gap:20px}}
.pg-head{{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}}.pg-head h1{{font-family:var(--font-head);font-size:clamp(28px,4vw,44px);font-weight:800;margin:4px 0 0;letter-spacing:-.02em}}.pg-lead{{color:var(--color-fg-muted);max-width:760px;margin:0;font-size:16px}}
.channels a.back{{font-weight:600}}
{css}{extra_css}</style></head>
<body>{_theme}<div class="bg-anim" aria-hidden="true"><i></i><i></i><i></i><i></i></div><canvas id="bg3d" aria-hidden="true"></canvas>
<div class="wrap">
<div class="pg-head"><div class="brand"><span class="brand-dot"></span>Экономика Ленобласти · аналитика</div><div class="channels"><a href="./" class="back">← К дашборду</a>{_toggle}</div></div>
<div class="pg-head"><div><h1>{h1}</h1><p class="pg-lead">{lead}</p></div></div>
{body}
{foot}
</div>
{('<script>'+js+'</script>') if js else ''}
<script src="site.js" defer></script>
</body></html>"""
    open(os.path.join(RT,fn),'w').write(page); print(fn, len(page))

subpage('post.html','Генератор постов','Генератор постов для бизнеса',
  'Опишите тему или выберите её из контент-плана — нейросеть подготовит черновик поста для Telegram, MAX или ВКонтакте с пользой для предпринимателей и списком того, что проверить перед публикацией.',
  _pg.build(data, _cfg.get('post_api','')).replace('<h2 class="ix-sec-h">Генератор постов для бизнеса</h2>',''), _pg.CSS, _pg.JS)
subpage('recs.html','Рекомендации по каналам','Как улучшить каналы',
  'Выводы из статистики Telegram, MAX и ВКонтакте на этом сайте и конкретные шаги. Цифры пересчитываются при каждом обновлении данных.',
  _recs.build(data).replace('<div class="rc-grid">', _wp.build(data, (__import__('datetime').datetime.now(__import__('datetime').timezone.utc)+__import__('datetime').timedelta(hours=3)).date()) + '<h2 class="ix-sec-h">Что улучшить</h2><div class="rc-grid">', 1), _recs.CSS + _wp.CSS)
