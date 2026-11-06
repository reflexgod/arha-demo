"""The v5 type rules on every built page, at 390 and 1440 (starts its own server). Prints problems, and the rhythm of section tones.

 - H1, H2 (headlines): Instrument Serif, sentence case, -0.01em, line-height about 1.1, on the scale. The footer column labels are the one exception.
 - H3: Jost 600, on the scale. D-DIN only at 15 px or below. Anything in capitals is D-DIN, and at 15 px or below.
 - Long headlines on 390: no word alone on its last line, no overflow, and how many lines (--lines prints them).

Usage: .venv/Scripts/python tools/qa/type_audit.py <port> [--lines] [--tones]
"""
import collections
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402

PORT = int(sys.argv[1])
BASE = f"http://127.0.0.1:{PORT}/"
ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {"review", "notes", ".venv", "src-assets", "tools", "assets", "before-after"}
QUIET = "try{sessionStorage.setItem('arha-intro','1');sessionStorage.setItem('riya-bubble','1')}catch(e){}"

PAGES = [""] + sorted(str(p.parent.relative_to(ROOT)).replace("\\", "/") + "/" for p in ROOT.rglob("index.html")
                      if p.parent != ROOT and not (set(p.relative_to(ROOT).parts) & SKIP_DIRS))

AUDIT = """(w) => {
  const out = {bad: [], lines: []};
  const name = (e) => e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className ? '.' + e.className.trim().split(/\\s+/)[0] : '');
  const seen = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden'; };
  for (const e of document.querySelectorAll('h1, h2, h3')) {
    if (e.closest('[hidden]') || !seen(e)) continue;
    const s = getComputedStyle(e), fam = s.fontFamily, size = parseFloat(s.fontSize), lh = parseFloat(s.lineHeight) / size, ls = parseFloat(s.letterSpacing) / size || 0;
    const tag = e.tagName.toLowerCase();
    if (e.closest('.footer__cols')) continue;
    if (tag !== 'h3') {
      if (!fam.includes('Instrument Serif')) out.bad.push(`${tag} family ${fam.slice(0, 20)}: ${e.textContent.trim().slice(0, 40)}`);
      if (s.textTransform !== 'none') out.bad.push(`${tag} ${s.textTransform}: ${e.textContent.trim().slice(0, 40)}`);
      if (Math.abs(lh - 1.1) > .03) out.bad.push(`${tag} line-height ${lh.toFixed(2)}: ${e.textContent.trim().slice(0, 40)}`);
      if (Math.abs(ls + .01) > .004) out.bad.push(`${tag} letter-spacing ${ls.toFixed(3)}em: ${e.textContent.trim().slice(0, 40)}`);
    } else {
      if (!fam.includes('Jost')) out.bad.push(`h3 family ${fam.slice(0, 20)}: ${e.textContent.trim().slice(0, 40)}`);
      if (s.textTransform !== 'none') out.bad.push(`h3 ${s.textTransform}: ${e.textContent.trim().slice(0, 40)}`);
    }
    out.lines.push({tag, size: Math.round(size * 10) / 10, text: e.textContent.trim().replace(/\\s+/g, ' ')});
    // words per line, for headlines
    if (tag !== 'h3') {
      const range = document.createRange(), walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT), rows = new Map();
      for (let n; (n = walker.nextNode());) {
        const re = /\\S+/g; let m;
        while ((m = re.exec(n.textContent))) { range.setStart(n, m.index); range.setEnd(n, m.index + m[0].length);
          const r = range.getClientRects()[0]; if (!r) continue; const k = Math.round(r.top); rows.set(k, (rows.get(k) || []).concat(m[0]));
          if (r.right > w - 8) out.bad.push(`${tag} word past the edge: ${m[0]}`); }
      }
      const list = [...rows.keys()].sort((a, b) => a - b).map((k) => rows.get(k).join(' '));
      out.lines[out.lines.length - 1].rows = list;
      if (list.length > 1 && list[list.length - 1].split(' ').length === 1 && list[list.length - 1].length < 9) out.bad.push(`${tag} short last line "${list.join(' / ')}"`);
      if (list.some((x) => x.length && !x.includes(' ') && list.length > 3)) out.bad.push(`${tag} one word on a row "${list.join(' / ')}"`);
    }
  }
  // anything in capitals is a small label in D-DIN; D-DIN is only ever a small label
  const flagged = new Set();
  for (const e of document.querySelectorAll('body *')) {
    if (!e.childNodes.length || e.closest('[hidden], .visually-hidden, script, style, noscript, .riya, .riya-launcher, .riya-bubble')) continue;
    const text = [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    if (!text || !seen(e)) continue;
    const s = getComputedStyle(e), size = parseFloat(s.fontSize), din = s.fontFamily.includes('D-DIN');
    if (s.textTransform === 'uppercase' && !din) flagged.add(`capitals not D-DIN: ${name(e)} ${size}px`);
    if (din && size > 15) flagged.add(`D-DIN too big: ${name(e)} ${size}px`);
    if (din && s.textTransform !== 'uppercase' && !/num|hotspot|avatar|spot/.test(String(e.className))) flagged.add(`D-DIN not capitals: ${name(e)} ${size}px`);
  }
  out.bad.push(...flagged);
  return out;
}"""

