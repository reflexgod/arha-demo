"""Our work (+ case pages), Founder, Doctors, The practice and Dental tourism, built from data.

Used by tools/pages.py. Unknown facts stay as visible placeholders (class "ph"): founder story,
portraits, languages, memberships, trip lengths. Sample cases are stock images, labelled
"Sample" everywhere, and never show a fake "before" (the slider's before side says so).
"""
import html
from urllib.parse import quote

import cases_markup
from picture import picture
from treatment_pages import ARROW, closing, crumbs, crumbs_jsonld, faq_block, steps_block, who_block, section

CAT_TREATMENT = {"implants": "dental-implants", "full-mouth": "full-mouth-rehabilitation",
                 "veneers": "cosmetic-dentistry", "aligners": "invisalign"}
SAMPLE_LINE = "Sample. Real, consented cases replace these at launch."


def ph(label, text, i="          "):
    """A clearly marked placeholder for content the clinic will send."""
    return f'{i}<div class="ph"><p class="ph__label">To come · {label}</p><p>{text}</p></div>'


def hero(pic, title, lede, trail, i="    "):
    return f"""{i}<section class="page-hero" aria-labelledby="page-title">
{i}  {pic}
{i}  <div class="page-hero__content">
{i}    <div class="hero__text">
{i}      {crumbs(trail)}
{i}      <h1 id="page-title">{title}</h1>
{i}      <p class="hero__lede">{lede}</p>
{i}    </div>
{i}  </div>
{i}</section>
"""


# ------------------------------------------------------------------ our work
def cases():
    """The sample cases with a slug each: sample-<category>-<n>."""
    out, count = [], {}
    for c in cases_markup.CASES:
        count[c["cat"]] = count.get(c["cat"], 0) + 1
        concern, plan, result = c.get("story") or cases_markup.STORIES[c["cat"]]
        looks, works, note = cases_markup.SAMPLE_COPY[c["cat"]] if c["sample"] else (c.get("looks"), c.get("works"), c.get("note"))
        out.append({**c, "slug": f"sample-{c['cat']}-{count[c['cat']]}", "name": cases_markup.NAMES[c["cat"]],
                    "concern": concern, "plan": plan, "result": result, "looks": looks, "works": works, "note": note})
    return out


