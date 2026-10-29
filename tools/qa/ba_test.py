"""Before/after slider, really driven: mouse drag, click to jump, keyboard (1440); touch drag, tap, vertical
swipe still scrolls (390, CDP touch events). Also frame timing during a drag. Usage: ba_test.py SCRATCH [paths...]"""
import json
import sys
sys.path.insert(0, sys.argv[1])
from pw import launch, BASE as B
from playwright.sync_api import sync_playwright

POS = "(sel) => parseFloat(document.querySelector(sel).style.getPropertyValue('--pos'))"
results = []


def rec(page, vp, action, ok, note=""):
    results.append({"page": page, "vp": vp, "action": action, "ok": bool(ok), "note": note})
    print(f"{'PASS' if ok else 'FAIL'}  {vp:>4}  {page:<28} {action:<34} {note}")


def box(pg, sel):
    pg.evaluate("(sel) => document.querySelector(sel).scrollIntoView({block: 'center', behavior: 'instant'})", sel)
    pg.wait_for_timeout(300)
    return pg.evaluate("(sel) => { const r = document.querySelector(sel).getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height} }", sel)


def desktop(pg, path, sel="[data-ba]"):
    pg.goto(B + path); pg.wait_for_timeout(500)
    b = box(pg, sel)
    y = b["y"] + b["h"] * 0.3
    # drag from 20% to 85% with frame timing
    pg.evaluate("""() => { window.__f = []; let last = performance.now(); const tick = (t) => { window.__f.push(t - last); last = t; if (window.__f.length < 400) requestAnimationFrame(tick) }; requestAnimationFrame(tick) }""")
    pg.mouse.move(b["x"] + b["w"] * 0.2, y); pg.mouse.down(); pg.wait_for_timeout(40)
    p1 = pg.evaluate(POS, sel)
    for k in range(1, 41):
        pg.mouse.move(b["x"] + b["w"] * (0.2 + 0.65 * k / 40), y)
        pg.wait_for_timeout(16)
    pg.mouse.up(); pg.wait_for_timeout(100)
    p2 = pg.evaluate(POS, sel)
    frames = pg.evaluate("window.__f.slice(2)")
    long = sum(1 for f in frames if f > 34)
    rec(path or "home", 1440, "mouse drag on photo (20%→85%)", abs(p1 - 20) < 2 and abs(p2 - 85) < 2, f"{p1:.0f}% → {p2:.0f}%")
    rec(path or "home", 1440, "frames during drag", long <= 2, f"{len(frames)} frames, {long} over 34 ms, avg {sum(frames)/max(len(frames),1):.1f} ms")
    pg.mouse.click(b["x"] + b["w"] * 0.4, b["y"] + b["h"] * 0.8); pg.wait_for_timeout(100)
    p3 = pg.evaluate(POS, sel)
    rec(path or "home", 1440, "click to jump (40%)", abs(p3 - 40) < 2, f"{p3:.0f}%")
    pg.focus(sel + " .ba__handle")
    pg.keyboard.press("ArrowRight"); pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(80)
    p4 = pg.evaluate(POS, sel)
    pg.keyboard.press("Shift+ArrowLeft"); pg.wait_for_timeout(80)
    p5 = pg.evaluate(POS, sel)
    pg.keyboard.press("End"); pg.wait_for_timeout(80)
    p6 = pg.evaluate(POS, sel)
    aria = pg.get_attribute(sel + " .ba__handle", "aria-valuenow")
    rec(path or "home", 1440, "keyboard (→ →, Shift+←, End)", abs(p4 - 44) < 1 and abs(p5 - 34) < 1 and p6 == 100 and aria == "100", f"{p4:.0f} / {p5:.0f} / {p6:.0f}, aria {aria}")
    # the line and handle follow the position in pixels
    hx = pg.evaluate("(sel) => { const h = document.querySelector(sel + ' .ba__handle').getBoundingClientRect(); const r = document.querySelector(sel).getBoundingClientRect(); return (h.x + h.width / 2 - r.x) / r.width * 100 }", sel)
    rec(path or "home", 1440, "handle sits on the line", abs(hx - 100) < 1.5, f"{hx:.1f}%")


def touch(cdp, kind, pts):
    cdp.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [{"x": x, "y": y} for x, y in pts]})


def mobile(pg, cdp, path, sel="[data-ba]"):
    pg.goto(B + path); pg.wait_for_timeout(500)
    b = box(pg, sel)
    y = b["y"] + b["h"] * 0.5
    x0 = b["x"] + b["w"] * 0.25
    touch(cdp, "touchStart", [(x0, y)])
    for k in range(1, 21):
        touch(cdp, "touchMove", [(x0 + b["w"] * 0.55 * k / 20, y + k * 0.3)]); pg.wait_for_timeout(16)
    touch(cdp, "touchEnd", []); pg.wait_for_timeout(150)
    p1 = pg.evaluate(POS, sel)
    rec(path or "home", 390, "touch drag (25%→80%)", abs(p1 - 80) < 4, f"{p1:.0f}%")
    xt = b["x"] + b["w"] * 0.3
    touch(cdp, "touchStart", [(xt, y)]); pg.wait_for_timeout(60); touch(cdp, "touchEnd", []); pg.wait_for_timeout(150)
    p2 = pg.evaluate(POS, sel)
    rec(path or "home", 390, "tap to jump (30%)", abs(p2 - 30) < 3, f"{p2:.0f}%")
    s0 = pg.evaluate("scrollY")
    touch(cdp, "touchStart", [(xt, y)])
    for k in range(1, 16):
        touch(cdp, "touchMove", [(xt + k * 0.4, y - k * 14)]); pg.wait_for_timeout(16)
    touch(cdp, "touchEnd", []); pg.wait_for_timeout(500)
    s1 = pg.evaluate("scrollY"); p3 = pg.evaluate(POS, sel)
    rec(path or "home", 390, "vertical swipe scrolls the page", s1 - s0 > 60 and abs(p3 - p2) < 2, f"scrolled {s1 - s0:.0f}px, slider {p2:.0f}→{p3:.0f}%")


if __name__ == "__main__":
    paths = sys.argv[2:] or ["", "our-work/sample-veneers-1/", "our-work/sample-implants-1/"]
    with sync_playwright() as p:
        br = launch(p)
        pg = br.new_page(viewport={"width": 1440, "height": 900})
        for path in paths:
            desktop(pg, path)
        ctx = br.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True, device_scale_factor=2)
        m = ctx.new_page()
        cdp = ctx.new_cdp_session(m)
        for path in paths:
            mobile(m, cdp, path)
        br.close()
    out = Path = __import__("pathlib").Path(sys.argv[1]) / "ba_results.json"
    out.write_text(json.dumps(results, indent=1))
    print(sum(r["ok"] for r in results), "/", len(results), "pass")
