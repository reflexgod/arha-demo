"""Problems first (notes/V4-PROBLEMS-FIRST.md): one page per problem at /problems/<slug>/, the homepage
"What brings you in?" module and the problem lists in the menus.

Every problem page shares one design system and has its own interactive, built with stock photographs
(site.js 19): a photo toggle, a magnifier, expanding panels, a blend scrubber, a whitening simulation, a
symptom picker, a gum self-check, a material switch, a denture toggle and an age dial.
Copy is general dental information in Arha's voice. No visit counts, prices or timings are invented:
those are decided at the consultation. Every clinical line is for Dr. Nikhil to review (notes/TO-CONFIRM.md).
"""
import html

import technology
import treatment_pages as tp
import treatments
from picture import picture

ARROW = treatments.ARROW
NAMES = {t["slug"]: t["name"] for g in treatments.GROUPS for t in g["items"]}

# slug -> page data. hero: the photograph shared by the homepage module and the page hero.
PROBLEMS = {
    "missing-tooth": {
        "name": "A missing tooth", "menu": "A missing tooth",
        "hero": ("stock-implant-crown", "A single implant crown on its titanium post, against a dark background", "50% 50%"),
        "line": "A gap changes how you chew, and over time how the teeth beside it sit. It can be replaced with an implant, a bridge or a denture.",
        "notice": [("Chewing on one side", "You avoid the gap without thinking about it."),
                   ("Teeth shifting", "The teeth next to the gap, and the one opposite, can drift into the space."),
                   ("Food trapping", "Food collects in the gap and at the edges of the teeth beside it."),
                   ("A change in your smile", "A gap near the front shows when you talk or smile.")],
        "fix": [("dental-implants", "An implant", "A fixed tooth on a small titanium post in the jaw. The teeth beside it are left as they are."),
                ("crowns-bridges", "A bridge", "A fixed tooth held by crowns on the teeth either side of the gap."),
                ("full-mouth-rehabilitation", "A denture", "A removable tooth or teeth on a base that rests on the gums.")],
        "clinic": ("arha-dental-care-operatory-glass-door", "A treatment room at Arha, seen through its glass door: the chair, the light and a screen"),
        "tech": ["panoramic-x-ray", "planning-desk"],
        "faq": [("Do I need to replace a single missing back tooth?", "Not always, but a gap can let the teeth around it move and change your bite over time. We will look at your bite and tell you honestly whether replacing it matters for you."),
                ("Which option lasts longest?", "Each can serve you well for many years with good care. How long depends on your gums, your bone, your bite and how you look after it, so we talk it through at the consultation."),
                ("Can I have a tooth the same day?", "Sometimes a temporary tooth can be fitted while the final one is made. Whether that is possible depends on the tooth and the bone, which an examination and X-ray show.")],
    },
    "chipped-tooth": {
        "name": "A chipped or broken tooth", "menu": "Chipped or broken tooth",
        "hero": ("stock-veneer-fingertip", "A thin porcelain veneer held up beside the front teeth of a dental model", "50% 40%"),
        "line": "A small chip can often be rebuilt in tooth-coloured bonding. A larger break may need a crown to protect what is left.",
        "notice": [("A rough or sharp edge", "Your tongue keeps finding it."),
                   ("Sensitivity", "Cold or sweet food can twinge if the break is deeper."),
                   ("A change in shape", "The edge of the tooth looks uneven in photos or the mirror."),
                   ("Pain on biting", "A crack can hurt when you bite on it, and should be checked.")],
        "fix": [("cosmetic-dentistry", "Bonding", "Tooth-coloured material shaped onto the tooth in one visit, for small chips."),
                ("crowns-bridges", "A crown", "A cap that covers and protects a tooth that has lost more of its structure."),
                ("cosmetic-dentistry", "A veneer", "A thin porcelain facing for a front tooth, when shape and colour matter too.")],
        "clinic": ("arha-dental-care-reception-desk", "Arha’s reception: the gold emblem on the marble wall above the front desk"),
        "tech": ["treatment-rooms", "panoramic-x-ray"],
        "faq": [("Is a chipped tooth an emergency?", "A small chip with no pain can wait for a normal appointment. Severe pain, a large break or a tooth knocked loose should be seen soon: see Dental emergencies."),
                ("Will a repair show?", "Bonding and porcelain are matched to the shade of your teeth, so a well-made repair blends in."),
                ("What should I do with the broken piece?", "Keep it clean and bring it with you. It is not always reattached, but it helps us see what happened.")],
    },
    "gaps": {
        "name": "Gaps between teeth", "menu": "Gaps between teeth",
        "hero": ("stock-veneers-fabric", "Four porcelain veneers resting on soft grey fabric", "50% 50%"),
        "line": "Gaps can be closed by adding to the teeth with bonding or veneers, or by moving them with aligners. The right choice depends on the gap and your bite.",
        "notice": [("A space you see in photos", "Most often between the two front teeth."),
                   ("Food catching", "Food collects in the space when you eat."),
                   ("Gaps that grow", "A gap that widens with time can mean the gums or bite need checking."),
                   ("Speech", "Some people notice a slight whistle on certain sounds.")],
        "fix": [("cosmetic-dentistry", "Bonding", "Tooth-coloured material added to the edges of the teeth to close a small gap."),
                ("cosmetic-dentistry", "Veneers", "Thin porcelain facings that change the width and shape of the front teeth."),
                ("invisalign", "Aligners", "Clear trays that move the teeth together, without adding to them.")],
        "clinic": ("arha-dental-care-logo-wall", "The Arha Dental Care emblem in gold on the reception’s marble wall"),
        "tech": ["planning-desk", "treatment-rooms"],
        "faq": [("Will the gap come back?", "After aligners, a retainer keeps the teeth where they are. Bonding and veneers do not move, but are checked at your regular visits."),
                ("Can a large gap be closed with bonding?", "Bonding suits small gaps best. A large gap may look better closed by moving the teeth, or with veneers, so the teeth keep natural proportions."),
                ("Do gaps mean gum disease?", "Usually not, but a new gap, or one that is growing, should be checked because gum problems can let teeth move.")],
    },
    "crooked-teeth": {
        "name": "Crooked teeth", "menu": "Crooked teeth",
        "hero": ("stock-aligner", "A clear aligner on a pale background", "50% 50%"),
        "line": "Teeth can be straightened at almost any age, with clear aligners or with braces. Straighter teeth are also easier to keep clean.",
        "notice": [("Overlapping teeth", "Teeth that sit in front of or behind their neighbours."),
                   ("Hard-to-clean corners", "Floss and the toothbrush struggle to reach between crowded teeth."),
                   ("Uneven wear", "Teeth that meet at an angle can wear faster."),
                   ("Your bite", "The upper and lower teeth may not meet evenly when you close.")],
        "fix": [("invisalign", "Clear aligners", "A series of clear trays you change as your teeth move. You take them out to eat and clean."),
                ("orthodontics", "Braces", "Brackets fixed to the teeth and joined by a wire, adjusted at regular visits."),
                ("smile-design", "Smile design", "When straightening is part of a wider plan for the shape and colour of the smile.")],
        "tech": ["planning-desk", "panoramic-x-ray"],
        "faq": [("Am I too old for straighter teeth?", "Adults straighten their teeth every day. What matters is the health of your gums and bone, which we check first."),
                ("Aligners or braces?", "Both move teeth well. Aligners are nearly invisible and removable, but need wearing most of the day; braces stay on and suit some movements better. We tell you which suits your teeth."),
                ("Will my teeth move back?", "Teeth naturally tend to move, so everyone wears a retainer after treatment to hold the result.")],
    },
    "stained-teeth": {
        "name": "Yellow or stained teeth", "menu": "Yellow or stained teeth",
        "hero": ("stock-shade-guide", "A tooth shade guide on a dental lab table, beside fine brushes and porcelain", "50% 22%"),
        "line": "Surface stains often lift with a professional clean. Deeper colour responds to whitening, and where whitening cannot help, bonding or veneers can.",
        "notice": [("Surface stains", "From tea, coffee, paan or smoking, often at the edges and between teeth."),
                   ("An even yellow tone", "Teeth naturally darken a little with age."),
                   ("One darker tooth", "A single tooth that has changed colour should be checked, as it can follow an old knock."),
                   ("White or brown patches", "Spots in the enamel that whitening alone may not change.")],
        "fix": [("general-dentistry", "A professional clean", "Removes surface stain and tartar; often the first step."),
                ("cosmetic-dentistry", "Whitening", "Lightens the natural colour of the teeth, under our supervision."),
                ("cosmetic-dentistry", "Bonding or veneers", "For colour that whitening cannot change, or when shape matters too.")],
        "clinic": ("arha-dental-care-reception-wide", "The reception and waiting area, with the emblem wall and a plant"),
        "tech": ["treatment-rooms"],
        "faq": [("Does whitening damage the teeth?", "Supervised whitening is designed to be safe for enamel. Some people feel short-lived sensitivity, which settles. We check your teeth and gums first."),
                ("Will crowns and fillings whiten?", "No. Whitening changes natural teeth only, so existing crowns or fillings may need replacing to match afterwards."),
                ("How white will my teeth get?", "It depends on your teeth. We aim for a shade that looks natural with your skin and smile, never paper-white.")],
    },
    "toothache": {
        "name": "Toothache or sensitivity", "menu": "Toothache or sensitivity", "urgent": True,
        "hero": ("stock-xray-screen", "A dental X-ray of the whole mouth on a monitor beside the chair", "50% 50%"),
        "line": "Sensitivity can come from worn enamel or receding gums; pain that lingers often means decay has reached the nerve. An exam and an X-ray tell which it is.",
        "notice": [("A short, sharp twinge", "With cold or sweet food, gone in seconds."),
                   ("Pain that lingers", "An ache that stays after the cold or heat has gone."),
                   ("Pain on biting", "A sharp pain when you bite down on one tooth."),
                   ("Throbbing or swelling", "Pain that wakes you, or a swollen gum or face, needs to be seen soon.")],
        "fix": [("general-dentistry", "A filling", "When decay has not reached the nerve, the tooth is cleaned and filled."),
                ("root-canal-treatment", "Root canal treatment", "When the nerve is inflamed or infected, it is removed and the tooth is saved."),
                ("crowns-bridges", "A crown", "To protect a cracked tooth, or a back tooth after root canal treatment.")],
        "tech": ["panoramic-x-ray", "treatment-rooms"],
        "faq": [("Should I wait for toothache to pass?", "Pain that comes and goes can still be a problem growing quietly. Pain that lingers, wakes you or comes with swelling should be seen soon."),
                ("Is root canal treatment painful?", "It is done with local anaesthetic and is usually no more uncomfortable than a filling. It relieves the pain of an inflamed nerve."),
                ("Can sensitive toothpaste fix it?", "It helps sensitivity from exposed roots or worn enamel. It does not treat decay or a cracked tooth, so a check-up is still worthwhile.")],
    },
    "bleeding-gums": {
        "name": "Bleeding gums", "menu": "Bleeding gums",
        "hero": ("stock-floss-hand", "A coil of dental floss in an open hand, one strand drawn out", "50% 55%"),
        "line": "Gums that bleed when you brush are usually inflamed, and that is treatable. A professional clean and better care at home often settle it.",
        "notice": [("Pink in the sink", "Bleeding when you brush or floss."),
                   ("Red or puffy gums", "Healthy gums are pale pink and firm."),
                   ("Bad breath", "Breath that does not freshen after brushing."),
                   ("Gums pulling back", "Teeth that look longer, or feel loose.")],
        "fix": [("general-dentistry", "A professional clean", "Removes the tartar and plaque that keep the gums inflamed."),
                ("general-dentistry", "Gum care", "Deeper cleaning and closer reviews when the gums need more help."),
                ("general-dentistry", "Care at home", "Brushing, flossing and the right tools, shown at your visit.")],
        "clinic": ("arha-dental-care-steriliser", "Arha’s steriliser on the counter of the sterilisation room"),
        "tech": ["treatment-rooms", "sterilisation-room"],
        "faq": [("Should I stop brushing where it bleeds?", "No. Keep brushing gently, twice a day, and clean between the teeth. Bleeding usually settles as the gums heal."),
                ("Is bleeding serious?", "It is common and treatable, but left alone, gum disease can loosen teeth. It is worth a check."),
                ("How often should I have a clean?", "It depends on your gums. We suggest an interval that suits you after we have seen them.")],
    },
    "metal-fillings": {
        "name": "Old metal fillings", "menu": "Old metal fillings",
        "hero": ("stock-steel-instruments", "Fine steel dental instruments laid side by side", "50% 50%"),
        "line": "Old metal fillings can crack, or leak at the edges, over the years. When one needs replacing, it can be redone in tooth-coloured material, or with a crown.",
        "notice": [("A dark grey tooth", "Metal can show through the enamel around it."),
                   ("Cracks around a filling", "Fine lines in the tooth next to an old filling."),
                   ("Sensitivity", "A twinge with cold, or on biting, near the filling."),
                   ("A rough edge", "A filling that feels worn or catches the floss.")],
        "fix": [("general-dentistry", "A tooth-coloured filling", "When the filling is small or medium, it is replaced in a composite that matches the tooth."),
                ("crowns-bridges", "A crown or onlay", "When a large filling has weakened the tooth, a cap protects what is left."),
                ("general-dentistry", "Watching it", "A sound filling with no decay can stay; we check it at your visits.")],
        "clinic": ("arha-dental-care-equipment-counter", "Equipment on the counter of Arha’s sterilisation room"),
        "tech": ["panoramic-x-ray", "treatment-rooms"],
        "faq": [("Should all my metal fillings be replaced?", "No. A filling that is sound, with no decay or cracks around it, can stay. We replace fillings when there is a reason to."),
                ("Are tooth-coloured fillings strong?", "Modern composites are strong enough for most back teeth. For a very large filling, a crown or onlay may protect the tooth better."),
                ("Will it look natural?", "The material is matched to the shade of your tooth, so the repair is hard to see.")],
    },
    "loose-dentures": {
        "name": "Loose or uncomfortable dentures", "menu": "Loose dentures",
        "hero": ("stock-denture-dark", "A full denture with pink gum, photographed against a dark background", "50% 50%"),
        "line": "A denture that moves when you eat or speak can be held firmly by a few implants. Sometimes a refit or a new denture is enough.",
        "notice": [("Movement when you eat", "The denture lifts or rocks when you chew."),
                   ("Sore spots", "Places on the gums that hurt where the denture presses."),
                   ("Avoiding foods", "Leaving out foods you used to enjoy."),
                   ("Speech", "Clicking, or the denture slipping, when you talk.")],
        "fix": [("full-mouth-rehabilitation", "A refit or new denture", "The fit is adjusted to how your gums have changed, or a new denture is made."),
                ("dental-implants", "Implant-retained denture", "Two or more implants hold the denture firmly; you still take it out to clean."),
                ("dental-implants", "Fixed implant teeth", "A full arch of teeth fixed to implants, for some patients.")],
        "clinic": ("arha-dental-care-reception-desk", "Arha’s front desk under the gold emblem"),
        "tech": ["panoramic-x-ray", "planning-desk"],
        "faq": [("Why has my denture become loose?", "The gums and bone under a denture slowly change shape, so a denture that once fitted well can loosen. A refit or a new denture helps."),
                ("Can I have implants if I have worn dentures for years?", "Often, yes. It depends on the bone, which an X-ray shows."),
                ("Do I take an implant-retained denture out?", "Yes, to clean it and the implants. It clips firmly onto the implants when it is in.")],
    },
    "child-teeth": {
        "name": "My child’s teeth", "menu": "My child’s teeth",
        "hero": ("stock-kids-brushes", "Four small children's toothbrushes in soft colours, standing in a row", "50% 45%"),
        "line": "Baby teeth hold space for the adult teeth and matter for eating and speech. Regular checks, sealants and fluoride help stop decay early.",
        "notice": [("The first teeth", "Usually from around six months; the first visit can follow soon after."),
                   ("Marks or spots", "White, brown or dark patches on the teeth."),
                   ("Crowding", "Adult teeth coming in crooked or behind the baby teeth."),
                   ("Habits", "Thumb-sucking or a dummy beyond the early years.")],
        "fix": [("kids-dentistry", "Check-ups", "Gentle visits that let your child get used to the dentist."),
                ("kids-dentistry", "Sealants and fluoride", "Protection for the grooves of the back teeth, and stronger enamel."),
                ("orthodontics", "An early orthodontic check", "Spotting bite or crowding problems while the jaws are still growing.")],
        "clinic": ("arha-dental-care-entrance-door", "The door of suite 107 at Doctor House, with the Arha emblem"),
        "tech": ["treatment-rooms", "panoramic-x-ray"],
        "faq": [("When should my child first see a dentist?", "Around the time the first tooth appears, or by their first birthday. Early visits are short and gentle."),
                ("Do baby teeth need fillings?", "Often, yes. Baby teeth hold space for the adult teeth, and decay in them can hurt and spread."),
                ("Are dental X-rays safe for children?", "X-rays are taken only when needed, with the lowest exposure that shows what we need to see.")],
    },
}
ORDER = list(PROBLEMS)