def work_page(site_url):
    cs = cases()
    chips = "".join(f'<button type="button" data-work-filter="{k}" aria-pressed="{str(k == "all").lower()}">{v}</button>'
                    for k, v in cases_markup.FILTERS)
    cards = "".join(f"""
          <li class="work-card reveal" data-cat="{c['cat']}">
            <a href="our-work/{c['slug']}/">
              <span class="work-card__media media">
{picture(c['img'], '(min-width: 900px) 30vw, 50vw', f"Sample image for the demo ({c['name'].lower()})", pos=c.get('pos'), indent='                ')}
                <span class="work-card__tag">Sample</span>
              </span>
              <span class="work-card__name">{html.escape(c['name'])}</span>
              <span class="work-card__meta">{html.escape(c['meta'])}</span>
              <span class="work-card__more">See the full case{ARROW}</span>
            </a>
          </li>""" for c in cs)
    quotes = [("He managed my pain and resolved the problem on the same day.", True),
              ("He is patient, gentle and takes the time to answer all my questions.", False),
              ("Excellent doctor and excellent service.", False)]
    voices = "".join(f"""
          <li class="voice{' voice--lead' if lead else ''} reveal"><blockquote><p>“{q}”</p></blockquote><p class="voice__by"><span>A patient · on Google</span></p></li>"""
                     for q, lead in quotes)
    trail = [("Home", ""), ("Our work", "our-work/")]
    main = f"""  <main id="main" tabindex="-1">

    <section class="section work-intro" aria-labelledby="page-title">
      <div class="container">
        {crumbs(trail)}
        <div class="section-head reveal">
          <h1 id="page-title">Our work</h1>
          <p class="lede">Natural results, planned around each face and bite. Choose a treatment to filter the cases.</p>
        </div>
        <p class="cases-note">{SAMPLE_LINE} Results vary.</p>
        <div class="work-filter" role="group" aria-label="Filter by treatment">{chips}</div>
        <ul class="work-grid" data-work-grid>{cards}
        </ul>
        <p class="work-empty" data-work-empty hidden>No cases for this treatment yet.</p>
      </div>
    </section>

    <!-- =================================================================== TESTIMONIALS -->
    <section class="section section--stone texture reviews" aria-labelledby="voices-title">
      <div class="container">
        <div class="section-head reveal">
          <h2 id="voices-title">In patients’ words</h2>
        </div>
        <div class="video-slot reveal">
          <div class="video-slot__frame"><span class="video-slot__icon" aria-hidden="true"></span></div>
          <div>
            <p class="ph__label">To come · Video testimonial</p>
            <p>A short film of a patient describing their treatment, recorded with their written consent.</p>
          </div>
        </div>
        <ul class="voices">{voices}
        </ul>
        <div class="section-cta reveal"><a class="cta" href="#" data-google-reviews>Read all reviews on Google</a></div>
      </div>
    </section>
{closing("Your own result starts with a consultation")}
  </main>
"""
    meta = {"title": "Our Work: Before &amp; After | Arha Dental Care, Peddar Road",
            "description": "Before and after cases from Arha Dental Care, Peddar Road, Mumbai: implants, full mouth rehabilitation, veneers and aligners. Sample images until consented cases are added.",
            "jsonld": [crumbs_jsonld(site_url, trail)]}
    return meta, main


def case_page(site_url, n, cs):
    c = cs[n]
    prev_c, next_c = cs[n - 1], cs[(n + 1) % len(cs)]
    treat = CAT_TREATMENT[c["cat"]]
    trail = [("Home", ""), ("Our work", "our-work/"), (f"{c['name']}, sample case", f"our-work/{c['slug']}/")]
    pic = picture(c["img"], "(min-width: 900px) 50vw, 100vw", f"Sample image for the demo: after ({c['name'].lower()})", pos=c.get("pos"), eager=True, indent="            ")
    face = (f"""
        <figure class="case-face reveal">
          <div class="media case-face__media">
{picture(c['face'], '(min-width: 900px) 30vw, 100vw', 'Sample image for the demo: full face', indent='            ')}
          </div>
          <figcaption>Full face · Sample</figcaption>
        </figure>""" if c.get("face") else "")
    main = f"""  <main id="main" tabindex="-1">

    <section class="section case-page" aria-labelledby="page-title">
      <div class="container">
        {crumbs(trail)}
        <div class="case-page__grid">
          <figure class="compare case-compare">
            <div class="ba" data-compare>
{pic}
              <div class="ba__before ba__pending"><p>Before photograph</p><p>Added with the patient’s written consent at launch.</p></div>
              <span class="ba__label ba__label--before">Before</span><span class="ba__label ba__label--after">After</span>
              <input class="ba__range" type="range" min="0" max="100" value="50" aria-label="Compare before and after">
              <span class="ba__handle" aria-hidden="true"><span class="ba__grip"></span></span>
            </div>
            <figcaption>{SAMPLE_LINE}</figcaption>
          </figure>
          <div class="case-page__text">
            <p class="sample-tag">Sample</p>
            <h1 id="page-title">{html.escape(c['name'])}</h1>
            <p class="case-page__meta">{html.escape(c['meta'])}</p>
            <dl class="case-story">
              <div><dt>Concern</dt><dd>{c['concern']}</dd></div>
              <div><dt>Plan</dt><dd>{c['plan']}</dd></div>
              <div><dt>Result</dt><dd>{c['result']}</dd></div>
            </dl>
            <dl class="case-story case-story--lw">
              <div><dt>Looks · Sample</dt><dd>{c['looks']}</dd></div>
              <div><dt>Works · Sample</dt><dd>{c['works']}</dd></div>
            </dl>
            <p class="case-page__used">Treatment: <a href="{treat}/">{html.escape(c['name'])}</a></p>
            <p class="case-page__note">Results vary. Every plan is made for one person.</p>
          </div>
        </div>{face}
        <nav class="case-nav" aria-label="More cases">
          <a href="our-work/{prev_c['slug']}/"><span>Previous case</span>{html.escape(prev_c['name'])}</a>
          <a href="our-work/">All cases</a>
          <a href="our-work/{next_c['slug']}/"><span>Next case</span>{html.escape(next_c['name'])}</a>
        </nav>
      </div>
    </section>
{closing("Considering this treatment?", "A consultation shows what is possible for your teeth, and what it would involve.")}
  </main>
"""
    meta = {"title": f"{c['name']}: Sample Case | Arha Dental Care, Peddar Road",
            "description": f"A sample {c['name'].lower()} case from Arha Dental Care, Peddar Road: the concern, the plan and the result. Real, consented cases replace the samples at launch.",
            "jsonld": [crumbs_jsonld(site_url, trail)]}
    return f"our-work/{c['slug']}", meta, main


