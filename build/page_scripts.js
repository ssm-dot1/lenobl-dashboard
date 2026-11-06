dash.calc('tg_kpi', {inputs: ['tg_posts', 'tg_history'], fn: (tg_posts, tg_history) => {
  const h = [...tg_history].sort((a, b) => a.at < b.at ? -1 : 1);
  const subs = +h[h.length - 1].subscribers;
  let views = 0, eng = 0;
  tg_posts.forEach(p => { views += +p.views; eng += +p.reactions + +p.reposts; });
  const n = tg_posts.length;
  const days = tg_posts.map(p => String(p.day).slice(0, 10)).sort();
  const span = (Date.parse(days[days.length - 1]) - Date.parse(days[0])) / 864e5 + 1;
  const avg = Math.round(views / n);
  return [{subscribers: subs, posts: n, avg_reach: avg, err: +(avg / subs * 100).toFixed(1), er: +(eng / views * 100).toFixed(1), posts_per_day: +(n / span).toFixed(1)}];
}});
dash.calc('tg_weekday', {inputs: ['tg_posts_history'], fn: (tg_posts_history) => {
  const names = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье'];
  const short = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
  const t = tg_posts_history.map(p => ({d: new Date(String(p.posted).slice(0, 16) + 'Z'), v: +p.views, r: +p.reactions}));
  const last = Math.max(...t.map(p => +p.d));
  const ok = t.filter(p => last - p.d >= 2 * 864e5);
  return short.map((s, i) => {
    const ps = ok.filter(p => (p.d.getUTCDay() + 6) % 7 === i);
    const vs = ps.map(p => p.v).sort((a, b) => a - b);
    const med = vs.length ? (vs.length % 2 ? vs[(vs.length - 1) / 2] : Math.round((vs[vs.length / 2 - 1] + vs[vs.length / 2]) / 2)) : null;
    const v = ps.reduce((a, p) => a + p.v, 0), r = ps.reduce((a, p) => a + p.r, 0);
    return {dow: i, day: s, day_full: names[i], posts: ps.length, reach: med, er: v ? +(r / v * 100).toFixed(1) : null};
  });
}});
dash.calc('tg_heat', {inputs: ['tg_posts_history'], fn: (tg_posts_history) => {
  const t = tg_posts_history.map(p => ({d: new Date(String(p.posted).slice(0, 16) + 'Z'), v: +p.views}));
  const last = Math.max(...t.map(p => +p.d));
  const m = {};
  t.filter(p => last - p.d >= 2 * 864e5).forEach(p => { const k = ((p.d.getUTCDay() + 6) % 7) + '_' + p.d.getUTCHours(); (m[k] = m[k] || []).push(p.v); });
  return Object.keys(m).map(k => { const [dow, hour] = k.split('_').map(Number); const a = m[k]; return {dow, hour, reach_avg: Math.round(a.reduce((x, y) => x + y, 0) / a.length), posts_count: a.length}; });
}});
dash.calc('max_weekday', {inputs: ['max_heatmap'], fn: (max_heatmap) => {
  const names = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье'];
  const short = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
  return short.map((s, i) => {
    const hs = max_heatmap.filter(h => +h.dow === i);
    const n = hs.reduce((a, h) => a + +h.posts_count, 0);
    const sum = hs.reduce((a, h) => a + +h.reach_avg * +h.posts_count, 0);
    return {dow: i, day: s, day_full: names[i], posts: n, reach: n ? Math.round(sum / n) : null};
  });
}});
dash.calc('tg_types', {inputs: ['tg_posts_history'], fn: (tg_posts_history) => {
  const t = tg_posts_history.map(p => ({d: Date.parse(String(p.posted).slice(0, 16) + 'Z'), v: +p.views, r: +p.reactions, type: p.type || 'Фото'}));
  const last = Math.max(...t.map(p => p.d)); const ok = t.filter(p => last - p.d >= 2 * 864e5);
  const med = (a) => { const s = [...a].sort((x, y) => x - y), n = s.length; return n ? (n % 2 ? s[(n - 1) / 2] : Math.round((s[n / 2 - 1] + s[n / 2]) / 2)) : null; };
  return [...new Set(ok.map(p => p.type))].map(ty => { const ps = ok.filter(p => p.type === ty); const v = ps.reduce((a, p) => a + p.v, 0), r = ps.reduce((a, p) => a + p.r, 0); return {label: ty, posts: ps.length, share: +(ps.length / ok.length * 100).toFixed(1), reach: med(ps.map(p => p.v)), er: v ? +(r / v * 100).toFixed(2) : null}; }).sort((a, b) => b.posts - a.posts);
}});
dash.calc('tg_topics', {inputs: ['tg_posts_history'], fn: (tg_posts_history) => {
  const rules = [['Поздравления', /поздрав|с дн[её]м|день рождени|62-лет/i], ['Дайджесты', /дайджест/i], ['Промтуризм («Крутая Локация»)', /крут\S* локаци|туризм|тропа|маршрут/i], ['Экспорт и международное', /экспорт|беларус|казахстан|китай|хубэй|инди|мумба|кыргыз|брикс|торгпред|иннопром/i], ['Поддержка бизнеса', /поддержк|мер[ыа] |конкурс|программ|акселерац|селлер|фонд|преми|субсид|займ|опрос/i], ['Инвестиции и проекты', /инвест|гчп|проект|площадк|усадьб|памятник|мастер-план|рнс|строител/i], ['Промышленность и предприятия', /завод|производ|предприят|промышл|порт|«/i]];
  const t = tg_posts_history.map(p => ({d: Date.parse(String(p.posted).slice(0, 16) + 'Z'), v: +p.views, r: +p.reactions, text: String(p.text || '')}));
  const last = Math.max(...t.map(p => p.d)); const ok = t.filter(p => last - p.d >= 2 * 864e5);
  ok.forEach(p => { const m = rules.find(([, re]) => re.test(p.text)); p.topic = m ? m[0] : 'Другое'; });
  const med = (a) => { const s = [...a].sort((x, y) => x - y), n = s.length; return n ? (n % 2 ? s[(n - 1) / 2] : Math.round((s[n / 2 - 1] + s[n / 2]) / 2)) : null; };
  return [...new Set(ok.map(p => p.topic))].map(tp => { const ps = ok.filter(p => p.topic === tp); return {topic: tp, posts: ps.length, reach: med(ps.map(p => p.v)), reactions_avg: +(ps.reduce((a, p) => a + p.r, 0) / ps.length).toFixed(1)}; }).sort((a, b) => b.reach - a.reach);
}});
dash.calc('tg_outliers', {inputs: ['tg_posts_history'], fn: (tg_posts_history) => {
  const t = tg_posts_history.map(p => ({id: p.id, posted: p.posted, text: p.text, url: p.url, v: +p.views, d: Date.parse(String(p.posted).slice(0, 16) + 'Z')}));
  const last = Math.max(...t.map(p => p.d)); const ok = t.filter(p => last - p.d >= 2 * 864e5);
  const s = ok.map(p => p.v).sort((a, b) => a - b), n = s.length; const m = n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2;
  const rows = ok.map(p => ({id: p.id, posted: p.posted, text: p.text, url: p.url, views: p.v, dev: Math.round((p.v / m - 1) * 100)})).sort((a, b) => b.dev - a.dev);
  return rows.slice(0, 5).map(r => ({...r, kind: 'выше'})).concat(rows.slice(-5).reverse().map(r => ({...r, kind: 'ниже'})));
}});
dash.calc('tg_timing', {inputs: ['tg_posts_history'], fn: (tg_posts_history) => {
  const t = tg_posts_history.map(p => ({d: Date.parse(String(p.posted).slice(0, 16) + 'Z'), v: +p.views, h: +String(p.posted).slice(11, 13)}));
  const last = Math.max(...t.map(p => p.d)); const ok = t.filter(p => last - p.d >= 2 * 864e5);
  const by = {}; ok.forEach(p => { (by[p.h] = by[p.h] || []).push(p.v); });
  const best = Object.keys(by).filter(h => by[h].length >= 3).map(h => ({h: +h, a: by[h].reduce((x, y) => x + y, 0) / by[h].length})).sort((a, b) => b.a - a.a).slice(0, 3).map(x => x.h).sort((a, b) => a - b);
  const recent = t.filter(p => last - p.d <= 30 * 864e5);
  const inBest = recent.filter(p => best.includes(p.h)).length;
  return [{best_hours: best.map(h => h + ':00').join(', '), share: +(inBest / recent.length * 100).toFixed(1), posts30: recent.length}];
}});
dash.calc('max_timing', {inputs: ['max_heatmap'], fn: (max_heatmap) => {
  const by = {}; max_heatmap.forEach(c => { const h = +c.hour; by[h] = by[h] || {s: 0, n: 0}; by[h].s += +c.reach_avg * +c.posts_count; by[h].n += +c.posts_count; });
  const best = Object.keys(by).filter(h => by[h].n >= 2).map(h => ({h: +h, a: by[h].s / by[h].n})).sort((a, b) => b.a - a.a).slice(0, 3).map(x => x.h).sort((a, b) => a - b);
  const total = Object.values(by).reduce((a, x) => a + x.n, 0); const inBest = best.reduce((a, h) => a + by[h].n, 0);
  return [{best_hours: best.map(h => h + ':00').join(', '), share: +(inBest / total * 100).toFixed(1), posts30: total}];
}});
dash.calc('max_speed', {inputs: ['max_posts_full'], fn: (max_posts_full) => max_posts_full.filter(p => p.views_1h != null && +p.views > 0).map(p => ({id: p.id, posted: p.posted, text: p.text, views_1h: +p.views_1h, views_24h: +p.views_24h, views: +p.views, p1: +(p.views_1h / p.views * 100).toFixed(1), p24: +(p.views_24h / p.views * 100).toFixed(1)}))});
dash.calc('max_speed_sum', {inputs: ['max_posts_full'], fn: (max_posts_full) => {
  const ps = max_posts_full.filter(p => p.views_1h != null && +p.views > 0);
  const med = (a) => { const s = [...a].sort((x, y) => x - y), n = s.length; return n ? (n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2) : null; };
  return [{p1: +med(ps.map(p => p.views_1h / p.views * 100)).toFixed(1), p24: +med(ps.map(p => p.views_24h / p.views * 100)).toFixed(1), v1h: Math.round(med(ps.map(p => +p.views_1h))), posts: ps.length}];
}});
dash.calc('cross_pairs', {inputs: ['tg_posts_history', 'max_posts_full'], fn: (tg_posts_history, max_posts_full) => {
  const key = (s) => String(s || '').toLowerCase().replace(/ё/g, 'е').replace(/[^a-zа-я0-9]/g, '').slice(0, 15);
  const out = [];
  max_posts_full.forEach(m => { const k = key(m.text); const dm = Date.parse(String(m.posted).slice(0, 16) + 'Z'); const t = tg_posts_history.find(p => key(p.text) === k && Math.abs(Date.parse(String(p.posted).slice(0, 16) + 'Z') - dm) <= 2 * 864e5); if (t) out.push({id: String(m.id), day: String(m.posted).slice(0, 10), text: m.text, tg_views: +t.views, max_views: +m.views, diff: Math.round((m.views / t.views - 1) * 100)}); });
  return out;
}});
dash.calc('cross_sum', {inputs: ['cross_pairs'], fn: (cross_pairs) => {
  const s = cross_pairs.map(r => r.diff).sort((a, b) => a - b), n = s.length;
  return [{pairs: n, median_diff: n ? (n % 2 ? s[(n - 1) / 2] : Math.round((s[n / 2 - 1] + s[n / 2]) / 2)) : null, max_wins: n ? +(cross_pairs.filter(r => r.max_views > r.tg_views).length / n * 100).toFixed(0) : null}];
}});
dash.calc('peers_calc', {inputs: ['tg_peers'], fn: (tg_peers) => tg_peers.map(p => ({handle: p.handle, name: p.name, ours: !!p.ours, subscribers: +p.subscribers, median_views: +p.median_views, err: +(p.median_views / p.subscribers * 100).toFixed(1), posts_per_day: +(p.posts_30d / 30).toFixed(1), er: +p.er, url: p.url}))});
dash.calc('peers_sum', {inputs: ['peers_calc'], fn: (peers_calc) => { const o = peers_calc.find(p => p.ours); const rest = peers_calc.filter(p => !p.ours); return [{ours: o ? o.err : null, others: rest.length ? +(rest.reduce((a, p) => a + p.err, 0) / rest.length).toFixed(1) : null}]; }});
dash.calc('tone_rf', {inputs: ['news_rf'], fn: (news_rf) => ['позитив', 'нейтрально', 'негатив'].map(t => ({tone: t, n: news_rf.filter(r => r.tone === t).length}))});
dash.calc('tone_lo', {inputs: ['news_lo'], fn: (news_lo) => ['позитив', 'нейтрально', 'негатив'].map(t => ({tone: t, n: news_lo.filter(r => r.tone === t).length}))});
dash.calc('tone_co', {inputs: ['companies'], fn: (companies) => ['позитив', 'нейтрально', 'негатив'].map(t => ({tone: t, n: companies.filter(r => r.tone === t).length}))});
dash.calc('co_own', {inputs: ['tg_posts_history', 'companies'], fn: (tg_posts_history, companies) => {
  const al = {'Любимый край': /любим\S* кра/i, 'Систэм Электрик': /систэм|систем электрик|systeme/i, 'Катюша': /катюш/i, 'Порт Фавор': /порт фавор/i, 'Солвиль': /солвил/i, 'Респираторный комплекс': /респираторн\S* комплекс/i, 'Технониколь / Технофлекс': /технонико|технофлекс/i, 'Комацо': /комацу|комацо|komatsu/i, 'Тихвинский вагоностроительный завод (ТВСЗ)': /твсз|тихвинск\S* вагон/i, 'Северная звезда': /северн\S* звезд/i, 'Светогорский ЦБК': /светогорск/i};
  return companies.map(c => { const re = al[c.company]; const ps = re ? tg_posts_history.filter(p => re.test(String(p.text || ''))) : []; return {company: c.company, posts: ps.length}; });
}});
dash.calc('tg_quarterly', {inputs: ['tg_monthly'], fn: (tg_monthly) => {
  const q = {};
  tg_monthly.forEach(m => { const [y, mo] = String(m.month).split('-').map(Number); const k = y + '-Q' + Math.ceil(mo / 3); const x = q[k] = q[k] || {quarter: k, months: 0, posts: 0, views: 0, reactions: 0, partial: false}; x.months++; x.posts += +m.posts; x.views += +m.views; x.reactions += +m.reactions; if (m.partial) x.partial = true; });
  const rows = Object.values(q).sort((a, b) => a.quarter < b.quarter ? -1 : 1).map(x => ({...x, partial: x.partial || x.months < 3, label: x.quarter.replace('-Q', ' · ') + ' кв.', per_post: Math.round(x.views / x.posts), react_per_post: +(x.reactions / x.posts).toFixed(1)}));
  rows.forEach((r, i) => { r.change = i ? Math.round((r.per_post / rows[i - 1].per_post - 1) * 100) : null; });
  return rows;
}});
dash.calc('tg_freq', {inputs: ['tg_posts_history'], fn: (tg_posts_history) => {
  const last = Math.max(...tg_posts_history.map(p => Date.parse(String(p.posted).slice(0, 16) + 'Z')));
  const per = {}; tg_posts_history.forEach(p => { const d = String(p.posted).slice(0, 10); per[d] = (per[d] || 0) + 1; });
  const ok = tg_posts_history.filter(p => last - Date.parse(String(p.posted).slice(0, 16) + 'Z') >= 2 * 864e5);
  const med = (a) => { const s = [...a].sort((x, y) => x - y), n = s.length; return n ? (n % 2 ? s[(n - 1) / 2] : Math.round((s[n / 2 - 1] + s[n / 2]) / 2)) : null; };
  return [1, 2, 3, 4, 5].map(k => { const ps = ok.filter(p => Math.min(per[String(p.posted).slice(0, 10)], 5) === k); return {bucket: k === 5 ? '5 и больше постов в день' : k + ' ' + (k === 1 ? 'пост' : 'поста') + ' в день', posts: ps.length, reach: med(ps.map(p => +p.views))}; }).filter(r => r.posts);
}});
dash.calc('tg_format', {inputs: ['tg_posts_history'], fn: (tg_posts_history) => {
  const last = Math.max(...tg_posts_history.map(p => Date.parse(String(p.posted).slice(0, 16) + 'Z')));
  const ok = tg_posts_history.filter(p => p.len != null && last - Date.parse(String(p.posted).slice(0, 16) + 'Z') >= 2 * 864e5);
  const med = (a) => { const s = [...a].sort((x, y) => x - y), n = s.length; return n ? (n % 2 ? s[(n - 1) / 2] : Math.round((s[n / 2 - 1] + s[n / 2]) / 2)) : null; };
  const g = [['Короткий текст (до 900 знаков)', p => p.len < 900], ['Средний текст (900–1500)', p => p.len >= 900 && p.len < 1500], ['Длинный текст (от 1500)', p => p.len >= 1500], ['Эмодзи в начале', p => p.emoji], ['Без эмодзи в начале', p => !p.emoji], ['Со ссылками', p => p.links > 0], ['Без ссылок', p => !(p.links > 0)], ['Свой пост', p => !p.fwd], ['Репост из другого канала', p => p.fwd]];
  return g.map(([label, f]) => { const ps = ok.filter(f); return {variant: label, posts: ps.length, reach: med(ps.map(p => +p.views))}; }).filter(r => r.posts);
}});
dash.calc('goals_calc', {inputs: ['goals'], fn: (goals) => goals.map(g => { const days = Math.max(0, Math.round((Date.parse(g.deadline) - Date.parse('2026-11-06')) / 864e5)); const fc = g.growth30 != null ? Math.round(+g.current + +g.growth30 / 30 * days) : null; return {platform: g.platform, current: +g.current, target: +g.target, deadline: g.deadline, progress: +(g.current / g.target * 100).toFixed(1), forecast: fc, need_per_day: +((g.target - g.current) / Math.max(days, 1)).toFixed(1), status: fc == null ? 'нет данных о темпе' : fc >= g.target ? 'успеваем' : 'не успеваем'}; })});
dash.calc('platform_quarters', {inputs: ['tg_monthly', 'max_daily', 'platforms'], fn: (tg_monthly, max_daily, platforms) => {
  const out = [];
  const q = {}; tg_monthly.forEach(m => { const [y, mo] = String(m.month).split('-').map(Number); const k = y + ' · ' + Math.ceil(mo / 3) + ' кв.'; const x = q[k] = q[k] || {posts: 0, views: 0}; x.posts += +m.posts; x.views += +m.views; });
  Object.keys(q).sort().forEach(k => out.push({id: 'tg_' + k, platform: 'Telegram', quarter: k, posts: q[k].posts, views: q[k].views, per_post: Math.round(q[k].views / q[k].posts), subscribers: null}));
  const mq = {}; max_daily.forEach(d => { const [y, mo] = String(d.day).split('-').map(Number); const k = y + ' · ' + Math.ceil(mo / 3) + ' кв.'; const x = mq[k] = mq[k] || {posts: 0, views: 0, subs: null, days: 0}; x.posts += +d.posts || 0; x.views += +d.views || 0; x.subs = +d.subscribers; x.days++; });
  Object.keys(mq).sort().forEach(k => out.push({id: 'max_' + k, platform: 'MAX', quarter: k + ' (' + mq[k].days + ' дн.)', posts: mq[k].posts, views: mq[k].views, per_post: mq[k].posts ? Math.round(mq[k].views / mq[k].posts) : null, subscribers: mq[k].subs}));
  platforms.filter(p => p.platform === 'ВКонтакте').forEach(p => out.push({id: 'vk_' + p.at, platform: 'ВКонтакте', quarter: '2026 · 4 кв. (на ' + String(p.at).slice(8, 10) + '.' + String(p.at).slice(5, 7) + ')', posts: null, views: null, per_post: null, subscribers: +p.subscribers}));
  return out;
}});
dash.calc('co_districts', {inputs: ['companies'], fn: (companies) => { const m = {}; companies.forEach(c => { const d = String(c.district || '—').split('(')[0].trim() || '—'; if (d === '—') return; m[d] = (m[d] || 0) + 1; }); return Object.keys(m).map(k => ({district: k, n: m[k]})); }});
dash.calc('fin_latest', {inputs: ['company_fin'], fn: (company_fin) => { const by = {}; company_fin.forEach(r => { (by[r.company] = by[r.company] || []).push(r); }); return Object.entries(by).map(([c, rs]) => { rs.sort((a, b) => a.year - b.year); const l = rs[rs.length - 1], p = rs[rs.length - 2]; return {company: c, year: l.year, revenue: l.revenue, profit: l.profit, rev_change: p && p.revenue && l.revenue ? Math.round((l.revenue / p.revenue - 1) * 100) : null, url: l.url}; }); }});
dash.calc('fx_last', {inputs: ['fx'], fn: (fx) => { const s = [...fx].sort((a, b) => a.date < b.date ? -1 : 1); const l = s[s.length - 1]; const ref = s.filter(r => Date.parse(r.date) <= Date.parse(l.date) - 30 * 864e5).pop() || s[0]; return [{date: l.date, usd: l.usd, eur: l.eur, cny: l.cny, usd_ch: +((l.usd / ref.usd - 1) * 100).toFixed(1), eur_ch: +((l.eur / ref.eur - 1) * 100).toFixed(1), cny_ch: +((l.cny / ref.cny - 1) * 100).toFixed(1)}]; }});
dash.calc('alerts', {inputs: ['tg_posts_history', 'tg_monthly', 'max_daily', 'companies'], fn: (tg_posts_history, tg_monthly, max_daily, companies) => {
  const out = []; const t = tg_posts_history.map(p => ({...p, d: Date.parse(String(p.posted).slice(0, 16) + 'Z')})); const last = Math.max(...t.map(p => p.d));
  const s = t.map(p => +p.views).sort((a, b) => a - b); const med = s[Math.floor(s.length / 2)];
  t.filter(p => last - p.d <= 7 * 864e5 && +p.views >= 1.5 * med).forEach(p => out.push({id: 'hot' + p.id, level: 'хорошо', area: 'Telegram', text: 'Пост набрал ' + p.views + ' просмотров — в ' + (p.views / med).toFixed(1) + ' раза больше медианы: ' + String(p.text).slice(0, 60)}));
  const m = tg_monthly.filter(x => !x.partial).sort((a, b) => a.month < b.month ? -1 : 1);
  if (m.length >= 2 && m[m.length - 1].median_views < m[m.length - 2].median_views) out.push({id: 'tgdrop', level: 'внимание', area: 'Telegram', text: 'Медианный охват поста снизился: ' + m[m.length - 2].median_views + ' → ' + m[m.length - 1].median_views + ' (' + m[m.length - 1].month + ').'});
  max_daily.filter(d => +d.growth < 0).slice(-3).forEach(d => out.push({id: 'maxneg' + d.day, level: 'внимание', area: 'MAX', text: 'Отписки превысили подписки ' + d.day + ': ' + d.growth + '.'}));
  companies.filter(c => c.tone === 'негатив').forEach(c => out.push({id: 'neg' + c.company, level: 'риск', area: 'Компании', text: c.company + ': ' + c.last_event}));
  if (!out.length) out.push({id: 'none', level: 'хорошо', area: 'Всё', text: 'Ничего необычного за последние 7 дней.'});
  return out;
}});
dash.calc('tg_by_day', {inputs: ['tg_posts'], fn: (tg_posts) => {
  const m = {};
  tg_posts.forEach(p => { const d = String(p.day).slice(0, 10); m[d] = (m[d] || 0) + +p.views; });
  return Object.keys(m).sort().map(day => ({day, views: m[day]}));
}});

