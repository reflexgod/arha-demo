"""Colour on hover, every reachable black and white photo on a page: hover -> filter none; away -> grey again."""
import sys; sys.path.insert(0, sys.argv[1])
from pw import launch, BASE as B
from playwright.sync_api import sync_playwright
PROBE = """(i) => { const im=document.querySelectorAll('img.bw-photo')[i]; const r=im.getBoundingClientRect();
  if (r.width < 60 || r.height < 60) return null;
  const x=r.x+r.width/2, y=Math.max(70, Math.min(r.y+r.height/2, innerHeight-60));
  const hit = (a, b) => { const st = document.elementsFromPoint(a, b); const g = im.closest('[data-colour-group]'); return st.includes(im) || (g && st.includes(g)); };
  if (!hit(x, y)) return null;
  // a point outside the photo where no part of it is under the pointer
  const cands=[[x, r.y-12],[x, r.bottom+12],[r.x-12, y],[r.right+12, y],[8,innerHeight-8],[innerWidth-8,70]];
  const out=cands.find(([a,b])=>a>0&&b>0&&a<innerWidth&&b<innerHeight&&!hit(a,b));
  return out ? [x,y,out[0],out[1], im.currentSrc.split('/').pop().replace(/-\d+\.\w+$/,'')] : null }"""
def run(pg, path):
    pg.goto(B + path); pg.wait_for_timeout(400)
    n = pg.evaluate("document.querySelectorAll('img.bw-photo').length")
    ok, bad, skipped = [], [], 0
    for i in range(n):
        pg.evaluate("(i)=>document.querySelectorAll('img.bw-photo')[i].scrollIntoView({block:'center',behavior:'instant'})", i)
        pg.wait_for_timeout(200)
        pr = pg.evaluate(PROBE, i)
        if not pr: skipped += 1; continue
        x, y, ox, oy, src = pr
        pg.mouse.move(ox, oy); pg.wait_for_timeout(700)
        g0 = pg.evaluate("(i)=>getComputedStyle(document.querySelectorAll('img.bw-photo')[i]).filter", i)
        pg.mouse.move(x, y, steps=3); pg.wait_for_timeout(700)
        f = pg.evaluate("(i)=>getComputedStyle(document.querySelectorAll('img.bw-photo')[i]).filter", i)
        pg.mouse.move(ox, oy); pg.wait_for_timeout(700)
        g = pg.evaluate("(i)=>getComputedStyle(document.querySelectorAll('img.bw-photo')[i]).filter", i)
        (ok if (g0 != "none" and f == "none" and g != "none") else bad).append((src, g0, f, g))
    return n, ok, bad, skipped
if __name__ == "__main__":
    with sync_playwright() as p:
        br = launch(p)
        pg = br.new_page(viewport={"width": 1440, "height": 900})
        for path in sys.argv[2:]:
            n, ok, bad, sk = run(pg, path)
            print(f"{path or 'home'}: bw {n}, pass {len(ok)}, fail {len(bad)}, not reachable {sk}", bad[:3])
        br.close()
