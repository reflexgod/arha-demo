"""Hero readability over the video (7 Nov 2026): screenshots of the homepage hero at 375, 1024 and 1440 px on chosen
video moments, and WCAG contrast of each text element against the pixels right behind it.

For every width and moment the clinic walkthrough is forced in (phones only ever show the poster; forcing the video
there tests the worst case), paused on the frame, and shot twice: as seen, and with the words hidden, so the
background (video + overlay) can be measured inside each element's box. Contrast is taken against the 95th-percentile
brightest background pixel and against the single brightest one (text-shadow ignored, so the figures are conservative).

Run (server on 8080):  .venv/Scripts/python -I tools/qa/hero_frames.py review/clean/hero 0,3,5.5,6
"""
import io
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from pw import launch  # noqa: E402

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "review/clean/hero")
MOMENTS = [-1.0] + [float(t) for t in (sys.argv[2] if len(sys.argv) > 2 else "0,3,5.5,6").split(",")]  # -1 = the poster
WIDTHS = [(375, 812), (1024, 768), (1440, 900)]
CREAM = (247, 243, 236)
INK = (59, 42, 32)  # --brand-deep, the primary button's text


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c[:3]
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


ELEMENTS = [  # selector, label, AA threshold, how the text sits
    (".hero-v9__kicker", "small line", 4.5, "over"),
    (".hero-v9 h1", "headline", 3.0, "over"),
    (".hero-v9__lede", "subline", 4.5, "over"),
    (".hero-v9__actions .btn:not(.btn--primary)", "secondary button", 4.5, "over"),
    (".hero-v9__actions .btn--primary", "primary button", 4.5, "solid"),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, worst = [], {}
    with sync_playwright() as p:
        b = launch(p)
        for w, h in WIDTHS:
            ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, is_mobile=w < 800, has_touch=w < 800)
            pg = ctx.new_page()
            pg.goto("http://127.0.0.1:8080/", wait_until="networkidle")
            # Each moment is the exact video frame (ffmpeg, from hero-land-1080.mp4) shown where the video plays, under the
            # same overlay: no seeking, no codec questions. "poster" is what phones and the first paint really show.
            pg.evaluate("document.querySelector('[data-hero-v9] video').style.display = 'none'")
            boxes = {sel: pg.eval_on_selector(sel, "e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }")
                     for sel, *_ in ELEMENTS if pg.query_selector(sel)}
            for t in MOMENTS:
                if t >= 0:
                    pg.evaluate("""(t) => new Promise((ok) => { const pic = document.querySelector('.hero-v9__media picture');
                        pic.querySelectorAll('source').forEach((x) => x.remove()); const img = pic.querySelector('img');
                        img.addEventListener('load', () => requestAnimationFrame(() => requestAnimationFrame(ok)), { once: true });
                        img.removeAttribute('srcset'); img.src = `review/clean/hero/frames/t${t}.jpg`; })""", ("%g" % t))
                name = f"hero-{w}-" + ("poster" if t < 0 else f"t{str(t).replace('.', '_')}")
                pg.screenshot(path=str(OUT / f"{name}.png"), clip={"x": 0, "y": 0, "width": w, "height": h})
                pg.add_style_tag(content=".hero-v9__text * { color: transparent !important; text-shadow: none !important; border-color: transparent !important; background: transparent !important; } .hero-v9__text svg { visibility: hidden; } .hero-v9__text * { box-shadow: none !important; outline: none !important; } .hero-v9__text *::before, .hero-v9__text *::after { opacity: 0 !important; } #bgprobe {}")
                bg = Image.open(io.BytesIO(pg.screenshot(clip={"x": 0, "y": 0, "width": w, "height": h}))).convert("RGB")
                bg.save(OUT / f"{name}-bg.png")
                pg.evaluate("document.querySelectorAll('style').forEach(s => { if (s.textContent.includes('#bgprobe')) s.remove(); })")
                for sel, label, need, how in ELEMENTS:
                    if sel not in boxes:
                        continue
                    if how == "solid":
                        r95 = rmax = ratio(CREAM, INK)
                    else:
                        x0, y0, x1, y1 = (max(0, int(v)) for v in boxes[sel])
                        x0, y0, x1, y1 = x0 + 3, y0 + 3, x1 - 3, y1 - 3  # inside the button's own 1 px border
                        px = sorted(bg.crop((x0, y0, min(w, x1), min(h, y1))).get_flattened_data(), key=lum)
                        r95 = ratio(CREAM, px[int(len(px) * 0.95) - 1])
                        rmax = ratio(CREAM, px[-1])
                    ok = r95 >= need
                    rows.append(f"{w:>5} {'poster' if t < 0 else f'{t:g}s':>6}  {label:<17} {r95:5.2f}:1 (95th pct)  {rmax:5.2f}:1 (brightest px)  needs {need}:1  {'PASS' if ok else 'FAIL'}")
                    key = (w, label)
                    worst[key] = min(worst.get(key, 99), r95)
            ctx.close()
        b.close()
    report = "\n".join(rows)
    (OUT / "contrast.txt").write_text(report + "\n", encoding="utf-8")
    print(report)
    print("FAILS:", sum("FAIL" in r for r in rows))


if __name__ == "__main__":
    main()
