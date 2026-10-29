"""Write the Before & After tiles + lightbox data into the pages (between <!-- cases:start/end -->).

Usage: .venv/Scripts/python -I tools/cases_markup.py   (fills every page with a cases:start marker)
Edit CASES below, then re-run. Each case needs an image set in assets/img (from photos.py / cases.py).
Fields per case:
  img      smile close-up image set (required)      face     full-face frame of the same patient (optional)
  before   the "before" image of the pair (sample cases: tools/pairs.py; real cases need written consent)
  cat, meta, story (concern, plan, result), looks, works, note (doctor's one-line note)
  doctor   who treated the case: shown only on real cases
  days, city   "Completed in X days · visiting from CITY": shown only on real cases with both values
  sample   True for the demo stock; sample cases are marked SAMPLE and never show doctor/days/city.
Never publish a case without the patient's written consent, and never fake a "before" image.
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from picture import picture  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
FILTERS = [("all", "All"), ("implants", "Implants"), ("full-mouth", "Full mouth"), ("veneers", "Veneers"), ("aligners", "Aligners")]

STORIES = {
    "implants": ("A missing tooth had made eating on one side uncomfortable.",
                 "A single implant planned from 3D scans, with a crown designed to match the neighbouring teeth.",
                 "A tooth that looks, feels and functions like the patient’s own."),
    "full-mouth": ("Worn and missing teeth were making chewing difficult and the smile look older.",
                   "A staged plan rebuilding the bite step by step, with comfort checked at every visit.",
                   "An even, comfortable bite and a smile in proportion with the face."),
    "veneers": ("Uneven, worn front teeth the patient had become self-conscious about.",
                "A smile designed around the face first and previewed before any treatment, then thin porcelain veneers.",
                "A brighter, balanced smile that still looks entirely natural."),
    "aligners": ("Crowded lower teeth that were difficult to keep clean.",
                 "Clear aligners planned digitally, with short reviews along the way.",
                 "Straighter teeth and easier daily care, without fixed braces."),
}
# Placeholder "Looks / Works" lines and doctor's notes for sample cases (Arha voice, no clinical claims)
SAMPLE_COPY = {
    "implants": ("In proportion with the neighbouring teeth; no one can tell which tooth is new.",
                 "Comfortable bite and normal chewing on both sides, built to last with routine care.",
                 "The aim is a tooth nobody notices, including the patient."),
    "full-mouth": ("Balanced proportions that suit the face, not just the teeth.",
                   "An even bite, comfortable chewing and a plan designed to last for years.",
                   "We rebuild the bite first; the smile follows from it."),
    "veneers": ("Natural shade and shape: brighter, never artificial.",
                "Normal bite and chewing, with thin porcelain that protects the tooth beneath.",
                "Less is usually more. The best veneers look like the patient on a good day."),
    "aligners": ("A straighter, softer smile line with no visible brackets.",
                 "Teeth that are easier to clean, with a bite that closes evenly.",
                 "Straight teeth matter, but a healthy, even bite matters more."),
}

NAMES = {"implants": "Dental implants", "full-mouth": "Full mouth rehabilitation",
         "veneers": "Smile design & veneers", "aligners": "Invisalign & aligners"}

# Sample cases: stock images (notes/credits.md, local only), clearly marked SAMPLE everywhere they appear.
DOCTOR = "Dr. Nikhil V. Jain"
SAMPLE = "Sample case for demo"
# Sample cases (v4 fixes 3, point 2). A before/after slider only for a same-photograph simulation
# (tools/pairs.py, "Simulation for demo"); the others show a clinical-detail photograph and the story.
# card: the photograph on the homepage and Our work cards (and the large one on a case page without a slider).
CASES = [
    {"img": "stock-pair-1-after", "before": "stock-pair-1-before", "cat": "veneers", "meta": "Smile design · a lighter, even shade",
     "card": "stock-pair-1-after", "card_alt": "A natural smile after a subtle shade change (simulation for demo)", "card_pos": "55% 50%", "sample": True, "doctor": DOCTOR},
    {"img": "stock-implant-models", "cat": "implants", "meta": "Implants · replacing a missing tooth",
     "card": "stock-implant-models", "card_alt": "Implant models: crowns on titanium posts in a model of the jaw", "card_pos": "50% 50%", "sample": True, "doctor": DOCTOR},
    {"img": "stock-restorations-set", "cat": "full-mouth", "meta": "Full mouth · an even, rebuilt bite",
     "card": "stock-restorations-set", "card_alt": "A full set of restorations on a dental model", "card_pos": "50% 50%", "sample": True, "doctor": DOCTOR},
    {"img": "stock-aligner-model", "cat": "aligners", "meta": "Aligners · straightening crowded teeth",
     "card": "stock-aligner-model", "card_alt": "A clear aligner above a model of the teeth", "card_pos": "50% 45%", "sample": True, "doctor": DOCTOR},
    # Real case template (needs written patient consent before publishing):
    # {"img": "case-implant-01", "before": "case-implant-01-before", "card": "case-implant-01", "cat": "implants",
    #  "meta": "4 visits · 5 months", "story": ("…", "…", "…"), "looks": "…", "works": "…", "note": "…",
    #  "doctor": DOCTOR, "days": 6, "city": "London", "sample": False},
]


def largest(name, ext, cap=1280):
    widths = sorted(int(m.group(1)) for p in IMG.glob(f"{name}-*.jpg") if (m := re.fullmatch(rf"{re.escape(name)}-(\d+)\.jpg", p.name)))
    w = max([x for x in widths if x <= cap] or widths[:1])
    return f"assets/img/{name}-{w}.{ext}"


def render(prefix, featured, only=None):
    tiles, data = [], []
    for i, c in enumerate([c for c in CASES if not only or c["cat"] == only]):
        name = NAMES[c["cat"]]
        sizes = "(min-width: 768px) 700px, 100vw" if featured and i == 0 else "(min-width: 768px) 340px, 50vw"
        # Results page: the first row is above the fold, so load it eagerly at high priority (LCP)
        eager = not featured and not only and i < 3
        pic = picture(c["img"], sizes, "", eager=eager, pos=c.get("pos"), indent="          ").replace('="assets/', f'="{prefix}assets/').replace(", assets/", f", {prefix}assets/")
        tiles.append(f"""      <li class="case-item reveal" data-cat="{c['cat']}">
        <button class="case" type="button" data-case="{i}">
          <span class="case__media">
{pic}
            <span class="case__panel">
              <span class="case__name">{html.escape(name)}</span>
              <span class="case__meta">{html.escape(c['meta'])}</span>
              <span class="case__view">View case</span>
            </span>
          </span>
          <span class="case__caption">
            <span class="case__name">{html.escape(name)}{'<span class="visually-hidden"> (sample case)</span>' if c['sample'] else ''}</span>
            <span class="case__view">View case</span>
          </span>
        </button>
      </li>""")
        concern, plan, result = c.get("story") or STORIES[c["cat"]]
        looks, works, note = (c.get("looks"), c.get("works"), c.get("note"))
        if c["sample"]:
            looks, works, note = SAMPLE_COPY[c["cat"]]
        real = not c["sample"]
        imgset = lambda key: {ext: prefix + largest(c[key], ext) for ext in ("avif", "webp", "jpg")} if c.get(key) else None  # noqa: E731
        data.append({"name": name, "meta": c["meta"], "sample": c["sample"], "concern": concern, "plan": plan, "result": result,
                     "looks": looks, "works": works, "note": note,
                     # Shown only for real cases: who treated it, and the visiting-patient tag
                     "doctor": c.get("doctor") if real else None,
                     "visit": (f"Completed in {c['days']} days · visiting from {c['city']}" if real and c.get("days") and c.get("city") else None),
                     "after": imgset("img"), "face": imgset("face"), "before": imgset("before")})
    start = f'<!-- cases:start{f" only={only}" if only else ""} (generated by tools/cases_markup.py) -->'
    if not tiles:  # no cases for this treatment yet
        return start + '\n    <p class="cases-empty">Cases for this treatment will appear here once patients have given their consent.</p>\n    <!-- cases:end -->'
    cls = "cases cases--featured" if featured else "cases"
    return (start + f'\n    <ul class="{cls}" data-cases>\n' + "\n".join(tiles) +
            "\n    </ul>\n    <script type=\"application/json\" id=\"case-data\">" + json.dumps(data, ensure_ascii=False) +
            "</script>\n    <!-- cases:end -->")


def filters():
    buttons = "\n".join(f'            <button type="button" data-filter="{k}" aria-pressed="{str(k == "all").lower()}">{v}</button>' for k, v in FILTERS)
    return f"<!-- filters:start -->\n{buttons}\n            <!-- filters:end -->"


def slugs():
    """The case page of each case: our-work/sample-<category>-<n>/ (as tools/more_pages.py builds them)."""
    count, out = {}, []
    for c in CASES:
        count[c["cat"]] = count.get(c["cat"], 0) + 1
        out.append(f"{'sample' if c['sample'] else 'case'}-{c['cat']}-{count[c['cat']]}")
    return out


def pairs(prefix):
    """Homepage: large image pairs side by side (smile close-up and full face of the same case), each with
    "See the full case". Only cases that have both photographs; never a faked before/after."""
    items = []
    for c, slug in zip(CASES, slugs()):
        if not c.get("face"):
            continue
        name = NAMES[c["cat"]]
        pic = lambda n, alt: picture(n, "(min-width: 900px) 24vw, 50vw", alt, pos=c.get("pos"), indent="              ").replace('="assets/', f'="{prefix}assets/').replace(", assets/", f", {prefix}assets/")  # noqa: E731
        label = "Sample image for the demo" if c["sample"] else name
        items.append(f"""      <li class="pair reveal">
        <a href="{prefix}our-work/{slug}/">
          <span class="pair__images">
            <span class="pair__img media media--hover">
{pic(c['img'], f'{label}: smile')}
            </span>
            <span class="pair__img media media--hover">
{pic(c['face'], f'{label}: full face')}
            </span>
          </span>
          <span class="pair__name">{html.escape(name)}</span>
          <span class="pair__meta">{'Sample case · ' if c['sample'] else ''}{html.escape(c['meta'].replace('Sample case · ', ''))}</span>
          <span class="cta">See the full case</span>
        </a>
      </li>""")
    return ("<!-- pairs:start (generated by tools/cases_markup.py) -->\n    <ul class=\"pairs\">\n" + "\n".join(items)
            + "\n    </ul>\n    <!-- pairs:end -->")


def main():
    """Every built page with a cases block. A block can narrow itself to one category,
    <!-- cases:start only=implants -->; the homepage's first case is the large featured tile.
    The homepage's <!-- pairs:start --> block shows large smile + face pairs instead."""
    for page in [ROOT / "index.html", *sorted(ROOT.glob("*/index.html")), *sorted(ROOT.glob("*/*/index.html"))]:
        s = page.read_text(encoding="utf-8")
        if "<!-- cases:start" not in s and "<!-- pairs:start" not in s:
            continue
        prefix = "../" * (len(page.relative_to(ROOT).parts) - 1)
        featured = page.parent == ROOT
        s = re.sub(r"<!-- pairs:start.*?<!-- pairs:end -->", lambda m: pairs(prefix), s, flags=re.S)
        s = re.sub(r"<!-- cases:start(?: only=([\w-]+))?.*?<!-- cases:end -->",
                   lambda m: render(prefix, featured, m.group(1)), s, flags=re.S)
        s = re.sub(r"<!-- filters:start -->.*?<!-- filters:end -->", lambda m: filters(), s, flags=re.S)
        page.write_text(s, encoding="utf-8", newline="\n")
        print("updated", page.relative_to(ROOT))


if __name__ == "__main__":
    main()
