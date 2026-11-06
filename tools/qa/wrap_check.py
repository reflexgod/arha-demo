"""Wrapping check (v5-fonts, 7 Nov 2026), every page at 375 and 1440 px: H1/H2 whose last line is a single word,
buttons whose label breaks onto two lines, the hero H1 over two lines on laptops, and horizontal overflow.

Run (server on 8080):  .venv/Scripts/python -I tools/qa/wrap_check.py
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from pw import launch  # noqa: E402
from type_check import PAGES  # noqa: E402

JS = """() => {
  const out = [];
  const lines = (el) => {
    const r = document.createRange(), tops = [], words = [];
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      const re = /\\S+/g; let m;
      while ((m = re.exec(n.data))) { r.setStart(n, m.index); r.setEnd(n, m.index + m[0].length); const b = r.getBoundingClientRect(); if (b.width) words.push([Math.round(b.top), m[0]]); }
    }
    const rows = [];
    words.forEach(([t, w]) => { const row = rows.find((x) => Math.abs(x.t - t) < 6); if (row) row.w.push(w); else rows.push({ t, w: [w] }); });
    return rows;
  };
  document.querySelectorAll('h1, h2').forEach((h) => {
    if (getComputedStyle(h).display === 'none' || h.closest('[hidden], .dropdown, .side-menu')) return;
    const rows = lines(h);
    if (rows.length > 1 && rows[rows.length - 1].w.length === 1) out.push(['orphan', h.tagName, h.textContent.trim().slice(0, 60), rows.length]);
    if (h.closest('.hero-v9') && innerWidth >= 1024 && rows.length > 2) out.push(['hero-lines', h.tagName, h.textContent.trim().slice(0, 60), rows.length]);
  });
  document.querySelectorAll('.btn').forEach((b) => {
    if (!b.offsetParent || b.closest('.dropdown, .side-menu, [hidden]')) return;
    const rows = lines(b);
    if (rows.length > 1) out.push(['button-wraps', 'BTN', b.textContent.trim().slice(0, 60), rows.length]);
  });
  if (document.documentElement.scrollWidth > innerWidth) out.push(['overflow', '', String(document.documentElement.scrollWidth), 0]);
  return out;
}"""


def main():
    issues = []
    with sync_playwright() as p:
        b = launch(p)
        for w in (375, 1440):
            for path in PAGES:
                pg = b.new_page(viewport={"width": w, "height": 812 if w < 800 else 900}, is_mobile=w < 800, has_touch=w < 800)
                try:
                    pg.goto("http://127.0.0.1:8080/" + path, wait_until="load")
                    pg.evaluate("document.fonts.ready")
                    for kind, tag, text, n in pg.evaluate(JS):
                        issues.append(f"{w:>5} {path or '/':<30} {kind:<13} {tag} {n} lines  {text}")
                except Exception as e:
                    issues.append(f"{w:>5} {path or '/':<30} skipped ({str(e)[:50]})")
                pg.close()
        b.close()
    print("\n".join(issues) or "no issues")
    print(len([i for i in issues if "skipped" not in i]), "issues")


if __name__ == "__main__":
    main()
