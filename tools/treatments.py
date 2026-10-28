"""Arha's treatments: one list drives the header mega menu, the side menu and the treatment pages.

Groups and names follow the clinic's current website (notes/ADDITION-treatments.md). Each slug is
the page's flat URL (/<slug>/). Pages not built yet are marked live=False; the menus still link to them.
"""

GROUPS = [
    {
        "title": "Specialist care",
        "specialty": True,  # cards carry a small SPECIALTY tag
        "items": [
            {"slug": "dental-implants", "name": "Dental implants", "live": True},
            {"slug": "full-mouth-rehabilitation", "name": "Full mouth rehabilitation", "live": True},
            {"slug": "maxillofacial-prosthetics", "name": "Maxillofacial prosthetics", "live": True},
        ],
    },
    {
        "title": "Smile &amp; aesthetics",
        "items": [
            {"slug": "smile-design", "name": "Smile design", "live": True},
            {"slug": "cosmetic-dentistry", "name": "Cosmetic dentistry", "live": True},
            {"slug": "invisalign", "name": "Invisalign clear aligners", "live": True},
            {"slug": "orthodontics", "name": "Orthodontics (braces)", "live": True},
        ],
    },
    {
        "title": "Everyday &amp; family care",
        "items": [
            {"slug": "general-dentistry", "name": "General dentistry &amp; cleaning", "live": True},
            {"slug": "root-canal-treatment", "name": "Root canal treatment", "live": True},
            {"slug": "crowns-bridges", "name": "Crowns &amp; bridges", "live": True},
            {"slug": "kids-dentistry", "name": "Kids’ dentistry", "live": True},
        ],
    },
]


def mega_menu(indent="            "):
    """The Treatments panel under the header: three groups, then All treatments and Emergencies."""
    out = [f'{indent}<div class="dropdown dropdown--mega" id="dd-treatments">',
           f'{indent}  <div class="mega">']
    for g in GROUPS:
        out.append(f'{indent}    <div class="mega__group">')
        tag = ' <span class="tag">Specialty</span>' if g.get("specialty") else ""
        out.append(f'{indent}      <p class="mega__title">{g["title"]}{tag}</p>')
        out.append(f'{indent}      <ul>')
        for t in g["items"]:
            out.append(f'{indent}        <li><a href="{t["slug"]}/">{t["name"]}</a></li>')
        out.append(f'{indent}      </ul>')
        out.append(f'{indent}    </div>')
    out += [f'{indent}    <div class="mega__foot">',
            f'{indent}      <a class="cta" href="treatments/">All treatments</a>',
            f'{indent}      <a class="mega__urgent" href="emergency/">Dental emergency? Get help now</a>',
            f'{indent}    </div>',
            f'{indent}  </div>',
            f'{indent}</div>']
    return "\n".join(out) + "\n"


def side_menu(indent="                  "):
    """The Treatments group in the side menu: every treatment, then All treatments."""
    out = [f'{indent}<li><a href="{t["slug"]}/">{t["name"]}</a></li>' for g in GROUPS for t in g["items"]]
    out.append(f'{indent}<li><a href="treatments/">All treatments</a></li>')
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ Common problems we fix
# Shown on the homepage and /treatments/. Each before/after pair is a line illustration
# (tools/illustrations.py), never a patient. "treat" lists treatment slugs from GROUPS.
PROBLEMS = [
    {"slug": "missing-tooth", "name": "A missing tooth",
     "lines": ["A gap affects how you chew and, over time, how the teeth beside it sit.",
               "It can be replaced with an implant, a bridge or a denture, depending on your gums, your bone and the teeth around it."],
     "treat": ["dental-implants", "crowns-bridges"],
     "ask": "I have a missing tooth. What are my options?"},
    {"slug": "chipped-tooth", "name": "Chipped or broken tooth",
     "lines": ["Small chips can often be rebuilt with tooth-coloured bonding.",
               "A larger break may need a crown to protect what is left of the tooth."],
     "treat": ["cosmetic-dentistry", "crowns-bridges"],
     "ask": "I have chipped a tooth. What can be done?"},
    {"slug": "gaps", "name": "Gaps between teeth",
     "lines": ["Gaps can be closed by moving the teeth, or by adding to them with bonding or veneers.",
               "The right choice depends on the size of the gap and on your bite."],
     "treat": ["invisalign", "orthodontics", "cosmetic-dentistry"],
     "ask": "I have gaps between my teeth. How can they be closed?"},
    {"slug": "crooked-teeth", "name": "Crooked teeth",
     "lines": ["Teeth can be straightened at almost any age, with clear aligners or with braces.",
               "Straighter teeth are also easier to keep clean."],
     "treat": ["invisalign", "orthodontics"],
     "ask": "My teeth are crooked. Are aligners or braces right for me?"},
    {"slug": "stained-teeth", "name": "Yellow or stained teeth",
     "lines": ["Surface stains often lift with a professional clean. Deeper colour responds to whitening.",
               "Where whitening cannot help, bonding or veneers can."],
     "treat": ["general-dentistry", "cosmetic-dentistry"],
     "ask": "My teeth look yellow. Can they be whitened?"},
    {"slug": "toothache", "name": "Toothache or sensitivity",
     "lines": ["Sensitivity can come from worn enamel or receding gums. Pain that lingers often means decay has reached the nerve.",
               "An exam and an X-ray tell which it is. A filling or root canal treatment can usually save the tooth."],
     "treat": ["root-canal-treatment", "general-dentistry"],
     "ask": "I have toothache. Should I come in?",
     "urgent": True},
    {"slug": "bleeding-gums", "name": "Bleeding gums",
     "lines": ["Gums that bleed when you brush are usually inflamed, and that is treatable.",
               "A professional clean and better care at home often settle it. Left alone, it can loosen teeth."],
     "treat": ["general-dentistry"],
     "ask": "My gums bleed when I brush. What should I do?"},
    {"slug": "metal-fillings", "name": "Old metal fillings",
     "lines": ["Old metal fillings can crack, or leak at the edges, over the years.",
               "When one needs replacing, it can be redone in tooth-coloured material, or with a crown."],
     "treat": ["general-dentistry", "crowns-bridges"],
     "ask": "Can my old metal fillings be replaced?"},
    {"slug": "dentures", "name": "Loose or uncomfortable dentures",
     "lines": ["A denture that moves when you eat or speak can be held firmly by a few implants.",
               "Sometimes a refit or a new denture is enough."],
     "treat": ["dental-implants", "full-mouth-rehabilitation"],
     "ask": "My denture is loose. Can implants help?"},
    {"slug": "child-teeth", "name": "My child’s teeth",
     "lines": ["Baby teeth hold space for the adult teeth and matter for eating and speech.",
               "Regular checks, sealants and fluoride help stop decay early."],
     "treat": ["kids-dentistry"],
     "ask": "When should my child first see a dentist?"},
]

