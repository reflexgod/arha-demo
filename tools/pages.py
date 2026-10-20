"""Build the inner pages from the homepage's shared chrome (head, header, menus, footer, lightbox).

Usage: .venv/Scripts/python -I tools/pages.py && .venv/Scripts/python -I tools/cases_markup.py
Each page's <main> lives in tools/pages/<slug>.html and is written relative to the site root;
paths are moved one folder down here. Markers: {{mark}} (bronze emblem divider), {{watermark}}
(band emblem), {{visit}} (the homepage's Visit section) and {{pic name | sizes | alt | pos=.. | eager}}.
Re-run after changing the header, menus or footer on the homepage so every page stays identical.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from picture import picture  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://arha.viraajautomates.tech/"

PAGES = {
    "before-after": {
        "title": "Before &amp; After | Arha Dental Care, Peddar Road",
        "description": "Before and after results from Arha Dental Care on Peddar Road, Mumbai: dental implants, full mouth rehabilitation, veneers and aligners.",
    },
    "dental-implants": {
        "title": "Dental Implants in South Mumbai | Arha Dental Care, Peddar Road",
        "description": "Prosthodontist-led dental implants on Peddar Road, Mumbai. How implants work, who they suit, the treatment journey and answers to common questions.",
        "jsonld": {
            "@context": "https://schema.org",
            "@type": "MedicalProcedure",
            "name": "Dental implants",
            "alternateName": "Dental implant treatment",
            "procedureType": "https://schema.org/SurgicalProcedure",
            "bodyLocation": "Jaw and teeth",
            "description": "Replacement of missing teeth with implants that support a crown, bridge or denture, planned by a prosthodontist.",
            "howPerformed": "Consultation and scans, treatment planning, implant placement under local anaesthetic, healing, then the final tooth is fitted.",
            "preparation": "A consultation with an examination and scans.",
            "followup": "Regular reviews and professional cleaning.",
            "url": SITE + "dental-implants/",
        },
    },
    "book": {
        "title": "Book a Consultation | Arha Dental Care, Peddar Road",
        "description": "Book an in-person consultation at Arha Dental Care on Peddar Road, Mumbai, or a virtual consultation from anywhere, by WhatsApp or phone.",
    },
}

SKIP = ("http", "#", "tel:", "mailto:", "data:", "/", "../", "javascript:")


def relocate(html, slug):
    """Move root-relative paths one folder down; links to this page become ./"""
    def fix_url(u):
        u = u.strip()
        if not u or u.startswith(SKIP):
            return u
        if u in ("./", "."):
            return "../"
        return "../" + u

    def fix_attr(m):
        attr, val = m.group(1), m.group(2)
        if attr in ("srcset", "imagesrcset"):
            val = ", ".join(" ".join([fix_url(part.split()[0])] + part.split()[1:]) for part in val.split(","))
        else:
            val = fix_url(val)
        return f'{attr}="{val}"'

    html = re.sub(r'\b(href|src|srcset|imagesrcset|data-base)="([^"]*)"', fix_attr, html)
    html = html.replace(f'href="../{slug}/"', 'href="./"').replace(f'href="../{slug}/#', 'href="./#')
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
    import json
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    watermark = re.search(r'<svg class="band__mark".*?</svg>', home).group(0)
    visit = re.search(r"    <!-- =+ 10\. VISIT US -->\n.*?</section>\n", home, flags=re.S).group(0)
    head = home[:home.index("<body>")]
    head = re.sub(r"\s*<!-- Hero poster is the LCP image.*?fetchpriority=\"high\">\n", "\n", head, flags=re.S)
    top = home[home.index("<body>"):home.index('  <main id="main"')]
    bottom = home[home.index("  </main>") + len("  </main>\n"):]

    for slug, meta in PAGES.items():
        h = re.sub(r"<title>.*?</title>", f"<title>{meta['title']}</title>", head)
        h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{meta["description"]}">', h)
        h = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{meta["description"]}">', h)
        h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{meta["title"]}">', h)
        h = h.replace(f'href="{SITE}"', f'href="{SITE}{slug}/"').replace(f'content="{SITE}"', f'content="{SITE}{slug}/"')
        if "jsonld" in meta:
            h = h.replace("</head>", '  <script type="application/ld+json">\n  ' + json.dumps(meta["jsonld"], indent=2).replace("\n", "\n  ") + "\n  </script>\n</head>")
        main_html = (ROOT / "tools" / "pages" / f"{slug}.html").read_text(encoding="utf-8")
        main_html = expand_pics(main_html.replace("{{watermark}}", watermark).replace("{{visit}}", visit))
        page = relocate(h + top + main_html + bottom, slug)
        out = ROOT / slug
        out.mkdir(exist_ok=True)
        (out / "index.html").write_text(page, encoding="utf-8")
        print(f"wrote {slug}/index.html  {len(page) // 1024} KB")


if __name__ == "__main__":
    main()
