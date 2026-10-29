"""The homepage <main>, in apaaesthetic.com's rhythm (notes/FINAL-v4.md section 5): ten large, calm
sections, each one idea. Problems first (notes/V4-PROBLEMS-FIRST.md): "What brings you in?" follows the hero. Written into index.html by tools/pages.py; the shared components it uses
(before/after slider, hotspots, expanding panels, review carousel, sticky story) live in site.js 17.

Facts only from the clinic. Before/after pairs are stock samples (tools/pairs.py), each labelled
"Sample case for demo", until consented cases replace them.
"""
import html

import more_pages
import problems
import treatments
from picture import picture

ARROW = '<svg class="arrow arrow--right" viewBox="0 0 12 10" aria-hidden="true" focusable="false"><path d="M1 5h10M7 1l4 4-4 4"/></svg>'
SAMPLE = "Sample case for demo"  # on every sample case (notes/TO-CONFIRM.md)
SIMULATION = "Simulation for demo"  # on every before/after slider: both sides are one photograph (tools/pairs.py)

REVIEWS = [  # real Google reviews (lines quoted as written; "grate" corrected to "great")
    "He managed my pain and resolved the problem on the same day.",
    "I had a very positive experience getting my cavity treated by Dr. Nikhil Jain.",
    "Excellent doctor and excellent service.",
    "I would highly recommend Dr. Jain to anyone considering orthodontic treatment.",
    "He is patient, gentle and takes the time to answer all my questions.",
    "The cap procedure was absolutely painless at Arha Dental Care.",
    "It was a smooth experience with great advice that gave her a comforting outcome.",
]

# Technology (v4 fixes 3, point 3): only what sets Arha apart, each on one of Arha's own photographs.
# (photo, alt, x, y, name, what it is, what it means for you). Positions in % of each photograph.
HOTSPOTS = [
    ("dental-implant-equipment-arha-dental-care-mumbai", "Arha's X-ray room: a floor-standing panoramic X-ray unit against a marble wall",
     "46%", "27%", "An in-house panoramic X-ray",
     "A panoramic X-ray unit in a room of its own at the clinic, showing all the teeth and both jaws in one image.",
     "Your X-rays are taken during your visit, so your plan can be explained the same day, with no trip to an imaging centre."),
    ("dental-operatory-arha-dental-care-peddar-road-01", "An Arha treatment room; the laptop on the counter shows a 3D model of a patient's teeth",
     "65%", "58%", "Digital 3D models of your teeth",
     "Scans of your teeth are viewed on screen in the treatment room as 3D models.",
     "You can see your own teeth from every side, and how a plan would change them, before any treatment starts."),
    ("autoclave-pantry-equipment-arha-dental-care-mumbai", "Arha's sterilisation room: the steriliser on the counter beside a sink",
     "80%", "50%", "A sterilisation room of its own",
     "Instruments are cleaned and sterilised in a separate room, in a steam steriliser, away from where you are treated.",
     "Everything used for your treatment has been through the same careful routine, every time."),
]

TRIO = [("arha-dental-care-exterior-dental-clinic-peddar-road", "50% 40%",
         "The door of suite 107 at Arha: the gold emblem and the names of Dr. Vasant P. Jain and Dr. Nikhil V. Jain",
         "Legacy since 1980", "What began as Dr. Vasant P. Jain’s family practice is now Arha: the same trust, in a space designed for modern dentistry.",
         "founder/", "About the founder"),
        ("arha-dental-care-delivery-unit", "50% 45%", "The instrument holder at an Arha chair, with its handpieces ready",
         "Specialist precision", "Dr. Nikhil V. Jain is an MDS Prosthodontist and ITI Scholar, focused on implants and full mouth rehabilitation.",
         "doctors/", "Meet the doctors"),
        ("arha-dental-care-consultation-desk", "50% 50%", "The consultation desk in an Arha treatment room",
         "Designed for you", "Every treatment plan is considered in relation to your face, your bite and your comfort, never a template.",
         "treatments/", "Explore treatments")]

JOURNEY = [("stock-consult-desk", "50% 40%", "A dentist explaining a treatment plan to a patient at a desk, with X-rays on screen", "Consultation",
            "We listen first: your concerns, your goals and your history, then a thorough examination and a clear explanation of your options."),
           ("arha-dental-care-chair-window", "50% 55%", "The dental chair under its light in an Arha treatment room", "Your treatment",
            "Planned in detail and carried out with precision, at a pace that keeps you comfortable."),
           ("arha-dental-care-reception-wide", "50% 50%", "Arha's reception and waiting area", "Lifelong care",
            "Your treatment is the start of a long relationship: reviews, cleanings and care to protect your result for years.")]

