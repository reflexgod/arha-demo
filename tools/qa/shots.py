"""Full-page shots of every page at several widths + a card-row alignment audit.

Usage: python shots.py BASEURL OUTDIR [--widths 1440,1280,768,390] [--only /,/blog/] [--noshots]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\viraa\IdeaProjects\arha demo\tools\qa")
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402

PAGES = """/ /blog/ /blog/are-dental-implants-right-for-me/ /blog/dental-implant-aftercare/ /blog/dental-implant-cost-in-mumbai/
/blog/dental-implant-timeline/ /blog/dental-implant-vs-bridge/ /blog/is-root-canal-treatment-painful/
/blog/when-should-a-child-first-see-a-dentist/ /contact/ /doctors/dr-nikhil-v-jain/ /doctors/dr-vasant-p-jain/
/emergency-dentist-south-mumbai/ /for-patients/ /international-patients/ /policies/privacy/ /referrals/ /the-practice/
/treatments/ /treatments/aligners/ /treatments/childrens-orthodontics/ /treatments/crowns-bridges-full-mouth-rehabilitation/
/treatments/dental-implants/ /treatments/dentures/ /treatments/gum-care/ /treatments/kids-dentistry/ /treatments/missing-teeth/
/treatments/root-canal-treatment/ /treatments/smile-design/ /treatments/teeth-whitening/""".split()

PREP = """async () => {
  document.querySelectorAll('img[loading=lazy]').forEach((i) => { i.loading = 'eager'; });
  for (let y = 0; y < document.body.scrollHeight; y += 700) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 40)); }
  window.scrollTo(0, 0);
  document.querySelectorAll('[data-reveal]').forEach((el) => el.classList.add('rv', 'is-in'));
  await Promise.all([...document.images].map((i) => i.decode().catch(() => {})));
  await new Promise((r) => setTimeout(r, 300));
}"""

AUDIT = """() => {
  const vis = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const out = [];
  const path = (e) => { let s = []; while (e && e !== document.body) { s.unshift(e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\\s+/).join('.') : '')); e = e.parentElement; } return s.slice(-3).join(' > '); };
  for (const g of document.querySelectorAll('main *')) {
    const cs = getComputedStyle(g);
    if (!(cs.display === 'grid' || (cs.display === 'flex' && cs.flexDirection.startsWith('row')))) continue;
    const kids = [...g.children].filter(vis).filter((k) => k.querySelector('h2,h3,h4') && k.querySelector('img,video,.vid'));
    if (kids.length < 2) continue;
    const rows = {};
    for (const k of kids) { const t = Math.round(k.getBoundingClientRect().top + scrollY); (rows[t] = rows[t] || []).push(k); }
    for (const [t, ks] of Object.entries(rows)) {
      if (ks.length < 2) continue;
      const m = ks.map((k) => { const x = k.querySelector('picture,img,.vid,video'); return Math.round(x.getBoundingClientRect().height); });
      const h = ks.map((k) => Math.round(k.querySelector('h2,h3,h4').getBoundingClientRect().top - k.getBoundingClientRect().top));
      const b = ks.map((k) => { const x = [...k.querySelectorAll('a.btn,a.tlink')].pop(); return x ? Math.round(x.getBoundingClientRect().top - k.getBoundingClientRect().top) : null; });
      const spread = (a) => { const v = a.filter((x) => x !== null); return v.length ? Math.max(...v) - Math.min(...v) : 0; };
      if (spread(m) > 2 || spread(h) > 2 || spread(b) > 2) out.push({grid: path(g), y: +t, media: m, heading: h, button: b});
    }
  }
  const over = document.documentElement.scrollWidth > innerWidth + 1;
  return {issues: out, overflow: over};
}"""


def main():
    base, out = sys.argv[1].rstrip("/"), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    widths = [int(w) for w in (sys.argv[sys.argv.index("--widths") + 1] if "--widths" in sys.argv else "1440,1280,768,390").split(",")]
    pages = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else PAGES
    shots = "--noshots" not in sys.argv
    report = {}
    with sync_playwright() as p:
        b = pw.launch(p)
        for w in widths:
            ctx = b.new_context(viewport={"width": w, "height": 900 if w > 600 else 844})
            ctx.add_init_script("try{localStorage.setItem('arha-consent', JSON.stringify({analytics:false,ts:1}));}catch(e){}")
            pg = ctx.new_page()
            for path in pages:
                pg.goto(base + path, wait_until="networkidle")
                pg.add_style_tag(content="[data-reveal]{opacity:1!important;transform:none!important;transition:none!important} .cookie,.cookies,#cookie{display:none!important}")
                pg.evaluate(PREP)
                pg.wait_for_timeout(250)
                a = pg.evaluate(AUDIT)
                if a["issues"] or a["overflow"]:
                    report[f"{path} @{w}"] = a
                if shots:
                    name = (path.strip("/").replace("/", "_") or "home") + f"-{w}.png"
                    pg.screenshot(path=str(out / name), full_page=True)
            ctx.close()
            print("done", w)
        b.close()
    (out / "audit.json").write_text(json.dumps(report, indent=1))
    for k, v in report.items():
        print(k, "OVERFLOW" if v["overflow"] else "")
        for i in v["issues"]:
            print("   ", i)


if __name__ == "__main__":
    main()
