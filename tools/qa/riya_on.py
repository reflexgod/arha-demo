"""Riya switched on still works: builds the site with riyaEnabled = True and a stand-in webhook URL, checks the
launcher, the chat (a message goes out, a mocked reply comes back, a failed request offers only the phone), and that
the teaser never covers the hero's heading, line or button at 390, 470, 768 and 1440 px; then rebuilds with SITE as
it is in tools/pages.py (Riya off), so the working tree is left as it was.

Usage: .venv/Scripts/python -I tools/qa/riya_on.py
"""
import functools
import http.server
import io
import json
import sys
import threading
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402
import pages  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
HOOK = "https://chat.example.test/webhook/riya"


def build(**over):
    saved = dict(pages.SITE)
    pages.SITE.update(over)
    try:
        with redirect_stdout(io.StringIO()):
            pages.main()
    finally:
        pages.SITE.clear()
        pages.SITE.update(saved)


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def overlap(a, b):
    return not (a["right"] <= b["left"] or b["right"] <= a["left"] or a["bottom"] <= b["top"] or b["bottom"] <= a["top"])


def main():
    results = []
    build(riyaEnabled=True, riya_webhook_url=HOOK)
    srv, base = serve()
    try:
        with sync_playwright() as p:
            b = pw.launch(p)
            # 1. Chat round trip with a mocked webhook, then a failure
            ctx = b.new_context(viewport={"width": 1440, "height": 900})
            ctx.add_init_script("try { sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
            sent = []
            ctx.route(HOOK, lambda r: (sent.append(json.loads(r.request.post_data)), r.fulfill(status=200, content_type="application/json",
                                                                                              body=json.dumps({"output": "Mocked reply from Riya."}))))
            pg = ctx.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(base, wait_until="load")
            pg.click(".riya-launcher")
            pg.wait_for_selector(".riya__form textarea", timeout=8000)
            status = pg.inner_text(".riya__status")
            pg.fill(".riya__form textarea", "What are your timings?")
            pg.keyboard.press("Enter")
            pg.wait_for_selector(".riya__msg--bot:has-text('Mocked reply')", timeout=8000)
            results.append(("Launcher opens the chat; a message reaches the webhook and the reply shows",
                            bool(sent) and sent[0].get("chatInput") == "What are your timings?"))
            results.append((f"Status line reads \"{status}\" (no \"Replies instantly\")", "instantly" not in status.lower()))
            ctx.unroute(HOOK)
            ctx.route(HOOK, lambda r: r.fulfill(status=404, body="No instance here"))
            pg.fill(".riya__form textarea", "Hello?")
            pg.keyboard.press("Enter")
            pg.wait_for_timeout(1500)
            fail = pg.locator(".riya__msg--bot").last.inner_text()
            results.append((f"Failure message: \"{fail}\"", "whatsapp" not in fail.lower() and "99755" in fail))
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(400)
            results.append(("Escape closes the chat and focus returns to the launcher",
                            pg.evaluate("document.activeElement && document.activeElement.classList.contains('riya-launcher')")))
            results.append(("No page errors", not errors))
            ctx.close()
            # 2. The teaser never covers the hero's heading, line or button
            for w, h in [(390, 844), (470, 900), (768, 1024), (1440, 900)]:
                ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=w < 768, has_touch=w < 768)
                ctx.add_init_script("try { sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
                pg = ctx.new_page()
                pg.goto(base, wait_until="load")
                pg.wait_for_timeout(500)
                early = pg.locator(".riya-bubble").count()
                hero_h = pg.evaluate("document.querySelector('[data-hero]').getBoundingClientRect().bottom + scrollY")
                pg.evaluate(f"scrollTo(0, {hero_h + 40})")
                pg.wait_for_timeout(700)
                shown = pg.locator(".riya-bubble.is-visible").count()
                # back up to the hero: the teaser leaves rather than sit over the heading
                pg.evaluate("scrollTo(0, 0)")
                pg.wait_for_timeout(700)
                rects = pg.evaluate("""() => { const r = (s) => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return {left: b.left, right: b.right, top: b.top, bottom: b.bottom}; };
                  return {bubble: document.querySelector('.riya-bubble.is-visible') ? r('.riya-bubble') : null, h1: r('.ah-hero h1'), lede: r('.ah-hero .hero__lede'), cta: r('.ah-hero .hero__actions')}; }""")
                covers = rects["bubble"] and any(overlap(rects["bubble"], rects[k]) for k in ("h1", "lede", "cta"))
                pg.reload(wait_until="load")
                pg.wait_for_timeout(500)
                pg.evaluate(f"scrollTo(0, {hero_h + 40})")
                pg.wait_for_timeout(700)
                again = pg.locator(".riya-bubble").count()
                results.append((f"{w}px: no teaser over the hero on load ({early}), shown once past it ({shown}), gone over the hero "
                                f"({'covers' if covers else 'clear'}), not again in the same visit ({again})",
                                early == 0 and shown == 1 and not covers and again == 0))
                ctx.close()
            b.close()
    finally:
        srv.shutdown()
        build()  # back to SITE as written in tools/pages.py
    for text, ok in results:
        print(("PASS  " if ok else "FAIL  ") + text)
    return 0 if all(ok for _t, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())
