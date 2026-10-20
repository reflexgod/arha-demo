"""Write the Before & After tiles + lightbox data into the pages (between <!-- cases:start/end -->).

Usage: .venv/Scripts/python -I tools/cases_markup.py
Edit CASES below, then re-run. Each case needs an image set in assets/img (from photos.py / cases.py).
Fields per case:
  img      smile close-up image set (required)      face     full-face frame of the same patient (optional)
  before   real "before" image -> drag comparison slider (optional; never faked)
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

# Sample cases: stock images (credits.md), clearly marked SAMPLE everywhere they appear.
DOCTOR = "Dr. Nikhil V. Jain"
CASES = [
    {"img": "stock-case-1", "face": "stock-case-1-face", "cat": "implants", "meta": "Sample case · 3 visits · 4 months", "sample": True, "doctor": DOCTOR},
    {"img": "stock-case-2", "face": "stock-case-2-face", "cat": "veneers", "meta": "Sample case · 3 visits · 3 weeks", "sample": True, "doctor": DOCTOR},
    {"img": "stock-case-3", "face": "stock-case-3-face", "cat": "full-mouth", "meta": "Sample case · 6 visits · 5 months", "sample": True, "doctor": DOCTOR},
    {"img": "stock-case-4", "face": "stock-case-4-face", "cat": "aligners", "meta": "Sample case · 8 visits · 9 months", "sample": True, "doctor": DOCTOR},
    {"img": "stock-case-5", "cat": "implants", "meta": "Sample case · 4 visits · 5 months", "sample": True, "doctor": DOCTOR},
    {"img": "stock-case-6", "face": "stock-case-6-face", "cat": "veneers", "meta": "Sample case · 2 visits · 2 weeks", "sample": True, "doctor": DOCTOR},
    # Real case template (needs written patient consent before publishing):
    # {"img": "case-implant-01", "face": "case-implant-01-face", "before": "case-implant-01-before", "cat": "implants",
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
        pic = picture(c["img"], sizes, "", eager=eager, indent="          ").replace('="assets/', f'="{prefix}assets/').replace(", assets/", f", {prefix}assets/")
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
    cls = "cases cases--featured" if featured else "cases"
    return (f'<!-- cases:start (generated by tools/cases_markup.py) -->\n    <ul class="{cls}" data-cases>\n' + "\n".join(tiles) +
            "\n    </ul>\n    <script type=\"application/json\" id=\"case-data\">" + json.dumps(data, ensure_ascii=False) +
            "</script>\n    <!-- cases:end -->")


def filters():
    buttons = "\n".join(f'            <button type="button" data-filter="{k}" aria-pressed="{str(k == "all").lower()}">{v}</button>' for k, v in FILTERS)
    return f"<!-- filters:start -->\n{buttons}\n            <!-- filters:end -->"


def main():
    pages = [(ROOT / "index.html", "", True, None),
             (ROOT / "before-after" / "index.html", "../", False, None),
             (ROOT / "dental-implants" / "index.html", "../", False, "implants")]
    for page, prefix, featured, only in pages:
        if not page.exists():
            continue
        s = page.read_text(encoding="utf-8")
        s = re.sub(r"<!-- cases:start.*?<!-- cases:end -->", lambda m: render(prefix, featured, only), s, flags=re.S)
        s = re.sub(r"<!-- filters:start -->.*?<!-- filters:end -->", lambda m: filters(), s, flags=re.S)
        page.write_text(s, encoding="utf-8")
        print("updated", page.relative_to(ROOT))


if __name__ == "__main__":
    main()
