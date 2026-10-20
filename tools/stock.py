"""Demo stock imagery (Unsplash, free licence): download, export responsive sets, write credits.md.

Usage: .venv/Scripts/python -I tools/stock.py <results.json from the Unsplash search>
Originals go to src-assets/stock/, outputs to assets/img/stock-<name>-<w>.{avif,webp,jpg}.
Stock is for the demo only and is never presented as Arha's patients, cases or doctors.
"""
import json
import sys
import urllib.request
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from photos import export  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src-assets" / "stock"

# name -> (search key, index in that search, use on the page)
PICKS = {
    "crowns": ("shade", 5, "Pillar: A legacy since 1980"),
    "gloved-hands": ("hands", 4, "Pillar: Specialist precision"),
    "natural-smile": ("teeth", 11, "Pillar: Designed for you"),
    "smile-1": ("teeth", 0, "Before & After sample tile"),
    "smile-2": ("teeth", 2, "Before & After sample tile"),
    "smile-3": ("teeth", 9, "Before & After sample tile"),
    "smile-4": ("teeth", 5, "Before & After sample tile"),
    "smile-5": ("teeth", 3, "Before & After sample tile"),
    "smile-6": ("teeth", 6, "Before & After sample tile"),
    "consultation": ("consult", 3, "Journey: Consultation"),
    "patient-chair": ("consult", 6, "Journey: Your treatment"),
    "smiling-patient": ("chair", 11, "Journey: Lifelong care"),
    "dentist-hands": ("hands", 8, "Meet the doctor (background, no face)"),
    "portrait-1": ("faces2", 9, "Reviews masonry"),
    "portrait-2": ("faces", 3, "Reviews masonry"),
    "portrait-3": ("teeth", 4, "Reviews masonry"),
}


def main():
    results = json.loads(Path(sys.argv[1]).read_text())
    picks = PICKS
    extra = [a for a in sys.argv[2:] if "=" in a]
    if extra:  # e.g. implant-hero=l_implant:3:"Implants page hero": process only these, append credits
        picks = {}
        for arg in extra:
            name, spec = arg.split("=", 1)
            key, idx, use = spec.split(":", 2)
            picks[name] = (key, int(idx), use)
    SRC.mkdir(parents=True, exist_ok=True)
    credits = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True, args=["--disable-blink-features=AutomationControlled"])
        pg = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36").new_page()
        for name, (key, idx, use) in picks.items():
            item = results[key][idx]
            src = SRC / f"{name}.jpg"
            if not src.exists():
                req = urllib.request.Request(item["raw"] + "?w=2400&q=85&fm=jpg", headers={"User-Agent": "Mozilla/5.0"})
                src.write_bytes(urllib.request.urlopen(req, timeout=60).read())
            pg.goto(item["page"], wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(1500)
            # Photographer = first profile link with a display name
            author = pg.evaluate("""() => {
              const a = [...document.querySelectorAll('a[href^="/@"]')].find(x => x.textContent.trim() && !x.textContent.trim().startsWith('/@'));
              if (!a) return 'Unknown';
              const href = a.getAttribute('href');
              return a.textContent.trim().split(' /@')[0].replace(href.slice(2), '').trim() + ' (https://unsplash.com' + href + ')';
            }""")
            im = Image.open(src).convert("RGB")
            files, size = export(im, f"stock-{name}")
            credits.append((name, use, author, item["page"]))
            print(f"{name:<16} {size[0]}x{size[1]}  {author:<24} 1280: {files.get(1280)}")
        b.close()
    if extra:
        credits_md = ROOT / "credits.md"
        text = credits_md.read_text(encoding="utf-8")
        rows = "".join(f"| `assets/img/stock-{n}-*` | {u} | {a} | {pg_url} |\n" for n, u, a, pg_url in credits if f"stock-{n}-*" not in text)
        credits_md.write_text(text.replace("\n## Video:", "\n" + rows + "\n## Video:", 1) if rows else text, encoding="utf-8")
        return
    lines = ["# Image and video credits (demo only)", "",
             "Stock media is used in this demo **only as placeholders**: it is not Arha's clinic, patients,",
             "cases or doctors, and must be replaced before launch. Not linked from the site.", "",
             "## Photos: Unsplash (Unsplash License)", "", "| File | Used for | Photographer | Source |", "|---|---|---|---|"]
    lines += [f"| `assets/img/stock-{n}-*` | {u} | {a} | {pg_url} |" for n, u, a, pg_url in credits]
    lines += ["", "## Video: Pexels (Pexels License)", "",
              "| File | Used for | Source |", "|---|---|---|",
              "| `assets/video/hero-city-*` (shot 1) | Hero loop: Mumbai skyline across the bay | https://www.pexels.com/video/majestic-mumbai-skyline-across-ocean-39648416/ |",
              "| `assets/video/hero-city-*` (shot 2) | Hero loop: Marine Drive | https://www.pexels.com/video/mumbai-skyline-view-from-marine-drive-31000790/ |",
              "", "## Arha's own assets (kept)", "",
              "Clinic photos supplied by the clinic: \"A clinic built around calm\" (reception), \"Visiting Mumbai\" (door sign), Visit section.",
              "Fonts: D-DIN (Datto, SIL OFL 1.1), Jost (indestructible type*, SIL OFL 1.1).", ""]
    (ROOT / "credits.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
