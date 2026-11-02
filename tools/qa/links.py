"""Internal links and anchors on every built page resolve (no 404s, no anchor that jumps to nothing).

Usage: .venv/Scripts/python -I tools/qa/links.py
Reads every index.html (and 404.html) of the site, resolves each internal href and src against the page,
and checks that the file exists (a folder means its index.html) and that a #fragment names an id on the
target page. Exit code 1 when anything is broken.
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
SKIP = ("review", ".venv", "tools", "src-assets", "node_modules", "notes", ".git")


def pages():
    for p in sorted(ROOT.rglob("index.html")):
        if not any(part in SKIP for part in p.relative_to(ROOT).parts):
            yield p
    yield ROOT / "404.html"


def ids(path, cache={}):
    if path not in cache:
        cache[path] = set(re.findall(r'\bid="([^"]+)"', path.read_text(encoding="utf-8")))
    return cache[path]


def target(page, url):
    parts = urlsplit(url)
    if parts.scheme or parts.netloc or url.startswith(("mailto:", "tel:", "data:", "javascript:")):
        return None, None
    base = page.parent
    if parts.path.startswith("/"):
        base, parts = ROOT, parts._replace(path=parts.path.lstrip("/"))
    path = (base / unquote(parts.path)).resolve() if parts.path else page
    if path.is_dir():
        path = path / "index.html"
    return path, parts.fragment


def main():
    broken, checked = [], 0
    for page in pages():
        html = re.sub(r"<!--.*?-->", "", page.read_text(encoding="utf-8"), flags=re.S)
        html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.S)
        urls = re.findall(r'\b(?:href|src)="([^"]+)"', html)
        urls += [u.strip().split(" ")[0] for s in re.findall(r'\bsrcset="([^"]+)"', html) for u in s.split(",")]
        rel = page.relative_to(ROOT).as_posix()
        for url in urls:
            if url in ("#", "") or url.startswith("#") and len(url) == 1:
                continue
            path, frag = target(page, url)
            if path is None:
                continue
            checked += 1
            if not path.exists():
                broken.append(f"{rel}: {url} (missing file)")
            elif frag and path.suffix == ".html" and frag not in ids(path):
                broken.append(f"{rel}: {url} (no #{frag} on the page)")
    print(f"{checked} internal links and files checked, {len(broken)} broken")
    for b in sorted(set(broken)):
        print("  " + b)
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
