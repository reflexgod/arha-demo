"""Every opening-hours state (hours_states.STATES, mocked clock) at narrow widths: no page wider than the screen,
with the side menu closed and open. The status text is longest while closed ("Closed · Opens tomorrow at 9:30 AM"),
which is what most first visits in the evening see.

Usage: .venv/Scripts/python -I tools/qa/hours_overflow.py
Exit code 1 on any problem.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402
from hours_states import STATES, serve  # noqa: E402

PAGES = ["", "emergency/", "book/", "dental-implants/", "problems/toothache/", "doctors/"]
WIDTHS = [320, 360, 375, 390, 414, 430, 600, 768]
WIDE = """(w) => { const d = document.documentElement;
  const out = d.scrollWidth > w + 1 ? ['page ' + d.scrollWidth] : [];
  const m = document.querySelector('.menu-toggle'); if (m && m.getBoundingClientRect().right > w + 1) out.push('menu button off-screen');
  return out; }"""


def main():
    srv, base = serve()
    problems, runs = [], 0
    with sync_playwright() as p:
        b = pw.launch(p)
        for label, utc, tz in STATES:
            when = datetime.fromisoformat(utc).replace(tzinfo=timezone.utc)
            for w in WIDTHS:
                ctx = b.new_context(viewport={"width": w, "height": 800}, is_mobile=True, has_touch=True, timezone_id=tz)
                ctx.add_init_script("try { sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
                pg = ctx.new_page()
                pg.clock.set_fixed_time(when)
                for path in PAGES:
                    pg.goto(base + path, wait_until="load")
                    pg.wait_for_timeout(150)
                    for x in pg.evaluate(WIDE, w):
                        problems.append(f"{label} {w}px /{path}: {x}")
                    pg.click(".menu-toggle")
                    pg.wait_for_timeout(450)
                    bad = pg.evaluate("""(w) => [...document.querySelectorAll('.side-menu *')].filter(e => {
                        const r = e.getBoundingClientRect(); return r.width > 0 && r.right > w + 1 && getComputedStyle(e).visibility !== 'hidden'; })
                        .slice(0, 2).map(e => e.className + ' ' + Math.round(e.getBoundingClientRect().right))""", w)
                    for x in bad:
                        problems.append(f"{label} {w}px /{path} menu open: {x}")
                    runs += 1
                ctx.close()
        b.close()
    srv.shutdown()
    for x in problems:
        print("FAIL  " + x)
    print(f"{len(STATES)} states x {len(WIDTHS)} widths x {len(PAGES)} pages = {runs} checks, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
