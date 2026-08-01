/* FlockOff service worker — makes the app installable and genuinely
   offline-first: the app shell (HTML/JS/CSS/icons) is precached, and map
   tiles are cached as you see them so recently-viewed areas keep working
   with no network. Overpass API calls (POST) are left to the app's own
   localStorage cache and never touched here. */

const APP_CACHE  = "flockoff-app-v1";
const TILE_CACHE = "flockoff-tiles-v1";
const TILE_MAX   = 400;   // rough LRU cap on cached tiles

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
  e.waitUntil(
    caches.open(APP_CACHE)
      // Tolerate individual misses so one 404 doesn't fail the whole install.
      .then((c) => Promise.all(APP_SHELL.map((u) => c.add(u).catch(() => {}))))
      .then(() => self.skipWaiting())
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

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;              // Overpass POST etc. → network

  const url = new URL(req.url);

  // Cross-origin GETs are map tiles (and web fonts): cache-first, capped.
  if (url.origin !== self.location.origin) {
    e.respondWith(tileFirst(req));
    return;
  }

  // Same-origin app shell: cache-first, fall back to network, then to the
  // cached index as a last resort so navigations always resolve.
  e.respondWith(
    caches.match(req).then((hit) =>
      hit || fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(APP_CACHE).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      }).catch(() => caches.match("./index.html"))
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
