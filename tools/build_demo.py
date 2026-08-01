#!/usr/bin/env python3
"""Generate demo.html from index.html.

The real app is left byte-for-byte intact; we only *prepend* a harness that
overrides navigator.geolocation and window.fetch so the untouched app logic
runs against a simulated drive with mock ALPR cameras. This keeps index.html
as the single source of truth for the actual application code.
"""
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent

src = (REPO / "index.html").read_text()

# --- 0. Use locally-vendored Leaflet so the demo is fully self-contained
#        and works offline / in sandboxes with no CDN access. -------------
src = src.replace(
    '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"\n'
    '      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">',
    '<link rel="stylesheet" href="vendor/leaflet.css">',
    1,
)
src = src.replace(
    '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"\n'
    '        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>',
    '<script src="vendor/leaflet.js"></script>',
    1,
)

# --- 1. Demo panel CSS (injected before </style>) ------------------------
DEMO_CSS = r"""
  /* ---------- Demo control panel ---------- */
  #demoPanel {
    position: absolute;
    top: 62px; left: 10px;   /* sits below the alert banner when it shows */
    z-index: 1500;
    width: min(300px, 88vw);
    background: rgba(22,27,34,.94);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 12px 14px;
    box-shadow: 0 4px 16px rgba(0,0,0,.55);
    backdrop-filter: blur(4px);
  }
  #demoPanel .tag {
    display: inline-block;
    font-size: 10.5px; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase;
    color: #04121f; background: var(--accent);
    padding: 2px 7px; border-radius: 5px; margin-bottom: 8px;
  }
  #demoPanel h1 { font-size: 15px; margin-bottom: 6px; }
  #demoPanel p { font-size: 12px; color: var(--muted); line-height: 1.5; margin-bottom: 10px; }
  #demoPanel .ctrls { display: flex; gap: 6px; flex-wrap: wrap; }
  #demoPanel .ctrls button {
    background: var(--panel-2); border: 1px solid var(--border);
    color: var(--text); border-radius: 7px; padding: 7px 10px;
    font-size: 13px; cursor: pointer; flex: 0 0 auto;
  }
  #demoPanel .ctrls button.on { background: var(--accent); border-color: var(--accent); color: #04121f; font-weight: 600; }
  #demoPanel .legend { margin-top: 10px; font-size: 11.5px; color: var(--muted); line-height: 1.7; }
  #demoPanel .legend .dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 6px; border: 1px solid #fff; vertical-align: middle; }
  #demoPanel .legend .d-red { background: #f85149; }
  #demoPanel .legend .d-amber { background: #d29922; }
  #demoPanel .legend .d-grey { background: #6e7681; }
  #demoPanel .collapse { position: absolute; top: 8px; right: 10px; background: none; border: none; color: var(--muted); font-size: 18px; cursor: pointer; line-height: 1; }
  #demoPanel.min .body { display: none; }
  #demoPanel.min { width: auto; }
"""

src = src.replace("</style>", DEMO_CSS + "\n</style>", 1)

# --- 2. Demo panel HTML (injected after the toast div) -------------------
DEMO_HTML = r"""
<div id="demoPanel">
  <button class="collapse" id="demoCollapse" title="Collapse">–</button>
  <span class="tag">Demo · simulated drive</span>
  <div class="body">
    <h1>FlockOff live demo</h1>
    <p>A simulated car is driving a downtown route past mock ALPR cameras.
       Watch the banner, status bar, and marker colors react in real time —
       this is the real app logic, fed a fake GPS + camera feed.</p>
    <div class="ctrls">
      <button id="demoPlay" class="on">⏸ Pause</button>
      <button id="demoRestart">↺ Restart</button>
      <button id="demoS1" class="on">1×</button>
      <button id="demoS2">2×</button>
      <button id="demoS4">4×</button>
    </div>
    <div class="legend">
      <div><span class="dot d-red"></span> inside alert radius (alert fires)</div>
      <div><span class="dot d-amber"></span> within 2× radius (approaching)</div>
      <div><span class="dot d-grey"></span> known camera, farther away</div>
    </div>
  </div>
</div>
"""

src = src.replace('<div id="toast"></div>', '<div id="toast"></div>\n' + DEMO_HTML, 1)

