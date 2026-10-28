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
            {"slug": "full-mouth-rehabilitation", "name": "Full mouth rehabilitation", "live": False},
            {"slug": "maxillofacial-prosthetics", "name": "Maxillofacial prosthetics", "live": False},
        ],
    },
    {
        "title": "Smile &amp; aesthetics",
        "items": [
            {"slug": "smile-design", "name": "Smile design", "live": False},
            {"slug": "cosmetic-dentistry", "name": "Cosmetic dentistry", "live": False},
            {"slug": "invisalign", "name": "Invisalign clear aligners", "live": False},
            {"slug": "orthodontics", "name": "Orthodontics (braces)", "live": False},
        ],
    },
    {
        "title": "Everyday &amp; family care",
        "items": [
            {"slug": "general-dentistry", "name": "General dentistry &amp; cleaning", "live": False},
            {"slug": "root-canal-treatment", "name": "Root canal treatment", "live": False},
            {"slug": "crowns-bridges", "name": "Crowns &amp; bridges", "live": False},
            {"slug": "kids-dentistry", "name": "Kids’ dentistry", "live": False},
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
