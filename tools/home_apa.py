"""The homepage <main> on apaaesthetic.com's homepage layout, section by section (notes/V4-APA-LITERAL.md;
apa measured in notes/APA-HOMEPAGE.md). Only the content is Arha's. Twelve blocks, in apa's order:

  1 hero (video, text bottom-left, one CTA)   2 trio heading      3 feature trio (2:1 images, linked H3)
  4 interior band (slideshow, About Arha)     5 problems grid (3x3 problem|fix squares, See all treatments)
  6 dark band (one CTA)                       7 process (three photo panels, numbered text overlaid)
  8 founder quote (Meet our doctors)          9 step inside (tour video | colour panel, 360 tour)
  10 reviews heading                          11 reviews mosaic (two staggered columns)   12 footer (chrome.py)

Interactions are apa's only: link underlines, the band's slow crossfade (site.js 22), the grid tiles
(black and white until hovered, then colour and "See how we fix it" fade in, 0.4 s) and the mosaic tiles'
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
    ("arha-dental-care-exterior-dental-clinic-peddar-road", "50% 45%", "The Arha sign at suite 107 with the names of Dr. Vasant P. Jain and Dr. Nikhil V. Jain",
     "Legacy since 1980", "A family practice begun by Dr. Vasant P. Jain in 1980, now two generations on Peddar Road.", "founder/"),
]

BAND = [("arha-dental-care-reception-south-mumbai-dental-clinic-01-lower", "50% 60%", "Arha's reception on Peddar Road: marble, soft light and the gold emblem"),
        ("dental-operatory-arha-dental-care-peddar-road-01", "50% 55%", "An Arha treatment room with its chair beneath a soft light")]

# The nine problems on the homepage grid (apa's grid has nine squares; all ten are on /problems/ and in the menu).
# Each square is a problem | fix pair, stacked like apa's smile pairs: (photo, position, alt) above, then below.
GRID = [
    ("missing-tooth", ("stock-implant-model", "50% 55%", "A model of an implant crown on its post between two natural teeth"),
     ("stock-implant-crown", "50% 50%", "A single implant crown on its titanium post")),
    ("chipped-tooth", ("stock-patient-chair", "50% 40%", "A dentist examining a patient's front teeth with a mirror"),
     ("stock-veneer-fingertip", "50% 45%", "A thin porcelain veneer held up beside the front teeth of a model")),
    ("gaps", ("stock-crooked", "50% 55%", "A smile with a small gap between the front teeth"),
     ("stock-veneers-fabric", "50% 50%", "Four porcelain veneers on soft grey fabric")),
    ("crooked-teeth", ("stock-aligner-gloved", "50% 45%", "A clear aligner held between gloved fingers"),
     ("stock-aligner", "50% 50%", "A clear aligner on a pale background")),
    ("stained-teeth", ("stock-stained", "50% 50%", "A smile with yellowed teeth"),
     ("stock-shade-guide", "50% 20%", "A tooth shade guide on a dental lab table")),
    ("toothache", ("stock-toothache-lower", "50% 50%", "A hand held against a sore cheek, the lower face only"),
     ("stock-xray-screen", "50% 50%", "A dental X-ray of the whole mouth on a monitor beside the chair")),
    ("bleeding-gums", ("stock-exam", "50% 45%", "A gentle gum check with a mirror and probe"),
     ("stock-floss-hand", "50% 55%", "A coil of dental floss in an open hand")),
    ("loose-dentures", ("stock-denture-tray", "50% 55%", "A full denture on its clean white base"),
     ("stock-implant-overdenture", "50% 50%", "A denture on a model with the clips that hold it to implants")),
    ("child-teeth", ("stock-child-chair", "50% 45%", "A smiling girl in the dental chair beside her dentist"),
     ("stock-kid-dentist", "50% 40%", "A boy relaxed in the dental chair while his dentist checks his teeth")),
]

PROCESS = [  # apa: three photo panels, the numbered heading and two lines overlaid bottom-left
    ("arha-dental-care-consultation-desk", "50% 50%", "The consultation desk in an Arha treatment room", "1. Consultation",
     "We listen first, then examine carefully and explain your options clearly, so you can decide calmly."),
    ("arha-dental-care-chair-window", "50% 55%", "The dental chair under its light in an Arha treatment room", "2. Your treatment",
     "Planned in detail and carried out with precision, at a pace that keeps you comfortable."),
    ("arha-dental-care-reception-wide", "50% 50%", "Arha's reception and waiting area", "3. Lifelong care",
     "Reviews, cleanings and care that protect your result for years, at the practice that has looked after families since 1980."),
]

# Review tiles in apa's mosaic: two columns of tall (3:4) and wide (3:2) tiles, columns of equal height.
# (review index or "photo", shape, tone). Tones alternate so the mosaic reads like apa's covers: charcoal,
# stone and paper with a hairline; the one photograph (Arha's logo wall, 3:2) shows the rating on hover, as apa's covers do.
MOSAIC = [
    [(0, "tall", "dark"), (2, "wide", "stone"), (4, "wide", "line"), (6, "wide", "stone")],
    [(1, "wide", "line"), ("photo", "wide", None), (3, "tall", "dark"), (5, "wide", "stone")],
]
STAR = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 1.5l2.6 5.6 6.1.7-4.5 4.2 1.2 6-5.4-3-5.4 3 1.2-6-4.5-4.2 6.1-.7z"/></svg>'


def pic(name, sizes, alt, pos, i, eager=False):
    return picture(name, sizes, alt, pos=pos, eager=eager, indent=i)


def hero():
    return """    <!-- =================================================================== 1. HERO (apa: video, text bottom-left, one CTA) -->
    <section class="hero ah-hero" data-hero aria-labelledby="hero-title">
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
          <h1 id="hero-title">Specialist dentistry on Peddar Road</h1>
          <p class="hero__lede">Your smile, designed around your face, your comfort and the way you live.</p>
          <p class="hero__actions"><a class="link link--light" href="book/">Book a consultation</a></p>
        </div>
      </div>
    </section>
