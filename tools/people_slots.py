"""Which stock photograph of people each treatment and problem page shows (Viraaj, 7 Nov 2026: "stock photos for
trust, clinic photos only where they belong").

Arha's own photographs stay only in the homepage hero, "A clinic built around calm", "Step inside", the gallery,
the "Technology & innovation" card (the real X-ray room) and the "Dr. Nikhil's clinic" card (the door sign), and on
the pages about the clinic itself (doctors, founder, the practice, technology, book, dental tourism).
Everywhere on the treatment and problem pages, every photograph is one of tools/people.json, except three
interactives that only work with their own photograph (KEEP): the numbered parts of an implant on the implant model,
the focus ring that moves across the 3D arches on Arha's planning screen, and the magnifier over porcelain veneers.

PAGES maps a page to {photograph the builders put there: the people photograph shown instead}. apply() runs on each
built page (tools/pages.py) and rebuilds each matching <picture> with the new photograph, its plain alt text (from
people.json; decorative images stay alt="") and its face position, keeping sizes, loading and classes. Page heroes are
the first photograph (eager, not lazy); everything else stays lazy. No photograph appears twice on one page
(check: tools/qa/people_check.py).
"""
import json
import re
from pathlib import Path

from picture import picture

PEOPLE = json.loads(Path(__file__).with_name("people.json").read_text(encoding="utf-8"))

# The photograph of each treatment page's hero; the homepage's "Explore treatments" rows and the treatments index use it too.
TREATMENT_HERO = {
    "dental-implants": "couple-laughing-outdoors",
    "full-mouth-rehabilitation": "grandfather-grandson",
    "smile-design": "woman-laughing-closeup",
    "invisalign": "young-woman-at-table",
    "crowns-bridges": "young-man-smile-closeup",
    "cosmetic-dentistry": "woman-smile-nath",
    "root-canal-treatment": "woman-relaxed-cafe",
    "orthodontics": "teen-smiling",
    "general-dentistry": "family-outdoors",
    "kids-dentistry": "mother-daughter-laughing",
    "maxillofacial-prosthetics": "couple-on-sofa",
}
# The photograph of each problem page's hero; the homepage's "What brings you in?" cards and the problems index use it too.
PROBLEM_HERO = {
    "missing-tooth": "older-man-smiling",
    "chipped-tooth": "young-man-scarf",
    "gaps": "woman-glasses-laughing",
    "crooked-teeth": "young-woman-smiling",
    "stained-teeth": "woman-with-cup",
    "toothache": "man-with-mug",
    "bleeding-gums": "woman-smiling-orange",
    "metal-fillings": "young-man-glasses",
    "loose-dentures": "older-woman-smiling",
    "child-teeth": "mother-daughter-portrait",
}
H, P = TREATMENT_HERO, PROBLEM_HERO

