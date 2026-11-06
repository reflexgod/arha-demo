"""The homepage <main> on apaaesthetic.com's homepage layout, section by section (notes/V4-APA-LITERAL.md;
apa measured in notes/APA-HOMEPAGE.md). Only the content is Arha's. Twelve blocks, in apa's order:

  1 hero (video, text bottom-left, one CTA)   2 trio heading      3 feature trio (2:1 images, linked H3)
  4 interior band (slideshow, About Arha)     5 problems grid (3x3 problem|fix squares, See all treatments)
  6 dark band (one CTA)                       7 process (three photo panels, numbered text overlaid)
  8 founder quote (Meet our doctors)          9 step inside (tour video | colour panel, 360 tour)
  10 reviews heading                          11 reviews mosaic (two staggered columns)   12 footer (chrome.py)

Interactions are apa's only: link underlines, the band's slow crossfade (site.js 22), the grid tiles
(black and white until hovered, then colour and "See how we treat it" fade in, 0.4 s) and the mosaic tiles'
hover overlay. CSS: the "apa homepage" layer at the end of site.css.
"""
import html

import home
import problems
from picture import SIG, picture

ARROW = home.ARROW

TRIO = [  # apa: three 2:1 images edge to edge, a linked H3 and one line under each
    ("arha-dental-care-delivery-unit", "50% 45%", "The instrument holder at an Arha chair, with its handpieces ready",
     "Specialist care", "Dr. Nikhil V. Jain is a prosthodontist and implantologist: implants, full mouth rehabilitation and smile design.", "doctors/"),
    ("dental-implant-equipment-arha-dental-care-mumbai", "50% 22%", "Arha's X-ray room: a panoramic X-ray unit against a marble wall",
     "Technology &amp; innovation", "An X-ray room and a sterilisation room of our own, and 3D models of your teeth on screen.", "technology/"),
    ("arha-dental-care-exterior-dental-clinic-peddar-road", "50% 45%", "The Arha sign at suite 107 with the names of Dr. Nikhil V. Jain and Dr. Vasant P. Jain",
     "Dr. Nikhil’s clinic", "Arha Dental Care is Dr. Nikhil V. Jain’s practice at 107, Doctor House, 14 Peddar Road.", "founder/"),
]

BAND = [("arha-dental-care-reception-south-mumbai-dental-clinic-01-lower", "50% 60%", "Arha's reception on Peddar Road: marble, soft light and the gold emblem"),
        ("dental-operatory-arha-dental-care-peddar-road-01", "50% 55%", "An Arha treatment room with its chair beneath a soft light")]

# The nine problems on the homepage grid (apa's grid has nine squares; all ten are on /problems/ and in the menu).
# One photograph per square, showing the problem only (Viraaj, 2 Nov 2026): (slug, photo, position, alt).
GRID = [
    ("missing-tooth", "stock-implant-model", "50% 55%", "A model of an implant crown on its post between two natural teeth"),
    ("chipped-tooth", "stock-patient-chair", "60% 40%", "A dentist examining a patient's front teeth with a mirror"),
    ("gaps", "stock-crooked", "50% 55%", "A smile with a small gap between the front teeth"),
    ("crooked-teeth", "stock-aligner-gloved", "50% 45%", "A clear aligner held between gloved fingers"),
    ("stained-teeth", "stock-stained", "50% 50%", "A smile with yellowed teeth"),
    ("toothache", "stock-toothache-lower", "50% 50%", "A hand held against a sore cheek, the lower face only"),
    ("bleeding-gums", "stock-exam", "40% 45%", "A gentle gum check with a mirror and probe"),
    ("loose-dentures", "stock-denture-tray", "50% 55%", "A full denture on its clean white base"),
    ("child-teeth", "stock-child-chair", "50% 45%", "A smiling girl in the dental chair beside her dentist"),
]

