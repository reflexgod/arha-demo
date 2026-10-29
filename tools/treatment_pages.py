"""Treatment pages, the Treatments hub and the Technology page, built from data.

Used by tools/pages.py. Adding a treatment = add its entry to TREATMENTS (and its menu item in
tools/treatments.py). Every page has: hero, intro, its own interactive block, "Is this for you?",
how it works, technology used, cases for this treatment, visits and time, FAQs and the call/book CTA.
Facts used: only the brief, the clinic's current website (ITI-certified prosthodontist, implants,
rotary endodontics, ceramic/zirconia/PFM crowns, braces and aligners for all ages, kids' check-ups,
sealants, fluoride, early orthodontic assessment) and what Arha's photographs show. Visits and
timings are placeholders until Dr. Nikhil confirms them (notes/TO-CONFIRM.md).
"""
import html
import re
from pathlib import Path

import technology
import treatments
from picture import picture

ROOT = Path(__file__).resolve().parent.parent
ARROW = technology.ARROW
TBC = "To be confirmed by Dr. Nikhil"

# ------------------------------------------------------------------ content
TREATMENTS = {
    "dental-implants": {
        "title": "Dental Implants in South Mumbai | Arha Dental Care, Peddar Road",
        "description": "Prosthodontist-led dental implants on Peddar Road, Mumbai: single teeth, several teeth and implant-supported dentures, how they work and what to expect.",
        "h1": "Dental implants",
        "lede": "Replacing missing teeth with results that look, feel and work like your own.",
        "hero": ("stock-implant-hero", "A ceramic crown seated on a dental implant in a model of the jaw", "30% 50%"),
        "card": "One tooth, several, or a full arch, planned around the tooth you will see.",
        "intro": ("A tooth that feels like your own",
                  "An implant is a small post, usually titanium, that takes the place of a missing tooth’s root. Once it has settled into the jaw, a crown, bridge or denture is fixed on top.",
                  "Implant care at Arha is led by an ITI-certified prosthodontist, so the tooth you will see and use is planned first, and the implant is placed to support it."),
        "interactive": ("implants", "Inside an implant", "Tap a number on the photograph to see what each part does, then see how implants replace one tooth, several, or a full arch."),
        "who": [("One missing tooth", "A single implant and crown, without reshaping the healthy teeth on either side."),
                ("Several missing teeth", "Implants can carry a bridge, so fewer implants replace more teeth."),
                ("Loose or uncomfortable dentures", "A denture can be anchored to implants so it stays firmly in place."),
                ("A tooth that cannot be saved", "When a tooth has to come out, its replacement can be planned at the same time.")],
        "steps": [("Consultation", "We listen to what you want and examine your mouth, with the X-rays or scans needed to plan safely."),
                  ("Treatment planning", "The final tooth is designed first, then the implant position is planned around it."),
                  ("Implant placement", "The implant is placed at a pace that keeps you comfortable. We explain beforehand how your smile will look while you heal."),
                  ("Healing", "The bone gradually bonds with the implant. We review how it is settling."),
                  ("Your final tooth", "The crown, bridge or denture is made to match your smile and fitted with your bite checked carefully."),
                  ("Aftercare", "Regular reviews and cleaning protect the implant and the gum around it.")],
        "cases": "implants",
        "timing": ["Single tooth", "Several teeth", "Full arch", "Visiting from abroad"],
        "faq": [("Am I a candidate for implants?", "Most adults who have lost a tooth can be considered, but your gums, your bone and your general health all play a part. A consultation, with the X-rays or scans needed, is the only reliable way to know."),
                ("Does it hurt?", "Implant treatment is carried out with anaesthetic so that you are comfortable. We will explain exactly what to expect during and after treatment at your consultation."),
                ("How long does it take?", "Implant treatment happens in stages, with healing time in between. How long depends on your bone and the teeth involved; you will get a personal timeline at your consultation."),
                ("How long do implants last?", "Implants are a long-term replacement. Like natural teeth, they depend on good care at home and regular reviews, and the crown on top may need attention over the years."),
                ("What if I have bone loss?", "Bone loss does not always rule implants out. We will explain the options suited to you once we have seen your X-rays or scans."),
                ("Can I have implants if I live abroad?", "Yes. We begin with a virtual consultation, review any recent X-rays you have, and plan your visits to Mumbai before you travel.")],
        "planner": True,
    },
    "full-mouth-rehabilitation": {
        "title": "Full Mouth Rehabilitation in Mumbai | Arha Dental Care, Peddar Road",
        "description": "Full mouth rehabilitation on Peddar Road, Mumbai: rebuilding worn, broken or missing teeth and the bite, planned in phases by a prosthodontist.",
        "h1": "Full mouth rehabilitation",
        "lede": "Rebuilding a worn, broken or incomplete set of teeth, and the bite that holds them together.",
        "hero": ("stock-crowns", "Four ceramic crowns resting on a dark surface", "50% 55%"),
        "card": "Worn, broken or missing teeth rebuilt as one plan, phase by phase.",
        "intro": ("When the whole bite needs attention",
                  "Full mouth rehabilitation brings every tooth, and the way the teeth meet, back into balance. It combines treatments such as crowns, bridges, implants and fillings in one plan.",
                  "Because the bite is planned as a whole, each step fits the next. A prosthodontist leads the plan from the first records to the final teeth."),
        "interactive": ("phases", "The plan, phase by phase", "Each phase has its own purpose. Step through them to see what happens."),
        "who": [("Teeth worn down by grinding", "Short, flat or sensitive teeth that have lost their shape over the years."),
                ("Several broken or missing teeth", "Gaps and broken teeth that make chewing hard on both sides."),
                ("A bite that has collapsed", "Teeth that have drifted or shortened so the face looks older and the bite feels wrong."),
                ("Old dental work failing in many places", "Crowns, bridges and fillings that need replacing together, not one at a time.")],
        "steps": None,  # the phase stepper explains how it works
        "cases": "full-mouth",
        "timing": ["Planning phase", "Trial smile", "Final restorations", "Visiting from abroad"],
        "faq": [("How long does full mouth rehabilitation take?", "It is done in phases over several months, with time to test the new bite before anything is final. You will get a personal timeline once your plan is made."),
                ("Is it painful?", "Treatment is done with anaesthetic where needed, and in stages so each visit is manageable. We will explain what to expect at every step."),
                ("Will my teeth look natural?", "The shape, length and colour of the new teeth are designed around your face and tried in before the final work is made, so you can see and change them first."),
                ("Can it be done if I live abroad?", "Often, yes. It needs several visits, which we plan with you before you travel. A virtual consultation is the best first step.")],
        "planner": True,
    },
    "maxillofacial-prosthetics": {
        "title": "Maxillofacial Prosthetics in Mumbai | Arha Dental Care, Peddar Road",
        "description": "Maxillofacial prosthetics at Arha Dental Care, Peddar Road: custom prostheses that help restore eating, speech and appearance after surgery, injury or a condition present from birth.",
        "h1": "Maxillofacial prosthetics",
        "lede": "Custom prostheses that help restore eating, speaking and appearance when part of the mouth or jaw is missing.",
        "hero": ("stock-prosthesis-hands", "Gloved hands finishing a dental prosthesis with a fine instrument", "50% 45%"),
        "card": "Custom prostheses after surgery or injury, or for a condition from birth.",
        "intro": ("Care that goes beyond teeth",
                  "Maxillofacial prosthetics is the part of prosthodontics that replaces missing parts of the mouth and jaw with prostheses made for one person.",
                  "Each prosthesis is made, fitted and adjusted over several visits. Treatment is usually planned together with your surgeon or medical team."),
        "interactive": ("who-we-help", "Who we help", "Choose the situation closest to yours for a plain explanation."),
        "who": [("Part of the palate or jaw is missing", "After surgery or an injury, or from birth."),
                ("Eating or speaking has become hard", "Food or air escaping, or speech that is difficult to understand."),
                ("An existing prosthesis no longer fits", "Prostheses change as the mouth changes, and need refitting."),
                ("You are preparing for surgery", "Planning a prosthesis before surgery can make recovery easier.")],
        "steps": [("Consultation", "We listen, examine and talk with your surgeon or medical team, with your permission."),
                  ("Impressions and records", "Careful records of your mouth, taken gently and at your pace."),
                  ("Trial fitting", "The prosthesis is tried in and adjusted before it is finished."),
                  ("Fitting", "It is fitted, and you are shown how to care for it."),
                  ("Reviews", "Regular reviews keep it comfortable as your mouth changes.")],
        "cases": None,
        "timing": ["Number of visits", "Time to fitting", "Reviews"],
        "faq": [("Do I need a referral?", "You can contact us directly. If you are under a surgeon’s care, we will ask your permission to speak with them."),
                ("Will the prosthesis look natural?", "It is made and coloured to blend in as closely as possible. We will talk through what to expect for your situation."),
                ("Is it uncomfortable to wear?", "There is a settling-in period. Fittings and reviews are there to adjust it until it is comfortable."),
                ("How long does a prosthesis last?", "It depends on the type and on changes in your mouth. Regular reviews tell us when it needs adjusting or remaking.")],
        "planner": False,
    },
    "smile-design": {
        "title": "Smile Design in South Mumbai | Arha Dental Care, Peddar Road",
        "description": "Smile design at Arha Dental Care, Peddar Road, Mumbai: your smile planned around your face and previewed before any work begins.",
        "h1": "Smile design",
        "lede": "Your new smile, planned around your face and previewed before any work begins.",
        "hero": ("dental-operatory-arha-dental-care-peddar-road-04", "The planning desk in an Arha treatment room: a screen, a laptop and notes", "50% 50%"),
        "preview": ("stock-veneer-brush", "A veneer placed on a model with a fine brush", "50% 50%"),
        "card": "Your smile planned around your face, and previewed before work begins.",
        "intro": ("Planned first, then made",
                  "Smile design is the planning that comes before cosmetic treatment: the length, width, shape and colour of your teeth, considered with your lips, your face and your bite.",
                  "You see and approve the plan before any tooth is touched. The treatment that follows may be whitening, bonding, veneers, crowns or aligners, often a mix."),
        "interactive": ("guides", "How a smile is planned", "Everything is measured, planned and previewed before work starts. Turn on the design guides to see what we look at."),
        "who": [("Teeth of uneven length or shape", "Edges that do not follow your lip line, or teeth out of proportion."),
                ("Gaps, chips or worn edges", "Small flaws that add up across a smile."),
                ("A smile that shows too much or too little", "Tooth length and gum line considered together."),
                ("Old cosmetic work you are unhappy with", "Crowns or veneers that no longer look right.")],
        "steps": [("Consultation and photographs", "What you like and dislike about your smile, with photographs and records."),
                  ("Smile analysis and design", "Proportions, midline and smile line, planned around your face."),
                  ("Preview", "A mock-up lets you see the planned shape before anything is changed."),
                  ("Treatment", "The planned work is carried out, often in stages."),
                  ("Review", "We check the result, your bite and your comfort.")],
        "cases": "veneers",
        "timing": ["Planning and preview", "Treatment", "Visiting from abroad"],
        "faq": [("Will it look fake?", "The aim is the opposite: a smile in proportion with your face that looks like your own teeth on a good day. You see the plan before anything is done."),
                ("Do I have to have veneers?", "No. Smile design is a plan, not a treatment. Many smiles need only whitening, bonding or aligners."),
                ("Can I see the result first?", "Yes. A preview shows the planned shape before any work begins, and you can ask for changes."),
                ("How long does it take?", "It depends on the treatments in your plan. You will get a timeline once the design is agreed.")],
        "planner": False,
    },
    "cosmetic-dentistry": {
        "title": "Cosmetic Dentistry in Mumbai: Veneers, Whitening, Bonding | Arha Dental Care",
        "description": "Cosmetic dentistry at Arha Dental Care, Peddar Road: veneers, teeth whitening and bonding, chosen for what your teeth actually need.",
        "h1": "Cosmetic dentistry",
        "lede": "Veneers, whitening and bonding, chosen for what your teeth actually need.",
        "hero": ("stock-crowns-soft", "Ceramic restorations, softly lit", "50% 55%"),
        "card": "Veneers, whitening and bonding, matched to the concern.",
        "intro": ("The lightest treatment that does the job",
                  "Cosmetic dentistry improves the colour, shape and alignment of teeth. The best result often comes from the least invasive option.",
                  "Every option is explained at your consultation: what it involves, how it is looked after, and how long it can be expected to last."),
        "interactive": ("matrix", "Which fix for which concern", "Choose a concern to see which treatments usually suit it, and why."),
        "who": [("Yellow or stained teeth", "General yellowing, or stains that brushing does not shift."),
                ("Small chips and worn edges", "Edges that have chipped or worn unevenly."),
                ("Small gaps", "Spaces between front teeth."),
                ("Teeth of uneven shape", "Teeth that are short, narrow or out of proportion.")],
        "steps": [("Consultation", "What bothers you, what you would like, and an examination of teeth and gums."),
                  ("Planning", "Shade and shape planned together, with a preview where useful."),
                  ("Treatment", "Whitening, bonding or veneers, as agreed."),
                  ("Aftercare", "How to look after the result, and when to come back.")],
        "cases": "veneers",
        "timing": ["Whitening", "Bonding", "Veneers"],
        "faq": [("Is whitening safe for my teeth?", "Professional whitening is planned after an examination, with the strength and timing suited to your teeth. Some sensitivity for a short time is common."),
                ("How long do veneers last?", "Veneers are a long-term treatment that depends on care, habits such as grinding, and regular reviews. We will explain what to expect for you."),
                ("Does bonding stain?", "Bonding can pick up stains over time, more than porcelain. Polishing at check-ups helps keep it looking fresh."),
                ("Do teeth need drilling for veneers?", "Usually a thin layer of enamel is shaped so the veneer sits naturally. How much depends on your plan; some cases need very little.")],
        "planner": False,
    },
    "invisalign": {
        "title": "Invisalign Clear Aligners in South Mumbai | Arha Dental Care, Peddar Road",
        "description": "Invisalign clear aligners at Arha Dental Care, Peddar Road, Mumbai: straightening teeth with clear, removable aligners, for teens and adults.",
        "h1": "Invisalign clear aligners",
        "lede": "Straightening teeth with a series of clear, removable aligners.",
        "hero": ("stock-aligner-case-hand", "A clear aligner held in a gloved hand beside its open case", "50% 50%"),
        "card": "Clear, removable aligners for teens and adults.",
        "intro": ("Straighter teeth, almost unseen",
                  "Clear aligners are thin, clear trays made for your teeth. Each set moves them a little, and you change to the next set on a schedule.",
                  "Arha offers Invisalign, one brand of clear aligner. Aligners suit many adults and teens, but not every bite; your consultation will tell you whether they suit you, or whether braces would do better."),
        "interactive": ("aligners", "How aligners move teeth", "Step through treatment from scan to straighter teeth, then compare aligners with braces."),
        "who": [("Crowded or crooked teeth", "Teeth that overlap or turn."),
                ("Gaps", "Spaces that can be closed by moving the teeth."),
                ("Teeth that moved after braces", "Relapse after earlier orthodontic treatment."),
                ("Adults who prefer not to wear braces", "Treatment that fits work and social life.")],
        "steps": [("Consultation", "An examination to see whether aligners suit your teeth and bite."),
                  ("Records and plan", "Photographs, X-rays and impressions or a scan, then a digital plan of every stage."),
                  ("Aligners fitted", "You receive your first aligners and learn how to wear and clean them."),
                  ("Reviews", "Short visits to check progress and give you the next sets."),
                  ("Retainers", "Retainers hold the new position once treatment ends.")],
        "cases": "aligners",
        "timing": ["Typical treatment", "Reviews", "Visiting from abroad"],
        "faq": [("How many hours a day do I wear them?", "Most of the day and night, usually 20 to 22 hours. They come out only to eat, drink anything but water, and clean your teeth."),
                ("Do aligners hurt?", "Each new set can feel tight for a day or two as the teeth move. Most people find it easy to manage."),
                ("Can I eat with aligners in?", "No. You take them out to eat and drink anything but water, then brush before putting them back."),
                ("Will I need a retainer afterwards?", "Yes. Teeth tend to drift back, so a retainer keeps them in their new position.")],
        "planner": False,
    },
    "orthodontics": {
        "title": "Orthodontics and Braces in South Mumbai | Arha Dental Care, Peddar Road",
        "description": "Braces and clear aligners for children, teens and adults at Arha Dental Care, Peddar Road, Mumbai, with early orthodontic assessment for children.",
        "h1": "Orthodontics (braces)",
        "lede": "Braces and aligners for children, teens and adults.",
        "hero": ("stock-braces-model", "Metal braces on a model of the teeth", "50% 55%"),
        "card": "Metal braces and clear aligners for children, teens and adults.",
        "intro": ("Straight teeth at any age",
                  "Orthodontics moves teeth into a better position, for a bite that works well and teeth that are easier to clean.",
                  "Metal braces and clear aligners are both available at Arha, for children, teens and adults, with an early orthodontic assessment for children."),
        "interactive": ("ages", "What usually suits each age", "Hover or tap an age group to see what is usually suitable."),
        "who": [("Crowded or crooked teeth", "Teeth that overlap, turn or sit out of line."),
                ("Gaps", "Spaces between teeth."),
                ("Teeth that stick out", "Front teeth that are prominent or easily knocked."),
                ("A bite that does not meet properly", "Teeth that do not come together evenly.")],
        "steps": [("Assessment", "An examination of the teeth, bite and, for children, how the jaws are growing."),
                  ("Records and plan", "Photographs and X-rays, then a plan with the options that suit you."),
                  ("Braces or aligners fitted", "Your braces are fitted, or your first aligners given."),
                  ("Regular reviews", "Adjustments and checks along the way."),
                  ("Retainers", "Retainers keep the teeth in their new position.")],
        "cases": "aligners",
        "timing": ["Typical treatment", "Review visits", "Retainers"],
        "faq": [("When should my child be checked?", "A first orthodontic check around age 7 is the usual advice. Most children only need monitoring at that age."),
                ("Do braces hurt?", "Teeth can feel sore for a few days after braces are fitted or adjusted. It usually settles quickly."),
                ("How long does treatment take?", "It depends on what needs correcting. You will get an estimate once your plan is made."),
                ("Will I need a retainer?", "Yes. Retainers are what keep teeth straight after treatment.")],
        "planner": False,
    },
    "general-dentistry": {
        "title": "General Dentistry, Check-ups and Cleaning | Arha Dental Care, Peddar Road",
        "description": "Dental check-ups, professional cleaning and tooth-coloured fillings at Arha Dental Care, Peddar Road, South Mumbai.",
        "h1": "General dentistry &amp; cleaning",
        "lede": "Check-ups, cleaning and fillings that keep problems small.",
        "hero": ("dental-operatory-arha-dental-care-peddar-road-02", "An Arha treatment room: the chair, a desk and marble walls", "50% 55%"),
        "preview": ("stock-scalers", "Scaling instruments laid out on a white tray", "50% 50%"),
        "card": "Check-ups, professional cleaning and fillings.",
        "intro": ("Prevention first",
                  "Regular check-ups find problems while they are still small and simple to treat. A professional clean removes the hard deposits that brushing cannot.",
                  "How often you need to come depends on your teeth and gums. We will suggest an interval that suits you."),
        "interactive": ("checkup", "Your check-up, step by step", "Swipe, drag or use the arrows to walk through a routine visit."),
        "who": [("It has been a while", "No check-up in the last year or more."),
                ("Bleeding gums or bad breath", "Common early signs of gum inflammation."),
                ("Sensitivity or a small cavity", "Caught early, often a simple filling."),
                ("Old fillings that need checking", "Fillings that are worn, cracked or leaking.")],
        "steps": [("We ask how you are", "Any pain or sensitivity, and any changes in your health or medicines."),
                  ("Examination", "Teeth, gums, bite, tongue and the soft tissues of the mouth."),
                  ("X-rays, if needed", "Taken in-house, and only when they will tell us something useful."),
                  ("Cleaning", "Scaling and polishing to remove plaque, tartar and surface stains."),
                  ("Your plan", "What we found, what needs doing now, and what can wait.")],
        "cases": None,
        "timing": ["Check-up and cleaning", "Fillings", "How often to come"],
        "faq": [("How often should I have a check-up?", "For most people, every six to twelve months. If your gums need more care, we may suggest shorter intervals."),
                ("Does cleaning damage enamel?", "No. Professional cleaning removes deposits from the tooth surface without harming the enamel."),
                ("Are tooth-coloured fillings strong?", "Modern tooth-coloured fillings are strong enough for most cavities. Very large ones may need a crown instead."),
                ("Are dental X-rays safe?", "Dental X-rays use a very small dose. We take them only when they will tell us something useful.")],
        "planner": False,
    },
    "root-canal-treatment": {
        "title": "Root Canal Treatment in South Mumbai | Arha Dental Care, Peddar Road",
        "description": "Root canal treatment at Arha Dental Care, Peddar Road: saving an infected tooth with rotary endodontics, explained step by step.",
        "h1": "Root canal treatment",
        "lede": "Saving a tooth whose nerve is infected or inflamed.",
        "hero": ("stock-mirror-tray", "Dental mirrors laid out on a steel tray", "50% 50%"),
        "card": "Saving an infected tooth, with rotary instruments.",
        "intro": ("Keep your own tooth",
                  "Inside each tooth is the pulp: nerves and blood vessels in narrow canals. When decay or a crack lets infection reach it, root canal treatment removes the infected pulp and seals the canals.",
                  "At Arha the canals are cleaned with rotary instruments: fine, flexible files driven by a motor. The tooth is then usually protected with a crown."),
        "interactive": ("root-canal", "What happens, step by step", "Choose a step to see what happens to the tooth."),
        "who": [("Lingering pain or sensitivity", "Pain that stays after hot or cold, or wakes you at night."),
                ("A deep cavity or crack", "Damage that reaches close to the nerve."),
                ("Swelling or a gum boil", "Signs that infection has spread from the tooth."),
                ("A tooth that has darkened", "Often after an old knock or injury.")],
        "steps": None,
        "cases": None,
        "timing": ["Number of visits", "Time per visit", "Crown afterwards"],
        "faq": [("Does a root canal hurt?", "It is done under local anaesthetic, and most people find it feels like having a filling. It relieves the pain the infection was causing."),
                ("How many visits will it take?", "It depends on the tooth and the infection. We will tell you before we start."),
                ("Do I always need a crown afterwards?", "Back teeth usually do, because a treated tooth is more brittle. Front teeth sometimes need only a filling."),
                ("Is taking the tooth out a better option?", "Keeping your own tooth is usually better for chewing and for the teeth around it. If a tooth cannot be saved, we will explain the replacements.")],
        "planner": False,
    },
    "crowns-bridges": {
        "title": "Crowns and Bridges in South Mumbai | Arha Dental Care, Peddar Road",
        "description": "Ceramic, zirconia and PFM crowns and bridges at Arha Dental Care, Peddar Road, Mumbai, planned by a prosthodontist.",
        "h1": "Crowns &amp; bridges",
        "lede": "Restoring broken teeth and replacing missing ones, made to match your smile.",
        "hero": ("stock-gloved-hands", "A gloved hand picking up a fine dental instrument from a tray", "60% 40%"),
        "card": "Ceramic, zirconia and PFM crowns, and bridges for a missing tooth.",
        "intro": ("Strength and a natural look",
                  "A crown covers and protects a damaged tooth. A bridge replaces a missing tooth by holding a new tooth between two crowns.",
                  "Arha offers ceramic, zirconia and PFM (porcelain fused to metal) crowns. The right one depends on where the tooth is and the work it has to do."),
        "interactive": ("materials", "Choosing a material", "Compare the three crown materials, then answer two questions about a missing tooth."),
        "who": [("A broken or cracked tooth", "A tooth too damaged for a filling."),
                ("A large old filling", "A tooth weakened by a big filling."),
                ("A tooth after root canal treatment", "Protection for a more brittle tooth."),
                ("One missing tooth", "A bridge across the gap, or an implant crown.")],
        "steps": [("Consultation and X-rays", "We check the tooth, its root and your bite."),
                  ("Preparing the tooth", "The tooth is shaped under local anaesthetic so the crown fits."),
                  ("Temporary crown", "A temporary protects the tooth while the crown is made."),
                  ("Fitting", "The crown or bridge is fitted and the bite adjusted."),
                  ("Review", "A check that it feels right and your gums are healthy.")],
        "cases": None,
        "timing": ["Crown", "Bridge", "Temporary in between"],
        "faq": [("How long do crowns last?", "Crowns are long-term restorations. Care at home, habits such as grinding and regular check-ups all affect how long they last."),
                ("Does preparing the tooth hurt?", "It is done under local anaesthetic, so you should feel pressure rather than pain."),
                ("Which material is best?", "There is no single best one. It depends on the tooth, your bite and how it needs to look; we will recommend one and explain why."),
                ("Bridge or implant?", "An implant leaves the neighbouring teeth untouched; a bridge relies on them. The decider above gives the general idea, and your consultation the answer for you.")],
        "planner": False,
    },
}