EXPECT = [("A conversation", "You tell us what is bothering you and what you would like. We listen before we look."),
          ("An examination", "A careful look at the teeth, gums and bite, with X-rays if they are needed."),
          ("Your options, explained", "What each option involves, how it would look and feel, and what it costs, so you can decide calmly."),
          ("A plan made for you", "The number of visits and the timing are agreed with you at the consultation, never guessed in advance.")]


# ------------------------------------------------------------------ interactives (site.js 19)
def pic(name, alt, sizes="(min-width: 900px) 60vw, 100vw", pos=None, i=""):
    return picture(name, sizes, alt, pos=pos, indent=i)


def xfade(slug, options, rows, variant="tabs", label="Choose an option", note=""):
    """A photo toggle: options are tabs; their photographs crossfade on one stage, and the rows below
    say how the chosen option differs. options: (key, label, photo, alt); rows: (row label, {key: text})."""
    tabs = "".join(f'<button type="button" role="tab" id="{slug}-t-{k}" aria-controls="{slug}-p-{k}" aria-selected="{str(n == 0).lower()}"'
                   f'{"" if n == 0 else " tabindex=\"-1\""}>{lab}</button>' for n, (k, lab, _p, _a) in enumerate(options))
    shots = "".join(f'\n        <div class="xfade__img{" is-active" if n == 0 else ""}" data-for="{slug}-p-{k}">{pic(p, a, "(min-width: 900px) 55vw, 100vw")}</div>'
                    for n, (k, _l, p, a) in enumerate(options))
    panels = ""
    for n, (k, lab, _p, _a) in enumerate(options):
        dl = "".join(f"<div><dt>{r}</dt><dd>{vals[k]}</dd></div>" for r, vals in rows)
        panels += f'\n        <div class="xfade__panel" role="tabpanel" id="{slug}-p-{k}" aria-labelledby="{slug}-t-{k}"{"" if n == 0 else " hidden"}><h3>{lab}</h3><dl>{dl}</dl></div>'
    nt = f'\n        <p class="ix-note">{note}</p>' if note else ""
    return f"""      <div class="xfade xfade--{variant} reveal" data-tabs data-xfade>
        <div class="xfade__stage media">{shots}
        </div>
        <div class="xfade__side">
          <div class="xfade__tabs" role="tablist" aria-label="{label}">{tabs}</div>{panels}{nt}
        </div>
      </div>"""


