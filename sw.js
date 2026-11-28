/* Service Worker لخلاصة الفكرة
   - الصفحة: من الشبكة أولاً (فتصل التحديثات فوراً)، ومن النسخة المحفوظة عند انقطاع الإنترنت.
   - الأيقونات والملفات الثابتة: من النسخة المحفوظة أولاً.
   غيّر VERSION عند تغيير الأيقونات أو قائمة CORE ليُحدَّث المحفوظ. */
const VERSION = 'kf-v1';
const CORE = [
  './',
  './manifest.webmanifest',
  './icons/favicon.svg',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(VERSION).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // نتعامل مع ملفات الموقع فقط، ونترك الخطوط الخارجية وأداة النقاط للمتصفح
  if (url.origin !== self.location.origin || url.pathname.includes('/tools/')) return;

  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then(res => {
          if (res.ok) { const copy = res.clone(); caches.open(VERSION).then(c => c.put('./', copy)); }
          return res;
        })
        .catch(() => caches.match('./'))
    );
    return;
  }

  event.respondWith(caches.match(req).then(hit => hit || fetch(req)));
});
