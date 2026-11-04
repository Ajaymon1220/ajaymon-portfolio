// Static export navigation preserves all original page interactions.
document.addEventListener('click', function (event) {
 const link = event.target.closest?.('a[href]');
 if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || link.target === '_blank' || link.download) return;
 const url = new URL(link.href, location.href);
 if (url.origin === location.origin && url.pathname !== location.pathname) {
  event.preventDefault(); event.stopImmediatePropagation(); location.assign(url.href);
 }
}, true);
