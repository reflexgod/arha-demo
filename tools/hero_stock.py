"""Build the demo hero loop from Pexels stock (Mumbai skyline + Marine Drive). See notes/credits.md (local only).

Usage: .venv/Scripts/python -I tools/hero_stock.py
Sources in src-assets/stock/video/. Output in assets/video/:
  hero-city-1080.mp4, hero-city-720.mp4 (H.264 only: VP9 came out larger for this footage), hero-city-poster-{1920,1280,720}.{avif,webp,jpg}
Seamless loop: the first XF seconds of shot 1 are crossfaded in at the end.
The previous clinic-walkthrough loop (tools/video.py, hero-land-*/hero-port-*) is kept but no longer used.
"""
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
GRADE = "eq=saturation=0.9:contrast=0.97,curves=master='0/0.03 0.5/0.51 1/0.98'"
VARIANTS = {"1080": ("1920:1080", 27), "720": ("1280:720", 28)}


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    inputs = []
    for f, start, dur in SHOTS:
        inputs += ["-ss", str(start), "-t", str(dur), "-i", str(SRC / f)]
    for name, (scale, crf) in VARIANTS.items():
        parts = [f"[{i}:v]scale={scale}:flags=lanczos,{GRADE},fps=30,format=yuv420p,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[v{i}]"
                 for i in range(len(SHOTS))]
        parts += ["[v0]split[a][b]", f"[a]trim=start={XF},setpts=PTS-STARTPTS[s0]", f"[b]trim=end={XF},setpts=PTS-STARTPTS[head]"]
        d0, d1 = SHOTS[0][2] - XF, SHOTS[1][2]
        parts.append(f"[s0][v1]xfade=transition=fade:duration={XF}:offset={d0 - XF:.3f}[x1]")
        total = d0 - XF + d1
        parts.append(f"[x1][head]xfade=transition=fade:duration={XF}:offset={total - XF:.3f}[out]")
        mp4 = OUT / f"hero-city-{name}.mp4"
        run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(parts), "-map", "[out]", "-an",
             "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-profile:v", "high", "-pix_fmt", "yuv420p",
             "-g", "90", "-movflags", "+faststart", "-maxrate", "1.15M" if name == "1080" else "0.6M", "-bufsize", "2.3M",
             str(mp4)])
        if name == "1080":
            png = OUT / "_poster.png"
            run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-frames:v", "1", str(png)])
            im = Image.open(png).convert("RGB")
            png.unlink()
            for w in (1920, 1280, 720):
                p = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
                base = OUT / f"hero-city-poster-{w}"
                p.save(f"{base}.avif", "AVIF", quality=55, speed=4)
                p.save(f"{base}.webp", "WEBP", quality=76, method=6)
                p.save(f"{base}.jpg", "JPEG", quality=78, optimize=True, progressive=True)
        print(f"{name}: {total:.1f}s")
    for f in sorted(OUT.glob("hero-city*")):
        print(f"  {f.name:<30} {f.stat().st_size / 1024:7.0f} KB")


if __name__ == "__main__":
    main()
