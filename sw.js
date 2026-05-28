// BesaFlow service worker
// - App shell: network-first for index.html so updates ship, cache fallback for offline.
// - Audio clips: cache-on-demand. They never change once written, so cache-first is correct.
// - Bump CACHE_NAME to force users to refetch the shell on next visit.

const CACHE_NAME = 'besaflow-v2-2026-05-28';
const SHELL_ASSETS = [
  './',
  'index.html',
  'favicon.png',
  'og-image.png',
  'assets/eagle.png',
  'manifest.webmanifest',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/apple-touch-icon.png',
  // Streak songs — small enough to pre-cache, needed instantly on milestone.
  'audio/milestones/shotaAudio.mp3',
  'audio/milestones/gjovalinAudio.mp3',
  'audio/milestones/lekeAudio.mp3',
  'audio/milestones/nikolleAudio.mp3',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  // Only handle same-origin
  if (url.origin !== self.location.origin) return;

  const path = url.pathname;
  const isHTML = req.mode === 'navigate' || path === '/' || path.endsWith('.html');
  const isAudio = path.startsWith('/audio/') || path.endsWith('.mp3');

  if (isHTML) {
    // Network-first for HTML: get updates, fall back to cache if offline.
    event.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE_NAME).then((c) => c.put(req, copy));
        return res;
      }).catch(() => caches.match(req).then((r) => r || caches.match('index.html')))
    );
    return;
  }

  if (isAudio) {
    // Cache-first for audio (immutable content).
    event.respondWith(
      caches.match(req).then((cached) => cached || fetch(req).then((res) => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((c) => c.put(req, copy));
        }
        return res;
      }).catch(() => cached))
    );
    return;
  }

  // Everything else: cache-first.
  event.respondWith(
    caches.match(req).then((cached) => cached || fetch(req).then((res) => {
      if (res.ok) {
        const copy = res.clone();
        caches.open(CACHE_NAME).then((c) => c.put(req, copy));
      }
      return res;
    }))
  );
});
