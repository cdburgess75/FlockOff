# FlockOff

FlockOff is a driver-facing map of the **ALPR surveillance dragnet** —
automated license-plate readers from Flock Safety and similar operators —
built from the crowdsourced [DeFlock](https://deflock.me) tags in
OpenStreetMap. It shows the cameras around you on a street map and gives a
real-time heads-up as you approach one.

**What it's for.** ALPR cameras log where your car is, when, and pool that
history across police departments and private operators — silently,
retroactively, at scale. Most people have no idea how densely they're
tracked. FlockOff exists to make that invisible network **visible to the
people driving through it**: you should get to know when and where you're
being read.

**What it is _not_.** It is not a routing engine. FlockOff never plans a
path to avoid cameras — it tells you what's around you and leaves the
driving to you. And it does not touch the cameras: it reads public map data
and your own device GPS, on your device, and interferes with no signal or
system.

> **Positioning, distribution, and the reasoning behind every major design
> choice live in [`docs/DIRECTION.md`](docs/DIRECTION.md).** Read that first
> if you want the *why*.

---

## Use it

Open `index.html` in a browser — as a local file, via GitHub Pages, or
installed as a PWA — and tap **"Enable alerts & keep screen on."** That one
gesture unlocks alert audio (browsers block sound until you interact) and
holds a screen Wake Lock so the app doesn't sleep in a mount. Grant location
access and drive. Camera data and settings are cached in `localStorage`, and
Leaflet is bundled under `vendor/`, so after the first successful load the
app keeps working fully offline (freshness is always shown in the status
bar). Distances can be shown in miles/feet or km/m — see the settings drawer.

Because it runs in the browser, treat it as a **foreground, screen-on**
tool: mounted and awake, not asleep in your pocket. Hardening this
(Wake Lock, install prompt, audio-first alerts) is the near-term priority —
see the roadmap.

- **Alerts:** audible double-beep, red banner, and vibration when the
  nearest camera crosses the alert radius (default 300 m). Each channel is
  toggleable; there's a master mute. Alerts are debounced — once per camera
  per approach, with a cooldown and hysteresis so a single camera doesn't
  chatter.
- **Settings drawer (⚙):** alert radius, fetch radius, cache max age,
  optional "only alert if camera is ahead" heading filter (±60°),
  refresh-now, clear-cache.
- **Markers:** grey = known camera, amber = within 2× the alert radius,
  red = inside it. Tap one for operator, brand, facing direction, and
  report date.

## What it maps and alerts on

All surveillance categories present in OpenStreetMap are — by direction —
**user-selectable**, because the data is public knowledge. The default
selection is **ALPR + acoustic gunshot sensors** (e.g. ShotSpotter): the
same mass-surveillance, dragnet character, and the cleanest civil-liberties
story.

Alerting is configurable per category. **Enabling real-time approach alerts
for traffic-enforcement cameras (speed / red-light) turns FlockOff into a
configurable enforcement-alert tool.** That is a deliberate, user-owned
choice — and it is also why the alerting build is **not** distributed
through the Apple or Google app stores (they treat it as a radar detector).
FlockOff ships as a **web app / PWA and direct install**. See
[`docs/DIRECTION.md`](docs/DIRECTION.md) for the full reasoning.

> _Today the app queries ALPR only. Multi-category selection with separate
> "show on map" vs "alert" controls is the direction described below, not
> yet shipped._

## Coverage honesty — silence is not safety

This is the most important thing to understand about the tool.

- The dataset is **crowdsourced and incomplete.** An empty area does **not**
  mean no cameras — mobile/trailer units and unmapped installs won't appear.
- Mapped locations can be wrong, moved, or stale.
- **No beep does not mean no camera.** Do not let the quiet lull you.

The near-term work here is to surface a real **coverage / confidence**
signal (how well-surveyed your area is, how confirmed each point is), rather
than only the data-age line the status bar shows today. Unconfirmed
reports are meant to appear *dimmed and silent* until they're confirmed —
so a single bad or mistaken submission can't make the app cry wolf.

## Try the demo (no driving required)

Open `demo.html` in a browser to watch the app work without a phone, GPS, or
network. It runs the **real application code unchanged** but feeds it a
simulated car driving a downtown route past mock ALPR cameras, so you can
see the proximity alerts, banner, marker colors (grey → amber → red), and
status bar react in real time. Play/pause, restart, and a speed control are
in the panel. Leaflet is vendored under `vendor/` so the demo is fully
self-contained and works offline.

`demo.html` is generated from `index.html` by `tools/build_demo.py` — the
app itself stays the single source of truth; the script only prepends a
harness that overrides geolocation and the Overpass fetch.

## Contributing camera locations (direction)

The intended contribute-back loop: **tap to add a camera → it's written to
OpenStreetMap under your own account** (reusing DeFlock's pipeline, no
backend of ours). A freshly submitted point shows on the map **dimmed and
silent**; it only starts **alerting** once it is either

1. approved on the project's **owner-signed allowlist**, or
2. **auto-promoted** after _N_ independent confirmations.

This keeps the canonical data in OSM, keeps a human gate against poisoning,
and keeps that gate from being a permanent bottleneck. Rationale and the
approver's exit path are in [`docs/DIRECTION.md`](docs/DIRECTION.md).

## Deploy & install

The app is a static site — host `index.html` (plus `vendor/`, `icons/`,
`manifest.webmanifest`, and `sw.js`) anywhere.

- **GitHub Pages:** `.github/workflows/pages.yml` deploys on every push to
  the default branch. One-time setup: **Settings → Pages → Source →
  "GitHub Actions."** The workflow regenerates `demo.html` and publishes a
  clean `_site` (no repo cruft).
- **Install as an app:** served over HTTPS, a **service worker** precaches
  the app shell (HTML/JS/CSS/icons) and caches map tiles as you view them, so
  the whole app — not just the camera data — works offline. The
  `manifest.webmanifest` makes it installable to a home screen; on iOS use
  Share → *Add to Home Screen*.

Because it enables real-time approach alerts across camera categories, the
alerting build is intended for **web / PWA / direct install**, not the Apple
or Google app stores (see [`docs/DIRECTION.md`](docs/DIRECTION.md)).

## Roadmap

**Shipped:** coverage/confidence signal ("silence ≠ safety"), PWA install +
offline app shell, screen Wake Lock, dark basemap with OSM fallback, imperial
units, one-tap alert/audio start, and an auto-deploy to GitHub Pages.

Next, ordered by what moves the needle:

1. **Category system** — user-selectable surveillance categories with
   independent *show-on-map* vs *alert* controls and per-category
   radius/cooldown to manage alert fatigue.
2. **Confidence-gated alerting** — dimmed/silent until confirmed; owner
   allowlist + auto-promote-on-_N_-confirmations.
3. **Contribute back** — tap-to-add via OSM OAuth, feeding the allowlist.
4. **Voice callouts** — hands-free, eyes-on-road spoken alerts (Web Speech).
5. **Live detection (north star)** — a passive BLE/WiFi companion sniffer to
   surface cameras not yet in any database. The only true fix for coverage,
   and by far the hardest build — deliberately deferred.

Open questions still to resolve: distracted-driving UX & liability, a
jurisdiction/legal stance for enforcement alerting, and a hard "we transmit
nothing about you" user-privacy guarantee. See the direction doc.

## Data credits

Camera data © OpenStreetMap contributors (ODbL), via the Overpass API,
using the [DeFlock](https://deflock.me) tagging scheme. Map tiles ©
OpenStreetMap contributors & [CARTO](https://carto.com/attributions), with
the OSM standard tiles as a fallback.
