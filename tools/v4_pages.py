"""Inner pages for v4, each built on one of apaaesthetic.com's page types (notes/FINAL-v4.md section 6),
with the shared components from tools/home.py. At most six or seven sections between the hero and
the closing band, one interactive in a section.

Facts only from the clinic. Anything not confirmed is a marked placeholder (notes/TO-CONFIRM.md).
"""
import html
import re
from pathlib import Path

from PIL import Image

import home
import more_pages
import problems
import technology
import treatment_pages as tp
import treatments
from home import ARROW, ba, carousel, problems_stage, results_grid, story, tour_figure
from picture import picture

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"


# ------------------------------------------------------------------ shared page parts
def page_hero(pic, title, lede, trail, eyebrow="", actions=True, i="    "):
    """apa's tall photo hero: text bottom-left over a wash; Book and Call as text links."""
    eb = f'\n{i}      <p class="eyebrow eyebrow--light">{eyebrow}</p>' if eyebrow else ""
    act = (f'\n{i}      <p class="hero__actions"><a class="link link--light" href="book/">Book a consultation</a>'
           f'<a class="link link--light" href="tel:+910000000000" data-call="page_hero" data-call-pop>Call now</a></p>') if actions else ""
    return f"""{i}<!-- =================================================================== HERO -->
{i}<section class="page-hero page-hero--tall" aria-labelledby="page-title">
{i}  {pic}
{i}  <div class="page-hero__content">
{i}    <div class="hero__text">
{i}      {tp.crumbs(trail)}{eb}
{i}      <h1 id="page-title">{title}</h1>
{i}      <p class="hero__lede">{lede}</p>{act}
{i}    </div>
{i}  </div>
{i}</section>
"""


def head(sid, title, lede="", eyebrow="", i="      "):
    eb = f'<p class="eyebrow">{eyebrow}</p>\n{i}  ' if eyebrow else ""
    ld = f'\n{i}  <p class="lede">{lede}</p>' if lede else ""
    return f'{i}<div class="section-head reveal">\n{i}  {eb}<h2 id="{sid}">{title}</h2>{ld}\n{i}</div>'


def drag(items_html, label, cls="", i="      "):
    return f"""{i}<div class="drag {cls}" data-drag aria-label="{label}">
{i}  <ul class="drag__track">{items_html}
{i}  </ul>
{i}  <div class="drag__ui">
{i}    <button class="drag__btn drag__btn--prev" type="button" aria-label="Previous"></button>
{i}    <span class="drag__progress" aria-hidden="true"><span></span></span>
{i}    <button class="drag__btn drag__btn--next" type="button" aria-label="Next"></button>
{i}  </div>
{i}</div>"""


def largest(name):
    """The biggest JPEG of a photograph, for the lightbox."""
    w = max(int(m.group(1)) for f in IMG.glob(f"{name}-*.jpg") if (m := re.fullmatch(rf"{re.escape(name)}-(\d+)\.jpg", f.name)))
    return f"assets/img/{name}-{w}.jpg"


def ratio(name):
    w, h = Image.open(IMG / f"{name}-640.jpg").size
    return w / h


# ------------------------------------------------------------------ treatment pages
STEP_PHOTOS = [  # keyword in the step title -> one of Arha's rooms (colour) or a clinical stock photograph
    (("consult", "assess", "ask how"), ("arha-dental-care-lounge-peddar-road", "50% 55%", "Arha’s patient lounge, where every visit begins")),
    (("x-ray",), ("dental-implant-equipment-arha-dental-care-mumbai", "50% 30%", "Arha’s X-ray room with its panoramic X-ray unit")),
    (("plan", "design", "record", "impression", "analysis", "examination"),
     ("stock-xray-screen", "50% 50%", "A dental X-ray displayed on a monitor in a clinic")),
    (("preview", "trial"), ("stock-mirror", "50% 40%", "A patient looking at their smile in a hand mirror")),
    (("aligner", "braces", "retainer"), ("stock-aligner", "50% 50%", "A clear aligner held between two fingers")),
    (("final", "fitting", "fitted", "crown", "temporary"), ("stock-crowns", "50% 55%", "Ceramic crowns resting on a dark surface")),
    (("heal",), ("arha-dental-care-reception-south-mumbai-dental-clinic-01-lower", "35% 70%", "Arha’s reception, calm and softly lit")),
    (("review", "aftercare", "maintenance", "your plan"), ("arha-dental-care-reception-south-mumbai-dental-clinic-02", "50% 40%", "Arha’s reception: the gold emblem on a marble wall")),
]
ROOM_FALLBACK = [("dental-operatory-arha-dental-care-peddar-road-01", "50% 60%", "An Arha treatment room: the dental chair under its overhead light"),
                 ("dental-operatory-arha-dental-care-peddar-road-06", "50% 55%", "A second Arha treatment room seen through a glass door"),
                 ("stock-cleaning", "50% 50%", "A dental hygienist cleaning a patient’s teeth")]


