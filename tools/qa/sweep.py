"""One sweep over every built page (needs the site served on 8080):

1. At 320, 390, 768, 1024, 1440 and 1920 px: sideways overflow (the page, or any element past the right edge that
   is not inside a rail that scrolls on its own), console errors, uncaught exceptions, failed same-site requests,
   and layout shift (CLS) while the page loads and is scrolled to the end.
2. JavaScript off (390 px): every heading, paragraph, list item and image in <main> is visible (no reveal left at 0,
   every tab and step shown); quiz answers and the stacked pictures of a crossfade are left out by design.
3. Reduced motion (390 px): every reveal is fully visible the moment it is scrolled to (no fade, no rise).

Usage: .venv/Scripts/python tools/qa/sweep.py [--widths 390,1440] [--out file]
Exit code 1 on any problem.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402
from console import paths, BASE  # noqa: E402

WIDTHS = [320, 390, 768, 1024, 1440, 1920]

OVERFLOW = """(w) => {
  const out = [];
  if (document.documentElement.scrollWidth > w + 1) out.push('page scrollWidth ' + document.documentElement.scrollWidth);
  const scrolls = (e) => { for (let p = e.parentElement; p; p = p.parentElement) { const s = getComputedStyle(p);
      if (/(auto|scroll|hidden|clip)/.test(s.overflowX)) return true; } return false; };
  for (const e of document.querySelectorAll('body *')) {
    const r = e.getBoundingClientRect();
    if (r.width === 0 || r.right <= w + 1) continue;
    const s = getComputedStyle(e);
    if (s.position === 'fixed' || s.visibility === 'hidden' || e.closest('[hidden], [aria-hidden="true"], .side-menu, dialog')) continue;
    if (scrolls(e)) continue;
    out.push(e.tagName.toLowerCase() + '.' + String(e.className).split(' ')[0] + ' right ' + Math.round(r.right));
    if (out.length > 4) break;
  }
  return out;
}"""

CLS_INIT = """window.__cls = 0; try { new PerformanceObserver((l) => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; })
  .observe({type: 'layout-shift', buffered: true}); } catch (e) {}
  try { sessionStorage.setItem('arha-intro', '1'); } catch (e) {}"""

HIDDEN = """() => [...document.querySelectorAll('main h1, main h2, main h3, main p, main li, main img, main .cta, main .btn, main a.link')].filter(e => {
  if (e.closest('[hidden], noscript, .visually-hidden, [aria-hidden="true"], template, dialog:not([open])')) return false;
  // by design: the answer of a quiz or picker (needs a script), and the stacked pictures of a crossfade (the first shows)
  if (e.closest('.picker__result, .quiz__result, .xfade__img, .agedial__img, .stages__img, .ah-band__slide')) return false;
  const r = e.getBoundingClientRect(); if (r.width === 0 && r.height === 0) return false;
  for (let p = e; p && p !== document.body; p = p.parentElement) { const s = getComputedStyle(p);
    if (parseFloat(s.opacity) < 0.99 || s.visibility === 'hidden') return true; }
  return false; }).slice(0, 4).map(e => e.tagName.toLowerCase() + '.' + String(e.className).split(' ')[0] + ' "' + (e.textContent || e.alt || '').trim().slice(0, 30) + '"')"""


def scroll_through(pg, step):
    h = pg.evaluate("document.documentElement.scrollHeight")
    y = 0
    while y < h:
        y += step
        pg.evaluate(f"scrollTo(0, {y})")
        pg.wait_for_timeout(60)
        h = pg.evaluate("document.documentElement.scrollHeight")


def main():
    widths = [int(w) for w in sys.argv[sys.argv.index("--widths") + 1].split(",")] if "--widths" in sys.argv else WIDTHS
    out = open(sys.argv[sys.argv.index("--out") + 1], "w", encoding="utf-8") if "--out" in sys.argv else sys.stdout
    problems, pages = [], list(paths())
    worst_cls = (0, "")
    with sync_playwright() as p:
        b = pw.launch(p)
        for w in widths:
            phone = w < 768
            ctx = b.new_context(viewport={"width": w, "height": 844 if phone else 900}, is_mobile=phone, has_touch=phone)
            ctx.add_init_script(CLS_INIT)
            for path in pages:
                pg = ctx.new_page()
                found = []
                pg.on("console", lambda m: found.append(f"console: {m.text[:120]}") if m.type == "error" else None)
                pg.on("pageerror", lambda e: found.append(f"exception: {str(e)[:120]}"))
                pg.on("requestfailed", lambda r: found.append(f"failed: {r.url[:100]}") if r.url.startswith(BASE) and "/assets/video/" not in r.url else None)
                pg.on("response", lambda r: found.append(f"{r.status}: {r.url[:100]}") if r.url.startswith(BASE) and r.status >= 400 else None)
                pg.goto(BASE + path, wait_until="load", timeout=60000)
                pg.wait_for_timeout(400)
                if pg.url.rstrip("/") != (BASE + path).rstrip("/"):  # a page that forwards
                    pg.close()
                    continue
                found += [f"overflow: {o}" for o in pg.evaluate(OVERFLOW, w)]
                scroll_through(pg, 700)
                pg.wait_for_timeout(300)
                found += [f"overflow after scroll: {o}" for o in pg.evaluate(OVERFLOW, w)]
                cls = pg.evaluate("window.__cls || 0")
                if cls > worst_cls[0]:
                    worst_cls = (cls, f"{w}px /{path}")
                if cls > 0.1:
                    found.append(f"CLS {cls:.3f}")
                for f in found:
                    problems.append(f"{w}px /{path}: {f}")
                pg.close()
            ctx.close()
            b.close()
            b = pw.launch(p)
            print(f"{w}px: {len(pages)} pages checked, {len(problems)} problems so far", file=out, flush=True)
        # JavaScript off
        b.close()
        b = pw.launch(p)  # a fresh browser for each pass
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, java_script_enabled=False)
        for path in pages:
            pg = ctx.new_page()
            pg.goto(BASE + path, wait_until="load", timeout=60000)
            pg.wait_for_timeout(900)  # CSS entrance animations finish
            try:
                hidden = pg.evaluate(HIDDEN)
            except Exception:  # a page that forwards (meta refresh)
                hidden = []
            for h in hidden:
                problems.append(f"JS off /{path}: hidden {h}")
            pg.close()
        ctx.close()
        print("JS off: done", file=out, flush=True)
        # Reduced motion: scroll to each reveal and read it at once
        b.close()
        b = pw.launch(p)  # a fresh browser for each pass
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, reduced_motion="reduce")
        ctx.add_init_script(CLS_INIT)
        for path in pages:
            pg = ctx.new_page()
            pg.goto(BASE + path, wait_until="load", timeout=60000)
            pg.wait_for_timeout(300)
            bad = pg.evaluate("""async () => { const bad = [];
              for (const e of document.querySelectorAll('main .reveal')) {
                if (e.closest('[hidden]')) continue;
                e.scrollIntoView({block: 'center'});
                await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
                const s = getComputedStyle(e);
                if (parseFloat(s.opacity) < 0.99 || (s.transform !== 'none' && s.transform !== 'matrix(1, 0, 0, 1, 0, 0)')) bad.push(String(e.className).split(' ')[0]);
                if (bad.length > 3) break; }
              return bad; }""")
            for x in bad:
                problems.append(f"reduced motion /{path}: .{x} not shown at once")
            pg.close()
        ctx.close()
        b.close()
    print(f"\nPages: {len(pages)}; widths: {widths}; worst CLS {worst_cls[0]:.4f} ({worst_cls[1]})", file=out)
    for x in problems:
        print("FAIL  " + x, file=out)
    print(f"{len(problems)} problems", file=out, flush=True)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
