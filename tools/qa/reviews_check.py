"""The Google reviews on the site are exactly what they were at a git ref: the same quotes, names, tags and stars
on the homepage and on Our work. The built pages are committed, so the ref's pages are read with git show.

Usage: .venv/Scripts/python -I tools/qa/reviews_check.py [git-ref]    (default ref: HEAD)
Exit code 1 on any difference.
"""
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = ("index.html", "our-work/index.html")


def parts(text):
    quotes = [html.unescape(re.sub(r"<[^>]+>", "", q)).strip()
              for q in re.findall(r"<blockquote[^>]*>(.*?)</blockquote>", text, flags=re.S)]
    names = re.findall(r'class="[^"]*(?:__name|__who)[^"]*">(.*?)</', text)
    tags = re.findall(r'class="[^"]*__tag[^"]*">(.*?)</', text)
    return {"quotes": sorted(quotes), "names": sorted(names), "tags": sorted(tags),
            "stars": len(re.findall(r"__stars", text))}


def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    problems = []
    for page in PAGES:
        before = subprocess.run(["git", "show", f"{ref}:{page}"], cwd=ROOT, capture_output=True,
                                text=True, encoding="utf-8").stdout
        a, b = parts(before), parts((ROOT / page).read_text(encoding="utf-8"))
        for key in a:
            if a[key] != b[key]:
                problems.append(f"{page}: {key} differ from {ref}")
                if key != "stars":
                    for v in sorted(set(a[key]) ^ set(b[key])):
                        problems.append(f"    {'was' if v in a[key] else 'now'}: {v[:80]}")
        print(f"{page}: {len(b['quotes'])} quotes, {len(b['names'])} names, {len(b['tags'])} tags")
    print(f"reviews: {len(problems)} problems (compared with {ref})")
    for p in problems:
        print("  " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