"""


def trio():
    cols = "".join(f"""
        <article class="ah-trio__item">
          <a class="ah-trio__media" href="{href}" tabindex="-1" aria-hidden="true">
{pic(name, '(min-width: 900px) 34vw, 100vw', alt, pos, '            ')}
          </a>
          <h3><a href="{href}">{title}</a></h3>
          <p>{line}</p>
        </article>""" for name, pos, alt, title, line, href in TRIO)
    return f"""
    <!-- =================================================================== 2. TRIO HEADING + 3. FEATURE TRIO -->
    <section class="ah-head" aria-labelledby="trio-title">
      <h2 id="trio-title"><a href="the-practice/">Crafted with precision. Given with care.</a></h2>
      <p>Specialist restorative and cosmetic dentistry with natural results, built on a family practice that began in 1980.</p>
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
      <div class="ah-band__text">
        <h2 id="band-title">A clinic built around calm</h2>
        <p>Marble, soft light and quiet rooms at Doctor House on Peddar Road. An X-ray room and a sterilisation room of our own, and two generations of dentists under one roof.</p>
        <a class="link link--light" href="founder/">About Arha</a>
      </div>
    </section>
"""


def grid():
    tiles = ""
    for slug, top, bottom in GRID:
        p = problems.PROBLEMS[slug]
        halves = "".join(f"""
            <span class="ah-tile__half">
{pic(name, '(min-width: 900px) 330px, 300px', alt, pos, '              ')}
            </span>""" for name, pos, alt in (top, bottom))
        tiles += f"""
        <li class="ah-tile">
          <a href="problems/{slug}/" data-colour-group>
            <span class="ah-tile__pair">{halves}
            </span>
            <span class="ah-tile__hover"><span class="ah-tile__name">{p['menu']}</span><span class="ah-tile__link">See how we fix it</span></span>
          </a>
        </li>"""
    return f"""
    <!-- =================================================================== 5. COMMON PROBLEMS WE TREAT (apa: the before & after grid) -->
    <section class="ah-grid" aria-labelledby="grid-title">
      <h2 id="grid-title"><a href="problems/">Common problems we treat</a></h2>
      <p class="ah-grid__lede">Each square shows a common problem above, and how it is usually put right below. Choose one to see how we fix it.</p>
      <ul class="ah-grid__tiles">{tiles}
      </ul>
      <p class="ah-grid__cta"><a class="link" href="treatments/">See all treatments</a></p>
    </section>