# Kids' dentistry has its own template (tools/pages/kids-dentistry.html); its card and meta live here
KIDS = {
    "title": "Kids’ Dentist (Paediatric Dentistry) on Peddar Road, South Mumbai | Arha Dental Care",
    "description": "Paediatric (pediatric) dentistry at Arha Dental Care, Peddar Road: gentle first visits, check-ups, sealants, fluoride and early orthodontic checks for children.",
    "card": "Gentle first visits, check-ups, sealants and fluoride.",
}

GROUP_CARDS = {"Specialist care": "Led by a prosthodontist, for the most complex work.",
               "Smile &amp; aesthetics": "Planned around your face and previewed first.",
               "Everyday &amp; family care": "Check-ups, cleaning and care for the whole family."}

TECH_GROUPS = [
    ("see", "See more", "Diagnosis and imaging"),
    ("plan", "Plan precisely", "Digital planning"),
    ("treat", "Treat gently", "Comfort and precision"),
    ("safe", "Kept safe", "Sterilisation"),
]


# ------------------------------------------------------------------ helpers
def esc(s):
    return html.escape(s, quote=True)


def faq_jsonld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": html.unescape(q),
                            "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub(r"<[^>]+>", "", a))}} for q, a in faq]}


def crumbs_jsonld(site, trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": html.unescape(n), "item": site + u}
                                for i, (n, u) in enumerate(trail)]}


