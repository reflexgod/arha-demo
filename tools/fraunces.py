"""Build the self-hosted Fraunces display face (SIL OFL) into assets/fonts/fraunces-var.woff2.

Usage: .venv/Scripts/python -I tools/fraunces.py <unpacked @fontsource-variable/fraunces package>
Source: files/fraunces-latin-opsz-normal.woff2 (axes wght + opsz). Kept: weights 400 to 500 and optical sizes 20 to 144
(only headlines and pull quotes use it, so the small text sizes are dropped), Latin + the site's punctuation.
Also prints the @font-face overrides that make Georgia take the same space as Fraunces, so the swap shifts nothing.
"""
import io
import shutil
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

pkg = Path(sys.argv[1])
out = Path(__file__).resolve().parent.parent / "assets" / "fonts"
GEORGIA = Path(r"C:\Windows\Fonts\georgia.ttf")
UNICODES = list(range(0x20, 0x7F)) + list(range(0xA0, 0x100)) + [0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026, 0x2192]
# English letter frequencies, for an average advance that matches running headlines
SAMPLE = "Specialist dentistry on Peddar Road. Crafted with precision. Given with care. What brings you in? How it works"

font = TTFont(pkg / "files" / "fraunces-latin-opsz-normal.woff2")
print("axes", [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in font["fvar"].axes])
font = instancer.instantiateVariableFont(font, {"wght": (400, 500), "opsz": (20, 144)})
opts = subset.Options()
opts.flavor = "woff2"
opts.layout_features = ["kern", "liga", "case", "lnum", "pnum"]
sub = subset.Subsetter(opts)
sub.populate(unicodes=UNICODES)
sub.subset(font)
font.flavor = "woff2"
font.save(out / "fraunces-var.woff2")
shutil.copy(pkg / "LICENSE", out / "OFL-Fraunces.txt")
print(f"fraunces-var.woff2 {(out / 'fraunces-var.woff2').stat().st_size / 1024:.1f} KB")


def avg_width(f, axes=None):
    if axes:
        buf = io.BytesIO()
        f.flavor = None
        f.save(buf)
        buf.seek(0)
        f = instancer.instantiateVariableFont(TTFont(buf), axes)
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    return sum(hmtx[cmap[ord(c)]][0] for c in SAMPLE) / len(SAMPLE) / upm, f["hhea"].ascent / upm, -f["hhea"].descent / upm, f["hhea"].lineGap / upm


fr = avg_width(TTFont(out / "fraunces-var.woff2"), {"wght": 400, "opsz": 40})
ge = avg_width(TTFont(GEORGIA))
scale = fr[0] / ge[0]
print(f"size-adjust: {scale * 100:.1f}%; ascent-override: {fr[1] / scale * 100:.1f}%; descent-override: {fr[2] / scale * 100:.1f}%; line-gap-override: {fr[3] / scale * 100:.1f}%")
