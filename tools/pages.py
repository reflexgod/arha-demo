"""Build the inner pages from the homepage's shared chrome (head, header, menus, footer, lightbox).

Usage: .venv/Scripts/python -I tools/pages.py && .venv/Scripts/python -I tools/cases_markup.py
Each page's <main> lives in tools/pages/<slug>.html and is written relative to the site root;
paths are moved one folder down here. Markers: {{visit}} (tools/pages/_visit.html) {{planner}} and {{pic name | sizes | alt | pos=.. | eager}}.
Re-run after changing the header, menus or footer on the homepage so every page stays identical.

Contact details live only in SITE below. The build writes them into index.html and every page:
every tel:, wa.me and mailto: link (data-contact="emergency" for the emergency line, "fixed" to leave one alone), text marked data-show="<key>", aria-labels marked
data-label="<key>", the Dentist JSON-LD, the call QR code and the JSON config site.js reads.
To change a number: edit SITE, run this script, commit.
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from picture import picture  # noqa: E402
import chrome  # noqa: E402
import finish  # noqa: E402
import home  # noqa: E402
import home_apa  # noqa: E402
import more_pages  # noqa: E402
import technology  # noqa: E402
import treatment_pages  # noqa: E402
import treatments  # noqa: E402
import v4_pages  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
# The Visit section of the inner pages ({{visit}}); the homepage follows apa and has none (V4-APA-LITERAL)
VISIT = ROOT / "tools" / "pages" / "_visit.html"
SITE_URL = "https://arha.svayra.com/"

# The one source of truth for contact details. Placeholders until the clinic confirms (notes/TO-CONFIRM.md).
SITE = {
    "phone": "+91 99755 07714",      # reception
    "whatsapp": "+91 00000 00000",
    "email": "hello@example.com",
    "emergency": "+91 00000 00000",
    # 0 = Sunday ... 6 = Saturday; None = closed. India time. From Riya's answers; Google shows 9:00 AM.
    "hours": [None, ("09:30", "18:30"), ("09:30", "18:30"), ("09:30", "18:30"),
              ("09:30", "18:30"), ("09:30", "18:30"), ("09:30", "18:30")],
    "time_zone": "Asia/Kolkata",
    # Riya, the online assistant. Off until her new webhook is live (the old one answered 404 on 3 Nov 2026).
    # To switch her on: paste the webhook URL here, set riyaEnabled to True, run this script. Nothing else.
    # Off: no launcher, no teaser, no chat code, no webhook URL and no "Ask Riya" button anywhere; those
    # buttons fall back to calling the clinic (<!--flag:riya--> / <!--flag:no-riya--> blocks).
    "riyaEnabled": False,
    "riya_webhook_url": "",
    # Reviews and before/after publicity stay out until the clinic decides (NMC ethical advertising guidelines,
    # National Dental Commission advisory, Oct 2026). Off: no review sections, stars or ratings anywhere, and
    # /our-work/ is not built and not linked (<!--flag:reviews--> and <!--flag:ourwork--> blocks). Content is kept.
    "showReviews": False,
    "showOurWork": False,
    "google_reviews_url": "https://share.google/PzhwgJ9QJMErZnk9R",
    # No Google rating or review count anywhere on the site (Viraaj, 2 Nov 2026)
    "google_rating": "",
    "google_review_count": None,
    # Hero line for the technology USP: from what Arha's own photos show, until the equipment list is confirmed
    "usp_line": "In-house X-ray · Own sterilisation room · Prosthodontist-led",
}

RIYA_SRC = ROOT / "tools" / "riya"


def flags():
    """Which optional parts of the site are published (SITE above)."""
    return {"riya": bool(SITE["riyaEnabled"] and SITE["riya_webhook_url"]),
            "reviews": bool(SITE["showReviews"]), "ourwork": bool(SITE["showOurWork"])}


def apply_flags(html):
    """Keep <!--flag:name-->...<!--/flag:name--> only while the flag is on, and <!--flag:no-name-->...
    <!--/flag:no-name--> only while it is off. Blocks of different names may nest."""
    for name, on in flags().items():
        html = re.sub(rf"<!--flag:{name}-->(.*?)<!--/flag:{name}-->", lambda m: m.group(1) if on else "", html, flags=re.S)
        html = re.sub(rf"<!--flag:no-{name}-->(.*?)<!--/flag:no-{name}-->", lambda m: "" if on else m.group(1), html, flags=re.S)
    return html


DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

PAGES = {
    "before-after": {
        "title": "What we treat | Arha Dental Care, Peddar Road",
        "description": "Common problems we treat at Arha Dental Care, Peddar Road, Mumbai.",
    },
    "book": {
        "title": "Book an Appointment | Arha Dental Care, Peddar Road",
        "description": "Book an in-person consultation at Arha Dental Care on Peddar Road, Mumbai, or a virtual consultation from anywhere, by phone.",
    },
    "404": {
        "title": "Page not found | Arha Dental Care, Peddar Road",
        "description": "This page is not here. Find treatments, book an appointment or call Arha Dental Care on Peddar Road, Mumbai.",
    },
    "emergency": {
        "title": "Emergency Dentist on Peddar Road, South Mumbai | Arha Dental Care",
        "description": "Dental emergency in South Mumbai? Call Arha Dental Care on Peddar Road. What counts as an emergency, and first aid for toothache, swelling, bleeding, broken and knocked-out teeth.",
        "jsonld": {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": "Dental emergencies", "item": SITE_URL + "emergency/"},
            ],
        },
    },
}

SKIP = ("http", "#", "tel:", "mailto:", "data:", "/", "../", "javascript:")


# ---------------------------------------------------------------- contact details
def digits(number):
    return re.sub(r"\D", "", number)


def clock(hhmm):
    h, m = map(int, hhmm.split(":"))
    return f"{(h + 11) % 12 + 1}:{m:02d} {'AM' if h < 12 else 'PM'}"


def hours_text():
    """Display strings for the opening hours (one set of hours on consecutive days, as now)."""
    open_days = [i for i, d in enumerate(SITE["hours"]) if d]
    sets = {SITE["hours"][i] for i in open_days}
    if len(sets) != 1 or open_days != list(range(open_days[0], open_days[-1] + 1)):
        raise SystemExit("hours_text() handles one set of hours on consecutive days; extend it for this schedule")
    (start, end), = sets
    first, last = DAYS[open_days[0]], DAYS[open_days[-1]]
    closed = [DAYS[i] for i, d in enumerate(SITE["hours"]) if not d]
    return {
        "hours-days": f"{first} to {last}",
        "hours-time": f"{clock(start)} to {clock(end)}",
        "hours-closed": " and ".join(closed) + " closed" if closed else "Open every day",
        "hours-short": f"{first[:3]}–{last[:3]} {clock(start)}–{clock(end)}",
    }


def show_values():
    return {
        "phone": SITE["phone"],
        "whatsapp": SITE["whatsapp"],
        "email": SITE["email"],
        "emergency": SITE["emergency"],
        "google-rating": SITE["google_rating"] or "",
        "google-count": f'{SITE["google_review_count"]} reviews' if SITE["google_review_count"] else "",
        # The homepage shows a visible placeholder until the clinic confirms the count (notes/TO-CONFIRM.md)
        "google-count-label": f'{SITE["google_review_count"]} Google reviews' if SITE["google_review_count"] else "Google reviews",
        "usp": SITE["usp_line"],
        **hours_text(),
    }


def client_config():
    """What site.js and Riya need, written into every page as JSON (no extra request)."""
    config = {
        "phone": "" if missing("phone") else SITE["phone"],
        "tel": "" if missing("phone") else "+" + digits(SITE["phone"]),
        "whatsapp": "" if missing("whatsapp") else digits(SITE["whatsapp"]),
        "email": "" if missing("email") else SITE["email"],
        "emergency": "" if missing("emergency") else SITE["emergency"],
        "timeZone": SITE["time_zone"],
        "hours": [list(d) if d else None for d in SITE["hours"]],
        **({"riyaWebhookUrl": SITE["riya_webhook_url"]} if flags()["riya"] else {}),
        **({"googleReviewsUrl": SITE["google_reviews_url"]} if flags()["reviews"] else {}),
    }
    # Leave out what is not set (site.js treats a missing key as empty), so no unused channel is named in a page
    return {k: v for k, v in config.items() if v not in ("", None)}


def apply_site(html):
    """Write SITE into a page. Idempotent: running it again changes nothing."""
    show = show_values()
    tel, emergency_tel = "+" + digits(SITE["phone"]), "+" + digits(SITE["emergency"])

    def fix_tag(m):
        tag = m.group(0)
        if 'data-contact="fixed"' in tag:  # e.g. the public 112 line
            return tag
        number = emergency_tel if 'data-contact="emergency"' in tag else tel
        tag = re.sub(r'href="tel:[^"]*"', f'href="tel:{number}"', tag)
        tag = re.sub(r'(https://wa\.me/)\d*', rf'\g<1>{digits(SITE["whatsapp"])}', tag)
        tag = re.sub(r'href="mailto:[^"?]*', f'href="mailto:{SITE["email"]}', tag)
        if "data-google-reviews" in tag and SITE["google_reviews_url"] and 'href="#"' in tag:
            tag = tag.replace('href="#"', f'href="{SITE["google_reviews_url"]}" target="_blank" rel="noopener"')
        label = re.search(r'data-label="([\w-]+)"', tag)
        if label:
            tag = re.sub(r'(aria-label="[^"]*?, )[^",]*"', rf'\g<1>{show[label.group(1)]}"', tag)
        return tag

    html = re.sub(r"<(?:a|button|img)\b[^>]*>", fix_tag, html)
    html = re.sub(r'(<[^>]*\bdata-show="([\w-]+)"[^>]*>)[^<]*(<)', lambda m: m.group(1) + show[m.group(2)] + m.group(3), html)
    html = re.sub(r'("telephone": )"[^"]*"', rf'\1"{SITE["phone"].replace(" ", "-")}"', html)
    open_days = [DAYS[i] for i, d in enumerate(SITE["hours"]) if d]
    start, end = next(d for d in SITE["hours"] if d)
    html = re.sub(r'("dayOfWeek": )\[[^\]]*\]', lambda m: m.group(1) + json.dumps(open_days), html)
    html = re.sub(r'("opens": )"[^"]*"', rf'\1"{start}"', html)
    html = re.sub(r'("closes": )"[^"]*"', rf'\1"{end}"', html)
    config = f'<script type="application/json" id="site-config">{json.dumps(client_config(), ensure_ascii=False)}</script>'
    if 'id="site-config"' in html:
        html = re.sub(r'<script type="application/json" id="site-config">.*?</script>', lambda m: config, html)
    else:
        html = html.replace('  <script src="assets/js/site.js" defer></script>', f'  {config}\n  <script src="assets/js/site.js" defer></script>')
    return html


# ---------------------------------------------------------------- placeholders are never shown
PLACEHOLDER_NUMBER = re.compile(r"^\+?\s*91[\s0-]*$")


def missing(key):
    """True while a contact detail in SITE is still a placeholder (or empty): +91 00000 00000, hello@example.com."""
    value = (SITE.get(key) or "").strip()
    if key == "email":
        return not value or value.lower().endswith(("@example.com", "@example.org"))
    return not value or bool(PLACEHOLDER_NUMBER.match(value))


def hide_missing(html):
    """Leave out of the page every element that would show a placeholder: tel:, WhatsApp and mailto: links, the
    numbers in text, the call panel and empty rows left behind. Blocks marked <!--if:phone--> ... <!--endif-->
    are kept only when the phone is real, <!--if:no-phone--> ... <!--endif--> only while it is missing (same for
    whatsapp, email, emergency). Everything comes back on its own once SITE has the real value."""
    gone = {k for k in ("phone", "whatsapp", "email", "emergency") if missing(k)}

    def cond(m):
        keep = (m.group(2) in gone) if m.group(1) else (m.group(2) not in gone)
        return m.group(3) if keep else ""
    html = re.sub(r"<!--if:(no-)?(\w+)-->(.*?)<!--endif-->", cond, html, flags=re.S)
    if not gone:
        return html

    def anchor(m):
        open_tag, inner = m.group(1), m.group(2)
        if 'data-contact="fixed"' in open_tag:  # the public 112 line stays
            return m.group(0)
        href = re.search(r'href="([^"]*)"', open_tag)
        href = href.group(1) if href else ""
        if href.startswith("tel:"):
            key = "emergency" if 'data-contact="emergency"' in open_tag else "phone"
        elif "wa.me/" in href:
            key = "whatsapp"
        elif href.startswith("mailto:"):
            key = "email"
        else:
            return m.group(0)
        if key not in gone:
            return m.group(0)
        ask = re.search(r'data-riya-ask="([^"]*)"', open_tag)
        if ask:  # "Ask Riya about this" keeps working without its WhatsApp fallback
            cls = re.search(r'class="([^"]*)"', open_tag)
            return f'<button class="{cls.group(1) if cls else ""}" type="button" data-riya-ask="{ask.group(1)}">{inner}</button>'
        return ""
    html = re.sub(r"(<a\b[^>]*>)(.*?)</a>", anchor, html, flags=re.S)
    keys = "|".join(sorted(gone))
    html = re.sub(rf'(?::\s*)?<span[^>]*\bdata-show="(?:{keys})"[^>]*>[^<]*</span>', "", html)
    if "phone" in gone:
        html = re.sub(r"\n?[ \t]*<!-- Call panel \(laptops\).*?(?=\n  </header>)", "", html, flags=re.S)
        html = re.sub(r'("telephone": )"[^"]*"', r'\1""', html)
    # Rows and wrappers left empty
    for _ in range(2):
        html = re.sub(r"\n?[ \t]*<li>\s*</li>", "", html)
        html = re.sub(r"\n?[ \t]*<div>\s*<dt>[^<]*</dt>\s*<dd>\s*</dd>\s*</div>", "", html)
        html = re.sub(r"\n?[ \t]*<p>\s*(?:·\s*)*</p>", "", html)
        html = re.sub(r'\n?[ \t]*<(p|div) class="[\w-]*__actions[^"]*">\s*</\1>', "", html)
    return html


def call_qr():
    """QR code that dials reception when scanned with a phone (shown in the desktop Call now popover)."""
    if missing("phone"):
        return
    import segno
    segno.make(f"tel:+{digits(SITE['phone'])}", error="m").save(
        str(ROOT / "assets" / "img" / "call-qr.svg"), kind="svg", border=2, omitsize=True,
        dark="#302F2F", light="#FAFAF6", xmldecl=False, nl=False)


def menus(html):
    """Generated blocks between <!-- name:start --> / <!-- name:end --> markers: the Treatments menus and
    Common problems (tools/treatments.py), and the Technology band (tools/technology.py)."""
    blocks = {
        "treatments-menu": treatments.mega_menu,
        "treatments-side": treatments.side_menu,
        "technology-band": technology.band,
        "problems": treatments.problems,
    }
    for name, make in blocks.items():
        html = re.sub(rf"(<!-- {name}:start -->\n).*?(\s*<!-- {name}:end -->)",
                      lambda m: m.group(1) + make().rstrip("\n") + m.group(2), html, flags=re.S)
    return html


# ---------------------------------------------------------------- inner pages
def relocate(html, slug):
    """Move root-relative paths down to the page's folder (one or two levels); links to this page become ./
    The 404 page can be served at any depth, so its paths are absolute from the site root."""
    up = "/" if slug == "404" else "../" * (slug.count("/") + 1)

    def fix_url(u):
        u = u.strip()
        if not u or u.startswith(SKIP):
            return u
        if u in ("./", "."):
            return up
        if u.startswith("./#"):
            return up + u[2:]
        return up + u

    def fix_attr(m):
        attr, val = m.group(1), m.group(2)
        if attr in ("srcset", "imagesrcset"):
            val = ", ".join(" ".join([fix_url(part.split()[0])] + part.split()[1:]) for part in val.split(","))
        else:
            val = fix_url(val)
        return f'{attr}="{val}"'

    html = re.sub(r'\b(href|src|srcset|imagesrcset|data-base|data-src)="([^"]*)"', fix_attr, html)
    html = html.replace(f'href="{up}{slug}/"', 'href="./"').replace(f'href="{up}{slug}/#', 'href="./#')
    return html


def closing_photo(html):
    """The closing band's photograph is chosen by its title; if the page already shows that photograph,
    use the next of Arha's rooms that it does not."""
    m = re.search(r'(statement--close[^\n]*\n[ \t]*\{\{pic )([^ |]+) \| 100vw \| [^|]+ \| pos=[^}]+\}\}', html)
    used = lambda name: f"{{{{pic {name} " in html[:m.start()] or f"assets/img/{name}-" in html[:m.start()]  # noqa: E731
    if not m or not used(m.group(2)):
        return html
    for name, alt, pos in treatment_pages.CLOSING_PHOTOS:
        if not used(name):
            return html[:m.start()] + f"{m.group(1)}{name} | 100vw | {alt} | pos={pos}}}}}" + html[m.end():]
    return html


