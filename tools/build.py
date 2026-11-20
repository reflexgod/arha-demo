"""Build the Arha Dental Care site (v5) into dist/.

Usage:  .venv/Scripts/python -I tools/build.py            (or: python tools/build.py on Cloudflare Pages)

Every page is pre-rendered HTML from templates/ (Jinja2) and content/ (YAML). Contact details, hours and switches
come only from content/site.yaml. The build also writes sitemap.xml, robots.txt, _headers and _redirects, and fails
on: duplicate or over-long titles/descriptions, a page without exactly one <h1>, an <img> without alt, any banned word.
"""
import hashlib
import html
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
TODAY = date.today()
BANNED = [r"\bn8n\b", r"\bNHS\b", r"\bpainless\b", r"\bguarantee", r"\bbest\b", r"\bRiya\b", r"\b1980\b"]
# Extra words that must never appear, kept outside the repo: one regex per line in notes/banned-words.txt
_extra = ROOT / "notes" / "banned-words.txt"
if _extra.exists():
    BANNED += [l.strip() for l in _extra.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def load(name):
    return yaml.safe_load((CONTENT / name).read_text(encoding="utf-8"))


SITE = load("site.yaml")
NAV = load("nav.yaml")
for _t in NAV["treatments"]:  # a treatment can live outside /treatments/ (the emergency page has its own URL)
    _t.setdefault("href", f"/treatments/{_t['slug']}/")
MEDIA = json.loads((STATIC / "media.json").read_text(encoding="utf-8"))
# Google reviews: content/google-reviews.json, copied word for word from the Google profile (rating, count, maps_cid_url,
# featured[]). Shown on the homepage only, when site.yaml show_reviews is true. No review schema.
REVIEWS = json.loads((CONTENT / "google-reviews.json").read_text(encoding="utf-8")) if (CONTENT / "google-reviews.json").exists() else {}


# ------------------------------------------------------------------------------------------------ helpers
def asset_version(rel):
    return hashlib.md5((STATIC / rel).read_bytes()).hexdigest()[:10]


TBC_RE = re.compile(r"\[\[TBC:?\s*([^\]]*)\]\]")
REVIEW_BUILD = os.environ.get("ARHA_REVIEW") == "1"   # ARHA_REVIEW=1 builds with every [[TBC]] tag visible


def _tbc_split(body):
    """[[TBC: note || fallback]] -> (note, fallback). The fallback is the neutral text visitors see until confirmed."""
    note, _, fb = body.partition("||")
    return note.strip(), fb.strip()


def tbc(text):
    """Facts the clinic still has to confirm. Public pages show only the fallback text (or nothing); the yellow
    <mark class="tbc"> tag shows with ?review=1 (site.js / head script) or an ARHA_REVIEW=1 build."""
    def rep(m):
        note, fb = _tbc_split(m.group(1))
        out = f'<mark class="tbc" title="To be confirmed by the clinic">[[TBC: {html.escape(note)}]]</mark>'
        return out + (f'<span class="tbc-fb">{html.escape(fb)}</span>' if fb else "")
    return Markup(TBC_RE.sub(rep, str(text)))


def strip_tbc(text):
    """Plain-text contexts (titles, alt text, schema): the fallback if there is one, else nothing."""
    def rep(m):
        fb = _tbc_split(m.group(1))[1]
        return (" " + fb) if fb else ""
    return re.sub(r"\s*\[\[TBC:?([^\]]*)\]\]", rep, str(text)).strip()


TBC_ONLY_RE = re.compile(r'<(p|li|dd|dt|h[1-6]|span|td)((?:\s[^>]*)?)>(\s*<mark class="tbc"[^>]*>[^<]*</mark>\s*)</\1>')


def mark_tbc_only(out):
    """An element whose whole content is a [[TBC]] with no fallback gets class tbc-only (hidden on public pages)."""
    def rep(m):
        tag, attrs, inner = m.groups()
        if 'class="' in attrs:
            attrs = attrs.replace('class="', 'class="tbc-only ', 1)
        else:
            attrs += ' class="tbc-only"'
        return f"<{tag}{attrs}>{inner}</{tag}>"
    return TBC_ONLY_RE.sub(rep, out)


def picture(name, sizes, cls="", eager=False, alt=None, pos=None):
    m = MEDIA["images"][name]
    ws = m["widths"]
    rw, rh = m["ratio"]
    srcset = lambda ext: ", ".join(f"/static/img/{name}-{w}.{ext} {w}w" for w in ws)
    big = ws[-1]
    h = round(big * rh / rw)
    pos = pos or m.get("pos")  # media.yaml pos: the focal point when the box crops the file
    style = f' style="object-position:{pos}"' if pos else ""
    load_attr = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    alt_text = html.escape(alt if alt is not None else m["alt"], quote=True)
    return Markup(
        f'<picture class="{cls}">'
        f'<source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
        f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
        f'<img src="/static/img/{name}-{ws[min(1, len(ws) - 1)]}.jpg" srcset="{srcset("jpg")}" sizes="{sizes}" '
        f'width="{big}" height="{h}" alt="{alt_text}"{style} {load_attr}></picture>')


def preload(name, sizes="100vw", default=1440):
    """<link rel=preload> for a hero image, built from the widths the image really has (a tight crop may stop short of
    1920, so a hard-coded srcset would point at a missing file)."""
    ws = MEDIA["images"][name]["widths"]
    href = min(ws, key=lambda w: abs(w - default))
    ss = ", ".join(f"/static/img/{name}-{w}.avif {w}w" for w in ws)
    return Markup(f'<link rel="preload" as="image" href="/static/img/{name}-{href}.avif" type="image/avif" '
                  f'imagesrcset="{ss}" imagesizes="{sizes}">')


def video(name, cls="", eager_poster=False, label="", manual=False, sizes="(min-width: 900px) 50vw, 100vw"):
    """Muted looping video: poster first, sources attached by site.js when on screen (or when its menu opens: manual)."""
    v = MEDIA["videos"][name]
    small, large = v["sizes"][0], v["sizes"][-1]
    srcs = []
    for w, h in ([large] if small == large else [large, small]):
        media = "" if small == large else ("(min-width: 900px)" if [w, h] == list(large) else "(max-width: 899px)")
        mq = f' data-media="{media}"' if media else ""
        if not v.get("audio"):
            srcs.append(f'<source data-src="/static/video/{name}-{w}.webm" type="video/webm"{mq}>')
        srcs.append(f'<source data-src="/static/video/{name}-{w}.mp4" type="video/mp4"{mq}>')
    rw, rh = v["ratio"]
    pic = picture_poster(name, eager_poster, sizes)
    attr = "data-video-manual" if manual else "data-video"
    return Markup(
        f'<div class="vid {cls}" {attr}>{pic}'
        f'<video muted loop playsinline preload="none" width="{rw}" height="{rh}" aria-label="{html.escape(label, quote=True)}" '
        f'>{"".join(srcs)}</video></div>')


def embed(name, title, sizes="(min-width: 768px) 45vw, 100vw", caption=""):
    """Click-to-play film with controls (the reference's embedded-video card). Nothing loads until the visitor presses
    play. Clips without a soundtrack play muted. caption = small text on the frame (none used at present)."""
    v = MEDIA["videos"][name]
    w = v["sizes"][-1][0]
    muted = "" if v.get("audio") else " data-muted"
    cap = f'<span class="embed__cap">{html.escape(caption)}</span>' if caption else ""
    return Markup(
        f'<div class="embed" data-embed="/static/video/{name}-{w}.mp4" data-name="{name}"{muted}>{picture_poster(name, False, sizes)}{cap}'
        f'<button class="embed__play" type="button" aria-label="Play video: {html.escape(title, quote=True)}">'
        f'<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="31" fill="rgba(15,27,39,.55)" stroke="#FDFDFD" stroke-width="1.5"/>'
        f'<path d="M26 21v22l17-11z" fill="#FDFDFD"/></svg><span>{html.escape(title)}</span></button></div>')


def picture_poster(name, eager, sizes="(min-width: 900px) 50vw, 100vw"):
    v = MEDIA["videos"][name]
    ws = v["poster_widths"]
    rw, rh = v["ratio"]
    ss = lambda ext: ", ".join(f"/static/img/{name}-poster-{w}.{ext} {w}w" for w in ws)
    load_attr = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture class="vid__poster"><source type="image/avif" srcset="{ss("avif")}" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{ss("webp")}" sizes="{sizes}">'
            f'<img src="/static/img/{name}-poster-{ws[0]}.jpg" width="{ws[-1]}" height="{round(ws[-1] * rh / rw)}" alt="" {load_attr} decoding="async"></picture>')