PAGES = {
    "treatments": {
        "stock-implant-arch": "friends-on-lawn",
        "stock-implant-models": H["dental-implants"], "stock-denture-tray": H["full-mouth-rehabilitation"],
        "stock-prosthesis-hands": H["maxillofacial-prosthetics"], "stock-veneer-fingertip": H["smile-design"],
        "stock-veneers-fabric": H["cosmetic-dentistry"], "stock-aligner-case-hand": H["invisalign"],
        "stock-braces-model": H["orthodontics"], "stock-scalers": H["general-dentistry"],
        "stock-steel-instruments": H["root-canal-treatment"], "stock-bridge-white": H["crowns-bridges"],
        "stock-child-chair": H["kids-dentistry"],
    },
    "problems": {
        "stock-handpieces": "friends-two-women",
        "stock-implant-crown": P["missing-tooth"], "stock-veneer-fingertip": P["chipped-tooth"],
        "stock-veneers-fabric": P["gaps"], "stock-aligner": P["crooked-teeth"], "stock-shade-guide": P["stained-teeth"],
        "stock-xray-screen": P["toothache"], "stock-floss-hand": P["bleeding-gums"],
        "stock-steel-instruments": P["metal-fillings"], "stock-denture-dark": P["loose-dentures"],
        "stock-kids-brushes": P["child-teeth"],
    },
    # ---------------------------------------------------------------- treatment pages
    "dental-implants": {"stock-implant-hero": H["dental-implants"], "arha-dental-care-operatory-chair": "older-man-smiling"},
    "full-mouth-rehabilitation": {"stock-crowns": H["full-mouth-rehabilitation"], "stock-loupe-teeth": "couple-talking",
                                  "stock-lab": "couple-on-sofa", "stock-restorations-set": "grandmother-baby",
                                  "stock-lab-grind": "older-woman-smiling", "stock-brushes-grey": "grandparents-grandchild"},
    "smile-design": {"dental-operatory-arha-dental-care-peddar-road-04": H["smile-design"], "stock-dentist-hands": "woman-laughing",
                     "arha-dental-care-scan-screen": "young-woman-smiling"},
    "invisalign": {"stock-aligner-case-hand": H["invisalign"], "arha-dental-care-operatory-chair": "young-man-suit",
                   "stock-aligner-model": "friends-two-men", "stock-aligner-case": "young-woman-smiling",
                   "stock-aligner-hands": "young-man-glasses", "stock-aligner": "friends-two-women"},
    "crowns-bridges": {"stock-gloved-hands": H["crowns-bridges"], "arha-dental-care-delivery-unit": "woman-smiling-orange",
                       "stock-lab-grind": "young-man-scarf", "stock-zirconia": "older-woman-smiling", "stock-pfm": "couple-reading"},
    "cosmetic-dentistry": {"stock-crowns-soft": H["cosmetic-dentistry"], "arha-dental-care-operatory-laptop": "woman-with-cup",
                           "stock-teeth-shades": "woman-laughing", "stock-veneer-brush": "young-man-scarf",
                           "stock-veneers-grey": "woman-glasses-laughing", "stock-veneers": "woman-laughing-closeup"},
    "root-canal-treatment": {"stock-mirror-tray": H["root-canal-treatment"], "stock-xray-panoramic": "man-with-mug",
                             "stock-endo-files": "man-relaxed-smiling", "stock-mirror-probe": "couple-reading",
                             "stock-lab-model": "older-man-smiling"},
    "orthodontics": {"stock-braces-model": H["orthodontics"], "arha-dental-care-planning-room": "young-man-suit",
                     "stock-aligner-model": "boy-smiling", "stock-braces": "girl-smiling", "stock-aligners-shadow": "friends-two-men"},
    "general-dentistry": {"dental-operatory-arha-dental-care-peddar-road-02": H["general-dentistry"],
                          "stock-instrument-tray": "couple-reading", "arha-dental-care-logo-dental-clinic-peddar-road": "woman-smiling-orange",
                          "stock-exam": "older-man-smiling", "stock-xray-panoramic": "friends-two-women",
                          "stock-mirror-probe": "young-man-glasses", "stock-scalers": "grandmother-baby"},
    "kids-dentistry": {"stock-parent-child": H["kids-dentistry"], "stock-kid-brush-wood": "toddler",
                       "stock-kid-brush-bright": "little-girl", "stock-kid-brush-electric": "boy-smiling",
                       "stock-aligner-hands": "teen-boy-kurta"},
    "maxillofacial-prosthetics": {"stock-prosthesis-hands": H["maxillofacial-prosthetics"], "arha-dental-care-planning-room": "couple-talking",
                                  "stock-lab": "older-woman-scarf", "stock-denture-dark": "young-man-scarf",
                                  "stock-prosthesis-model": "man-relaxed-smiling", "stock-zirconia": "girl-bright-smile"},
    # ---------------------------------------------------------------- problem pages
    "problems/bleeding-gums": {"stock-floss-hand": P["bleeding-gums"], "stock-brushes-grey": "couple-reading",
                               "arha-dental-care-steriliser": "grandmother-baby"},
    "problems/child-teeth": {"stock-kids-brushes": P["child-teeth"], "stock-kid-brush-wood": "toddler",
                             "stock-kid-brush-bright": "little-girl", "stock-kid-brush-electric": "boy-smiling",
                             "stock-aligners-shadow": "girl-smiling", "stock-braces": "teen-boy-kurta",
                             "arha-dental-care-exterior-dental-clinic-peddar-road": "mother-daughter-laughing"},
    "problems/chipped-tooth": {"stock-veneer-fingertip": P["chipped-tooth"], "arha-dental-care-reception-desk": "woman-with-cup"},
    "problems/crooked-teeth": {"stock-aligner": P["crooked-teeth"]},
    "problems/gaps": {"stock-veneers-fabric": P["gaps"], "stock-veneer-placing": "woman-laughing-closeup",
                      "stock-veneers": "woman-smile-nath", "stock-aligner-gloved": "young-woman-at-table",
                      "arha-dental-care-logo-wall": "friends-two-women"},
    "problems/loose-dentures": {"stock-denture-dark": P["loose-dentures"], "stock-denture-hand": "older-woman-scarf",
                                "stock-implant-overdenture": "couple-laughing-outdoors",
                                "arha-dental-care-reception-desk": "grandparents-grandchild"},
    "problems/metal-fillings": {"stock-steel-instruments": P["metal-fillings"], "stock-handpieces-dark": "young-man-suit",
                                "stock-bridge-white": "woman-laughing", "arha-dental-care-equipment-counter": "friends-on-lawn"},
    "problems/missing-tooth": {"stock-implant-crown": P["missing-tooth"], "stock-implant-hand": "couple-laughing-outdoors",
                               "stock-implant-bridge": "couple-talking", "stock-denture-hand": "couple-on-sofa",
                               "arha-dental-care-operatory-glass-door": "grandfather-grandson"},
    "problems/stained-teeth": {"stock-shade-guide": P["stained-teeth"], "arha-dental-care-reception-wide": "woman-laughing"},
    "problems/toothache": {"stock-xray-screen": P["toothache"], "arha-dental-care-xray-room": "woman-relaxed-cafe"},
}

KEEP = {"dental-implants": {"stock-implant-model"}, "problems/crooked-teeth": {"arha-dental-care-scan-screen"},
        "problems/chipped-tooth": {"stock-veneers-grey"}}

PIC = re.compile(r'(?P<indent>[ \t]*)<picture class="(?P<cls>[^"]*)">\n(?P<body>.*?)</picture>', re.S)


def swap_name(slug, name):
    """The people photograph that replaces `name` on this page (for the Open Graph image), or `name` itself."""
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