def step_photo(title, used):
    low = title.lower()
    for keys, shot in STEP_PHOTOS:
        if any(k in low for k in keys) and shot[0] not in used:
            return shot
    return next(s for s in ROOM_FALLBACK + [shot for _k, shot in STEP_PHOTOS] if s[0] not in used)


PROCESS_PHOTO = {  # one photograph per treatment page, pinned while its steps scroll past: Arha's own rooms first
    "dental-implants": ("arha-dental-care-operatory-chair", "50% 50%", "The dental chair and its light in an Arha treatment room"),
    "maxillofacial-prosthetics": ("arha-dental-care-planning-room", "50% 50%", "A quiet room at Arha with a desk beside the equipment counter"),
    "smile-design": ("stock-dentist-hands", "50% 50%", "A dentist's gloved hands at work, holding fine instruments"),
    "cosmetic-dentistry": ("arha-dental-care-operatory-laptop", "50% 50%", "An Arha treatment room with the chair, the light and a laptop on the counter"),
    "invisalign": ("arha-dental-care-operatory-chair", "50% 50%", "The dental chair and its light in an Arha treatment room"),
    "orthodontics": ("arha-dental-care-planning-room", "50% 50%", "A quiet room at Arha with a desk beside the equipment counter"),
    "general-dentistry": ("stock-instrument-tray", "50% 50%", "Sterile instruments laid out on a tray"),
    "crowns-bridges": ("arha-dental-care-delivery-unit", "50% 45%", "The instrument holder at an Arha chair, with its handpieces ready"),
}


def process(t, slug):
    """How it works: the steps scroll past one pinned photograph (the page's own, PROCESS_PHOTO)."""
    name, pos, alt = PROCESS_PHOTO[slug]
    steps = [(name, pos, alt, title, text) if n == 0 else (None, None, None, title, text) for n, (title, text) in enumerate(t["steps"])]
    return f"""
    <!-- =================================================================== HOW IT WORKS (sticky story) -->
    <section class="section section--flush process" aria-labelledby="process-title">
      <div class="container">
{head("process-title", "How it works", "Step by step, from the first conversation to the care that follows.")}
      </div>
{story(steps, label="How it works, step by step")}
    </section>
"""


