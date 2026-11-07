"""Which stock photograph each treatment and problem page shows (Viraaj, 7 Nov 2026).

Round 2, "rebalance" (7 Nov 2026): faces appear in four places only (FACES): the homepage "Specialist care" card (a
family at home), and the heroes of full mouth rehabilitation (grandparents with their grandchild), Invisalign (a young
woman) and kids' dentistry (a mother and daughter). Everywhere else a photograph is a close-up of a smile (lips and teeth
only) or a detail (aligner, implant model, crowns, veneers, toothbrush, dental mirror, linen); all are in
tools/people.json, graded alike. The homepage "Explore treatments" list and the treatments index use TREATMENT_ROW,
which is the page's hero except on the three pages whose hero is a face (no faces in the list).

Arha's own photographs stay only in the homepage hero, "A clinic built around calm", "Step inside", the gallery,
the "Technology & innovation" card (the real X-ray room) and the "Dr. Nikhil's clinic" card (the door sign), and on
the pages about the clinic itself (doctors, founder, the practice, technology, dental tourism). Three interactives
keep their own photograph (KEEP): the numbered parts of an implant on the implant model, the focus ring that moves
across the 3D arches on Arha's planning screen, and the magnifier over porcelain veneers.

PAGES maps a page to {photograph the builders put there: the photograph shown instead}. apply() runs on each built
page (tools/pages.py) and rebuilds each matching <picture> with the new photograph, its plain alt text (from
people.json; decorative images stay alt="") and its position, keeping sizes, loading and classes. Page heroes are the
first photograph (eager, not lazy); everything else stays lazy. No photograph appears twice on one page, and faces only
in their four places (check: tools/qa/people_check.py).
"""
import json
import re
from pathlib import Path

from picture import picture

PEOPLE = json.loads(Path(__file__).with_name("people.json").read_text(encoding="utf-8"))

# The only photographs with faces, and the one place each may appear: (page, section class, or "hero").
FACES = {"family-at-home": ("index.html", "ah-trio"), "grandparents-grandchild": ("full-mouth-rehabilitation/index.html", "hero"),
         "young-woman-at-table": ("invisalign/index.html", "hero"), "mother-daughter-laughing": ("kids-dentistry/index.html", "hero")}

# The photograph of each treatment page's hero.
TREATMENT_HERO = {
    "dental-implants": "detail-implant-hero",
    "full-mouth-rehabilitation": "grandparents-grandchild",
    "smile-design": "smile-wide",
    "invisalign": "young-woman-at-table",
    "crowns-bridges": "smile-soft",
    "cosmetic-dentistry": "smile-natural",
    "root-canal-treatment": "detail-crowns-soft",
    "orthodontics": "smile-braces",
    "general-dentistry": "detail-toothbrush",
    "kids-dentistry": "mother-daughter-laughing",
    "maxillofacial-prosthetics": "detail-prosthesis-model",
}
# The homepage "Explore treatments" rows and the treatments index: the hero, but never a face.
TREATMENT_ROW = dict(TREATMENT_HERO, **{"full-mouth-rehabilitation": "detail-restorations",
                                        "invisalign": "detail-aligners-shadow", "kids-dentistry": "detail-kids-brush"})
# The photograph of each problem page's hero; the homepage's "What brings you in?" cards and the problems index use it too.
PROBLEM_HERO = {
    "missing-tooth": "detail-bridge",
    "chipped-tooth": "detail-veneers-fabric",
    "gaps": "detail-aligners-shadow",
    "crooked-teeth": "detail-aligner",
    "stained-teeth": "detail-teeth-shades",
    "toothache": "detail-mirror",
    "bleeding-gums": "detail-floss",
    "metal-fillings": "smile-bright",
    "loose-dentures": "detail-denture",
    "child-teeth": "detail-kids-brush-wood",
}
H, R, P = TREATMENT_HERO, TREATMENT_ROW, PROBLEM_HERO

