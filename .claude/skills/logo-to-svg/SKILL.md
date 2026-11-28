---
name: logo-to-svg
description: Rebuild a flat logo from a raster image (JPG/PNG) as a precise inline SVG and export icon PNGs from it. Use when a user supplies a logo image to put on a site, as a favicon or app icon, or needs it crisp in dark mode.
---

# Logo image to SVG

A raster logo blurs when scaled and brings its background into dark mode. Flat logos (solid shapes, round strokes, simple curves) can be rebuilt exactly as SVG from measurements. Wordmarks in a font are better left as live text in the site's font, or kept as the original image (e.g. for link previews).

## Measure

With PIL on the original image:

1. Sample colours at points inside each shape and the background; report hex.
2. Bounding box per colour (threshold on the channel that separates it, e.g. gold `r>200 and b<80`, dark `sum(rgb)<200`).
3. Row and column scans through each shape: first/last dark pixel per line give stroke thickness, cap positions, and arc radii (outer minus inner = stroke width; midline radius = their mean).

## Build

- Express strokes as one path with `stroke-width` and `stroke-linecap="round"` (e.g. `M x1 y H x2 a r r 0 0 1 0 2r H x3`) rather than filled outlines; fewer numbers, exact rounded ends.
- Use the image's pixel coordinates directly as the `viewBox` (crop to the mark's bounding box plus a few pixels), so measurements need no conversion.
- Put the mark in a `<symbol>` and use `stroke="currentColor"` for the dark part so CSS can switch it for dark mode; fixed colours for accent parts.

## Check by overlay

Render the original crop and the SVG side by side, then the SVG at 50% opacity in contrasting colours on top of the original (Playwright `setContent`, original as a base64 background positioned at `-x -y`). Done when the overlay shows no visible offset at any edge.

## Export icons

Render square SVGs (background rect plus the mark scaled to ~60% height, ~50% for maskable) in a Playwright page whose viewport equals the target size with `deviceScaleFactor: 1`, and `screenshot` each: 32, 180, 192, 512, maskable 512. Verify sizes with PIL and view a contact sheet; preview pages cannot load `file://` images, so composite with PIL instead.
