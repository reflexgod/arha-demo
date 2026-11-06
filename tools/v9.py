"""v9 design upgrade (Viraaj's "v5 upgrade" + "design upgrade" briefs, 6 Nov 2026): shared blocks for the homepage
and the inner pages. tools/pages.py calls inject() on every inner page after it is built.

Placeholders the clinic must confirm are marked TODO-CONFIRM here and listed in notes/TO-CONFIRM.md.
"""
import re

from home import ARROW

SAMPLE_NOTE = "Sample images for this demo. Arha’s own cases, shared with patient consent, will replace them before launch."

# n, label (what the sample shows). All are whitening-style samples (tools/samples.py): the same photograph both sides.
SMILES = [(1, "Brighter shade"), (5, "Brighter shade"), (4, "Even colour"), (2, "Brighter shade"), (3, "Softer shade"), (6, "Brighter shade")]


def smile_card(n, label, i="        "):
    src = lambda side: f"assets/stock/sample-smile-{n}-{side}-640.webp 640w, assets/stock/sample-smile-{n}-{side}-1200.webp 1200w"  # noqa: E731
    sizes = "(min-width: 900px) 33vw, 90vw"
    return f"""{i}<li class="smile-card reveal">
{i}  <figure class="ba smile-ba" data-ba data-colour-group style="--pos: 50%">
{i}    <div class="ba__layer ba__layer--after"><img src="assets/stock/sample-smile-{n}-after-640.webp" srcset="{src('after')}" sizes="{sizes}" width="1200" height="900" loading="lazy" decoding="async" alt="Sample smile after whitening (stock photograph, simulated)"></div>
{i}    <div class="ba__layer ba__layer--before"><img src="assets/stock/sample-smile-{n}-before-640.webp" srcset="{src('before')}" sizes="{sizes}" width="1200" height="900" loading="lazy" decoding="async" alt="Sample smile before whitening (stock photograph, simulated)"></div>
{i}    <span class="ba__tag ba__tag--before" aria-hidden="true">Before</span><span class="ba__tag ba__tag--after" aria-hidden="true">After</span>
{i}    <span class="smile-card__sample">Sample</span>
{i}    <span class="ba__line" aria-hidden="true"></span>
{i}    <span class="ba__handle" role="slider" tabindex="0" aria-label="Compare before and after: {label.lower()} (sample)" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50" aria-valuetext="Half before, half after"></span>
{i}  </figure>
{i}  <p class="smile-card__label">{label}</p>
{i}</li>"""


def smile_results(count, title_id="results-title", more=True):
    cards = "\n".join(smile_card(n, label) for n, label in SMILES[:count])
    link = '\n        <p class="smile-results__more"><a class="link" href="gallery/#results">See more results</a></p>' if more else ""
    return f"""
    <!-- =================================================================== SMILE RESULTS (stock samples, tools/samples.py) -->
    <section class="smile-results" id="results" aria-labelledby="{title_id}">
      <div class="v9-head reveal">
        <h2 id="{title_id}">Smile results</h2>
        <p class="smile-results__note">{SAMPLE_NOTE}</p>
      </div>
      <ul class="smile-results__grid" role="list">
{cards}
      </ul>{link}
    </section>
"""


# ------------------------------------------------------------------ Dr. Nikhil: the placeholder portrait (no stock face)
def doctor_frame():
    return """<div class="doc-frame" role="img" aria-label="Portrait placeholder: Dr. Nikhil V. Jain, prosthodontist and implantologist. Photo coming soon">
          <span class="doc-frame__mark" aria-hidden="true"></span>
          <span class="doc-frame__name">Dr. Nikhil V. Jain</span>
          <span class="doc-frame__role">Prosthodontist &amp; implantologist</span>
          <span class="doc-frame__soon">Photo coming soon</span>
        </div>"""


# ------------------------------------------------------------------ Dental implants: the journey, a vertical timeline
# TODO-CONFIRM: every visit count and week below is a typical placeholder until Dr. Nikhil confirms Arha's own.
IMPLANT_STEPS = [
    ("Consultation &amp; 3D planning", "An examination, X-rays and a 3D scan where needed. You see your options and the plan before anything begins.", "1–2 visits", "Week 1"),  # TODO-CONFIRM
    ("Implant placement", "The implant is placed under local anaesthetic, in a single appointment.", "1 visit", "Week 2–4"),  # TODO-CONFIRM
    ("Healing", "The implant settles into the jaw. A temporary tooth can often be worn in the meantime.", "1–2 short checks", "About 8–12 weeks"),  # TODO-CONFIRM
    ("Final crown", "Your crown is made to match your own teeth and fitted on the implant.", "2 visits", "About 1–2 weeks"),  # TODO-CONFIRM
]


