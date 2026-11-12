"""List every [[TBC]] still on the built site, page by page, into notes/TO-CONFIRM.md (between generated markers).

Usage: .venv/Scripts/python -I tools/tbc_list.py   (run after tools/build.py)

Public pages hide these tags (visitors see the neutral fallback, or nothing); open any page with ?review=1, or build
with ARHA_REVIEW=1, to see them in place.
"""
import html
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
NOTES = ROOT / "notes" / "TO-CONFIRM.md"
START, END = "<!-- tbc-list:start -->", "<!-- tbc-list:end -->"
RAW = re.compile(r"\[\[TBC:?\s*([^\]]*)\]\]")


def page_url(f):
    rel = f.relative_to(DIST).as_posix()
    return "/" + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    pages, total = {}, 0
    for f in sorted(DIST.rglob("*.html")):
        h = f.read_text(encoding="utf-8")
        found = []
        for m in RAW.finditer(h):  # marks in the HTML and raw markers in embedded JSON (planner data)
            note, _, fb = html.unescape(m.group(1)).replace('\\"', '"').partition("||")
            item = note.strip() or "(unspecified)"
            if fb.strip():
                item += f' (visitors see: "{fb.strip()}")'
            if item not in found:
                found.append(item)
        if found:
            pages[page_url(f)] = found
            total += len(found)
    # Items from shared blocks (visit block, footer, ...) appear on many pages: list them once.
    count = {}
    for items in pages.values():
        for i in items:
            count[i] = count.get(i, 0) + 1
    shared = [i for i, n in count.items() if n >= 5]
    pages = {u: [i for i in items if i not in shared] for u, items in pages.items()}
    pages = {u: items for u, items in pages.items() if items}
    total = len(shared) + sum(len(v) for v in pages.values())
    lines = [START, f"## Every [[TBC]] on the site (generated {date.today():%d %b %Y} by tools/tbc_list.py: {total} distinct items)",
             "Hidden on public pages; open a page with ?review=1 to see them in place.", "", "### Shared blocks (on 5+ pages)"]
    lines += [f"- [ ] {i} ({count[i]} pages)" for i in shared] + [""]
    for url, items in pages.items():
        lines.append(f"### {url}")
        lines += [f"- [ ] {i}" for i in items]
        lines.append("")
    lines.append(END)
    block = "\n".join(lines)
    text = NOTES.read_text(encoding="utf-8") if NOTES.exists() else "# To confirm\n"
    if START in text and END in text:
        text = text[:text.index(START)] + block + text[text.index(END) + len(END):]
    else:
        text = text.rstrip("\n") + "\n\n" + block + "\n"
    NOTES.write_text(text, encoding="utf-8")
    print(f"{total} distinct TBC items ({len(shared)} shared) -> {NOTES.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