TONES = """() => {
  const tone = (c) => ({'rgb(250, 250, 246)': 'paper', 'rgb(231, 227, 220)': 'stone', 'rgb(48, 47, 47)': 'charcoal', 'rgba(0, 0, 0, 0)': '-'}[c] || c);
  return [...document.querySelectorAll('main > section, main > nav, main > div')].filter((e) => e.getBoundingClientRect().height > 0).map((e) => {
    const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    return `${String(e.className).split(' ').filter((c) => c !== 'section' && !c.startsWith('reveal') && c !== 'is-in' && c !== 'is-armed').slice(0, 2).join('.')}:${tone(s.backgroundColor)}:${Math.round(parseFloat(s.paddingTop))}/${Math.round(parseFloat(s.paddingBottom))}`;
  });
}"""


def main():
    server = subprocess.Popen([sys.executable, "-I", str(Path(__file__).parent / "gzserve.py"), str(PORT)])
    bad = collections.Counter()
    where = {}
    longest = []
    try:
        with sync_playwright() as p:
            b = pw.launch(p)
            for w, h, phone in [(390, 844, True), (1440, 900, False)]:
                ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=phone, has_touch=phone)
                ctx.add_init_script(QUIET)
                for path in PAGES:
                    pg = ctx.new_page()
                    pg.goto(BASE + path, wait_until="load", timeout=60000)
                    if pg.url.rstrip("/") != (BASE + path).rstrip("/"):
                        pg.close()
                        continue
                    pg.evaluate("document.fonts.ready")
                    r = pg.evaluate(AUDIT, w)
                    for x in r["bad"]:
                        bad[f"{w}: {x}"] += 1
                        where.setdefault(f"{w}: {x}", "/" + path)
                    if w == 390:
                        longest += [(len(x["text"]), x["tag"], x["size"], " / ".join(x.get("rows", []))) for x in r["lines"] if x["tag"] != "h3"]
                    if "--tones" in sys.argv and w == 1440:
                        print("/" + path, " > ".join(pg.evaluate(TONES)))
                    pg.close()
                ctx.close()
            b.close()
    finally:
        server.kill()
    for k, n in bad.most_common():
        print(f"{n:3}x {k}   (first: {where[k]})")
    print(f"{len(bad)} kinds of problem on {len(PAGES)} pages")
    if "--lines" in sys.argv:
        for row in sorted(set(longest), reverse=True)[:40]:
            print(row[1], row[2], row[3])


if __name__ == "__main__":
    main()
