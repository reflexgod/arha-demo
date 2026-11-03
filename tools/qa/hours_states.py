"""Opening-hours states with a mocked clock: what the footer, the menu, the phone call bar, the desktop call panel
and the Emergencies page say at set moments (always India time, whatever the visitor's own time zone).

Usage: .venv/Scripts/python -I tools/qa/hours_states.py <out folder for screenshots>
Prints one table row per state; saves the call bar and the top of /emergency/ at 390 px for each state.
"""
import functools
import http.server
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
# (label, UTC moment, visitor time zone). IST = UTC + 5:30. 3 Nov 2026 is a Tuesday.
STATES = [
    ("Weekday 08:00 IST (before opening)", "2026-11-03T02:30:00", "Asia/Kolkata"),
    ("Weekday 10:00 IST", "2026-11-03T04:30:00", "Asia/Kolkata"),
    ("Weekday 18:45 IST (just closed)", "2026-11-03T13:15:00", "Asia/Kolkata"),
    ("Saturday 19:30 IST (after closing)", "2026-11-07T14:00:00", "Asia/Kolkata"),
    ("Sunday 12:00 IST", "2026-11-08T06:30:00", "Asia/Kolkata"),
    ("Visitor in New York, Mon 23:30 local = Tue 10:00 IST", "2026-11-03T04:30:00", "America/New_York"),
    ("Visitor in London, Tue 20:00 local = Wed 01:30 IST", "2026-11-03T20:00:00", "Europe/London"),
]

READ = """() => {
  const t = (s) => { const e = document.querySelector(s); return e ? e.textContent.trim().replace(/\\s+/g, ' ') : '(none)'; };
  return {
    footer: t('.footer__status'),
    menu: t('.side-menu .open-status'),
    bar: t('.call-bar [data-call-label]') + ' / ' + t('.call-bar [data-call-status]'),
    pop: t('[data-call-pop-status]'),
  };
}"""


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    srv, base = serve()
    rows = []
    with sync_playwright() as p:
        b = pw.launch(p)
        for n, (label, utc, tz) in enumerate(STATES):
            when = datetime.fromisoformat(utc).replace(tzinfo=timezone.utc)
            ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, timezone_id=tz)
            ctx.add_init_script("try { sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
            pg = ctx.new_page()
            pg.clock.set_fixed_time(when)
            pg.goto(base + "doctors/", wait_until="load")
            pg.wait_for_timeout(300)
            pg.evaluate("scrollTo(0, 900)")  # past the hero: the call bar is up
            pg.wait_for_timeout(500)
            r = pg.evaluate(READ)
            local = pg.evaluate("new Date().toString().slice(0, 21)")
            if out:
                pg.screenshot(path=str(out / f"hours-{n}-callbar.png"), clip={"x": 0, "y": 844 - 120, "width": 390, "height": 120})
            pg.goto(base + "emergency/", wait_until="load")
            pg.wait_for_timeout(400)
            em = pg.evaluate("() => [...document.querySelectorAll('.urgent [data-call-label], .urgent .open-status')].map(e => e.textContent.trim()).join(' / ')")
            if out:
                pg.screenshot(path=str(out / f"hours-{n}-emergency.png"))
            ctx.close()
            # Desktop call panel
            ctx = b.new_context(viewport={"width": 1440, "height": 900}, timezone_id=tz)
            ctx.add_init_script("try { sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
            pg = ctx.new_page()
            pg.clock.set_fixed_time(when)
            pg.goto(base + "doctors/", wait_until="load")
            pg.wait_for_timeout(300)
            pg.locator("[data-call-pop]:visible").first.click()  # the header number, or the hero's Call now while it is in view
            pg.wait_for_timeout(300)
            r["pop"] = pg.evaluate(READ)["pop"]
            ctx.close()
            rows.append((label, local, r, em))
        b.close()
    srv.shutdown()
    for label, local, r, em in rows:
        print(f"\n{label}  [visitor's clock: {local}]")
        print(f"  footer:     {r['footer']}")
        print(f"  menu:       {r['menu']}")
        print(f"  call bar:   {r['bar']}")
        print(f"  call panel: {r['pop']}")
        print(f"  emergency:  {em}")


if __name__ == "__main__":
    main()