const ru = d3.formatLocale({decimal: ',', thousands: ' ', grouping: [3], currency: ['', ' ₽']});
const MONTHS = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'];
const fmtDate = (s) => { if (!s) return '—'; const [y, m, d] = String(s).slice(0, 10).split('-'); return `${+d} ${MONTHS[+m - 1]} ${y}`; };
const fmtShort = (dt) => `${dt.getUTCDate()} ${MONTHS[dt.getUTCMonth()]}`;
const FMT = {
  int: (v) => ru.format(',.0f')(+v),
  signed: (v) => (+v > 0 ? '+' : '') + ru.format(',.0f')(+v),
  pct1: (v) => ru.format(',.1f')(+v) + '%',
  pct2: (v) => ru.format(',.2f')(+v) + '%',
  rate: (v) => ru.format(',.2~f')(+v) + '%',
  num: (v) => ru.format(',.2~f')(+v),
  date: fmtDate,
  dt: (v) => fmtDate(v) + (String(v).length > 10 ? ', ' + String(v).slice(11, 16) + ' МСК' : ''),
  text: (v) => String(v ?? '—'),
  spct: (v) => (+v > 0 ? '+' : '') + ru.format(',.0f')(+v) + '%',
};

const pickRow = (el) => {
  const d = dash.data(el.dataset.source);
  if (d.status !== 'ok' || !d.data || !d.data.length) return null;
  if (el.dataset.where) {
    const conds = el.dataset.where.split('&').map(p => p.split('=').map(decodeURIComponent));
    return d.data.find(r => conds.every(([k, v]) => String(r[k]) === v)) || null;
  }
  return d.data[+(el.dataset.row || 0)];
};
dash.draw('val', (el) => {
  const row = pickRow(el);
  el.classList.remove('lx-up', 'lx-down');
  if (!row || row[el.dataset.field] == null) { el.textContent = '—'; return; }
  const v = row[el.dataset.field];
  el.textContent = (FMT[el.dataset.fmt] || FMT.text)(v);
  if (el.dataset.tone) { el.classList.toggle('lx-up', +v > 0); el.classList.toggle('lx-down', +v < 0); }
});
dash.draw('count', (el) => { const d = dash.data(el.dataset.source); el.textContent = d.status === 'ok' ? String(d.data.length) : '—'; });
dash.draw('countwith', (el) => { const d = dash.data(el.dataset.source); el.textContent = d.status === 'ok' ? String(d.data.filter(r => +r.mentions_2026 > 0).length) : '—'; });

