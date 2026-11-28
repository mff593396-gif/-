---
name: preview-safe-pages
description: Make a static web page keep working inside in-app file previews and sandboxed iframes. Use when a user reports login or saved data "not sticking", forms doing nothing, or an animation dead until refresh, especially when they open the HTML file inside an app (chat app, file viewer) instead of a browser.
---

# Pages that survive in-app previews

In-app previews load the page in a sandboxed iframe: often no `allow-same-origin` (so `localStorage` throws), sometimes no `allow-forms` (so `submit` never fires), and the frame may start hidden or zero-sized before it is shown. Each breaks a different feature silently.

## Reproduce first

Build a Playwright harness that mirrors the preview, then confirm the symptom before fixing:

```js
await page.setContent(`<iframe id="f" sandbox="allow-scripts allow-popups" src="${URL}" style="width:0;height:0"></iframe>`);
await page.waitForTimeout(1500);
await page.evaluate(() => { const f = document.getElementById('f'); f.style.width = '100%'; f.style.height = '780px'; });
const frame = page.frames()[1];
```

Drop `allow-forms` to test blocked forms; keep the 0-size start to test late layout.

## Fixes

- **Storage:** wrap `localStorage` in a store that falls back to an in-memory map when it throws, so login and cart work while the page is open. Probe once at startup (`setItem`/`removeItem` in try) and show a plain notice ("this window can't save; open the link in Safari/Chrome") after login and on account pages. A toast saying "logged in" while nothing persisted is the bug's signature.
- **Forms:** handle the submit button's `click` (call `preventDefault()` and run the handler) in addition to `submit`. Pressing Enter performs implicit submission by clicking the default button, so it still works; the sandbox check happens after the click, inside submission.
- **Zero-size start:** never permanently disable a feature because a measurement returned zero. Return early when the container is under a few pixels, and re-run layout on `resize`, `load`, `pageshow`, `visibilitychange`, and a `ResizeObserver` on the container (debounced). Guard canvas work: a 0×0 canvas makes `getImageData` throw.

## Done when

The harness shows the feature working after the frame becomes visible, login survives navigation inside the frame with storage blocked, and Enter or click submits with forms blocked. Keep these as regression tests.
