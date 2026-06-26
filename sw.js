/* ──────────────────────────────────────────────────────────────────────────
   Te Pā Tūwatawata — Service Worker (PWA) v3
   Strategy:
     - HTML pages: network-first, fall back to cache (always fresh)
     - CSS / JS / SVG / fonts: cache-first, long TTL
     - Images (PNG/JPG): stale-while-revalidate
   Ko te mātauranga he taonga nō te katoa — offline too.
────────────────────────────────────────────────────────────────────────── */

const CACHE_VERSION = 'kd-te-pa-v3';
const STATIC_CACHE  = `${CACHE_VERSION}-static`;
const IMAGE_CACHE   = `${CACHE_VERSION}-images`;
const ALL_CACHES    = [STATIC_CACHE, IMAGE_CACHE];

const PRECACHE_STATIC = [
  '/kiwi-dialectic-te-pa-minisite/',
  '/kiwi-dialectic-te-pa-minisite/index.html',
  '/kiwi-dialectic-te-pa-minisite/assets/kiwi-dialectic.css',
  '/kiwi-dialectic-te-pa-minisite/assets/search.js',
  '/kiwi-dialectic-te-pa-minisite/assets/rhizome-d3.js',
  '/kiwi-dialectic-te-pa-minisite/manifest.json',
];

// ── INSTALL ──────────────────────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('[KD SW v3] Pre-caching static assets');
        return cache.addAll(PRECACHE_STATIC);
      })
      .then(() => self.skipWaiting())
  );
});

// ── ACTIVATE: prune old caches ───────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => !ALL_CACHES.includes(k))
          .map(k => {
            console.log('[KD SW v3] Deleting old cache:', k);
            return caches.delete(k);
          })
      )
    ).then(() => self.clients.claim())
  );
});

// ── FETCH ────────────────────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Skip cross-origin (CDN fonts, Fuse.js)
  if (url.origin !== location.origin) return;

  const path = url.pathname;
  const isHTML = event.request.mode === 'navigate' || path.endsWith('.html') || path.endsWith('/');
  const isImage = /\.(png|jpg|jpeg|gif|webp)$/i.test(path);
  const isStatic = /\.(css|js|svg|woff2?|ttf)$/i.test(path);

  if (isHTML) {
    // HTML: network-first, cache fallback
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const clone = response.clone();
          caches.open(STATIC_CACHE).then(cache => cache.put(event.request, clone));
          return response;
        })
        .catch(() => caches.match(event.request)
          .then(cached => cached || caches.match('/kiwi-dialectic-te-pa-minisite/index.html'))
        )
    );
    return;
  }

  if (isImage) {
    // Images: stale-while-revalidate
    event.respondWith(
      caches.open(IMAGE_CACHE).then(cache =>
        cache.match(event.request).then(cached => {
          const fetchPromise = fetch(event.request).then(response => {
            cache.put(event.request, response.clone());
            return response;
          });
          return cached || fetchPromise;
        })
      )
    );
    return;
  }

  if (isStatic) {
    // CSS/JS/SVG: cache-first
    event.respondWith(
      caches.match(event.request).then(cached => {
        if (cached) return cached;
        return fetch(event.request).then(response => {
          caches.open(STATIC_CACHE).then(cache => cache.put(event.request, response.clone()));
          return response;
        });
      })
    );
    return;
  }

  // Default: network with cache fallback
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
