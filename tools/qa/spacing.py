"""v4 feedback 8: every text link or CTA sits at least 32px below the text above it.
Measures, on every page at 1440 and 390, each block-level link (.link, .cta, .text-link) against the
nearest text block above it in the same column. Inline links inside a sentence, and the header, menus
and footer, are not counted. Usage: spacing.py SCRATCH [paths...]"""
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
from pw import launch, BASE as B  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

ROOT = Path(r"C:\Users\viraa\IdeaProjects\arha demo")
JS = r"""() => {
  document.querySelectorAll('.reveal').forEach(e => e.classList.add('is-in'));
  const out = [];
  const visible = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.opacity !== '0' && !el.closest('[hidden]'); };
  const skip = 'header, footer, nav, .side-menu, .dropdown, .call-pop, .riya, [class*="riya"], .call-bar, .drag__ui, .brings__items, .problem-links__list, .more-cases__list, .techlist__list, .fmenu, .crumbs, .work-filter, .lightbox, .xfade__tabs, [role=tablist]';
  const texts = [...document.querySelectorAll('main p, main h1, main h2, main h3, main h4, main dd, main blockquote, main figcaption, main legend')]
    .filter(t => visible(t) && !t.querySelector('a.link, a.cta, .text-link') && !t.closest('a') && t.textContent.trim());
  document.querySelectorAll('main a.link, main a.cta, main button.cta, main .text-link').forEach((a) => {
    if (!visible(a) || a.closest(skip)) return;
    const p = a.parentElement;
    const own = [...p.childNodes].filter(n => !(n.nodeType === 1 && n.matches('a, button, br'))).map(n => n.textContent).join('').trim();
    if (p.tagName === 'P' && own) return;   // inline, inside a sentence (a row of links alone is measured)
    if (a.closest('li') && !a.closest('li').querySelector('p, h3')) return;          // a list of links
    const r = a.getBoundingClientRect();
    let best = null;
    texts.forEach((t) => {
      if (t.contains(a)) return;
      const q = t.getBoundingClientRect();
      if (q.bottom > r.top + 2 || q.right <= r.left || q.left >= r.right) return;
      if (!best || q.bottom > best.q.bottom) best = { t, q };
    });
    if (!best) return;
    const gap = r.top - best.q.bottom;
    if (gap < 31.5 && gap > -2) out.push({ link: a.textContent.trim().slice(0, 40), above: best.t.tagName + ': ' + best.t.textContent.trim().slice(0, 40), gap: Math.round(gap * 10) / 10, cls: (a.className || '').toString().slice(0, 30), where: (a.closest('section, article, [class]') || {}).className.toString().slice(0, 40) });
  });
  return out;
}"""


def paths():
    out = [""]
    for p in sorted(ROOT.rglob("index.html")):
        rel = p.parent.relative_to(ROOT).as_posix()
        if rel.split("/")[0] in ("review", ".venv", "tools", "src-assets") or rel in (".", "before-after"):
            continue
        out.append(rel + "/")
    return out


if __name__ == "__main__":
    todo = sys.argv[2:] or paths()
    found = []
    with sync_playwright() as p:
        br = launch(p)
        for w, h in ((1440, 900), (390, 844)):
            ctx = br.new_context(viewport={"width": w, "height": h}, is_mobile=w < 600, has_touch=w < 600)
            pg = ctx.new_page()
            for path in todo:
                pg.goto(B + path, wait_until="domcontentloaded"); pg.wait_for_timeout(250)
                pg.add_style_tag(content="*, *::before, *::after { transition: none !important; animation: none !important; }")
                for v in pg.evaluate(JS):
                    found.append({"vp": w, "page": path or "home", **v})
            ctx.close()
        br.close()
    for f in found:
        print(f"{f['vp']:>4} {f['page']:<32} {f['gap']:>5}px  {f['link']:<34} under {f['above']:<46} [{f['where']}]")
    print(len(found), "links closer than 32px")
    (Path(sys.argv[1]) / "spacing.json").write_text(json.dumps(found, indent=1))