def tel(n):
    return "tel:" + re.sub(r"[^\d+]", "", n)


def wa(n, text=None):
    digits = re.sub(r"\D", "", n)
    return f"https://wa.me/{digits}" + (f"?text={quote(text)}" if text else "")


def fmt_time(t):
    h, m = map(int, t.split(":"))
    suffix = "am" if h < 12 else "pm"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {suffix}" if m else f"{h12} {suffix}"


def hours_rows():
    """Monday-first rows for the opening-hours list: [(day, text)], merging nothing (one row per day)."""
    rows = []
    for i in [1, 2, 3, 4, 5, 6, 0]:
        d = SITE["hours"][i]
        rows.append((DAYS[i], f"{fmt_time(d[0])} – {fmt_time(d[1])}" if d else "Closed"))
    return rows


def address_one_line():
    a = SITE["address"]
    road = f" ({a['road']})" if a.get("road") else ""
    return f"{a['line1']}, {a['line2']}{road}, {a['locality']} {a['postcode']}"


def address_full():
    """Postal address as the clinic writes it, with the landmark: footer and schema."""
    a = SITE["address"]
    road = f" ({a['road']})" if a.get("road") else ""
    near = ", Opp. " + a["landmark"].removeprefix("Opposite ") if a.get("landmark", "").startswith("Opposite ") else (f", {a['landmark']}" if a.get("landmark") else "")
    return f"{a['line1']}, {a['line2']}{road}{near}, {a['locality']} {a['postcode']}"


