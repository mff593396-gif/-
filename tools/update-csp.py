#!/usr/bin/env python3
"""Recompute the Content-Security-Policy script hashes in index.html.

Run after editing any <script> in index.html:
    python3 tools/update-csp.py
With --check it only verifies the hashes (used by the deploy workflow).
"""
import base64
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"

POLICY = (
    "default-src 'self'; "
    "script-src {hashes}; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src https://fonts.gstatic.com; "
    "img-src 'self' data: blob:; "
    "manifest-src 'self' blob:; "
    "connect-src 'self'; "
    "worker-src 'self'; "
    "object-src 'none'; "
    "base-uri 'none'; "
    "form-action 'none'; "
    "upgrade-insecure-requests"
)

META = re.compile(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]*)(">)')
# Executable inline scripts only: plain <script> tags (the type="text/plain" block is data).
SCRIPT = re.compile(r"<script>(.*?)</script>", re.S)


def build(html: str) -> str:
    hashes = []
    for body in SCRIPT.findall(html):
        digest = base64.b64encode(hashlib.sha256(body.encode("utf-8")).digest()).decode()
        hashes.append(f"'sha256-{digest}'")
    if not hashes:
        sys.exit("no inline scripts found")
    return POLICY.format(hashes=" ".join(hashes))


def main() -> None:
    html = PAGE.read_text(encoding="utf-8")
    match = META.search(html)
    if not match:
        sys.exit("CSP meta tag not found in index.html")
    policy = build(html)
    if "--check" in sys.argv:
        if match.group(2) != policy:
            sys.exit("CSP hashes are out of date: run python3 tools/update-csp.py")
        print("CSP hashes are up to date")
        return
    PAGE.write_text(META.sub(lambda m: m.group(1) + policy + m.group(3), html, count=1), encoding="utf-8")
    print("CSP updated")


if __name__ == "__main__":
    main()