# --- 3. Simulation harness (injected BEFORE the app's inline script) -----
HARNESS = r"""<script>
/* ============================================================
   DEMO HARNESS  (not part of the real app)
   Overrides geolocation + fetch so the untouched application
   below runs against a simulated drive and mock camera data.
   ============================================================ */
(function () {
  "use strict";

  // Start every demo from a clean, known state.
  try {
    localStorage.removeItem("alprmap.cameras.v1");
    localStorage.removeItem("alprmap.lastview.v1");
    localStorage.setItem("alprmap.settings.v1", JSON.stringify({
      alertRadiusM: 300, fetchRadiusKm: 10, maxAgeH: 24, headingFilter: false,
      chAudio: true, chVisual: true, chHaptic: true, muted: false, follow: true
    }));
  } catch (e) {}

  // ---- Mock ALPR cameras (OSM/Overpass node shape) ----
  var CAMERAS = [
    { id: 1001, lat: 33.7482, lon: -84.3905, tags: { "surveillance:type": "ALPR", operator: "Flock Safety", manufacturer: "Flock Safety", direction: "270", start_date: "2024-11-02" } },
    { id: 1002, lat: 33.7478, lon: -84.3852, tags: { "surveillance:type": "ALPR", operator: "City of Atlanta PD", direction: "90", start_date: "2025-01-15" } },
    { id: 1003, lat: 33.7515, lon: -84.3845, tags: { "surveillance:type": "ALPR", operator: "Flock Safety", manufacturer: "Flock Safety", direction: "0", start_date: "2024-08-20" } },
    { id: 1004, lat: 33.7558, lon: -84.3852, tags: { "surveillance:type": "ALPR", operator: "Vigilant Solutions", direction: "180", start_date: "2023-12-01" } },
    { id: 1005, lat: 33.7562, lon: -84.3792, tags: { "surveillance:type": "ALPR", operator: "Flock Safety", manufacturer: "Flock Safety", direction: "90", start_date: "2025-03-10" } },
    { id: 1006, lat: 33.7560, lon: -84.3735, tags: { "surveillance:type": "ALPR", operator: "GDOT", direction: "90", start_date: "2025-05-05" } },
    { id: 1007, lat: 33.7500, lon: -84.3905, tags: { "surveillance:type": "ALPR", operator: "Flock Safety", direction: "180", start_date: "2025-02-18" } },
    { id: 1008, lat: 33.7540, lon: -84.3808, tags: { "surveillance:type": "ALPR", operator: "Flock Safety", direction: "0", start_date: "2025-04-22" } }
  ];

  // ---- Mock Overpass endpoint ----
  var realFetch = (typeof window.fetch === "function") ? window.fetch.bind(window) : null;
  window.fetch = function (url, opts) {
    var u = String(url);
    if (u.indexOf("overpass") >= 0 || u.indexOf("interpreter") >= 0) {
      var elements = CAMERAS.map(function (c) {
        return { type: "node", id: c.id, lat: c.lat, lon: c.lon, tags: c.tags };
      });
      // Small delay so the "fetching…" state is briefly visible, like the real thing.
      return new Promise(function (resolve) {
        setTimeout(function () {
          resolve({ ok: true, status: 200, json: function () { return Promise.resolve({ elements: elements }); } });
        }, 350);
      });
    }
    return realFetch ? realFetch(url, opts) : Promise.reject(new Error("network disabled in demo"));
  };

  // ---- Route the simulated car follows ----
  var WP = [
    [33.7480, -84.3990],
    [33.7480, -84.3905],
    [33.7480, -84.3850],
    [33.7515, -84.3848],
    [33.7560, -84.3850],
    [33.7560, -84.3790],
    [33.7560, -84.3720]
  ];

  function hav(la1, lo1, la2, lo2) {
    var R = 6371000, tr = function (d) { return d * Math.PI / 180; };
    var dLa = tr(la2 - la1), dLo = tr(lo2 - lo1);
    var a = Math.sin(dLa / 2) * Math.sin(dLa / 2) +
            Math.cos(tr(la1)) * Math.cos(tr(la2)) * Math.sin(dLo / 2) * Math.sin(dLo / 2);
    return 2 * R * Math.asin(Math.sqrt(a));
  }
  function brg(la1, lo1, la2, lo2) {
    var tr = function (d) { return d * Math.PI / 180; };
    var y = Math.sin(tr(lo2 - lo1)) * Math.cos(tr(la2));
    var x = Math.cos(tr(la1)) * Math.sin(tr(la2)) -
            Math.sin(tr(la1)) * Math.cos(tr(la2)) * Math.cos(tr(lo2 - lo1));
    return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
  }

  // Precompute segments with cumulative start distance + heading.
  var SEG = [], total = 0;
  for (var i = 0; i < WP.length - 1; i++) {
    var a = WP[i], b = WP[i + 1];
    var len = hav(a[0], a[1], b[0], b[1]);
    SEG.push({ a: a, b: b, len: len, cum: total, brg: brg(a[0], a[1], b[0], b[1]) });
    total += len;
  }

  function ptAtDist(m) {
    if (m <= 0) return { lat: SEG[0].a[0], lon: SEG[0].a[1], heading: SEG[0].brg };
    for (var i = 0; i < SEG.length; i++) {
      var s = SEG[i];
      if (m >= s.cum && m <= s.cum + s.len) {
        var f = s.len ? (m - s.cum) / s.len : 0;
        return { lat: s.a[0] + (s.b[0] - s.a[0]) * f, lon: s.a[1] + (s.b[1] - s.a[1]) * f, heading: s.brg };
      }
    }
    var last = SEG[SEG.length - 1];
    return { lat: last.b[0], lon: last.b[1], heading: last.brg };
  }

  // ---- Fake geolocation ----
  // navigator.geolocation is a getter-only accessor, so we can't assign to it;
  // define a shadowing own-property with our simulated implementation.
  var successCb = null;
  var fakeGeo = {
    watchPosition: function (s) { successCb = s; return 1; },
    clearWatch: function () {},
    getCurrentPosition: function (s) { if (lastPt) s(makePos(lastPt)); }
  };
  try {
    Object.defineProperty(navigator, "geolocation", { value: fakeGeo, configurable: true });
  } catch (e) {
    try { navigator.geolocation.watchPosition = fakeGeo.watchPosition; } catch (e2) {}
  }

  var BASE = 13;        // metres/second baseline (~47 km/h)
  var dist = 0, playing = true, mult = 1, lastTs = null, lastPt = null;

  function makePos(p) {
    return { coords: { latitude: p.lat, longitude: p.lon, accuracy: 8, heading: p.heading, speed: BASE * mult }, timestamp: Date.now() };
  }

  function tick(ts) {
    requestAnimationFrame(tick);
    if (lastTs === null) lastTs = ts;
    var dt = (ts - lastTs) / 1000; lastTs = ts;
    if (!playing || !successCb) return;
    dist += BASE * mult * dt;
    if (dist > total) { dist = 0; }          // loop the drive
    lastPt = ptAtDist(dist);
    successCb(makePos(lastPt));
  }
  requestAnimationFrame(tick);

  // Exposed for the demo control panel.
  window.__demo = {
    play: function () { playing = true; },
    pause: function () { playing = false; },
    toggle: function () { playing = !playing; return playing; },
    restart: function () { dist = 0; },
    setSpeed: function (x) { mult = x; },
    isPlaying: function () { return playing; }
  };
})();
</script>
"""

