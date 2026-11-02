// Omogućava da aplikacija radi i bez interneta i da se brzo otvara.
// Kad mijenjaš aplikaciju, povećaj broj verzije ispod.
const V = 'frizer-rakic-v8';
const SHELL = ['./', './index.html', './firebase-config.js', './manifest.webmanifest',
  './img/logo.webp', './img/logo-light.webp', './img/avatar.jpg', './img/icon-192.png', './img/icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(V).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== V).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

function put(req, res) {
  if (res && (res.ok || res.type === 'opaque')) {
    const copy = res.clone();
    caches.open(V).then(c => c.put(req, copy));
  }
  return res;
}
const networkFirst = req => fetch(req).then(res => put(req, res)).catch(() => caches.match(req).then(m => m || caches.match('./index.html')));
const cacheFirst = req => caches.match(req).then(m => m || fetch(req).then(res => put(req, res)));

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === location.origin) {
    // slike: iz memorije; sve ostalo (stranica, podešavanja, vijesti, igre): prvo s interneta
    e.respondWith(url.pathname.includes('/img/') ? cacheFirst(req) : networkFirst(req));
    return;
  }
  // Firebase biblioteke i fontovi se ne mijenjaju, pa se čuvaju za rad bez interneta.
  if (url.hostname === 'www.gstatic.com' || url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(cacheFirst(req));
  }
  // Pozivi prema Firebase bazi i prijavi idu direktno (Firebase ima svoju memoriju za rad bez interneta).
});
