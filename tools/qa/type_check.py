"""Typography audit (v5-fonts, 7 Nov 2026): on every built page, the computed type of each H1/H2/H3, body paragraph,
nav link and button, grouped by style. Prints the groups that break the font brief.

Run (server on 8080):  .venv/Scripts/python -I tools/qa/type_check.py [--all]
"""
import sys
from collections import Counter
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from pw import launch  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PAGES = sorted({"" if p.parent == ROOT else p.parent.relative_to(ROOT).as_posix() + "/"
                for p in ROOT.glob("**/index.html") if not any(x in p.parts for x in (".venv", "review", "node_modules", "src-assets"))})
JS = """() => {
  const out = [];
  const name = (e) => e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\\s+/).join('.') : '')
    + ' < ' + (e.parentElement ? e.parentElement.tagName.toLowerCase() + '.' + String(e.parentElement.className).trim().split(/\\s+/)[0] : '');
  const add = (kind, e) => {
    const s = getComputedStyle(e);
    if (s.display === 'none' || !e.textContent.trim()) return;
    const fs = parseFloat(s.fontSize), lh = s.lineHeight === 'normal' ? 'normal' : (parseFloat(s.lineHeight) / fs).toFixed(2);
    out.push([kind, name(e), s.fontFamily.split(',')[0].replace(/"/g, ''), s.fontWeight, s.fontStyle, s.textTransform,
              lh, (parseFloat(s.letterSpacing) / fs || 0).toFixed(3), fs.toFixed(1)]);
  };
  document.querySelectorAll('h1, h2, h3').forEach((e) => add('heading', e));
  document.querySelectorAll('main p:not([class])').forEach((e) => add('body', e));
  document.querySelectorAll('.nav__link, .nav__trigger').forEach((e) => add('nav', e));
  document.querySelectorAll('.btn').forEach((e) => add('button', e));
  document.querySelectorAll('.eyebrow').forEach((e) => add('eyebrow', e));
  document.querySelectorAll('em, i, [style*="italic"]').forEach((e) => add('italic?', e));
  return out;
}"""


def main():
    seen = Counter()
    where = {}
    with sync_playwright() as p:
        b = launch(p)
        for path in PAGES:
            pg = b.new_page(viewport={"width": 1440, "height": 900})
            try:
                pg.goto("http://127.0.0.1:8080/" + path, wait_until="load")
                pg.evaluate("document.fonts.ready")
                rows = pg.evaluate(JS)
            except Exception as e:  # a page that redirects (e.g. a retired URL) is skipped
                print("skipped", path, str(e)[:60])
                continue
            finally:
                pass
            pg.close()
            for row in rows:
                key = tuple(row)
                seen[key] += 1
                where.setdefault(key, path or "/")
        b.close()
    bad = []
    for key, n in sorted(seen.items()):
        kind, el, fam, wt, style, tt, lh, ls, fs = key
        problems = []
        if kind == "heading":
            if tt == "uppercase":
                if fam != "Jost" or wt != "500":
                    problems.append("label-style heading not Jost 500")
            else:
                if fam != "Cormorant Garamond": problems.append("not Cormorant")
                if wt != "500": problems.append(f"weight {wt}")
                if el.startswith("h1") and lh not in ("1.08",): problems.append(f"lh {lh}")
                if not el.startswith("h1") and lh not in ("1.15",): problems.append(f"lh {lh}")
                if ls != "-0.005": problems.append(f"ls {ls}")
        elif kind in ("body",):
            if fam != "Jost" or wt != "400": problems.append(f"{fam} {wt}")
            if lh != "1.65": problems.append(f"lh {lh}")
        elif kind == "nav":
            if fam != "Jost" or wt != "500": problems.append(f"{fam} {wt}")
        elif kind in ("button", "eyebrow"):
            if fam != "Jost" or wt != "500" or tt != "uppercase" or ls != "0.140" or not 12 <= float(fs) <= 13:
                problems.append(f"{fam} {wt} {tt} ls {ls} {fs}px")
        elif kind == "italic?":
            if style == "italic" and "accent" not in el: problems.append("italic outside the hero accent")
        if problems or "--all" in sys.argv:
            bad.append(f"{n:>3}x {kind:<8} {el[:70]:<70} {fam} {wt} {style} {tt} lh {lh} ls {ls} {fs}px  {'; '.join(problems)}  e.g. {where[key]}")
    print("\n".join(bad))
    print(f"{len(PAGES)} pages, {len(bad)} style groups flagged")


if __name__ == "__main__":
    main()