def expand_pics(html):
    html = closing_photo(html)

    def repl(m):
        indent, body = m.group(1), m.group(2)
        parts = [x.strip() for x in body.split(" | ")]
        name, sizes, alt = parts[:3]
        opts = dict(o.split("=", 1) if "=" in o else (o, True) for o in parts[3:])
        return picture(name, sizes, alt, eager=bool(opts.get("eager")), pos=opts.get("pos"), indent=indent)
    return re.sub(r"^([ \t]*)\{\{pic (.+?)\}\}$", repl, html, flags=re.M)


def build_home(page):
    """index.html is the source of every page's chrome: the header, menu and footer (tools/chrome.py) and the
    homepage's sections (tools/home.py) are written into it; the <head> stays as it is. Riya's launcher
    (tools/riya/launcher.html) is added only while she is switched on."""
    visit = VISIT.read_text(encoding="utf-8")
    start = page.index("  <!-- ===================================================================== HEADER -->")
    riya = (RIYA_SRC / "launcher.html").read_text(encoding="utf-8") if flags()["riya"] else ""
    return (page[:start] + chrome.header() + chrome.side_menu() + "\n" + home_apa.main_html(visit) + "\n"
            + chrome.footer() + "\n" + chrome.call_bar() + "\n" + riya + "</body>\n</html>\n")


