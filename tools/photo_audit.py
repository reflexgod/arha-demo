"""Photo repeats (v4 feedback 5): a photograph appears at most once per page and on at most two pages.

Usage: .venv/Scripts/python -I tools/photo_audit.py [--list]
Counts every <img> photograph on every built page (assets/img and video posters). Files that are the
same photograph count as one (tools/photo_ids.py). /gallery/ is the clinic's photo album, the one page
meant to show every photograph of Arha's rooms, so it is not counted. --list prints every photo's pages.
Exit code 1 when a rule is broken.
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import photo_ids  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SKIP = ("gallery", "before-after")  # the photo album; a redirect
# The one exception, by design (v4 feedback 3): a sample case's own before/after pair is on the homepage,
# on Our work and on its own case page, because the homepage pairs link to the case pages Our work lists.
CASE_PAGES = 3


def pages():
    for p in sorted(ROOT.rglob("index.html")):
        rel = p.parent.relative_to(ROOT).as_posix()
        if rel.split("/")[0] in ("review", ".venv", "tools", "src-assets", "node_modules") or rel in SKIP:
            continue
        yield (rel if rel != "." else "home"), p
    yield "404", ROOT / "404.html"


def photos(html):
    """Canonical photographs on a page. The two sides of one before/after pair (stock-pair-<n>-*,
    stock-sim-whiten-*) are one appearance: a simulated pair is one photograph by design."""
    names = re.findall(r'<img\b[^>]*?\ssrc="[^"]*?assets/(?:img|video)/([a-z0-9-]+?)-\d+\.(?:jpg|webp|avif)"', html)
    canon = photo_ids.groups()
    out, seen_pairs = [], set()
    for n in names:
        pair = re.match(r"(stock-pair-\d+|stock-sim-whiten)-(?:before|after)$", n)
        if pair:
            if pair.group(1) in seen_pairs:
                continue
            seen_pairs.add(pair.group(1))
        out.append(canon.get(n, n))
    return out


def audit():
    site = defaultdict(set)
    problems = []
    for rel, path in pages():
        counts = Counter(photos(path.read_text(encoding="utf-8")))
        for name, k in counts.items():
            site[name].add(rel)
            if k > 1:
                problems.append(f"{rel}: {name} appears {k} times")
    cases = {photo_ids.groups().get(f"stock-pair-{n}-after") for n in range(1, 10)}
    for name, where in sorted(site.items()):
        if len(where) > (CASE_PAGES if name in cases and all(w in ("home", "our-work") or w.startswith("our-work/") for w in where) else 2):
            problems.append(f"{name} on {len(where)} pages: {', '.join(sorted(where))}")
    return site, problems


if __name__ == "__main__":
    site, problems = audit()
    if "--list" in sys.argv:
        for name, where in sorted(site.items(), key=lambda kv: -len(kv[1])):
            print(f"{len(where)}  {name}: {', '.join(sorted(where))}")
    print("\n".join(problems) or "No repeats: every photograph is on one page once, and on at most two pages.")
    print(f"{len(problems)} problems, {len(site)} photographs")
    sys.exit(1 if problems else 0)
