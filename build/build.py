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
header=f"""<header class="site-head">
  <div class="row"><img class="logo" src="logo-aerlo-white.png" alt="Агентство экономического развития Ленинградской области">
  <div class="channels"><a href="https://t.me/lenoblinvest" target="_blank" rel="noopener">Telegram</a><a href="https://max.ru/id4703059140_gos" target="_blank" rel="noopener">MAX</a><a href="https://vk.com/lenoblinvest" target="_blank" rel="noopener">ВКонтакте</a></div></div>
  <div class="title">Аналитика: каналы, экономика РФ и Ленобласти</div>
  <div class="sub">Telegram, MAX и ВКонтакте «Экономика Ленобласти», экономика России и региона, предприятия области. Данные обновляются раз в час{(' · обновлено '+upd) if upd else ''}.</div>
  <div class="kpis">{kpis}</div>
</header>"""
html=re.sub(r'<header>.*?</header>', lambda m: header, html, count=1, flags=re.S)
html=html.replace('<p class="lx-note">Данные обновляются автоматически раз в час из открытых источников.</p>', '', 1)
html=re.sub(r'@media \(prefers-color-scheme: dark\)\{.*?\}\}', '', html, count=1)
html=html.replace("colors: ['#3a6fd8', '#d9822b', '#2e9e6b', '#9b59b6', '#c2412d', '#1f9bb3', '#b8860b', '#7f8c8d']", "colors: ['#153F9B', '#12AA9E', '#FDBC16', '#804F80', '#666FB4', '#c2412d', '#0e8f84', '#7f8c8d']", 1)
css=open(os.path.join(B,'site.css')).read()
i=html.find('</style>', html.find('<div class="wrap">'))
html=html[:i+8]+'\n<style>\n'+css+'\n</style>\n'+html[i+8:]
foot='<footer class="site-foot"><span>Агентство экономического развития Ленинградской области · <a href="https://lenoblinvest.ru" target="_blank" rel="noopener">lenoblinvest.ru</a></span><span>Источники: TGStat, Telemetr, MXStat, Банк России, Росстат, Минэкономразвития, открытые данные</span></footer>'
html=html.replace('\n<script>\n'+scripts, '\n'+foot+'\n<script>\n'+scripts, 1)
open(os.path.join(RT,'index.html'),'w').write(html); print(len(html))
