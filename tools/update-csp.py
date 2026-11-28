#!/usr/bin/env python3
"""Recompute the Content-Security-Policy script hashes.

Covers index.html and tools/points-signer.html. Run after editing any
<script> in either file:
    python3 tools/update-csp.py
With --check it only verifies the hashes and exits non-zero if they are stale.
"""
import base64
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

PAGES = {
    ROOT / "index.html": (
        "default-src 'self'; "
        "script-src {hashes}; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "manifest-src 'self'; "
        "connect-src 'self'; "
        "worker-src 'self'; "
        "object-src 'none'; "
        "base-uri 'none'; "
        "form-action 'none'; "
        "upgrade-insecure-requests"
    ),
    # The owner's tool may not load or contact anything: no connect-src at all.
    ROOT / "tools" / "points-signer.html": (
        "default-src 'none'; "
        "script-src {hashes}; "
        "style-src 'unsafe-inline'; "
        "img-src data:; "
        "base-uri 'none'; "
        "form-action 'none'"
    ),
}

META = re.compile(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]*)(">)')
# Executable inline scripts only: plain <script> tags.
SCRIPT = re.compile(r"<script>(.*?)</script>", re.S)


def build(html: str, policy: str, name: str) -> str:
    hashes = []
    for body in SCRIPT.findall(html):
        digest = base64.b64encode(hashlib.sha256(body.encode("utf-8")).digest()).decode()
        hashes.append(f"'sha256-{digest}'")
    if not hashes:
        sys.exit(f"{name}: no inline scripts found")
    return policy.format(hashes=" ".join(hashes))


def main() -> None:
    check = "--check" in sys.argv
    stale = []
    for page, policy in PAGES.items():
        name = page.relative_to(ROOT)
        html = page.read_text(encoding="utf-8")
        match = META.search(html)
        if not match:
            sys.exit(f"{name}: CSP meta tag not found")
        new = build(html, policy, str(name))
        if match.group(2) == new:
            continue
        stale.append(str(name))
        if not check:
            page.write_text(META.sub(lambda m: m.group(1) + new + m.group(3), html, count=1), encoding="utf-8")
    if check:
        if stale:
            sys.exit("CSP hashes are out of date in: " + ", ".join(stale) + " (run python3 tools/update-csp.py)")
        print("CSP hashes are up to date")
    else:
        print("CSP updated: " + (", ".join(stale) if stale else "nothing to change"))


if __name__ == "__main__":
    main()
