---
name: csp-inline-hashes
description: Hash-based Content-Security-Policy for static pages with inline <script> blocks. Use when adding or tightening a CSP on a single-file or static site, when an inline script is blocked by CSP after an edit, or when site config must stay editable without breaking the policy.
---

# CSP with inline-script hashes

A static page with inline scripts gets a strict policy by listing each script's SHA-256 instead of `'unsafe-inline'`. Any edit to a script changes its hash, so the hash list is generated, never hand-written.

## Steps

1. Put the policy in `<meta http-equiv="Content-Security-Policy" content="...">` in `<head>` (works on any static host, including GitHub Pages, which cannot set headers).
2. Write a small generator script kept in the repo (this project: `tools/update-csp.py`) that, per page:
   - finds executable inline scripts with `<script>(.*?)</script>` (plain tags only; `type="text/plain"` or JSON data blocks are not executed and must be excluded),
   - hashes the exact body bytes (UTF-8, whitespace included) with SHA-256, base64,
   - rewrites the meta tag from a per-page policy template with `{hashes}`,
   - supports `--check` that exits non-zero when stale.
3. Run the generator after every script edit, and `--check` before committing. Done when `--check` passes for every page.
4. Verify in a real browser: load the page with Playwright and collect `console` errors; a CSP block shows as `Refused to execute inline script`. Done when no CSP errors appear.

## Policy shape

- Site: `default-src 'self'; script-src <hashes>; style-src 'self' 'unsafe-inline' <font css host>; font-src <font host>; img-src 'self' data:; manifest-src 'self'; connect-src 'self'; worker-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; upgrade-insecure-requests`.
- Owner/admin tool page: `default-src 'none'` plus script hashes and `style-src 'unsafe-inline'`, with **no `connect-src`**, so even injected code cannot send data anywhere.
- `frame-ancestors` is ignored in a meta tag; send it as a header (e.g. `netlify.toml`) if needed.

## Keep config out of scripts

Values a non-developer will edit (public keys, phone numbers, feature flags) belong in a `<meta name="...">` tag read by the script (`document.querySelector('meta[name=x]').content`), not inside the `<script>`. Editing a meta tag leaves every hash valid, so an edit from the GitHub web editor cannot silently disable the site.

## Gotchas

- Event-handler attributes (`onclick=`) and `javascript:` URLs are blocked by a hash policy; bind events in script.
- Inline `style=""` attributes need `'unsafe-inline'` in `style-src`; that is acceptable, scripts are what matters.
- A host that rewrites HTML (minifiers, injected analytics) changes the bytes and breaks hashes; publish the file untouched.
