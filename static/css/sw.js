self.addEventListener('install', (e) => {
  console.log('[Service Worker] Instalado exitosamente en el dispositivo');
});

self.addEventListener('fetch', (e) => {
  // Se deja en blanco intencionalmente para la PWA básica
});