const showTab = (id) => {
  document.querySelectorAll('.lx-page').forEach(s => { s.hidden = s.id !== id; });
  document.querySelectorAll('.lx-tab').forEach(b => b.setAttribute('aria-selected', String(b.dataset.tab === id)));
  dash.setLink(id);
};
document.querySelectorAll('.lx-tab').forEach(b => b.addEventListener('click', () => showTab(b.dataset.tab)));
const startTab = location.hash.slice(1);
if (startTab && document.getElementById(startTab) && document.getElementById(startTab).classList.contains('lx-page')) showTab(startTab);

const prep = (el) => {
  const d = dash.data(el.dataset.source);
  if (d.status !== 'ok' || !d.data.length) { el.replaceChildren(); return null; }
  el.classList.remove('dash-skeleton'); el.replaceChildren();
  return d.data;
};
const tip = (el) => { const t = document.createElement('div'); t.className = 'lx-tip'; t.hidden = true; el.append(t); return t; };
const setTip = (t, el, x, y, head, val) => {
  const h = document.createElement('span'); h.textContent = head;
  const v = document.createElement('div'); v.textContent = val;
  t.replaceChildren(h, v); t.hidden = false;
  const w = el.clientWidth, tw = t.offsetWidth;
  t.style.left = Math.max(0, Math.min(w - tw, x - tw / 2)) + 'px';
  t.style.top = Math.max(0, y - t.offsetHeight - 10) + 'px';
};
const styleAxis = (g) => { g.attr('font-size', null).attr('font-family', null); g.selectAll('text').attr('fill', 'var(--color-fg-muted)').style('font-size', 'var(--cds-font-size-caption)'); g.selectAll('.domain').attr('stroke', 'var(--cds-chart-axis)'); g.selectAll('line').attr('stroke', 'var(--cds-chart-grid)'); };
const yAxisLeft = (svg, y, H, fmt, ticks) => {
  const g = svg.append('g').call(d3.axisLeft(y).ticks(ticks).tickFormat(fmt).tickSize(0));
  styleAxis(g); g.select('.domain').remove();
  let w = 0; g.selectAll('text').each(function () { w = Math.max(w, this.getComputedTextLength()); });
  return {g, w};
};
const timeChart = (el, kind) => {
  const rows = prep(el); if (!rows) return;
  const xk = el.dataset.x, yk = el.dataset.y;
  const data = rows.map(r => ({x: new Date(String(r[xk]).slice(0, 10) + 'T00:00:00Z'), y: +r[yk]})).sort((a, b) => a.x - b.x);
  const W = el.clientWidth || 600, H = 220, m = {t: 12, r: 24, b: 26};
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`);
  const yMin = kind === 'bars' ? 0 : d3.min(data, d => d.y) * 0.98, yMax = d3.max(data, d => d.y) * (kind === 'bars' ? 1.05 : 1.01);
  const y = d3.scaleLinear([kind === 'step' ? Math.floor(d3.min(data, d => d.y) - 1) : yMin, kind === 'step' ? Math.ceil(yMax + 0.5) : yMax], [H - m.b, m.t]).nice();
  const yf = (v) => ru.format(kind === 'step' ? ',.1~f' : ',.0f')(v);
  const ax = yAxisLeft(svg, y, H, yf, 4); const L = ax.w + 10;
  ax.g.attr('transform', `translate(${L - 6},0)`);
  svg.append('g').selectAll('line').data(y.ticks(4)).join('line').attr('x1', L).attr('x2', W - m.r).attr('y1', d => y(d)).attr('y2', d => y(d)).attr('stroke', 'var(--cds-chart-grid)');
  const color = dash.colors[0];
  let xpos;
  if (kind === 'bars') {
    const x = d3.scaleBand(data.map(d => +d.x), [L, W - m.r]).padding(0.2);
    xpos = (d) => x(+d.x) + x.bandwidth() / 2;
    svg.append('g').selectAll('rect').data(data).join('rect').attr('x', d => x(+d.x)).attr('width', Math.min(32, x.bandwidth())).attr('y', d => y(d.y)).attr('height', d => y(0) - y(d.y)).attr('rx', 2).attr('fill', color);
    const every = Math.ceil(data.length / Math.max(2, Math.floor((W - L) / 70)));
    const gx = svg.append('g').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues(data.filter((d, i) => i % every === 0).map(d => +d.x)).tickFormat(v => fmtShort(new Date(v))).tickSize(0).tickPadding(8));
    styleAxis(gx);
  } else {
    const x = d3.scaleUtc(d3.extent(data, d => d.x), [L, W - m.r]);
    xpos = (d) => x(d.x);
    const line = d3.line().x(d => x(d.x)).y(d => y(d.y)).curve(kind === 'step' ? d3.curveStepAfter : d3.curveLinear);
    svg.append('path').datum(data).attr('fill', 'none').attr('stroke', color).attr('stroke-width', 2).attr('stroke-linejoin', 'round').attr('stroke-linecap', 'round').attr('d', line);
    if (kind === 'step') svg.append('g').selectAll('circle').data(data).join('circle').attr('cx', d => x(d.x)).attr('cy', d => y(d.y)).attr('r', 3).attr('fill', color);
    const n = Math.max(2, Math.floor((W - L) / 80));
    const gx = svg.append('g').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(n).tickFormat(v => kind === 'step' ? `${MONTHS[v.getUTCMonth()]} ${String(v.getUTCFullYear()).slice(2)}` : fmtShort(v)).tickSize(0).tickPadding(8));
    styleAxis(gx);
  }
  const t = tip(el);
  const dot = svg.append('circle').attr('r', 4).attr('fill', color).attr('stroke', 'var(--color-bg)').attr('stroke-width', 2).style('display', 'none');
  svg.append('rect').attr('x', L).attr('y', 0).attr('width', W - m.r - L).attr('height', H - m.b).attr('fill', 'transparent')
    .on('pointermove', (ev) => {
      const [mx] = d3.pointer(ev);
      const d = data[d3.minIndex(data, p => Math.abs(xpos(p) - mx))];
      const sx = el.clientWidth / W;
      dot.style('display', null).attr('cx', xpos(d)).attr('cy', y(d.y));
      setTip(t, el, xpos(d) * sx, y(d.y) * sx, fmtDate(d.x.toISOString()), `${el.dataset.label}: ${kind === 'step' ? ru.format(',.2~f')(d.y) + '%' : ru.format(',.0f')(d.y)}`);
    })
    .on('pointerleave', () => { t.hidden = true; dot.style('display', 'none'); });
};
dash.draw('line', (el) => timeChart(el, 'line'));
dash.draw('bars', (el) => timeChart(el, 'bars'));
dash.draw('step', (el) => timeChart(el, 'step'));

dash.draw('hbars', (el) => {
  const rows = prep(el); if (!rows) return;
  const data = rows.map(r => ({k: String(r[el.dataset.x]), v: +r[el.dataset.y]})).sort((a, b) => b.v - a.v || a.k.localeCompare(b.k));
  const W = el.clientWidth || 600, rowH = 22, H = data.length * rowH + 8;
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`);
  const labels = svg.append('g');
  labels.selectAll('text').data(data).join('text').text(d => d.k).attr('y', (d, i) => i * rowH + rowH / 2 + 4).attr('fill', 'var(--color-fg)').style('font-size', 'var(--cds-font-size-caption)');
  let lw = 0; labels.selectAll('text').each(function () { lw = Math.max(lw, this.getComputedTextLength()); });
  lw = Math.min(lw, W * 0.5);
  labels.selectAll('text').attr('x', 0);
  const L = lw + 10;
  const x = d3.scaleLinear([0, Math.max(1, d3.max(data, d => d.v))], [L, W - 30]);
  const color = dash.colors[0];
  svg.append('g').selectAll('rect').data(data).join('rect').attr('x', L).attr('y', (d, i) => i * rowH + 4).attr('height', rowH - 8).attr('width', d => Math.max(d.v ? 2 : 0, x(d.v) - L)).attr('rx', 2).attr('fill', d => d.v ? color : 'var(--cds-chart-muted)');
  svg.append('g').selectAll('text').data(data).join('text').text(d => String(d.v)).attr('x', d => x(d.v) + 6).attr('y', (d, i) => i * rowH + rowH / 2 + 4).attr('fill', 'var(--color-fg-muted)').style('font-size', 'var(--cds-font-size-caption)');
});