def ba(c, sizes, i="          ", eager=False):
    """Before/after slider (site.js 17) for a same-photograph simulation: the before on the left of the line,
    the after on the right. Drag anywhere on the photograph, click or tap to jump, arrow keys on the handle."""
    name = c["name"].lower()
    before = picture(c["before"], sizes, f"Before: {name} (simulation for demo)", pos=c.get("pos"), eager=eager, indent=i + "    ")
    after = picture(c["img"], sizes, f"After: {name} (simulation for demo)", pos=c.get("pos"), eager=eager, indent=i + "    ")
    return f"""{i}<figure class="ba" data-ba data-colour-group style="--pos: 50%">
{i}  <div class="ba__layer ba__layer--after">
{after}
{i}  </div>
{i}  <div class="ba__layer ba__layer--before">
{before}
{i}  </div>
{i}  <span class="ba__tag ba__tag--before" aria-hidden="true">Before</span><span class="ba__tag ba__tag--after" aria-hidden="true">After</span>
{i}  <span class="ba__line" aria-hidden="true"></span>
{i}  <span class="ba__handle" role="slider" tabindex="0" aria-label="Compare before and after" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50" aria-valuetext="Half before, half after"></span>
{i}  <figcaption class="sample-line">{SIMULATION}</figcaption>
{i}</figure>"""


def case_card(c, prefix="", i="      ", sizes="(min-width: 900px) 30vw, 100vw", attrs=""):
    """A sample case as an elegant card: its image, the title, "See the case" (no mouth pairs, no portraits)."""
    note = SIMULATION if c.get("before") else SAMPLE
    return f"""
{i}<li class="case-card reveal"{attrs}>
{i}  <a href="{prefix}our-work/{c['slug']}/">
{i}    <span class="case-card__media media media--hover">
{picture(c['card'], sizes, c['card_alt'], pos=c.get('card_pos'), indent=i + '      ')}
{i}    </span>
{i}    <span class="sample-line">{note}</span>
{i}    <span class="case-card__name">{html.escape(c['name'])}</span>
{i}    <span class="case-card__meta">{html.escape(c['meta'])}</span>
{i}    <span class="link">See the case{ARROW}</span>
{i}  </a>
{i}</li>"""


def results_grid(cases, prefix="", i="      "):
    """Every sample case as a card; data-cat feeds the Our work filter."""
    tiles = "".join(case_card(c, prefix, i + "  ", attrs=f' data-cat="{c["cat"]}"') for c in cases)
    return f'{i}<ul class="case-cards" data-work-grid>{tiles}\n{i}</ul>'


def results_home(cases, i="        "):
    """Homepage: one large slider (the featured simulation), then the other cases as cards."""
    first = next(c for c in cases if c.get("before"))
    rest = [c for c in cases if c is not first]
    return f"""{i}<div class="featured-case reveal">
{ba(first, '(min-width: 900px) 80vw, 100vw', i + '  ')}
{i}  <div class="featured-case__text">
{i}    <h3>{html.escape(first['name'])}</h3>
{i}    <p>{html.escape(first['meta'])}</p>
{i}    <a class="link" href="our-work/{first['slug']}/">See the case{ARROW}</a>
{i}  </div>
{i}</div>
{i}<ul class="case-cards case-cards--home">{"".join(case_card(c, "", i + "  ") for c in rest)}
{i}</ul>"""


