"""Build self-hosted web fonts into assets/fonts.

Usage: python -I tools/fonts.py <download-dir>
  <download-dir> holds d-din.zip (fontsquirrel.com/fonts/d-din, SIL OFL)
  and the Fontsource Jost files jost-latin-{400-normal,400-italic,600-normal}.woff2 (SIL OFL).
D-DIN Bold is subset to Latin + the punctuation the site uses, then saved as WOFF2.
"""
import shutil
import sys
import zipfile
from pathlib import Path

from fontTools import subset

src = Path(sys.argv[1])
out = Path(__file__).resolve().parent.parent / "assets" / "fonts"
out.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(src / "d-din.zip") as z:
    (src / "D-DIN-Bold.otf").write_bytes(z.read("D-DIN-Bold.otf"))
    (out / "OFL-D-DIN.txt").write_bytes(z.read("SIL Open Font License.txt"))

opts = subset.Options()
opts.flavor = "woff2"
opts.layout_features = ["kern", "liga", "case"]
font = subset.load_font(str(src / "D-DIN-Bold.otf"), opts)
# Basic Latin + Latin-1 + dashes, quotes, bullet, ellipsis, middle dot, multiplication sign
unicodes = list(range(0x20, 0x7F)) + list(range(0xA0, 0x100)) + [0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026]
sub = subset.Subsetter(opts)
sub.populate(unicodes=unicodes)
sub.subset(font)
subset.save_font(font, str(out / "d-din-bold.woff2"), opts)

for name, dest in [("jost-latin-400-normal", "jost-400"), ("jost-latin-400-italic", "jost-400-italic"), ("jost-latin-600-normal", "jost-600")]:
    shutil.copy(src / f"{name}.woff2", out / f"{dest}.woff2")
shutil.copy(src / "jost-LICENSE", out / "OFL-Jost.txt")

for f in sorted(out.iterdir()):
    print(f"{f.name:<24} {f.stat().st_size / 1024:6.1f} KB")