# ------------------------------------------------------------------ founder, doctors
def founder_page(site_url):
    trail = [("Home", ""), ("About", "founder/"), ("The founder", "founder/")]
    timeline = [("1980", "Dr. Vasant P. Jain begins a family dental practice."),
                ("Year to come", "Dr. Nikhil V. Jain joins the practice."),
                ("Year to come", "Arha Dental Care opens at Doctor House, Peddar Road."),
                ("Today", "Two generations, one standard of care.")]
    tl = "".join(f'<li class="reveal"><p class="founder-tl__year">{y}</p><p>{t}</p></li>' for y, t in timeline)
    main = f"""  <main id="main" tabindex="-1">

    <!-- Founder: Dr. Vasant P. Jain (door sign: "Dr. Vasant P. Jain, B.D.S., Dental Surgeon"; the demo's "since 1980").
         Story, portrait, quote and memberships are placeholders until the family sends them (notes/TO-CONFIRM.md). -->
    <section class="section founder" aria-labelledby="page-title">
      <div class="container">
        {crumbs(trail)}
        <div class="founder__head">
          <div class="founder__portrait portrait-ph reveal" role="img" aria-label="Portrait of Dr. Vasant P. Jain, to come">
            <p>Portrait to come</p>
          </div>
          <div class="founder__intro reveal">
            <p class="eyebrow">The founder</p>
            <h1 id="page-title">Dr. Vasant P. Jain</h1>
            <p class="lede">The dentist who began the family practice in 1980, from which Arha grew.</p>
            <p class="founder__creds">B.D.S. · Dental Surgeon</p>
          </div>
        </div>

        <div class="founder__body">
          <div class="founder__story reveal">
            <h2>The story</h2>
{ph("The story", "How the practice began, the patients and families it has looked after, and how it became Arha. In the family's own words.")}
          </div>
          <blockquote class="pull reveal">
            <p>“A quote from Dr. Vasant P. Jain on how he has always practised will appear here.”</p>
            <footer>Placeholder</footer>
          </blockquote>
          <div class="founder__timeline reveal">
            <h2>From 1980 to today</h2>
            <ol class="founder-tl">{tl}</ol>
          </div>
          <div class="founder__creds-block reveal">
            <h2>Credentials and memberships</h2>
            <dl class="vs">
              <div><dt>Qualification</dt><dd>B.D.S. (as on the clinic door)</dd></div>
              <div><dt>Memberships</dt><dd>To come</dd></div>
            </dl>
          </div>
        </div>
      </div>
    </section>
{closing("Meet the doctors", "Two generations practise together at Arha on Peddar Road.").replace('<a class="cta" href="book/">Book a Consultation</a>', '<a class="cta" href="doctors/">The doctors</a>')}
  </main>
"""
    meta = {"title": "Dr. Vasant P. Jain, Founder | Arha Dental Care, Peddar Road",
            "description": "The founder of Arha Dental Care: Dr. Vasant P. Jain, whose family dental practice on Peddar Road, Mumbai, began in 1980.",
            "jsonld": [crumbs_jsonld(site_url, trail)]}
    return meta, main


