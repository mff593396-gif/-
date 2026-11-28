---
name: scroll-intro-animation
description: Scroll-driven sticky intro animations that stay smooth on phones. Use when building a hero where scrolling drives a sequence (drop, reveal, grow into the next section), or when such an intro is janky, blurry, or heavy on mobile.
---

# Scroll-driven sticky intro

A tall root (`height: 240–280svh`) holds a `position: sticky; top: 0; height: 100svh` stage. Scroll position maps to progress `p ∈ [0,1]`, and each element reads its own phase from `p`.

## Structure

- Measure once in `layout()`: `rootTop = root.getBoundingClientRect().top + scrollY`, `dist = root.offsetHeight - stage.offsetHeight`, sticky `top`, plus element geometry. Per frame compute `p = clamp((scrollY + stickyTop - rootTop) / dist)` with no layout reads.
- Phases: `seg(p, a, b) = clamp((p - a) / (b - a))` with easing; overlap phases slightly so the motion reads as one gesture.
- Drive frames from a passive `scroll` listener that schedules one `requestAnimationFrame`; skip the frame when `p` is unchanged.
- Re-run `layout()` on resize, font load (`document.fonts.ready`, `loadingdone`), and a `ResizeObserver` on the stage. Return early when the stage has no size yet (see `preview-safe-pages`); never disable the effect for good on a failed measurement.
- Growing a circle to fill the screen: size the element at its final diameter and animate `scale` from small to 1, so it stays sharp.

## Mobile performance

- Animate only `transform` and `opacity`. A highlight that grows uses `scaleX`, not `width`.
- No `backdrop-filter` on mobile (the costliest effect while scrolling); use a solid translucent background.
- Fewer layered `text-shadow`s on mobile for extruded 3D text.
- No permanent `will-change` on large or text layers: it rasterises them and they blur when scaled.
- Pointer tilt only when `(hover: hover) and (pointer: fine)`.
- `content-visibility: auto` with `contain-intrinsic-size` on sections below the fold.

## Accessibility

Under `prefers-reduced-motion: reduce`, drop the tall root and show the final state in normal flow (content readable, nothing hidden behind scroll).

## Verify

With Playwright, scroll to fixed fractions of `dist` and assert element styles change (transform, opacity) at each phase; take frame screenshots at desktop and phone sizes.