def riya_assets():
    """The chat window's code is published only while Riya is on."""
    out = ROOT / "assets" / "js" / "riya.js"
    if flags()["riya"]:
        out.write_bytes((RIYA_SRC / "riya.js").read_bytes())
    elif out.exists():
        out.unlink()


def main():
    index = ROOT / "index.html"
    original = index.read_text(encoding="utf-8")
    home_page = expand_pics(build_home(original))
    home = finishing_head(hide_missing(apply_site(apply_flags(menus(home_page)))), finish.og_image("home", "Specialist dentistry on Peddar Road", "hero-city-poster"))
    finish.favicons()
    if home != original:
        index.write_text(home, encoding="utf-8", newline="\n")
        print("updated index.html (contact details, menus)")
    call_qr()
    riya_assets()

    visit = VISIT.read_text(encoding="utf-8")
    planner = "" if missing("whatsapp") else (ROOT / "tools" / "pages" / "_planner.html").read_text(encoding="utf-8")
    head = home[:home.index("<body>")]
    head = re.sub(r"\s*<!-- Hero poster is the LCP image[^\n]*\n(?:[ \t]*<link rel=\"preload\" as=\"image\"[^>]*>\n)+", "\n", head)
    # Inner pages carry a class: their stock smiles and faces render in black and white (site.css)
    top = home[home.index("<body>"):home.index('  <main id="main"')].replace("<body>", '<body class="page-inner">', 1)
    bottom = home[home.index("  </main>") + len("  </main>\n"):]

    pages = dict(PAGES)
    for slug, meta, main_html in v4_pages.all_pages(SITE_URL, visit):
        if slug.split("/")[0] == "our-work" and not flags()["ourwork"]:
            continue
        pages[slug] = {**meta, "main": main_html}
    if not flags()["ourwork"] and (ROOT / "our-work").exists():  # not published: take the old build away
        import shutil
        shutil.rmtree(ROOT / "our-work")
    for slug, meta in pages.items():
        h = re.sub(r"<title>.*?</title>", f"<title>{meta['title']}</title>", head)
        h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{meta["description"]}">', h)
        h = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{meta["description"]}">', h)
        h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{meta["title"]}">', h)
        h = h.replace(f'href="{SITE_URL}"', f'href="{SITE_URL}{slug}/"').replace(f'content="{SITE_URL}"', f'content="{SITE_URL}{slug}/"')
        if slug in v4_pages.moved():  # the old before/after pages forward to What we treat
            to = v4_pages.moved()[slug]
            h = h.replace(f'href="{SITE_URL}{slug}/"', f'href="{SITE_URL}{to}"')
            h = h.replace("</head>", f'  <meta http-equiv="refresh" content="0; url={"../" * (slug.count("/") + 1)}{to}">\n</head>')
        if slug == "404":  # a missing page has no address of its own
            h = re.sub(r'\s*<link rel="canonical"[^>]*>', "", h)
            h = re.sub(r'\s*<meta property="og:url"[^>]*>', "", h)
        blocks = meta.get("jsonld") or []
        for block in blocks if isinstance(blocks, list) else [blocks]:
            h = h.replace("</head>", '  <script type="application/ld+json">\n  ' + json.dumps(block, indent=2, ensure_ascii=False).replace("\n", "\n  ") + "\n  </script>\n</head>")
        main_html = meta.get("main") or (ROOT / "tools" / "pages" / f"{slug}.html").read_text(encoding="utf-8")
        main_html = main_html.replace("{{problems}}", treatments.problems())
        # The page's own photograph (its first one) for its Open Graph image
        first = re.search(r"\{\{pic ([\w-]+)|assets/img/([\w-]+?)-\d+\.(?:jpg|webp|avif)", main_html)
        photo = (first.group(1) or first.group(2)) if first else "hero-city-poster"
        main_html = expand_pics(main_html.replace("{{visit}}", visit).replace("{{planner}}", planner))
        if slug == "emergency":  # emergency help must be readable at once: no scroll reveals on this page
            main_html = re.sub(r'(class="[^"]*?)\s*\breveal(?![\w-])', r'\1', main_html)
        og = finish.og_image(slug.replace("/", "-"), html.unescape(meta["title"].split(" | ")[0]), photo)
        page = relocate(hide_missing(apply_site(apply_flags(finishing_head(h, og) + top + main_html + bottom))), slug)
        out = ROOT / ("." if slug == "404" else slug)
        out.mkdir(parents=True, exist_ok=True)
        name = "404.html" if slug == "404" else "index.html"
        (out / name).write_text(page, encoding="utf-8", newline="\n")
        print(f"wrote {slug}/{name}  {len(page) // 1024} KB")


def finishing_head(head, og):
    """Per-page Open Graph image (1200 x 630) and the full favicon set in the <head>."""
    head = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{SITE_URL}{og}">', head)
    head = re.sub(r'<meta property="og:image:width" content="\d+">', '<meta property="og:image:width" content="1200">', head)
    head = re.sub(r'<meta property="og:image:height" content="\d+">', '<meta property="og:image:height" content="630">', head)
    if 'rel="manifest"' not in head:
        head = head.replace('  <link rel="apple-touch-icon" href="apple-touch-icon.png">',
                            '  <link rel="apple-touch-icon" href="apple-touch-icon.png">\n  <link rel="manifest" href="site.webmanifest">', 1)
    return head


if __name__ == "__main__":
    main()