def doctors_page(site_url):
    trail = [("Home", ""), ("About", "founder/"), ("The doctors", "doctors/")]
    docs = [("nikhil", "Dr. Nikhil V. Jain", "B.D.S., M.D.S., ITI Scholar (London) · Prosthodontist &amp; Implantologist",
             "Dental implants, full mouth rehabilitation, smile design, crowns and bridges.", "Book with Dr. Nikhil"),
            ("vasant", "Dr. Vasant P. Jain", "B.D.S. · Dental Surgeon",
             None, "Book with Dr. Vasant")]
    cards = []
    for key, name, quals, focus, cta in docs:
        focus_html = f"<dd>{focus}</dd>" if focus else "<dd class=\"ph-inline\">To come</dd>"
        wa = "https://wa.me/910000000000?text=" + quote(f"Hello Arha Dental Care, I'd like to book a consultation with {name}.")
        cards.append(f"""
          <article class="doc reveal" id="{key}" aria-labelledby="{key}-name">
            <div class="doc__portrait portrait-ph" role="img" aria-label="Portrait of {name}, to come"><p>Portrait to come</p></div>
            <div class="doc__text">
              <h2 id="{key}-name">{name}</h2>
              <p class="doc__quals">{quals}</p>
              <dl class="vs">
                <div><dt>Areas of focus</dt>{focus_html}</div>
                <div><dt>Languages</dt><dd class="ph-inline">To come</dd></div>
              </dl>
              <div class="doc__actions">
                <a class="cta" href="{wa}" target="_blank" rel="noopener">{cta}</a>
                <a class="cta" href="book/">Book a consultation</a>
              </div>
            </div>
          </article>""")
    main = f"""  <main id="main" tabindex="-1">

    <!-- Qualifications as on the clinic's door sign. Portraits, languages and Dr. Vasant's areas of focus: to come. -->
    <section class="section" aria-labelledby="page-title">
      <div class="container">
        {crumbs(trail)}
        <div class="section-head reveal">
          <h1 id="page-title">The doctors</h1>
          <p class="lede">Two generations, one standard of care, on Peddar Road.</p>
        </div>
        <div class="docs">{"".join(cards)}
        </div>
      </div>
    </section>
{closing()}
  </main>
"""
    meta = {"title": "Our Dentists: Dr. Nikhil V. Jain and Dr. Vasant P. Jain | Arha Dental Care",
            "description": "Meet the dentists at Arha Dental Care, Peddar Road: Dr. Nikhil V. Jain, prosthodontist and implantologist, and Dr. Vasant P. Jain, dental surgeon.",
            "jsonld": [crumbs_jsonld(site_url, trail)]}
    return meta, main


