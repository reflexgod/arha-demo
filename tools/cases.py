"""Sample before/after tiles: six stock smiles cropped to one identical framing (demo only).

Usage: .venv/Scripts/python -I tools/cases.py <unsplash results.json for the c* candidates>
Framing: 4:5, lips centred horizontally at 45% of the height, mouth = 66% of the crop width.
Mouth boxes (centre x, centre y, width; fractions of the source) were measured by eye.
Outputs assets/img/stock-case-<n>-<w>.* and the "Before & After samples" rows of credits.md.
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from photos import export  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MOUTH_FRACTION, LIPS_AT = 0.66, 0.45

# case n: (source file, search key in results.json or None, (cx, cy, w))
CASES = {
    1: ("cand/c9.jpg", "c9", (0.70, 0.42, 0.44)),   # featured on the homepage
    2: ("cand/c5.jpg", "c5", (0.62, 0.37, 0.37)),
    3: ("cand/c8.jpg", "c8", (0.52, 0.48, 0.65)),
    4: ("cand/c4.jpg", "c4", (0.72, 0.47, 0.37)),
    5: ("cand/c2.jpg", "c2", (0.52, 0.51, 0.85)),  # mouth wider than 66%: source cannot zoom out further
    6: ("cand/c6.jpg", "c6", (0.49, 0.595, 0.17)),
}

# Cases whose photograph also shows the whole face (case 5 is a lower-face shot only)
FACES = {1, 2, 3, 4, 6}


def crop(im, cx, cy, w, mouth=MOUTH_FRACTION, lips_at=LIPS_AT):
    W, H = im.size
    cw = min(w * W / mouth, W, H * 4 / 5)  # never crop outside the photograph
    ch = cw * 5 / 4
    left = min(max(cx * W - cw / 2, 0), W - cw)
    top = min(max(cy * H - ch * lips_at, 0), H - ch)
    return im.crop((round(left), round(top), round(left + cw), round(top + ch)))


def main():
    meta = json.loads(Path(sys.argv[1]).read_text())
    rows = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True, args=["--disable-blink-features=AutomationControlled"])
        pg = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36").new_page()
        for n, (src, key, box) in CASES.items():
            im = crop(Image.open(ROOT / "src-assets" / "stock" / src).convert("RGB"), *box)
            if im.width < 800:  # small source mouth: gentle upscale so every case has a 640w file
                im = im.resize((800, 1000), Image.LANCZOS)
            files, size = export(im, f"stock-case-{n}")
            if n in FACES:  # full-face frame from the same photograph (same 4:5, mouth ~28% of the width)
                face = crop(Image.open(ROOT / "src-assets" / "stock" / src).convert("RGB"), *box, mouth=0.28, lips_at=0.70)
                if face.width < 800:
                    face = face.resize((800, 1000), Image.LANCZOS)
                export(face, f"stock-case-{n}-face")
            page_url = meta[key]["page"] if key else None
            author = "Lesly Juarez (https://unsplash.com/@jblesly)"  # smile-5, see credits above
            if page_url:
                pg.goto(page_url, wait_until="domcontentloaded", timeout=60000)
                pg.wait_for_timeout(1500)
                author = pg.evaluate("""() => {
                  const a = [...document.querySelectorAll('a[href^="/@"]')].find(x => x.textContent.trim() && !x.textContent.trim().startsWith('/@'));
                  if (!a) return 'Unknown';
                  const href = a.getAttribute('href');
                  return a.textContent.trim().split(' /@')[0].replace(href.slice(2), '').trim() + ' (https://unsplash.com' + href + ')';
                }""")
            else:
                page_url = "see smile-5 above"
            rows.append(f"| `assets/img/stock-case-{n}-*` | Before & After sample tile | {author} | {page_url} |")
            print(n, size, author)
        b.close()
    credits = ROOT / "credits.md"
    text = credits.read_text(encoding="utf-8")
    text = re.sub(r"\| `assets/img/stock-smile-[1-46]-\*` \|[^\n]*\n", "", text)  # retired sample tiles
    text = text.replace("| `assets/img/stock-smile-5-*` | Before & After sample tile |", "| `src-assets/stock/smile-5.jpg` (source of case 5) | Before & After sample tile |")
    text = re.sub(r"\| `assets/img/stock-case-[^\n]*\n", "", text)
    text = text.replace("\n## Video:", "\n" + "\n".join(rows) + "\n\n## Video:", 1)
    text = text.replace("| `assets/img/stock-portrait-", "| (retired) `assets/img/stock-portrait-")
    credits.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