def problems_stage(prefix="", i="      "):
    """Common problems we fix: a list of problems beside a large photo stage that crossfades."""
    tabs, panels = [], []
    for n, p in enumerate(treatments.PROBLEMS):
        sel = n == 0
        photo, alt = treatments.PHOTOS[p["slug"]]
        links = " ".join(f'<a class="link" href="{prefix}{s}/">{treatments.treatment(s)["name"]}</a>' for s in p["treat"])
        tabs.append(f'{i}    <button class="problems__tab" type="button" role="tab" id="pt-{p["slug"]}" aria-controls="pp-{p["slug"]}" '
                    f'aria-selected="{str(sel).lower()}"{"" if sel else " tabindex=\"-1\""}>{p["name"]}</button>')
        panels.append(f"""{i}  <div class="problems__panel" role="tabpanel" id="pp-{p['slug']}" aria-labelledby="pt-{p['slug']}"{'' if sel else ' hidden'}>
{i}    <div class="problems__photo media">
{picture(photo, '(min-width: 900px) 62vw, 100vw', alt + " (stock photograph)", indent=i + '      ')}
{i}    </div>
{i}    <div class="problems__text">
{i}      <p>{p['lines'][0]} {p['lines'][1]}</p>
{i}      <p class="problems__label">Usually treated with</p>
{i}      <p class="problems__links">{links}</p>
{i}    </div>
{i}  </div>""")
    return (f'{i}<div class="problems" data-tabs>\n'
            f'{i}  <div class="problems__list" role="tablist" aria-label="Common problems" aria-orientation="vertical">\n'
            + "\n".join(tabs) + f"\n{i}  </div>\n{i}  <div class=\"problems__stage\">\n" + "\n".join(panels)
            + f"\n{i}  </div>\n{i}</div>")


def story(steps, i="      ", label="Your journey at Arha"):
    """Sticky scroll storytelling: the photograph stays pinned and crossfades as each step scrolls past."""
    imgs = "".join(f"""
{i}    <div class="story__img{' is-active' if n == 0 else ''}" data-i="{n}">
{picture(name, '(min-width: 900px) 50vw, 100vw', alt, pos=pos, indent=i + '      ')}
{i}    </div>""" for n, (name, pos, alt, _t, _b) in enumerate(steps) if name)
    items = "".join(f"""
{i}    <li class="story__step{' is-active' if n == 0 else ''}" data-i="{n}">
{i}      <p class="story__num">{n + 1:02d}</p>
{i}      <h3>{t}</h3>
{i}      <p>{b}</p>
{i}    </li>""" for n, (_n, _p, _a, t, b) in enumerate(steps))
    return f"""{i}<div class="story" data-story aria-label="{label}">
{i}  <div class="story__media">{imgs}
{i}  </div>
{i}  <ol class="story__steps">{items}
{i}  </ol>
{i}</div>"""


def carousel(quotes, i="        "):
    slides = "".join(f"""
{i}    <li class="quotes__slide"><blockquote><p>“{q}”</p></blockquote><p class="quotes__by">Google review</p></li>""" for q in quotes)
    return f"""{i}<div class="drag drag--quotes" data-drag aria-roledescription="carousel" aria-label="Google reviews">
{i}  <ul class="drag__track">{slides}
{i}  </ul>
{i}  <div class="drag__ui">
{i}    <button class="drag__btn drag__btn--prev" type="button" aria-label="Previous review"></button>
{i}    <span class="drag__progress" aria-hidden="true"><span></span></span>
{i}    <button class="drag__btn drag__btn--next" type="button" aria-label="Next review"></button>
{i}  </div>
{i}</div>"""


def hotspots(i="      "):
    """Three of Arha's own photographs side by side, one numbered marker on each; the card below says what
    it is and what it means for you (site.js 17, [data-spots])."""
    shots, panels = [], []
    for n, (photo, alt, x, y, name, what, you) in enumerate(HOTSPOTS):
        shots.append(f"""{i}    <figure class="spots__shot">
{picture(photo, '(min-width: 900px) 33vw, 80vw', alt, indent=i + '      ')}
{i}      <button class="spot" type="button" style="--x: {x}; --y: {y}" aria-expanded="{str(n == 0).lower()}" aria-controls="hs-{n}"><span aria-hidden="true">{n + 1}</span><span class="visually-hidden">{name}</span></button>
{i}    </figure>""")
        panels.append(f"""{i}    <div class="spots__card" id="hs-{n}"{'' if n == 0 else ' hidden'}>
{i}      <p class="spots__num">{n + 1:02d}</p>
{i}      <h3>{name}</h3>
{i}      <dl>
{i}        <div><dt>What it is</dt><dd>{what}</dd></div>
{i}        <div><dt>What it means for you</dt><dd>{you}</dd></div>
{i}      </dl>
{i}    </div>""")
    return f"""{i}<div class="spots spots--three" data-spots>
{i}  <div class="spots__row">
{chr(10).join(shots)}
{i}  </div>
{i}  <div class="spots__cards">
{chr(10).join(panels)}
{i}  </div>
{i}</div>"""


