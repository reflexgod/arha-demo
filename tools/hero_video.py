"""Hero video for the web (7 Nov 2026 brief): re-encodes the graded clinic walkthrough loop made by tools/video.py
(hero-land-1080.mp4, kept as hero-land-master.mp4) into small files, and writes the WebP posters from its first frame.

  hero-land-1080.mp4 / hero-land-720.mp4    H.264, CRF 28, no audio, faststart (targets: < 3 MB and < 1.5 MB)
  hero-land-1080.webm / hero-land-720.webm  VP9, constant quality, no audio
  hero-poster-land-{768,1280,1920}.webp     the first frame, for the <picture> srcset and the preload

Run: .venv/Scripts/python -I tools/hero_video.py
"""
import subprocess
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "assets" / "video"
MASTER = OUT.parent.parent / "src-assets" / "hero-land-master.mp4"  # git-ignored, never published


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    if not MASTER.exists():
        (OUT / "hero-land-1080.mp4").rename(MASTER)  # first run only: the tools/video.py loop becomes the master
    common = ["-map", "0:v:0", "-an", "-pix_fmt", "yuv420p", "-g", "60"]
    for name, scale in (("1080", "1920:1080"), ("720", "1280:720")):
        vf = ["-vf", f"scale={scale}:flags=lanczos"]
        run(["ffmpeg", "-v", "error", "-y", "-i", str(MASTER), *common, *vf, "-c:v", "libx264", "-preset", "slower",
             "-crf", "28", "-profile:v", "high", "-movflags", "+faststart",
             "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", str(OUT / f"hero-land-{name}.mp4")])
        run(["ffmpeg", "-v", "error", "-y", "-i", str(MASTER), *common, *vf, "-c:v", "libvpx-vp9", "-b:v", "0",
             "-crf", "40" if name == "1080" else "38", "-row-mt", "1", "-deadline", "good", "-cpu-used", "2",
             str(OUT / f"hero-land-{name}.webm")])
    png = OUT / "_hero-first.png"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(MASTER), "-frames:v", "1", str(png)])
    im = Image.open(png).convert("RGB")
    png.unlink()
    for w in (768, 1280, 1920):
        im.resize((w, round(w * 9 / 16)), Image.LANCZOS).save(OUT / f"hero-poster-land-{w}.webp", "WEBP", quality=74, method=6)
    for f in sorted(OUT.glob("hero-land-*")) + sorted(OUT.glob("hero-poster-land-*.webp")):
        print(f"  {f.name:<28} {f.stat().st_size / 1024:8.0f} KB")


if __name__ == "__main__":
    main()