def crumbs(trail):
    """Visible breadcrumb: Home / Treatments / Dental implants (the last item is the current page)."""
    items = [f'<li><a href="{u or "./"}">{n}</a></li>' for n, u in trail[:-1]]
    items.append(f'<li aria-current="page">{trail[-1][0]}</li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'


def hero(slug, t, specialty, i="    "):
    name, alt, pos = t["hero"]
    tag = '<p class="tag tag--light">Specialty</p>' if specialty else ""
    return f"""{i}<!-- =================================================================== HERO -->
{i}<section class="page-hero" aria-labelledby="page-title">
{i}  {{{{pic {name} | 100vw | {alt} | pos={pos} | eager}}}}
{i}  <div class="page-hero__content">
{i}    <div class="hero__text">
{i}      {crumbs([("Home", ""), ("Treatments", "treatments/"), (t["h1"], slug + "/")])}
{i}      {tag}
{i}      <h1 id="page-title">{t["h1"]}</h1>
{i}      <p class="hero__lede">{t["lede"]}</p>
{i}      <div class="hero__actions">
{i}        <a class="cta" href="book/">Book a Consultation</a>
{i}        <a class="cta" href="tel:+910000000000" data-call="treatment_hero">Call <span data-show="phone">+91 00000 00000</span></a>
{i}      </div>
{i}    </div>
{i}  </div>
{i}</section>
"""


def section(cls, sid, title, body, lede="", i="    "):
    lede_html = f'\n{i}      <p class="lede">{lede}</p>' if lede else ""
    return f"""
{i}<section class="section {cls}" aria-labelledby="{sid}">
{i}  <div class="container">
{i}    <div class="section-head reveal">
{i}      <h2 id="{sid}">{title}</h2>{lede_html}
{i}    </div>
{body}
{i}  </div>
{i}</section>
"""


def tabs(name, items, panel, label, orient="horizontal", cls="", hash_=False):
    """items: [(key, tab label)], panel(key) -> inner HTML. Uses the shared tabs component."""
    t, p = [], []
    for n, (key, lab) in enumerate(items):
        sel = n == 0
        t.append(f'<button class="itabs__tab" type="button" role="tab" id="{name}-t-{key}" aria-controls="{name}-{key}" '
                 f'aria-selected="{str(sel).lower()}"{"" if sel else " tabindex=\"-1\""}>{lab}</button>')
        p.append(f'<div class="itabs__panel" role="tabpanel" id="{name}-{key}" aria-labelledby="{name}-t-{key}" tabindex="0"{"" if sel else " hidden"}>{panel(key)}</div>')
    return (f'<div class="itabs {cls}" data-tabs{" data-hash" if hash_ else ""}>'
            f'<div class="itabs__list" role="tablist" aria-label="{label}" aria-orientation="{orient}">{"".join(t)}</div>'
            f'{"".join(p)}</div>')


def photo(name, alt, sizes="(min-width: 900px) 60vw, 100vw", pos=None, cls="ix-photo", ratio="3 / 2"):
    """A real photograph in a fixed-ratio frame (the frame never jumps when panels change)."""
    pic = picture(name, sizes, alt, pos=pos, indent="")
    return f'<div class="{cls} media" style="aspect-ratio: {ratio}">{pic}</div>'


def stepper(name, label, steps):
    """Phase / step-by-step component: progress line, numbered steps (tabs), Previous / Next.
    steps: [(title, text, photo name, alt[, extra html])]; each step shows its photograph and a large number."""
    items = [(f"s{n + 1}", f'<span class="stepper__num">{n + 1:02d}</span><span class="stepper__name">{s[0]}</span>') for n, s in enumerate(steps)]

    def panel(key):
        n = int(key[1:]) - 1
        title, text, img, alt = steps[n][:4]
        extra = steps[n][4] if len(steps[n]) > 4 else ""
        return (f'{photo(img, alt)}<div class="stepper__text"><p class="stepper__big" aria-hidden="true">{n + 1:02d}</p>'
                f'<p class="stepper__count">Step {n + 1} of {len(steps)}</p><h3>{title}</h3><p>{text}</p>{extra}</div>')
    return (f'<div class="stepper" data-stepper style="--steps: {len(steps)}">'
            f'<div class="stepper__track" aria-hidden="true"><span class="stepper__progress"></span></div>'
            + tabs(name, items, panel, label, cls="itabs--steps")
            + '<div class="stepper__nav"><button class="cta" type="button" data-step="-1">Previous</button>'
            '<button class="cta" type="button" data-step="1">Next</button></div></div>')


def photo_tabs(name, label, items, cls="itabs--photo", orient="horizontal"):
    """Tabs whose panels each lead with a photograph: items [(key, tab label, photo, alt, body html)]."""
    return tabs(name, [(k, lab) for k, lab, *_ in items],
                lambda key: next(f'{photo(img, alt)}<div class="itabs__body">{body}</div>' for k, lab, img, alt, body in items if k == key),
                label, orient=orient, cls=cls)


def checklist(name, legend, items, results, note):
    """Self-check: tick what applies; a result appears below (data-if: any:a,b / none). Not a diagnosis."""
    boxes = "".join(f'<li><label class="check"><input type="checkbox" value="{v}"><span>{t}</span></label></li>' for v, t in items)
    res = "".join(f'<div class="checklist__result" data-if="{cond}" hidden>{body}</div>' for cond, body in results)
    return (f'<form class="checklist" data-checklist onsubmit="return false"><fieldset><legend>{legend}</legend>'
            f'<ul>{boxes}</ul></fieldset><div class="checklist__out" aria-live="polite">{res}</div>'
            f'<p class="checklist__note">{note}</p></form>')


# ------------------------------------------------------------------ the interactive block of each page (all photographs)
def ix_implants():
    # Numbered markers on a real implant model (positions in % of the 3:2 photograph)
    spots = [("crown", "Crown", "The part you see and chew with, shaped and coloured to match your teeth.", 48, 38),
             ("abutment", "Abutment", "A small connector that joins the crown to the implant, at the gum line.", 48, 48),
             ("implant", "Implant", "A titanium post that takes the place of the root and bonds with the bone as it heals.", 48, 61),
             ("bone", "Bone", "The jawbone holds the implant firmly once it has healed around it.", 37, 69)]
    markers = "".join(
        f'<button class="hotspot" type="button" role="tab" id="spot-t-{k}" aria-controls="spot-{k}" aria-label="{n + 1}: {name}" '
        f'aria-selected="{str(n == 0).lower()}"{"" if n == 0 else " tabindex=\"-1\""} style="left: {x}%; top: {y}%">{n + 1}</button>'
        for n, (k, name, _, x, y) in enumerate(spots))
    panels = "".join(
        f'<div class="hotspots__panel" role="tabpanel" id="spot-{k}" aria-labelledby="spot-t-{k}" tabindex="0"{"" if n == 0 else " hidden"}>'
        f'<p class="hotspots__num" aria-hidden="true">{n + 1:02d}</p><h3>{name}</h3><p>{line}</p></div>'
        for n, (k, name, line, _, _) in enumerate(spots))
    explorer = f"""<div class="hotspots reveal" data-tabs>
        <div class="hotspots__frame media" style="aspect-ratio: 3 / 2">
          {picture("stock-implant-model", "(min-width: 900px) 62vw, 100vw", "A model of the jaw cut open: a crown on an implant post between two natural teeth, with the bone around them", indent="")}
          <div class="hotspots__markers" role="tablist" aria-label="Parts of an implant">{markers}</div>
        </div>
        <div class="hotspots__info">{panels}<p class="ix-note">Tap a number on the photograph.</p></div>
      </div>"""
    return explorer


def ix_phases():
    v = ""  # visits are agreed at the consultation; no placeholder line
    steps = [("Diagnose", "A full examination, X-rays, photographs and records of how your teeth meet. We start with what bothers you most.",
              "arha-dental-care-operatory-laptop", "An Arha treatment room, where records and photographs are reviewed on screen", v),
             ("Design the bite &amp; smile", "Your new bite and tooth shapes are designed on models and on screen, around your face and your jaw.",
              "stock-lab", "Gloved hands holding a dental model during planning", v),
             ("Trial smile", "You try the design in temporary teeth, so you can see, speak and chew with it before anything is final.",
              "stock-mirror", "A patient looking at his smile in a hand mirror with the dentist beside him", v),
             ("Final restorations", "The final crowns, bridges or implant teeth are made and fitted in stages, with the bite checked at each visit.",
              "stock-lab-grind", "Gloved hands finishing a ceramic crown in the laboratory", v),
             ("Maintenance", "Regular reviews and cleaning protect the work. A night guard may be advised if you grind your teeth.",
              "stock-brushes-grey", "Toothbrushes for care at home", v)]
    return f'<div class="reveal">{stepper("phase", "Phases of full mouth rehabilitation", steps)}</div>'


def ix_who_we_help():
    # Calm laboratory and clinical photographs: respectful, never a patient, nothing graphic
    who = [("surgery", "After oral cancer surgery", "stock-lab", "Gloved hands holding a dental model during planning",
            "When surgery removes part of the palate or jaw, a prosthesis called an obturator can close the gap, so that eating, drinking and speaking feel more normal again. It is planned with your surgical team, sometimes before the operation."),
           ("cleft", "Cleft palate", "stock-mirror", "A patient looking at his smile in a hand mirror with the dentist beside him",
            "Some children and adults born with a cleft palate are helped by a plate that closes an opening in the roof of the mouth or supports speech. It works alongside the care of the cleft team."),
           ("injury", "Facial or jaw injury", "stock-prosthesis-model", "A prosthesis made on a stone model of the jaw",
            "After an accident, teeth and parts of the jaw can be rebuilt in stages, with prostheses that restore the bite and support the shape of the face."),
           ("birth", "From birth", "stock-zirconia", "Solid white crowns on a dental model",
            "Some people are born without certain teeth or parts of the jaw. Prostheses, sometimes held by implants, can help with chewing, speech and appearance.")]
    items = [(k, n, img, alt, f"<h3>{n}</h3><p>{d}</p><p class=\"ix-note\">Every situation is different. A consultation, and often your surgeon’s advice, decides what is possible.</p>")
             for k, n, img, alt, d in who]
    return f'<div class="reveal">{photo_tabs("who", "Who we help", items, cls="itabs--photo itabs--side", orient="vertical")}</div>'


def ix_guides():
    # Midline, smile line and tooth boundaries measured on the 640 x 800 sample photograph (stock-case-3)
    ticks = "".join(f'<path d="M{x} 322V402"/>' for x in (182, 228, 405, 450))
    overlay = f"""<svg class="guides__overlay" viewBox="0 0 640 800" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
            <g class="guides__lines">
              <path class="g-mid" d="M336 286V484"/>
              <path class="g-curve" d="M160 368Q336 446 490 372"/>
              <g class="g-ticks">{ticks}</g>
              <text x="344" y="280">Midline</text><text x="470" y="436">Smile line</text><text x="120" y="312">Proportions</text>
            </g>
          </svg>"""
    pic = picture("stock-case-3", "(min-width: 900px) 40vw, 100vw", "Sample photograph of a smile, used to show the design guides", pos="50% 50%", indent="")
    return f"""<div class="guides-wrap reveal">
        <figure class="guides" data-guides>
          <div class="guides__frame media">{pic}{overlay}</div>
          <figcaption><span>Sample photograph</span><button class="cta" type="button" aria-pressed="false" data-guides-toggle>Show design guides</button></figcaption>
        </figure>
        <div class="guides__text">
          <h3>Measured before anything is changed</h3>
          <p>The <strong>midline</strong> between the front teeth is matched to the centre of your face. The <strong>smile line</strong> along the biting edges follows your lower lip. Each tooth’s <strong>proportions</strong> are planned in relation to its neighbours.</p>
          <p>The design is then previewed so you can see it, and change it, before treatment.</p>
        </div>
      </div>"""


def ix_matrix():
    opts = ["Whitening", "Bonding", "Veneers"]
    grid = {
        "stains": ("Stains", "stock-teeth-shades", "Sets of artificial teeth in a range of natural shades",
                   [("good", "Lightens natural tooth colour; works best on general yellowing."),
                    ("some", "Can cover a dark patch on a single tooth."),
                    ("some", "For deep stains that whitening cannot lift.")]),
        "chips": ("Chips", "stock-veneer-brush", "A thin veneer placed on a model with a fine brush",
                  [("no", "Changes colour, not shape."),
                   ("good", "Tooth-coloured resin rebuilds small chips with little or no drilling."),
                   ("some", "For larger chips, or when several teeth need reshaping.")]),
        "gaps": ("Gaps", "stock-veneers-grey", "Veneers that change the width of the front teeth, on grey fabric",
                 [("no", "Changes colour, not spacing."),
                  ("good", "Adds width to close small gaps."),
                  ("some", "Closes gaps while also changing shape and colour.")]),
        "shape": ("Shape", "stock-veneers", "Thin porcelain veneers before they are fitted",
                  [("no", "Changes colour, not shape."),
                   ("some", "Small changes to length or edges."),
                   ("good", "Changes the shape, length and colour of several teeth together.")]),
    }
    words = {"good": "A good fit", "some": "Sometimes", "no": "Not for this"}
    items = []
    for k, (n, img, alt, cells) in grid.items():
        row = "".join(f'<div class="matrix__cell matrix__cell--{v}"><p class="matrix__opt">{o}</p><p class="matrix__fit">{words[v]}</p><p>{why}</p></div>'
                      for o, (v, why) in zip(opts, cells))
        items.append((k, n, img, alt, f'<h3 class="visually-hidden">{n}</h3><div class="matrix__row">{row}</div>'))
    extra = '<p class="ix-note">Large gaps or crooked teeth may be better treated by moving them. See <a href="invisalign/">Invisalign clear aligners</a>.</p>'
    return f'<div class="matrix reveal">{photo_tabs("concern", "Your concern", items, cls="itabs--photo itabs--stack")}{extra}</div>'


def ix_aligners():
    """A range that steps through the stages (site.js 19, [data-stages]), then aligners and braces compared."""
    stages = [("Your scan", "Your teeth are recorded with photographs, X-rays and a scan or impressions, and every stage is planned on screen.",
               "arha-dental-care-scan-screen", "A screen in an Arha treatment room showing 3D scans of the upper and lower teeth"),
              ("Your aligners", "A series of thin, clear aligners is made for your teeth, each a small step from the last.",
               "stock-aligner-case", "A clear aligner in its case"),
              ("Wearing them", "You wear each set most of the day and night, and move to the next set when we say.",
               "stock-aligner-hands", "Hands holding a clear aligner, its case and a cleaning spray"),
              ("Straighter teeth", "When the last aligner is done, a retainer keeps the teeth in their new place.",
               "stock-man-smile", "A young man with a natural, even smile")]
    n = len(stages)
    imgs = "".join(f'<div class="stages__img{" is-active" if k == 0 else ""}" data-stage="{k + 1}">{picture(img, "(min-width: 900px) 55vw, 100vw", alt, indent="")}</div>'
                   for k, (_t, _x, img, alt) in enumerate(stages))
    texts = "".join(f'<div class="stages__text" data-stage="{k + 1}"{"" if k == 0 else " hidden"}><h3>{ti}</h3><p>{tx}</p></div>'
                    for k, (ti, tx, _i, _a) in enumerate(stages))
    ticks = "".join(f"<span>Stage {k + 1}</span>" for k in range(n))
    vs_rows = [("Visible", "Nearly invisible", "Brackets and a wire show"), ("Removable", "Yes, to eat and clean", "No, fixed until the end"),
               ("Eating", "Anything, with the aligners out", "Some hard or sticky foods are avoided"),
               ("Cleaning", "Brush as usual; clean the aligners too", "More care around the brackets"),
               ("Check-ups", "Regular reviews of progress", "Regular visits to adjust the wire")]
    vs = tabs("vs", [("aligners", "Aligners"), ("braces", "Braces")],
              lambda key: '<dl class="vs">' + "".join(f"<div><dt>{r}</dt><dd>{a if key == 'aligners' else b}</dd></div>" for r, a, b in vs_rows) + "</dl>",
              "Aligners or braces", cls="itabs--vs")
    return f"""<div class="stages reveal" data-stages>
        <div class="stages__stage media">{imgs}</div>
        <div class="stages__side">
          <label class="stages__control" for="stage-range"><span class="stages__count">Stage <output data-stage-out>1</output> of {n}</span>
            <input id="stage-range" type="range" min="1" max="{n}" step="1" value="1" aria-valuetext="Stage 1: {stages[0][0]}">
          </label>
          <div class="stages__ticks" aria-hidden="true">{ticks}</div>{texts}
        </div>
      </div>
      <div class="vs-wrap reveal"><h3 class="vs-wrap__title">Aligners or braces?</h3>{vs}<p class="ix-note">Not sure which suits you? See <a href="orthodontics/">orthodontics (braces)</a>.</p></div>"""


def ix_ages():
    """Child, teen or adult as expanding photo panels (hover or focus on a laptop, tap on a phone)."""
    ages = [("stock-kid-dentist", "50% 40%", "A boy in the dental chair with the dentist beside him", "Child (7 to 11)",
             "An early orthodontic check around age 7 spots problems with how the jaws and teeth are growing. Most children only need monitoring; some benefit from early treatment."),
            ("stock-braces", "50% 50%", "A smile with metal braces", "Teen (12 to 18)",
             "Most adult teeth are in, so this is the most common time for braces, or aligners where they suit."),
            ("stock-aligners-shadow", "50% 50%", "Clear aligners on a model, in soft shadow", "Adult",
             "It is never too late. Many adults choose clear aligners; braces suit some bites better. Gum health is checked first.")]
    lis = "".join(f"""
        <li class="xpanel{' is-active' if k == 0 else ''}" data-xpanel tabindex="0">
          {picture(name, '(min-width: 900px) 50vw, 100vw', alt, pos=pos, indent='')}
          <div class="xpanel__body">
            <h3>{title}</h3>
            <div class="xpanel__more">
              <p>{text}</p>
              <a class="link link--light" href="invisalign/">Invisalign clear aligners</a>
            </div>
          </div>
        </li>""" for k, (name, pos, alt, title, text) in enumerate(ages))
    return f'<ul class="xpanels xpanels--ix reveal" data-xpanels>{lis}\n      </ul>'


def ix_checkup():
    """Your check-up, step by step: photo cards in the shared drag strip (swipe, drag or the arrows)."""
    steps = [("ask", "We ask how you are", "Any pain, changes or worries since your last visit, and your medical history.", "stock-consultation", "A dentist talking a patient through a treatment model"),
             ("exam", "Examination", "Teeth, fillings, gums, tongue and the soft tissues of the mouth, looked at carefully.", "stock-exam", "A dentist examining a patient’s teeth with a mirror and probe"),
             ("xray", "X-rays, if needed", "Only when they will show something we need to see, taken in the clinic.", "stock-xray-panoramic", "A panoramic dental X-ray of the whole mouth"),
             ("gum-care", "Gum check", "The gum line is measured gently around each tooth, to catch gum disease early.", "stock-mirror-probe", "A dental mirror and probe on a tray"),
             ("clean", "Cleaning", "Tartar and stain are removed and the teeth polished, and you are told what we found and when to come back.", "stock-scalers", "Scaling instruments laid out on a white tray")]
    cards = "".join(f"""
          <li class="tl-card" id="{k}">
            <div class="tl-card__media media">{picture(img, '(min-width: 900px) 28vw, 78vw', alt, indent='')}</div>
            <p class="tl-card__num">{n + 1:02d}</p>
            <h3>{title}</h3>
            <p>{text}</p>
          </li>""" for n, (k, title, text, img, alt) in enumerate(steps))
    return f"""<div class="drag drag--timeline reveal" data-drag aria-label="Your check-up, step by step">
        <ul class="drag__track">{cards}
        </ul>
        <div class="drag__ui">
          <button class="drag__btn drag__btn--prev" type="button" aria-label="Previous step"></button>
          <span class="drag__progress" aria-hidden="true"><span></span></span>
          <button class="drag__btn drag__btn--next" type="button" aria-label="Next step"></button>
        </div>
      </div>
      <p class="ix-note">Bleeding gums? Try the <a href="problems/bleeding-gums/">gum self-check</a>.</p>"""


def ix_root_canal():
    """Four steps as a numbered list beside one photo stage that crossfades (tabs + site.js 19 [data-xfade])."""
    steps = [("infected", "Infected pulp", "Decay or a crack has let bacteria reach the pulp, causing pain, swelling or sensitivity that lingers. An X-ray shows it.",
              "stock-xray-panoramic", "A panoramic dental X-ray of the whole mouth"),
             ("cleaned", "Cleaned", "Under local anaesthetic, the infected pulp is removed and the canals are cleaned and shaped with rotary instruments.",
              "stock-endo-files", "Fine endodontic files with coloured handles, used to clean the canals"),
             ("sealed", "Sealed and checked", "The clean canals are filled and sealed so that bacteria cannot return, and an X-ray checks the result.",
              "stock-mirror-probe", "A dental mirror and probe on a tray"),
             ("crown", "Crown on top", "A crown is usually placed to protect the tooth, as a treated back tooth is more brittle.",
              "stock-lab-model", "Ceramic crowns on a dental model")]
    tabs_html = "".join(f'<button type="button" role="tab" id="rct-t-{k}" aria-controls="rct-p-{k}" aria-selected="{str(n == 0).lower()}"{"" if n == 0 else " tabindex=\"-1\""}>'
                        f'<span class="xfade__num">{n + 1:02d}</span>{title}</button>' for n, (k, title, _x, _i, _a) in enumerate(steps))
    shots = "".join(f'<div class="xfade__img{" is-active" if n == 0 else ""}" data-for="rct-p-{k}">{picture(img, "(min-width: 900px) 55vw, 100vw", alt, indent="")}</div>'
                    for n, (k, _t, _x, img, alt) in enumerate(steps))
    panels = "".join(f'<div class="xfade__panel" role="tabpanel" id="rct-p-{k}" aria-labelledby="rct-t-{k}"{"" if n == 0 else " hidden"}><p>{text}</p></div>'
                     for n, (k, _t, text, _i, _a) in enumerate(steps))
    return f"""<div class="xfade xfade--steps reveal" data-tabs data-xfade>
        <div class="xfade__stage media">{shots}</div>
        <div class="xfade__side">
          <div class="xfade__tabs" role="tablist" aria-label="Steps of root canal treatment" aria-orientation="vertical">{tabs_html}</div>{panels}
        </div>
      </div>"""


def ix_materials():
    mats = [("ceramic", "Ceramic", "stock-lab-grind", "A ceramic crown being finished in the laboratory",
             ["The most natural; light passes through it like enamel", "Strong for front teeth, less so for heavy chewing", "Yes", "Front teeth"]),
            ("zirconia", "Zirconia", "stock-zirconia", "Solid white crowns on a dental model",
             ["Natural, slightly more opaque", "Very strong", "Yes", "Back teeth, and front teeth where strength matters"]),
            ("pfm", "PFM", "stock-pfm", "A crown on a dental model",
             ["Good, though a grey line can show at the gum over time", "Strong, with a long track record", "No: porcelain over a metal base", "Back teeth and bridges"])]
    labels = ["Look", "Strength", "Metal-free", "Usually used for"]
    items = [(k, n, img, alt, '<dl class="vs">' + "".join(f"<div><dt>{l}</dt><dd>{v}</dd></div>" for l, v in zip(labels, vals)) + "</dl>")
             for k, n, img, alt, vals in mats]
    decider = """<form class="decider reveal" data-decider aria-labelledby="dec-title" onsubmit="return false">
        <h3 id="dec-title">Crown, bridge or implant?</h3>
        <fieldset><legend>Is the tooth still there?</legend>
          <label><input type="radio" name="there" value="yes"><span>Yes</span></label><label><input type="radio" name="there" value="no"><span>No, it is missing</span></label>
        </fieldset>
        <fieldset data-show-if="there:yes" hidden><legend>Is it badly broken, cracked or heavily filled?</legend>
          <label><input type="radio" name="weak" value="yes"><span>Yes</span></label><label><input type="radio" name="weak" value="no"><span>No</span></label>
        </fieldset>
        <fieldset data-show-if="there:no" hidden><legend>Are the teeth either side healthy, with few or no fillings?</legend>
          <label><input type="radio" name="sides" value="yes"><span>Yes</span></label><label><input type="radio" name="sides" value="no"><span>No, they need work too</span></label>
        </fieldset>
        <div class="decider__out" aria-live="polite">
          <div data-when="there:yes weak:yes" hidden><p class="picker__step">Usually a crown</p><p>A crown covers and protects what is left of the tooth.</p></div>
          <div data-when="there:yes weak:no" hidden><p class="picker__step">Perhaps just a filling</p><p>A sound tooth may only need a tooth-coloured filling. An examination tells.</p><a class="link" href="general-dentistry/">General dentistry</a></div>
          <div data-when="there:no sides:yes" hidden><p class="picker__step">Often an implant</p><p>An implant replaces the tooth without touching the healthy teeth beside it.</p><a class="link" href="dental-implants/">Dental implants</a></div>
          <div data-when="there:no sides:no" hidden><p class="picker__step">Often a bridge</p><p>A bridge can use crowns that the teeth beside the gap may need anyway.</p></div>
        </div>
        <p class="ix-flag">General guidance, not a diagnosis. Your consultation gives the answer for you.</p>
      </form>"""
    return f'<div class="reveal">{photo_tabs("mat", "Crown material", items, cls="itabs--photo itabs--split")}</div>\n      {decider}'


INTERACTIVES = {"implants": ix_implants, "phases": ix_phases, "who-we-help": ix_who_we_help, "guides": ix_guides,
                "matrix": ix_matrix, "aligners": ix_aligners, "ages": ix_ages, "checkup": ix_checkup,
                "root-canal": ix_root_canal, "materials": ix_materials}


# ------------------------------------------------------------------ shared page blocks


def steps_block(items):
    lis = "".join(f'\n          <li class="steps__item reveal"><p class="steps__num">Step {n + 1:02d}</p><div class="steps__body"><h3>{a}</h3><p>{b}</p></div></li>'
                  for n, (a, b) in enumerate(items))
    return f'        <ol class="steps">{lis}\n        </ol>'


def cases_block(cat):
    only = f" only={cat}" if cat else " only=none"
    return f"""
    <section class="section results" aria-labelledby="cases-title">
      <div class="container">
        <div class="section-head reveal">
          <h2 id="cases-title">Results</h2>
        </div>
        <div data-cases-block>
          <p class="cases-note reveal">Sample images for demo. Arha’s own cases, shared with patient consent, will appear here. Results vary.</p>
          <!-- cases:start{only} --><!-- cases:end -->
        </div>
        <div class="section-cta reveal">
          <a class="cta" href="our-work/">See all our work{ARROW}</a>
        </div>
      </div>
    </section>
"""


def faq_block(faq):
    items = "".join(f"""
          <div class="faq__item">
            <h3><button class="faq__trigger" type="button" aria-expanded="false" aria-controls="faq-{n + 1}">{q}<span class="plus" aria-hidden="true"></span></button></h3>
            <div class="faq__panel" id="faq-{n + 1}"><div class="acc__clip"><p>{a}</p></div></div>
          </div>""" for n, (q, a) in enumerate(faq))
    return f"""
    <section class="section section--stone texture" aria-labelledby="faq-title">
      <div class="container">
        <div class="section-head reveal">
          <h2 id="faq-title">Questions, answered</h2>
        </div>
        <div class="faq reveal" data-accordion>{items}
        </div>
      </div>
    </section>
"""


CLOSING_PHOTOS = [  # Arha's own rooms, chosen by title so a page always closes on the same photograph (no desk or laptop shots)
    ("arha-dental-care-reception-south-mumbai-dental-clinic-01-lower", "Arha Dental Care reception: a curved front desk, soft seating and a glass entrance door", "35% 70%"),
    ("arha-dental-care-lounge-peddar-road", "Arha's patient lounge: soft seating and warm light", "50% 55%"),
    ("dental-operatory-arha-dental-care-peddar-road-01", "An Arha treatment room: the dental chair under its overhead light", "50% 62%"),
    ("arha-dental-care-reception-south-mumbai-dental-clinic-01", "Arha's reception and the glass entrance door", "50% 60%"),
]


def closing(title="Begin with a conversation", text="Every plan at Arha starts with a consultation: a careful examination, a clear explanation and a plan made for you."):
    """apa's dark band as punctuation: no photograph (v4 feedback 5: a photo is on two pages at most), the two actions."""
    return f"""
    <!-- =================================================================== CALL / BOOK (a plain charcoal band) -->
    <section class="statement statement--close statement--plain band" aria-labelledby="closing-title">
      <div class="container statement__content reveal">
        <h2 id="closing-title">{title}</h2>
        <p>{text}</p>
        <div class="band__actions">
          <a class="cta" href="book/">Book a Consultation</a>
          <a class="cta" href="tel:+910000000000" data-call="treatment_band">Call <span data-show="phone">+91 00000 00000</span></a>
        </div>
      </div>
    </section>
"""


# ------------------------------------------------------------------ pages
ROOMS = [  # Arha's own rooms, rotated across the treatment pages beside "Is this for you?"
    ("dental-operatory-arha-dental-care-peddar-road-01", "An Arha treatment room: the dental chair under its overhead light", "50% 60%"),
    ("arha-dental-care-reception-south-mumbai-dental-clinic-02", "Arha's reception: the gold emblem and wordmark on a marble wall", "50% 40%"),
    ("arha-dental-care-lounge-peddar-road", "The patients' lounge at Arha", "50% 60%"),
    ("dental-operatory-arha-dental-care-peddar-road-06", "A treatment room seen through a glass door", "50% 55%"),
    ("dental-operatory-arha-dental-care-peddar-road-02", "A treatment room with a desk, the chair and marble walls", "50% 55%"),
    ("arha-dental-care-reception-south-mumbai-dental-clinic-01", "Arha's reception: a curved front desk and soft seating", "50% 45%"),
    ("dental-operatory-arha-dental-care-peddar-road-04", "The consultation desk with a large monitor", "50% 50%"),
]


def who_split(items, n, title="Is this for you?", photo=None):
    """A short list beside one of Arha's own photographs, so photography leads the section."""
    name, alt, pos = photo or ROOMS[n % len(ROOMS)]
    lis = "".join(f'\n            <li class="reveal"><h3>{a}</h3><p>{b}</p></li>' for a, b in items)
    return f"""
    <section class="section who-split" aria-labelledby="who-title">
      <div class="container split split--even">
        <div class="split__media media media--hover who-split__media reveal">
{picture(name, "(min-width: 900px) 50vw, 100vw", alt, pos=pos, indent="          ")}
        </div>
        <div class="split__text">
          <h2 id="who-title" class="reveal">{title}</h2>
          <ul class="who who--list">{lis}
          </ul>
        </div>
      </div>
    </section>
"""


def intro_split(title, lede, more, who, n):
    """One idea: what the treatment is and who it is for, beside one of Arha's own rooms."""
    name, alt, pos = ROOMS[n % len(ROOMS)]
    lis = "".join(f'<li><span class="for-list__name">{a}</span> {b}</li>' for a, b in who)
    return f"""
    <!-- =================================================================== INTRO -->
    <section class="section intro-split" aria-labelledby="intro-title">
      <div class="container split split--even">
        <div class="split__media media media--hover intro-split__media reveal">
{picture(name, "(min-width: 900px) 50vw, 100vw", alt, pos=pos, indent="          ")}
        </div>
        <div class="split__text reveal">
          <h2 id="intro-title">{title}</h2>
          <p class="lede">{lede}</p>
          <p>{more}</p>
          <p class="for-list__label">Is this for you?</p>
          <ul class="for-list">{lis}</ul>
        </div>
      </div>
    </section>
"""


def specialty_slugs():
    return {t["slug"] for g in treatments.GROUPS if g.get("specialty") for t in g["items"]}


def treatment_page(slug, site_url):
    """Six sections at most, one interactive (notes/apa-study.md): hero; what it is and who it is for,
    beside one of Arha's rooms; the interactive; results, or how it works when there are no cases yet;
    questions; the call/book band."""
    t = TREATMENTS[slug]
    title, lede, more = t["intro"]
    kind, ix_title, ix_lede = t["interactive"]
    body = hero(slug, t, slug in specialty_slugs())
    body += intro_split(title, lede, more, t["who"], list(TREATMENTS).index(slug))
    body += "\n    <!-- =================================================================== INTERACTIVE -->" + section(
        f"section--stone texture ix ix--{kind}", "ix-title", ix_title, "      " + INTERACTIVES[kind](), ix_lede)
    if t["cases"]:  # results where sample cases exist; otherwise how it works (if not already the interactive)
        body += cases_block(t["cases"])
    elif t["steps"]:
        body += section("", "how-title", "How it works", steps_block(t["steps"]))
    body += faq_block(t["faq"])
    body += closing()
    main_html = f'  <main id="main" tabindex="-1">\n\n{body}\n  </main>\n'
    jsonld = [
        {"@context": "https://schema.org", "@type": "MedicalProcedure", "name": html.unescape(t["h1"]),
         "description": html.unescape(t["intro"][1]), "url": site_url + slug + "/"},
        faq_jsonld(t["faq"]),
        crumbs_jsonld(site_url, [("Home", ""), ("Treatments", "treatments/"), (t["h1"], slug + "/")]),
    ]
    return {"title": t["title"], "description": t["description"], "jsonld": jsonld}, main_html


def hub_page(site_url, problems_html):
    groups = []

    def card_photo(slug):  # each treatment's own hero photograph; Kids' dentistry has its own
        name, alt, pos = TREATMENTS[slug]["hero"] if slug in TREATMENTS else ("stock-kid-dentist", "A boy in the dental chair with the dentist beside him", "50% 45%")
        return picture(name, "(min-width: 1100px) 24vw, (min-width: 768px) 45vw, 100vw", alt, pos=pos, indent="                ")
    for g in treatments.GROUPS:
        tag = '<span class="tag">Specialty</span>' if g.get("specialty") else ""
        cards = "".join(f"""
            <li class="tcard reveal"><a href="{t['slug']}/">
              <span class="tcard__media media media--hover">
{card_photo(t['slug'])}
              </span>
              {tag}
              <h3>{t['name']}</h3>
              <p>{(TREATMENTS.get(t['slug']) or KIDS)['card']}</p>
              <span class="cta">Learn more</span>
            </a></li>""" for t in g["items"])
        groups.append(f"""
      <div class="tgroup-block">
        <div class="tgroup-block__head reveal">
          <h2>{g['title']}</h2>
          <p>{GROUP_CARDS[g['title']]}</p>
        </div>
        <ul class="tcards">{cards}
        </ul>
      </div>""")
    main_html = f"""  <main id="main" tabindex="-1">

    <!-- =================================================================== HERO -->
    <section class="page-hero" aria-labelledby="page-title">
      {{{{pic arha-dental-care-reception-south-mumbai-dental-clinic-01 | 100vw | Arha Dental Care reception: a curved front desk, soft seating and the Arha wordmark on marble | pos=50% 45% | eager}}}}
      <div class="page-hero__content">
        <div class="hero__text">
          {crumbs([("Home", ""), ("Treatments", "treatments/")])}
          <h1 id="page-title">Treatments</h1>
          <p class="hero__lede">Specialist care, smile and aesthetics, and everyday dentistry for the whole family.</p>
        </div>
      </div>
    </section>

    <section class="section" aria-label="All treatments">
      <div class="container">{"".join(groups)}
      </div>
    </section>

    <!-- =================================================================== COMMON PROBLEMS (shared with the homepage) -->
    <section class="section section--stone texture problems-section" id="common-problems" aria-labelledby="problems-title">
      <div class="container">
        <div class="section-head reveal">
          <h2 id="problems-title">Common problems we fix</h2>
          <p class="lede">Not sure which treatment you need? Start with what is bothering you.</p>
        </div>
{problems_html}
      </div>
    </section>
{closing("Not sure where to start?", "Book a consultation and we will explain your options plainly, with no obligation to go ahead.")}
  </main>
"""
    meta = {"title": "Dental Treatments in South Mumbai | Arha Dental Care, Peddar Road",
            "description": "All treatments at Arha Dental Care, Peddar Road, Mumbai: dental implants, full mouth rehabilitation, smile design, Invisalign, braces, root canal, crowns and kids' dentistry.",
            "jsonld": [crumbs_jsonld(site_url, [("Home", ""), ("Treatments", "treatments/")])]}
    return meta, main_html


def technology_page(site_url):
    blocks, index = [], []
    rotary = {"slug": "rotary-endodontics", "name": "Rotary endodontics", "group": "treat", "photo": "stock-endo-files", "pos": "50% 50%",
              "alt": "Fine endodontic files with coloured handles, laid out on a surface",
              "what": "Fine, flexible files driven by a motor, used to clean and shape the canals inside a tooth.",
              "for_you": "The canals are cleaned evenly during root canal treatment.", "treatments": ["root-canal-treatment"]}
    items = technology.ITEMS + [rotary]
    for key, name, sub in TECH_GROUPS:
        cards = []
        for t in [x for x in items if x["group"] == key]:
            links = t["treatments"] or []
            used = ("Used in every treatment" if not links else
                    "Used in: " + ", ".join(f'<a href="{s}/">{treatments.treatment(s)["name"]}</a>' for s in links))
            media = picture(t["photo"], "(min-width: 900px) 40vw, 100vw", t["alt"], pos=t["pos"], indent="                ")
            cards.append(f"""
            <article class="titem reveal" id="{t['slug']}" aria-labelledby="{t['slug']}-name">
              <div class="titem__media media">
{media}
              </div>
              <div class="titem__text">
                <h3 id="{t['slug']}-name">{t['name']}</h3>
                <dl>
                  <div><dt>What it is</dt><dd>{t['what']}</dd></div>
                  <div><dt>What it means for you</dt><dd>{t['for_you']}</dd></div>
                </dl>
                <p class="titem__used">{used}</p>
              </div>
            </article>""")
        index.append(f'<li><a href="technology/#group-{key}" data-spy="group-{key}">{name}</a></li>')
        blocks.append(f"""
          <details class="tgroup" id="group-{key}" open>
            <summary><h2 class="tgroup__name">{name}</h2><span class="tgroup__sub">{sub}</span><span class="plus" aria-hidden="true"></span></summary>
            <div class="tgroup__items">{"".join(cards)}
            </div>
          </details>""")
    main_html = f"""  <main id="main" tabindex="-1">

    <!-- =================================================================== HERO -->
    <section class="page-hero" aria-labelledby="page-title">
      {{{{pic stock-handpieces-dark | 100vw | Dental handpieces on their holders, softly lit | pos=50% 50% | eager}}}}
      <div class="page-hero__content">
        <div class="hero__text">
          {crumbs([("Home", ""), ("Technology", "technology/")])}
          <h1 id="page-title">Technology</h1>
          <p class="hero__lede">The equipment behind your care, following your visit: how we see, plan, treat and keep you safe.</p>
        </div>
      </div>
    </section>

    <!-- Only equipment visible in Arha's photographs, plus rotary endodontics (on the clinic's own site).
         More is listed once the clinic confirms its equipment (tools/technology.py CANDIDATES, notes/TO-CONFIRM.md). -->
    <section class="section" aria-label="Our technology">
      <div class="container tech-page">
        <nav class="tech-index" aria-label="Technology groups">
          <ol>{"".join(index)}</ol>
        </nav>
        <div class="tech-groups" data-spy-root>{"".join(blocks)}
        </div>
      </div>
    </section>

    <section class="section section--stone texture" aria-labelledby="why-title">
      <div class="container">
        <div class="section-head reveal">
          <h2 id="why-title">Why it matters</h2>
          <p class="lede">Good equipment does not replace judgement. It helps a careful dentist see more, plan more exactly and work more gently, and it keeps every visit clean and safe.</p>
          <p class="intro__more">Suitability for any treatment is decided at your consultation.</p>
        </div>
      </div>
    </section>
{closing()}
  </main>
"""
    meta = {"title": "Technology at Arha Dental Care | Dental Clinic on Peddar Road, Mumbai",
            "description": "The technology at Arha Dental Care, Peddar Road: in-house panoramic X-ray, treatment rooms, planning on screen, rotary endodontics and a dedicated sterilisation room.",
            "jsonld": [crumbs_jsonld(site_url, [("Home", ""), ("Technology", "technology/")])]}
    return meta, main_html


def kids_page(site_url):
    """Kids' dentistry: for parents, led by photographs. Facts: the brief (first-visit guidance, the 47% figure and its source,
    toothpaste amounts, knocked-out tooth) and the clinic's site (check-ups, sealants, fluoride, early
    orthodontic assessment, braces and aligners for children). No specialist is named until confirmed."""
    ages = [("0-2", "0 to 2", "The first teeth, the gums and how the teeth are coming in, and the earliest signs of decay.",
             "Wipe the gums after feeds. Once teeth arrive, brush twice a day with a smear of fluoride toothpaste the size of a grain of rice.",
             "Avoid putting your child to sleep with a bottle of milk or juice. Thumb-sucking and dummies are normal at this age."),
            ("3-5", "3 to 5", "All twenty baby teeth, decay between the back teeth, and how the bite is developing.",
             "A pea-size amount of fluoride toothpaste, twice a day, with an adult brushing or helping.",
             "Keep sweet snacks and drinks to mealtimes. Night-time bottles should have stopped."),
            ("6-9", "6 to 9", "The first adult molars and front teeth, sealants on the new molars, and a first orthodontic check around age 7.",
             "Brush twice a day with fluoride toothpaste, with an adult checking until your child brushes well alone.",
             "Thumb-sucking that continues as the adult front teeth arrive can affect how they grow; we can help. Mouthguards for contact sport."),
            ("10-14", "10 to 14", "Baby teeth falling out on time, adult teeth coming in, crowding and the bite; braces or aligners if needed.",
             "Twice-daily brushing with fluoride toothpaste, and cleaning between the teeth.",
             "Sugary and fizzy drinks between meals. Mouthguards for sport.")]

    shots = {"0-2": ("stock-kid-brush-wood", "A small wooden toothbrush for a first set of teeth"), "3-5": ("stock-kid-brush-bright", "A bright children's toothbrush"),
             "6-9": ("stock-kid-brush-electric", "A children's electric toothbrush"), "10-14": ("stock-aligner-hands", "Hands holding a clear aligner and its case")}
    guide = photo_tabs("ages", "Age group", [
        (k, f"Ages {n}", *shots[k], f'<h3 class="visually-hidden">Ages {n}</h3><dl class="vs">'
                                    f"<div><dt>What we check</dt><dd>{chk}</dd></div><div><dt>Care at home</dt><dd>{home}</dd></div>"
                                    f"<div><dt>Habits</dt><dd>{hab}</dd></div></dl>")
        for k, n, chk, home, hab in ages], cls="itabs--photo itabs--split")
    visit = [("A short, unhurried visit", "Your child can sit on your lap. We keep the first visit brief."),
             ("Tell, show, do", "We explain each step in simple words, show the instrument, and only then use it."),
             ("A gentle look", "We count the teeth and check the gums and bite. Nothing is forced; if your child is not ready, we try again next time."),
             ("Advice for you", "Brushing, toothpaste, diet and habits, and when to come back.")]
    faq = [("When should my child first see a dentist?", "By the first birthday, or within six months of the first tooth appearing."),
           ("Are baby teeth really important?", "Yes. They let your child chew and speak properly, and they hold space for the adult teeth. Decay in baby teeth can cause pain and infection."),
           ("What if my child is scared?", "We go at your child’s pace, explain everything first and never force anything. Short, positive visits early on make later visits much easier."),
           ("Are dental X-rays safe for children?", "Dental X-rays use a very small dose. We take them only when they will tell us something we cannot see, and we use the fewest needed."),
           ("What do you offer for children?", "Check-ups and cleaning, fluoride, pit and fissure sealants, an early orthodontic assessment around age 7, and braces or clear aligners for children and teens who need them."),
           ("What if a tooth is knocked out?", "A baby tooth should not be put back: press a clean cloth on the gum and bring your child in. An adult tooth should be held by the crown, rinsed briefly in milk, put back or kept in milk, and seen within 30 to 60 minutes. See <a href=\"emergency/\">dental emergencies</a>.")]
    trail = [("Home", ""), ("Treatments", "treatments/"), ("Kids’ dentistry", "kids-dentistry/")]
    main_html = f"""  <main id="main" tabindex="-1">

    <!-- =================================================================== HERO -->
    <section class="page-hero" aria-labelledby="page-title">
      {{{{pic stock-parent-child | 100vw | A parent helping a young child brush their teeth | pos=50% 40% | eager}}}}
      <div class="page-hero__content">
        <div class="hero__text">
          {crumbs(trail)}
          <p class="eyebrow eyebrow--light">Paediatric dentistry</p>
          <h1 id="page-title">Kids’ dentistry</h1>
          <p class="hero__lede">Gentle, unhurried dental care for babies, children and teenagers, with parents welcome in the room.</p>
          <div class="hero__actions">
            <a class="cta" href="book/">Book a first visit</a>
            <a class="cta" href="tel:+910000000000" data-call="kids_hero">Call <span data-show="phone">+91 00000 00000</span></a>
          </div>
        </div>
      </div>
    </section>

    <!-- =================================================================== FIRST VISIT + WHY IT MATTERS -->
    <section class="section" aria-labelledby="first-title">
      <div class="container split split--even">
        <div class="split__text reveal">
          <h2 id="first-title">First visit by the first birthday</h2>
          <p class="lede">Or within six months of the first tooth, whichever comes first.</p>
          <p>Tooth decay in young children, called early childhood caries, is common in India and often starts before parents notice it. Early visits find it while it is small, and teach the habits that prevent it. Whether you call it paediatric or pediatric dentistry, the aim is the same.</p>
          <p class="cite">International paediatric dentistry guidance, also argued for India in the Journal of the Indian Society of Pedodontics and Preventive Dentistry (2024), “Visit to the Dentist at Age One” policy paper.</p>
        </div>
        <figure class="stat reveal">
          <p class="stat__num">About 47%</p>
          <figcaption>
            <p>of young children in India have early childhood caries.</p>
            <p class="cite">Devan, Ramanarayanan &amp; Janakiram, Indian Journal of Public Health, 2022: a meta-analysis of 71 studies.</p>
          </figcaption>
        </figure>
      </div>
    </section>

    <!-- =================================================================== AGE GUIDE -->
    <section class="section section--stone texture ix ix--ages" aria-labelledby="ix-title">
      <div class="container">
        <div class="section-head reveal">
          <h2 id="ix-title">A guide by age</h2>
          <p class="lede">What we check, care at home, and habits worth watching, at each stage.</p>
        </div>
        <div class="reveal">{guide}</div>
      </div>
    </section>
{section("", "visit-steps-title", "Your child’s first visit, step by step", steps_block(visit))}
{faq_block(faq)}{closing("Book your child’s first visit", "A short, gentle visit to meet us, look at the teeth and answer your questions.")}
  </main>
"""
    meta = {"title": KIDS["title"], "description": KIDS["description"],
            "jsonld": [{"@context": "https://schema.org", "@type": "MedicalProcedure", "name": "Paediatric dentistry",
                        "alternateName": "Pediatric dentistry", "url": site_url + "kids-dentistry/"},
                       faq_jsonld(faq), crumbs_jsonld(site_url, trail)]}
    return meta, main_html


def all_pages(site_url, problems_html):
    """(slug, meta, main html) for every generated page."""
    out = [(slug, *treatment_page(slug, site_url)) for slug in TREATMENTS]
    out.append(("kids-dentistry", *kids_page(site_url)))
    out.append(("treatments", *hub_page(site_url, problems_html)))
    out.append(("technology", *technology_page(site_url)))
    return out
