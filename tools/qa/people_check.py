"""Check the stock photo rules on the built pages (7 Nov 2026; round 2 "rebalance" the same day).

Usage: .venv/Scripts/python -I tools/qa/people_check.py

Per page (home, both indexes, every treatment and problem page, book):
  - no photograph appears in two places (a finder card and its answer panel, or an index row and its hover preview,
    are one appearance of the same photograph and count once);
  - on treatment and problem pages, no clinic or old object stock remains: every photograph is from assets/stock/
    (except people_slots.KEEP, three interactives that need their own photograph);
  - on the homepage, Arha's own photographs only in the hero, "A clinic built around calm", "Step inside", and the
    "Technology & innovation" and "Dr. Nikhil's clinic" cards;
  - only the page's first (hero) photograph is eager; everything else has loading="lazy"; every <img> has width/height.
Site-wide (every built page):
  - faces only in four places (people_slots.FACES): each face photograph only on its own page and in its own place;
  - the only older assets/img/stock-* photographs left are KEEP and OBJECTS_OK (checked by eye: no faces).
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
# Older object photographs still used on the clinic pages (dental tourism, technology, the practice): no people in them.
OBJECTS_OK = {"stock-arrival", "stock-marine-drive", "stock-endo-files", "stock-handpieces-dark", "stock-instrument-tray"}


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
        if rel not in ("index.html", "book/index.html") and n == 0 and not eager:
            problems.append(f"{rel}: the hero ({name}) is lazy")
        if n > 0 and eager and folder != "video" and rel != "book/index.html":  # book: two option cards, both above the fold
            problems.append(f"{rel}: {name} is not lazy")
        if rel == "index.html":
            if folder == "img":
                allowed = next((v for k, v in HOME_REAL.items() if k in sec.split()), False)
                if allowed is False or (allowed is not None and name not in allowed):
                    problems.append(f"home: Arha/old photograph {name} in {sec}")
        elif rel != "book/index.html" and folder != "stock" and name not in people_slots.KEEP.get(rel.rsplit("/index.html", 1)[0], set()):
            problems.append(f"{rel}: non-stock photograph {name} in {sec or 'hero'}")
    return [(name, len(p)) for name, p in seen.items()]


def faces(problems):
    """Site-wide: where each face photograph appears; no other people photographs anywhere."""
    keep = set().union(*people_slots.KEEP.values())
    places = []
    for page in sorted(ROOT.glob("**/index.html")):
        if any(p in page.parts for p in ("src-assets", "review", "notes", ".venv", "node_modules")):
            continue
        rel = page.relative_to(ROOT).as_posix()
        for n, (folder, name, sec, tag) in enumerate(images(page.read_text(encoding="utf-8"))):
            if folder == "img" and name.startswith("stock-") and name not in keep | OBJECTS_OK:
                problems.append(f"{rel}: older stock photograph {name} (may show people)")
            if folder == "stock" and name in people_slots.FACES:
                where, place = people_slots.FACES[name]
                ok = rel == where and ((place == "hero" and n == 0) or place in sec.split())
                places.append(f"{name} on {rel} ({'hero' if n == 0 else sec.split()[0]})")
                if not ok:
                    problems.append(f"{rel}: face photograph {name} outside its place ({where}, {place})")
    return places


def main():
    pages = ["index.html", "treatments/index.html", "problems/index.html", "book/index.html"]
    pages += [f"{s}/index.html" for s in people_slots.TREATMENT_HERO] + [f"problems/{s}/index.html" for s in people_slots.PROBLEM_HERO]
    problems, report = [], []
    for rel in pages:
        used = check(rel, problems)
        report.append(f"{rel}: {len(used)} photographs")
    print("\n".join(report))
    print("faces:\n  " + "\n  ".join(faces(problems)))
    print("\n".join(problems) or "people_check: 0 problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