"""


def dark():
    return """
    <!-- =================================================================== 6. DARK BAND (apa: centred statement, one CTA) -->
    <section class="ah-dark" aria-labelledby="dark-title">
      <h2 id="dark-title">Dentistry, done carefully</h2>
      <p>Arha is led by a prosthodontist, a specialist in restoring and replacing teeth. Every plan starts with listening and a careful examination, and is explained clearly before anything begins.</p>
      <a class="link link--light" href="book/">Book a consultation</a>
    </section>
"""


def process():
    panels = "".join(f"""
      <article class="ah-process__panel">
{pic(name, '(min-width: 900px) 34vw, 100vw', alt, pos, '        ')}
        <div class="ah-process__text">
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
      <div class="ah-founder__text">
        <h2 id="founder-title">From the founder</h2>
        <blockquote>
          <p>“A good restoration should never announce itself. My aim is a result that feels natural, functions beautifully and lasts.”</p>
          <footer>Dr. Nikhil V. Jain, prosthodontist and implantologist</footer>
        </blockquote>
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
        <h3 id="teaser-title">Step inside Arha</h3>
        <a class="link" href="gallery/">Take the 360° tour</a>
      </div>
    </section>
"""


def reviews():
    stars = f'<span class="ah-review__stars" role="img" aria-label="5 out of 5 stars">{STAR * 5}</span>'
    cols = []
    for col in MOSAIC:
        items = ""
        for k, shape, tone in col:
            if k == "photo":
                items += f"""
          <li class="ah-review ah-review--{shape} ah-review--photo">
            <a href="#" data-google-reviews>
{pic('arha-dental-care-logo-dental-clinic-peddar-road', '(min-width: 900px) 450px, 250px', 'The Arha Dental Care emblem and name on the marble wall of the practice', '50% 50%', '              ')}
              <span class="ah-review__hover ah-review__hover--score">
                <span class="ah-review__score" data-show="google-rating">5.0</span>
                {stars}
                <span>Read all <span data-show="google-count-label">31 Google reviews</span></span>
              </span>
            </a>
          </li>"""
                continue
            items += f"""
          <li class="ah-review ah-review--{shape} ah-review--{tone}">
            <a href="#" data-google-reviews>
              <span class="ah-review__mark" aria-hidden="true">“</span>
              <blockquote><p>{html.escape(home.REVIEWS[k], quote=False)}</p></blockquote>
              <span class="ah-review__foot">{stars}<span class="ah-review__source">Google review</span></span>
              <span class="ah-review__hover"><span>Google review</span><span>Read on Google</span></span>
            </a>
          </li>"""
        cols.append(items)
    return f"""
    <!-- =================================================================== 10. REVIEWS HEADING + 11. MOSAIC (apa: the media section) -->
    <section class="ah-head ah-head--reviews" aria-labelledby="reviews-title">
      <!-- Rating and count from SITE (tools/pages.py), checked on Google on 29 Oct 2026 -->
      <h2 id="reviews-title"><span data-show="google-rating">5.0</span> · <span data-show="google-count-label">31 Google reviews</span></h2>
      <p>What patients say about Arha Dental Care, in their own words. Every line here is quoted as it was written on Google, where you can read each review in full.</p>
      <a class="link" href="#" data-google-reviews>Read all reviews on Google</a>
    </section>
    <section class="ah-mosaic" aria-label="Google reviews">
      <ul class="ah-mosaic__col">{cols[0]}
      </ul>
      <ul class="ah-mosaic__col">{cols[1]}
      </ul>
    </section>
"""


def main_html(visit=None):
    """The homepage <main>. The footer (apa's closing line, logo and columns) comes from chrome.py."""
    return ('  <main id="main" class="home-apa" tabindex="-1">\n\n' + hero() + trio() + band() + grid() + dark() + process() + founder()
            + teaser() + reviews() + "\n  </main>\n")
