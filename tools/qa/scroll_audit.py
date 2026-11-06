"""What a visitor sees mid-scroll, on slow 4G: reveals still hidden and photos not painted while on screen, plus CLS.
Samples every 100 ms during a steady scroll of the home page (about 1,600 px a second). Starts its own gzip server.

Usage: .venv/Scripts/python tools/qa/scroll_audit.py <site root> <port> [speed px/s] [path]
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402

ROOT, PORT = sys.argv[1], int(sys.argv[2])
SPEED = int(sys.argv[3]) if len(sys.argv) > 3 else 1600
PATH = sys.argv[4] if len(sys.argv) > 4 else ""
BASE = f"http://127.0.0.1:{PORT}/"
INIT = """try{sessionStorage.setItem('arha-intro','1');sessionStorage.setItem('riya-bubble','1')}catch(e){}
window.__cls=0;try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}"""
SAMPLE = """() => {
  const vh = innerHeight, vw = innerWidth, out = {hiddenReveals: [], blankImgs: []};
  const onScreen = (r) => r.width > 0 && r.height > 0 && r.bottom > 40 && r.top < vh - 40 && r.right > 0 && r.left < vw;
  document.querySelectorAll('.reveal').forEach((e) => {
    if (e.closest('[hidden]')) return;
    const r = e.getBoundingClientRect();
    if (onScreen(r) && parseFloat(getComputedStyle(e).opacity) < 0.5) out.hiddenReveals.push(String(e.className).split(' ')[0]);
  });
  document.querySelectorAll('main img').forEach((img) => {
    if (img.closest('[hidden]')) return;
    const r = img.getBoundingClientRect();
    if (!onScreen(r)) return;
    if (!img.complete || !img.naturalWidth || parseFloat(getComputedStyle(img).opacity) < 0.5) out.blankImgs.push((img.currentSrc || img.src).split('/').pop().slice(0, 40));
  });
  return out;
}"""


def run(b, w, h, phone):
    ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=phone, has_touch=phone)
    ctx.add_init_script(INIT)
    pg = ctx.new_page()
    cdp = ctx.new_cdp_session(pg)
    cdp.send("Network.enable")
    cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})
    cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150, "downloadThroughput": 1.6e6 / 8, "uploadThroughput": 750e3 / 8})
    pg.goto(BASE + PATH, wait_until="load", timeout=120000)
    pg.wait_for_timeout(800)
    total = pg.evaluate("document.documentElement.scrollHeight") - h
    y, samples, hid, blank, hid_names, blank_names = 0, 0, 0, 0, set(), set()
    tick = 100
    while y < total:
        y += SPEED * tick / 1000
        pg.evaluate(f"scrollTo({{top: {y}, behavior: 'instant'}})")
        pg.wait_for_timeout(tick)
        s = pg.evaluate(SAMPLE)
        samples += 1
        hid += 1 if s["hiddenReveals"] else 0
        blank += 1 if s["blankImgs"] else 0
        hid_names.update(s["hiddenReveals"])
        blank_names.update(s["blankImgs"])
    cls = pg.evaluate("window.__cls")
    ctx.close()
    return {"width": w, "samples": samples, "samplesWithHiddenReveal": hid, "samplesWithBlankPhoto": blank, "cls": round(cls, 4),
            "reveals": sorted(hid_names), "photos": sorted(blank_names)}


def main():
    server = subprocess.Popen([sys.executable, "-I", str(Path(__file__).parent / "gzserve.py"), str(PORT), ROOT])
    try:
        with sync_playwright() as p:
            b = pw.launch(p)
            for w, h, phone in [(390, 844, True), (1440, 900, False)]:
                print(json.dumps(run(b, w, h, phone)), flush=True)
            b.close()
    finally:
        server.kill()


if __name__ == "__main__":
    main()