const bestRow = (rows) => { const ok = rows.filter(r => r.reach != null && +r.posts >= 5); return ok.length ? ok.reduce((a, r) => +r.reach > +a.reach ? r : a) : null; };
dash.draw('best', (el) => { const d = dash.data(el.dataset.source); const b = d.status === 'ok' ? bestRow(d.data) : null; el.textContent = b ? b.day_full : '—'; });
dash.draw('bestval', (el) => { const d = dash.data(el.dataset.source); const b = d.status === 'ok' ? bestRow(d.data) : null; el.textContent = b ? ru.format(',.0f')(b.reach) : '—'; });
dash.draw('weekday', (el) => {
  const rows = prep(el); if (!rows) return;
  const data = [...rows].sort((a, b) => a.dow - b.dow);
  const best = bestRow(data);
  const W = el.clientWidth || 600, H = 220, m = {t: 22, b: 40};
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`);
  const x = d3.scaleBand(data.map(d => d.day), [0, W]).padding(0.25);
  const y = d3.scaleLinear([0, d3.max(data, d => +d.reach || 0) * 1.1 || 1], [H - m.b, m.t]);
  const bw = Math.min(32, x.bandwidth()), off = (x.bandwidth() - bw) / 2;
  const g = svg.append('g').selectAll('g').data(data).join('g').attr('transform', d => `translate(${x(d.day)},0)`);
  g.filter(d => d.reach != null).append('rect').attr('x', off).attr('width', bw).attr('y', d => y(+d.reach)).attr('height', d => y(0) - y(+d.reach)).attr('rx', 2).attr('fill', d => best && d.dow === best.dow ? dash.colors[0] : 'var(--cds-chart-muted)');
  g.filter(d => d.reach != null).append('text').text(d => ru.format(',.0f')(+d.reach)).attr('x', x.bandwidth() / 2).attr('y', d => y(+d.reach) - 6).attr('text-anchor', 'middle').attr('fill', 'var(--color-fg)').style('font-size', 'var(--cds-font-size-caption)').style('font-variant-numeric', 'tabular-nums');
  g.append('text').text(d => d.day).attr('x', x.bandwidth() / 2).attr('y', H - m.b + 16).attr('text-anchor', 'middle').attr('fill', 'var(--color-fg)').style('font-size', 'var(--cds-font-size-caption)');
  g.append('text').text(d => d.posts + ' п.').attr('x', x.bandwidth() / 2).attr('y', H - m.b + 32).attr('text-anchor', 'middle').attr('fill', 'var(--color-fg-muted)').style('font-size', 'var(--cds-font-size-caption)');
  svg.append('line').attr('x1', 0).attr('x2', W).attr('y1', y(0)).attr('y2', y(0)).attr('stroke', 'var(--cds-chart-axis)');
});
dash.draw('heat', (el) => {
  const rows = prep(el); if (!rows) return;
  const days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
  const hours = d3.range(d3.min(rows, r => +r.hour), d3.max(rows, r => +r.hour) + 1);
  const W = el.clientWidth || 600, L = 30, T = 20, ch = 26;
  const H = T + days.length * ch + 4;
  const cw = (W - L) / hours.length;
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`);
  const max = d3.max(rows, r => +r.reach_avg), min = d3.min(rows, r => +r.reach_avg);
  const op = d3.scaleLinear([min, max], [0.15, 1]);
  svg.append('g').selectAll('text').data(days).join('text').text(d => d).attr('x', 0).attr('y', (d, i) => T + i * ch + ch / 2 + 4).attr('fill', 'var(--color-fg-muted)').style('font-size', 'var(--cds-font-size-caption)');
  const step = cw < 22 ? 2 : 1;
  svg.append('g').selectAll('text').data(hours.filter((h, i) => i % step === 0)).join('text').text(h => h).attr('x', h => L + (h - hours[0]) * cw + cw / 2).attr('y', T - 6).attr('text-anchor', 'middle').attr('fill', 'var(--color-fg-muted)').style('font-size', 'var(--cds-font-size-caption)');
  svg.append('g').selectAll('rect').data(days.flatMap((d, i) => hours.map(h => ({i, h})))).join('rect').attr('x', c => L + (c.h - hours[0]) * cw + 1).attr('y', c => T + c.i * ch + 1).attr('width', Math.max(1, cw - 2)).attr('height', ch - 2).attr('rx', 2).attr('fill', 'var(--color-panel)').attr('stroke', 'var(--cds-chart-grid)');
  const cells = svg.append('g').selectAll('g').data(rows).join('g').attr('transform', r => `translate(${L + (+r.hour - hours[0]) * cw + 1},${T + +r.dow * ch + 1})`);
  cells.append('rect').attr('width', Math.max(1, cw - 2)).attr('height', ch - 2).attr('rx', 2).attr('fill', dash.colors[0]).attr('fill-opacity', r => op(+r.reach_avg));
  if (cw >= 26) cells.append('text').text(r => Math.round(+r.reach_avg)).attr('x', (cw - 2) / 2).attr('y', ch / 2 + 3).attr('text-anchor', 'middle').attr('fill', r => op(+r.reach_avg) > 0.55 ? 'var(--color-bg)' : 'var(--color-fg)').style('font-size', 'var(--cds-font-size-caption)').style('font-variant-numeric', 'tabular-nums');
  const t = tip(el);
  cells.on('pointerenter', (ev, r) => { const sx = el.clientWidth / W; setTip(t, el, (L + (+r.hour - hours[0]) * cw + cw / 2) * sx, (T + +r.dow * ch) * sx, `${days[+r.dow]}, ${r.hour}:00–${+r.hour + 1}:00`, `Охват: ${Math.round(+r.reach_avg)} · постов: ${r.posts_count}`); }).on('pointerleave', () => { t.hidden = true; });
});

