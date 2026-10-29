"""Clinic stills from Arha's own walkthrough video (v4 fixes 3, point 1: the clinic leads every page).

Usage: .venv/Scripts/python -I tools/stills.py [--only name,name] [--sheet <out.jpg>]
Source: src-assets/IMG_2303.MOV (1080x1920 portrait, HEVC 10-bit HLG; the 30 s tour MP4 is the same
footage pillarboxed). For each moment in STILLS, the frames from 0.6 s before to 0.6 s after (10 a second) are
tone-mapped to SDR (the same HLG -> bt709 chain as tools/video.py), the sharpest (variance of the
Laplacian) is kept, cropped if asked, given the same gentle white balance and exposure as Arha's photos
(photos.tone) and exported as assets/img/arha-dental-care-<name>-<w>.{avif,webp,jpg}. The "arha" in
the name gives them the site's warm clinic grade (site.css).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from photos import export, tone  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src-assets" / "IMG_2303.MOV"
TONEMAP = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=rgb24")

# name: (second, crop (left, top, right, bottom) fractions or None, alt text[, half-window in seconds, default 0.6])
STILLS = {
    "entrance-door": (0.5, (0, 0.04, 0, 0.18), "The door of suite 107 at Doctor House, with the Arha emblem and both doctors’ names"),
    "reception-desk": (12.5, (0, 0.10, 0, 0.12), "Arha’s reception: the gold emblem on the marble wall above the front desk"),
    "operatory-glass-door": (22.5, (0, 0.08, 0, 0.10), "A treatment room seen through its glass door: the chair, the light and a screen"),
    "operatory-laptop": (24.0, (0, 0.10, 0, 0.10), "A treatment room with the chair, the overhead light and a laptop on the counter"),
    "consultation-desk": (27.0, (0, 0.12, 0, 0.08), "The consultation desk in a treatment room, with a screen and two chairs"),
    "chair-window": (33.0, (0, 0.10, 0, 0.08), "The dental chair under its light, beside a window with a soft blind"),
    "scan-screen": (37.5, (0, 0.10, 0, 0.34), "A screen in a treatment room showing 3D scans of the upper and lower teeth", 0.15),
    "steriliser": (45.5, (0, 0.18, 0, 0.12), "Arha’s steriliser on the counter of the sterilisation room"),
    "xray-room": (51.0, (0, 0.06, 0, 0.10), "The X-ray room: a panoramic X-ray unit against a marble wall"),
    "reception-wide": (54.5, (0, 0.08, 0, 0.10), "The reception and waiting area, with the emblem wall and a plant"),
    "planning-room": (62.5, (0, 0.12, 0, 0.06), "A quiet room with a desk and chair beside the equipment counter"),
    "equipment-counter": (68.0, (0, 0.14, 0, 0.10), "Equipment on the counter of the sterilisation room"),
    "operatory-chair": (71.5, (0, 0.06, 0, 0.08), "The dental chair and its light in a second treatment room"),
    "delivery-unit": (73.5, (0, 0.10, 0, 0.12), "The instrument holder at the chair, with its handpieces ready"),
    "logo-wall": (83.5, (0, 0.10, 0, 0.18), "The Arha Dental Care emblem in gold on the reception’s marble wall"),
}


def frames(t, tmp, span=0.6):
    pattern = str(Path(tmp) / f"s{t:05.1f}-%02d.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(t - span, 0):.2f}", "-i", str(SRC), "-t", f"{2 * span:.2f}",
                    "-vf", f"fps=10,{TONEMAP}", pattern], check=True)
    return sorted(Path(tmp).glob(f"s{t:05.1f}-*.png"))


def sharpest(paths):
    def score(p):
        g = cv2.resize(cv2.imread(str(p), 0), (540, 960))
        return cv2.Laplacian(g, cv2.CV_64F).var()
    return max(paths, key=score)


def build(only=None):
    made = {}
    with tempfile.TemporaryDirectory() as tmp:
        for name, (t, crop, _alt, *span) in STILLS.items():
            if only and name not in only:
                continue
            best = sharpest(frames(t, tmp, *span))
            im = Image.open(best).convert("RGB")
            if crop:
                l, tp, r, b = crop
                im = im.crop((round(l * im.width), round(tp * im.height), round(im.width * (1 - r)), round(im.height * (1 - b))))
            im, note = tone(im)
            files, size = export(im, f"arha-dental-care-{name}")
            made[name] = im
            print(f"{name:<22} {t:>5.1f}s  {size[0]}x{size[1]}  {note}")
    return made


if __name__ == "__main__":
    made = build(sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None)
    if "--sheet" in sys.argv:
        tw, th = 270, 420
        sheet = Image.new("RGB", (tw * 8, th * 2), "white")
        for k, im in enumerate(made.values()):
            im = im.copy(); im.thumbnail((tw - 6, th - 6))
            sheet.paste(im, ((k % 8) * tw + 3, (k // 8) * th + 3))
        sheet.save(sys.argv[sys.argv.index("--sheet") + 1], quality=82)
