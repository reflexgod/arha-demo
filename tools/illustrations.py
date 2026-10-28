"""Arha's line illustrations: hairline ink drawings with a bronze accent, written as SVG.

Usage: .venv/Scripts/python -I tools/illustrations.py
Output: assets/illustrations/<name>.svg. Used where a photograph would be dishonest or unavailable:
the "Common problems we fix" before/after pairs show what a treatment does, not a patient.
Style: paper ground, ink outlines (1.5), stone gums, bronze for whatever the treatment adds.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "illustrations"
PAPER, INK, STONE, BRONZE, MUTED = "#FAFAF6", "#252424", "#E7E3DC", "#B08154", "#6B6766"
W, H = 640, 400


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def svg(body, title, view=(0, 0, W, H)):
    x, y, w, h = view
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f(x)} {f(y)} {f(w)} {f(h)}" role="img" aria-label="{title}">'
            f"<title>{title}</title>"
            f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="{PAPER}"/>'
            f'<g fill="none" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round">{body}</g></svg>\n')


# ------------------------------------------------------------------ front view of the upper front teeth
# canine, lateral, central | central, lateral, canine: (width, height, pointed)
TEETH = [(52, 112, True), (50, 100, False), (66, 122, False), (66, 122, False), (50, 100, False), (52, 112, True)]
TOP = 132  # where the teeth meet the gum


def tooth_path(cx, w, h, pointed=False, chip=None):
    """Front outline of one tooth, crown only: narrower at the gum, rounded at the biting edge."""
    t, b = TOP, TOP + h
    l0, r0, l1, r1 = cx - .41 * w, cx + .41 * w, cx - .5 * w, cx + .5 * w
    if pointed:
        edge = f"Q{f(l1)} {f(b - 4)} {f(cx - .18 * w)} {f(b - 2)}L{f(cx)} {f(b + 8)}L{f(cx + .18 * w)} {f(b - 2)}Q{f(r1)} {f(b - 4)} {f(r1)} {f(b - 20)}"
    elif chip == "right":
        edge = f"Q{f(l1)} {f(b)} {f(l1 + 12)} {f(b)}L{f(cx - .02 * w)} {f(b)}L{f(cx + .16 * w)} {f(b - 14)}L{f(r1 - 2)} {f(b - 40)}"
    else:
        edge = f"Q{f(l1)} {f(b)} {f(l1 + 12)} {f(b)}L{f(r1 - 12)} {f(b)}Q{f(r1)} {f(b)} {f(r1)} {f(b - 12)}"
    start = f"M{f(l0)} {f(t)}C{f(l0 - 4)} {f(t + .35 * h)} {f(l1)} {f(t + .55 * h)} {f(l1)} {f(b - (20 if pointed else 12))}"
    return start + edge + f"C{f(r1)} {f(t + .55 * h)} {f(r0 + 4)} {f(t + .35 * h)} {f(r0)} {f(t)}"


def layout(gap=4, spread=None):
    """Centre x of each tooth. spread: extra space added after tooth i (index -> px)."""
    spread = spread or {}
    total = sum(w for w, _, _ in TEETH) + gap * (len(TEETH) - 1) + sum(spread.values())
    x, out = W / 2 - total / 2, []
    for i, (w, _, _) in enumerate(TEETH):
        out.append(x + w / 2)
        x += w + gap + spread.get(i, 0)
    return out


def gum(centres, swollen=False):
    """Stone gum above the teeth with a scalloped margin; swollen = rounder, lower margin."""
    xs = [(c - w / 2, c + w / 2) for c, (w, _, _) in zip(centres, TEETH)]
    d = f"M0 0H{W}V{TOP + 10}"
    margin = ""
    depth, papilla = (14, 22) if swollen else (24, 12)
    pts = list(reversed(xs))
    d += f"L{f(pts[0][1] + 30)} {TOP + 10}"
    for x0, x1 in pts:
        d += f"L{f(x1)} {TOP + papilla}Q{f((x0 + x1) / 2)} {TOP - depth} {f(x0)} {TOP + papilla}"
        margin += f"M{f(x1)} {TOP + papilla}Q{f((x0 + x1) / 2)} {TOP - depth} {f(x0)} {TOP + papilla}"
    d += f"L{f(pts[-1][0] - 30)} {TOP + 10}H0Z"
    tint = "#EAD6C8" if swollen else STONE  # inflamed gum: stone warmed towards bronze
    return f'<path d="{d}" fill="{tint}" stroke="none"/><path d="{margin}"/>'


def row(centres=None, skip=(), rotate=None, drop=None, fill=PAPER, chip=None, accent=(), accent_dash=False, extra=""):
    centres = centres or layout()
    rotate, drop = rotate or {}, drop or {}
    out = []
    for i, (c, (w, h, pt)) in enumerate(zip(centres, TEETH)):
        if i in skip:
            continue
        d = tooth_path(c, w, h, pt, chip if (chip and i == 3) else None)
        stroke = f' stroke="{BRONZE}"' if i in accent else ""
        tr = []
        if i in drop:
            tr.append(f"translate(0 {drop[i]})")
        if i in rotate:
            tr.append(f"rotate({rotate[i]} {f(c)} {TOP + h / 2})")
        t = f' transform="{" ".join(tr)}"' if tr else ""
        out.append(f'<path d="{d}" fill="{fill}"{stroke}{t}/>')
    return "".join(out) + extra


FRONT = (120, TOP - 90, 400, 250)  # the front views are cropped to the teeth (8:5)


def front(title, **kw):
    centres = kw.pop("centres", None) or layout()
    swollen = kw.pop("swollen", False)
    teeth = row(centres, **kw)
    return svg(teeth + gum(centres, swollen), title, FRONT)


def missing(after):
    c = layout()
    w, h, _ = TEETH[2]
    if not after:
        ridge = f'<path d="M{f(c[2] - w / 2)} {TOP + 14}Q{f(c[2])} {TOP + 30} {f(c[2] + w / 2)} {TOP + 14}"/>'
        return front("A gap where an upper front tooth is missing", centres=c, skip=(2,), extra=ridge)
    post = (f'<g stroke="{BRONZE}" stroke-dasharray="4 4">'
            f'<path d="M{f(c[2] - 9)} {TOP - 8}V{TOP - 58}L{f(c[2])} {TOP - 70}L{f(c[2] + 9)} {TOP - 58}V{TOP - 8}"/>'
            + "".join(f'<path d="M{f(c[2] - 9)} {TOP - 18 - 10 * k}L{f(c[2] + 9)} {TOP - 24 - 10 * k}"/>' for k in range(4))
            + "</g>")
    # the post sits in the bone above the gum line, drawn over the stone gum
    return svg(row(c, accent=(2,)) + gum(c) + post, "The gap filled by an implant crown, with the implant post shown in the bone above", FRONT)


def chipped(after):
    if not after:
        return front("An upper front tooth with a chipped corner", chip="right")
    c = layout()
    w, h, _ = TEETH[3]
    b = TOP + h
    patch = f'<path d="M{f(c[3] - .02 * w)} {b}L{f(c[3] + .16 * w)} {b - 14}L{f(c[3] + .5 * w - 2)} {b - 40}" stroke="{BRONZE}" stroke-dasharray="3 4"/>'
    return front("The chipped corner rebuilt in tooth-coloured material", extra=patch)


def gaps(after):
    if after:
        return front("Front teeth with the gaps closed")
    return front("Gaps between the upper front teeth", centres=layout(spread={1: 12, 2: 20, 3: 12}))


def crooked(after):
    if after:
        return front("Upper front teeth in a straight, even line")
    return front("Crooked upper front teeth: turned and overlapping",
                 centres=layout(gap=-4, spread={0: 6}), rotate={1: -9, 2: 6, 3: -5, 4: 10}, drop={1: 6, 4: -4})


def stained(after):
    if after:
        return front("Clean, brighter front teeth")
    return front("Stained front teeth", fill="#E2CDB6")  # bronze at about 35% on paper


def bleeding(after):
    if after:
        return front("Firm gums with a tight, even margin")
    c = layout()
    dots = "".join(f'<circle cx="{f(x)}" cy="{TOP + 20}" r="5" fill="{BRONZE}" stroke="none"/>'
                   for x in [(c[i] + c[i + 1]) / 2 for i in range(len(c) - 1)])
    return front("Swollen gums that bleed between the teeth", swollen=True, extra=dots)


def section_tooth(stage):
    """Cross-section of a molar: crown, pulp chamber, two roots, gum and bone."""
    body = (f'<path d="M0 270H{W}" stroke="{MUTED}" stroke-width="1"/>'  # gum line
            f'<rect x="0" y="270" width="{W}" height="{H - 270}" fill="{STONE}" stroke="none"/>')
    outline = ("M240 120C240 90 262 74 290 78C304 80 312 88 320 88C328 88 336 80 350 78C378 74 400 90 400 120"
               "C400 170 392 210 392 250C392 300 384 352 368 372C360 382 350 376 348 362L336 290C334 280 306 280 304 290"
               "L292 362C290 376 280 382 272 372C256 352 248 300 248 250C248 210 240 170 240 120Z")
    pulp = ("M286 150C286 134 300 130 320 130C340 130 354 134 354 150C354 186 350 220 346 250L360 352"
            "C360 358 354 360 352 354L334 268C330 258 310 258 306 268L288 354C286 360 280 358 280 352L294 250C290 220 286 186 286 150Z")
    body += f'<path d="{outline}" fill="{PAPER}"/>'
    if stage == "ache":
        body += f'<path d="{pulp}" fill="{STONE}"/>'
        body += f'<path d="M300 96C312 104 318 116 314 128" stroke="{INK}"/><path d="M296 92Q306 100 302 110L314 112" fill="{INK}" stroke="none" opacity=".75"/>'
        body += "".join(f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{BRONZE}"/>' for x1, y1, x2, y2 in
                        [(320, 196, 320, 216), (300, 200, 290, 214), (340, 200, 350, 214), (306, 182, 292, 184), (334, 182, 348, 184)])
        title = "Cross-section of a molar with decay reaching the nerve"
    else:
        body += f'<path d="{pulp}" fill="{BRONZE}" fill-opacity=".22" stroke="{BRONZE}"/>'
        body += f'<path d="M298 92C312 100 320 112 318 126" stroke="{BRONZE}" stroke-dasharray="3 4"/>'
        title = "The same molar cleaned, sealed and restored"
    return svg(body, title)


def fillings(after):
    """Two molars from above, with fillings in the grooves."""
    def molar(cx, cy):
        return (f'<path d="M{cx - 70} {cy - 40}C{cx - 74} {cy - 74} {cx - 40} {cy - 80} {cx} {cy - 76}C{cx + 40} {cy - 80} {cx + 74} {cy - 74} {cx + 70} {cy - 40}'
                f'C{cx + 80} {cy} {cx + 74} {cy + 70} {cx + 40} {cy + 74}C{cx} {cy + 80} {cx - 40} {cy + 78} {cx - 70} {cy + 66}C{cx - 80} {cy + 30} {cx - 78} {cy - 10} {cx - 70} {cy - 40}Z" fill="{PAPER}"/>'
                f'<path d="M{cx - 40} {cy - 6}Q{cx} {cy + 12} {cx + 40} {cy - 6}M{cx} {cy - 50}Q{cx - 6} {cy} {cx} {cy + 50}" stroke="{MUTED}" stroke-width="1"/>')

    def filling(cx, cy):
        d = (f"M{cx - 42} {cy - 14}C{cx - 30} {cy - 24} {cx - 14} {cy - 20} {cx - 10} {cy - 44}C{cx - 4} {cy - 54} {cx + 8} {cy - 50} {cx + 10} {cy - 38}"
             f"C{cx + 14} {cy - 18} {cx + 34} {cy - 22} {cx + 42} {cy - 10}C{cx + 46} {cy + 2} {cx + 30} {cy + 10} {cx + 12} {cy + 8}"
             f"C{cx + 6} {cy + 30} {cx - 6} {cy + 34} {cx - 12} {cy + 16}C{cx - 30} {cy + 12} {cx - 48} {cy + 2} {cx - 42} {cy - 14}Z")
        if after:
            return f'<path d="{d}" fill="{PAPER}" stroke="{BRONZE}" stroke-dasharray="3 4"/>'
        return f'<path d="{d}" fill="{MUTED}" stroke="{INK}"/>'

    body = molar(230, 200) + molar(410, 200) + filling(230, 200) + filling(410, 200)
    return svg(body, "Two back teeth with tooth-coloured fillings" if after else "Two back teeth with dark metal fillings")


def dentures(after):
    """Side view of the lower jaw ridge with a denture; after: held by two implants."""
    ridge = (f'<path d="M60 300C120 250 200 236 320 236C440 236 520 250 580 300V{H}H60Z" fill="{STONE}" stroke="none"/>'
             f'<path d="M60 300C120 250 200 236 320 236C440 236 520 250 580 300"/>')
    lift = 0 if after else -26
    base = (f'<g transform="translate(0 {lift})"><path d="M110 268C160 232 230 222 320 222C410 222 480 232 530 268'
            f'C470 250 400 244 320 244C240 244 170 250 110 268Z" fill="{PAPER}"/>'
            + "".join(f'<path d="M{x - 18} 226C{x - 20} 196 {x - 14} 176 {x} 172C{x + 14} 176 {x + 20} 196 {x + 18} 226" fill="{PAPER}"/>'
                      for x in (190, 232, 276, 320, 364, 408, 450))
            + "</g>")
    if after:
        posts = "".join(f'<g stroke="{BRONZE}"><path d="M{x - 8} 246V316L{x} 328L{x + 8} 316V246"/>'
                        + "".join(f'<path d="M{x - 8} {258 + 12 * k}L{x + 8} {252 + 12 * k}"/>' for k in range(5)) + "</g>"
                        for x in (220, 420))
        return svg(ridge + posts + base, "A lower denture held firmly by two implants")
    arrows = f'<g stroke="{BRONZE}"><path d="M140 222V246M134 240L140 248L146 240M500 222V246M494 240L500 248L506 240"/></g>'
    return svg(ridge + base + arrows, "A lower denture lifting off the gum")


def child(after):
    """Baby teeth: smaller, rounder, naturally spaced; one with a cavity, then sealed and filled."""
    global TEETH, TOP
    saved = TEETH, TOP
    TEETH = [(40, 70, True), (38, 62, False), (46, 74, False), (46, 74, False), (38, 62, False), (40, 70, True)]
    TOP = 150
    c = layout(gap=10)
    if after:
        x, y = c[2], TOP + 40
        extra = f'<path d="M{f(x - 8)} {y - 6}Q{f(x)} {y - 12} {f(x + 8)} {y - 4}Q{f(x + 6)} {y + 8} {f(x - 4)} {y + 6}Z" fill="{PAPER}" stroke="{BRONZE}" stroke-dasharray="2 3"/>'
        title = "Baby teeth kept healthy, with the small cavity filled"
    else:
        x, y = c[2], TOP + 40
        extra = f'<path d="M{f(x - 8)} {y - 6}Q{f(x)} {y - 12} {f(x + 8)} {y - 4}Q{f(x + 6)} {y + 8} {f(x - 4)} {y + 6}Z" fill="{MUTED}"/>'
        title = "Baby teeth with a small cavity starting"
    out = svg(row(c, extra=extra) + gum(c), title, (170, TOP - 60, 300, 187.5))
    TEETH, TOP = saved
    return out


PAIRS = {
    "missing-tooth": missing,
    "chipped-tooth": chipped,
    "gaps": gaps,
    "crooked-teeth": crooked,
    "stained-teeth": stained,
    "toothache": lambda after: section_tooth("fixed" if after else "ache"),
    "bleeding-gums": bleeding,
    "metal-fillings": fillings,
    "dentures": dentures,
    "child-teeth": child,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, make in PAIRS.items():
        for state, after in (("before", False), ("after", True)):
            (OUT / f"problem-{name}-{state}.svg").write_text(make(after), encoding="utf-8", newline="\n")
    art = treatment_art()
    for name, text in art.items():
        (OUT / f"{name}.svg").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(PAIRS) * 2 + len(art)} illustrations to {OUT.relative_to(ROOT)}")



# ------------------------------------------------------------------ treatment pages (Phase 3)
def implant_bridge():
    """Three linked crowns carried by two implants (upper front view)."""
    c = layout()
    posts = "".join(f'<g stroke="{BRONZE}" stroke-dasharray="4 4"><path d="M{f(x - 9)} {TOP - 8}V{TOP - 58}L{f(x)} {TOP - 70}L{f(x + 9)} {TOP - 58}V{TOP - 8}"/>'
                    + "".join(f'<path d="M{f(x - 9)} {TOP - 18 - 10 * k}L{f(x + 9)} {TOP - 24 - 10 * k}"/>' for k in range(4)) + "</g>"
                    for x in (c[1], c[3]))
    return svg(row(c, accent=(1, 2, 3)) + gum(c) + posts, "An implant bridge: three crowns carried by two implants", FRONT)


def full_arch(after):
    """Worn, short and missing teeth, then the whole front rebuilt (bronze = new restorations)."""
    global TEETH
    saved = TEETH
    if not after:
        TEETH = [(w, round(h * .74), False) for w, h, _ in saved]
        out = front("Worn, short front teeth with one missing", skip=(4,))
    else:
        out = front("The front teeth rebuilt to an even length and shape", accent=tuple(range(6)))
    TEETH = saved
    return out


def smile_design(after):
    global TEETH
    saved = TEETH
    if not after:
        TEETH = [(52, 100, True), (46, 112, False), (70, 112, False), (60, 126, False), (54, 92, False), (50, 116, True)]
        out = front("Front teeth of uneven length, width and shape")
    else:
        out = front("The same teeth designed to even proportions along the smile line", accent=tuple(range(6)))
    TEETH = saved
    return out


def aligner_stage(t):
    """Stage t (0 = start, 1 = finish) of straightening with aligners."""
    k = 1 - t
    centres = layout(gap=-4 + 8 * t, spread={0: 6 * k})
    return front(f"Aligner stage: teeth {'straight' if t == 1 else 'moving into line'}", centres=centres,
                 rotate={1: -9 * k, 2: 6 * k, 3: -5 * k, 4: 10 * k}, drop={1: 6 * k, 4: -4 * k})


def root_canal(step):
    """Four steps: infected pulp, cleaned with rotary files, sealed, crown on top."""
    if step == 0:
        return section_tooth("ache").replace("Cross-section of a molar with decay reaching the nerve",
                                             "Step 1: decay has reached the pulp and it is infected")
    base = section_tooth("fixed")
    if step == 1:
        base = base.replace(f'fill="{BRONZE}" fill-opacity=".22" stroke="{BRONZE}"', f'fill="{PAPER}" stroke="{INK}"')
        files = (f'<g stroke="{BRONZE}" stroke-width="1.2"><path d="M300 40L292 330"/><path d="M340 40L348 330"/>'
                 + "".join(f'<path d="M{296 - k * .03:.1f} {80 + 26 * k}l6 -6M{344 + k * .03:.1f} {80 + 26 * k}l-6 -6"/>' for k in range(9))
                 + f'<rect x="288" y="20" width="16" height="22" fill="{PAPER}"/><rect x="336" y="20" width="16" height="22" fill="{PAPER}"/></g>')
        base = base.replace("</g></svg>", files + "</g></svg>")
        title = "Step 2: the canals are cleaned and shaped with fine rotary instruments"
    elif step == 2:
        title = "Step 3: the cleaned canals are filled and sealed"
    else:
        cap = (f'<path d="M232 128C230 86 260 66 290 70C304 72 312 80 320 80C328 80 336 72 350 70C380 66 410 86 408 128'
               f'C408 150 404 168 400 182L240 182C236 168 232 150 232 128Z" stroke="{BRONZE}" stroke-width="2"/>')
        base = base.replace("</g></svg>", cap + "</g></svg>")
        title = "Step 4: a crown covers and protects the treated tooth"
    return re.sub(r"<title>.*?</title>", f"<title>{title}</title>", re.sub(r'aria-label="[^"]*"', f'aria-label="{title}"', base))


def treatment_art():
    out = {"implant-single": missing(True), "implant-bridge": implant_bridge(), "implant-denture": dentures(True),
           "full-arch-before": full_arch(False), "full-arch-after": full_arch(True),
           "smile-design-before": smile_design(False), "smile-design-after": smile_design(True)}
    for n in range(6):
        out[f"aligner-stage-{n + 1}"] = aligner_stage(n / 5)
    for n in range(4):
        out[f"root-canal-step-{n + 1}"] = root_canal(n)
    return out


if __name__ == "__main__":
    main()