def treatment(slug):
    return next(t for g in GROUPS for t in g["items"] if t["slug"] == slug)


def problems(indent="        "):
    """Common problems we fix: tabs on the left, a stage with a before/after illustration on the right.
    The URL hash (#problem-<slug>) selects a problem, so each one can be linked to directly."""
    import re
    from pathlib import Path
    from urllib.parse import quote
    art = Path(__file__).resolve().parent.parent / "assets" / "illustrations"

    def alt(slug, state):  # the drawing's own <title>, written by tools/illustrations.py
        text = (art / f"problem-{slug}-{state}.svg").read_text(encoding="utf-8")
        return f"Illustration, {state}: " + re.search(r"<title>(.*?)</title>", text).group(1).lower()

    i = indent
    tabs, panels = [], []
    for n, p in enumerate(PROBLEMS):
        sel = n == 0
        tabs.append(f'{i}    <button class="problems__tab" type="button" role="tab" id="pt-{p["slug"]}" aria-controls="problem-{p["slug"]}" '
                    f'aria-selected="{str(sel).lower()}"{"" if sel else " tabindex=\"-1\""}>{p["name"]}</button>')
        chips = "".join(f'<li><a href="{s}/">{treatment(s)["name"]}</a></li>' for s in p["treat"])
        urgent = (f'\n{i}      <p class="problems__urgent">In severe pain or swollen? <a href="emergency/">Dental emergencies</a></p>'
                  if p.get("urgent") else "")
        wa = "https://wa.me/910000000000?text=" + quote(f"Hello Arha Dental Care. {p['ask']}")
        panels.append(f"""{i}  <div class="problems__panel" role="tabpanel" id="problem-{p["slug"]}" aria-labelledby="pt-{p["slug"]}" tabindex="0"{"" if sel else " hidden"}>
{i}    <figure class="compare">
{i}      <div class="ba" data-compare>
{i}        <img src="assets/illustrations/problem-{p["slug"]}-after.svg" alt="{alt(p["slug"], "after")}" width="640" height="400" loading="lazy">
{i}        <img class="ba__before" src="assets/illustrations/problem-{p["slug"]}-before.svg" alt="{alt(p["slug"], "before")}" width="640" height="400" loading="lazy">
{i}        <span class="ba__label ba__label--before">Before</span><span class="ba__label ba__label--after">After</span>
{i}        <input class="ba__range" type="range" min="0" max="100" value="50" aria-label="Compare before and after: {p["name"].lower()}">
{i}        <span class="ba__handle" aria-hidden="true"><span class="ba__grip"></span></span>
{i}      </div>
{i}      <figcaption>Illustration, not a patient</figcaption>
{i}    </figure>
{i}    <div class="problems__text">
{i}      <h3>{p["name"]}</h3>
{i}      <p>{p["lines"][0]}</p>
{i}      <p>{p["lines"][1]}</p>
{i}      <p class="problems__usually">Usually treated with</p>
{i}      <ul class="chips">{chips}</ul>{urgent}
{i}      <a class="cta" href="{wa}" target="_blank" rel="noopener" data-riya-ask="{p["ask"]}">Ask Riya about this</a>
{i}    </div>
{i}  </div>""")
    return (f'{i}<div class="problems" data-tabs data-hash>\n'
            f'{i}  <div class="problems__tabs" role="tablist" aria-label="Common problems" aria-orientation="vertical">\n'
            + "\n".join(tabs) + f"\n{i}  </div>\n"
            + "\n".join(panels) + f"\n{i}</div>\n")
