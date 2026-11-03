"""Keyboard-only walkthrough (needs the site served on 8080). For the pages a visitor is most likely to use, at 1440
and 390 px, press Tab from the top of the page to the end and check every stop:

- the first stop is the skip link, it becomes visible, and Enter moves focus into <main>;
- the focused element is visible (not faded out by a reveal, not zero-sized), inside the screen, not hidden under
  the sticky header or the call bar, and shows a focus ring (outline or box-shadow);
- Tab never gets stuck, and Shift+Tab goes back to the previous stop.

Usage: .venv/Scripts/python -I tools/qa/keyboard.py [--out file]
Exit code 1 on any problem.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402
from console import BASE  # noqa: E402

PAGES = ["", "book/", "emergency/", "dental-implants/", "problems/", "problems/toothache/", "doctors/",
         "gallery/", "treatments/", "the-practice/"]
LIMIT = 260

PROBE = """() => {
  let e = document.activeElement;
  if (!e || e === document.body) return {body: true};
  // a visually hidden checkbox or radio: its label's box shows the state and the focus ring
  if (e.matches('label > input[type=checkbox], label > input[type=radio]') && parseFloat(getComputedStyle(e).opacity) === 0)
    e = e.nextElementSibling || e.parentElement;
  const r = e.getBoundingClientRect();
  const s = getComputedStyle(e);
  let faded = false;
  for (let p = e; p && p !== document.body; p = p.parentElement) { const ps = getComputedStyle(p);
    if (parseFloat(ps.opacity) < 0.5 || ps.visibility === 'hidden') { faded = true; break; } }
  const ring = (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) || (s.boxShadow && s.boxShadow !== 'none');
  // what covers the middle of the element (the sticky header or the call bar would hide it)
  const cx = Math.min(Math.max(r.left + r.width / 2, 1), innerWidth - 1), cy = Math.min(Math.max(r.top + r.height / 2, 1), innerHeight - 1);
  const top = document.elementFromPoint(cx, cy);
  const covered = top && !(e === top || e.contains(top) || top.contains(e)) && !!top.closest('.site-header, .callbar, .call-bar, [class*="callbar"]');
  const name = (e.getAttribute('aria-label') || e.textContent || e.value || e.alt || '').trim().replace(/\\s+/g, ' ').slice(0, 40);
  return {tag: e.tagName.toLowerCase(), cls: String(e.className).split(' ')[0], name,
          w: r.width, h: r.height, top: r.top, bottom: r.bottom, left: r.left, right: r.right,
          faded, ring, covered, inMain: !!e.closest('main'), skip: e.matches('.skip-link, [href="#main"], [href="#content"]'),
          vw: innerWidth, vh: innerHeight};
}"""


def settle(pg):
    """Wait until a smooth scroll to the focused element has finished (scrollY still for 3 frames, at most 1.5 s)."""
    pg.evaluate("""() => new Promise(done => { let last = -1, still = 0; const t0 = performance.now();
      const tick = () => { const y = scrollY; still = (y === last) ? still + 1 : 0; last = y;
        if (still >= 3 || performance.now() - t0 > 1500) done(); else requestAnimationFrame(tick); };
      requestAnimationFrame(tick); })""")


def label(s):
    return f'{s.get("tag")}.{s.get("cls")} "{s.get("name")}"'


def walk(pg, path, w, problems):
    pg.goto(BASE + path, wait_until="load", timeout=60000)
    pg.wait_for_timeout(500)
    pg.keyboard.press("Tab")
    first = pg.evaluate(PROBE)
    if not first.get("skip"):
        problems.append(f"{w}px /{path}: first Tab stop is {label(first)}, not the skip link")
    elif first["w"] < 2 or first["top"] < -2 or first["faded"]:
        problems.append(f"{w}px /{path}: the skip link does not show when focused")
    else:
        pg.keyboard.press("Enter")
        pg.wait_for_timeout(150)
        pg.keyboard.press("Tab")
        if not pg.evaluate(PROBE).get("inMain"):
            problems.append(f"{w}px /{path}: after the skip link, Tab does not land inside <main>")
        pg.goto(BASE + path, wait_until="load", timeout=60000)
        pg.wait_for_timeout(400)
    seen, stops, prev = [], 0, None
    for i in range(LIMIT):
        pg.keyboard.press("Tab")
        settle(pg)
        s = pg.evaluate(PROBE)
        if s.get("body"):
            break
        key = (label(s), round(s["top"] + pg.evaluate("scrollY")))
        if seen and key == seen[0]:
            break  # back at the start
        if prev and key == prev:
            problems.append(f"{w}px /{path}: Tab is stuck on {label(s)}")
            break
        seen.append(key)
        prev, stops = key, stops + 1
        bad = []
        if s["w"] < 1 or s["h"] < 1:
            bad.append("zero-sized")
        if s["faded"]:
            pg.wait_for_timeout(400)  # a reveal may still be fading in
            if pg.evaluate(PROBE)["faded"]:
                bad.append("faded out")
        if s["bottom"] < 0 or s["top"] > s["vh"] or s["right"] < 0 or s["left"] > s["vw"]:
            bad.append("off screen")
        if not s["ring"]:
            bad.append("no focus ring")
        if s["covered"]:
            bad.append("under the header or call bar")
        if bad:
            problems.append(f"{w}px /{path}: stop {stops} {label(s)}: {', '.join(bad)}")
    else:
        problems.append(f"{w}px /{path}: more than {LIMIT} Tab stops (a trap?)")
    # Shift+Tab goes back one stop
    if stops > 2:
        pg.keyboard.press("Shift+Tab")
        pg.wait_for_timeout(40)
        if pg.evaluate(PROBE).get("body"):
            problems.append(f"{w}px /{path}: Shift+Tab loses focus")
    return stops


def main():
    out = open(sys.argv[sys.argv.index("--out") + 1], "w", encoding="utf-8") if "--out" in sys.argv else sys.stdout
    problems = []
    with sync_playwright() as p:
        b = pw.launch(p)
        for w in (1440, 390):
            phone = w < 768
            ctx = b.new_context(viewport={"width": w, "height": 844 if phone else 900}, is_mobile=False, has_touch=False)
            ctx.add_init_script("try { sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
            for path in PAGES:
                pg = ctx.new_page()
                n = walk(pg, path, w, problems)
                print(f"{w}px /{path}: {n} Tab stops", file=out, flush=True)
                pg.close()
            ctx.close()
        b.close()
    for x in problems:
        print("FAIL  " + x, file=out)
    print(f"{len(problems)} problems", file=out, flush=True)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
