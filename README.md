# FlockOff

A single-file, offline-first web app that shows nearby ALPR (Flock and
similar) cameras on a street map and gives you a heads-up alert as you
approach one. Camera locations come from the crowdsourced DeFlock tags in
OpenStreetMap, fetched via the Overpass API.

**FlockOff is passive.** It reads public map data and your own device GPS.
It transmits nothing to any camera and does not interfere with any signal
or system. It's a privacy-awareness tool, not evasion.

## Use it

Open `index.html` in a browser — as a local file or via GitHub Pages —
grant location access, and drive. Camera data and settings are cached in
`localStorage`, so after the first successful load it keeps working
offline (data age is always shown in the status bar).

- **Alerts:** audible double-beep, red banner, and vibration when the
  nearest camera crosses the alert radius (default 300 m). Each channel
  is toggleable; there's a master mute. Alerts are debounced — once per
  camera per approach, with a cooldown.
- **Settings drawer (⚙):** alert radius, fetch radius, cache max age,
  optional "only alert if camera is ahead" heading filter (±60°),
  refresh-now, clear-cache.
- **Markers:** grey = known camera, amber = within 2× the alert radius,
  red = inside it. Tap one for operator, brand, facing direction, and
  report date.

## Try the demo (no driving required)

Open `demo.html` in a browser to watch the app work without a phone, GPS, or
network. It runs the **real application code unchanged** but feeds it a
simulated car driving a downtown route past mock ALPR cameras, so you can see
the proximity alerts, banner, marker colors (grey → amber → red), and status
bar react in real time. Play/pause, restart, and a speed control are in the
panel. Leaflet is vendored under `vendor/` so the demo is fully self-contained
and works offline.

`demo.html` is generated from `index.html` by `tools/build_demo.py` — the app
itself stays the single source of truth; the script only prepends a harness
that overrides geolocation and the Overpass fetch.

## Honest limitations

- The dataset is **crowdsourced and incomplete** — an empty area does not
  mean no cameras. Mobile/trailer units and unmapped installs won't appear.
- Mapped locations can be wrong, moved, or stale.

## Roadmap

1. **Live detection** — pair with a passive BLE/WiFi sniffer to surface
   cameras not yet in the database.
2. **Contribute back** — submit newly spotted cameras to OSM (OAuth).
3. **Route awareness** — list cameras along a planned route before driving.
4. **Heading-aware voice callouts** via the Web Speech API.

## Data credits

Camera data © OpenStreetMap contributors (ODbL), via the Overpass API,
using the [DeFlock](https://deflock.me) tagging scheme. Map tiles ©
OpenStreetMap.