const TONE = {'позитив': 'ok', 'негатив': 'bad', 'нейтрально': 'warn', 'растёт': 'ok', 'есть сигнал': 'warn', 'нет сигналов': 'bad', 'успеваем': 'ok', 'не успеваем': 'bad'};
const toneColor = (t) => t === 'позитив' ? 'var(--color-ok)' : t === 'негатив' ? 'var(--color-bad)' : 'var(--cds-chart-muted)';
dash.draw('cbars', (el) => {
  const rows = prep(el); if (!rows) return;
  const xk = el.dataset.x, yk = el.dataset.y, nk = el.dataset.n, fmt = FMT[el.dataset.fmt || 'int'], hl = el.dataset.hl || 'max';
  const data = rows.filter(r => r[yk] != null).map(r => ({k: String(r[xk]), v: +r[yk], n: nk ? +r[nk] : null, ours: !!r.ours}));
  if (el.dataset.sort !== 'none') data.sort((a, b) => b.v - a.v);
  const W = el.clientWidth || 600, rowH = 26, H = data.length * rowH + 4;
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`);
  const lab = svg.append('g').selectAll('text').data(data).join('text').attr('x', 0).attr('y', (d, i) => i * rowH + rowH / 2 + 4).attr('fill', 'var(--color-fg)').style('font-size', 'var(--cds-font-size-caption)').text(d => d.k);
  const maxL = W * 0.42;
  lab.each(function (d) { let s = d.k; while (this.getComputedTextLength() > maxL && s.length > 4) { s = s.slice(0, -2); this.textContent = s + '…'; } });
  let lw = 0; lab.each(function () { lw = Math.max(lw, this.getComputedTextLength()); });
  const L = lw + 10;
  const nl = el.dataset.nlabel || ' п.';
  const txt = (d) => fmt(d.v) + (d.n != null ? ' · ' + d.n + nl : '');
  let vw = 0; const probe = svg.append('text').style('font-size', 'var(--cds-font-size-caption)').style('font-variant-numeric', 'tabular-nums');
  data.forEach(d => { probe.text(txt(d)); vw = Math.max(vw, probe.node().getComputedTextLength()); }); vw += 12; probe.remove();
  const x = d3.scaleLinear([0, d3.max(data, d => d.v) || 1], [L, Math.max(L + 20, W - vw)]);
  const top = d3.max(data, d => d.v);
  const col = (d) => el.dataset.color === 'tone' ? toneColor(d.k) : hl === 'ours' ? (d.ours ? dash.colors[0] : 'var(--cds-chart-muted)') : hl === 'none' ? dash.colors[0] : (d.v === top ? dash.colors[0] : 'var(--cds-chart-muted)');
  svg.append('g').selectAll('rect').data(data).join('rect').attr('x', L).attr('y', (d, i) => i * rowH + 5).attr('height', rowH - 10).attr('width', d => Math.max(d.v ? 2 : 0, x(d.v) - L)).attr('rx', 2).attr('fill', col);
  svg.append('g').selectAll('text').data(data).join('text').text(txt).attr('x', d => x(d.v) + 6).attr('y', (d, i) => i * rowH + rowH / 2 + 4).attr('fill', 'var(--color-fg-muted)').style('font-size', 'var(--cds-font-size-caption)').style('font-variant-numeric', 'tabular-nums');
});
const daysLeft = (s) => { const t = new Date(); const today = Date.UTC(t.getFullYear(), t.getMonth(), t.getDate()); const d = Math.round((Date.parse(String(s).slice(0, 10) + 'T00:00:00Z') - today) / 864e5); return d === 0 ? 'сегодня' : d > 0 ? 'через ' + d + ' дн.' : 'прошло'; };
FMT.spct1 = (v) => (+v > 0 ? '+' : '') + ru.format(',.1f')(+v) + '%';
const MONF = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'];
dash.draw('mchart', (el) => {
  let rows = prep(el); if (!rows) return;
  if (el.dataset.filter) { const [fk, fv] = el.dataset.filter.split('='); rows = rows.filter(r => String(r[fk]) === fv); if (!rows.length) return; }
  const xk = el.dataset.x, ys = el.dataset.y.split(','), kind = el.dataset.kind || 'line', unit = el.dataset.unit || '';
  const toD = (s) => new Date(String(s).length === 7 ? s + '-01T00:00:00Z' : String(s).slice(0, 10) + 'T00:00:00Z');
  const data = rows.map(r => ({x: toD(r[xk]), xs: String(r[xk]), v: ys.map(k => r[k] == null ? null : +r[k]), partial: !!r.partial})).sort((a, b) => a.x - b.x);
  const monthly = String(rows[0][xk]).length === 7;
  const W = el.clientWidth || 600, H = +(el.dataset.h || 200), m = {t: ys.length > 1 ? 24 : 14, r: 22, b: 24};
  if (ys.length > 1) { const lg = document.createElement('div'); lg.className = 'lx-muted'; lg.style.cssText = 'position:absolute;top:0;right:0;display:flex;gap:12px'; (el.dataset.names || '').split(',').forEach((n, i) => { const s = document.createElement('span'); const dot = document.createElement('span'); dot.textContent = '● '; dot.style.color = dash.colors[i]; s.append(dot, n); lg.append(s); }); el.append(lg); }
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`);
  const all = data.flatMap(d => d.v).filter(v => v != null);
  let lo = d3.min(all), hi = d3.max(all);
  if (kind === 'bars' || el.dataset.zero) { lo = Math.min(0, lo); hi = Math.max(0, hi); } else { const pad = (hi - lo) * 0.1 || Math.abs(hi) * 0.02 || 1; lo -= pad; hi += pad; }
  const y = d3.scaleLinear([lo, hi], [H - m.b, m.t]).nice();
  const yf = (v) => ru.format(Math.abs(hi) >= 10000 ? ',.0f' : ',.1~f')(v);
  const ax = yAxisLeft(svg, y, H, yf, 4); const L = ax.w + 10; ax.g.attr('transform', `translate(${L - 6},0)`);
  svg.append('g').selectAll('line').data(y.ticks(4)).join('line').attr('x1', L).attr('x2', W - m.r).attr('y1', d => y(d)).attr('y2', d => y(d)).attr('stroke', d => d === 0 ? 'var(--cds-chart-axis)' : 'var(--cds-chart-grid)');
  const lab = (d) => monthly ? MONF[d.x.getUTCMonth()] + ' ' + String(d.x.getUTCFullYear()).slice(2) : fmtShort(d.x);
  let xpos;
  if (kind === 'bars') {
    const x = d3.scaleBand(data.map(d => d.xs), [L, W - m.r]).padding(0.2); xpos = (d) => x(d.xs) + x.bandwidth() / 2;
    const bw = Math.min(32, x.bandwidth());
    svg.append('g').selectAll('rect').data(data).join('rect').attr('x', d => xpos(d) - bw / 2).attr('width', bw).attr('y', d => y(Math.max(0, d.v[0]))).attr('height', d => Math.abs(y(d.v[0]) - y(0))).attr('rx', 2).attr('fill', d => d.partial ? 'var(--cds-chart-muted)' : (d.v[0] < 0 ? 'var(--color-bad)' : dash.colors[0]));
    const every = Math.ceil(data.length / Math.max(2, Math.floor((W - L) / 56)));
    svg.append('g').selectAll('text').data(data.filter((d, i) => i % every === 0)).join('text').text(lab).attr('x', xpos).attr('y', H - 6).attr('text-anchor', 'middle').attr('fill', 'var(--color-fg-muted)').style('font-size', 'var(--cds-font-size-caption)');
  } else {
    const x = d3.scaleUtc(d3.extent(data, d => d.x), [L, W - m.r]); xpos = (d) => x(d.x);
    ys.forEach((k, i) => { svg.append('path').datum(data.filter(d => d.v[i] != null)).attr('fill', 'none').attr('stroke', dash.colors[i]).attr('stroke-width', 2).attr('stroke-linejoin', 'round').attr('stroke-linecap', 'round').attr('d', d3.line().x(d => x(d.x)).y(d => y(d.v[i]))); });
    const gx = svg.append('g').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(Math.max(2, Math.floor((W - L) / 70))).tickFormat(v => monthly ? MONF[v.getUTCMonth()] + ' ' + String(v.getUTCFullYear()).slice(2) : fmtShort(v)).tickSize(0).tickPadding(8)); styleAxis(gx);
  }
  const names = (el.dataset.names || el.dataset.label || '').split(',');
  const t = tip(el); const dot = svg.append('circle').attr('r', 4).attr('fill', dash.colors[0]).attr('stroke', 'var(--color-bg)').attr('stroke-width', 2).style('display', 'none');
  svg.append('rect').attr('x', L).attr('y', 0).attr('width', W - m.r - L).attr('height', H - m.b).attr('fill', 'transparent').on('pointermove', (ev) => { const [mx] = d3.pointer(ev); const d = data[d3.minIndex(data, p => Math.abs(xpos(p) - mx))]; const sx = el.clientWidth / W; if (kind !== 'bars') dot.style('display', null).attr('cx', xpos(d)).attr('cy', y(d.v[0])); setTip(t, el, xpos(d) * sx, y(d3.max(d.v.filter(v => v != null))) * sx, monthly ? MONF[d.x.getUTCMonth()] + ' ' + d.x.getUTCFullYear() + (d.partial ? ' (неполный)' : '') : fmtDate(d.xs), ys.map((k, i) => (names[i] ? names[i] + ': ' : '') + (d.v[i] == null ? '—' : ru.format(',.2~f')(d.v[i]) + unit)).join(' · ')); }).on('pointerleave', () => { t.hidden = true; dot.style('display', 'none'); });
});
dash.draw('list', (ul) => {
  const d = dash.data(ul.dataset.source); ul.replaceChildren(); if (d.status !== 'ok') return;
  const lv = {'хорошо': 'ok', 'внимание': 'warn', 'риск': 'bad'};
  d.data.forEach(r => { const li = document.createElement('li'); const tag = document.createElement('span'); tag.className = 'lx-pill ' + (lv[r.level] || ''); tag.textContent = r.area; const txt = document.createElement('span'); txt.textContent = ' ' + r.text; li.append(tag, txt); ul.append(li); });
});
const cell = (tr, text, cls) => { const td = document.createElement('td'); if (cls) td.className = cls; td.textContent = text; tr.append(td); return td; };
const linkCell = (tr, text, url) => { const td = document.createElement('td'); if (url) { const a = document.createElement('a'); a.href = url; a.target = '_blank'; a.rel = 'noopener'; a.textContent = text; td.append(a); } else td.textContent = text; tr.append(td); };
const pill = (tr, text, cls) => { const td = document.createElement('td'); const s = document.createElement('span'); s.className = 'lx-pill ' + (cls || ''); s.textContent = text || '—'; td.append(s); tr.append(td); };
const tableRows = (tbody) => { const d = dash.data(tbody.closest('table').dataset.source); return d.status === 'ok' ? d.data : null; };
dash.draw('table', (tbody) => {
  const table = tbody.closest('table'); const d = dash.data(table.dataset.source); tbody.replaceChildren(); if (d.status !== 'ok') return;
  let rows = [...d.data];
  if (table.dataset.filter) { const [k, v] = table.dataset.filter.split('='); rows = rows.filter(r => String(r[k]) === v); }
  if (table.dataset.sort) { const [k, dir] = table.dataset.sort.split(':'); const sg = dir === 'asc' ? 1 : -1; rows.sort((a, b) => { const x = a[k], y = b[k]; return sg * ((typeof x === 'number' && typeof y === 'number') ? x - y : String(x).localeCompare(String(y))); }); }
  const ths = [...table.querySelectorAll('th[data-field]')];
  rows.forEach(r => {
    const tr = document.createElement('tr');
    ths.forEach(th => {
      const f = th.dataset.field, fm = th.dataset.fmt || 'text', v = r[f], num = th.classList.contains('lx-num');
      if (fm === 'link') { linkCell(tr, v == null ? '—' : String(v), r.url); return; }
      const c = cell(tr, v == null ? '—' : fm === 'daysleft' ? fmtDate(v) + ' · ' + daysLeft(v) : (FMT[fm] || FMT.text)(v), num ? 'lx-num' : '');
      if (fm === 'date' || fm === 'dt' || fm === 'daysleft') c.style.whiteSpace = 'nowrap';
      if (th.dataset.tone && v != null) c.classList.add(+v > 0 ? 'lx-up' : +v < 0 ? 'lx-down' : 'lx-flat');
    });
    tbody.append(tr);
  });
});
dash.draw('news', (tbody) => {
  const rows = tableRows(tbody); tbody.replaceChildren(); if (!rows) return;
  [...rows].sort((a, b) => a.date < b.date ? 1 : -1).forEach(r => {
    const tr = document.createElement('tr');
    cell(tr, fmtDate(r.date)).style.whiteSpace = 'nowrap'; linkCell(tr, r.title, r.url); cell(tr, r.topic); cell(tr, r.source); pill(tr, r.tone, TONE[r.tone]);
    tbody.append(tr);
  });
});
dash.draw('posts', (tbody) => {
  const rows = tableRows(tbody); tbody.replaceChildren(); if (!rows) return;
  const f = ru.format(',.0f');
  const fields = [...tbody.closest('table').querySelectorAll('th[data-field]')].map(th => th.dataset.field);
  [...rows].sort((a, b) => b.views - a.views).forEach(r => {
    const tr = document.createElement('tr');
    fields.forEach(k => {
      if (k === 'day') cell(tr, fmtDate(r.day)).style.whiteSpace = 'nowrap';
      else if (k === 'text') cell(tr, r.text);
      else cell(tr, r[k] == null ? '—' : f(r[k]), 'lx-num');
    });
    tbody.append(tr);
  });
});
dash.draw('companies', (tbody) => {
  const rows = tableRows(tbody); tbody.replaceChildren(); if (!rows) return;
  const tone = {'Есть новости': 'ok', 'Уточнить': 'bad'};
  [...rows].sort((a, b) => (b.last_date || '').localeCompare(a.last_date || '') || a.company.localeCompare(b.company)).forEach(r => {
    const tr = document.createElement('tr');
    cell(tr, r.company); cell(tr, r.sector); cell(tr, r.district);
    cell(tr, r.last_date ? fmtDate(r.last_date) : '—').style.whiteSpace = 'nowrap';
    linkCell(tr, r.last_event, r.url);
    pill(tr, r.status, tone[r.status] || 'warn'); pill(tr, r.tone, TONE[r.tone]);
    tbody.append(tr);
  });
});

