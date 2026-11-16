// Offline cache for SATB Part Player. Bump VERSION on every release.
const VERSION = 'satb-v1';
const ASSETS = [
  './', 'index.html', 'manifest.webmanifest',
  'vendor/opensheetmusicdisplay.min.js', 'vendor/jszip.min.js',
  'scores/sicut-cervus.xml', 'scores/hymne-a-la-nuit.xml',
  'fonts/young-serif-latin-400-normal.woff2',
  'fonts/figtree-latin-400-normal.woff2', 'fonts/figtree-latin-500-normal.woff2',
  'fonts/figtree-latin-600-normal.woff2', 'fonts/figtree-latin-700-normal.woff2',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/icon-maskable-512.png', 'icons/apple-touch-icon.png'
];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
// Serve from the cache straight away, refresh it in the background when online.
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  e.respondWith(caches.open(VERSION).then(async cache => {
    const hit = await cache.match(req, { ignoreSearch: true });
    const fresh = fetch(req).then(res => { if (res.ok) cache.put(req, res.clone()); return res; }).catch(() => null);
    if (hit) { e.waitUntil(fresh); return hit; }
    return (await fresh) || (req.mode === 'navigate' ? cache.match('index.html') : Response.error());
  }));
});