def xpanels(i="      "):
    items = "".join(f"""
{i}  <li class="xpanel{' is-active' if n == 0 else ''}" data-xpanel tabindex="0">
{picture(name, '(min-width: 900px) 50vw, 100vw', alt, pos=pos, indent=i + '    ')}
{i}    <div class="xpanel__body">
{i}      <h3>{title}</h3>
{i}      <div class="xpanel__more">
{i}        <p>{text}</p>
{i}        <a class="link link--light" href="{href}">{cta}</a>
{i}      </div>
{i}    </div>
{i}  </li>""" for n, (name, pos, alt, title, text, href, cta) in enumerate(TRIO))
    return f'{i}<ul class="xpanels" data-xpanels>{items}\n{i}</ul>'


def tour_figure(prefix="", i="        ", sizes="(min-width: 900px) 30vw, 80vw"):
    return f"""{i}<figure class="tour reveal" data-tour data-base="{prefix}assets/video/tour-">
{i}  <picture class="fill">
{i}    <source type="image/avif" srcset="{prefix}assets/video/tour-poster-720.avif 720w, {prefix}assets/video/tour-poster-1080.avif 1080w" sizes="{sizes}">
{i}    <source type="image/webp" srcset="{prefix}assets/video/tour-poster-720.webp 720w, {prefix}assets/video/tour-poster-1080.webp 1080w" sizes="{sizes}">
{i}    <img src="{prefix}assets/video/tour-poster-720.jpg" width="720" height="1280" loading="lazy" decoding="async" alt="Arha's reception, the first frame of the clinic tour">
{i}  </picture>
{i}  <button class="tour__play" type="button">
{i}    <span class="tour__icon" aria-hidden="true"></span>
{i}    <span class="tour__label">Play the clinic tour <span class="tour__len">1 min 24 s · no sound</span></span>
{i}  </button>
{i}</figure>"""