# ------------------------------------------------------------------ the practice
GALLERY = [
    ("arha-dental-care-reception-south-mumbai-dental-clinic-02", "Reception: the gold emblem and wordmark on a marble wall above the front desk", "Reception"),
    ("arha-dental-care-reception-south-mumbai-dental-clinic-01", "Reception: a curved front desk, soft seating and a glass entrance door", "Reception"),
    ("arha-dental-care-lounge-peddar-road", "The patients’ lounge: a sofa, a plant and warm light", "Lounge"),
    ("dental-operatory-arha-dental-care-peddar-road-01", "A treatment room: the dental chair under its overhead light", "Treatment room"),
    ("dental-operatory-arha-dental-care-peddar-road-02", "A treatment room with a desk, the chair and marble walls", "Treatment room"),
    ("dental-operatory-arha-dental-care-peddar-road-06", "A second treatment room seen through a glass door", "Treatment room"),
    ("dental-operatory-arha-dental-care-peddar-road-04", "The consultation desk with a large monitor", "Planning desk"),
    ("dental-implant-equipment-arha-dental-care-mumbai", "The X-ray room: a floor-standing panoramic X-ray unit", "X-ray room"),
    ("autoclave-pantry-equipment-arha-dental-care-mumbai", "The sterilisation room: a benchtop steam steriliser beside a sink", "Sterilisation"),
    ("dental-dentistry-equipment-arha-dental-care-mumbai", "An automatic handpiece cleaning unit and a water distiller", "Instrument care"),
    ("arha-dental-care-exterior-dental-clinic-peddar-road", "The door of suite 107, Doctor House, with the Arha sign and the doctors’ names", "Entrance"),
    ("arha-dental-care-logo-dental-clinic-peddar-road", "The Arha wordmark and emblem in gold on marble", "Reception wall"),
]