def ix_missing():
    return xfade("mt", [("implant", "Implant", "stock-implant-hand", "A gloved hand holding a dental implant post with its crown"),
                        ("bridge", "Bridge", "stock-implant-bridge", "A dental bridge being made on a plaster model of the teeth"),
                        ("denture", "Denture", "stock-denture-hand", "A hand holding a partial denture with pink gum and two teeth")],
                 [("Fixed or removable", {"implant": "Fixed. It stays in, like a natural tooth.", "bridge": "Fixed. It is cemented in place.", "denture": "Removable. You take it out to clean it."}),
                  ("The teeth beside the gap", {"implant": "Left untouched.", "bridge": "Shaped to hold the crowns that support the bridge.", "denture": "Untouched, or used for small clasps."}),
                  ("How long it lasts", {"implant": "Many years with good care and regular checks.", "bridge": "Many years with good care; the supporting teeth must stay healthy.", "denture": "Several years; it is refitted or remade as the gums change."})],
                 label="How the gap is replaced", note="General information. Which option suits you depends on your gums, your bone and the teeth around the gap.")


def ix_chipped():
    lens = pic("stock-veneers-grey", "Four thin porcelain veneers on dark leather", "(min-width: 900px) 70vw, 100vw")
    return f"""      <div class="loupe-wrap reveal">
        <figure class="loupe" data-loupe tabindex="0" aria-label="Magnifier. Move over the photograph, or use the arrow keys, to look closely at the porcelain veneers.">
          {lens}
          <span class="loupe__lens" aria-hidden="true"></span>
          <figcaption class="loupe__hint">Move over the photograph · drag on a phone · arrow keys</figcaption>
        </figure>
        <div class="compare2">
          <div><h3>Bonding</h3><p>Tooth-coloured material is shaped onto the chipped edge and polished, usually in one visit. Best for small chips.</p><a class="link" href="cosmetic-dentistry/">Cosmetic dentistry{ARROW}</a></div>
          <div><h3>A crown</h3><p>A cap that covers the whole tooth, made to match. Best when a larger part of the tooth has broken.</p><a class="link" href="crowns-bridges/">Crowns &amp; bridges{ARROW}</a></div>
        </div>
      </div>"""