def maps_dir():
    return "https://www.google.com/maps/dir/?api=1&destination=" + quote(SITE["maps_query"])


def maps_embed():
    return "https://www.google.com/maps?q=" + quote(SITE["maps_query"]) + "&output=embed"


def client_config():
    cfg = {"phone": SITE["phone"], "timeZone": SITE["time_zone"], "hours": SITE["hours"],
           "formsEndpoint": SITE["forms_endpoint"], "turnstile": SITE["turnstile_site_key"], "ga4": SITE["ga4_id"]}
    return Markup(json.dumps(cfg, separators=(",", ":")))


# ------------------------------------------------------------------------------------------------ schema
def org_node():
    a = SITE["address"]
    spec = []
    for i in range(7):
        d = SITE["hours"][i]
        if d:
            spec.append({"@type": "OpeningHoursSpecification", "dayOfWeek": DAYS[i], "opens": d[0], "closes": d[1]})
    node = {
        "@type": ["Dentist", "LocalBusiness"], "@id": SITE["domain"] + "/#clinic", "name": SITE["name"],
        "url": SITE["domain"] + "/", "telephone": SITE["phone"].replace(" ", ""),
        "image": SITE["domain"] + "/static/img/practice-hero-1440.jpg",
        "logo": SITE["domain"] + "/static/brand/logo-lockup-dark.svg",
        "address": {"@type": "PostalAddress", "streetAddress": address_full().rsplit(", " + a["locality"], 1)[0], "addressLocality": a["locality"],
                    "addressRegion": a["region"], "postalCode": a["postcode"], "addressCountry": a["country"]},
        "geo": {"@type": "GeoCoordinates", "latitude": SITE["geo"]["lat"], "longitude": SITE["geo"]["lng"]},
        "hasMap": "https://www.google.com/maps?q=" + quote(SITE["maps_query"]),
        "openingHoursSpecification": spec,
        "areaServed": ["Peddar Road", "Kemps Corner", "Breach Candy", "Malabar Hill", "Cumballa Hill", "Tardeo", "South Mumbai"],
        "employee": [{"@type": "Person", "@id": person_id(d), "name": d["name"], "url": SITE["domain"] + doctor_path(d)} for d in SITE["doctors"]],
        "priceRange": "₹₹",
    }
    if SITE.get("email"):
        node["email"] = SITE["email"]
    if SITE.get("same_as"):
        node["sameAs"] = [x["url"] for x in SITE["same_as"]]
    return node