def practice_page(site_url, visit):
    from PIL import Image
    trail = [("Home", ""), ("About", "founder/"), ("The practice", "the-practice/")]

    def ratio(name):  # each tile keeps its photo's own shape (masonry)
        w, h = Image.open(cases_markup.IMG / f"{name}-640.jpg").size
        return f"{w} / {h}"
    tiles = "".join(f"""
          <li class="gallery__item reveal">
            <button class="gallery__btn media media--hover" type="button" style="aspect-ratio: {ratio(name)}" data-gallery-open="{n}" aria-label="Open photo: {html.escape(cap)}">
{picture(name, '(min-width: 900px) 30vw, 50vw', alt, indent='              ')}
            </button>
            <p class="gallery__cap">{cap}</p>
          </li>""" for n, (name, alt, cap) in enumerate(GALLERY))
    full = [{"src": cases_markup.largest(name, "jpg", 1920), "alt": alt, "cap": cap} for name, alt, cap in GALLERY]
    data = "".join(f'<li data-src="{f["src"]}" data-alt="{html.escape(f["alt"])}" data-cap="{html.escape(f["cap"])}"></li>' for f in full)
    main = f"""  <main id="main" tabindex="-1">

{hero('{{pic arha-dental-care-reception-south-mumbai-dental-clinic-01-lower | 100vw | Arha Dental Care reception: a curved front desk, soft seating and a glass entrance door | pos=35% 70% | eager}}', "The practice", "Doctor House, 14 Peddar Road: reception, lounge, treatment rooms and the rooms behind them.", trail)}
    <!-- =================================================================== GALLERY (Arha's own photographs) -->
    <section class="section" id="gallery" aria-labelledby="gallery-title">
      <div class="container">
        <div class="section-head reveal">
          <h2 id="gallery-title">Gallery</h2>
          <p class="lede">Photographed at Arha, as it is. Select a photo to see it larger.</p>
        </div>
        <ul class="gallery" data-gallery>{tiles}
        </ul>
        <ul hidden data-gallery-full>{data}</ul>
      </div>
    </section>

    <!-- Gallery view: the case view's look, for photographs -->
    <div class="case-view gallery-view" id="gallery-view" role="dialog" aria-modal="true" aria-label="Photo" inert>
      <button class="case-view__close" type="button" data-gv-close aria-label="Close photo"></button>
      <button class="case-view__nav case-view__nav--prev" type="button" data-gv-prev aria-label="Previous photo"></button>
      <button class="case-view__nav case-view__nav--next" type="button" data-gv-next aria-label="Next photo"></button>
      <figure class="gallery-view__figure"><img data-gv-img alt=""><figcaption data-gv-cap></figcaption></figure>
    </div>

    <!-- =================================================================== CLINIC TOUR (video) -->
    <section class="section section--stone texture" id="video" aria-labelledby="video-title">
      <div class="container split split--even practice-video">
        <figure class="tour tour--page reveal" data-tour data-base="assets/video/tour-">
          <picture class="fill">
            <source type="image/avif" srcset="assets/video/tour-poster-720.avif 720w, assets/video/tour-poster-1080.avif 1080w" sizes="(min-width: 900px) 40vw, 100vw">
            <source type="image/webp" srcset="assets/video/tour-poster-720.webp 720w, assets/video/tour-poster-1080.webp 1080w" sizes="(min-width: 900px) 40vw, 100vw">
            <img src="assets/video/tour-poster-720.jpg" width="720" height="1280" loading="lazy" decoding="async" alt="Arha's reception, the first frame of the clinic tour">
          </picture>
          <button class="tour__play" type="button">
            <span class="tour__icon" aria-hidden="true"></span>
            <span class="tour__label">Play the clinic tour <span class="tour__len">1 min 24 s · no sound</span></span>
          </button>
        </figure>
        <div class="split__text reveal">
          <h2 id="video-title">Walk through the clinic</h2>
          <p>A short, unedited walk from reception through to the treatment rooms, filmed at Arha. It plays only when you press play, without sound.</p>
        </div>
      </div>
    </section>

    <!-- =================================================================== 360° TOUR (Pannellum, loaded only on click) -->
    <section class="section" id="tour" aria-labelledby="tour-title">
      <div class="container">
        <div class="section-head reveal">
          <h2 id="tour-title">360° tour</h2>
          <p class="lede">Look around every room as if you were standing in it: entrance, reception, lounge, treatment room and sterilisation.</p>
        </div>
        <div class="pano reveal" data-pano data-base="assets/">
          <picture class="fill">
            <source type="image/avif" srcset="assets/pano/sample-360-poster.avif">
            <source type="image/webp" srcset="assets/pano/sample-360-poster.webp">
            <img src="assets/pano/sample-360-poster.jpg" width="1280" height="704" loading="lazy" alt="A sample 360° photograph of a white room">
          </picture>
          <div class="pano__cover">
            <p class="pano__soon">Arha’s 360° tour is coming soon</p>
            <p>Until the clinic’s own 360° photographs are taken, try the viewer with a sample image.</p>
            <button class="cta" type="button" data-pano-start>Try the sample 360° view</button>
          </div>
          <div class="pano__viewer" id="pano-viewer" hidden></div>
        </div>
        <p class="pano__note">Sample image: a photo studio, not Arha. Drag, swipe or use the arrow keys to look around; the arrows on screen move between rooms.</p>
      </div>
    </section>

{visit}{closing("Come and see it for yourself", "Book a consultation, or call us to arrange a visit.")}
  </main>
"""
    meta = {"title": "The Practice: Gallery, Clinic Tour and 360° Tour | Arha Dental Care, Peddar Road",
            "description": "Inside Arha Dental Care on Peddar Road, Mumbai: a gallery of the reception, lounge and treatment rooms, the clinic tour video and a 360° tour.",
            "jsonld": [crumbs_jsonld(site_url, trail)]}
    return meta, main