PAGES = {
    "treatments": {
        "stock-implant-arch": "detail-texture-linen",
        "stock-implant-models": R["dental-implants"], "stock-denture-tray": R["full-mouth-rehabilitation"],
        "stock-prosthesis-hands": R["maxillofacial-prosthetics"], "stock-veneer-fingertip": R["smile-design"],
        "stock-veneers-fabric": R["cosmetic-dentistry"], "stock-aligner-case-hand": R["invisalign"],
        "stock-braces-model": R["orthodontics"], "stock-scalers": R["general-dentistry"],
        "stock-steel-instruments": R["root-canal-treatment"], "stock-bridge-white": R["crowns-bridges"],
        "stock-child-chair": R["kids-dentistry"],
    },
    "problems": {
        "stock-handpieces": "detail-veneers",
        "stock-implant-crown": P["missing-tooth"], "stock-veneer-fingertip": P["chipped-tooth"],
        "stock-veneers-fabric": P["gaps"], "stock-aligner": P["crooked-teeth"], "stock-shade-guide": P["stained-teeth"],
        "stock-xray-screen": P["toothache"], "stock-floss-hand": P["bleeding-gums"],
        "stock-steel-instruments": P["metal-fillings"], "stock-denture-dark": P["loose-dentures"],
        "stock-kids-brushes": P["child-teeth"],
    },
    "book": {"stock-virtual-call": "detail-laptop"},
    # ---------------------------------------------------------------- treatment pages
    "dental-implants": {"stock-implant-hero": H["dental-implants"], "arha-dental-care-operatory-chair": "detail-lab-model"},
    "full-mouth-rehabilitation": {"stock-crowns": H["full-mouth-rehabilitation"], "stock-loupe-teeth": "detail-crowns",
                                  "stock-lab": "detail-denture", "stock-restorations-set": "detail-restorations",
                                  "stock-lab-grind": "detail-bridge", "stock-brushes-grey": "detail-toothbrush"},
    "smile-design": {"dental-operatory-arha-dental-care-peddar-road-04": H["smile-design"], "stock-dentist-hands": "smile-side",
                     "arha-dental-care-scan-screen": "smile-bright"},
    "invisalign": {"stock-aligner-case-hand": H["invisalign"], "arha-dental-care-operatory-chair": "smile-bright",
                   "stock-aligner-model": "detail-aligner-model", "stock-aligner-case": "detail-aligner-case",
                   "stock-aligner-hands": "detail-aligners-shadow", "stock-aligner": "detail-aligner"},
    "crowns-bridges": {"stock-gloved-hands": H["crowns-bridges"], "arha-dental-care-delivery-unit": "detail-crowns-soft",
                       "stock-lab-grind": "detail-bridge", "stock-zirconia": "detail-zirconia", "stock-pfm": "detail-pfm"},
    "cosmetic-dentistry": {"stock-crowns-soft": H["cosmetic-dentistry"], "arha-dental-care-operatory-laptop": "smile-bright",
                           "stock-teeth-shades": "detail-teeth-shades", "stock-veneer-brush": "detail-veneers-fabric",
                           "stock-veneers-grey": "detail-crowns", "stock-veneers": "detail-veneers"},
    "root-canal-treatment": {"stock-mirror-tray": H["root-canal-treatment"], "stock-xray-panoramic": "detail-mirror",
                             "stock-endo-files": "detail-texture-linen", "stock-mirror-probe": "detail-toothpaste",
                             "stock-lab-model": "detail-lab-model"},
    "orthodontics": {"stock-braces-model": H["orthodontics"], "arha-dental-care-planning-room": "detail-aligner",
                     "stock-aligner-model": "detail-aligner-model", "stock-braces": "detail-braces-model",
                     "stock-aligners-shadow": "detail-aligners-shadow"},
    "general-dentistry": {"dental-operatory-arha-dental-care-peddar-road-02": H["general-dentistry"],
                          "stock-instrument-tray": "detail-mirror", "arha-dental-care-logo-dental-clinic-peddar-road": "smile-soft",
                          "stock-exam": "detail-floss", "stock-xray-panoramic": "detail-texture-linen",
                          "stock-mirror-probe": "detail-toothpaste", "stock-scalers": "smile-bright"},
    "kids-dentistry": {"stock-parent-child": H["kids-dentistry"], "stock-kid-brush-wood": "detail-kids-brush-wood",
                       "stock-kid-brush-bright": "detail-kids-brush", "stock-kid-brush-electric": "detail-toothbrush",
                       "stock-aligner-hands": "detail-aligners-shadow"},
    "maxillofacial-prosthetics": {"stock-prosthesis-hands": H["maxillofacial-prosthetics"], "arha-dental-care-planning-room": "detail-texture-linen",
                                  "stock-lab": "detail-lab-model", "stock-denture-dark": "detail-denture",
                                  "stock-prosthesis-model": "detail-restorations", "stock-zirconia": "detail-zirconia"},
    # ---------------------------------------------------------------- problem pages
    "problems/bleeding-gums": {"stock-floss-hand": P["bleeding-gums"], "stock-brushes-grey": "detail-toothbrush",
                               "arha-dental-care-steriliser": "detail-toothpaste"},
    "problems/child-teeth": {"stock-kids-brushes": P["child-teeth"], "stock-kid-brush-wood": "detail-kids-brush",
                             "stock-kid-brush-bright": "detail-toothbrush", "stock-kid-brush-electric": "detail-toothpaste",
                             "stock-aligners-shadow": "detail-aligners-shadow", "stock-braces": "detail-braces-model",
                             "arha-dental-care-exterior-dental-clinic-peddar-road": "detail-texture-linen"},
    "problems/chipped-tooth": {"stock-veneer-fingertip": P["chipped-tooth"], "arha-dental-care-reception-desk": "smile-soft"},
    "problems/crooked-teeth": {"stock-aligner": P["crooked-teeth"]},
    "problems/gaps": {"stock-veneers-fabric": P["gaps"], "stock-veneer-placing": "smile-side",
                      "stock-veneers": "detail-veneers", "stock-aligner-gloved": "detail-aligner",
                      "arha-dental-care-logo-wall": "smile-bright"},
    "problems/loose-dentures": {"stock-denture-dark": P["loose-dentures"], "stock-denture-hand": "detail-denture-hand",
                                "stock-implant-overdenture": "detail-implant-hero",
                                "arha-dental-care-reception-desk": "detail-texture-linen"},
    "problems/metal-fillings": {"stock-steel-instruments": P["metal-fillings"], "stock-handpieces-dark": "detail-mirror",
                                "stock-bridge-white": "detail-bridge", "arha-dental-care-equipment-counter": "smile-soft"},
    "problems/missing-tooth": {"stock-implant-crown": P["missing-tooth"], "stock-implant-hand": "detail-implant-hero",
                               "stock-implant-bridge": "detail-restorations", "stock-denture-hand": "detail-denture-hand",
                               "arha-dental-care-operatory-glass-door": "detail-texture-linen"},
    "problems/stained-teeth": {"stock-shade-guide": P["stained-teeth"], "arha-dental-care-reception-wide": "smile-soft"},
    "problems/toothache": {"stock-xray-screen": P["toothache"], "arha-dental-care-xray-room": "detail-texture-linen"},
}

