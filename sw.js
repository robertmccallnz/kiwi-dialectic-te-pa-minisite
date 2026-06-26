/* ──────────────────────────────────────────────────────────────────────────
   Te Pā Tūwatawata — Service Worker (PWA)
   Caches all course modules, motifs, assets, and PDFs for offline use.
   Strategy: Cache-first with network fallback.
   Ko te mātauranga he taonga nō te katoa — offline too.
────────────────────────────────────────────────────────────────────────── */

const CACHE_NAME = 'kd-te-pa-v1';

const PRECACHE_URLS = [
  '/kiwi-dialectic-te-pa-minisite/',
  '/kiwi-dialectic-te-pa-minisite/index.html',
  '/kiwi-dialectic-te-pa-minisite/rhizome-mapper.html',
  '/kiwi-dialectic-te-pa-minisite/assets/kiwi-dialectic.css',
  '/kiwi-dialectic-te-pa-minisite/assets/search.js',
  '/kiwi-dialectic-te-pa-minisite/assets/rhizome-d3.js',
  // Modules
  '/kiwi-dialectic-te-pa-minisite/modules/module-1.html',
  '/kiwi-dialectic-te-pa-minisite/modules/module-2.html',
  '/kiwi-dialectic-te-pa-minisite/modules/module-3.html',
  '/kiwi-dialectic-te-pa-minisite/modules/module-4.html',
  '/kiwi-dialectic-te-pa-minisite/modules/module-5.html',
  '/kiwi-dialectic-te-pa-minisite/modules/module-6.html',
  '/kiwi-dialectic-te-pa-minisite/modules/rhizome.html',
  // Motifs
  '/kiwi-dialectic-te-pa-minisite/motifs/index.html',
  '/kiwi-dialectic-te-pa-minisite/motifs/koru.html',
  '/kiwi-dialectic-te-pa-minisite/motifs/kowhaiwhai.html',
  '/kiwi-dialectic-te-pa-minisite/motifs/niho-taniwha.html',
  '/kiwi-dialectic-te-pa-minisite/motifs/pa-tuwatawata.html',
  '/kiwi-dialectic-te-pa-minisite/motifs/takarangi.html',
  '/kiwi-dialectic-te-pa-minisite/motifs/unaunahi.html',
  // SVG motifs
  '/kiwi-dialectic-te-pa-minisite/assets/motifs/koru-dark-square.svg',
  '/kiwi-dialectic-te-pa-minisite/assets/motifs/koru-light-square.svg',
  '/kiwi-dialectic-te-pa-minisite/assets/motifs/pa-tuwatawata-dark-square.svg',
  '/kiwi-dialectic-te-pa-minisite/assets/motifs/niho-taniwha-dark-square.svg',
  '/kiwi-dialectic-te-pa-minisite/assets/motifs/kowhaiwhai-dark-square.svg',
  '/kiwi-dialectic-te-pa-minisite/assets/motifs/unaunahi-dark-square.svg',
  '/kiwi-dialectic-te-pa-minisite/assets/motifs/takarangi-dark-square.svg',
  // Social/brand
  '/kiwi-dialectic-te-pa-minisite/assets/social/kiwi-dialectic-x-card.png',
  // Manifest
  '/kiwi-dialectic-te-pa-minisite/manifest.json',
];

// ── INSTALL: pre-cache core assets ──────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[KD SW] Pre-caching core assets');
      return cache.addAll(PRECACHE_URLS);
    }).then(() => self.skipWaiting())
  );
});

// ── ACTIVATE: remove old caches ──────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// ── FETCH: cache-first strategy ──────────────────────────────────────────
self.addEventListener('fetch', event => {
  // Skip non-GET and cross-origin requests (CDN scripts etc.)
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.origin !== location.origin) return;

  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        // Cache successful responses for same-origin pages/assets
        if (response && response.status === 200 && response.type === 'basic') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => {
        // Offline fallback for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('/kiwi-dialectic-te-pa-minisite/index.html');
        }
      });
    })
  );
});
