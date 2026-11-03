"""Every panel, at 1440 and 390 px: open by click (and hover for the desktop dropdowns), close with Escape and by
clicking outside, focus moves in and returns to the button that opened it, Tab stays inside a modal panel (focus
trap) and the page does not scroll behind it (scroll lock).

Usage: .venv/Scripts/python -I tools/qa/panels.py
Panels: the two header dropdowns (What we treat, Who we are), the call panel, the full-screen menu (and a + group in
it), the gallery lightbox and the finder's answer panel. Exit code 1 on any failure.
"""
import functools
import http.server
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def focused(pg, sel):
    return pg.evaluate("(s) => { const e = document.activeElement; return !!e && !!e.closest(s); }", sel)


def modal(pg, w, name, open_sel, panel_sel, open_check, close_sel=None):
    """Open, trap, lock, Escape + focus return, reopen, outside click / close button."""
    y0 = pg.evaluate("scrollY")
    pg.click(open_sel)
    pg.wait_for_timeout(500)
    check(f"{w}px {name}: opens on click", pg.evaluate(open_check))
    check(f"{w}px {name}: focus moves into it", focused(pg, panel_sel))
    inside = True
    for _ in range(40):
        pg.keyboard.press("Tab")
        inside = inside and focused(pg, panel_sel)
    check(f"{w}px {name}: Tab stays inside (focus trap)", inside)
    pg.mouse.wheel(0, 800)
    pg.wait_for_timeout(300)
    check(f"{w}px {name}: page does not scroll behind it", pg.evaluate("scrollY") == y0, f"scrollY {y0} -> {pg.evaluate('scrollY')}")
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(500)
    check(f"{w}px {name}: Escape closes it", not pg.evaluate(open_check))
    check(f"{w}px {name}: focus returns to its button", focused(pg, open_sel))
    if close_sel:
        pg.click(open_sel)
        pg.wait_for_timeout(500)
        pg.click(close_sel)
        pg.wait_for_timeout(500)
        check(f"{w}px {name}: its close button closes it", not pg.evaluate(open_check))


def main():
    srv, base = serve()
    with sync_playwright() as p:
        b = pw.launch(p)
        for w, h in ((1440, 900), (390, 844)):
            phone = w < 768
            ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=phone, has_touch=phone)
            ctx.add_init_script("try { sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
            pg = ctx.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(base, wait_until="load")
            pg.wait_for_timeout(500)
            if not phone:
                for key, label in (("dd-fix", "What we treat"), ("dd-who", "Who we are")):
                    trig = f'.nav__trigger[aria-controls="{key}"]'
                    is_open = f"document.querySelector('{trig}').getAttribute('aria-expanded') === 'true'"
                    pg.hover(trig)
                    pg.wait_for_timeout(400)
                    check(f"{w}px {label}: opens on hover", pg.evaluate(is_open))
                    pg.mouse.move(w / 2, h - 40)
                    pg.wait_for_timeout(700)
                    check(f"{w}px {label}: closes when the mouse leaves", not pg.evaluate(is_open))
                    pg.focus(trig)
                    pg.keyboard.press("Enter")
                    pg.wait_for_timeout(300)
                    check(f"{w}px {label}: opens with the keyboard", pg.evaluate(is_open))
                    pg.keyboard.press("Tab")
                    check(f"{w}px {label}: Tab moves into its links", focused(pg, f"#{key}"))
                    pg.keyboard.press("Escape")
                    pg.wait_for_timeout(300)
                    check(f"{w}px {label}: Escape closes it and focus returns", not pg.evaluate(is_open) and focused(pg, trig))
                    pg.click(trig)
                    pg.wait_for_timeout(300)
                    opened = pg.evaluate(is_open)
                    pg.mouse.click(w / 2, h - 40)
                    pg.wait_for_timeout(400)
                    check(f"{w}px {label}: click opens, a click outside closes", opened and not pg.evaluate(is_open))
                # Call panel (laptops): the header number opens it
                is_open = "!document.getElementById('call-pop').hidden"
                pg.click(".header-call")
                pg.wait_for_timeout(400)
                check(f"{w}px Call panel: opens on click", pg.evaluate(is_open))
                check(f"{w}px Call panel: focus moves to the number", focused(pg, "#call-pop"))
                pg.keyboard.press("Escape")
                pg.wait_for_timeout(400)
                check(f"{w}px Call panel: Escape closes it and focus returns", not pg.evaluate(is_open) and focused(pg, ".header-call"))
                pg.click(".header-call")
                pg.wait_for_timeout(400)
                pg.mouse.click(w / 2, h - 40)
                pg.wait_for_timeout(400)
                check(f"{w}px Call panel: a click outside closes it", not pg.evaluate(is_open))
            # Full-screen menu
            menu_open = "document.querySelector('.side-menu').classList.contains('is-open')"
            modal(pg, w, "Menu", ".menu-toggle", ".side-menu", menu_open, ".side-menu__close")
            pg.click(".menu-toggle")
            pg.wait_for_timeout(500)
            pg.click('.fmenu__toggle[aria-controls="fm-fix"]')
            pg.wait_for_timeout(400)
            check(f"{w}px Menu: + opens What we treat in place",
                  pg.evaluate("!document.getElementById('fm-fix').hidden && document.querySelector('[aria-controls=fm-fix]').getAttribute('aria-expanded') === 'true'"))
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(400)
            # Finder answer panel (homepage)
            pg.evaluate("document.getElementById('what-brings-you-in').scrollIntoView()")
            pg.wait_for_timeout(500)
            pg.click('.finder__card[data-go="r-gap"]')
            pg.wait_for_timeout(800)
            check(f"{w}px Finder: a card opens its answer", pg.evaluate("!document.getElementById('r-gap').hidden"))
            check(f"{w}px Finder: focus moves to the answer's heading", focused(pg, "#r-gap"))
            pg.click("#r-gap .finder__back--top")
            pg.wait_for_timeout(800)
            check(f"{w}px Finder: Go back returns to the cards, focus on the same card",
                  pg.evaluate("document.getElementById('r-gap').hidden") and focused(pg, '.finder__card[data-go="r-gap"]'))
            # Gallery lightbox
            pg.goto(base + "gallery/", wait_until="load")
            pg.wait_for_timeout(500)
            first = ".gal [data-full] >> nth=0"
            pg.locator(first).scroll_into_view_if_needed()
            lb_open = "(() => { const d = document.querySelector('.lightbox, [data-lightbox-view], dialog[open]'); return !!d && (d.open || d.classList.contains('is-open') || !d.hidden); })()"
            y0 = pg.evaluate("scrollY")
            pg.locator(first).click()
            pg.wait_for_timeout(600)
            check(f"{w}px Lightbox: a photograph opens large", pg.evaluate(lb_open))
            pg.keyboard.press("ArrowRight")
            pg.wait_for_timeout(300)
            pg.mouse.wheel(0, 600)
            pg.wait_for_timeout(300)
            check(f"{w}px Lightbox: page does not scroll behind it", pg.evaluate("scrollY") == y0)
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(500)
            check(f"{w}px Lightbox: Escape closes it and focus returns to the photograph",
                  not pg.evaluate(lb_open) and focused(pg, ".gal"))
            check(f"{w}px no page errors", not errors, "; ".join(errors)[:200])
            ctx.close()
        b.close()
    srv.shutdown()
    bad = [r for r in results if not r[1]]
    for name, ok, detail in results:
        print(("PASS  " if ok else "FAIL  ") + name + (f"  ({detail})" if detail and not ok else ""))
    print(f"\n{len(results) - len(bad)} of {len(results)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