def ix_gaps():
    items = [("stock-veneer-placing", "50% 50%", "A fine brush placing a thin tooth-coloured facing on a dental model", "Bonding",
              "Tooth-coloured material added to the sides of the teeth. Quick and conservative, for small gaps.", "cosmetic-dentistry/", "Cosmetic dentistry"),
             ("stock-veneers", "50% 50%", "Thin porcelain veneers resting on a dark surface", "Veneers",
              "Thin porcelain facings that reshape the front teeth, closing gaps while improving shape and colour.", "cosmetic-dentistry/", "Cosmetic dentistry"),
             ("stock-aligner-gloved", "50% 50%", "A clear aligner held in a gloved hand beside its blue case", "Aligners",
              "Clear trays that move the teeth together. Nothing is added to the teeth.", "invisalign/", "Invisalign clear aligners")]
    lis = "".join(f"""
        <li class="xpanel{' is-active' if n == 0 else ''}" data-xpanel tabindex="0">
{picture(name, '(min-width: 900px) 50vw, 100vw', alt, pos=pos, indent='          ')}
          <div class="xpanel__body">
            <h3>{title}</h3>
            <div class="xpanel__more">
              <p>{text}</p>
              <a class="link link--light" href="{href}">{cta}</a>
            </div>
          </div>
        </li>""" for n, (name, pos, alt, title, text, href, cta) in enumerate(items))
    return f'      <ul class="xpanels xpanels--ix reveal" data-xpanels>{lis}\n      </ul>'


