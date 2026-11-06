"""Build the demo hero loop from Pexels stock (Mumbai skyline + Marine Drive). See notes/credits.md (local only).

Usage: .venv/Scripts/python -I tools/hero_stock.py
Sources in src-assets/stock/video/. Output in assets/video/:
  hero-city-1080.mp4, hero-city-720.mp4 (H.264 only: VP9 came out larger for this footage), hero-city-poster-{1920,1280,720}.{avif,webp,jpg}
  hero-city-phone.mp4 + hero-city-poster-port-{540,810}.*: a 9:16 cut from the centre of the frame for phones held upright
  (sharper and far lighter than scaling the 16:9 loop up to fill a tall screen).
3 Nov 2026: graded slightly darker and encoded lighter (the 1080p loop was 3.8 MB), so white text reads on every frame.
Seamless loop: the first XF seconds of shot 1 are crossfaded in at the end.
The previous clinic-walkthrough loop (tools/video.py, hero-land-*/hero-port-*) is kept but no longer used.
6 Nov 2026 (--light): the phone cuts, 720p and under 800 KB. A shorter loop of the same two shots from the same first
frame keeps the poster and the picture quality; squeezing the full 27 s into 800 KB would have smeared the water.
  .venv/Scripts/python -I tools/hero_stock.py --light   writes hero-city-phone.mp4 (9:16) and hero-city-720-light.mp4 (16:9)
"""
import sys
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src-assets" / "stock" / "video"
OUT = ROOT / "assets" / "video"
XF = 1.2
SHOTS = [  # (file, start, duration)
    ("16902674_2560_1440_30fps.mp4", 0.0, 19.8),   # Mumbai skyline across the bay (Pexels 39648416)
    ("13251826_2560_1440_30fps.mp4", 0.0, 9.5),    # Marine Drive, clouds over the bay (Pexels 31000790)
]
GRADE = "eq=saturation=0.9:contrast=0.97,curves=master='0/0.02 0.5/0.45 1/0.9'"
# name: (crop, scale, crf, maxrate)
VARIANTS = {"1080": ("", "1920:1080", 30, "0.62M"), "720": ("", "1280:720", 31, "0.36M"),
            "phone": ("crop=ih*9/16:ih,", "720:1280", 31, "0.4M")}


def run(cmd):
    subprocess.run(cmd, check=True)


def light():
    """Same grade and first frame as the full loop: 11 s of the skyline and 6 s of Marine Drive, two-pass to about 420 kbit/s."""
    cuts = ((SHOTS[0][0], 0.0, 11.0), (SHOTS[1][0], 0.0, 6.0))
    inputs = []
    for f, start, dur in cuts:
        inputs += ["-ss", str(start), "-t", str(dur), "-i", str(SRC / f)]
    for name, crop, scale in (("phone", "crop=ih*9/16:ih,", "720:1280"), ("720-light", "", "1280:720")):
        parts = [f"[{i}:v]{crop}scale={scale}:flags=lanczos,{GRADE},fps=24,format=yuv420p,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[v{i}]" for i in range(2)]
        parts += ["[v0]split[a][b]", f"[a]trim=start={XF},setpts=PTS-STARTPTS[s0]", f"[b]trim=end={XF},setpts=PTS-STARTPTS[head]"]
        d0, d1 = cuts[0][2] - XF, cuts[1][2]
        parts.append(f"[s0][v1]xfade=transition=fade:duration={XF}:offset={d0 - XF:.3f}[x1]")
        total = d0 - XF + d1
        parts.append(f"[x1][head]xfade=transition=fade:duration={XF}:offset={total - XF:.3f}[out]")
        mp4 = OUT / f"hero-city-{name}.mp4"
        log = str(OUT / f"_2pass-{name}")
        common = ["-filter_complex", ";".join(parts), "-map", "[out]", "-an", "-c:v", "libx264", "-preset", "slow", "-b:v", "420k",
                  "-profile:v", "high", "-pix_fmt", "yuv420p", "-g", "72", "-passlogfile", log]
        run(["ffmpeg", "-v", "error", "-y", *inputs, *common, "-pass", "1", "-f", "null", "NUL"])
        run(["ffmpeg", "-v", "error", "-y", *inputs, *common, "-pass", "2", "-movflags", "+faststart", str(mp4)])
        for f in OUT.glob(f"_2pass-{name}*"):
            f.unlink()
        print(f"{mp4.name}: {total:.1f}s {mp4.stat().st_size / 1024:.0f} KB")


def main():
    if "--light" in sys.argv:
        return light()
    inputs = []
    for f, start, dur in SHOTS:
        inputs += ["-ss", str(start), "-t", str(dur), "-i", str(SRC / f)]
    for name, (crop, scale, crf, rate) in VARIANTS.items():
        parts = [f"[{i}:v]{crop}scale={scale}:flags=lanczos,{GRADE},fps=24,format=yuv420p,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[v{i}]"
                 for i in range(len(SHOTS))]
        parts += ["[v0]split[a][b]", f"[a]trim=start={XF},setpts=PTS-STARTPTS[s0]", f"[b]trim=end={XF},setpts=PTS-STARTPTS[head]"]
        d0, d1 = SHOTS[0][2] - XF, SHOTS[1][2]
        parts.append(f"[s0][v1]xfade=transition=fade:duration={XF}:offset={d0 - XF:.3f}[x1]")
        total = d0 - XF + d1
        parts.append(f"[x1][head]xfade=transition=fade:duration={XF}:offset={total - XF:.3f}[out]")
        mp4 = OUT / f"hero-city-{name}.mp4"
        run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(parts), "-map", "[out]", "-an",
             "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-profile:v", "high", "-pix_fmt", "yuv420p",
             "-g", "72", "-movflags", "+faststart", "-maxrate", rate, "-bufsize", "1.6M",
             str(mp4)])
        if name in ("1080", "phone"):
            png = OUT / "_poster.png"
            run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-frames:v", "1", str(png)])
            im = Image.open(png).convert("RGB")
            png.unlink()
            if name == "phone":  # the poster is cut from the 1440p source frame for full sharpness
                run(["ffmpeg", "-v", "error", "-y", "-ss", str(SHOTS[0][1]), "-i", str(SRC / SHOTS[0][0]), "-frames:v", "1",
                     "-vf", f"crop=ih*9/16:ih,scale=810:1440:flags=lanczos,{GRADE}", str(png)])
                im = Image.open(png).convert("RGB")
                png.unlink()
            for w in ((810, 540) if name == "phone" else (1920, 1280, 720)):
                p = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
                base = OUT / (f"hero-city-poster-port-{w}" if name == "phone" else f"hero-city-poster-{w}")
                p.save(f"{base}.avif", "AVIF", quality=55, speed=4)
                p.save(f"{base}.webp", "WEBP", quality=76, method=6)
                p.save(f"{base}.jpg", "JPEG", quality=78, optimize=True, progressive=True)
        print(f"{name}: {total:.1f}s")
    for f in sorted(OUT.glob("hero-city*")):
        print(f"  {f.name:<30} {f.stat().st_size / 1024:7.0f} KB")


if __name__ == "__main__":
    main()
