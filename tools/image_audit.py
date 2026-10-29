"""Image inventory per page (v4 fixes 3, point 1), written to notes/IMAGE-AUDIT.md (part 1).

Usage: .venv/Scripts/python -I tools/image_audit.py [--check]
Rules: Arha's own photographs lead; at most ONE stock person per page; at most ONE tasteful mouth
close-up per page; nothing gross (decay, rotten or broken teeth, blood, extreme macro). Every photograph
is classified in KIND below (by its canonical name, tools/photo_ids.py); an unclassified one is an error,
so a new stock pick has to be looked at before it can be used. --check exits 1 when a rule is broken.
The stock slot reviews (part 2 of IMAGE-AUDIT.md) are written by hand from tools/qa/shortlist.py.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import photo_audit  # noqa: E402
import photo_ids  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "notes" / "IMAGE-AUDIT.md"

CLINIC, STILL, VIDEO, OBJECT, HANDS, PERSON, MOUTH, GROSS, CITY = (
    "Arha photo", "Arha video still", "Arha video", "stock still life", "stock hands at work",
    "stock person", "mouth close-up", "gross / macro", "Mumbai")
# Every stock photograph by what it shows (people and mouths are what the rules count)
KIND = {
    # still life and clinical details
    "stock-aligner": OBJECT, "stock-crowns": OBJECT, "stock-veneers": OBJECT, "stock-zirconia": OBJECT, "stock-pfm": OBJECT,
    "stock-implant-hero": OBJECT, "stock-implant-model": OBJECT, "stock-implant-arch": OBJECT, "stock-implant-bridge": OBJECT,
    "stock-implant-overdenture": OBJECT, "stock-lab-model": OBJECT, "stock-instrument-tray": OBJECT, "stock-mirror-probe": OBJECT,
    "stock-mirror-tray": OBJECT, "stock-handpieces": OBJECT, "stock-endo-files": OBJECT, "stock-xray-panoramic": OBJECT,
    "stock-xray-screen": OBJECT, "stock-arrival": OBJECT, "stock-marine-drive": CITY,
    # hands, no face
    "stock-gloved-hands": HANDS, "stock-dentist-hands": HANDS, "stock-lab": HANDS, "stock-lab-grind": HANDS,
    "stock-implant-hand": HANDS, "stock-prosthesis-hands": HANDS, "stock-denture-hand": HANDS,
    # people (a face is visible)
    "stock-consultation": PERSON, "stock-patient-chair": PERSON, "stock-smiling-patient": PERSON, "stock-clinic-consult": PERSON,
    "stock-clinic-work": PERSON, "stock-toothache": PERSON, "stock-mirror": PERSON, "stock-virtual-call": PERSON,
    "stock-denture-man": PERSON, "stock-cleaning": PERSON, "stock-scan": PERSON, "stock-parent-child": PERSON,
    "stock-child-brush": PERSON, "stock-kid-chair": PERSON, "stock-kid-dentist": PERSON, "stock-kid-face": PERSON,
    "stock-kid-boy": PERSON, "stock-kid-smile": PERSON, "stock-teen": PERSON, "stock-teen-boy": PERSON, "stock-toddler": PERSON,
    "stock-braces-kid": PERSON, "stock-woman-smile": PERSON, "stock-man-smile": PERSON,
    # mouths (tasteful close-ups; one per page at most)
    "stock-natural-smile": MOUTH, "stock-straight-smile": MOUTH, "stock-aligner-in": MOUTH, "stock-braces": MOUTH,
    "stock-case-1": MOUTH, "stock-case-2": MOUTH, "stock-case-3": MOUTH, "stock-case-4": MOUTH, "stock-case-5": MOUTH,
    "stock-case-6": MOUTH, "stock-smile-1": MOUTH, "stock-sim-whiten-before": MOUTH, "stock-loupe-teeth": MOUTH,
    "stock-gaps": MOUTH, "stock-gums": MOUTH, "stock-exam": MOUTH,
    # never: decay, broken or yellow-rotten teeth, retractors and blood, extreme macro
    "stock-decayed-tooth": GROSS, "stock-metal-fillings": GROSS, "stock-filling-white": GROSS, "stock-molar": GROSS,
    "stock-before-worn": GROSS, "stock-before-missing": GROSS, "stock-before-missing-2": GROSS, "stock-before-crowded": GROSS,
    "stock-crowded-arch": GROSS, "stock-gum-check": GROSS, "stock-bonding": GROSS,
}
for n in range(1, 17):
    KIND[f"stock-face-{n}"] = PERSON
for n in (1, 2, 3, 4, 5, 6):
    KIND[f"stock-case-{n}-face"] = PERSON
EXTRA = {  # v4 fixes 3 picks (tools/qa/stock_slots.json), each looked at before use
    **dict.fromkeys(["stock-crowns-soft", "stock-veneers-grey", "stock-implant-models", "stock-restorations-set", "stock-aligner-model",
                     "stock-aligner-sculpture", "stock-aligner-case", "stock-prosthesis-model", "stock-braces-model", "stock-aligners-shadow",
                     "stock-handpieces-dark", "stock-implant-crown", "stock-veneer-fingertip", "stock-veneers-fabric", "stock-denture-dark",
                     "stock-veneer-placing", "stock-veneer-brush", "stock-bridge-white", "stock-floss-hand", "stock-steel-instruments",
                     "stock-kids-brushes", "stock-kid-brush-wood", "stock-kid-brush-bright", "stock-kid-brush-electric",
                     "stock-brushes-grey", "stock-scalers", "stock-shade-guide", "stock-teeth-shades"], OBJECT),
    **dict.fromkeys(["stock-aligner-case-hand", "stock-aligner-gloved", "stock-aligner-hands"], HANDS),
    "stock-consult-desk": PERSON,
    "stock-sim-smile-a": MOUTH, "stock-sim-smile-b": MOUTH,
}


def kind(name):
    if name.startswith(("dental-", "arha-dental-care-", "autoclave-")):
        still = name.removeprefix("arha-dental-care-") in STILLS
        return STILL if still else CLINIC
    if name.startswith(("hero-city", "tour-poster")):
        return CITY if name.startswith("hero-city") else VIDEO
    if name.startswith("stock-pair-"):
        return MOUTH
    return EXTRA.get(name) or KIND.get(name)


def stills():
    try:
        import stills as s
        return set(s.STILLS)
    except Exception:
        return set()


STILLS = stills()


def section_of(html, pos):
    """The id or class of the section an image sits in (the last <section ...> before it)."""
    m = list(re.finditer(r'<(?:section|article|figure|div class="(?:brings|spots|story|xfade|ix-split|blend|agedial|stages|loupe-wrap|pair|featured-case|xpanels|drag)[^"]*")[^>]*?(?:id="([^"]+)"|class="([^"]+)")', html[:pos]))
    if not m:
        return "?"
    g = m[-1]
    return (g.group(1) or g.group(2) or "?").split()[0]


def inventory():
    canon = photo_ids.groups()
    pages = {}
    for rel, path in photo_audit.pages():
        html = path.read_text(encoding="utf-8")
        rows, seen = [], set()
        for m in re.finditer(r'<img\b[^>]*?\ssrc="[^"]*?assets/(?:img|video)/([a-z0-9-]+?)-\d+\.(?:jpg|webp|avif)"', html):
            raw = m.group(1)
            pair = re.match(r"(stock-pair-\d+|stock-sim-whiten)-(?:before|after)$", raw)
            key = pair.group(1) if pair else raw
            if key in seen:
                continue
            seen.add(key)
            rows.append((section_of(html, m.start()), raw, canon.get(raw, raw), kind(canon.get(raw, raw)) or kind(raw)))
        pages[rel] = rows
    return pages


def check(pages):
    problems = []
    for rel, rows in pages.items():
        kinds = [k for *_x, k in rows]
        if None in kinds:
            problems.append(f"{rel}: unclassified {[r[1] for r in rows if r[3] is None]}")
        if kinds.count(PERSON) > 1:
            problems.append(f"{rel}: {kinds.count(PERSON)} stock people (max 1)")
        if kinds.count(MOUTH) > 1:
            problems.append(f"{rel}: {kinds.count(MOUTH)} mouth close-ups (max 1)")
        if GROSS in kinds:
            problems.append(f"{rel}: gross or macro image {[r[1] for r in rows if r[3] == GROSS]}")
    return problems


def write(pages, problems):
    head = OUT.read_text(encoding="utf-8").split("\n## Part 2", 1) if OUT.exists() else ["", ""]
    part2 = "\n## Part 2" + head[1] if len(head) > 1 else ""
    lines = ["# Image audit (v4 fixes 3)", "",
             "Part 1 is generated by `tools/image_audit.py` from the built pages:",
             "- Rules: Arha's own photographs lead; at most one stock person per page; at most one tasteful mouth close-up per page; nothing gross or macro.",
             "- Repeats are checked by `tools/photo_audit.py`: a photo is on a page once and on at most two pages.",
             "- Part 2 records how each stock slot was chosen.", "",
             f"**Rule check: {'all pages pass' if not problems else str(len(problems)) + ' problems'}.**", ""]
    lines += [f"- {p}" for p in problems]
    lines += ["", "## Part 1: images per page", "", "| Page | Faces (stock people) | Mouth close-ups | Arha photos and stills | Images, by section |", "|---|---|---|---|---|"]
    for rel, rows in pages.items():
        kinds = [r[3] for r in rows]
        own = sum(k in (CLINIC, STILL, VIDEO) for k in kinds)
        imgs = "<br>".join(f"{sec}: `{raw}` ({k})" for sec, raw, _c, k in rows) or "(no photographs)"
        lines.append(f"| /{'' if rel == 'home' else rel + '/'} | {kinds.count(PERSON)} | {kinds.count(MOUTH)} | {own} of {len(rows)} | {imgs} |")
    OUT.write_text("\n".join(lines) + "\n" + part2, encoding="utf-8")


if __name__ == "__main__":
    pages = inventory()
    problems = check(pages)
    write(pages, problems)
    print("\n".join(problems) or "all pages pass")
    print(f"{len(problems)} problems, {len(pages)} pages")
    if "--check" in sys.argv and problems:
        sys.exit(1)