def main_html(visit):
    cases = more_pages.cases()
    return f"""  <main id="main" tabindex="-1">

    <!-- =================================================================== 1. HERO (the Mumbai video) -->
    <section class="hero" data-hero aria-labelledby="hero-title">
      <div class="hero__media">
        <picture>
          <source type="image/avif" srcset="assets/video/hero-city-poster-720.avif 720w, assets/video/hero-city-poster-1280.avif 1280w, assets/video/hero-city-poster-1920.avif 1920w" sizes="(orientation: portrait) 80vh, 100vw">
          <source type="image/webp" srcset="assets/video/hero-city-poster-720.webp 720w, assets/video/hero-city-poster-1280.webp 1280w, assets/video/hero-city-poster-1920.webp 1920w" sizes="(orientation: portrait) 80vh, 100vw">
          <img src="assets/video/hero-city-poster-1280.jpg" srcset="assets/video/hero-city-poster-720.jpg 720w, assets/video/hero-city-poster-1280.jpg 1280w, assets/video/hero-city-poster-1920.jpg 1920w" sizes="(orientation: portrait) 80vh, 100vw" width="1920" height="1080" alt="The Mumbai skyline across the bay" fetchpriority="high" decoding="async">
        </picture>
        <!-- site.js adds the source after page load: 1080p on large screens, 720p otherwise -->
        <video class="hero__video" data-base="assets/video/hero-city-" muted loop playsinline preload="none" aria-hidden="true" tabindex="-1"></video>
      </div>
      <div class="hero__content">
        <div class="hero__text">
          <!-- Technology USP: SITE["usp_line"] in tools/pages.py (from what Arha's own photos show) -->
          <p class="hero__eyebrow" data-show="usp">In-house X-ray · Own sterilisation room · Prosthodontist-led</p>
          <h1 id="hero-title">Specialist dentistry <br class="br-wide">on Peddar Road</h1>
          <p class="hero__lede">Your smile, designed around your face, your comfort and the way you live.</p>
          <p class="hero__actions">
            <a class="link link--light" href="book/">Book a consultation</a>
            <a class="link link--light" href="tel:+910000000000" data-call="hero" data-call-pop>Call now</a>
          </p>
        </div>
      </div>
    </section>

{problems.brings_you_in()}

    <!-- =================================================================== 2. GOOGLE REVIEWS -->
    <section class="section reviews-hl" aria-labelledby="reviews-title">
      <div class="container">
        <div class="section-head reveal">
          <p class="eyebrow">What patients say</p>
          <!-- Rating and count from SITE (tools/pages.py), checked on Google on 29 Oct 2026 -->
          <h2 id="reviews-title" class="reviews-hl__score"><span data-show="google-rating">5.0</span> · <span data-show="google-count-label">31 Google reviews</span></h2>
        </div>
{carousel(REVIEWS)}
        <p class="section-cta"><a class="link" href="#" data-google-reviews>Read all reviews on Google</a></p>
      </div>
    </section>

    <!-- =================================================================== 3. FEATURE TRIO (expanding panels) -->
    <section class="section section--flush trio" aria-labelledby="trio-title">
      <div class="container section-head reveal">
        <h2 id="trio-title">Crafted with precision. Given with care.</h2>
        <p class="lede">Specialist restorative and cosmetic dentistry, led by a prosthodontist and built on a family practice that began in 1980.</p>
      </div>
{xpanels()}
    </section>

    <!-- =================================================================== 4. TECHNOLOGY (Arha's own treatment room, hotspots) -->
    <section class="section section--flush tech-hl" aria-labelledby="tech-title">
      <div class="container section-head reveal">
        <p class="eyebrow">Technology &amp; innovation</p>
        <h2 id="tech-title">Equipped in-house</h2>
        <p class="lede">Three things you will find in Arha’s own rooms. Tap a number to see what it is, and what it means for you.</p>
      </div>
{hotspots()}
      <p class="section-cta container"><a class="link" href="technology/">Explore technology &amp; innovation{ARROW}</a></p>
    </section>

    <!-- =================================================================== 5. RESULTS (sliders) -->
    <section class="section results-hl" aria-labelledby="results-title">
      <div class="container-wide">
        <div class="section-head reveal">
          <h2 id="results-title">Results that look like you</h2>
          <p class="lede">Careful, natural improvements that keep your smile in balance with your face. Drag across the photograph to compare a simulated shade.</p>
        </div>
{results_home(cases)}
        <p class="section-cta"><a class="link" href="our-work/">See all our work{ARROW}</a></p>
      </div>
    </section>

    <!-- =================================================================== 7. THE JOURNEY (sticky story) -->
    <section class="section section--flush journey-hl" aria-labelledby="journey-title">
      <div class="container section-head reveal">
        <h2 id="journey-title">Your journey at Arha</h2>
      </div>
{story(JOURNEY)}
    </section>

    <!-- =================================================================== 8. DR. NIKHIL'S QUOTE -->
    <section class="quote-band" aria-labelledby="quote-title">
{picture('stock-dentist-hands', '100vw', '', pos='30% 50%', indent='      ')}
      <div class="container quote-band__content reveal">
        <h2 id="quote-title" class="eyebrow eyebrow--light">From the founder</h2>
        <blockquote class="pull-quote pull-quote--light">
          <p>“A good restoration should never announce itself. My aim is a result that feels natural, functions beautifully and lasts.”</p>
          <footer>Dr. Nikhil V. Jain · MDS Prosthodontist · ITI Scholar</footer>
        </blockquote>
        <a class="link link--light" href="founder/">About the founder{ARROW}</a>
      </div>
    </section>

    <!-- =================================================================== 9. STEP INSIDE (clinic tour + 360) -->
    <section class="inside" aria-labelledby="inside-title">
{picture('arha-dental-care-reception-south-mumbai-dental-clinic-01-lower', '100vw', '', pos='35% 70%', indent='      ')}
      <div class="container inside__grid">
        <div class="inside__text reveal">
          <h2 id="inside-title">Step inside</h2>
          <p>Marble, soft light and quiet rooms on Peddar Road. Walk through the clinic in a short film, or look around every room.</p>
          <p class="inside__links"><a class="link link--light" href="gallery/#tour">Take the 360° tour{ARROW}</a> <a class="link link--light" href="gallery/">See the gallery</a></p>
        </div>
{tour_figure()}
      </div>
    </section>

    <!-- =================================================================== VISITING MUMBAI -->
    <section class="statement statement--travel" aria-labelledby="travel-title">
{picture('stock-marine-drive', '100vw', 'Marine Drive and the South Mumbai skyline across the bay', pos='50% 50%', indent='      ')}
      <div class="container statement__content reveal">
        <h2 id="travel-title">Visiting Mumbai for treatment?</h2>
        <p>Many of our patients live abroad. Start with a virtual consultation, and we will plan your treatment and timeline before you arrive.</p>
        <a class="link link--light" href="dental-tourism/">Plan your treatment{ARROW}</a>
      </div>
    </section>

{visit}
  </main>
"""