def blend(slug, a, b, start, end, label, tag, ticks=None, cls=""):
    ts = "".join(f"<span>{t}</span>" for t in (ticks or [start, end]))
    return f"""      <div class="blend {cls} reveal" data-blend style="--mix: 0">
        <div class="blend__stage media" data-colour-group>
          <div class="blend__a">{pic(*a, "(min-width: 900px) 70vw, 100vw")}</div>
          <div class="blend__b">{pic(*b, "(min-width: 900px) 70vw, 100vw")}</div>
          <p class="blend__tag">{tag}</p>
        </div>
        <label class="blend__control" for="{slug}-mix">
          <span class="visually-hidden">{label}</span>
          <input id="{slug}-mix" type="range" min="0" max="100" value="0" step="1" aria-valuetext="{start}">
          <span class="blend__ticks" aria-hidden="true">{ts}</span>
        </label>
      </div>"""


def ix_crooked():
    """A scrubber across the screen in Arha's treatment room (arha-dental-care-scan-screen): a focus ring
    moves from one 3D arch to the next and the text follows (site.js 19, [data-scan]). data-points are
    fractions of the 4:3 stage (the square photograph cropped top and bottom): x, y and the ring's radius (of the width)."""
    steps = [("Scan", "Your teeth in 3D", "Your teeth are recorded and shown as a 3D model on the screen in the treatment room."),
             ("Plan", "Each movement, planned", "The planning software moves the teeth in small steps, so you can see how they would straighten."),
             ("Result", "Where they could end up", "You see the planned result before anything starts, and decide with us whether it is right for you.")]
    texts = "".join(f'<div class="scan__text" data-step="{k}"{"" if k == 0 else " hidden"}><h3>{t}</h3><p>{x}</p></div>' for k, (_s, t, x) in enumerate(steps))
    ticks = "".join(f"<span>{s}</span>" for s, _t, _x in steps)
    return f"""      <div class="scan reveal" data-scan data-points="0.305 0.537 0.1, 0.5 0.543 0.105, 0.815 0.575 0.145">
        <figure class="scan__stage media">
          {pic("arha-dental-care-scan-screen", "The screen in an Arha treatment room, showing three 3D models of an upper arch of teeth", "(min-width: 900px) 55vw, 100vw")}
          <span class="scan__focus" aria-hidden="true"></span>
          <figcaption class="scan__tag">Arha’s screen · a planning view</figcaption>
        </figure>
        <div class="scan__side">
          <label class="scan__control" for="ct-scan"><span class="visually-hidden">Move across the screen</span>
            <input id="ct-scan" type="range" min="0" max="100" value="0" step="1" aria-valuetext="{steps[0][1]}">
          </label>
          <div class="scan__ticks" aria-hidden="true">{ticks}</div>
          <div class="scan__texts" aria-live="polite">{texts}</div>
          <p class="ix-note">Photographed on the screen in our treatment room. A planning view, not a patient’s result.</p>
        </div>
      </div>
      <div class="compare2 reveal">
        <div><h3>Clear aligners</h3><p>Nearly invisible trays, changed as the teeth move. Removable for eating and cleaning; worn most of the day.</p><a class="link" href="invisalign/">Invisalign clear aligners{ARROW}</a></div>
        <div><h3>Braces</h3><p>Brackets and a wire that stay on and are adjusted at visits. Suit some movements better.</p><a class="link" href="orthodontics/">Orthodontics (braces){ARROW}</a></div>
      </div>"""


def ix_stained():
    return blend("st", ("stock-sim-whiten-before", "A smile with yellowed teeth"),
                 ("stock-sim-whiten-after", "The same smile with the teeth whitened (simulation)"),
                 "Today", "After whitening", "Whitening simulation: slide to lighten the teeth", "Simulation",
                 ticks=["Today", "After whitening (simulation)"], cls="blend--shade") + """
      <p class="ix-note reveal">A simulation on a stock photograph, not a promise of a shade. How far your teeth lighten depends on your teeth; we aim for a colour that looks natural with your smile.</p>"""