PROCESS = [  # apa: three photo panels, the numbered heading and two lines overlaid bottom-left
    ("arha-dental-care-consultation-desk", "50% 50%", "The consultation desk in an Arha treatment room", "1. Consultation",
     "We listen first, then examine carefully and explain your options clearly, so you can decide calmly."),
    ("arha-dental-care-chair-window", "50% 55%", "The dental chair under its light in an Arha treatment room", "2. Your treatment",
     "Planned in detail and carried out with precision, at a pace that keeps you comfortable."),
    ("arha-dental-care-reception-wide", "50% 50%", "Arha's reception and waiting area", "3. Lifelong care",
     "Reviews and cleanings that protect your result for years, with the doctors who planned it, on Peddar Road."),
]

# Review tiles in apa's mosaic: two columns of tall (3:4) and wide (3:2) tiles, columns of equal height.
# (review index or "photo", shape, tone). Tones alternate so the mosaic reads like apa's covers: charcoal,
# stone and paper with a hairline; the one photograph (Arha's logo wall, 3:2) shows the rating on hover, as apa's covers do.
MOSAIC = [  # indices into home.TESTIMONIALS: reviews 1, 2, 3 and 7 (Viraaj, 2 Nov 2026)
    [(1, "tall", "dark"), (0, "wide", "stone")],
    [(2, "wide", "line"), ("photo", "wide", None), (6, "wide", "stone")],
]
STAR = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 1.5l2.6 5.6 6.1.7-4.5 4.2 1.2 6-5.4-3-5.4 3 1.2-6-4.5-4.2 6.1-.7z"/></svg>'


def pic(name, sizes, alt, pos, i, eager=False):
    return picture(name, sizes, alt, pos=pos, eager=eager, indent=i)


def hero():
    """v8: split hero on paper. Left, the reception photograph in colour (the one photograph the black and white rule
    leaves alone), edge to edge, with a slow 8 s zoom (none with reduced motion). Right, the eyebrow, H1, line and two
    buttons. Phones: the photograph on top, the words below. The skyline video files stay in assets/video, unused."""
    return f"""    <!-- =================================================================== 1. HERO (v8: reception photograph | words) -->
    <section class="hero-split" aria-labelledby="hero-title">
      <div class="hero-split__media">
{pic('arha-dental-care-reception-south-mumbai-dental-clinic-01', '(min-width: 900px) 50vw, 100vw', "Arha's reception on Peddar Road: marble, soft light and the gold emblem", '50% 50%', '        ', eager=True)}
      </div>
      <div class="hero-split__text">
        <p class="eyebrow">Peddar Road, Mumbai</p>
        <h1 id="hero-title">Specialist dentistry on Peddar Road</h1>
        <p class="hero-split__lede">Your smile, designed around your face, your comfort and the way you live.</p>
        <p class="hero-split__actions"><a class="btn" href="book/"><span>Book an appointment</span>{ARROW}</a><a class="btn" href="book/#first-visit"><span>Your first visit</span>{ARROW}</a></p>
      </div>
    </section>
"""


def trio():
    cols = "".join(f"""
        <article class="ah-trio__item reveal">
          <a class="ah-trio__media" href="{href}" tabindex="-1" aria-hidden="true">
{pic(name, '(min-width: 900px) 34vw, 100vw', alt, pos, '            ')}
          </a>
          <h3><a href="{href}">{title}</a></h3>
          <p>{line}</p>
        </article>""" for name, pos, alt, title, line, href in TRIO)
    return f"""
    <!-- =================================================================== 2. TRIO HEADING + 3. FEATURE TRIO -->
    <section class="ah-head reveal" aria-labelledby="trio-title">
      <p class="eyebrow">Why Arha</p>
      <h2 id="trio-title"><a href="the-practice/">Crafted with precision. Given with care.</a></h2>
      <p>Specialist restorative and cosmetic dentistry with natural results, led by prosthodontist Dr. Nikhil V. Jain on Peddar Road.</p>
    </section>
    <section class="ah-trio" aria-label="Why Arha">{cols}
    </section>
"""


