"""Measure a page's sections top to bottom (V4-APA-LITERAL, points 1 and 7): apaaesthetic.com or Arha.

Usage: .venv/Scripts/python tools/qa/apa_measure.py OUTDIR URL NAME [--widths 1440,390]
For each width: scrolls the whole page for real (lazy content), then lists every top-level block of the
page (the children of <main>, or of <body> when there is no main) with its y, height, background colour,
headings (text, x, width, alignment, size), paragraphs, links/CTAs (text, x, alignment) and images
(x, y, w, h, aspect ratio, object-fit, filter), plus the computed hover transitions of images and links.
Writes OUTDIR/<NAME>-<width>.json and full-page and per-section screenshots OUTDIR/<NAME>-<width>-sNN.png.
Measurement only: no code, text or image of the measured site is reused.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402

JS = r"""() => {
  const root = document.querySelector('main') || document.body;
  let blocks = [...root.children].filter((el) => { const r = el.getBoundingClientRect(); return r.height > 40 && getComputedStyle(el).display !== 'none'; });
  // A single wrapper: descend into it
  while (blocks.length === 1 && blocks[0].children.length > 1) blocks = [...blocks[0].children].filter((el) => el.getBoundingClientRect().height > 40);
  const footer = [...document.querySelectorAll('footer')].find((f) => !f.closest('main, blockquote, figure'));
  if (footer && !blocks.includes(footer) && !root.contains(footer)) blocks.push(footer);
  const box = (el) => { const r = el.getBoundingClientRect(); return { x: Math.round(r.x), y: Math.round(r.y + scrollY), w: Math.round(r.width), h: Math.round(r.height) }; };
  const vis = (el) => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el); return r.width > 4 && r.height > 4 && cs.visibility !== 'hidden' && cs.opacity !== '0'; };
  const bg = (el) => { let e = el; while (e) { const c = getComputedStyle(e).backgroundColor; if (c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') return c; e = e.parentElement; } return ''; };
  return blocks.map((sec, i) => {
    const b = box(sec);
    const heads = [...sec.querySelectorAll('h1,h2,h3')].filter(vis).slice(0, 6).map((h) => ({ ...box(h), text: h.textContent.trim().replace(/\s+/g, ' ').slice(0, 70), align: getComputedStyle(h).textAlign, size: getComputedStyle(h).fontSize, tag: h.tagName }));
    const paras = [...sec.querySelectorAll('p')].filter(vis).slice(0, 8).map((p) => ({ ...box(p), text: p.textContent.trim().replace(/\s+/g, ' ').slice(0, 60), align: getComputedStyle(p).textAlign, size: getComputedStyle(p).fontSize }));
    const links = [...sec.querySelectorAll('a')].filter(vis).slice(0, 14).map((a) => ({ ...box(a), text: a.textContent.trim().replace(/\s+/g, ' ').slice(0, 40), size: getComputedStyle(a).fontSize, transform: getComputedStyle(a).textTransform, transition: getComputedStyle(a).transition.slice(0, 60) }));
    const imgs = [...sec.querySelectorAll('img, video')].filter(vis).slice(0, 24).map((m) => { const r = box(m); const cs = getComputedStyle(m); return { ...r, ar: +(r.w / Math.max(r.h, 1)).toFixed(2), fit: cs.objectFit, filter: cs.filter, transition: cs.transition.slice(0, 60), tag: m.tagName }; });
    return { i, tag: sec.tagName, cls: (sec.className && sec.className.baseVal === undefined ? sec.className : '').toString().slice(0, 80), ...b, bg: bg(sec), heads, paras, links, imgs };
  });
}"""


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    url, name = sys.argv[2], sys.argv[3]
    widths = [int(w) for w in (sys.argv[sys.argv.index("--widths") + 1] if "--widths" in sys.argv else "1440,390").split(",")]
    with sync_playwright() as p:
        b = pw.launch(p)
        for w in widths:
            ctx = b.new_context(viewport={"width": w, "height": 900 if w > 600 else 844}, is_mobile=w < 600, has_touch=w < 600,
                                user_agent=None)
            pg = ctx.new_page()
            pg.add_init_script("try { sessionStorage.setItem('riya-bubble', '1'); sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
            pg.goto(url, wait_until="networkidle", timeout=90000)
            pg.wait_for_timeout(1500)
            # Close cookie or newsletter pop-ups if any, then scroll the whole page for real
            for sel in ["button:has-text('Accept')", "button:has-text('Close')", "[aria-label='Close']"]:
                try:
                    pg.locator(sel).first.click(timeout=800)
                except Exception:
                    pass
            h = pg.evaluate("document.body.scrollHeight")
            for y in range(0, h + 900, 450):
                pg.mouse.wheel(0, 450); pg.wait_for_timeout(120)
            pg.wait_for_timeout(1500)
            pg.evaluate("window.scrollTo(0, 0)"); pg.wait_for_timeout(800)
            data = pg.evaluate(JS)
            (out / f"{name}-{w}.json").write_text(json.dumps({"url": url, "width": w, "height": pg.evaluate("document.body.scrollHeight"), "sections": data}, indent=1), encoding="utf-8")
            pg.add_style_tag(content=".riya-bubble{display:none!important} .reveal{opacity:1!important;transform:none!important} picture.fill img{opacity:1!important}")
            pg.screenshot(path=str(out / f"{name}-{w}-full.png"), full_page=True)
            print(f"{name} {w}: {len(data)} sections, page {pg.evaluate('document.body.scrollHeight')}px")
            for s in data:
                print(f"  s{s['i']:02d} y={s['y']:>6} h={s['h']:>5} {s['tag']:<8} {s['cls'][:40]:<40} bg={s['bg'][:22]:<22} imgs={len(s['imgs'])} "
                      + "; ".join(f"{h['tag']} '{h['text'][:40]}' {h['align']}" for h in s['heads'][:2]))
            ctx.close()
        b.close()


if __name__ == "__main__":
    main()