def ix_toothache():
    opts = [("cold", "Sensitivity to cold or hot"), ("bite", "Pain when I bite"), ("night", "Throbbing, or pain that wakes me"), ("swelling", "Swelling in my gum or face")]
    boxes = "".join(f'<label class="chip-check"><input type="checkbox" name="symptom" value="{v}"><span>{t}</span></label>' for v, t in opts)
    results = [("any:swelling", "Please call us today", "Swelling can mean an infection that needs to be seen soon. If your face is swelling fast, you have a fever, or you find it hard to swallow or breathe, go to a hospital emergency department.", "emergency/", "Dental emergencies"),
               ("any:night", "Book an urgent appointment", "Throbbing pain, or pain that wakes you, often means the nerve is inflamed. Root canal treatment can usually save the tooth.", "root-canal-treatment/", "Root canal treatment"),
               ("any:bite", "Have it checked soon", "Pain when you bite can come from a cracked tooth, a deep filling or an inflamed root. An exam and an X-ray tell which.", "crowns-bridges/", "Crowns &amp; bridges"),
               ("any:cold", "Book a check-up", "A short twinge with cold or heat is often from worn enamel or a receding gum. Pain that lingers after the cold has gone should be seen sooner.", "general-dentistry/", "General dentistry")]
    res = "".join(f'<div class="picker__result" data-if="{c}" hidden><p class="picker__step">{h}</p><p>{t}</p><a class="link" href="{href}">{cta}{ARROW}</a></div>' for c, h, t, href, cta in results)
    return f"""      <div class="ix-split ix-split--picker reveal">
        <div class="ix-split__media media">{pic("arha-dental-care-xray-room", "Arha’s X-ray room: a panoramic X-ray unit against a marble wall", "(min-width: 900px) 40vw, 100vw")}</div>
        <form class="picker" data-checklist aria-labelledby="picker-legend">
          <fieldset>
            <legend id="picker-legend">What do you feel? Tick all that apply.</legend>
            <div class="chip-checks">{boxes}</div>
          </fieldset>
          <div class="picker__results" aria-live="polite">
            <div class="picker__result" data-if="none"><p class="picker__step">Your likely next step</p><p>Tick what you feel to see what we would usually suggest.</p></div>{res}
          </div>
          <p class="ix-flag">Not a diagnosis. Only an examination and an X-ray can tell what is causing the pain.</p>
        </form>
      </div>"""


def ix_gums():
    qs = [("bleed", "Do your gums bleed when you brush or floss?"), ("red", "Are your gums red, puffy or tender?"), ("breath", "Do you notice bad breath, or gums pulling back from the teeth?")]
    fields = "".join(f"""
            <fieldset class="quiz__q"><legend><span>{n + 1:02d}</span>{q}</legend>
              <label><input type="radio" name="{k}" value="yes"><span>Yes</span></label><label><input type="radio" name="{k}" value="no"><span>No</span></label>
            </fieldset>""" for n, (k, q) in enumerate(qs))
    return f"""      <div class="ix-split ix-split--quiz reveal">
        <div class="ix-split__media media">{pic("stock-brushes-grey", "Two soft toothbrushes and their box on a grey-green surface", "(min-width: 900px) 45vw, 100vw")}</div>
        <form class="quiz" data-quiz aria-label="Gum self-check">{fields}
          <div class="quiz__results" aria-live="polite">
            <p class="quiz__result" data-score="pending">Answer the three questions to see your result.</p>
            <div class="quiz__result" data-score="0" hidden><p class="picker__step">Your gums sound healthy</p><p>Keep brushing twice a day and cleaning between the teeth, and come for your regular check-up and clean.</p><a class="link" href="general-dentistry/">General dentistry &amp; cleaning{ARROW}</a></div>
            <div class="quiz__result" data-score="1" hidden><p class="picker__step">Worth a check and a clean</p><p>One sign on its own is common and usually settles with a professional clean and good care at home.</p><a class="link" href="general-dentistry/#gum-care">Gum care{ARROW}</a></div>
            <div class="quiz__result" data-score="2" hidden><p class="picker__step">Book a gum check soon</p><p>Two or more signs suggest your gums are inflamed. It is treatable, and the sooner it is seen the easier it is.</p><a class="link" href="general-dentistry/#gum-care">Gum care{ARROW}</a></div>
          </div>
          <p class="ix-flag">Not a diagnosis. Nothing you choose is stored or sent.</p>
        </form>
      </div>"""


def ix_metal():
    return xfade("mf", [("metal", "Metal", "stock-handpieces-dark", "Steel dental handpieces in their holder: metal, as a material"),
                        ("white", "Tooth-coloured", "stock-bridge-white", "Three tooth-coloured restorations joined as one piece, shown on their own")],
                 [("How it looks", {"metal": "Dark grey; it can show through the tooth.", "white": "Matched to the shade of the tooth."}),
                  ("How it is held", {"metal": "Packed into a shaped cavity.", "white": "Bonded to the tooth, so less of it is drilled away."}),
                  ("When we replace one", {"metal": "When it is cracked, leaking or has decay beneath it.", "white": "It is placed when an old filling needs replacing."})],
                 variant="switch", label="Filling material")


def ix_dentures():
    return xfade("ld", [("conventional", "Conventional", "stock-denture-hand", "A removable denture with pink gum, held in the hand"),
                        ("implant", "Implant-retained", "stock-implant-overdenture", "A denture on a model, with the clips that attach it to implants")],
                 [("What holds it", {"conventional": "The fit against the gums, and sometimes adhesive.", "implant": "Two or more implants it clips onto."}),
                  ("When you eat and talk", {"conventional": "It can lift or rock, especially a lower denture.", "implant": "It stays firmly in place."}),
                  ("Over the years", {"conventional": "Refitted or remade as the gums change.", "implant": "The implants help preserve the bone beneath."})],
                 variant="split", label="Type of denture")


