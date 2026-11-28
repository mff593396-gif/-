---
name: static-pwa
description: Make a static site an installable PWA with real manifest, icons, service worker and an install button. Use when asked to make a site installable, add it to the home screen, give it an app icon, or work offline.
---

# Installable static site (PWA)

## Files

- `manifest.webmanifest` (real file; blob/data manifests are unreliable for install): `id`, `name`, `short_name`, `lang`/`dir`, relative `start_url` and `scope` (`./`), `display: standalone`, `background_color`, `theme_color`, icons 192 and 512 with `purpose: any`, plus a separate 512 `purpose: maskable` with the mark inside the central ~80% circle. Optional `shortcuts` to hash routes.
- `<head>`: `<link rel="manifest">`, SVG favicon (it may carry its own `@media (prefers-color-scheme: dark)`), a 32px PNG favicon, `apple-touch-icon` 180px (iOS ignores the manifest icons), `apple-mobile-web-app-capable`, and `apple-mobile-web-app-status-bar-style: default` on light sites (`black-translucent` puts white text on a white page).
- `sw.js` at the site root: network-first for navigations with the cached page as offline fallback (updates show immediately), cache-first for icons, ignore other origins and private tool paths. Bump the cache `VERSION` when cached files change. Serve it with `Cache-Control: no-cache`.
- CSP needs `manifest-src 'self'` and `worker-src 'self'`.

## Registration and install button

- Register only when `isSecureContext` and the protocol is http(s), after `load`.
- `beforeinstallprompt`: `preventDefault()`, keep the event, show the install button; on click call `prompt()` and await `userChoice`. Hide on `appinstalled` and when `display-mode: standalone` or `navigator.standalone`.
- iPhone/iPad never fire `beforeinstallprompt`: show the button anyway (detect iOS, including iPadOS reporting `MacIntel` with touch points) and open a dialog with the Share → Add to Home Screen steps.

## Icons from a logo

Render PNG icons from the SVG mark with Playwright screenshots at exact viewport sizes (see `logo-to-svg`); keep the background the logo's own colour.

## Verify

- Chrome's own check: `cdp.send('Page.getAppManifest')` (no `errors`) and `cdp.send('Page.getInstallabilityErrors')` (empty) on `http://localhost`.
- `navigator.serviceWorker.ready` has an active worker; with `context.setOffline(true)` a reload still renders the page.
- Existing tests that rely on `page.route` interception need `serviceWorkers: 'block'` in their context, because routes do not see requests answered by a service worker.
