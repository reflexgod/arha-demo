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
from picture import picture

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
    return """    <!-- =================================================================== 1. HERO (apa: video, text bottom-left, one CTA) -->
    <section class="hero ah-hero" data-hero aria-labelledby="hero-title">
      <div class="hero__media">
        <!-- The poster: the loop's first frame (an upright cut for phones held upright). It stays if the video
             cannot play (reduced motion, data saver, autoplay blocked). -->
        <picture>
          <source media="(orientation: portrait)" type="image/avif" srcset="assets/video/hero-city-poster-port-540.avif 540w, assets/video/hero-city-poster-port-810.avif 810w" sizes="100vw">
          <source media="(orientation: portrait)" type="image/webp" srcset="assets/video/hero-city-poster-port-540.webp 540w, assets/video/hero-city-poster-port-810.webp 810w" sizes="100vw">
          <source media="(orientation: portrait)" srcset="assets/video/hero-city-poster-port-540.jpg 540w, assets/video/hero-city-poster-port-810.jpg 810w" sizes="100vw">
          <source type="image/avif" srcset="assets/video/hero-city-poster-720.avif 720w, assets/video/hero-city-poster-1280.avif 1280w, assets/video/hero-city-poster-1920.avif 1920w" sizes="100vw">
          <source type="image/webp" srcset="assets/video/hero-city-poster-720.webp 720w, assets/video/hero-city-poster-1280.webp 1280w, assets/video/hero-city-poster-1920.webp 1920w" sizes="100vw">
          <img src="assets/video/hero-city-poster-1280.jpg" srcset="assets/video/hero-city-poster-720.jpg 720w, assets/video/hero-city-poster-1280.jpg 1280w, assets/video/hero-city-poster-1920.jpg 1920w" sizes="100vw" width="1920" height="1080" alt="The Mumbai skyline across the bay" fetchpriority="high" decoding="async">
        </picture>
        <!-- site.js adds the source after page load: an upright cut on phones held upright, else 1080p or 720p -->
        <video class="hero__video" data-base="assets/video/hero-city-" muted loop playsinline preload="none" aria-hidden="true" tabindex="-1"></video>
      </div>
      <div class="hero__content">
        <div class="hero__text">
          <h1 id="hero-title">Specialist dentistry on Peddar Road</h1>
          <p class="hero__lede">Your smile, designed around your face, your comfort and the way you live.</p>
          <p class="hero__actions"><a class="link link--light" href="book/">Book an appointment</a></p>
        </div>
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
    return """
    <!-- =================================================================== 6. DARK BAND (apa: centred statement, one CTA) -->
    <section class="ah-dark" aria-labelledby="dark-title">
      <div class="reveal">
        <h2 id="dark-title">Dentistry, done carefully</h2>
        <p>Arha is led by a prosthodontist, a specialist in restoring and replacing teeth. Every plan starts with listening and a careful examination, and is explained clearly before anything begins.</p>
        <a class="link link--light" href="book/">Book an appointment</a>
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


def founder():
    return f"""
    <!-- =================================================================== 8. FOUNDER QUOTE (apa: full-bleed photo, centred text on the left half) -->
    <section class="ah-founder" aria-labelledby="founder-title">
{pic('stock-dentist-hands', '100vw', '', '70% 50%', '      ')}
      <div class="ah-founder__text reveal">
        <h2 id="founder-title">Our philosophy</h2>
        <!-- Clinic philosophy, not a quote: no source for these words in the notes (notes/TO-CONFIRM.md) -->
        <p class="ah-founder__line">A good restoration should never announce itself. The aim is a result that feels natural, works well and lasts.</p>
        <a class="link link--light" href="doctors/">Meet our doctors</a>
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
          <h3 id="teaser-title">Step inside Arha</h3>
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
             "chipped": "55% 35%", "child": "50% 55%"}
# Face-free photographs for the cards whose own finder photograph showed a person's face (a stranger's face reads
# as a patient of the clinic). The others keep their stock-finder-<name> photograph.
FINDER_PHOTOS = {"pain": "stock-xray-screen", "stained": "stock-teeth-shades", "child": "stock-kids-brushes"}


def finder_photo(name, sizes, i):
    return pic(FINDER_PHOTOS.get(name, f"stock-finder-{name}"), sizes, "", PHOTO_POS[name], i)


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
                    for rid, label, ic, *_ in FINDER)
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
            <p class="finder__actions"><a class="finder__book" href="book/">Book an appointment</a><!--if:phone--><a class="finder__call" href="tel:+910000000000" data-call="finder">Call the clinic</a><!--endif--></p>
            <p class="finder__confirm">General information, not a diagnosis. Dr. Nikhil will confirm at your visit.</p>
            <button class="finder__back finder__back--end" type="button" data-back>{BACK}</button>
          </div>
          <div class="finder__visual">
{finder_photo(ic, PANEL_SIZES, "            ")}
          </div>
        </div>"""
    return f"""
    <!-- =================================================================== WHAT BRINGS YOU IN? (treatment finder, site.js 23a) -->
    <section class="ah-finder" id="what-brings-you-in" aria-labelledby="finder-title">
      <div class="ah-finder__head reveal">
        <h2 id="finder-title">What brings you in?</h2>
        <p>Choose what sounds closest.</p>
      </div>
      <div class="finder" data-finder>
        <ul class="finder__grid" data-finder-grid data-reveal-group aria-label="Choose what sounds closest">{cards}
        </ul>{panels}
      </div>
      <p class="finder__all reveal"><a class="link" href="problems/">All the problems we treat</a></p>
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
    return ('  <main id="main" class="home-apa" tabindex="-1">\n\n' + hero() + finder() + trio() + band() + dark() + process() + founder()
            + teaser() + reviews() + "\n  </main>\n")