def ix_child():
    bands = [(0, 2, "Birth to 2", "stock-kid-brush-wood", "A small wooden toothbrush with soft red bristles", "The first teeth arrive. Book the first visit around the first tooth or the first birthday, and wipe or brush the teeth twice a day."),
             (3, 5, "3 to 5 years", "stock-child-brush", "A young boy brushing his teeth", "All the baby teeth are in. Short check-ups, fluoride and help with brushing; watch for sweet drinks."),
             (6, 9, "6 to 9 years", "stock-kid-brush-electric", "A children’s electric toothbrush with a bright pattern", "The first adult molars come through. Sealants protect their grooves; an early orthodontic check spots crowding."),
             (10, 12, "10 to 12 years", "stock-aligners-shadow", "Clear aligners on a model, in soft shadow", "The last baby teeth go. A good time to plan braces or aligners if the bite needs it."),
             (13, 18, "Teenagers", "stock-kid-brush-bright", "A bright toothbrush with yellow bristles", "Adult teeth in place. Regular cleans, sports mouthguards, and straightening if wanted.")]
    shots = "".join(f'\n          <div class="agedial__img{" is-active" if n == 0 else ""}" data-band="{n}">{pic(p, a, "(min-width: 900px) 45vw, 100vw")}</div>' for n, (_a, _b, _l, p, a, _t) in enumerate(bands))
    texts = "".join(f'\n          <div class="agedial__text" data-band="{n}" data-min="{lo}" data-max="{hi}"{"" if n == 0 else " hidden"}><h3>{lab}</h3><p>{t}</p></div>' for n, (lo, hi, lab, _p, _a, t) in enumerate(bands))
    return f"""      <div class="agedial reveal" data-agedial>
        <div class="agedial__stage media">{shots}
        </div>
        <div class="agedial__side">
          <label class="agedial__control" for="age-dial"><span class="agedial__label">Your child’s age: <output for="age-dial" data-age-out>1</output></span>
            <input id="age-dial" type="range" min="0" max="18" value="1" step="1" aria-valuetext="1 year">
          </label>
          <div class="agedial__scale" aria-hidden="true"><span>0</span><span>6</span><span>12</span><span>18</span></div>{texts}
          <a class="link" href="kids-dentistry/">Kids’ dentistry{ARROW}</a>
        </div>
      </div>"""


INTERACTIVES = {
    "missing-tooth": ("Implant, bridge or denture?", "Choose an option to see it, and how it compares.", ix_missing),
    "chipped-tooth": ("Look closely", "Move the magnifier over the veneers to see how fine the porcelain is, then compare the two usual repairs.", ix_chipped),
    "gaps": ("Three ways to close a gap", "Hover or tap each one to see how it works.", ix_gaps),
    "crooked-teeth": ("From crowded to straight, planned on screen", "Slide across the screen in our treatment room to follow an aligner plan.", ix_crooked),
    "stained-teeth": ("See what whitening can do", "Slide to lighten the teeth in this simulation.", ix_stained),
    "toothache": ("What is the pain telling you?", "Tick what you feel to see the likely next step.", ix_toothache),
    "bleeding-gums": ("A gum self-check", "Three questions you can answer at home.", ix_gums),
    "metal-fillings": ("Metal or tooth-coloured?", "Switch between the two to compare.", ix_metal),
    "loose-dentures": ("Conventional or implant-retained?", "Choose one to see it, and the three main differences.", ix_dentures),
    "child-teeth": ("What to expect at each age", "Slide to your child’s age.", ix_child),
}


# ------------------------------------------------------------------ page parts
def notice(p):
    items = "".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a, b in p["notice"])
    return f"""
    <!-- =================================================================== WHAT YOU MAY NOTICE -->
    <section class="section notice" aria-labelledby="notice-title">
      <div class="container">
        <div class="section-head reveal"><h2 id="notice-title">What you may notice</h2></div>
        <ul class="notice__list reveal">{items}</ul>
      </div>
    </section>
"""


def fix_block(p):
    cards = "".join(f"""
          <li class="fix__item">
            <h3>{opt}</h3>
            <p>{text}</p>
            <a class="link" href="{slug}/">{NAMES[slug]}{ARROW}</a>
          </li>""" for slug, opt, text in p["fix"])
    return f"""
    <!-- =================================================================== HOW WE USUALLY FIX IT -->
    <section class="section fix" aria-labelledby="fix-title">
      <div class="container">
        <div class="section-head reveal"><h2 id="fix-title">How we usually fix it</h2><p class="lede">The options, side by side. Which suits you is decided together, after an examination.</p></div>
        <ul class="fix__list reveal">{cards}
        </ul>
      </div>
    </section>
"""


def expect_block(clinic=None):
    """The four steps of a first visit; with clinic (photo, alt), Arha's own room beside them."""
    steps = "".join(f"<li><p class=\"expect__num\">{n + 1:02d}</p><h3>{t}</h3><p>{b}</p></li>" for n, (t, b) in enumerate(EXPECT))
    head = '<div class="section-head reveal"><h2 id="expect-title">What to expect</h2><p class="lede">Visits and timing are decided at your consultation.</p></div>'
    if not clinic:
        return f"""
    <!-- =================================================================== WHAT TO EXPECT -->
    <section class="section section--stone expect" aria-labelledby="expect-title">
      <div class="container">
        {head}
        <ol class="expect__list reveal">{steps}</ol>
      </div>
    </section>
"""
    return f"""
    <!-- =================================================================== WHAT TO EXPECT (beside Arha's own room) -->
    <section class="section section--stone expect expect--photo" aria-labelledby="expect-title">
      <div class="container-wide expect__grid">
        <figure class="expect__media media reveal">
{picture(clinic[0], "(min-width: 900px) 40vw, 100vw", clinic[1], indent="          ")}
          <figcaption>At Arha, Peddar Road</figcaption>
        </figure>
        <div class="expect__body">
          {head}
          <ol class="expect__list reveal">{steps}</ol>
        </div>
      </div>
    </section>
"""


def tech_list(slugs, title="Technology used"):
    items = [t for t in technology.ITEMS if t["slug"] in slugs]
    lis = "".join(f"""
          <li><a href="technology/#{t['slug']}"><span class="techlist__name">{t['short']}</span><span class="techlist__for">{t['for_you']}</span></a></li>""" for t in items)
    return f"""
    <!-- =================================================================== TECHNOLOGY USED -->
    <section class="section techlist" aria-labelledby="techlist-title">
      <div class="container">
        <div class="section-head reveal"><p class="eyebrow">Technology &amp; innovation</p><h2 id="techlist-title">{title}</h2></div>
        <ul class="techlist__list reveal">{lis}
        </ul>
      </div>
    </section>
"""


