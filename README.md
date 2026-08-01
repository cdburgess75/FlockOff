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
