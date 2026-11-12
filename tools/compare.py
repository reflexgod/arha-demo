"""Screenshot the built site (dist/) and place each page next to its reference capture.

Usage:  .venv/Scripts/python -I tools/compare.py [page ...]

Reference captures live in review/compare/reference/<stem>-<width>.png (git-ignored, made in Phase 1).
Output: review/compare/v5/<page>-<width>.png (our page) and review/compare/<page>-<width>.png (side by side,
reference left, v5 right), plus a "-top" version of the first 2200 px for quick review.
"""
import functools
import http.server
import socketserver
import sys
import threading
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
OUT = ROOT / "review" / "compare"
REF = OUT / "reference"
PORT = 8765

# our page -> (url path, reference capture stem)
PAGES = {
    "home": ("/", "home"),
    "dental-implants": ("/treatments/dental-implants/", "dental-implants"),
    "fmr": ("/treatments/crowns-bridges-full-mouth-rehabilitation/", "dental-implants"),
    "root-canal": ("/treatments/root-canal-treatment/", "dental-implants"),
    "kids": ("/treatments/kids-dentistry/", "dental-implants"),
    "the-practice": ("/the-practice/", "the-practice"),
    "contact": ("/contact/", "contact"),
    "dentures": ("/treatments/dentures/", "dental-implants"),
    "missing-teeth": ("/treatments/missing-teeth/", "dental-implants"),
    "teeth-whitening": ("/treatments/teeth-whitening/", "teeth-whitening"),
    "smile-design": ("/treatments/smile-design/", "dental-implants"),
    "gum-care": ("/treatments/gum-care/", "dental-implants"),
    "aligners": ("/treatments/aligners/", "dental-implants"),
    "emergency": ("/treatments/emergency-dentistry/", "dental-implants"),
    "treatments": ("/treatments/", "treatments"),
    "for-patients": ("/for-patients/", "for-patients"),
    "referrals": ("/referrals/", "dental-referrals"),
    "policy-complaints": ("/policies/complaints/", "policy-complaints-policy"),
    "policy-privacy": ("/policies/privacy/", "policy-website-patient-privacy-notice"),
    "policy-terms": ("/policies/terms/", "policy-website-terms-of-use"),
    "policy-cookies": ("/policies/cookies/", "policy-cookie-policy"),
    "policy-accessibility": ("/policies/accessibility/", "policy-accessibility-statement"),
    "404": ("/404.html", None),
}
WIDTHS = {1440: 900, 390: 844}


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    handler.log_message = lambda *a, **k: None
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def shoot(page, path, out):
    page.goto(f"http://127.0.0.1:{PORT}{path}", wait_until="load")
    # scroll through so lazy images, the map and in-view videos load, then return to the top
    h = page.evaluate("document.documentElement.scrollHeight")
    for y in range(0, h, 600):
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(120)
    page.wait_for_timeout(2500)  # map embed
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1200)
    page.screenshot(path=str(out), full_page=True)


def label(img, text):
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        f = ImageFont.load_default()
    d.rectangle([0, 0, 16 + 12 * len(text), 36], fill=(220, 40, 40))
    d.text((8, 6), text, fill="white", font=f)


def side_by_side(ref, ours, out, scale):
    a = Image.open(ref).convert("RGB") if ref and ref.exists() else None
    b = Image.open(ours).convert("RGB")
    w = b.width
    if a and a.width != w:
        a = a.resize((w, round(a.height * w / a.width)))
    gap = 24
    H = max(b.height, a.height if a else 0)
    canvas = Image.new("RGB", (w * 2 + gap, H), (255, 0, 255))
    if a:
        canvas.paste(a, (0, 0)); label(canvas, "reference")
    canvas.paste(b, (w + gap, 0))
    d = ImageDraw.Draw(canvas)
    d.rectangle([w + gap, 0, w + gap + 70, 36], fill=(40, 120, 40))
    d.text((w + gap + 8, 6), "v5", fill="white")
    if scale != 1:
        canvas = canvas.resize((round(canvas.width * scale), round(canvas.height * scale)), Image.LANCZOS)
    canvas.save(out, optimize=True)
    top = canvas.crop((0, 0, canvas.width, min(canvas.height, round(2200 * scale))))
    top.save(out.with_name(out.stem + "-top.png"), optimize=True)


def main():
    names = sys.argv[1:] or list(PAGES)
    (OUT / "v5").mkdir(parents=True, exist_ok=True)
    httpd = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            for width, height in WIDTHS.items():
                ctx = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1,
                                          is_mobile=width < 500, has_touch=width < 500)
                page = ctx.new_page()
                for name in names:
                    path, ref = PAGES[name]
                    ours = OUT / "v5" / f"{name}-{width}.png"
                    shoot(page, path, ours)
                    side_by_side(REF / f"{ref}-{width}.png" if ref else None, ours, OUT / f"{name}-{width}.png",
                                 0.5 if width > 500 else 1)
                    print("shot", name, width)
                ctx.close()
            browser.close()
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()