def implant_timeline():
    items = "".join(f"""
          <li class="vtl__step reveal">
            <span class="vtl__dot" aria-hidden="true"></span>
            <h3>{title}</h3>
            <p>{text}</p>
            <p class="vtl__meta"><span>{visits}</span><span>{weeks}</span></p>
          </li>""" for title, text, visits, weeks in IMPLANT_STEPS)
    return f"""
    <!-- =================================================================== IMPLANT JOURNEY (v9; numbers TODO-CONFIRM) -->
    <section class="section vtl-section" aria-labelledby="vtl-title">
      <div class="container">
        <div class="v9-head reveal">
          <h2 id="vtl-title">Your implant journey</h2>
          <p>Typical timeline. Dr. Nikhil confirms yours at consultation.</p>
        </div>
        <ol class="vtl">{items}
        </ol>
      </div>
    </section>
"""


# ------------------------------------------------------------------ Smile design: whitening shade slider (SVG, no photos)
SHADES = ["A3", "A2", "B2", "A1", "B1"]  # darker to lighter, as on a shade guide


def shade_slider():
    teeth = ""
    # eight upper front teeth drawn as simple rounded shapes; widths mirror a real arch (centrals widest)
    widths = [34, 40, 46, 56, 56, 46, 40, 34]
    x = 10
    for w in widths:
        h = 70 if w == 56 else 64 if w == 46 else 58
        teeth += f'<path d="M{x} 20 h{w} v{h - 14} q0 14 -14 14 h{-(w - 28)} q-14 0 -14 -14 z" />'
        x += w + 4
    return f"""
    <!-- =================================================================== WHITENING SHADE SLIDER (v9; illustration, site.js 26) -->
    <section class="section shade-section" aria-labelledby="shade-title">
      <div class="container">
        <div class="v9-head reveal">
          <h2 id="shade-title">See the shade change</h2>
          <p>Drag from shade A3 to B1, as on a dentist’s shade guide.</p>
        </div>
        <div class="shade reveal" data-shade>
          <svg class="shade__teeth" viewBox="0 0 {x + 6} 104" role="img" aria-label="An illustrated row of front teeth showing the selected shade">
            <rect x="0" y="0" width="{x + 6}" height="22" rx="2" class="shade__gum"/>
            <g class="shade__row">{teeth}</g>
          </svg>
          <div class="shade__control">
            <label for="shade-range">Shade <output data-shade-out>A3</output></label>
            <input id="shade-range" type="range" min="0" max="{len(SHADES) - 1}" step="1" value="0" aria-valuetext="Shade A3" data-shade-range>
            <p class="shade__ends" aria-hidden="true"><span>A3</span><span>B1</span></p>
          </div>
          <p class="shade__caption">An illustration, not a prediction. Whitening results vary from person to person; some teeth lighten more than others, and fillings and crowns do not change colour.</p>
        </div>
      </div>
    </section>
"""


# ------------------------------------------------------------------ inner pages
def inject(slug, html):
    """Add the v9 blocks to the inner pages built by tools/pages.py (before relocate() fixes the paths)."""
    if slug == "dental-implants":
        # the vertical journey replaces the sticky "How it works" story on this page
        html = re.sub(r'\s*<section class="section section--flush process".*?</section>\n', implant_timeline(), html, count=1, flags=re.S)
    if slug == "smile-design":
        html = html.replace('    <section class="section section--stone glance"', shade_slider() + '    <section class="section section--stone glance"', 1)
    if slug == "gallery":
        html = html.replace('    <section class="section gal-intro"', smile_results(6, more=False) + '    <section class="section gal-intro"', 1)
    if slug == "doctors":
        card = f"""
    <section class="section doc-intro-v9" aria-label="Dr. Nikhil V. Jain">
      <div class="container doc-intro-v9__inner">
        {doctor_frame()}
      </div>
    </section>
"""
        html = html.replace('    <section class="section docs-intro"', card + '    <section class="section docs-intro"', 1)
    return html
