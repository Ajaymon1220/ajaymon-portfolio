// Full document navigation keeps the captured static pages and their interactions in sync.
// Consume a short-lived, destination-specific marker before the first paint.
(() => {
 const key = 'ajay:page-switch';
 let pending;
 try {
  pending = JSON.parse(sessionStorage.getItem(key) || 'null');
  sessionStorage.removeItem(key);
 } catch {}
 const type = performance.getEntriesByType('navigation')[0]?.type;
 const destination = location.pathname + location.search;
 const internalSwitch = pending && pending.destination === destination && Date.now() - pending.at < 15000;
 const skip = type !== 'reload' && (type === 'back_forward' || internalSwitch);
 window.__ajaySkipIntro = Boolean(skip);
 if (skip) {
  document.documentElement.dataset.skipIntro = 'true';
  document.documentElement.dataset.revealed = 'true';
 }
 document.addEventListener('click', function (event) {
  const link = event.target.closest?.('a[href]');
  if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || (link.target && link.target !== '_self') || link.download || link.hasAttribute('download')) return;
  const url = new URL(link.href, location.href);
  if (url.origin === location.origin && url.pathname !== location.pathname) {
   event.preventDefault();
   event.stopImmediatePropagation();
   try { sessionStorage.setItem(key, JSON.stringify({destination:url.pathname + url.search, at:Date.now()})); } catch {}
   location.assign(url.href);
  }
 }, true);
})();
