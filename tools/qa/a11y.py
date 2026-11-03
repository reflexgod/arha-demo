"""axe-core (WCAG 2 A/AA, colour contrast included) on every built page, at 390 and 1440 px, with the clock
mocked to a weekday 11:00 IST (open) and a weekday 19:30 IST (closed): the open status in the footer, the menu and
the call bar changes colour with the time. Needs the site served on 8080 and axe-core from Lighthouse's npx cache
(or AXE=path/to/axe.min.js).

Usage: .venv/Scripts/python -I tools/qa/a11y.py [--out file]
Exit code 1 on any violation.
"""
import glob
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402
from console import paths, BASE  # noqa: E402

IST = timezone(timedelta(hours=5, minutes=30))
TIMES = {"open (Tue 11:00 IST)": datetime(2026, 11, 3, 11, 0, tzinfo=IST),
         "closed (Tue 19:30 IST)": datetime(2026, 11, 3, 19, 30, tzinfo=IST)}


def axe_source():
    path = os.environ.get("AXE") or next(iter(sorted(glob.glob(os.path.expanduser(
        "~/AppData/Local/npm-cache/_npx/*/node_modules/axe-core/axe.min.js")))), None)
    if not path:
        raise SystemExit("axe-core not found: run Lighthouse once (tools/qa/lh.sh) or set AXE=")
    return Path(path).read_text(encoding="utf-8")


RUN = """async () => {
  const r = await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']},
    resultTypes: ['violations']});
  return r.violations.map(v => v.id + ' (' + v.nodes.length + '): ' + v.nodes.slice(0, 2).map(n => n.target.join(' ')).join(' | '));
}"""


def main():
    out = open(sys.argv[sys.argv.index("--out") + 1], "w", encoding="utf-8") if "--out" in sys.argv else sys.stdout
    axe, problems, runs = axe_source(), [], 0
    pages = list(paths()) + ["404.html"]
    with sync_playwright() as p:
        b = pw.launch(p)
        for label, when in TIMES.items():
            for w in (390, 1440):
                phone = w < 768
                ctx = b.new_context(viewport={"width": w, "height": 844 if phone else 900}, is_mobile=phone,
                                    has_touch=phone, reduced_motion="reduce")
                ctx.add_init_script("try { sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
                for path in pages:
                    pg = ctx.new_page()
                    pg.clock.set_fixed_time(when)
                    pg.goto(BASE + path, wait_until="load", timeout=60000)
                    pg.wait_for_timeout(300)
                    pg.evaluate("scrollTo(0, document.documentElement.scrollHeight)")
                    pg.wait_for_timeout(200)
                    pg.evaluate("scrollTo(0, 0)")
                    pg.add_script_tag(content=axe)
                    for v in pg.evaluate(RUN):
                        problems.append(f"{label} {w}px /{path}: {v}")
                    runs += 1
                    pg.close()
                ctx.close()
                print(f"{label} {w}px: {len(pages)} pages, {len(problems)} violations so far", file=out, flush=True)
        b.close()
    for x in problems:
        print("FAIL  " + x, file=out)
    print(f"{runs} page runs, {len(problems)} violations", file=out, flush=True)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
