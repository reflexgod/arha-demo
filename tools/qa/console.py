"""Console errors and failed requests on every built page (needs the site served on 8080).

Usage: .venv/Scripts/python tools/qa/console.py [--width 1440]
Opens each page, scrolls it to the end (lazy images and videos load), and lists console errors,
uncaught exceptions and failed same-site requests. Exit code 1 when there are any.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BASE = "http://127.0.0.1:8080/"
SKIP = ("review", ".venv", "tools", "src-assets", "node_modules", "notes", ".git")


def paths():
    for p in sorted(ROOT.rglob("index.html")):
        rel = p.parent.relative_to(ROOT)
        if not any(part in SKIP for part in rel.parts):
            yield "" if str(rel) == "." else rel.as_posix() + "/"


def main():
    width = int(sys.argv[sys.argv.index("--width") + 1]) if "--width" in sys.argv else 1440
    problems = []
    with sync_playwright() as p:
        b = pw.launch(p)
        ctx = b.new_context(viewport={"width": width, "height": 900 if width > 600 else 844}, is_mobile=width < 600, has_touch=width < 600)
        for path in paths():
            pg = ctx.new_page()
            found = []
            pg.on("console", lambda m: found.append(f"console {m.type}: {m.text[:160]}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: found.append(f"exception: {str(e)[:160]}"))
            pg.on("requestfailed", lambda r: found.append(f"failed: {r.url[:120]}") if r.url.startswith(BASE) else None)
            pg.on("response", lambda r: found.append(f"{r.status}: {r.url[:120]}") if r.url.startswith(BASE) and r.status >= 400 else None)
            pg.goto(BASE + path, wait_until="load", timeout=60000)
            pg.wait_for_timeout(300)  # a page that forwards (meta refresh) moves on here
            pg.wait_for_load_state("load")
            h = pg.evaluate("document.body.scrollHeight")
            for _y in range(0, h, 700):
                pg.mouse.wheel(0, 700)
                pg.wait_for_timeout(40)
            pg.wait_for_timeout(500)
            for f in found:
                problems.append(f"/{path}: {f}")
            pg.close()
        b.close()
    n = len(list(paths()))
    print(f"{n} pages at {width}px: {len(problems)} problems")
    for line in problems:
        print("  " + line)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
