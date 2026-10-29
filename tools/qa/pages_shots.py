"""Every page at 1440 and 390, full length, for the final visual pass (v4 fixes 3, point 5).

Usage: .venv/Scripts/python tools/qa/pages_shots.py OUTDIR [--widths 1440,390] [--only slug,slug]
Reveal animations are finished and lazy images loaded before each capture; Riya's proactive bubble is
suppressed (it is a once-a-visit prompt). Also writes OUTDIR/sheets/<width>-<n>.jpg: the pages side by side,
scaled down, to look through quickly. Server on http://127.0.0.1:8080/.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import photo_audit  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
PREP = """async () => {
  try { sessionStorage.setItem('riya-bubble', '1'); sessionStorage.setItem('arha-intro', '1'); } catch (e) {}
  document.querySelectorAll('img[loading=lazy]').forEach((i) => { i.loading = 'eager'; });
  for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 60)); }
  window.scrollTo(0, 0);
  document.querySelectorAll('.reveal').forEach((el) => el.classList.add('is-in', 'is-visible'));
  await Promise.all([...document.images].filter((i) => !i.complete).map((i) => new Promise((r) => { i.onload = i.onerror = r; })));
}"""


def url(rel):
    return pw.BASE + ("" if rel == "home" else ("404.html" if rel == "404" else rel + "/"))


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    widths = [int(w) for w in (sys.argv[sys.argv.index("--widths") + 1] if "--widths" in sys.argv else "1440,390").split(",")]
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    pages = [rel for rel, _p in photo_audit.pages() if not only or rel in only]
    with sync_playwright() as p:
        b = pw.launch(p)
        for w in widths:
            pg = b.new_page(viewport={"width": w, "height": 900 if w > 600 else 844})
            pg.add_init_script("try { sessionStorage.setItem('riya-bubble', '1'); sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
            shots = []
            for rel in pages:
                pg.goto(url(rel), wait_until="networkidle")
                pg.add_style_tag(content=".reveal{opacity:1!important;transform:none!important;transition:none!important} .riya-bubble{display:none!important} picture.fill img{opacity:1!important;transition:none!important}")
                pg.evaluate(PREP)
                pg.wait_for_timeout(300)
                f = out / f"{rel.replace('/', '_')}-{w}.png"
                pg.screenshot(path=str(f), full_page=True)
                shots.append(f)
                print(f)
            pg.close()
            sheets(out, w, shots)
        b.close()


def sheets(out, w, shots, per=6, col=300):
    (out / "sheets").mkdir(exist_ok=True)
    for n in range(0, len(shots), per):
        ims = []
        for f in shots[n:n + per]:
            im = Image.open(f).convert("RGB")
            ims.append(im.resize((col, round(im.height * col / im.width))))
        h = max(i.height for i in ims)
        s = Image.new("RGB", (col * len(ims) + 8 * (len(ims) - 1), min(h, 12000)), "white")
        for k, im in enumerate(ims):
            s.paste(im, (k * (col + 8), 0))
        s.save(out / "sheets" / f"{w}-{n // per + 1:02d}.jpg", quality=72)


if __name__ == "__main__":
    main()
