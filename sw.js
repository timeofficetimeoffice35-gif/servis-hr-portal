const CACHE_NAME = 'servis-hr-v1';
const urlsToCache = [
  './',
  './index.html',
  './dashboard.html',
  './leave.html',
  './attendance.html',
  './manifest.json',
  './leave_data.json',
  './attendance_data.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  );
});