def band():
    slides = "".join(f"""
        <div class="ah-band__slide{' is-active' if n == 0 else ''}">
{pic(name, '100vw', alt if n == 0 else '', pos, '          ')}
        </div>""" for n, (name, pos, alt) in enumerate(BAND))
    return f"""
    <!-- =================================================================== 4. INTERIOR BAND (apa: slideshow, text bottom-left) -->
    <section class="ah-band" data-slideshow aria-labelledby="band-title">
      <div class="ah-band__slides">{slides}
      </div>
      <div class="ah-band__text reveal">
        <p class="eyebrow eyebrow--light">The practice</p>
        <h2 id="band-title">A clinic built around calm</h2>
        <p>Marble, soft light and quiet rooms at Doctor House on Peddar Road. An X-ray room and a sterilisation room of our own, and Dr. Nikhil V. Jain and Dr. Vasant P. Jain under one roof.</p>
        <a class="link link--light" href="founder/">About Arha</a>
      </div>
    </section>
"""


def how(p):
    """One line on how the problem is usually treated, from its page's three options: "An implant, a bridge or a denture." """
    names = [f[1] for f in p["fix"]]
    low = [n[0].lower() + n[1:] for n in names[1:]]
    return f"{names[0]}, {low[0]} or {low[1]}."


def grid():
    tiles = ""
    for slug, name, pos, alt in GRID:
        p = problems.PROBLEMS[slug]
        tiles += f"""
        <li class="ah-tile reveal">
          <a href="problems/{slug}/" data-colour-group>
            <span class="ah-tile__pair">
              <span class="ah-tile__half">
{pic(name, '(min-width: 900px) 330px, 300px', alt, pos, '                ')}
              </span>
            </span>
            <span class="ah-tile__hover"><span class="ah-tile__name">{p['menu']}</span><span class="ah-tile__how">{how(p)}</span><span class="ah-tile__link">See how we treat it</span></span>
          </a>
        </li>"""
    return f"""
    <!-- =================================================================== 5. COMMON PROBLEMS WE TREAT (apa: the grid of squares) -->
    <section class="ah-grid" aria-labelledby="grid-title">
      <h2 id="grid-title" class="reveal"><a href="problems/">Common problems we treat</a></h2>
      <p class="ah-grid__lede reveal">The concerns patients most often come to us with. Choose one to see how we treat it.</p>
      <ul class="ah-grid__tiles">{tiles}
      </ul>
      <p class="ah-grid__cta reveal"><a class="link" href="treatments/">See all treatments</a></p>
    </section>
"""


def dark():
    return f"""
    <!-- =================================================================== 6. DARK BAND (v8: on paper, centred statement, one CTA) -->
    <section class="ah-dark" aria-labelledby="dark-title">
      <div class="reveal">
        <p class="eyebrow">Specialist care</p>
        <h2 id="dark-title">Dentistry, done carefully</h2>
        <p>Arha is led by a prosthodontist, a specialist in restoring and replacing teeth. Every plan starts with listening and a careful examination, and is explained clearly before anything begins.</p>
        <a class="link" href="book/">Book an appointment</a>
      </div>
    </section>
"""


def process():
    panels = "".join(f"""
      <article class="ah-process__panel">
{pic(name, '(min-width: 900px) 34vw, 100vw', alt, pos, '        ')}
        <div class="ah-process__text reveal">
          <h3>{title}</h3>
          <p>{line}</p>
        </div>
      </article>""" for name, pos, alt, title, line in PROCESS)
    return f"""
    <!-- =================================================================== 7. PROCESS (apa: three photo panels, numbered text overlaid) -->
    <section class="ah-process" aria-label="Your journey at Arha">{panels}
    </section>
"""


def statement():
    """v8: the clinic philosophy as a large serif pull quote on deep brown (the words were the founder band's line)."""
    return f"""
    <!-- =================================================================== STATEMENT (v8: deep brown, the philosophy as a pull quote) -->
    <section class="ah-statement" aria-labelledby="statement-title">
      <div class="ah-statement__inner reveal">
        <p class="eyebrow eyebrow--light">The Arha approach</p>
        <h2 id="statement-title" class="visually-hidden">Our philosophy</h2>
        <!-- Clinic philosophy, not a quote: no source for these words in the notes (notes/TO-CONFIRM.md) -->
        <blockquote class="ah-statement__quote"><p>A good restoration should never announce itself.</p></blockquote>
        <span class="ah-statement__rule" aria-hidden="true"></span>
        <p class="ah-statement__line">The aim is a result that feels natural, works well and lasts.</p>
        <a class="link link--light" href="doctors/">Meet our doctors</a>
      </div>
    </section>
"""


