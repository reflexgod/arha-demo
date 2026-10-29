"""Colour on hover, appended to ix_results.json: at 1440 every reachable black and white photo turns to
colour under the mouse and back to grey when it leaves; at 390 a photo turns to colour when it is
mostly in view and back when scrolled away. Usage: colour_suite.py SCRATCH"""
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
from pw import launch, BASE as B  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
import colour_check  # noqa: E402

OUT = Path(sys.argv[1]) / "ix_results.json"
results = json.loads(OUT.read_text()) if OUT.exists() else []
results = [r for r in results if r["interactive"] != "Colour on hover"]
PAGES = ["", "problems/missing-tooth/", "problems/gaps/", "dental-implants/", "orthodontics/", "our-work/", "our-work/sample-implants-1/", "founder/", "kids-dentistry/"]

with sync_playwright() as p:
    br = launch(p)
    pg = br.new_page(viewport={"width": 1440, "height": 900})
    for path in PAGES:
        n, ok, bad, sk = colour_check.run(pg, path)
        tr = pg.evaluate("() => { const i = document.querySelector('img.bw-photo'); if (!i) return ''; const s = getComputedStyle(i); return s.transitionProperty + ' / ' + s.transitionDuration }")
        props, durs = [x.split(', ') for x in tr.split(' / ')] if tr else ([], [])
        slow = any(pr == "filter" and du == "0.6s" for pr, du in zip(props, durs))
        results.append({"page": path or "home", "interactive": "Colour on hover", "vp": 1440, "action": f"hover {len(ok)} photos on, then off",
                        "ok": not bad and len(ok) > 0 and slow, "note": f"{len(ok)} pass, {len(bad)} fail, 600ms {slow}" + (f"; {bad[:2]}" if bad else "")})
        print(results[-1])
    ctx = br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    m = ctx.new_page()
    for path in PAGES:
        m.goto(B + path); m.wait_for_timeout(500)
        res = m.evaluate("""async () => {
          const ims = [...document.querySelectorAll('img.bw-photo')].filter(i => i.getBoundingClientRect().height > 80 && !i.closest('[hidden]'));
          let ok = 0, bad = 0;
          for (const im of ims.slice(0, 8)) {
            im.scrollIntoView({block: 'center', behavior: 'instant'}); await new Promise(r => setTimeout(r, 750));
            const on = getComputedStyle(im).filter === 'none' || im.classList.contains('in-colour') || !!im.closest('.in-colour');
            const top = im.getBoundingClientRect().top + scrollY;
            window.scrollTo(0, top > innerHeight * 1.5 ? 0 : document.body.scrollHeight); await new Promise(r => setTimeout(r, 750));
            await new Promise(r => setTimeout(r, 200)); const off = getComputedStyle(im).filter !== 'none';
            (on && off) ? ok++ : bad++;
          }
          return [ims.length, ok, bad];
        }""")
        results.append({"page": path or "home", "interactive": "Colour on hover", "vp": 390, "action": "mostly in view: colour; away: grey",
                        "ok": res[2] == 0 and res[1] > 0, "note": f"{res[1]} pass, {res[2]} fail (of the first 8 photos)"})
        print(results[-1])
    br.close()
OUT.write_text(json.dumps(results, indent=1))
