/* Декоративные 3D-модели на canvas без внешних библиотек.
   Глобус из точек в шапке и полупрозрачные фигуры на фоне страницы.
   При prefers-reduced-motion фигуры рисуются один раз и не вращаются. */
(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function sphere(n) { // точки по спирали Фибоначчи
    var pts = [], g = Math.PI * (3 - Math.sqrt(5));
    for (var i = 0; i < n; i++) { var y = 1 - (i / (n - 1)) * 2, r = Math.sqrt(1 - y * y), t = g * i; pts.push([Math.cos(t) * r, y, Math.sin(t) * r]); }
    return pts;
  }
  function rings(lat, lon, seg) { // параллели и меридианы
    var lines = [], i, j, a, b;
    for (i = 1; i < lat; i++) { a = -Math.PI / 2 + Math.PI * i / lat; var l = []; for (j = 0; j <= seg; j++) { b = 2 * Math.PI * j / seg; l.push([Math.cos(a) * Math.cos(b), Math.sin(a), Math.cos(a) * Math.sin(b)]); } lines.push(l); }
    for (i = 0; i < lon; i++) { b = Math.PI * i / lon; var m = []; for (j = 0; j <= seg; j++) { a = 2 * Math.PI * j / seg; m.push([Math.cos(a) * Math.cos(b), Math.sin(a), Math.cos(a) * Math.sin(b)]); } lines.push(m); }
    return lines;
  }
  function torus(R, r, n1, n2) {
    var lines = [], i, j;
    for (i = 0; i < n1; i++) { var u = 2 * Math.PI * i / n1, l = []; for (j = 0; j <= n2; j++) { var v = 2 * Math.PI * j / n2; l.push([(R + r * Math.cos(v)) * Math.cos(u), r * Math.sin(v), (R + r * Math.cos(v)) * Math.sin(u)]); } lines.push(l); }
    for (j = 0; j < n2; j += 2) { var v2 = 2 * Math.PI * j / n2, m = []; for (i = 0; i <= n1 * 2; i++) { var u2 = 2 * Math.PI * i / (n1 * 2); m.push([(R + r * Math.cos(v2)) * Math.cos(u2), r * Math.sin(v2), (R + r * Math.cos(v2)) * Math.sin(u2)]); } lines.push(m); }
    return lines;
  }
  function ico() {
    var t = (1 + Math.sqrt(5)) / 2, v = [[-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0], [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t], [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]];
    var s = Math.sqrt(1 + t * t); v = v.map(function (p) { return [p[0] / s, p[1] / s, p[2] / s]; });
    var e = [], i, j; for (i = 0; i < 12; i++) for (j = i + 1; j < 12; j++) { var d = Math.hypot(v[i][0] - v[j][0], v[i][1] - v[j][1], v[i][2] - v[j][2]); if (d < 1.1) e.push([v[i], v[j]]); }
    return e;
  }
  function rot(p, ax, ay) {
    var x = p[0], y = p[1], z = p[2], cy = Math.cos(ay), sy = Math.sin(ay), cx = Math.cos(ax), sx = Math.sin(ax);
    var x1 = x * cy + z * sy, z1 = -x * sy + z * cy, y1 = y * cx - z1 * sx, z2 = y * sx + z1 * cx;
    return [x1, y1, z2];
  }
  function fit(cv) {
    var dpr = Math.min(window.devicePixelRatio || 1, 2), w = cv.clientWidth, h = cv.clientHeight;
    if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
    return {w: w, h: h, dpr: dpr};
  }

  // Глобус в шапке
  var hc = document.getElementById('globe3d');
  if (hc) {
    var gpts = sphere(520), glines = rings(7, 8, 72), hctx = hc.getContext('2d');
    var drawGlobe = function (t) {
      var f = fit(hc), c = hctx; c.setTransform(f.dpr, 0, 0, f.dpr, 0, 0); c.clearRect(0, 0, f.w, f.h);
      var R = Math.min(f.w, f.h) * 0.42, cx = f.w / 2, cy = f.h / 2, ay = t * 0.00025, ax = 0.35;
      var P = function (p) { var q = rot(p, ax, ay), k = 3.2 / (3.2 - q[2]); return [cx + q[0] * R * k, cy - q[1] * R * k, q[2]]; };
      c.lineWidth = 1;
      glines.forEach(function (l) { c.beginPath(); for (var i = 0; i < l.length; i++) { var p = P(l[i]); if (i) c.lineTo(p[0], p[1]); else c.moveTo(p[0], p[1]); } c.strokeStyle = 'rgba(255,255,255,0.16)'; c.stroke(); });
      gpts.forEach(function (p) { var q = P(p), a = 0.25 + 0.75 * (q[2] + 1) / 2; c.fillStyle = 'rgba(255,255,255,' + a.toFixed(2) + ')'; c.beginPath(); c.arc(q[0], q[1], 0.6 + a * 1.4, 0, 6.283); c.fill(); });
      // «спутник» — точка Ленобласти
      var s = P([Math.cos(1.05) * Math.cos(-0.53), Math.sin(1.05), Math.cos(1.05) * Math.sin(-0.53)]);
      if (s[2] > -0.2) { c.fillStyle = '#FDBC16'; c.beginPath(); c.arc(s[0], s[1], 4, 0, 6.283); c.fill(); c.strokeStyle = 'rgba(253,188,22,0.5)'; c.beginPath(); c.arc(s[0], s[1], 9 + 3 * Math.sin(t / 400), 0, 6.283); c.stroke(); }
    };
  }

  // Фигуры на фоне
  var bc = document.getElementById('bg3d');
  if (bc) {
    var shapes = [
      {kind: 'torus', lines: torus(1, 0.38, 28, 18), x: 0.88, y: 0.30, s: 0.17, sp: 0.00018, col: '123,77,219'},
      {kind: 'ico', edges: ico(), x: 0.08, y: 0.62, s: 0.12, sp: 0.00026, col: '18,170,158'},
      {kind: 'ico', edges: ico(), x: 0.70, y: 0.86, s: 0.07, sp: -0.00034, col: '128,79,128'}
    ];
    var bctx = bc.getContext('2d');
    var drawBg = function (t) {
      var f = fit(bc), c = bctx; c.setTransform(f.dpr, 0, 0, f.dpr, 0, 0); c.clearRect(0, 0, f.w, f.h);
      shapes.forEach(function (sh, k) {
        var R = Math.min(f.w, f.h) * sh.s, cx = f.w * sh.x, cy = f.h * sh.y + Math.sin(t / 2600 + k) * 12, ay = t * sh.sp, ax = t * sh.sp * 0.7 + k;
        var P = function (p) { var q = rot(p, ax, ay), kk = 3 / (3 - q[2]); return [cx + q[0] * R * kk, cy - q[1] * R * kk]; };
        c.strokeStyle = 'rgba(' + sh.col + ',0.22)'; c.lineWidth = 1;
        if (sh.kind === 'torus') sh.lines.forEach(function (l) { c.beginPath(); l.forEach(function (p, i) { var q = P(p); if (i) c.lineTo(q[0], q[1]); else c.moveTo(q[0], q[1]); }); c.stroke(); });
        else sh.edges.forEach(function (e) { var a = P(e[0]), b = P(e[1]); c.beginPath(); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); c.stroke(); });
      });
    };
  }

  var visible = true;
  document.addEventListener('visibilitychange', function () { visible = !document.hidden; if (visible && !reduce) requestAnimationFrame(loop); });
  function frame(t) { if (hc) drawGlobe(t); if (bc) drawBg(t); }
  function loop(t) { if (!visible) return; frame(t); requestAnimationFrame(loop); }
  if (reduce) frame(9000); else requestAnimationFrame(loop);
  window.addEventListener('resize', function () { if (reduce) frame(9000); });

  // Лёгкий 3D-наклон плиток за курсором
  if (!reduce && window.matchMedia('(hover: hover)').matches) {
    document.addEventListener('pointermove', function (e) {
      var el = e.target.closest && e.target.closest('.kpi-card, .lx-tile');
      document.querySelectorAll('.tilting').forEach(function (n) { if (n !== el) { n.classList.remove('tilting'); n.style.transform = ''; } });
      if (!el) return;
      var r = el.getBoundingClientRect(), px = (e.clientX - r.left) / r.width - 0.5, py = (e.clientY - r.top) / r.height - 0.5;
      el.classList.add('tilting'); el.style.transform = 'perspective(600px) rotateX(' + (-py * 8).toFixed(2) + 'deg) rotateY(' + (px * 10).toFixed(2) + 'deg) translateZ(4px)';
      el.style.setProperty('--mx', (px + 0.5) * 100 + '%'); el.style.setProperty('--my', (py + 0.5) * 100 + '%');
    });
  }
})();

/* Переключатель светлой и тёмной темы */
(function () {
  var btn = document.querySelector('.theme-toggle');
  if (!btn) return;
  btn.addEventListener('click', function () {
    var root = document.documentElement, t = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', t);
    try { localStorage.setItem('lxTheme', t); } catch (e) {}
    var pal = window.__lxPal && window.__lxPal[t];
    if (pal && window.dash && window.dash.colors) for (var i = 0; i < pal.length; i++) window.dash.colors[i] = pal[i];
    window.dispatchEvent(new Event('resize')); // перерисовать графики в новых цветах
  });
})();
