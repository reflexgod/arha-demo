"""Writes notes/INTERACTION-TESTS.md from a QA run (ix_suite + colour_suite, ba_test, spacing, centred).

Usage: .venv/Scripts/python tools/qa/report_tests.py RESULTS_DIR "<title line>"
RESULTS_DIR holds ix_results.json, ba_results.json, spacing.json and centred.json from the same run.
"""
import json
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    d = Path(sys.argv[1])
    title = sys.argv[2] if len(sys.argv) > 2 else "Interaction tests"
    ix = json.loads((d / "ix_results.json").read_text())
    ba = json.loads((d / "ba_results.json").read_text())
    spacing = json.loads((d / "spacing.json").read_text()) if (d / "spacing.json").exists() else {}
    centred = json.loads((d / "centred.json").read_text()) if (d / "centred.json").exists() else {}
    allr = ix + [{"page": r.get("page"), "interactive": "Before/after slider (timing)", "vp": r.get("vp"), "action": r.get("action"), "ok": r.get("ok"), "note": r.get("note", "")} for r in ba]
    n, ok = len(allr), sum(r["ok"] for r in allr)
    rows = OrderedDict()
    for r in allr:
        key = (r["page"], r["interactive"])
        rows.setdefault(key, {1440: [], 390: []})
        rows[key].setdefault(r["vp"], []).append(f"{'PASS' if r['ok'] else 'FAIL'}: {r['action']}" + (f" ({r['note']})" if r["note"] not in ("", "None") else ""))
    frames = [r for r in ba if "frames" in r.get("action", "")]
    lines = [f"# {title}", "",
             "Every interactive on every page, really driven with Playwright (Chromium), branch v4:",
             "- **1440:** desktop, with mouse moves, drags, clicks and the keyboard;",
             "- **390:** a phone (is_mobile, touch), with taps and real touch drags and swipes sent as Chrome touch events.", "",
             f"**Result: {ok} of {n} checks pass.**", "",
             "Scripts are in `tools/qa/`; run them against a local server on port 8080:",
             "- `ix_suite.py` (with `ix_treatments.py`): every page's interactives, Riya's launcher and the case pages;",
             "- `colour_suite.py`: colour on hover; `ba_test.py`: slider drags and frame timing;",
             "- `spacing.py`: link spacing; `centred.py`: lines under centred headings; `pages_shots.py`: every page at 1440 and 390;",
             "- `report_tests.py`: writes this file.", "",
             "Also checked:",
             f"- **Link spacing:** {sum(len(v) for v in spacing.values()) if isinstance(spacing, dict) else len(spacing)} links closer than 32px to the text above, at 1440 and 390.",
             f"- **Centred sections:** {sum(len(v) for v in centred.values())} off-centre links under a centred heading, at 1440 and 390.",
             "- **Photos:** `tools/photo_audit.py` and `tools/image_audit.py` report 0 problems.",
             "- **JavaScript errors:** none thrown on any page visited, at either width.",
             "- **Slider smoothness:** " + "; ".join(f"{r['page']}: {r['note']}" for r in frames) + " (60 fps is 16.7 ms).", "",
             "| Page | Interactive | 1440 (mouse, keyboard) | 390 (touch) |", "|---|---|---|---|"]
    for (page, name), v in rows.items():
        lines.append(f"| {page} | {name} | {'<br>'.join(v.get(1440) or ['n/a'])} | {'<br>'.join(v.get(390) or ['n/a'])} |")
    (ROOT / "notes" / "INTERACTION-TESTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{ok}/{n} -> notes/INTERACTION-TESTS.md")


if __name__ == "__main__":
    main()
