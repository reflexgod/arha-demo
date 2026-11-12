"""Phone-width checks on the built site (dist/), fresh browser storage for every page.

Usage:  .venv/Scripts/python -I tools/qa_mobile.py [width]      (default 390)

For every page in dist/: the cookie banner shows on a first visit; nothing fixed (cookie banner, call bar) covers the
H1 on load; the call bar is hidden over the first section and the footer and shown in between; no sideways scroll.
Saves a first-screen screenshot per page to review/compare/v5/<page>-<width>-fold.png.
"""
import functools
import http.server
import socketserver
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
OUT = ROOT / "review" / "compare" / "v5"
PORT = 8769

JS_STATE = """() => {
  const vh = innerHeight, r = e => e && e.getBoundingClientRect();
  const bar = document.querySelector('[data-callbar]'), ck = document.querySelector('#cookie'), ico = document.querySelector('[data-cookie-reopen]');
  const h1 = r(document.querySelector('h1'));
  const fixed = [bar, ck, ico].filter(e => e && getComputedStyle(e).display !== 'none' && !e.hidden)
    .map(e => ({name: e.id || 'callbar', rect: r(e)})).filter(o => o.rect.bottom > 0 && o.rect.top < vh);
  const covers = fixed.filter(o => h1 && h1.bottom > o.rect.top && h1.top < o.rect.bottom && h1.top < vh).map(o => o.name);
  const onScreen = e => { const b = r(e); return !!b && b.bottom > 0 && b.top < vh; };
  const shouldShow = !onScreen(document.querySelector('[data-callbar-first]') || document.querySelector('#main > section')) && !onScreen(document.querySelector('.ftr'))
    && ![...document.querySelectorAll('[data-callbar-hide]')].some(onScreen);
  const icoVisible = !!ico && getComputedStyle(ico).display !== 'none';
  return {icoVisible, shouldShow, barShown: !!bar && bar.classList.contains('is-shown'), cookie: !!ck && !ck.hidden, h1Covered: covers,
          overflow: document.documentElement.scrollWidth - innerWidth};
}"""


def main():
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 390
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    handler.log_message = lambda *a, **k: None
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    OUT.mkdir(parents=True, exist_ok=True)
    pages = sorted("/" + str(p.relative_to(DIST)).replace("\\", "/").replace("index.html", "") for p in DIST.rglob("*.html"))
    problems = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            for path in pages:
                ctx = browser.new_context(viewport={"width": width, "height": 844}, is_mobile=True, has_touch=True)
                pg = ctx.new_page()
                pg.goto(f"http://127.0.0.1:{PORT}{path}", wait_until="load")
                pg.wait_for_timeout(500)
                name = path.strip("/").replace("/", "_") or "home"
                pg.screenshot(path=str(OUT / f"{name}-{width}-fold.png"))
                top = pg.evaluate(JS_STATE)
                if not top["cookie"]:
                    problems.append(f"{path}: cookie banner not shown on first visit")
                if top["barShown"]:
                    problems.append(f"{path}: call bar visible over the first section")
                if top["h1Covered"]:
                    problems.append(f"{path}: H1 covered on load by {top['h1Covered']}")
                if top["overflow"] > 0:
                    problems.append(f"{path}: sideways scroll {top['overflow']}px")
                pg.click("[data-consent=all]")
                h = pg.evaluate("document.documentElement.scrollHeight")
                pg.evaluate(f"window.scrollTo(0, {h // 2})"); pg.wait_for_timeout(500)
                mid = pg.evaluate(JS_STATE)
                pg.evaluate(f"window.scrollTo(0, {h})"); pg.wait_for_timeout(500)
                end = pg.evaluate(JS_STATE)
                if mid["icoVisible"] and width < 992:
                    problems.append(f"{path}: floating cookie icon shown on a phone")
                for where, st in (("mid-page", mid), ("page end", end)):
                    if st["barShown"] != st["shouldShow"]:
                        problems.append(f"{path}: call bar {'shown' if st['barShown'] else 'hidden'} at {where}, expected the opposite")
                print(f"{path:58} cookie={top['cookie']} bar(top/mid/end)={top['barShown']}/{mid['barShown']}/{end['barShown']} "
                      f"h1_covered={top['h1Covered'] or '-'} overflow={top['overflow']}")
                ctx.close()
            browser.close()
    finally:
        httpd.shutdown()
    print("\n".join(problems) if problems else "OK: no problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