# Two treatments, each a full-bleed photograph with its serif name over it and a light card under it with the line from
# its own page (the page hero's line). (slug, name, photo, position, alt, line)
TREATMENT_ROWS = [  # every treatment page: its own title, a line from its own intro, its own hero photograph
    ("dental-implants", "Dental implants", "Replacing missing teeth, made to feel your own.", "stock-implant-hero", "30% 50%"),
    ("smile-design", "Smile design", "A new smile, previewed before work begins.", "dental-operatory-arha-dental-care-peddar-road-04", "50% 50%"),
    ("invisalign", "Invisalign clear aligners", "Straightening teeth with clear, removable aligners.", "stock-aligner-case-hand", "50% 50%"),
    ("full-mouth-rehabilitation", "Full mouth rehabilitation", "Rebuilding worn or broken teeth, and the bite.", "stock-crowns", "50% 55%"),
    ("maxillofacial-prosthetics", "Maxillofacial prosthetics", "Restoring eating, speaking and appearance.", "stock-prosthesis-hands", "50% 45%"),
    ("cosmetic-dentistry", "Cosmetic dentistry", "Veneers, whitening and bonding.", "stock-crowns-soft", "50% 55%"),
    ("crowns-bridges", "Crowns &amp; bridges", "Restoring broken teeth and replacing missing ones.", "stock-gloved-hands", "60% 40%"),
    ("root-canal-treatment", "Root canal treatment", "Saving a tooth whose nerve is infected.", "stock-mirror-tray", "50% 50%"),
    ("orthodontics", "Orthodontics (braces)", "Braces and aligners for children, teens and adults.", "stock-braces-model", "50% 55%"),
    ("general-dentistry", "General dentistry &amp; cleaning", "Check-ups, cleaning and fillings.", "dental-operatory-arha-dental-care-peddar-road-02", "50% 55%"),
    ("kids-dentistry", "Kids’ dentistry", "Gentle care for babies, children and teens.", "stock-parent-child", "50% 40%"),
]


def highlights():
    """Explore treatments (7 Nov 2026), after the demo clinic's index: laptops, big serif names on the left, one line
    each on the right and the row's photograph in the centre, crossfading as a row is hovered or focused (site.js 28);
    phones and tablets, a plain list with a small photograph beside each row. Only the first photograph loads at once."""
    rows = "".join(f"""
        <li><a class="tx__row" href="{slug}/" data-tx-row="{n}">
          <span class="tx__thumb">
{pic(photo, '64px', '', pos, '            ')}
          </span>
          <span class="tx__name">{name}</span>
          <span class="tx__line">{line}</span>
        </a></li>""" for n, (slug, name, line, photo, pos) in enumerate(TREATMENT_ROWS))
    previews = "".join(
        pic(photo, '(min-width: 1024px) 300px, 1px', '', pos, '        ', eager=(n == 0))
        .replace('<picture class="fill"', f'<picture class="fill tx__img{" is-active" if n == 0 else ""}"', 1)
        .replace(' fetchpriority="high"', '')
        for n, (slug, name, line, photo, pos) in enumerate(TREATMENT_ROWS))
    return f"""
    <!-- =================================================================== EXPLORE TREATMENTS (the demo clinic's hover list) -->
    <section class="ah-highlights tx" aria-labelledby="hl-title" data-tx>
      <div class="ah-highlights__head reveal">
        <h2 id="hl-title">Explore treatments</h2>
      </div>
      <div class="tx__wrap">
        <ul class="tx__list" role="list">{rows}
        </ul>
        <div class="tx__preview" aria-hidden="true">
{previews}
        </div>
      </div>
    </section>
"""


