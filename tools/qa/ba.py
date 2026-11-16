"""Before/after element screenshots of every changed section, desktop 1440 + mobile 390.
Usage: python ba.py OUTDIR [section keys...]   (before = :8091, after = :8090)"""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\viraa\IdeaProjects\arha demo\tools\qa")
from PIL import Image  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
BEFORE, AFTER = "http://localhost:8091", "http://localhost:8090"
T = "/treatments/"
SECTIONS = [
    ("home-cards", "Home: treatment cards", "/", "section.cards"),
    ("home-team", "Home: dentist cards", "/", "section.team"),
    ("blog-listing", "Blog: listing, filter and cards", "/blog/", "section.blogidx"),
    ("post-top", "Blog post: hero image and meta line", "/blog/when-should-a-child-first-see-a-dentist/", "main > section:first-of-type"),
    ("post-rct", "Blog post: root canal, hero image", "/blog/is-root-canal-treatment-painful/", "main > section:first-of-type"),
    ("post-related", "Blog post: related treatments", "/blog/dental-implant-timeline/", "section.relt"),
    ("post-more", "Blog post: more from the blog", "/blog/dental-implant-timeline/", "section.morepost"),
    ("doctor-articles", "Dr. Nikhil's profile: articles", "/doctors/dr-nikhil-v-jain/", "section.morepost"),
    ("hub-implants", "Treatments hub: implants and rehabilitation", T, "section.hubcat:nth-of-type(1)"),
] + [(f"hero-{s}", f"Treatment page hero: {s.replace('-', ' ')}", f"{T}{s}/", "main > section:first-of-type") for s in
     "dental-implants crowns-bridges-full-mouth-rehabilitation root-canal-treatment kids-dentistry dentures missing-teeth "
     "teeth-whitening smile-design gum-care aligners childrens-orthodontics".split()] + [
    (f"cta-{s}", f"Treatment page side card: {s.replace('-', ' ')}", f"{T}{s}/", ".ctacard") for s in
    "dental-implants crowns-bridges-full-mouth-rehabilitation root-canal-treatment kids-dentistry dentures missing-teeth "
    "teeth-whitening smile-design gum-care emergency-dentistry".split()]
# hub sections are siblings of other sections, so pick them by index among .hubcat
HUB = [("hub-" + k, f"Treatments hub: {k}", T, i) for i, k in enumerate(["implants", "restorative", "cosmetic", "children", "general"])]

PREP = """async () => {
  document.querySelectorAll('img[loading=lazy]').forEach((i) => { i.loading = 'eager'; });
  for (let y = 0; y < document.body.scrollHeight; y += 700) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 30)); }
  window.scrollTo(0, 0);
  document.querySelectorAll('[data-reveal]').forEach((el) => el.classList.add('rv', 'is-in'));
  await Promise.all([...document.images].map((i) => i.decode().catch(() => {})));
  await new Promise((r) => setTimeout(r, 300));
}"""
CSS = "[data-reveal]{opacity:1!important;transform:none!important;transition:none!important} .cookie,.cookies,#cookie,.callbar{display:none!important}"


def shot(pg, base, path, sel, idx, f):
    pg.goto(base + path, wait_until="networkidle")
    pg.add_style_tag(content=CSS)
    pg.evaluate(PREP)
    loc = pg.locator(sel)
    if loc.count() == 0:
        return False
    el = loc.nth(idx) if idx is not None else loc.first
    el.scroll_into_view_if_needed()
    pg.wait_for_timeout(150)
    el.screenshot(path=str(f), animations="disabled")
    im = Image.open(f)
    if im.height > 3200:  # keep very long sections readable
        im.crop((0, 0, im.width, 3200)).save(f)
    return True


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    items = [(k, lab, p, s, None) for k, lab, p, s in SECTIONS if not k.startswith("hub-")]
    items += [(k, lab, p, "section.hubcat", i) for k, lab, p, i in HUB]
    only = sys.argv[2:]  # optional section keys: capture just these, in this order
    if only:
        items = [next(it for it in items if it[0] == k) for k in only]
    index = []
    with sync_playwright() as p:
        b = pw.launch(p)
        for w in (1440, 390):
            ctx = b.new_context(viewport={"width": w, "height": 900 if w > 600 else 844}, device_scale_factor=1)
            ctx.add_init_script("try{localStorage.setItem('arha-consent', JSON.stringify({analytics:false,ts:1}));}catch(e){}")
            pg = ctx.new_page()
            for k, lab, path, sel, idx in items:
                fb, fa = out / f"{k}-{w}-before.png", out / f"{k}-{w}-after.png"
                ok = shot(pg, BEFORE, path, sel, idx, fb) and shot(pg, AFTER, path, sel, idx, fa)
                if ok:
                    for f in (fb, fa):  # jpeg, smaller for the review page
                        Image.open(f).convert("RGB").save(f.with_suffix(".jpg"), quality=80, optimize=True)
                    index.append({"key": k, "label": lab, "path": path, "w": w})
                print(w, k, "ok" if ok else "MISSING")
            ctx.close()
        b.close()
    (out / "index.json").write_text(json.dumps(index, indent=1))


if __name__ == "__main__":
    main()
