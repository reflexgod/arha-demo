"""Centred sections (v4 fixes 3, point 4): a link or CTA standing on its own line inside a section whose
heading is centred must be centred too ("Read all reviews on Google" under the carousel, for example).

Usage: .venv/Scripts/python tools/qa/centred.py OUTDIR [--widths 1440,390]
For every page and width: each a.link / a.cta / button.cta that is the only element on its line (its parent
holds nothing else, or only text around it) inside a <section> whose .section-head is text-align: center.
Its centre must be within 6px of the centre of the section's centred heading. Writes OUTDIR/centred.json and
prints the offenders; exit code 1 if any.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import photo_audit  # noqa: E402

JS = """() => {
  const out = [];
  document.querySelectorAll('main section').forEach((sec) => {
    const head = sec.querySelector('.section-head, .case-v4__head');
    if (!head || getComputedStyle(head).textAlign !== 'center') return;
    sec.querySelectorAll('a.link, a.cta, button.cta').forEach((a) => {
      const p = a.parentElement;
      if (!p || p.children.length !== 1 || a.closest('.section-head, nav, li, dd, figure, [hidden], .statement, .xpanel, .spots__card, .brings__caption, .aid')) return;
      if (p.textContent.trim() !== a.textContent.trim() && !p.matches('.case-v4__used')) return;  // a link inside a sentence
      // The whole line (a label such as "Treatment:" counts with its link)
      const range = document.createRange();
      range.selectNodeContents(p);
      const r = range.getBoundingClientRect();
      if (!r.width || !a.getBoundingClientRect().width) return;
      // Measured against the centred heading, not the parent: a centred line in a narrow, left-placed box is still off
      const hr = head.getBoundingClientRect();
      const off = Math.round((r.left + r.width / 2) - (hr.left + hr.width / 2));
      if (Math.abs(off) > 6) out.push({ text: a.textContent.trim().slice(0, 50), section: sec.className || sec.id, off });
    });
  });
  return out;
}"""


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    widths = [int(w) for w in (sys.argv[sys.argv.index("--widths") + 1] if "--widths" in sys.argv else "1440,390").split(",")]
    found = {}
    with sync_playwright() as p:
        b = pw.launch(p)
        for w in widths:
            pg = b.new_page(viewport={"width": w, "height": 900})
            for rel, _path in photo_audit.pages():
                url = pw.BASE + ("" if rel == "home" else ("404.html" if rel == "404" else rel + "/"))
                pg.goto(url, wait_until="domcontentloaded")
                bad = pg.evaluate(JS)
                if bad:
                    found[f"{rel} @{w}"] = bad
            pg.close()
        b.close()
    (out / "centred.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    for k, v in found.items():
        for x in v:
            print(f"{k}: '{x['text']}' in {x['section']} is {x['off']}px off centre")
    print(f"{sum(len(v) for v in found.values())} off-centre links")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