KEEP = {"dental-implants": {"stock-implant-model"}, "problems/crooked-teeth": {"arha-dental-care-scan-screen"},
        "problems/chipped-tooth": {"stock-veneers-grey"}}

PIC = re.compile(r'(?P<indent>[ \t]*)<picture class="(?P<cls>[^"]*)">\n(?P<body>.*?)</picture>', re.S)


def swap_name(slug, name):
    """The photograph that replaces `name` on this page (for the Open Graph image), or `name` itself."""
    return PAGES.get(slug, {}).get(name, name)


def apply(slug, html):
    table = PAGES.get(slug)
    if not table:
        return html

    def repl(m):
        img = re.search(r'<img src="assets/img/([\w-]+?)-\d+\.jpg"[^>]*>', m.group("body"))
        if not img or img.group(1) not in table:
            return m.group(0)
        new = table[img.group(1)]
        tag = img.group(0)
        sizes = re.search(r'sizes="([^"]*)"', tag).group(1)
        alt = re.search(r'alt="([^"]*)"', tag).group(1)
        eager = 'fetchpriority="high"' in tag
        extra = " ".join(c for c in m.group("cls").split() if c != "fill") or None
        return picture(new, sizes, PEOPLE[new]["alt"] if alt else "", eager=eager, cls=extra,
                       pos=PEOPLE[new]["pos"], indent=m.group("indent")).rstrip("\n")
    return PIC.sub(repl, html)
