"""One call action per screen: on every page, at 390, 768, 1024 and 1440 px, with no panel open, the clinic's
phone number or a call button shows at most once in the viewport, at every scroll position (scrolling down,
then back up, so the header is tested both hidden and shown).

Usage: .venv/Scripts/python -I tools/qa/one_call.py [--widths 390,768] [--pages book/,emergency/]
Serves the site itself (an in-process server on a free port). Exit code 1 on any screen with two or more.
Counted: every visible tel: link (the public 112 line excepted) and any visible text with the number outside one.
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
SKIP = ("review", ".venv", "tools", "src-assets", "node_modules", "notes", ".git")

COUNT = """(digits) => {
  const vw = innerWidth, vh = innerHeight;
  const shown = (el) => {
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2 || r.bottom <= 1 || r.top >= vh - 1 || r.right <= 1 || r.left >= vw - 1) return false;
    if (getComputedStyle(el).visibility !== 'visible') return false;
    for (let n = el; n && n !== document.documentElement; n = n.parentElement) {
      if (n.hidden || n.inert) return false;
      const cs = getComputedStyle(n);
      if (cs.display === 'none' || parseFloat(cs.opacity) < 0.05) return false;
    }
    return true;
  };
  const found = [];
  document.querySelectorAll('a[href^="tel:"]').forEach((a) => {
    if (a.getAttribute('href') === 'tel:112') return;
    if (shown(a)) found.push(`${a.dataset.call || a.className || 'tel'}: ${a.textContent.trim().replace(/\\s+/g, ' ').slice(0, 40)}`);
  });
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let t = walker.nextNode(); t; t = walker.nextNode()) {
    if (!t.data.replace(/\\D/g, '').includes(digits)) continue;
    const el = t.parentElement;
    if (!el || el.closest('a[href^="tel:"], script, style, noscript')) continue;
    if (shown(el)) found.push(`text: ${t.data.trim().slice(0, 40)}`);
  }
  return found;
}"""


def paths():
    for p in sorted(ROOT.rglob("index.html")):
        rel = p.parent.relative_to(ROOT)
        if not any(part in SKIP for part in rel.parts):
            yield "" if str(rel) == "." else rel.as_posix() + "/"


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=str(ROOT))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1].split(",") if name in sys.argv else default


def main():
    widths = [int(w) for w in arg("--widths", ["390", "768", "1024", "1440"])]
    pages = arg("--pages", list(paths()))
    digits = "9975507714"
    srv, base = serve()
    bad, screens = [], 0
    with sync_playwright() as p:
        b = pw.launch(p)
        for width in widths:
            touch = width <= 1024
            ctx = b.new_context(viewport={"width": width, "height": 844 if width < 768 else 1024 if width < 1100 else 900},
                                is_mobile=width < 768, has_touch=touch)
            ctx.add_init_script("try { sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
            for path in pages:
                pg = ctx.new_page()
                pg.goto(base + path, wait_until="load")
                pg.wait_for_timeout(500)
                vh = pg.evaluate("innerHeight")
                h = pg.evaluate("document.documentElement.scrollHeight")
                stops = list(range(0, max(h - vh, 0) + 1, int(vh * 0.7))) + [max(h - vh, 0)]
                for direction, ys in (("down", stops), ("up", stops[::-1][1:])):
                    for y in ys:
                        pg.evaluate(f"window.scrollTo(0, {y})")
                        pg.wait_for_timeout(420)
                        found = pg.evaluate(COUNT, digits)
                        screens += 1
                        if len(found) > 1:
                            bad.append(f"{width}px /{path} at {y} ({direction}): {len(found)}: " + " | ".join(found))
                pg.close()
            ctx.close()
        b.close()
    srv.shutdown()
    print(f"{len(pages)} pages x {len(widths)} widths, {screens} screens checked: {len(bad)} with the number or a call button more than once")
    for line in bad:
        print("  " + line)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