def teaser():
    return f"""
    <!-- =================================================================== 9. STEP INSIDE (apa: the video | a colour panel) -->
    <section class="ah-teaser" aria-labelledby="teaser-title">
      <div class="ah-teaser__video">
{home.tour_figure('', '        ', '(min-width: 900px) 50vw, 100vw').replace('class="tour reveal"', 'class="tour ah-teaser__tour"')}
      </div>
      <div class="ah-teaser__panel">
        <div class="reveal">
          <p class="eyebrow">Gallery</p>
          <h2 id="teaser-title">Step inside Arha</h2>
          <a class="link" href="gallery/">See the gallery</a>
        </div>
      </div>
    </section>
"""


# ------------------------------------------------------------------ What brings you in? (treatment finder, site.js 23a)
# Six cards, one tap to a short plain-English answer. Every answer comes from the site's own problem and treatment
# pages and ends "Dr. Nikhil will confirm at your visit." Nothing is stored or sent.
# Each card shows a free-licence Unsplash photograph (sources: notes/IMAGE-SOURCES.md; graded with photos.stock_grade
# like every stock photo), and the answer panel shows the same photograph larger. Decorative (alt=""): the label says it.
# By design, a card and its panel are one appearance of the photograph (tools/photo_audit.py).
PHOTO_POS = {"pain": "50% 50%", "gap": "45% 50%", "crooked": "42% 50%", "stained": "50% 50%",
             "chipped": "55% 35%", "child": "50% 24%"}
# Face-free photographs for the cards whose own finder photograph showed a person's face (a stranger's face reads
# as a patient of the clinic). The others keep their stock-finder-<name> photograph.
FINDER_PHOTOS = {"pain": "stock-xray-screen", "stained": "stock-teeth-shades", "child": "stock-kids-brushes"}


def finder_photo(name, sizes, i, eager=False):
    return pic(FINDER_PHOTOS.get(name, f"stock-finder-{name}"), sizes, "", PHOTO_POS[name], i, eager)


# card label, photo, panel heading, two or three short sentences, safety line (or ""), related pages
FINDER = [
    ("r-pain", "Tooth pain or swelling", "pain", "Finding the cause of the pain",
     "Pain when you bite, or with hot and cold, often comes from decay, a crack or an inflamed nerve. "
     "An examination and an X-ray show which. Severe pain or swelling should be seen soon.",
     "Go to a hospital first if swelling spreads towards your eye or neck, or if breathing or swallowing is hard.",
     [("emergency/", "Dental emergencies"), ("problems/toothache/", "Toothache, explained"),
      ("root-canal-treatment/", "Root canal treatment")]),
    ("r-gap", "A gap or a missing tooth", "gap", "Filling a gap",
     "A missing tooth can be replaced with an implant, a bridge or a denture. "
     "A space between teeth can be closed with bonding, veneers or aligners. "
     "Dr. Nikhil is a prosthodontist: replacing teeth is his speciality.",
     "", [("problems/missing-tooth/", "A missing tooth, explained"), ("problems/gaps/", "Gaps, explained"),
          ("dental-implants/", "Dental implants")]),
    ("r-crooked", "Crooked or crowded teeth", "crooked", "Straightening your teeth",
     "Teeth can be straightened at almost any age, with clear aligners or with braces. "
     "Straighter teeth are also easier to keep clean.",
     "", [("problems/crooked-teeth/", "Crooked teeth, explained"), ("invisalign/", "Clear aligners"),
          ("orthodontics/", "Braces")]),
    ("r-stained", "Stained or yellow teeth", "stained", "Brightening your smile",
     "Surface stains often lift with a professional clean. Deeper colour responds to whitening, "
     "and where whitening cannot help, bonding or veneers can.",
     "", [("problems/stained-teeth/", "Stained teeth, explained"), ("cosmetic-dentistry/", "Cosmetic dentistry")]),
    ("r-chipped", "A chipped or broken tooth", "chipped", "Repairing a chipped tooth",
     "A small chip can often be rebuilt in tooth-coloured bonding. A larger break may need a crown, "
     "a cap that protects the tooth. If it hurts, it should be seen soon.",
     "", [("problems/chipped-tooth/", "A chipped tooth, explained"), ("crowns-bridges/", "Crowns &amp; bridges")]),
    ("r-child", "A check-up for my child", "child", "Your child’s check-up",
     "Gentle check-ups help children get used to the dentist. "
     "An early check also spots bite or crowding problems while the jaws are still growing.",
     "", [("kids-dentistry/", "Kids’ dentistry"), ("problems/child-teeth/", "Children’s teeth, explained")]),
]
CARD_SIZES = "(max-width: 767px) 76vw, 347px"
PANEL_SIZES = "(max-width: 767px) 90vw, 460px"
BACK = '<span aria-hidden="true">←</span> Go back'


