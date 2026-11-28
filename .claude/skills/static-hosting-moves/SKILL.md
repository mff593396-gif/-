---
name: static-hosting-moves
description: Publish and move static sites between GitHub Pages and Netlify without breaking links or user data. Use when a deployed site still shows an old version, when choosing or switching hosts, or when changing a site's URL.
---

# Static hosting: GitHub Pages and Netlify

## Find out how the site is published before changing anything

- GitHub Pages "Deploy from a branch" shows up in Actions as runs named `pages build and deployment` on that branch. In that mode a custom deploy workflow using `actions/deploy-pages` fails, so do not add one; the branch content is the site.
- "Old version on the live link" almost always means the work is on a side branch and the published branch was never merged. Check `git log origin/main` and the latest Pages run's `head_sha`.
- Branch mode runs Jekyll: dot-folders (`.claude/`) are skipped, HTML without front matter is copied as-is.

## Netlify

- `netlify.toml` at the repo root: `[build] publish = "."` (no build step for a plain site), `[[headers]]` for security headers (`nosniff`, `Referrer-Policy`, `Permissions-Policy`, HSTS; `X-Robots-Tag`/`X-Frame-Options` on private tool pages; `Cache-Control: no-cache` on `sw.js`), `[[redirects]]` with `status = 404, force = true` to hide dev files.
- The owner imports the repo in the Netlify UI (Add new project → Import from GitHub); after that every merge to `main` deploys automatically.

## Moving to a new URL

- **User data is per origin.** `localStorage` on `user.github.io` is invisible on `name.netlify.app`: customers lose logins, carts and local balances. Move before real users arrive, and pick one official URL for good.
- Redirect the old host from the page itself, first thing in `<head>`: `if (location.hostname === 'old.host') location.replace('https://new.host/' + location.hash)`. Keeping `location.hash` preserves deep links and hash-carried tokens. Add `<link rel="canonical">`.
- Pages that store their own data (an owner tool) should stay on their original origin, or be migrated by exporting and importing a backup.
- Update every place that builds absolute links (owner tools, Open Graph tags, README), and auto-upgrade a saved old URL in tools so the owner does not have to.

## Verify

Playwright can serve both hosts locally with `context.route('https://old.host/**', ...)` and `context.route('https://new.host/**', ...)` fulfilling the local file, then assert the redirect lands on the new host with the hash intact.
