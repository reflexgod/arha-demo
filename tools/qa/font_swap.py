"""Does the headline font shift anything when it arrives? Holds instrument-serif-400.woff2 back until the page has painted in the fallback,
then lets it through, measures the layout shift of the swap and compares headline line counts before and after. Starts its own server.
Usage: .venv/Scripts/python tools/qa/font_swap.py <port> [path ...]
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402

PORT = int(sys.argv[1])
PATHS = sys.argv[2:] or ["", "dental-implants/", "problems/loose-dentures/", "book/"]
BASE = f"http://127.0.0.1:{PORT}/"
INIT = """try{sessionStorage.setItem('arha-intro','1')}catch(e){}
window.__cls=0;try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}"""
LINES = """() => [...document.querySelectorAll('main h1, main h2')].filter((e) => e.getBoundingClientRect().height).map((e) => Math.round(e.getBoundingClientRect().height / parseFloat(getComputedStyle(e).lineHeight)))"""
FONT = "document.fonts.check('400 40px \"Instrument Serif\"')"


def main():
    server = subprocess.Popen([sys.executable, "-I", str(Path(__file__).parent / "gzserve.py"), str(PORT), str(Path(__file__).resolve().parents[2])])
    worst = 0
    try:
        with sync_playwright() as p:
            b = pw.launch(p)
            for w, h, phone in [(390, 844, True), (1440, 900, False)]:
                for path in PATHS:
                    ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=phone, has_touch=phone)
                    ctx.add_init_script(INIT)
                    pg = ctx.new_page()
                    held = []
                    open_gate = []
                    pg.route("**/instrument-serif-400.woff2", lambda route: route.continue_() if open_gate else held.append(route))
                    pg.goto(BASE + path, wait_until="commit")
                    pg.wait_for_selector("main h1")
                    pg.wait_for_timeout(1200)  # headlines have painted in the fallback
                    before, loaded0 = pg.evaluate(LINES), pg.evaluate(FONT)
                    open_gate.append(True)
                    for r in held:
                        r.continue_()
                    pg.wait_for_timeout(1500)
                    pg.evaluate("document.fonts.ready")
                    after, loaded1 = pg.evaluate(LINES), pg.evaluate(FONT)
                    cls = pg.evaluate("window.__cls")
                    worst = max(worst, cls)
                    changed = sum(1 for x, y in zip(before, after) if x != y)
                    print(f"{w}px /{path}: font before {loaded0}, after {loaded1}; CLS {cls:.4f}; {changed} of {len(after)} headlines changed line count")
                    ctx.close()
            b.close()
    finally:
        server.kill()
    print(f"worst CLS {worst:.4f}")


if __name__ == "__main__":
    main()
