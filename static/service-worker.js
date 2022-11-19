self.ver = '1.8';

self.addEventListener('install', function (e) {
    console.log('Installing version ' + self.ver);
    e.waitUntil(
        caches.open('pwa').then(function (cache) {
            var assets = [
                '/',
                '?source=pwa',
                '/manifest.webmanifest',
                '/ico-192.png',
                '/ico-512.png',
                '/main.js',
                '/favicon.ico',
                '/index.html',
            ];
            return Promise.all(assets.map(function (asset) {
                return fetch(asset + '?t=' + Date.now()).then(function (response) {
                    if (response.ok) {
                        return cache.put(asset, response);
                    }
                });
            }), cache.keys().then(function (cacheNames) {
                return Promise.all(cacheNames.filter(function (cacheName) {
                    return !assets.includes(new URL(cacheName.url).pathname);
                }).map(function (cacheName) {
                    return caches.delete(cacheName);
                }));
            }));
        })
    );
});

self.addEventListener('fetch', function (event) {
    if (event.request.url.match(/google/)) {
        event.respondWith(fetch(event.request));
    } else if (event.request.url.match(/\/version.txt/)) {
        event.respondWith(new Response(self.ver, { headers: { 'Content-Type': 'plain/text' } }));
    } else {
        event.respondWith(
            caches.match(event.request).then(function (response) {
                return response || fetch(event.request);
            })
        );
    }
});

self.addEventListener('message', function (event) {
    if (event.data === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

self.addEventListener('activate', function (event) {
    console.log('Installed version ' + self.ver);
});