dash.calc('tg_kpi', {inputs: ['tg_posts_history', 'tg_history'], fn: (tg_posts_history, tg_history) => {
  const h = [...tg_history].sort((a, b) => a.at < b.at ? -1 : 1);
  const subs = +h[h.length - 1].subscribers;
  const t = tg_posts_history.map(p => ({d: Date.parse(String(p.posted).slice(0, 16) + 'Z'), v: +p.views, r: +p.reactions || 0}));
  const last = Math.max(...t.map(p => p.d));
  const rec = t.filter(p => last - p.d <= 30 * 864e5);
  const ok = rec.filter(p => last - p.d >= 864e5);
  const views = ok.reduce((a, p) => a + p.v, 0), reac = ok.reduce((a, p) => a + p.r, 0);
  const avg = ok.length ? Math.round(views / ok.length) : null;
  return [{subscribers: subs, posts: rec.length, avg_reach: avg, err: avg != null ? +(avg / subs * 100).toFixed(1) : null, er: views ? +(reac / views * 100).toFixed(1) : null, posts_per_day: +(rec.length / 30).toFixed(1)}];
}});
dash.calc('tg_top30', {inputs: ['tg_posts_history'], fn: (tg_posts_history) => {
  const last = Math.max(...tg_posts_history.map(p => Date.parse(String(p.posted).slice(0, 16) + 'Z')));
  return tg_posts_history.filter(p => last - Date.parse(String(p.posted).slice(0, 16) + 'Z') <= 30 * 864e5).map(p => ({id: String(p.id), day: String(p.posted).slice(0, 10), text: String(p.text || '').slice(0, 120), views: +p.views, reactions: +p.reactions || 0})).sort((a, b) => b.views - a.views).slice(0, 20);
}});
dash.calc('tg_by_day', {inputs: ['tg_posts_history'], fn: (tg_posts_history) => {
  const m = {};
  const last = Math.max(...tg_posts_history.map(p => Date.parse(String(p.posted).slice(0, 16) + 'Z')));
  tg_posts_history.filter(p => last - Date.parse(String(p.posted).slice(0, 16) + 'Z') <= 30 * 864e5).forEach(p => { const d = String(p.posted).slice(0, 10); m[d] = (m[d] || 0) + +p.views; });
  return Object.keys(m).sort().map(day => ({day, views: m[day]}));
}});
dash.calc('alerts', {inputs: ['tg_posts_history', 'tg_monthly', 'max_daily', 'companies'], fn: (tg_posts_history, tg_monthly, max_daily, companies) => {
  const out = []; const t = tg_posts_history.map(p => ({...p, d: Date.parse(String(p.posted).slice(0, 16) + 'Z')})); const last = Math.max(...t.map(p => p.d));
  const s = t.map(p => +p.views).sort((a, b) => a - b); const med = s[Math.floor(s.length / 2)];
  t.filter(p => last - p.d <= 30 * 864e5 && +p.views >= 1.5 * med).sort((a, b) => b.views - a.views).slice(0, 5).forEach(p => out.push({id: 'hot' + p.id, level: 'хорошо', area: 'Telegram', text: 'Пост набрал ' + p.views + ' просмотров — в ' + (p.views / med).toFixed(1) + ' раза больше медианы: ' + String(p.text).slice(0, 60)}));
  const m = tg_monthly.filter(x => !x.partial).sort((a, b) => a.month < b.month ? -1 : 1);
  if (m.length >= 2 && m[m.length - 1].median_views < m[m.length - 2].median_views) out.push({id: 'tgdrop', level: 'внимание', area: 'Telegram', text: 'Медианный охват поста снизился: ' + m[m.length - 2].median_views + ' → ' + m[m.length - 1].median_views + ' (' + m[m.length - 1].month + ').'});
  max_daily.filter(d => +d.growth < 0 && Date.parse(d.day) >= Date.parse(max_daily.map(x => x.day).sort().pop()) - 30 * 864e5).slice(-3).forEach(d => out.push({id: 'maxneg' + d.day, level: 'внимание', area: 'MAX', text: 'Отписки превысили подписки ' + d.day + ': ' + d.growth + '.'}));
  companies.filter(c => c.tone === 'негатив').forEach(c => out.push({id: 'neg' + c.company, level: 'риск', area: 'Компании', text: c.company + ': ' + c.last_event}));
  if (!out.length) out.push({id: 'none', level: 'хорошо', area: 'Всё', text: 'Ничего необычного за последние 30 дней.'});
  return out;
}});
dash.calc('co_districts', {inputs: ['companies'], fn: (companies) => { const m = {}; companies.forEach(c => { const d = String(c.district || '—').split('(')[0].trim(); if (!d || d === '—' || d === 'Ленобласть') return; const x = m[d] = m[d] || {district: d, n: 0, list: [], pos: 0, neg: 0}; x.n++; x.list.push(String(c.company).replace(/ \(.*\)$/, '')); if (c.tone === 'позитив') x.pos++; if (c.tone === 'негатив') x.neg++; }); return Object.values(m).map(x => ({district: x.district, n: x.n, names: x.list.join(', '), pos: x.pos, neg: x.neg})); }});
dash.calc('fx_changes', {inputs: ['fx'], fn: (fx) => {
  const s = [...fx].sort((a, b) => a.date < b.date ? -1 : 1); const l = s[s.length - 1], p = s[s.length - 2];
  const back = (days) => s.filter(r => Date.parse(r.date) <= Date.parse(l.date) - days * 864e5).pop();
  const m1 = back(30), y1 = back(365) || s[0], ys = s.filter(r => r.date < l.date.slice(0, 4) + '-01-01').pop();
  const yr = s.filter(r => Date.parse(r.date) > Date.parse(l.date) - 365 * 864e5);
  const ch = (a, b) => a && b ? +((a / b - 1) * 100).toFixed(1) : null;
  return [['usd', 'Доллар'], ['eur', 'Евро'], ['cny', 'Юань']].map(([k, name]) => ({cur: name, rate: l[k], d1: ch(l[k], p && p[k]), m1: ch(l[k], m1 && m1[k]), ytd: ch(l[k], ys && ys[k]), y1: ch(l[k], y1 && y1[k]), lo: Math.min(...yr.map(r => r[k])), hi: Math.max(...yr.map(r => r[k]))}));
}});

