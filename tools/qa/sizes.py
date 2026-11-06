"""Static check for layout shift: every <img>, <video> and <iframe> in the built pages needs width and height attributes,
or has to sit inside a box that sizes it (picture.fill and the known media boxes, checked live by sweep.py's CLS reading).
Usage: .venv/Scripts/python tools/qa/sizes.py
"""
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP = {"review", "notes", "tools", ".venv", "node_modules", ".git", "vendor"}
TAG = re.compile(r"<(img|video|iframe)\b[^>]*>", re.I)
FILL = re.compile(r'<picture[^>]*class="[^"]*\bfill\b[^"]*"[^>]*>(?:(?!</picture>).)*$', re.S)


def main():
    pages = [p for p in ROOT.rglob("*.html") if not SKIP & set(p.relative_to(ROOT).parts)]
    total, sized, filled, bad = Counter(), 0, 0, []
    for page in pages:
        html = page.read_text(encoding="utf-8")
        for m in TAG.finditer(html):
            tag, kind = m.group(0), m.group(1).lower()
            total[kind] += 1
            if re.search(r"\bwidth=", tag) and re.search(r"\bheight=", tag):
                sized += 1
            elif FILL.search(html[max(0, m.start() - 1500):m.start()]):
                filled += 1
            else:
                bad.append((str(page.relative_to(ROOT)), tag[:110]))
    print(f"{len(pages)} pages; {dict(total)}; {sized} with width and height, {filled} filling a sized box, {len(bad)} to look at")
    seen = Counter(t for _, t in bad)
    for tag, n in seen.most_common(30):
        print(f"  {n} x {tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