def doctor_path(d):
    return f"/doctors/{d['slug']}/"


def person_id(d):
    return SITE["domain"] + doctor_path(d) + "#person"


def person_node(d, full=False):
    """Person for a doctor. The full node (on the doctor's own page) adds credentials, description and specialties."""
    n = {"@type": "Person", "@id": person_id(d), "name": d["name"], "jobTitle": d["role"], "honorificSuffix": d["credentials"],
         "url": SITE["domain"] + doctor_path(d), "worksFor": {"@id": SITE["domain"] + "/#clinic"}}
    if d.get("registration"):
        n["identifier"] = d["registration"]
    if full:
        n.update({"honorificPrefix": "Dr.", "description": d["description"], "knowsAbout": d["knows_about"],
                  "hasOccupation": {"@type": "Occupation", "name": d["role"]},
                  "hasCredential": [{"@type": "EducationalOccupationalCredential", "name": q["full"],
                                     "alternateName": q["name"], "credentialCategory": q["category"]} for q in d["qualifications"]]})
    return n


def person_nodes():
    return [person_node(d) for d in SITE["doctors"]]


def breadcrumb_node(crumbs):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE["domain"] + href} for i, (name, href) in enumerate(crumbs)]}


def jsonld(*nodes):
    graph = {"@context": "https://schema.org", "@graph": [n for n in nodes if n]}
    return Markup('<script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False, separators=(",", ":")) + "</script>")


# ------------------------------------------------------------------------------------------------ pages
def treatment_pages():
    pages = []
    for f in sorted((CONTENT / "treatments").glob("*.yaml")):
        t = yaml.safe_load(f.read_text(encoding="utf-8"))
        path = t.get("path") or f"/treatments/{t['slug']}/"
        crumbs = ([("Home", "/"), (t["nav_label"], path)] if t.get("path") else
                  [("Home", "/"), ("Treatments", "/treatments/"), (t["nav_label"], path)])
        faqs = [qa for s in t["sections"] for qa in s.get("faqs", [])]
        proc = {"@type": "MedicalProcedure", "name": strip_tbc(t["h1"]), "url": SITE["domain"] + path,
                "description": strip_tbc(t["answer"]), "procedureType": "https://schema.org/" + t["procedure"]["type"],
                "bodyLocation": t["procedure"]["body_location"], "howPerformed": t["procedure"]["how_performed"],
                "preparation": t["procedure"]["preparation"], "followup": t["procedure"]["followup"]}
        faq = faq_node(faqs)
        pages.append({"path": path, "template": t.get("template", "treatment.html"), "title": t["title"], "description": t["description"],
                      "crumbs": crumbs, "t": t, "schema": [org_node(), breadcrumb_node(crumbs), proc, faq],
                      "og_image": f"/static/img/{t['hero']}-1080.jpg", "noindex": t.get("noindex", False)})
    return pages


def static_pages():
    return [
        {"path": "/", "template": "home.html", "title": "Dentist on Peddar Road, South Mumbai | Arha Dental Care",
         "description": "Arha Dental Care, 107 Doctor House, Peddar Road: implants, crowns, root canal treatment and children's dentistry, led by prosthodontist Dr. Nikhil V. Jain.",
         "crumbs": None, "schema": [org_node(), *person_nodes()], "og_image": "/static/img/home-hero-918.jpg"},
        {"path": "/the-practice/", "template": "practice.html", "title": "About Arha Dental Care | Our Story and Team",
         "description": "Meet Dr. Nikhil V. Jain, prosthodontist and ITI Scholar (London), and Dr. Vasant P. Jain at Arha Dental Care, 107 Doctor House, Peddar Road, Mumbai.",
         "crumbs": [("Home", "/"), ("The practice", "/the-practice/")], "og_image": "/static/img/practice-hero-800.jpg", "fp": load("for-patients.yaml"),
         "schema_fn": lambda p: [org_node(), *person_nodes(), breadcrumb_node(p["crumbs"])]},
        {"path": "/contact/", "template": "contact.html", "title": "Book an Appointment | Arha Dental Care, Peddar Road",
         "description": "Book an appointment or send an enquiry to Arha Dental Care, 107 Doctor House, Peddar Road. Easy to reach from Kemps Corner, Breach Candy and Malabar Hill.",
         "crumbs": [("Home", "/"), ("Contact", "/contact/")], "og_image": "/static/img/contact-photo-800.jpg",
         "schema_fn": lambda p: [org_node(), breadcrumb_node(p["crumbs"])]},
        {"path": "/404.html", "template": "404.html", "title": "Page not found | Arha Dental Care",
         "description": "This page has moved or no longer exists. Find treatments, book an appointment or call Arha Dental Care on Peddar Road, Mumbai.",
         "crumbs": None, "schema": [], "noindex": True, "og_image": "/static/img/practice-hero-800.jpg"},
    ]


def faq_node(faqs):
    """FAQPage schema. Questions whose answer is still only a [[TBC]] stay on the page but out of the schema."""
    qs = [{"@type": "Question", "name": qa["q"], "acceptedAnswer": {"@type": "Answer", "text": strip_tbc(qa["a"])}}
          for qa in faqs if strip_tbc(qa["a"])]
    return {"@type": "FAQPage", "mainEntity": qs} if qs else None


def international_page():
    """International & NRI hub: noindex, kept out of menus and the sitemap until approved."""
    i = load("international.yaml")
    plans = load("travel-plans.yaml")
    data = {"plans": plans, "countries": i["countries"], "general": i["general"], "hours": SITE["hours"],
            "clinicTz": SITE["time_zone"], "whatsapp": re.sub(r"\D", "", SITE["whatsapp"]), "phone": SITE["phone"]}
    plan_json = Markup(json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
    crumbs = [("Home", "/"), ("International patients", "/international-patients/")]
    return [{"path": "/international-patients/", "template": "international.html", "title": i["title"],
             "description": i["description"], "crumbs": crumbs, "noindex": True, "i": i, "plans": plans,
             "plan_json": plan_json, "og_image": "/static/img/practice-story-715.jpg",
             "schema": [org_node(), breadcrumb_node(crumbs), faq_node(i["faqs"])]}]


def fill_tokens(text):
    """Policy text: {phone}, {address}, {email} come from site.yaml so they never drift."""
    email = f'<a href="mailto:{SITE["email"]}">{SITE["email"]}</a>' if SITE["email"] else "[[TBC: clinic email || the enquiry form on our contact page]]"
    return (text.replace("{phone}", f'<a href="{tel(SITE["phone"])}">{SITE["phone_display"]}</a>')
                .replace("{address}", html.escape(address_one_line())).replace("{email}", email))


def more_pages():
    hub = load("hub.yaml")
    fp = load("for-patients.yaml")
    pages = [
        {"path": "/treatments/", "template": "hub.html", "title": hub["title"], "description": hub["description"],
         "crumbs": [("Home", "/"), ("Treatments", "/treatments/")], "h": hub, "og_image": "/static/img/hub-implants-1080.jpg",
         "schema_fn": lambda p: [org_node(), breadcrumb_node(p["crumbs"]), faq_node(p["h"]["faqs"])]},
        {"path": "/for-patients/", "template": "for_patients.html", "title": fp["title"], "description": fp["description"],
         "crumbs": [("Home", "/"), ("For patients", "/for-patients/")], "fp": fp, "og_image": f"/static/img/{fp['hero']}-1080.jpg",
         "schema_fn": lambda p: [org_node(), breadcrumb_node(p["crumbs"])]},
        {"path": "/referrals/", "template": "referrals.html", "title": "Dental Referrals to a Prosthodontist | Arha Dental Care",
         "description": "Refer a patient to prosthodontist Dr. Nikhil V. Jain at Arha Dental Care, Peddar Road: implants, crowns, bridges, dentures and full-mouth rehabilitation.",
         "crumbs": [("Home", "/"), ("Dental referrals", "/referrals/")], "og_image": "/static/img/practice-hero-800.jpg",
         "schema_fn": lambda p: [org_node(), breadcrumb_node(p["crumbs"])]},
    ]
    for f in sorted((CONTENT / "policies").glob("*.yaml")):
        pol = yaml.safe_load(f.read_text(encoding="utf-8"))
        pol["intro"] = fill_tokens(pol["intro"])
        for sec in pol["sections"]:
            sec["body"] = fill_tokens(sec["body"])
        path = f"/policies/{pol['slug']}/"
        pages.append({"path": path, "template": "policy.html", "title": pol["title"], "description": pol["description"],
                      "crumbs": [("Home", "/"), (pol["nav_label"], path)], "pol": pol,
                      "og_image": "/static/img/practice-hero-800.jpg", "noindex": pol.get("noindex", False),
                      "schema_fn": lambda p: [org_node(), breadcrumb_node(p["crumbs"])]})
    return pages


def blog_pages():
    """Blog index + posts (content/blog/*.yaml). Article schema; the clinical reviewer stays [[TBC]] until a doctor signs off."""
    idx = load("blog.yaml")
    posts = []
    doctors = {d["id"]: d for d in SITE["doctors"]}
    by_slug = {t["slug"]: t for t in NAV["treatments"]}
    for f in sorted((CONTENT / "blog").glob("*.yaml")):
        b = yaml.safe_load(f.read_text(encoding="utf-8"))
        b["path"] = f"/blog/{b['slug']}/"
        b["author"] = doctors[b.get("author", "dr-nikhil-jain")]
        text = " ".join([b["lead"], b["body"]] + [qa["q"] + " " + qa["a"] for qa in b.get("faqs", [])])
        b["words"] = len(TBC_RE.sub(" ", re.sub(r"<[^>]+>", " ", text)).split())
        b["minutes"] = max(1, round(b["words"] / 200))
        b["related_t"] = [by_slug[x] for x in b.get("related", [])]
        posts.append(b)
    posts.sort(key=lambda b: (str(b["date"]), b["slug"]), reverse=True)
    pages = [{"path": "/blog/", "template": "blog.html", "title": idx["title"], "description": idx["description"],
              "crumbs": [("Home", "/"), ("Blog", "/blog/")], "blog": idx, "posts": posts,
              "og_image": f"/static/img/{posts[0]['image']}-1080.jpg",
              "schema_fn": lambda p: [org_node(), breadcrumb_node(p["crumbs"])]}]
    for b in posts:
        crumbs = [("Home", "/"), ("Blog", "/blog/"), (b["nav_label"], b["path"])]
        author = b["author"]
        url = SITE["domain"] + b["path"]
        art = {"@type": "Article", "@id": url + "#article", "headline": strip_tbc(b["h1"]), "description": b["description"],
               "datePublished": str(b["date"]), "dateModified": str(b.get("updated") or b["date"]),
               "image": SITE["domain"] + f"/static/img/{b['image']}-1080.jpg", "articleSection": b["category"],
               "wordCount": b["words"], "inLanguage": "en-IN", "author": person_node(author),
               "publisher": {"@id": SITE["domain"] + "/#clinic"}, "mainEntityOfPage": {"@id": url}}
        page = {"@type": "WebPage", "@id": url, "url": url, "name": b["title"], "isPartOf": {"@id": SITE["domain"] + "/#website"},
                "breadcrumb": breadcrumb_node(crumbs), "inLanguage": "en-IN"}
        if b.get("reviewed"):  # only once the doctor has actually read and signed off the article
            page.update({"@type": "MedicalWebPage", "reviewedBy": {"@id": person_id(author)}, "lastReviewed": str(b["reviewed"])})
        pages.append({"path": b["path"], "template": "post.html", "title": b["title"], "description": b["description"],
                      "crumbs": crumbs, "post": b, "posts": posts, "og_image": f"/static/img/{b['image']}-1080.jpg",
                      "schema": [org_node(), website_node(), page, art, faq_node(b.get("faqs", []))]})
    return pages


def website_node():
    return {"@type": "WebSite", "@id": SITE["domain"] + "/#website", "url": SITE["domain"] + "/", "name": SITE["name"],
            "publisher": {"@id": SITE["domain"] + "/#clinic"}, "inLanguage": "en-IN"}


def doctor_pages(posts):
    """One profile page per doctor (/doctors/<slug>/): ProfilePage + full Person schema. Portrait = logo placeholder."""
    pages = []
    for d in SITE["doctors"]:
        path = doctor_path(d)
        crumbs = [("Home", "/"), ("The practice", "/the-practice/"), (d["name"], path)]
        prof = {"@type": "ProfilePage", "@id": SITE["domain"] + path, "url": SITE["domain"] + path, "name": f"{d['name']}, {d['role']}",
                "mainEntity": {"@id": person_id(d)}, "isPartOf": {"@id": SITE["domain"] + "/#website"}, "inLanguage": "en-IN",
                "breadcrumb": breadcrumb_node(crumbs)}
        pages.append({"path": path, "template": "doctor.html", "title": d["page_title"], "description": d["description"],
                      "crumbs": crumbs, "doc": d, "doc_posts": [b for b in posts if b["author"]["id"] == d["id"]],
                      "og_image": "/static/img/practice-hero-800.jpg",
                      "schema": [org_node(), website_node(), prof, person_node(d, full=True)]})
    return pages


# ------------------------------------------------------------------------------------------------ checks
def check(pages, rendered):
    errors = []
    titles, descs = {}, {}
    for p in pages:
        if len(p["title"]) > 60:
            errors.append(f"{p['path']}: title {len(p['title'])} > 60 chars")
        if len(p["description"]) > 155:
            errors.append(f"{p['path']}: description {len(p['description'])} > 155 chars")
        if p["title"] in titles:
            errors.append(f"{p['path']}: same title as {titles[p['title']]}")
        if p["description"] in descs:
            errors.append(f"{p['path']}: same description as {descs[p['description']]}")
        titles[p["title"]] = descs[p["description"]] = p["path"]
        out = rendered[p["path"]]
        n_h1 = len(re.findall(r"<h1[\s>]", out))
        if n_h1 != 1:
            errors.append(f"{p['path']}: {n_h1} <h1> elements")
        for img in re.findall(r"<img\b[^>]*>", out):
            if not re.search(r'\balt="', img):
                errors.append(f"{p['path']}: img without alt: {img[:80]}")
        visible = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", "", out, flags=re.S)
        if "[[TBC" in re.sub(r'<mark class="tbc"[^>]*>.*?</mark>|<[^>]+>', "", visible, flags=re.S):
            errors.append(f"{p['path']}: raw [[TBC]] marker in the page (missing | tbc filter)")
        for pat in BANNED:
            if re.search(pat, visible, re.I):
                errors.append(f"{p['path']}: banned word /{pat}/")
    return errors


# ------------------------------------------------------------------------------------------------ main
ASSET_RE = re.compile(r'/static/([A-Za-z0-9_./-]+?\.(?:avif|webp|jpe?g|png|svg|gif|mp4|webm|css|js|woff2|ico))(?:\?v=[0-9a-f]+)?')


def hash_assets(dist):
    """Cache busting (16 Nov 2026): every file under dist/static is renamed to name.<hash8>.ext from its content, and
    every reference in the built HTML, sitemap, CSS and JS is rewritten (src, srcset, preloads, og:image, JSON-LD, font
    URLs inside the CSS). A changed image therefore always gets a new URL, so /static/* can be cached forever and no
    browser keeps an old photo. Leaves first, then CSS/JS (their contents point at fonts and images), then pages."""
    static = dist / "static"
    mapping = {}

    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()[:8]

    def rename(f):
        rel = f.relative_to(static).as_posix()
        stem, ext = rel.rsplit(".", 1)
        new = f"{stem}.{digest(f)}.{ext}"
        f.rename(static / new)
        mapping[rel] = new

    def rewrite(text):
        def sub(m):
            new = mapping.get(m.group(1))
            if new is None:
                raise SystemExit(f"hash_assets: reference to a missing file /static/{m.group(1)}")
            return "/static/" + new
        return ASSET_RE.sub(sub, text)

    files = [f for f in static.rglob("*") if f.is_file()]
    for f in files:
        if f.suffix not in (".css", ".js"):
            rename(f)
    for f in files:
        if f.suffix in (".css", ".js"):
            f.write_text(rewrite(f.read_text(encoding="utf-8")), encoding="utf-8")
            rename(f)
    for f in dist.rglob("*"):
        if f.is_file() and static not in f.parents and f.suffix in (".html", ".xml", ".txt", ".webmanifest", ".json"):
            t = f.read_text(encoding="utf-8")
            n = rewrite(t)
            if n != t:
                f.write_text(n, encoding="utf-8")
    return mapping


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(STATIC, DIST / "static", ignore=shutil.ignore_patterns("media.json"))

    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True, undefined=StrictUndefined,
                      trim_blocks=True, lstrip_blocks=True)
    env.globals.update(review_build=REVIEW_BUILD, site=SITE, nav=NAV, reviews=REVIEWS, picture=picture, preload=preload, video=video, embed=embed, tel=tel, wa=wa, maps_dir=maps_dir,
                       maps_embed=maps_embed, address_one_line=address_one_line, address_full=address_full, hours_rows=hours_rows,
                       client_config=client_config, css_v=asset_version("css/site.css"), js_v=asset_version("js/site.js"), planner_v=asset_version("js/planner.js"),
                       year=TODAY.year, updated=TODAY.strftime("%-d %B %Y") if sys.platform != "win32" else TODAY.strftime("%#d %B %Y"))
    env.filters["tbc"] = tbc
    env.filters["strip_tbc"] = strip_tbc
    env.filters["nicedate"] = lambda d: f"{d.day} {d.strftime('%B %Y')}"

    treatments = {t["t"]["slug"]: t["t"] for t in treatment_pages()}
    env.globals["built_treatments"] = treatments
    env.globals["doctor_path"] = doctor_path
    # Doctor photos: a slot doctor-<id>-card / doctor-<id>-portrait in content/media.yaml switches the logo placeholder
    # for the photo everywhere (home team cards, the practice page, the profile hero, "Also at Arha"). See NEXT-STEPS.md.
    env.globals["has_image"] = lambda name: name in MEDIA["images"]

    blog = blog_pages()
    pages = (static_pages() + treatment_pages() + more_pages() + blog
             + doctor_pages([p["post"] for p in blog if "post" in p]) + international_page())
    rendered = {}
    for p in pages:
        schema = p["schema_fn"](p) if "schema_fn" in p else p.get("schema", [])
        ctx = {"page": p, "schema": jsonld(*schema) if schema else "", "canonical": SITE["domain"] + (p["path"] if p["path"] != "/404.html" else "/"),
               **{k: p[k] for k in ("t", "h", "fp", "pol", "blog", "post", "posts", "i", "plans", "plan_json", "doc", "doc_posts") if k in p}}
        out = mark_tbc_only(env.get_template(p["template"]).render(**ctx))
        rendered[p["path"]] = out
        target = DIST / (p["path"].lstrip("/") or "index.html")
        if p["path"].endswith("/"):
            target = DIST / p["path"].lstrip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(out, encoding="utf-8")

    errors = check(pages, rendered)

    # sitemap, robots, headers, redirects
    built = {p["path"] for p in pages}
    for p in pages:  # internal links must point at a page this build made
        for href in set(re.findall(r'href="(/[^"#?]*)', rendered[p["path"]])):
            if not href.startswith("/static/") and href not in built:
                errors.append(f"{p['path']}: dead link {href}")
    urls = [p for p in pages if not p.get("noindex") and p["path"] != "/404.html"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{SITE['domain']}{p['path']}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>" for p in urls]
    sm.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
    robots = ("User-agent: *\nDisallow: /\n" if SITE["preview"] else "User-agent: *\nAllow: /\n") + f"\nSitemap: {SITE['domain']}/sitemap.xml\n"
    (DIST / "robots.txt").write_text(robots, encoding="utf-8")
    headers = ["/*", "  X-Content-Type-Options: nosniff", "  Referrer-Policy: strict-origin-when-cross-origin",
               "  Permissions-Policy: camera=(), microphone=(), geolocation=()"]
    if SITE["preview"]:
        headers.append("  X-Robots-Tag: noindex, nofollow")
    # every /static file name carries its content hash (hash_assets), so all of it can be cached for a year
    headers += ["", "/static/*", "  Cache-Control: public, max-age=31536000, immutable", ""]
    (DIST / "_headers").write_text("\n".join(headers), encoding="utf-8")
    (DIST / "_redirects").write_text((CONTENT / "redirects.txt").read_text(encoding="utf-8"), encoding="utf-8")

    hashed = hash_assets(DIST)
    print(f"built {len(pages)} pages -> {DIST} ({len(hashed)} static files hashed)")
    if errors:
        print("\n".join("  ERROR " + e for e in errors))
        sys.exit(1)


if __name__ == "__main__":
    main()