def finder():
    cards = "".join(f"""
          <li class="reveal"><button class="finder__card" type="button" data-go="{rid}" data-colour-group><span class="finder__media">
{finder_photo(ic, CARD_SIZES, "              ")}
            </span><span class="finder__label">{label}<span class="finder__arrow" aria-hidden="true">→</span></span></button></li>"""
                    for n, (rid, label, ic, *_) in enumerate(FINDER))
    panels = ""
    for rid, _label, ic, title, text, urgent, links in FINDER:
        urgent_html = f'\n            <p class="finder__urgent">{urgent}</p>' if urgent else ""
        link_html = "".join(f'<li><a href="{h}">{n}</a></li>' for h, n in links)
        panels += f"""
        <div class="finder__panel" id="{rid}" data-panel hidden>
          <div class="finder__text">
            <button class="finder__back finder__back--top" type="button" data-back>{BACK}</button>
            <p class="finder__eyebrow">What it usually means</p>
            <h3 tabindex="-1">{title}</h3>
            <p>{text}</p>{urgent_html}
            <ul class="finder__links">{link_html}</ul>
            <p class="finder__actions"><a class="link" href="book/">Book an appointment</a><!--if:phone--><a class="link" href="tel:+910000000000" data-call="finder">Call the clinic</a><!--endif--></p>
            <p class="finder__confirm">General information, not a diagnosis. Dr. Nikhil will confirm at your visit.</p>
            <button class="finder__back finder__back--end" type="button" data-back>{BACK}</button>
          </div>
          <div class="finder__visual">
{finder_photo(ic, PANEL_SIZES, "            ")}
          </div>
        </div>"""
    from home import ARROW
    return f"""
    <!-- =================================================================== WHAT BRINGS YOU IN? (treatment finder, site.js 23a) -->
    <section class="ah-finder" id="what-brings-you-in" aria-labelledby="finder-title">
      <div class="ah-finder__head reveal">
        <p class="eyebrow">What we treat</p>
        <h2 id="finder-title">What brings you in?</h2>
        <p>Choose what sounds closest.</p>
      </div>
      <div class="finder" data-finder>
        <ul class="finder__grid" data-finder-grid data-reveal-group aria-label="Choose what sounds closest">{cards}
        </ul>{panels}
      </div>
      <div class="finder__all finder__else reveal">
        <div>
          <h3>Something else, or not sure?</h3>
          <p>Tell us what's bothering you and we'll guide you to the right care.</p>
        </div>
        <div class="finder__else-actions"><!--if:phone--><a class="btn btn--solid" href="tel:+910000000000" data-call="finder_else"><span>Call <span data-show="phone">+91 00000 00000</span></span>{ARROW}</a><!--endif--><a class="btn" href="book/"><span>Book an appointment</span>{ARROW}</a></div>
        <a class="link" href="problems/">All the problems we treat</a>
      </div>
    </section>
"""


# ------------------------------------------------------------------ reviews: the four tiles, now a calm carousel
REVIEW_TILES = [(1, "dark"), (0, "stone"), (2, "line"), (6, "stone")]  # reviews 2, 1, 3 and 7 (Viraaj, 2 Nov 2026)
CHEV = {"prev": '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M12.5 4 6.5 10l6 6"/></svg>',
        "next": '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="m7.5 4 6 6-6 6"/></svg>',
        "pause": '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M7 4v12M13 4v12"/></svg>',
        "play": '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M6 4l10 6-10 6z"/></svg>'}


