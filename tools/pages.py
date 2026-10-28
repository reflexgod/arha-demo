"""Build the inner pages from the homepage's shared chrome (head, header, menus, footer, lightbox).

Usage: .venv/Scripts/python -I tools/pages.py && .venv/Scripts/python -I tools/cases_markup.py
Each page's <main> lives in tools/pages/<slug>.html and is written relative to the site root;
paths are moved one folder down here. Markers: {{visit}} (the homepage's Visit section) {{planner}} and {{pic name | sizes | alt | pos=.. | eager}}.
Re-run after changing the header, menus or footer on the homepage so every page stays identical.

Contact details live only in SITE below. The build writes them into index.html and every page:
every tel:, wa.me and mailto: link (data-contact="emergency" for the emergency line, "fixed" to leave one alone), text marked data-show="<key>", aria-labels marked
data-label="<key>", the Dentist JSON-LD, the call QR code and the JSON config site.js reads.
To change a number: edit SITE, run this script, commit.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from picture import picture  # noqa: E402
import more_pages  # noqa: E402
import technology  # noqa: E402
import treatment_pages  # noqa: E402
import treatments  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://arha.svayra.com/"

# The one source of truth for contact details. Placeholders until the clinic confirms (notes/TO-CONFIRM.md).
SITE = {
    "phone": "+91 00000 00000",      # reception
    "whatsapp": "+91 00000 00000",
    "email": "hello@example.com",
    "emergency": "+91 00000 00000",
    # 0 = Sunday ... 6 = Saturday; None = closed. India time. From Riya's answers; Google shows 9:00 AM.
    "hours": [None, ("09:30", "18:30"), ("09:30", "18:30"), ("09:30", "18:30"),
              ("09:30", "18:30"), ("09:30", "18:30"), ("09:30", "18:30")],
    "time_zone": "Asia/Kolkata",
    "riya_webhook_url": "https://viraaj19.app.n8n.cloud/webhook/ac85a7b5-2995-4909-9988-614bba42debb/chat",
    "google_reviews_url": "https://share.google/PzhwgJ9QJMErZnk9R",
    # Google rating strip: only the real figures. The demo has shown 5.0; the count is unknown (None hides it).
    "google_rating": "5.0",
    "google_review_count": None,
    # Hero line for the technology USP: from what Arha's own photos show, until the equipment list is confirmed
    "usp_line": "In-house X-ray · Own sterilisation room · Prosthodontist-led",
}

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

PAGES = {
    "before-after": {
        "title": "Before &amp; After | Arha Dental Care, Peddar Road",
        "description": "Before and after results from Arha Dental Care on Peddar Road, Mumbai: dental implants, full mouth rehabilitation, veneers and aligners.",
    },
    "book": {
        "title": "Book a Consultation | Arha Dental Care, Peddar Road",
        "description": "Book an in-person consultation at Arha Dental Care on Peddar Road, Mumbai, or a virtual consultation from anywhere, by WhatsApp or phone.",
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
        "usp": SITE["usp_line"],
        **hours_text(),
    }


def client_config():
    """What site.js and Riya need, written into every page as JSON (no extra request)."""
    return {
        "phone": SITE["phone"],
        "tel": "+" + digits(SITE["phone"]),
        "whatsapp": digits(SITE["whatsapp"]),
        "email": SITE["email"],
        "emergency": SITE["emergency"],
        "timeZone": SITE["time_zone"],
        "hours": [list(d) if d else None for d in SITE["hours"]],
        "riyaWebhookUrl": SITE["riya_webhook_url"],
        "googleReviewsUrl": SITE["google_reviews_url"],
    }


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


def call_qr():
    """QR code that dials reception when scanned with a phone (shown in the desktop Call now popover)."""
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
    """Move root-relative paths down to the page's folder (one or two levels); links to this page become ./"""
    up = "../" * (slug.count("/") + 1)

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


def expand_pics(html):
    def repl(m):
        indent, body = m.group(1), m.group(2)
        parts = [x.strip() for x in body.split(" | ")]
        name, sizes, alt = parts[:3]
        opts = dict(o.split("=", 1) if "=" in o else (o, True) for o in parts[3:])
        return picture(name, sizes, alt, eager=bool(opts.get("eager")), pos=opts.get("pos"), indent=indent)
    return re.sub(r"^([ \t]*)\{\{pic (.+?)\}\}$", repl, html, flags=re.M)


def main():
    index = ROOT / "index.html"
    original = index.read_text(encoding="utf-8")
    home = apply_site(menus(original))
    if home != original:
        index.write_text(home, encoding="utf-8")
        print("updated index.html (contact details, menus)")
    call_qr()

    visit = re.search(r"    <!-- =+ 10\. VISIT US -->\n.*?</section>\n", home, flags=re.S).group(0)
    planner = (ROOT / "tools" / "pages" / "_planner.html").read_text(encoding="utf-8")
    head = home[:home.index("<body>")]
    head = re.sub(r"\s*<!-- Hero poster is the LCP image.*?fetchpriority=\"high\">\n", "\n", head, flags=re.S)
    top = home[home.index("<body>"):home.index('  <main id="main"')]
    bottom = home[home.index("  </main>") + len("  </main>\n"):]

    pages = dict(PAGES)
    for slug, meta, main_html in treatment_pages.all_pages(SITE_URL, treatments.problems()):
        pages[slug] = {**meta, "main": main_html}
    for slug, meta, main_html in more_pages.all_pages(SITE_URL, visit):
        pages[slug] = {**meta, "main": main_html}
    for slug, meta in pages.items():
        h = re.sub(r"<title>.*?</title>", f"<title>{meta['title']}</title>", head)
        h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{meta["description"]}">', h)
        h = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{meta["description"]}">', h)
        h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{meta["title"]}">', h)
        h = h.replace(f'href="{SITE_URL}"', f'href="{SITE_URL}{slug}/"').replace(f'content="{SITE_URL}"', f'content="{SITE_URL}{slug}/"')
        blocks = meta.get("jsonld") or []
        for block in blocks if isinstance(blocks, list) else [blocks]:
            h = h.replace("</head>", '  <script type="application/ld+json">\n  ' + json.dumps(block, indent=2, ensure_ascii=False).replace("\n", "\n  ") + "\n  </script>\n</head>")
        main_html = meta.get("main") or (ROOT / "tools" / "pages" / f"{slug}.html").read_text(encoding="utf-8")
        main_html = main_html.replace("{{problems}}", treatments.problems())
        main_html = expand_pics(main_html.replace("{{visit}}", visit).replace("{{planner}}", planner))
        page = relocate(apply_site(h + top + main_html + bottom), slug)
        out = ROOT / slug
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(page, encoding="utf-8")
        print(f"wrote {slug}/index.html  {len(page) // 1024} KB")


if __name__ == "__main__":
    main()