# ------------------------------------------------------------------ dental tourism
def tourism_page(site_url):
    trail = [("Home", ""), ("Dental tourism", "dental-tourism/")]
    why = [("On Peddar Road, South Mumbai", "Opposite Jaslok Hospital, in Doctor House, 14 Peddar Road."),
           ("Close to Marine Drive", "South Mumbai has a wide choice of hotels and serviced apartments a short drive away."),
           ("Specialist-led", "Implants, full mouth rehabilitation and smile design, led by a prosthodontist."),
           ("Planned before you fly", "Your plan, visits and written estimate are agreed before you book travel.")]
    steps = [("Virtual consultation", "On WhatsApp or video: your concerns, your photographs and any recent X-rays."),
             ("Plan and written estimate", "A treatment plan with the number of visits, how long each takes, and the costs."),
             ("Arrival", "Your first appointment is fixed before you land."),
             ("Treatment visits", "Planned around the time you have in Mumbai."),
             ("Remote follow-up", "Reviews by WhatsApp or video once you are home.")]
    trips = [("Dental implants", "2 visits, about 5 to 7 days each"),
             ("Full mouth rehabilitation", "3 visits, about 7 to 10 days each"),
             ("Smile design &amp; veneers", "2 visits, about 7 to 10 days in all"),
             ("Clear aligners", "1 visit of about 3 to 5 days, then remote reviews")]
    trip_rows = "".join(f"<div><dt>{t}</dt><dd>{d}</dd></div>" for t, d in trips)
    faq = [("How do I pay?", "Your written estimate explains the costs and how payment works. Please ask us about anything that is unclear before you travel."),
           ("What happens with aftercare at home?", "We plan aftercare with you before you leave, and follow up by WhatsApp or video. Routine check-ups can continue with us on your next visit."),
           ("How far ahead should I plan?", "Start with a virtual consultation a few weeks before you hope to travel, so the plan and appointments are ready in time."),
           ("What should I bring?", "Any recent X-rays or scans, a list of your medicines, and details of past dental work."),
           ("Can someone come with me?", "Yes, you are welcome to bring someone to your appointments.")]
    main = f"""  <main id="main" tabindex="-1">

{hero('{{pic stock-marine-drive | 100vw | Marine Drive and the South Mumbai skyline across the bay | pos=50% 50% | eager}}', "Dental tourism", "Planning dental treatment in Mumbai from abroad: one virtual consultation, a written plan, then your visits.", trail)}
{section("", "why-title", "Why Arha", who_block(why))}
{section("section--stone texture", "how-title", "How it works", steps_block(steps))}
    <section class="section" aria-labelledby="trip-title">
      <div class="container split split--even">
        <div class="split__text reveal">
          <h2 id="trip-title">Typical trip lengths</h2>
          <p>Every plan is different. These sample figures show the shape of a typical trip; your own timeline comes with your plan.</p>
        </div>
        <div class="timing texture reveal">
          <p class="timing__flag">Sample · to be confirmed by Dr. Nikhil</p>
          <dl>{trip_rows}</dl>
        </div>
      </div>
    </section>
{{{{planner}}}}{faq_block(faq)}
    <section class="band" aria-labelledby="closing-title">
      <div class="container reveal">
        <h2 id="closing-title">Start with a virtual consultation</h2>
        <p>Talk to us from wherever you are. We will tell you what is possible and plan your visits around your travel.</p>
        <div class="band__actions">
          <a class="cta" href="book/#virtual">Book a virtual consultation</a>
          <a class="cta" href="https://wa.me/910000000000?text=Hello%20Arha%20Dental%20Care%2C%20I%27d%20like%20a%20virtual%20consultation." target="_blank" rel="noopener">WhatsApp us</a>
        </div>
      </div>
    </section>
  </main>
"""
    from treatment_pages import faq_jsonld
    meta = {"title": "Dental Tourism in Mumbai | Arha Dental Care, Peddar Road",
            "description": "Visiting Mumbai for dental treatment? Start with a virtual consultation, get a written plan and estimate, then your visits at Arha Dental Care, Peddar Road.",
            "jsonld": [faq_jsonld(faq), crumbs_jsonld(site_url, trail)]}
    return meta, main


def all_pages(site_url, visit):
    cs = cases()
    out = [("our-work", *work_page(site_url))]
    out += [case_page(site_url, n, cs) for n in range(len(cs))]
    out += [("founder", *founder_page(site_url)), ("doctors", *doctors_page(site_url)),
            ("the-practice", *practice_page(site_url, visit)), ("dental-tourism", *tourism_page(site_url))]
    return out
