/* FlockOff service worker.
   Version is stamped in at deploy time so every release ships a *different*
   worker — that's what lets the browser notice an update at all.

   Cache strategy:
   - HTML / navigations: NETWORK-FIRST, so a new deploy shows up as soon as
     you're online (falling back to cache when offline). The old cache-first
     approach is exactly why installs got stuck on a stale version.
   - Static assets (JS/CSS/icons): cache-first, but the cache name carries the
     version, so a new release starts a fresh cache and drops the old one.
   - Map tiles: cache-first into a capped cache, so seen areas work offline.
   Overpass POSTs are left to the app's own localStorage cache. */

const VERSION    = "__BUILD_VERSION__";
const APP_CACHE  = "flockoff-app-" + VERSION;
const TILE_CACHE = "flockoff-tiles-v1";
const TILE_MAX   = 400;

const APP_SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./vendor/leaflet.css",
  "./vendor/leaflet.js",
  "./vendor/images/marker-icon.png",
  "./vendor/images/marker-icon-2x.png",
  "./vendor/images/marker-shadow.png",
  "./vendor/images/layers.png",
  "./vendor/images/layers-2x.png",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-512.png",
];

self.addEventListener("install", (e) => {
  // No skipWaiting here: a first install (no existing worker) activates on its
  // own; an *update* waits so the page can offer an "Update now" button.
  e.waitUntil(
    caches.open(APP_CACHE).then((c) =>
      Promise.all(APP_SHELL.map((u) => c.add(u).catch(() => {})))
    )
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k !== APP_CACHE && k !== TILE_CACHE).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// The page posts this when the user taps "Update now".
self.addEventListener("message", (e) => {
  if (e.data && e.data.type === "SKIP_WAITING") self.skipWaiting();
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;              // Overpass POST etc. → network

  const url = new URL(req.url);
  const sameOrigin = url.origin === self.location.origin;

  // HTML / navigations: network-first so updates land when online.
  if (req.mode === "navigate" || (sameOrigin && url.pathname.endsWith(".html"))) {
    e.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(APP_CACHE).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      }).catch(() => caches.match(req).then((h) => h || caches.match("./index.html")))
    );
    return;
  }

  // Cross-origin (map tiles): cache-first, capped.
  if (!sameOrigin) {
    e.respondWith(tileFirst(req));
    return;
  }

  // Same-origin static assets: cache-first, fall back to network.
  e.respondWith(
    caches.match(req).then((hit) =>
      hit || fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(APP_CACHE).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      })
    )
  );
});

async function tileFirst(req) {
  const cache = await caches.open(TILE_CACHE);
  const hit = await cache.match(req);
  if (hit) return hit;
  try {
    const res = await fetch(req);
    cache.put(req, res.clone());
    trim(cache, TILE_MAX);
    return res;
  } catch (e) {
    return hit || Response.error();
  }
}

async function trim(cache, max) {
  const keys = await cache.keys();
  if (keys.length <= max) return;
  for (let i = 0; i < keys.length - max; i++) cache.delete(keys[i]);
}