def problem_page(slug, site_url):
    import v4_pages  # page_hero; imported here because v4_pages imports this module
    p = PROBLEMS[slug]
    trail = [("Home", ""), ("What we fix", "problems/"), (p["name"], f"problems/{slug}/")]
    name, alt, pos = p["hero"]
    body = v4_pages.page_hero(f"{{{{pic {name} | 100vw | {alt} | pos={pos} | eager}}}}", p["name"], p["line"], trail, eyebrow="What we fix")
    if p.get("urgent"):
        body += """    <p class="urgent-line container">In severe pain, or swollen? <a class="link" href="emergency/">Dental emergencies</a></p>
"""
    body += notice(p)
    title, lede, make = INTERACTIVES[slug]
    body += f"""
    <!-- =================================================================== INTERACTIVE -->
    <section class="section section--stone ix ix--problem ix--{slug}" aria-labelledby="ix-title">
      <div class="container-wide">
        <div class="section-head reveal"><h2 id="ix-title">{title}</h2><p class="lede">{lede}</p></div>
{make()}
      </div>
    </section>
"""
    body += fix_block(p)
    body += expect_block(p.get("clinic"))
    body += tech_list(p["tech"])
    body += tp.faq_block(p["faq"])
    body += closing_band()
    meta = {"title": f"{p['name'].replace('’', '&#8217;')} | What We Fix | Arha Dental Care, Peddar Road",
            "description": html.escape(p["line"], quote=True),
            "jsonld": [tp.faq_jsonld(p["faq"]), tp.crumbs_jsonld(site_url, trail)]}
    return f"problems/{slug}", meta, f'  <main id="main" tabindex="-1">\n\n{body}\n  </main>\n'


def closing_band(title="Begin with a conversation", text="Every plan at Arha starts with a consultation: a careful examination, a clear explanation and a plan made for you."):
    """apa's dark band as punctuation: no photograph, the two actions (tools/treatment_pages.closing)."""
    return tp.closing(title, text)


def index_page(site_url):
    """/problems/: the ten problems as the large-type list, with the photo stage."""
    import v4_pages
    trail = [("Home", ""), ("What we fix", "problems/")]
    body = f"""
    <section class="section problems-index" aria-labelledby="page-title">
      <div class="container">
        {tp.crumbs(trail)}
        <div class="section-head reveal"><h1 id="page-title">What we fix</h1><p class="lede">Start with what is bothering you. Each page shows what treatment would involve.</p></div>
      </div>
    </section>
    <section class="section section--stone problem-links" aria-label="Problems we fix">
      <div class="container">
        <ul class="problem-links__list reveal">{"".join(f'<li><a href="problems/{s}/">{PROBLEMS[s]["menu"]}{ARROW}</a></li>' for s in ORDER)}</ul>
      </div>
    </section>
{closing_band()}"""
    meta = {"title": "What We Fix: Common Dental Problems | Arha Dental Care, Peddar Road",
            "description": "Missing, chipped, crooked or stained teeth, gaps, toothache, bleeding gums, old fillings, loose dentures and children's teeth: how Arha Dental Care on Peddar Road usually fixes each.",
            "jsonld": [tp.crumbs_jsonld(site_url, trail)]}
    _ = v4_pages
    return "problems", meta, f'  <main id="main" tabindex="-1">\n{body}\n  </main>\n'


# ------------------------------------------------------------------ homepage: What brings you in?
def brings_you_in(heading=True, i="    "):
    """The ten problems as a large-type list; hovering, focusing or tapping one crossfades its photograph,
    with one line and "See how we fix it". site.js 19 ([data-brings])."""
    items, shots = "", ""
    for n, slug in enumerate(ORDER):
        p = PROBLEMS[slug]
        name, alt, pos = p["hero"]
        items += f'\n{i}        <li><a class="brings__item{" is-active" if n == 0 else ""}" href="problems/{slug}/" data-i="{n}"><span class="brings__num">{n + 1:02d}</span>{p["menu"]}</a></li>'
        shots += f"""
{i}      <div class="brings__shot{' is-active' if n == 0 else ''}" data-i="{n}">
{picture(name, '(min-width: 900px) 55vw, 100vw', alt, pos=pos, indent=i + '        ')}
{i}        <div class="brings__caption">
{i}          <p>{p['line']}</p>
{i}          <a class="link link--light" href="problems/{slug}/" tabindex="-1">See how we fix it{ARROW}</a>
{i}        </div>
{i}      </div>"""
    head = (f'{i}      <p class="eyebrow">Common problems we fix</p>\n{i}      <h2 id="brings-title">What brings you in?</h2>\n') if heading else ""
    label = ' aria-labelledby="brings-title"' if heading else ' aria-label="What brings you in?"'
    return f"""{i}<!-- =================================================================== WHAT BRINGS YOU IN? (problems first) -->
{i}<section class="section brings" id="what-we-fix"{label}>
{i}  <div class="container-wide brings__grid" data-brings>
{i}    <div class="brings__list">
{head}{i}      <ol class="brings__items">{items}
{i}      </ol>
{i}    </div>
{i}    <div class="brings__stage">{shots}
{i}    </div>
{i}  </div>
{i}</section>"""


def all_pages(site_url):
    return [index_page(site_url)] + [problem_page(s, site_url) for s in ORDER]


def for_treatment(slug):
    """The problems a treatment page links back to."""
    return [(s, PROBLEMS[s]["menu"]) for s in ORDER if any(f[0] == slug for f in PROBLEMS[s]["fix"])]