def reviews():
    """The same review tiles as before (text, names, stars and "Google review" unchanged), one or two at a time:
    advances every 7 s while on screen, pauses on hover, focus or touch and with the Pause button; never moves on
    its own with reduced motion. site.js 23."""
    n = len(REVIEW_TILES)
    slides = ""
    for k, (idx, tone) in enumerate(REVIEW_TILES):
        t = home.TESTIMONIALS[idx]
        slides += f"""
          <div class="ah-review ah-review--wide ah-review--{tone} rv__slide" role="group" aria-roledescription="slide" aria-label="{k + 1} of {n}" data-slide>
            <a href="#" data-google-reviews>
              <span class="ah-review__mark" aria-hidden="true">“</span>
              <blockquote><p>{html.escape(t[3], quote=False)}</p></blockquote>
              <span class="ah-review__name">{home.reviewer(t)}</span>
              <span class="ah-review__foot">{home.stars(t[2], "ah-review__stars")}<span class="ah-review__source">Google review</span></span>
              <span class="ah-review__hover"><span>{home.reviewer(t)}</span><span>Read on Google</span></span>
            </a>
          </div>"""
    dots = "".join(f'<li><button class="rv__dot" type="button" aria-label="Show review {k + 1}" data-dot="{k}"></button></li>' for k in range(n))
    return f"""
    <!--flag:reviews--><!-- =================================================================== 10. REVIEWS HEADING + 11. CAROUSEL (SITE["showReviews"]) -->
    <section class="ah-head ah-head--reviews reveal" aria-labelledby="reviews-title">
      <!-- No rating or review count anywhere on the site (Viraaj, 2 Nov 2026) -->
      <h2 id="reviews-title">What patients say on Google</h2>
      <p>In patients’ own words, quoted as they wrote them on Google. Where a review is longer, it ends with “…”: read it in full on Google.</p>
      <a class="link" href="#" data-google-reviews>Read all reviews on Google</a>
    </section>
    <section class="ah-carousel" aria-label="Google reviews">
      <div class="rv reveal" data-reviews aria-roledescription="carousel" aria-labelledby="reviews-title">
        <div class="rv__track" data-track>{slides}
        </div>
        <div class="rv__controls">
          <ul class="rv__dots">{dots}</ul>
          <div class="rv__buttons">
            <button class="rv__btn" type="button" data-pause aria-label="Pause the reviews"><span class="rv__icon-pause">{CHEV['pause']}</span><span class="rv__icon-play">{CHEV['play']}</span></button>
            <button class="rv__btn" type="button" data-prev aria-label="Previous review">{CHEV['prev']}</button>
            <button class="rv__btn" type="button" data-next aria-label="Next review">{CHEV['next']}</button>
          </div>
        </div>
      </div>
    </section><!--/flag:reviews-->
"""


def main_html(visit=None):
    """The homepage <main>. The footer (apa's closing line, logo and columns) comes from chrome.py.
    One problem picker only, "What brings you in?": the grid of problem squares (grid()) repeated it, and all ten
    problems are one tap away on /problems/ (Demo-ready, 3 Nov 2026)."""
    return ('  <main id="main" class="home-apa" tabindex="-1">\n\n' + hero_v9() + finder() + statement() + trio()
            + "    " + SIG + "\n" + highlights() + band() + dark() + process() + "    " + SIG + "\n" + step_inside() + reviews() + "\n  </main>\n")


