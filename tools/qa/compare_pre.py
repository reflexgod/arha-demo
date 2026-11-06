"""Before/after check for v5-clean (7 Nov 2026): full-page screenshots of the same pages on the pre-upgrade build
(port 8081, a worktree at 8c83dc1) and the current build (8080), at 375 and 1440 px, and a pixel diff of each pair.
Reduced motion is emulated on both, so slideshows and reveals hold still and the two runs are comparable.

Run:  .venv/Scripts/python -I tools/qa/compare_pre.py review/clean/compare
"""
import sys
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from pw import launch  # noqa: E402

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "review/clean/compare")
PAGES = ["", "dental-implants/", "smile-design/", "book/", "gallery/", "the-practice/"]  # the-practice = contact (#visit)
SIDES = {"before": "http://127.0.0.1:8081/", "after": "http://127.0.0.1:8080/"}


def shoot(b, base, path, w, out):
    ctx = b.new_context(viewport={"width": w, "height": 812 if w < 800 else 900}, device_scale_factor=1,
                        is_mobile=w < 800, has_touch=w < 800, reduced_motion="reduce")
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(base + path, wait_until="networkidle")
    h = pg.evaluate("document.documentElement.scrollHeight")
    for y in range(0, h, 600):
        pg.evaluate(f"window.scrollTo(0,{y})")
        pg.wait_for_timeout(40)
    pg.evaluate("window.scrollTo(0,0)")
    pg.wait_for_timeout(600)
    sw = pg.evaluate("document.documentElement.scrollWidth")
    pg.screenshot(path=str(out), full_page=True)
    ctx.close()
    return sw, errors


def main():
    rows = []
    with sync_playwright() as p:
        b = launch(p)
        for w in (375, 1440):
            for path in PAGES:
                name = (path.strip("/") or "home") + f"-{w}.png"
                info = {}
                for side, base in SIDES.items():
                    (OUT / side).mkdir(parents=True, exist_ok=True)
                    info[side] = shoot(b, base, path, w, OUT / side / name)
                a, c = (Image.open(OUT / s / name).convert("RGB") for s in SIDES)
                if a.size != c.size:
                    verdict = f"DIFFERENT SIZE {a.size} vs {c.size}"
                else:
                    box = ImageChops.difference(a, c).getbbox()
                    verdict = "identical" if box is None else f"differs in {box}"
                sw, errs = info["after"]
                rows.append(f"{name:<26} {verdict:<44} scrollWidth {sw}{'  ERRORS ' + str(errs) if errs else ''}")
        b.close()
    (OUT / "compare.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