app_anchor = '<script>\n"use strict";'
assert app_anchor in src, "could not find the app script anchor"
src = src.replace(app_anchor, HARNESS + "\n" + app_anchor, 1)

# --- 4. Wire the demo panel controls (injected before </body>) -----------
WIRING = r"""<script>
/* Demo panel wiring (runs after the app has booted). */
(function () {
  "use strict";
  // The live demo auto-runs, so dismiss the start gate for the viewer
  // (also unlocks audio + attempts the wake lock, exercising that path).
  var sg = document.getElementById("startGate");
  if (sg) { var bs = document.getElementById("btnStart"); if (bs) bs.click(); else sg.classList.remove("show"); }

  var play = document.getElementById("demoPlay");
  var speedBtns = { 1: document.getElementById("demoS1"), 2: document.getElementById("demoS2"), 4: document.getElementById("demoS4") };

  play.onclick = function () {
    var p = window.__demo.toggle();
    play.textContent = p ? "⏸ Pause" : "▶ Play";
    play.classList.toggle("on", p);
  };
  document.getElementById("demoRestart").onclick = function () { window.__demo.restart(); };

  function setSpeed(x) {
    window.__demo.setSpeed(x);
    for (var k in speedBtns) speedBtns[k].classList.toggle("on", +k === x);
  }
  speedBtns[1].onclick = function () { setSpeed(1); };
  speedBtns[2].onclick = function () { setSpeed(2); };
  speedBtns[4].onclick = function () { setSpeed(4); };

  var panel = document.getElementById("demoPanel");
  document.getElementById("demoCollapse").onclick = function () {
    panel.classList.toggle("min");
    this.textContent = panel.classList.contains("min") ? "+" : "–";
  };
})();
</script>
"""

src = src.replace("</body>", WIRING + "\n</body>", 1)

out = REPO / "demo.html"
out.write_text(src)
print("wrote", out, "(", len(src), "bytes )")