dash.calc('goal_series', {inputs: ['goals', 'max_daily', 'max_summary', 'tg_subs_daily', 'platforms'], fn: (goals, max_daily, max_summary, tg_subs_daily, platforms) => {
  const out = [];
  const ms = [...max_summary].sort((a, b) => a.at < b.at ? -1 : 1).pop() || {};
  const series = {
    MAX: (() => { const d = [...max_daily].sort((a, b) => a.day < b.day ? -1 : 1).map(r => ({date: String(r.day).slice(0, 10), v: +r.subscribers})); if (d.length && ms.growth30 != null) { const last = d[d.length - 1]; const start = new Date(Date.parse(last.date) - 30 * 864e5).toISOString().slice(0, 10); if (!d.some(x => x.date <= start)) d.unshift({date: start, v: last.v - +ms.growth30}); } return {pts: d, pace: ms.growth30 != null ? +ms.growth30 / 30 : null, pace_src: 'за 30 дней'}; })(),
    Telegram: (() => { const d = [...tg_subs_daily].sort((a, b) => a.day < b.day ? -1 : 1).map(r => ({date: String(r.day).slice(0, 10), v: +r.subscribers})); const span = d.length > 1 ? (Date.parse(d[d.length - 1].date) - Date.parse(d[0].date)) / 864e5 : 0; return {pts: d, pace: span >= 3 ? (d[d.length - 1].v - d[0].v) / span : null, pace_src: 'за ' + Math.round(span) + ' дн.'}; })(),
    'ВКонтакте': (() => { const p = platforms.filter(r => r.platform === 'ВКонтакте').map(r => ({date: String(r.at).slice(0, 10), v: +r.subscribers})).sort((a, b) => a.date < b.date ? -1 : 1); const span = p.length > 1 ? (Date.parse(p[p.length - 1].date) - Date.parse(p[0].date)) / 864e5 : 0; return {pts: p, pace: span >= 7 ? (p[p.length - 1].v - p[0].v) / span : null, pace_src: 'за ' + Math.round(span) + ' дн.'}; })()
  };
  goals.forEach(g => {
    const s = series[g.platform]; if (!s || !s.pts.length) return;
    const first = s.pts[0], last = s.pts[s.pts.length - 1];
    s.pts.forEach(p => out.push({id: g.platform + '_a_' + p.date, platform: g.platform, date: p.date, actual: p.v, plan: null, forecast: null, target: +g.target, deadline: g.deadline}));
    out.push({id: g.platform + '_p0', platform: g.platform, date: first.date, actual: null, plan: first.v, forecast: null, target: +g.target, deadline: g.deadline});
    out.push({id: g.platform + '_p1', platform: g.platform, date: g.deadline, actual: null, plan: +g.target, forecast: null, target: +g.target, deadline: g.deadline});
    if (s.pace != null) { const days = (Date.parse(g.deadline) - Date.parse(last.date)) / 864e5; out.push({id: g.platform + '_f0', platform: g.platform, date: last.date, actual: null, plan: null, forecast: last.v, target: +g.target, deadline: g.deadline, pace: s.pace, pace_src: s.pace_src}); out.push({id: g.platform + '_f1', platform: g.platform, date: g.deadline, actual: null, plan: null, forecast: Math.round(last.v + s.pace * days), target: +g.target, deadline: g.deadline, pace: s.pace, pace_src: s.pace_src}); }
  });
  return out;
}});
dash.calc('goals_calc', {inputs: ['goals', 'goal_series'], fn: (goals, goal_series) => goals.map(g => {
  const a = goal_series.filter(r => r.platform === g.platform && r.actual != null).sort((x, y) => x.date < y.date ? -1 : 1);
  const cur = a.length ? a[a.length - 1].actual : +g.current; const lastDate = a.length ? a[a.length - 1].date : '2026-11-06';
  const f = goal_series.find(r => r.platform === g.platform && r.forecast != null && r.date === g.deadline);
  const days = Math.max(1, Math.round((Date.parse(g.deadline) - Date.parse(lastDate)) / 864e5));
  return {platform: g.platform, current: cur, target: +g.target, deadline: g.deadline, progress: +(cur / g.target * 100).toFixed(1), forecast: f ? f.forecast : null, pace_per_day: f ? +f.pace.toFixed(2) : null, need_per_day: +((g.target - cur) / days).toFixed(1), status: !f ? 'нет данных о темпе' : f.forecast >= g.target ? 'успеваем' : 'не успеваем'};
})});
dash.calc('platforms_cmp', {inputs: ['platforms', 'tg_kpi', 'tg_posts_history', 'max_summary', 'vk_posts', 'goal_series'], fn: (platforms, tg_kpi, tg_posts_history, max_summary, vk_posts, goal_series) => {
  const k = tg_kpi[0] || {}; const ms = [...max_summary].sort((a, b) => a.at < b.at ? -1 : 1).pop() || {};
  const last = Math.max(...tg_posts_history.map(p => Date.parse(String(p.posted).slice(0, 16) + 'Z')));
  const tg30 = tg_posts_history.filter(p => last - Date.parse(String(p.posted).slice(0, 16) + 'Z') <= 30 * 864e5);
  const vk = platforms.find(p => p.platform === 'ВКонтакте') || {};
  return [
    {platform: 'Telegram', url: 'https://t.me/lenoblinvest', subscribers: k.subscribers, posts30: k.posts, reach: k.avg_reach, err: k.err, react: tg30.length ? +(tg30.reduce((a, p) => a + (+p.reactions || 0), 0) / tg30.length).toFixed(1) : null, growth30: null},
    {platform: 'MAX', url: 'https://max.ru/id4703059140_gos', subscribers: +ms.subscribers, posts30: +ms.posts30, reach: +ms.avg_views_post, err: +ms.err, react: ms.avg_reactions_post != null ? +ms.avg_reactions_post : null, growth30: ms.growth30 != null ? +ms.growth30 : null},
    {platform: 'ВКонтакте', url: 'https://vk.com/lenoblinvest', subscribers: +vk.subscribers, posts30: null, reach: null, err: null, react: vk_posts.length ? +(vk_posts.reduce((a, p) => a + (+p.likes || 0), 0) / vk_posts.length).toFixed(1) : null, growth30: null}
  ];
}});
dash.calc('oil_last', {inputs: ['oil', 'fx'], fn: (oil, fx) => { const s = [...oil].sort((a, b) => a.date < b.date ? -1 : 1); const l = s[s.length - 1]; const ref = s.filter(r => Date.parse(r.date) <= Date.parse(l.date) - 30 * 864e5).pop() || s[0]; const usd = [...fx].sort((a, b) => a.date < b.date ? -1 : 1).pop(); return [{date: l.date, brent: l.brent, ch30: +((l.brent / ref.brent - 1) * 100).toFixed(1), rub: usd ? Math.round(l.brent * usd.usd) : null}]; }});
dash.calc('co_growth', {inputs: ['companies', 'company_jobs', 'company_tenders', 'fin_latest'], fn: (companies, company_jobs, company_tenders, fin_latest) => companies.map(c => {
  const j = company_jobs.find(r => r.company === c.company), t = company_tenders.find(r => r.company === c.company), f = fin_latest.find(r => r.company === c.company);
  const sig = (j && j.vacancies_spb_lo >= 5 ? 1 : 0) + (t && t.contracts > 0 ? 1 : 0) + (f && f.rev_change > 0 ? 1 : 0);
  const known = !!(j || t || f);
  return {company: c.company, url: t ? t.url : (j ? j.url : null), vacancies: j ? j.vacancies_spb_lo : null, contracts: t ? t.contracts : null, sum_mln: t ? t.sum_mln : null, rev_change: f ? f.rev_change : null, score: sig, status: !known ? 'нет данных' : sig >= 2 ? 'растёт' : sig === 1 ? 'есть сигнал' : 'нет сигналов'};
})});
dash.calc('co_map', {inputs: ['lo_districts', 'company_geo', 'companies'], fn: (lo_districts, company_geo, companies) => {
  const out = lo_districts.map(d => ({id: 'd_' + d.district, kind: 'district', name: d.district, path: d.path, n: companies.filter(c => String(c.district || '').startsWith(d.district)).length}));
  company_geo.forEach(g => { const c = companies.find(x => x.company === g.company) || {}; out.push({id: 'c_' + g.company, kind: 'company', name: g.company, lon: +g.lon, lat: +g.lat, place: g.place, tone: c.tone || 'нейтрально', event: c.last_event || ''}); });
  return out;
}});
dash.calc('media_monthly', {inputs: ['media_programs'], fn: (media_programs) => {
  const P = [['kl', '«Крутая Локация»'], ['aerlo', 'АЭРЛО'], ['sdelano', '«Сделано в Ленобласти»']];
  const MON = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'];
  const months = [...new Set(media_programs.map(r => r.month))].sort();
  const out = [];
  months.forEach(m => P.forEach(([k, label]) => { const rs = media_programs.filter(r => r.month === m); const part = rs.some(r => r.partial); out.push({id: m + '_' + k, month: m, month_label: MON[+m.slice(5, 7) - 1] + ' ' + m.slice(0, 4) + (part ? ' (неполный)' : ''), program: label, own: rs.filter(r => r.own).reduce((a, r) => a + (+r[k] || 0), 0), region: rs.filter(r => !r.own).reduce((a, r) => a + (+r[k] || 0), 0)}); }));
  return out;
}});
dash.calc('lo_last', {inputs: ['lo_series'], fn: (s) => { const M = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']; const Q = {'03': 'I кв.', '06': 'II кв.', '09': 'III кв.', '12': 'IV кв.'}; const pick = (k, how) => { const r = s.filter(x => x.indicator === k && x.value != null).sort((a, b) => String(a.period).localeCompare(String(b.period))).pop(); if (!r) return null; const y = String(r.period).slice(0, 4), m = String(r.period).slice(5, 7); const lbl = how === 'q' ? (Q[m] || M[+m - 1]) + ' ' + y : how === 'ytd' ? 'январь–' + M[+m - 1] + ' ' + y : M[+m - 1] + ' ' + y; return {indicator: 'lo_' + k, value: r.value, note: lbl}; }; return [pick('unemp', 'q'), pick('invest', 'ytd'), pick('prom', 'm'), pick('infl', 'm')].filter(Boolean); }});
// Новые блоки: инфляция, PMI, кредиты, соседи, организации
dash.calc('rf_infl_tiles', {inputs: ['rf_infl_week', 'rf_infl_month'], fn: (w, m) => { const lw = [...w].sort((a, b) => String(a.date).localeCompare(String(b.date))).pop() || {}; const lm = [...m].sort((a, b) => String(a.period).localeCompare(String(b.period))).pop() || {}; const M = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']; const p = String(lm.period || ''); return [{week: lw.week, wow: lw.wow, yoy: lw.yoy, m_label: p ? M[+p.slice(5, 7) - 1] + ' ' + p.slice(0, 4) : '—', m_yoy: lm.yoy}]; }});
dash.calc('rf_pmi_tiles', {inputs: ['rf_pmi'], fn: (s) => { const r = [...s].sort((a, b) => String(a.period).localeCompare(String(b.period))); const l = r[r.length - 1] || {}, p = r[r.length - 2] || {}; const M = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']; const n = (v, pv) => (v >= 50 ? 'рост' : 'спад') + (pv != null ? ', месяцем ранее ' + String(pv).replace('.', ',') : ''); return [{label: l.period ? M[+String(l.period).slice(5, 7) - 1] : '—', mfg: l.mfg, services: l.services, mfg_note: n(l.mfg, p.mfg), srv_note: n(l.services, p.services)}]; }});
dash.calc('rf_credit_tiles', {inputs: ['rf_loans', 'rf_rates'], fn: (g, r) => { const M = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']; const lab = (p) => p ? M[+String(p).slice(5, 7) - 1] + ' ' + String(p).slice(0, 4) : '—'; const lg = [...g].sort((a, b) => String(a.period).localeCompare(String(b.period))).pop() || {}; const lr = [...r].sort((a, b) => String(a.period).localeCompare(String(b.period))).pop() || {}; return [{yoy: lg.yoy, g_label: 'на ' + lab(lg.period), long: lr.long, msp_long: lr.msp_long, r_label: lab(lr.period)}]; }});
dash.calc('lo_orgs_tiles', {inputs: ['lo_orgs'], fn: (s) => { const r = [...s].sort((a, b) => String(a.period).localeCompare(String(b.period))); const l = r[r.length - 1] || {}; const y = String(l.period || '').slice(0, 4); return [{label: l.label, registered: l.registered, liquidated: l.liquidated, ytd: r.filter(x => String(x.period).startsWith(y)).reduce((a, x) => a + (+x.saldo || 0), 0)}]; }});
dash.calc('nb_pivot', {inputs: ['lo_neighbors'], fn: (s) => { const K = {'Ленинградская область': 'lo', 'Санкт-Петербург': 'spb', 'Новгородская область': 'nov', 'Псковская область': 'psk'}; const by = {}; s.forEach(r => { const o = by[r.ind] = by[r.ind] || {id: r.ind, indicator: r.indicator, period: r.period, order: r.order, ru: r.russia}; o[K[r.region]] = r.value; }); const lowGood = {infl: 1, unemp: 1}; return Object.values(by).map(o => { const vals = ['lo', 'spb', 'nov', 'psk'].map(k => o[k]).filter(v => v != null); const better = vals.filter(v => lowGood[o.id] ? v < o.lo : v > o.lo).length; o.place = (better + 1) + '-е' + (lowGood[o.id] ? ' (меньше — лучше)' : ''); return o; }); }});
// ВВП и ВРП
dash.calc('gdp_tiles', {inputs: ['gdp_rf'], fn: (g) => { const last = (k, est) => { const rs = g.filter(r => r.kind === k && (est == null || r.est === est)).sort((a, b) => a.order - b.order); return rs[rs.length - 1] || {}; }; const y = last('год', false), q = last('квартал'), m = last('месяц'), f = last('год', true); return [{y_label: y.period, y_growth: y.growth, y_nom: y.nominal, q_label: q.period, q_growth: q.growth, m_label: m.period, m_growth: m.growth, f_label: f.period, f_growth: f.growth}]; }});
dash.calc('grp_tiles', {inputs: ['grp_lo'], fn: (g) => { const a = g.filter(r => !r.est); const l = a[a.length - 1] || {}; const e = g.filter(r => r.est).pop() || {}; return [{l_year: l.year, l_grp: l.grp / 1000, l_real: l.real_pct, e_year: e.year, e_grp: e.grp / 1000, e_real: e.real_pct}]; }});
dash.draw('vbars', (el) => { try { lxVbars(el); } catch (e) { el.replaceChildren(); const p = document.createElement('div'); p.className = 'lx-fail'; p.textContent = 'График не построился: ' + e.message; el.append(p); } });
const lxVbars = (el) => {
  let rows = prep(el); if (!rows) return;
  if (el.dataset.kind) rows = rows.filter(r => String(r.kind) === el.dataset.kind);
  if (rows.length && rows[0].order != null) rows = [...rows].sort((a, b) => a.order - b.order);
  const xk = el.dataset.x, yk = el.dataset.y, fmt = FMT[el.dataset.fmt || 'num'];
  const data = rows.filter(r => r[yk] != null).map(r => ({k: String(r[xk]), v: +r[yk], est: !!r.est, r}));
  const W = el.clientWidth || 600, H = +(el.dataset.h || 220), m = {t: 20, r: 8, b: 30, l: 8};
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`);
  const x = d3.scaleBand(data.map(d => d.k), [m.l, W - m.r]).padding(0.3);
  const lo = Math.min(0, d3.min(data, d => d.v)), hi = Math.max(0, d3.max(data, d => d.v));
  const y = d3.scaleLinear([lo, hi], [H - m.b, m.t]).nice();
  svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(0)).attr('y2', y(0)).attr('stroke', 'var(--cds-chart-axis)');
  const t = tip(el);
  svg.append('g').selectAll('rect').data(data).join('rect')
    .attr('x', d => x(d.k)).attr('width', x.bandwidth())
    .attr('y', d => Math.min(y(d.v), y(0))).attr('height', d => Math.max(1, Math.abs(y(d.v) - y(0))))
    .attr('rx', 2).attr('fill', d => d.v < 0 ? 'var(--color-bad)' : dash.colors[0]).attr('fill-opacity', d => d.est ? 0.45 : 1)
    .on('pointerenter', (ev, d) => { const sx = el.clientWidth / W; setTip(t, el, (x(d.k) + x.bandwidth() / 2) * sx, Math.min(y(d.v), y(0)) * sx, d.k + ': ' + fmt(d.v) + (el.dataset.unit || ''), d.r.note || ''); })
    .on('pointerleave', () => { t.hidden = true; });
  svg.append('g').selectAll('text').data(data).join('text').attr('x', d => x(d.k) + x.bandwidth() / 2).attr('y', d => d.v < 0 ? y(d.v) + 13 : y(d.v) - 5).attr('text-anchor', 'middle').attr('fill', 'var(--color-fg)').style('font-size', 'var(--cds-font-size-caption)').text(d => fmt(d.v) + (el.dataset.unit || ''));
  const two = (s) => { const i = s.indexOf(' ('); if (i > 0) return [s.slice(0, i), s.slice(i + 1)]; const j = s.lastIndexOf(' '); return j > 0 ? [s.slice(0, j), s.slice(j + 1)] : [s]; };
  const xl = svg.append('g').selectAll('text').data(data).join('text').attr('text-anchor', 'middle').attr('fill', 'var(--color-fg-muted)').style('font-size', '11px');
  xl.each(function (d) { const parts = two(d.k); const cx = x(d.k) + x.bandwidth() / 2; parts.forEach((p, i) => { const ts = document.createElementNS('http://www.w3.org/2000/svg', 'tspan'); ts.setAttribute('x', cx); ts.setAttribute('y', H - (parts.length === 2 ? 17 : 10) + i * 12); ts.textContent = p; this.append(ts); }); });
};
dash.calc('media_sum', {inputs: ['media_monthly'], fn: (media_monthly) => { const full = media_monthly.filter(r => !/неполный/.test(r.month_label)); const m = full.map(r => r.month).sort().pop(); const rs = full.filter(r => r.month === m); return [{month: m, month_label: rs[0] ? rs[0].month_label.replace(/ \d{4}$/, '') : '—', own: rs.reduce((a, r) => a + r.own, 0), region: rs.reduce((a, r) => a + r.region, 0)}]; }});

// Цели: факт, план, прогноз
dash.draw('goalchart', (el) => {
  let rows = prep(el); if (!rows) return;
  if (el.dataset.filter) { const [fk, fv] = el.dataset.filter.split('='); rows = rows.filter(r => String(r[fk]) === fv); }
  if (!rows.length) { const p = document.createElement('div'); p.className = 'lx-fail'; p.textContent = 'Нет данных'; el.replaceChildren(p); return; }
  const D = (s) => new Date(String(s).slice(0, 10) + 'T00:00:00Z');
  const act = rows.filter(r => r.actual != null).map(r => ({x: D(r.date), y: +r.actual})).sort((a, b) => a.x - b.x);
  const plan = rows.filter(r => r.plan != null).map(r => ({x: D(r.date), y: +r.plan})).sort((a, b) => a.x - b.x);
  const fc = rows.filter(r => r.forecast != null).map(r => ({x: D(r.date), y: +r.forecast})).sort((a, b) => a.x - b.x);
  const target = +rows[0].target, dl = D(rows[0].deadline);
  const W = el.clientWidth || 320, H = +(el.dataset.h || 200), m = {t: 16, r: 14, b: 24};
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`);
  const ys = act.concat(plan, fc).map(p => p.y).concat([target]);
  let lo = d3.min(ys), hi = d3.max(ys); const pad = (hi - lo) * 0.08 || hi * 0.02 || 1;
  const y = d3.scaleLinear([lo - pad, hi + pad], [H - m.b, m.t]).nice();
  const ax = yAxisLeft(svg, y, H, (v) => ru.format(',.0f')(v), 4); const L = ax.w + 10; ax.g.attr('transform', `translate(${L - 6},0)`);
  const xs = act.concat(plan, fc).map(p => p.x);
  const x = d3.scaleUtc([d3.min(xs), d3.max(xs.concat([dl]))], [L, W - m.r]);
  svg.append('g').selectAll('line').data(y.ticks(4)).join('line').attr('x1', L).attr('x2', W - m.r).attr('y1', d => y(d)).attr('y2', d => y(d)).attr('stroke', 'var(--cds-chart-grid)');
  const gx = svg.append('g').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(Math.max(2, Math.floor((W - L) / 70))).tickFormat(v => fmtShort(v)).tickSize(0).tickPadding(8)); styleAxis(gx);
  const line = d3.line().x(d => x(d.x)).y(d => y(d.y));
  svg.append('line').attr('x1', L).attr('x2', W - m.r).attr('y1', y(target)).attr('y2', y(target)).attr('stroke', 'var(--cds-chart-axis)').attr('stroke-width', 1);
  svg.append('text').text('цель ' + ru.format(',.0f')(target)).attr('x', W - m.r).attr('y', y(target) - 4).attr('text-anchor', 'end').attr('fill', 'var(--color-fg-muted)').style('font-size', 'var(--cds-font-size-caption)');
  if (plan.length > 1) svg.append('path').datum(plan).attr('fill', 'none').attr('stroke', 'var(--cds-chart-muted)').attr('stroke-width', 2).attr('stroke-dasharray', '6 4').attr('d', line);
  if (fc.length > 1) { svg.append('path').datum(fc).attr('fill', 'none').attr('stroke', dash.colors[0]).attr('stroke-width', 2).attr('stroke-dasharray', '1 4').attr('stroke-linecap', 'round').attr('d', line); const f = fc[fc.length - 1]; svg.append('circle').attr('cx', x(f.x)).attr('cy', y(f.y)).attr('r', 3.5).attr('fill', f.y >= target ? 'var(--color-ok)' : 'var(--color-bad)'); svg.append('text').text('прогноз ' + ru.format(',.0f')(f.y)).attr('x', x(f.x) - 6).attr('y', y(f.y) + (f.y >= target ? -8 : 14)).attr('text-anchor', 'end').attr('fill', f.y >= target ? 'var(--color-ok)' : 'var(--color-bad)').style('font-size', 'var(--cds-font-size-caption)'); }
  if (act.length > 1) svg.append('path').datum(act).attr('fill', 'none').attr('stroke', dash.colors[0]).attr('stroke-width', 2.5).attr('stroke-linejoin', 'round').attr('d', line);
  svg.append('g').selectAll('circle').data(act).join('circle').attr('cx', d => x(d.x)).attr('cy', d => y(d.y)).attr('r', act.length > 12 ? 0 : 3).attr('fill', dash.colors[0]);
});
dash.draw('lomap', (el) => {
  const rows = prep(el); if (!rows) return;
  const ds = rows.filter(r => r.kind === 'district').map(r => ({...r, pts: String(r.path).split(' ').map(s => s.split(',').map(Number))}));
  const cs = rows.filter(r => r.kind === 'company');
  const all = ds.flatMap(d => d.pts);
  const minLon = d3.min(all, p => p[0]), maxLon = d3.max(all, p => p[0]), minLat = d3.min(all, p => p[1]), maxLat = d3.max(all, p => p[1]);
  const kx = Math.cos(60 * Math.PI / 180);
  const W = el.clientWidth || 600, pad = 8;
  const s = (W - 2 * pad) / ((maxLon - minLon) * kx);
  const H = Math.round((maxLat - minLat) * s + 2 * pad);
  const px = (lon) => pad + (lon - minLon) * kx * s, py = (lat) => pad + (maxLat - lat) * s;
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`);
  const maxN = d3.max(ds, d => d.n) || 1;
  svg.append('g').selectAll('path').data(ds).join('path').attr('d', d => 'M' + d.pts.map(p => px(p[0]).toFixed(1) + ',' + py(p[1]).toFixed(1)).join('L') + 'Z').attr('fill', d => d.n ? dash.colors[0] : 'var(--color-panel)').attr('fill-opacity', d => d.n ? 0.12 + 0.28 * d.n / maxN : 1).attr('stroke', 'var(--cds-chart-axis)').attr('stroke-width', 0.8).attr('stroke-linejoin', 'round');
  if (W >= 480) svg.append('g').selectAll('text').data(ds).join('text').text(d => d.name).each(function (d) { const c = d3.polygonCentroid(d.pts.map(p => [px(p[0]), py(p[1])])); d3.select(this).attr('x', c[0]).attr('y', c[1]); }).attr('text-anchor', 'middle').attr('fill', 'var(--color-fg-muted)').style('font-size', '10px').style('pointer-events', 'none').style('opacity', 0.75);
  const short = (n) => n.replace(/ \(.*\)$/, '').replace('Тихвинский вагоностроительный завод', 'ТВСЗ').replace(' / Технофлекс', '');
  const g = svg.append('g').selectAll('g').data(cs).join('g').attr('transform', c => `translate(${px(c.lon)},${py(c.lat)})`);
  g.append('circle').attr('r', 6).attr('fill', c => toneColor(c.tone)).attr('stroke', 'var(--color-bg)').attr('stroke-width', 2);
  const OFF = {'Катюша': [-9, 4, 'end'], 'Любимый край': [-9, 4, 'end'], 'Северная звезда': [-9, -4, 'end'], 'Систэм Электрик': [6, 18, 'start'], 'Технониколь / Технофлекс': [9, -4, 'start']};
  if (W >= 420) g.append('text').text(c => short(c.name)).attr('x', c => (OFF[c.name] || [9])[0]).attr('y', c => (OFF[c.name] || [9, 4])[1]).attr('text-anchor', c => (OFF[c.name] || [0, 0, 'start'])[2]).attr('fill', 'var(--color-fg)').style('font-size', 'var(--cds-font-size-caption)').style('paint-order', 'stroke').style('stroke', 'var(--color-bg)').style('stroke-width', '3px');
});
