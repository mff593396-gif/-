---
name: arabic-glyph-dot
description: Locate the exact position and size of an Arabic letter's dot (nuqta) in any font with a canvas diff, to animate or replace it. Use when a design detaches, moves, or restyles a letter's dot (e.g. the dot of خ, ف, ن) and it must line up with the real glyph.
---

# Measuring an Arabic letter's dot

Fonts place dots differently, so hard-coded offsets break when the web font loads late or a fallback is used. Measure from the font itself.

## Method

1. Read the target element's computed `font-size`, `font-weight`, `font-family`; bail out if size is 0.
2. On an offscreen canvas (`willReadFrequently: true`), set `direction = 'rtl'`, `textAlign = 'right'`, `textBaseline = 'alphabetic'`, and draw the dotted form and its dotless twin at the same origin: `خـ` vs `حـ`, `فـ` vs `ڡـ`, `نـ` vs `ٮـ`. The tatweel keeps the joining form identical to the one in the word.
3. Pixels opaque in the dotted drawing and clear in the dotless one are the dot. Their bounding box gives centre `(dx, dy)` relative to the start of the letter and the baseline, and width/height.
4. Place the animated dot from a marker element at the letter's start (a zero-width span) plus `(dx, dy)`.
5. Show the word with the dotless letter while the separate dot element is visible (`حلاصة` with the dot drawn on top), and swap back to the real text when the effect is disabled.

## Re-measure

After fonts finish loading and on resize. If the diff finds no pixels (canvas blocked or font missing the glyph), fall back to the plain text.
