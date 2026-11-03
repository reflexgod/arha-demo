"""The full phone journey, tapped like a visitor, on an emulated iPhone 13 and Pixel 7 (Chromium with each device's
screen, pixel ratio, touch and user agent): land on the homepage, scroll the hero away, choose "Tooth pain" in the
finder, read the answer, open "Toothache, explained", go on to Root canal treatment, read it to the end, tap Book an
appointment and reach the phone number on /book/. Screenshots at each step; console errors, failed requests and
sideways overflow are recorded along the way.

Usage: .venv/Scripts/python -I tools/qa/journey.py <out folder>
Serves the site itself. Exit code 1 on any problem.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402
from hours_states import serve  # noqa: E402

DEVICES = {"iphone-13": "iPhone 13", "pixel-7": "Pixel 7"}
WIDE = "() => document.documentElement.scrollWidth - innerWidth"


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    srv, base = serve()
    problems, log = [], []
    with sync_playwright() as p:
        b = pw.launch(p)
        for key, name in DEVICES.items():
            ctx = b.new_context(**p.devices[name])
            pg = ctx.new_page()
            errs = []
            pg.on("console", lambda m: errs.append("console: " + m.text[:140]) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append("exception: " + str(e)[:140]))
            pg.on("response", lambda r: errs.append(f"{r.status} {r.url[:90]}") if r.url.startswith(base) and r.status >= 400 else None)
            step = [0]

            def shot(label):
                step[0] += 1
                pg.wait_for_timeout(350)
                pg.screenshot(path=str(out / f"{key}-{step[0]:02d}-{label}.png"))
                over = pg.evaluate(WIDE)
                if over > 1:
                    problems.append(f"{key} {label}: page {over}px wider than the screen")
                log.append(f"{key} {step[0]:02d} {label}: {pg.url.replace(base, '/')} scrollY={pg.evaluate('Math.round(scrollY)')}")

            pg.goto(base, wait_until="load")
            shot("intro")  # first visit in a tab: the emblem draws itself (1.15 s), then the hero
            pg.wait_for_timeout(1200)
            shot("landing")
            bar = pg.evaluate("() => { const b = document.querySelector('.call-bar'); return b ? getComputedStyle(b).transform + ' ' + b.getBoundingClientRect().top : 'none'; }")
            log.append(f"{key} call bar on landing: {bar}")
            pg.mouse.wheel(0, 900)
            pg.evaluate("scrollBy(0, 900)")
            shot("hero-scrolled-away")
            pg.locator(".finder__card[data-go='r-pain']").scroll_into_view_if_needed()
            shot("finder")
            pg.locator(".finder__card[data-go='r-pain']").tap()
            pg.wait_for_timeout(500)
            if not pg.locator("#r-pain").is_visible():
                problems.append(f"{key}: tapping Tooth pain did not open its answer")
            shot("finder-answer")
            pg.locator("#r-pain a[href='problems/toothache/']").scroll_into_view_if_needed()
            with pg.expect_navigation(wait_until="load"):
                pg.locator("#r-pain a[href='problems/toothache/']").tap()
            if "problems/toothache" not in pg.url:
                problems.append(f"{key}: 'Toothache, explained' did not open the toothache page ({pg.url})")
            shot("toothache-top")
            pg.evaluate("scrollTo(0, document.documentElement.scrollHeight / 2)")
            shot("toothache-middle")
            link = pg.locator("main a[href$='root-canal-treatment/']:visible").first
            link.scroll_into_view_if_needed()
            shot("toothache-to-root-canal")
            with pg.expect_navigation(wait_until="load"):
                link.tap()
            if "root-canal-treatment" not in pg.url:
                problems.append(f"{key}: the root canal link did not open the treatment page ({pg.url})")
            shot("treatment-top")
            h = pg.evaluate("document.documentElement.scrollHeight")
            for frac in (0.33, 0.66):
                pg.evaluate(f"scrollTo(0, {int(h * frac)})")
                shot(f"treatment-{int(frac * 100)}")
            pg.evaluate("scrollTo(0, document.documentElement.scrollHeight)")
            shot("treatment-end")
            book = pg.locator("a[href$='book/']:visible").last
            book.scroll_into_view_if_needed()
            with pg.expect_navigation(wait_until="load"):
                book.tap()
            if "/book/" not in pg.url:
                problems.append(f"{key}: Book an appointment did not open /book/ ({pg.url})")
            shot("book")
            tel = pg.locator("main a[href^='tel:+91']").first
            if not tel.count():
                problems.append(f"{key}: no call link on /book/")
            else:
                tel.scroll_into_view_if_needed()
                shot("book-call")
                log.append(f"{key} book call link: {tel.get_attribute('href')} '{tel.inner_text().strip()}'")
            for e in errs:
                problems.append(f"{key}: {e}")
            ctx.close()
        b.close()
    srv.shutdown()
    (out / "journey.txt").write_text("\n".join(log + [""] + ["FAIL  " + x for x in problems] + [f"{len(problems)} problems"]), encoding="utf-8")
    print("\n".join(log))
    for x in problems:
        print("FAIL  " + x)
    print(f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
