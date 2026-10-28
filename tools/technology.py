"""Arha's technology: one list drives the homepage Technology band and the /technology/ page.

Only what can be seen in Arha's own photographs is described, with no brand or model names, until
the clinic confirms its equipment list (notes/TO-CONFIRM.md). Candidates the clinic may confirm
later live in CANDIDATES and are not published.
"""
from picture import picture

# group: see | plan | treat | safe (the patient's path on /technology/)
ITEMS = [
    {
        "slug": "panoramic-x-ray",
        "name": "Panoramic X-ray, in-house",
        "short": "Panoramic X-ray",
        "group": "see",
        "photo": "dental-implant-equipment-arha-dental-care-mumbai",
        "pos": "50% 24%",
        "alt": "Arha's X-ray room: a floor-standing panoramic X-ray unit against a marble wall, with its computer beside it",
        "what": "A floor-standing panoramic X-ray unit in its own room, which images all your teeth and both jaws in one pass.",
        "for_you": "Routine X-rays are taken here during your visit, with no trip to a separate imaging centre.",
        "treatments": ["dental-implants", "full-mouth-rehabilitation", "root-canal-treatment", "orthodontics"],
    },
    {
        "slug": "treatment-rooms",
        "name": "Treatment rooms",
        "short": "Treatment rooms",
        "group": "treat",
        "photo": "dental-operatory-arha-dental-care-peddar-road-01",
        "pos": "50% 60%",
        "alt": "An Arha treatment room: a cream dental chair under an overhead light, marble walls and a laptop on the counter",
        "what": "Rooms with a fully adjustable dental chair, an overhead operating light and a screen beside the chair.",
        "for_you": "You lie back comfortably, the work area is well lit, and your images can be shown to you as we explain.",
        "treatments": ["general-dentistry", "root-canal-treatment", "crowns-bridges", "cosmetic-dentistry"],
    },
    {
        "slug": "planning-desk",
        "name": "Planning on screen",
        "short": "Planning on screen",
        "group": "plan",
        "photo": "dental-operatory-arha-dental-care-peddar-road-04",
        "pos": "50% 50%",
        "alt": "A consultation desk in a treatment room with a large monitor, a laptop and notebooks",
        "what": "A consultation desk in the treatment room, with a large monitor for X-rays and photographs.",
        "for_you": "Your options are talked through on screen, at a desk, before anything is decided.",
        "treatments": ["smile-design", "dental-implants", "full-mouth-rehabilitation", "invisalign"],
    },
    {
        "slug": "sterilisation-room",
        "name": "Steam sterilisation",
        "short": "Sterilisation",
        "group": "safe",
        "photo": "autoclave-pantry-equipment-arha-dental-care-mumbai",
        "pos": "70% 62%",
        "alt": "Arha's sterilisation room: a benchtop steam steriliser beside a sink, under pale cabinets",
        "what": "A separate sterilisation room with a benchtop steam steriliser and its own sink.",
        "for_you": "Instruments are cleaned and sterilised in their own room, away from where you are treated.",
        "treatments": [],
    },
    {
        "slug": "instrument-care",
        "name": "Instrument care",
        "short": "Instrument care",
        "group": "safe",
        "photo": "dental-dentistry-equipment-arha-dental-care-mumbai",
        "pos": "50% 50%",
        "alt": "An automatic handpiece cleaning and oiling unit next to a white water distiller on a counter",
        "what": "An automatic unit that cleans and oils the dental handpieces, beside a water distiller.",
        "for_you": "Handpieces are maintained after use, and distilled water is made on site for the equipment.",
        "treatments": [],
    },
]

# To confirm with the clinic before anything below is published (brief section 7)
CANDIDATES = [
    "CBCT / 3D X-ray (is the panoramic unit 3D-capable?)", "Intraoral scanner", "RVG digital X-ray",
    "Dental microscope", "Dental laser", "Digital smile design", "Guided implant surgery", "CAD/CAM crowns",
    "Rotary endodontics (confirmed on the clinic's site)", "Computer-controlled anaesthesia",
    "Class B autoclave (the steriliser's class)", "3D printer",
]

ARROW = '<svg class="arrow arrow--right" viewBox="0 0 12 10" aria-hidden="true" focusable="false"><path d="M1 5h10M7 1l4 4-4 4"/></svg>'


def band(indent="      "):
    """Homepage Technology band: accessible tabs; each panel is a real Arha photo and two lines."""
    i = indent
    tabs, panels = [], []
    for n, t in enumerate(ITEMS):
        sel = n == 0
        tabs.append(f'{i}    <button class="tech__tab" type="button" role="tab" id="tt-{t["slug"]}" aria-controls="tp-{t["slug"]}" '
                    f'aria-selected="{str(sel).lower()}"{"" if sel else " tabindex=\"-1\""}><span class="tech__num">{n + 1:02d}</span>{t["short"]}</button>')
        pic = picture(t["photo"], "(min-width: 900px) 56vw, 100vw", t["alt"], pos=t["pos"], indent=i + "      ")
        panels.append(
            f'{i}  <div class="tech__panel" role="tabpanel" id="tp-{t["slug"]}" aria-labelledby="tt-{t["slug"]}" tabindex="0"{"" if sel else " hidden"}>\n'
            f'{i}    <div class="tech__media media">\n{pic}\n{i}    </div>\n'
            f'{i}    <dl class="tech__text">\n'
            f'{i}      <div><dt>What it is</dt><dd>{t["what"]}</dd></div>\n'
            f'{i}      <div><dt>What it means for you</dt><dd>{t["for_you"]}</dd></div>\n'
            f'{i}    </dl>\n'
            f'{i}  </div>')
    return (f'{i}<div class="tech__body" data-tabs>\n'
            f'{i}  <div class="tech__tabs" role="tablist" aria-label="Arha’s technology" aria-orientation="vertical">\n'
            + "\n".join(tabs) + f'\n{i}  </div>\n'
            + "\n".join(panels) + f'\n{i}</div>\n')