# ------------------------------------------------------------------ 7 Nov 2026 (v5-clean): the clinic walkthrough hero and
# "Step inside", kept from the v9 upgrade and restyled in the v8 palette and type (site.css, last layer).
def hero_v9():
    """Full-bleed clinic walkthrough, text bottom-left over a dark gradient. The poster paints first (preloaded in
    index.html); site.js 27 attaches the video after the load event, on screens 1024 px and wider only."""
    from chrome import WA
    return f"""    <!-- =================================================================== 1. HERO (the clinic walkthrough, text bottom-left) -->
    <section class="hero-v9" data-hero-v9 aria-labelledby="hero-title">
      <div class="hero-v9__media">
        <picture>
          <source media="(max-width: 1023px) and (orientation: portrait)" type="image/webp" srcset="assets/video/hero-poster-port-720.webp">
          <source type="image/webp" srcset="assets/video/hero-poster-land-768.webp 768w, assets/video/hero-poster-land-1280.webp 1280w, assets/video/hero-poster-land-1920.webp 1920w" sizes="100vw">
          <img src="assets/video/hero-poster-land-1280.jpg" width="1920" height="1080" alt="Arha's reception on Peddar Road, the first frame of the clinic walkthrough" fetchpriority="high">
        </picture>
        <video class="hero-v9__video" data-base="assets/video/hero-land-" muted loop playsinline preload="none" aria-hidden="true" tabindex="-1"></video>
      </div>
      <div class="hero-v9__text">
        <p class="hero-v9__kicker">Peddar Road, Mumbai</p>
        <h1 id="hero-title">Implants and smile design by a <em class="accent">prosthodontist</em>.</h1>
        <p class="hero-v9__lede">Dr. Nikhil V. Jain’s practice on Peddar Road, opposite Jaslok Hospital.</p>
        <p class="hero-v9__actions"><a class="btn btn--primary" href="book/"><span>Book an appointment</span>{ARROW}</a><!--if:whatsapp--><a class="btn" href="{WA}" target="_blank" rel="noopener"><span>WhatsApp</span>{ARROW}</a><!--endif--><!--if:phone--><a class="btn" href="tel:+910000000000" data-call="hero"><span>Call <span data-show="phone">+91 00000 00000</span></span>{ARROW}</a><!--endif--></p>
      </div>
    </section>
"""


INSIDE = [  # real clinic photographs only
    ("arha-dental-care-reception-south-mumbai-dental-clinic-01", "Arha's reception: marble, soft light and the gold emblem", "Reception"),
    ("arha-dental-care-lounge-peddar-road", "The patients' lounge at Arha", "The lounge"),
    ("dental-operatory-arha-dental-care-peddar-road-01", "An Arha treatment room with its chair beneath a soft light", "A treatment room"),
    ("arha-dental-care-consultation-desk", "The consultation desk in an Arha treatment room", "Consultation"),
    ("dental-implant-equipment-arha-dental-care-mumbai", "Arha's X-ray room with its panoramic X-ray unit", "The X-ray room"),
    ("arha-dental-care-exterior-dental-clinic-peddar-road", "The Arha sign at suite 107, Doctor House", "Suite 107, Doctor House"),
]


def step_inside():
    """Where the v8 teaser was: a swipe strip of the real rooms, and the clinic tour in a lightbox (site.js 25)."""
    items = "".join(f"""
        <li class="inside-strip__item">
          <figure>
            <div class="inside-strip__media">
{pic(name, '(min-width: 900px) 30vw, 78vw', alt, '50% 50%', '              ')}
            </div>
            <figcaption>{cap}</figcaption>
          </figure>
        </li>""" for name, alt, cap in INSIDE)
    return f"""
    <!-- =================================================================== 9. STEP INSIDE (the real rooms; the tour in a lightbox) -->
    <section class="inside-v9" aria-labelledby="inside-title">
      <div class="inside-v9__head reveal">
        <div>
          <p class="eyebrow">Gallery</p>
          <h2 id="inside-title">Step inside</h2>
        </div>
        <button class="btn" type="button" data-tour-open><span>Play the clinic tour</span>{ARROW}</button>
      </div>
      <ul class="inside-strip" role="list" tabindex="0" aria-label="Photographs of the clinic, scroll sideways">{items}
      </ul>
      <dialog class="tour-box" data-tour-box aria-label="Clinic tour">
        <button class="tour-box__close" type="button" data-tour-close aria-label="Close the clinic tour"></button>
        <video controls playsinline preload="none" data-poster="assets/video/tour-poster-720.jpg" data-src="assets/video/tour-720.mp4"></video>
      </dialog>
    </section>
"""
