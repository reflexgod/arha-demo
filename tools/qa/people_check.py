"""Check the stock-people rules on the built pages (7 Nov 2026).

Usage: .venv/Scripts/python -I tools/qa/people_check.py

Per page (home, both indexes, every treatment and problem page):
  - no photograph appears in two places (a finder card and its answer panel, or an index row and its hover preview,
    are one appearance of the same photograph and count once);
  - on treatment and problem pages, no clinic or old object stock remains: every photograph is from assets/stock/
    (except people_slots.KEEP, three interactives that need their own photograph);
  - on the homepage, Arha's own photographs only in the hero, "A clinic built around calm", "Step inside", and the
    "Technology & innovation" and "Dr. Nikhil's clinic" cards;
  - only the page's first (hero) photograph is eager; everything else has loading="lazy"; every <img> has width/height.
Exits 1 on any problem.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import people_slots  # noqa: E402

PAIRED = ("finder", "tx", "xindex", "problem-rows")  # sections where one photograph shows twice by design
HOME_REAL = {"ah-trio": {"arha-dental-care-xray-room", "arha-dental-care-sign-board-wide"},
             "ah-band": None, "inside-v9": None}  # None: any of Arha's own photographs


def images(html):
    main = re.search(r"<main.*?</main>", html, re.S).group(0)
    out = []
    for m in re.finditer(r'<img [^>]*>', main):
        tag = m.group(0)
        src = re.search(r'src="(?:\.\./)*assets/(img|stock|video)/([\w-]+?)-\d+\.(?:jpg|webp)"', tag)
        if not src:
            continue
        secs = re.findall(r'<section[^>]*class="([^"]*)"', main[:m.start()])
        out.append((src.group(1), src.group(2), secs[-1] if secs else "", tag))
    return out


def check(rel, problems):
    path = ROOT / rel
    html = path.read_text(encoding="utf-8")
    imgs = images(html)
    seen = {}
    for folder, name, sec, tag in imgs:
        key = sec.split()[0] if any(p in sec for p in PAIRED) else f"{sec}#{len(seen)}"
        seen.setdefault(name, set()).add(key)
        if "width=" not in tag or "height=" not in tag:
            problems.append(f"{rel}: {name} has no width/height")
    for name, places in seen.items():
        if len(places) > 1:
            problems.append(f"{rel}: {name} appears {len(places)} times")
    for n, (folder, name, sec, tag) in enumerate(imgs):
        eager = 'loading="lazy"' not in tag
        if rel != "index.html" and n == 0 and not eager:
            problems.append(f"{rel}: the hero ({name}) is lazy")
        if n > 0 and eager and folder != "video":
            problems.append(f"{rel}: {name} is not lazy")
        if rel == "index.html":
            if folder == "img":
                allowed = next((v for k, v in HOME_REAL.items() if k in sec.split()), False)
                if allowed is False or (allowed is not None and name not in allowed):
                    problems.append(f"home: Arha/old photograph {name} in {sec}")
        elif folder != "stock" and name not in people_slots.KEEP.get(rel.rsplit("/index.html", 1)[0], set()):
            problems.append(f"{rel}: non-stock photograph {name} in {sec or 'hero'}")
    return [(name, len(p)) for name, p in seen.items()]


def main():
    pages = ["index.html", "treatments/index.html", "problems/index.html"]
    pages += [f"{s}/index.html" for s in people_slots.TREATMENT_HERO] + [f"problems/{s}/index.html" for s in people_slots.PROBLEM_HERO]
    problems, report = [], []
    for rel in pages:
        used = check(rel, problems)
        report.append(f"{rel}: {len(used)} photographs")
    print("\n".join(report))
    print("\n".join(problems) or "people_check: 0 problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