def intro(t):
    title, lede, more = t["intro"]
    who = "".join(f'\n            <div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in t["who"])
    return f"""
    <!-- =================================================================== INTRO -->
    <section class="section intro-v4" aria-labelledby="intro-title">
      <div class="container intro-v4__grid">
        <div class="intro-v4__text reveal">
          <h2 id="intro-title">{title}</h2>
          <p class="lede">{lede}</p>
          <p>{more}</p>
        </div>
        <div class="intro-v4__who reveal">
          <h3>Is this for you?</h3>
          <dl class="who-list">{who}
          </dl>
        </div>
      </div>
    </section>
"""


CAT_FOR = {"implants": ["implants"], "full-mouth": ["full-mouth"], "veneers": ["veneers"], "aligners": ["aligners"]}


def results_pairs(cat, title="Sample cases"):
    """This treatment's sample cases as quiet links to their case pages (the photographs themselves stay on
    the homepage, Our work and each case page: v4 feedback 5)."""
    mine = [c for c in more_pages.cases() if cat and c["cat"] == cat]
    if not mine:
        return ""
    lis = "".join(f"""
          <li><a class="more-cases__link" href="our-work/{c['slug']}/"><span>{html.escape(c['name'])}</span><span>{html.escape(c['meta'])} · Sample case for demo</span></a></li>""" for c in mine)
    return f"""
    <!-- =================================================================== SAMPLE CASES (links) -->
    <section class="section results-links" aria-labelledby="results-title">
      <div class="container">
{head("results-title", title, "Before and after, built from stock photographs for the demo. Real, consented cases replace them before launch.")}
        <ul class="more-cases__list reveal">{lis}
        </ul>
        <p class="section-cta"><a class="link" href="our-work/">See all our work{ARROW}</a></p>
      </div>
    </section>
"""


def tech_used(slug):
    items = [t for t in technology.ITEMS if not t["treatments"] or slug in t["treatments"]][:4]
    lis = "".join(f"""
        <li class="techuse__item reveal">
          <a href="technology/#{t['slug']}">
            <span class="techuse__media media media--hover">
{picture(t['photo'], '(min-width: 900px) 25vw, 80vw', t['alt'], pos=t['pos'], indent='              ')}
            </span>
            <span class="techuse__name">{t['short']}</span>
            <span class="techuse__for">{t['for_you']}</span>
          </a>
        </li>""" for t in items)
    return f"""
    <!-- =================================================================== TECHNOLOGY USED -->
    <section class="section techuse" aria-labelledby="techuse-title">
      <div class="container">
{head("techuse-title", "Technology used", "", "Technology &amp; innovation")}
      </div>
      <ul class="techuse__list">{lis}
      </ul>
    </section>
"""


def treatment_page(slug, site_url):
    """apa's treatment page: tall hero, intro, the process as a sticky sequence, the page's own
    interactive, a before/after carousel, technology used, questions, then the closing band."""
    t = tp.TREATMENTS[slug]
    name, alt, pos = t["hero"]
    trail = [("Home", ""), ("Explore treatments", "treatments/"), (t["h1"], slug + "/")]
    eyebrow = "Specialist care" if slug in tp.specialty_slugs() else ""
    body = page_hero(f"{{{{pic {name} | 100vw | {alt} | pos={pos} | eager}}}}", t["h1"], t["lede"], trail, eyebrow)
    body += intro(t)
    fixes = problems.for_treatment(slug)
    if fixes:
        body += f"""
    <!-- =================================================================== PROBLEMS IT FIXES -->
    <nav class="container fixes-line reveal" aria-label="Problems this treatment fixes">
      <p class="eyebrow">Often chosen for</p>
      <ul>{"".join(f'<li><a class="link" href="problems/{s}/">{n}</a></li>' for s, n in fixes)}</ul>
    </nav>
"""
    if t["steps"]:
        body += process(t, slug)
    kind, ix_title, ix_lede = t["interactive"]
    body += "\n    <!-- =================================================================== INTERACTIVE -->" + tp.section(
        f"section--stone ix ix--{kind}", "ix-title", ix_title, "      " + tp.INTERACTIVES[kind](), ix_lede)
    body += results_pairs(t["cases"])
    body += problems.tech_list([x["slug"] for x in technology.ITEMS if not x["treatments"] or slug in x["treatments"]][:4])
    body += tp.faq_block(t["faq"])
    body += problems.closing_band()
    jsonld = [
        {"@context": "https://schema.org", "@type": "MedicalProcedure", "name": html.unescape(t["h1"]),
         "description": html.unescape(t["intro"][1]), "url": site_url + slug + "/"},
        tp.faq_jsonld(t["faq"]),
        tp.crumbs_jsonld(site_url, trail),
    ]
    return {"title": t["title"], "description": t["description"], "jsonld": jsonld}, f'  <main id="main" tabindex="-1">\n\n{body}\n  </main>\n'


# ------------------------------------------------------------------ explore treatments (index)
def hub_page(site_url):
    groups, shots = "", ""
    first = True
    for g in treatments.GROUPS:
        links = ""
        for item in g["items"]:
            s = item["slug"]
            t = tp.TREATMENTS.get(s)
            photo, alt, pos = (t.get("preview") or t["hero"]) if t else ("stock-parent-child", "A parent and child smiling together", "50% 40%")
            card = t["card"] if t else tp.KIDS["card"]
            links += f"""
              <li>
                <a class="tindex__link" href="{s}/" data-shot="{s}">
                  <span class="tindex__name">{item['name']}</span>
                  <span class="tindex__card">{card}</span>
                </a>
              </li>"""
            shots += f"""
          <div class="tindex__shot{' is-active' if first else ''}" data-shot="{s}">
{picture(photo, '(min-width: 900px) 50vw, 1px', alt, pos=pos, eager=first, indent='            ')}
          </div>"""
            first = False
        groups += f"""
          <div class="tindex__group">
            <h2 class="tindex__title">{g['title']}</h2>
            <p class="tindex__sub">{tp.GROUP_CARDS[g['title']]}</p>
            <ul>{links}
            </ul>
          </div>"""
    trail = [("Home", ""), ("Explore treatments", "treatments/")]
    body = page_hero("{{pic stock-implant-arch | 100vw | A full arch of implant-supported teeth on a model | pos=50% 50% | eager}}",
                     "Explore treatments", "Specialist care, smile and aesthetic treatment, and everyday care for the whole family.", trail)
    body += f"""
    <!-- =================================================================== INDEX (hover swaps the preview) -->
    <section class="section tindex" aria-label="Treatments" data-preview>
      <div class="container tindex__grid">
        <div class="tindex__list">{groups}
        </div>
        <div class="tindex__preview" aria-hidden="true">{shots}
        </div>
      </div>
    </section>

    <!-- =================================================================== WHAT WE FIX (links to the problem pages) -->
    <section class="section section--stone problem-links" id="problems" aria-labelledby="problems-title">
      <div class="container">
{head("problems-title", "Start with what is bothering you", "Each problem has its own page: what you may notice, and what treatment would involve.", "What we fix")}
        <ul class="problem-links__list reveal">{"".join(f'<li><a href="problems/{s}/">{problems.PROBLEMS[s]["menu"]}{ARROW}</a></li>' for s in problems.ORDER)}</ul>
      </div>
    </section>
{problems.closing_band()}"""
    meta = {"title": "Explore Treatments | Arha Dental Care, Peddar Road, South Mumbai",
            "description": "Dental treatments at Arha Dental Care, Peddar Road: implants, full mouth rehabilitation, smile design, aligners, braces, root canals, crowns, general and kids’ dentistry.",
            "jsonld": [tp.crumbs_jsonld(site_url, trail)]}
    return meta, f'  <main id="main" tabindex="-1">\n\n{body}\n  </main>\n'


# ------------------------------------------------------------------ our work, case pages
def work_page(site_url):
    cs = more_pages.cases()
    chips = "".join(f'<button type="button" data-work-filter="{k}" aria-pressed="{str(k == "all").lower()}">{v}</button>'
                    for k, v in more_pages.cases_markup.FILTERS)
    trail = [("Home", ""), ("Our work", "our-work/")]
    body = page_hero("{{pic arha-dental-care-logo-wall | 100vw | The Arha Dental Care emblem in gold on the reception’s marble wall | pos=50% 45% | eager}}", "Our work",
                     "Natural results, planned around each face and bite.", trail)
    body += f"""
    <!-- =================================================================== BEFORE & AFTER (filterable sliders) -->
    <section class="section" aria-labelledby="work-title">
      <div class="container-wide">
{head("work-title", "Before &amp; after", "Choose a treatment, then open a case to see how it was planned.")}
        <div class="work-filter" role="group" aria-label="Filter by treatment">{chips}</div>
        <p class="cases-note">Sample cases for the demo: one simulation on a stock photograph, and clinical-detail photographs for the others. Real cases, shared with each patient’s written consent, replace them before launch. Results vary.</p>
{results_grid(cs)}
        <p class="work-empty" data-work-empty hidden>No cases for this treatment yet.</p>
      </div>
    </section>

    <!-- =================================================================== TESTIMONIALS -->
    <section class="section section--stone testimonials" id="testimonials" aria-labelledby="testimonials-title">
      <div class="container">
{head("testimonials-title", "Testimonials", "", "In patients’ own words")}
{carousel(home.REVIEWS)}
        <p class="section-cta"><a class="link" href="#" data-google-reviews>Read all reviews on Google</a></p>
      </div>
    </section>
{tp.closing("Your own result starts with a consultation")}"""
    meta = {"title": "Our Work: Before &amp; After and Testimonials | Arha Dental Care, Peddar Road",
            "description": "Before and after cases and patient testimonials from Arha Dental Care, Peddar Road, Mumbai: implants, full mouth rehabilitation, veneers and aligners. Sample images until consented cases are added.",
            "jsonld": [tp.crumbs_jsonld(site_url, trail)]}
    return meta, f'  <main id="main" tabindex="-1">\n\n{body}\n  </main>\n'


def case_page(site_url, n, cs):
    c = cs[n]
    prev_c, next_c = cs[n - 1], cs[(n + 1) % len(cs)]
    treat = more_pages.CAT_TREATMENT[c["cat"]]
    trail = [("Home", ""), ("Our work", "our-work/"), (f"{c['name']}, sample case", f"our-work/{c['slug']}/")]
    if c.get("before"):
        big = ba(c, "(min-width: 900px) 90vw, 100vw", "        ", eager=True)
        note = "Drag across the photograph, tap it, or use the arrow keys to compare. A simulation on one stock photograph for the demo; a real, consented case replaces it before launch."
    else:
        big = f"""        <figure class="case-v4__photo media">
{picture(c['img'], '(min-width: 900px) 90vw, 100vw', c['card_alt'], pos=c.get('card_pos'), eager=True, indent='          ')}
          <figcaption class="sample-line">{home.SAMPLE}</figcaption>
        </figure>"""
        note = "A sample case for the demo, shown with a clinical-detail photograph. Real, consented cases with their own photographs replace it before launch."
    others = [x for x in cs if x is not c]
    more = "".join(f"""
          <li><a class="more-cases__link" href="our-work/{o['slug']}/"><span>{html.escape(o['name'])}</span><span>{html.escape(o['meta'])}</span></a></li>""" for o in others)
    body = f"""
    <section class="section case-v4" aria-labelledby="page-title">
      <div class="container">
        {tp.crumbs(trail)}
        <header class="case-v4__head reveal">
          <p class="eyebrow">Sample case</p>
          <h1 id="page-title">{html.escape(c['name'])}</h1>
          <p class="case-v4__meta">{html.escape(c['meta'])}</p>
        </header>
      </div>
      <div class="container-wide case-v4__stage">
{big}
        <p class="cases-note">{note}</p>
      </div>
      <div class="container case-v4__story">
        <dl class="case-story case-story--cols">
          <div><dt>Concern</dt><dd>{c['concern']}</dd></div>
          <div><dt>Plan</dt><dd>{c['plan']}</dd></div>
          <div><dt>Result</dt><dd>{c['result']}</dd></div>
        </dl>
        <dl class="case-story case-story--cols case-story--two">
          <div><dt>Looks · Sample</dt><dd>{c['looks']}</dd></div>
          <div><dt>Works · Sample</dt><dd>{c['works']}</dd></div>
        </dl>
        <p class="case-v4__used">Treatment: <a class="link" href="{treat}/">{html.escape(c['name'])}</a></p>
        <nav class="case-nav" aria-label="More cases">
          <a href="our-work/{prev_c['slug']}/"><span>Previous case</span>{html.escape(prev_c['name'])}</a>
          <a href="our-work/">All cases</a>
          <a href="our-work/{next_c['slug']}/"><span>Next case</span>{html.escape(next_c['name'])}</a>
        </nav>
      </div>
    </section>

    <!-- =================================================================== MORE TRANSFORMATIONS (apa: a dark band of other cases) -->
    <section class="section more-cases" aria-labelledby="more-title">
      <div class="container-wide">
{head("more-title", "More transformations")}
        <ul class="more-cases__list">{more}
        </ul>
        <p class="section-cta"><a class="link link--light" href="our-work/">See all our work{ARROW}</a></p>
      </div>
    </section>
{tp.closing("Considering this treatment?", "A consultation shows what is possible for your teeth, and what it would involve.")}"""
    meta = {"title": f"{c['name']}: Sample Case | Arha Dental Care, Peddar Road",
            "description": f"A sample {c['name'].lower()} case from Arha Dental Care, Peddar Road: the concern, the plan and the result. Real, consented cases replace the samples at launch.",
            "jsonld": [tp.crumbs_jsonld(site_url, trail)]}
    return f"our-work/{c['slug']}", meta, f'  <main id="main" tabindex="-1">\n{body}\n  </main>\n'


# ------------------------------------------------------------------ about: founder, doctors, practice, gallery
QUOTE = "A good restoration should never announce itself. My aim is a result that feels natural, functions beautifully and lasts."
TIMELINE = [("1980", "Dr. Vasant P. Jain begins a family dental practice in Mumbai.", "arha-dental-care-logo-dental-clinic-peddar-road", "50% 50%"),
            ("The next generation", "Dr. Nikhil V. Jain joins the practice, as a prosthodontist and implantologist.", "stock-handpieces", "50% 50%"),
            ("Arha", "Arha Dental Care opens at 107, Doctor House, 14 Peddar Road.", "arha-dental-care-reception-south-mumbai-dental-clinic-02", "50% 40%"),
            ("Today", "Two generations, one standard of care.", "arha-dental-care-lounge-peddar-road", "50% 55%")]


def founder_page(site_url):
    trail = [("Home", ""), ("About", "founder/"), ("About the founder", "founder/")]
    tl = "".join(f"""
          <li class="tl-card">
            <span class="tl-card__media media">
{picture(name, '(min-width: 900px) 30vw, 78vw', '', pos=pos, indent='              ')}
            </span>
            <p class="tl-card__year">{year}</p>
            <p>{text}</p>
          </li>""" for year, text, name, pos in TIMELINE)
    body = page_hero("{{pic arha-dental-care-reception-south-mumbai-dental-clinic-01 | 100vw | Arha's reception: a curved front desk and soft seating | pos=50% 50% | eager}}",
                     "Dr. Nikhil V. Jain", "Prosthodontist and implantologist, and the founder of Arha Dental Care on Peddar Road.", trail, "About the founder", actions=False)
    body += f"""
    <!-- =================================================================== THE LONG READ -->
    <!-- Founder: the brief names Dr. Nikhil as Arha's founder; the family practice began with Dr. Vasant P. Jain
         in 1980. The story in the family's own words, and the years, are placeholders (notes/TO-CONFIRM.md). -->
    <article class="section longread" aria-label="The story">
      <div class="container prose">
        <p class="longread__lead reveal">Arha grew out of a family practice. Dr. Vasant P. Jain began seeing patients in 1980; today Dr. Nikhil V. Jain leads Arha Dental Care at Doctor House on Peddar Road, where two generations practise side by side.</p>
        <p class="reveal">Dr. Nikhil is a prosthodontist: a specialist in restoring and replacing teeth. His qualifications, as on the clinic door, are B.D.S., M.D.S. and ITI Scholar (London). His work centres on dental implants, full mouth rehabilitation, smile design, and crowns and bridges.</p>
        <blockquote class="pull-quote pull-quote--big reveal">
          <p>“{QUOTE}”</p>
          <footer>Dr. Nikhil V. Jain</footer>
        </blockquote>
        <p class="reveal">Arha was designed to make specialist dentistry feel unhurried: marble, soft light, quiet treatment rooms, an X-ray room and a separate room for sterilisation, all under one roof.</p>
      </div>
    </article>

    <!-- =================================================================== 1980 TO TODAY (drag) -->
    <section class="section section--stone timeline-v4" aria-labelledby="tl-title">
      <div class="container">
{head("tl-title", "From 1980 to today", "Drag to move through the years.")}
      </div>
      <div class="container-wide">
{drag(tl, "From 1980 to today", "drag--timeline")}
      </div>
    </section>
{tp.closing("Meet the doctors", "Two generations practise together at Arha on Peddar Road.").replace('<a class="cta" href="book/">Book a Consultation</a>', '<a class="cta" href="doctors/">The doctors</a>')}"""
    meta = {"title": "About the Founder: Dr. Nikhil V. Jain | Arha Dental Care, Peddar Road",
            "description": "Dr. Nikhil V. Jain, prosthodontist and implantologist, founder of Arha Dental Care on Peddar Road, Mumbai, a family practice since 1980.",
            "jsonld": [tp.crumbs_jsonld(site_url, trail)]}
    return meta, f'  <main id="main" tabindex="-1">\n\n{body}\n  </main>\n'


def doctors_page(site_url):
    from urllib.parse import quote
    trail = [("Home", ""), ("About", "founder/"), ("The doctors", "doctors/")]
    docs = [("nikhil", "Dr. Nikhil V. Jain", "B.D.S., M.D.S., ITI Scholar (London)", "Prosthodontist &amp; Implantologist",
             "Dental implants, full mouth rehabilitation, smile design, crowns and bridges.", "Book with Dr. Nikhil"),
            ("vasant", "Dr. Vasant P. Jain", "B.D.S.", "Dental Surgeon", None, "Book with Dr. Vasant")]
    cards = ""
    for key, name, quals, role, focus, cta in docs:
        wa = "https://wa.me/910000000000?text=" + quote(f"Hello Arha Dental Care, I'd like to book a consultation with {name}.")
        focus_html = f"<dd>{focus}</dd>" if focus else '<dd class="ph-inline">To come</dd>'
        cards += f"""
        <article class="doc-v4 reveal" id="{key}" aria-labelledby="{key}-name">
          <div class="doc-v4__portrait portrait-ph" role="img" aria-label="Portrait of {name}, to come"><img src="assets/logo/logo-seal-bronze.svg" alt="" width="96" height="96"><p>Portrait to come</p></div>
          <p class="eyebrow">{role}</p>
          <h2 id="{key}-name">{name}</h2>
          <p class="doc-v4__quals">{quals}</p>
          <dl class="vs">
            <div><dt>Areas of focus</dt>{focus_html}</div>
            <div><dt>Languages</dt><dd class="ph-inline">To come</dd></div>
          </dl>
          <p class="doc-v4__actions"><a class="link" href="{wa}" target="_blank" rel="noopener">{cta}</a></p>
        </article>"""
    body = page_hero("{{pic dental-operatory-arha-dental-care-peddar-road-06 | 100vw | An Arha treatment room on Peddar Road | pos=50% 55% | eager}}",
                     "The doctors", "Two generations, one standard of care, on Peddar Road.", trail, "About")
    body += f"""
    <!-- Qualifications as on the clinic's door sign. Portraits, languages and Dr. Vasant's areas of focus: to come. -->
    <section class="section" aria-label="Our dentists">
      <div class="container-wide docs-v4">{cards}
      </div>
    </section>
{tp.closing()}"""
    meta = {"title": "Our Dentists: Dr. Nikhil V. Jain and Dr. Vasant P. Jain | Arha Dental Care",
            "description": "Meet the dentists at Arha Dental Care, Peddar Road: Dr. Nikhil V. Jain, prosthodontist and implantologist, and Dr. Vasant P. Jain, dental surgeon.",
            "jsonld": [tp.crumbs_jsonld(site_url, trail)]}
    return meta, f'  <main id="main" tabindex="-1">\n\n{body}\n  </main>\n'


def practice_page(site_url, visit):
    trail = [("Home", ""), ("About", "founder/"), ("The practice", "the-practice/")]
    rooms = "".join(f"""
          <li class="room" style="--r: {ratio(name):.3f}">
            <figure>
              <span class="room__media media">
{picture(name, '(min-width: 900px) 50vw, 86vw', alt, indent='                ')}
              </span>
              <figcaption>{cap}</figcaption>
            </figure>
          </li>""" for name, alt, cap in more_pages.GALLERY[:10])
    body = page_hero("{{pic arha-dental-care-reception-south-mumbai-dental-clinic-01-lower | 100vw | Arha Dental Care reception: a curved front desk, soft seating and a glass entrance door | pos=35% 70% | eager}}",
                     "The practice", "Doctor House, 14 Peddar Road: reception, lounge, treatment rooms and the rooms behind them.", trail, "About")
    body += f"""
    <!-- =================================================================== THE CLINIC -->
    <section class="section" aria-labelledby="story-title">
      <div class="container prose">
        <h2 id="story-title" class="reveal">A clinic built around calm</h2>
        <p class="lede reveal">Marble, soft light and quiet rooms. Arha is on the first floor of Doctor House, opposite Jaslok Hospital, and every room was planned so that specialist dentistry feels unhurried.</p>
        <p class="reveal">You arrive at a reception and a lounge, away from the treatment rooms. X-rays are taken in their own room, and instruments are cleaned and sterilised in a separate room of their own.</p>
      </div>
    </section>

    <!-- =================================================================== THE ROOMS (drag) -->
    <section class="section section--flush rooms" aria-labelledby="rooms-title">
      <div class="container">
{head("rooms-title", "The rooms", "Drag to walk through the clinic.")}
      </div>
{drag(rooms, "The rooms at Arha", "drag--rooms")}
      <p class="section-cta"><a class="link" href="gallery/">Gallery &amp; 360° tour{ARROW}</a></p>
    </section>

    <!-- =================================================================== HYGIENE AND STERILISATION -->
    <section class="statement statement--hygiene" aria-labelledby="hygiene-title">
      {{{{pic stock-instrument-tray | 100vw | Sterile instruments laid out on a tray | pos=50% 50%}}}}
      <div class="container statement__content reveal">
        <p class="eyebrow eyebrow--light">Hygiene &amp; sterilisation</p>
        <h2 id="hygiene-title">Kept safe, in a room of its own</h2>
        <p>Instruments are cleaned and sterilised in a separate room with a benchtop steam steriliser, away from where you are treated. Handpieces are cleaned and oiled by an automatic unit after use.</p>
        <a class="link link--light" href="technology/#group-safe">How we keep you safe{ARROW}</a>
      </div>
    </section>

{visit}{tp.closing("Come and see it for yourself", "Book a consultation, or call us to arrange a visit.")}"""
    meta = {"title": "The Practice: Rooms, Hygiene and Sterilisation | Arha Dental Care, Peddar Road",
            "description": "Inside Arha Dental Care on Peddar Road, Mumbai: reception, lounge, treatment rooms, the X-ray room and a separate sterilisation room.",
            "jsonld": [tp.crumbs_jsonld(site_url, trail)]}
    return meta, f'  <main id="main" tabindex="-1">\n\n{body}\n  </main>\n'


PANO = """    <!-- =================================================================== 360° TOUR (Pannellum, loads on click) -->
    <section class="section" id="tour" aria-labelledby="tour-title">
      <div class="container-wide">
{head}
        <div class="pano pano--wide reveal" data-pano data-base="assets/">
          <picture class="fill">
            <source type="image/avif" srcset="assets/pano/sample-360-poster.avif">
            <source type="image/webp" srcset="assets/pano/sample-360-poster.webp">
            <img src="assets/pano/sample-360-poster.jpg" width="1280" height="704" loading="lazy" alt="A sample 360° photograph of a white room">
          </picture>
          <div class="pano__cover">
            <p class="pano__soon">Sample 360° scene for the demo</p>
            <p>Until the clinic’s own 360° photographs are taken, look around with a sample image.</p>
            <button class="link link--light" type="button" data-pano-start>Start the sample 360° view</button>
          </div>
          <div class="pano__viewer" id="pano-viewer" hidden></div>
        </div>
        <p class="pano__note">Sample image: a photo studio, not Arha. Drag, swipe or use the arrow keys to look around.</p>
      </div>
    </section>
"""


def gallery_page(site_url):
    trail = [("Home", ""), ("About", "founder/"), ("Gallery &amp; 360° tour", "gallery/")]
    tiles = "".join(f"""
          <li class="gal__item reveal" style="--r: {ratio(name):.3f}">
            <a href="{largest(name)}" data-full="{largest(name)}" data-caption="{cap}">
              <span class="gal__media media media--hover">
{picture(name, '(min-width: 900px) 33vw, 100vw', alt, indent='                ')}
              </span>
              <span class="gal__cap">{cap}</span>
            </a>
          </li>""" for name, alt, cap in more_pages.GALLERY)
    body = page_hero("{{pic arha-dental-care-lounge-peddar-road | 100vw | Arha's patient lounge: soft seating and warm light | pos=50% 55% | eager}}",
                     "Gallery &amp; 360° tour", "Photographed at Arha, as it is. Open any photograph to see it large.", trail, "About", actions=False)
    body += f"""
    <!-- =================================================================== PHOTOGRAPHS (lightbox) -->
    <section class="section" aria-labelledby="gal-title">
      <div class="container-wide">
{head("gal-title", "The clinic", "Twelve photographs of Arha’s rooms.")}
        <ul class="gal" data-lightbox>{tiles}
        </ul>
      </div>
    </section>

    <!-- =================================================================== CLINIC TOUR (film) -->
    <section class="inside inside--page" id="film" aria-labelledby="film-title">
      {{{{pic arha-dental-care-reception-south-mumbai-dental-clinic-02 | 100vw | Arha’s reception: the gold emblem and wordmark on a marble wall | pos=50% 40%}}}}
      <div class="container inside__grid">
        <div class="inside__text reveal">
          <h2 id="film-title">Walk through the clinic</h2>
          <p>A short, unedited walk from reception through to the treatment rooms, filmed at Arha. It plays only when you press play, without sound.</p>
        </div>
{tour_figure()}
      </div>
    </section>

{PANO.replace("{head}", head("tour-title", "360° tour", "Look around every room as if you were standing in it."))}{tp.closing("Come and see it for yourself", "Book a consultation, or call us to arrange a visit.")}"""
    meta = {"title": "Gallery and 360° Tour | Arha Dental Care, Peddar Road",
            "description": "Photographs of Arha Dental Care on Peddar Road, Mumbai, the clinic tour film and a 360° tour (a sample until Arha's own 360° photographs are taken).",
            "jsonld": [tp.crumbs_jsonld(site_url, trail)]}
    return meta, f'  <main id="main" tabindex="-1">\n\n{body}\n  </main>\n'


def all_pages(site_url, visit):
    """Every page v4 builds itself; the rest (kids, technology, tourism) come from the older modules."""
    cs = more_pages.cases()
    out = [(slug, *treatment_page(slug, site_url)) for slug in tp.TREATMENTS]
    out += [("kids-dentistry", *tp.kids_page(site_url)), ("treatments", *hub_page(site_url)),
            ("technology", *tp.technology_page(site_url)), ("our-work", *work_page(site_url))]
    out += [case_page(site_url, n, cs) for n in range(len(cs))]
    out += [("founder", *founder_page(site_url)), ("doctors", *doctors_page(site_url)),
            ("the-practice", *practice_page(site_url, visit)), ("gallery", *gallery_page(site_url)),
            ("dental-tourism", *more_pages.tourism_page(site_url))]
    out += problems.all_pages(site_url)
    return out
