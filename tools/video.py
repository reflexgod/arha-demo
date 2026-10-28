"""Build the home-page hero loop from the iPhone clinic walkthrough.

Usage: .venv/Scripts/python -I tools/video.py            (hero loop)
       .venv/Scripts/python -I tools/video.py --tour     (clinic tour for The practice)
Source: src-assets/IMG_2303.MOV (1080x1920 portrait, HEVC 10-bit HLG). The 30 s tour MP4 is the same
footage pillarboxed at ~608px wide, so the original MOV is used.

Output (assets/video/), muted, H.264 MP4 + VP9 WebM, about 12 s, seamless loop:
  hero-land-1080.mp4 / hero-land-720.{mp4,webm}  16:9 band cropped from the portrait frame (desktop)
  hero-port-720.{mp4,webm}                       full portrait frame (phones)
  hero-poster-{land-1920,land-1280,port-720}.{avif,webp,jpg}   first frame of each loop
Grade: HLG tone-mapped to SDR, then soft and calm: saturation 0.86, contrast 0.96, lifted shadows.
"""
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src-assets" / "IMG_2303.MOV"
OUT = ROOT / "assets" / "video"
XF = 0.8  # crossfade seconds

# (start, duration, vertical centre of the 16:9 band as a fraction of frame height)
SHOTS = [
    (10.0, 4.0, 0.36),  # reception: logo wall and desk (first frame = poster)
    (32.0, 4.5, 0.33),  # operatory: chair and light against the window (steadiest section)
    (57.0, 4.0, 0.40),  # second operatory through the glass door
    (75.6, 3.4, 0.55),  # lounge: sofa and plant
]
TONEMAP = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
GRADE = "eq=saturation=0.86:contrast=0.96,curves=master='0/0.04 0.5/0.515 1/0.975'"
VARIANTS = {
    "land-1080": dict(band=True, scale="1920:1080", sharpen=True),
    "land-720": dict(band=True, scale="1280:720"),
    "port-720": dict(band=False, scale="720:1280"),
}


def graph(v):
    parts, labels = [], []
    for i, (_, _, centre) in enumerate(SHOTS):
        crop = f"crop=1080:608:0:'min(max(0,{centre}*ih-304),ih-608)'," if v["band"] else ""
        sharpen = ",unsharp=5:5:0.35" if v.get("sharpen") else ""
        parts.append(f"[{i}:v]{TONEMAP},{GRADE},{crop}scale={v['scale']}:flags=lanczos{sharpen},"
                     f"fps=30000/1001,format=yuv420p,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[v{i}]")
        labels.append(f"v{i}")
    # Seamless loop: the first XF seconds of shot 1 are moved to the end and crossfaded in.
    parts.append(f"[v0]split[v0a][v0b]")
    parts.append(f"[v0a]trim=start={XF},setpts=PTS-STARTPTS[s0]")
    parts.append(f"[v0b]trim=end={XF},setpts=PTS-STARTPTS[head]")
    seq = ["s0"] + labels[1:] + ["head"]
    durs = [SHOTS[0][1] - XF] + [s[1] for s in SHOTS[1:]] + [XF]
    acc, prev = durs[0], seq[0]
    for k, (lab, d) in enumerate(zip(seq[1:], durs[1:]), 1):
        out = "out" if k == len(seq) - 1 else f"x{k}"
        parts.append(f"[{prev}][{lab}]xfade=transition=fade:duration={XF}:offset={acc - XF:.3f}[{out}]")
        acc, prev = acc - XF + d, out
    return ";".join(parts), acc


def run(cmd):
    subprocess.run(cmd, check=True)


def tour():
    """The clinic tour for The practice page: the whole walkthrough, portrait, no sound.
    (The supplied tour MP4 is this footage pillarboxed at ~608px, so the original MOV is used.)
    Output: tour-720.{mp4,webm}, tour-1080.mp4, tour-poster-{720,1080}.{avif,webp,jpg} (frame at 10.5 s, reception)."""
    vf = f"{TONEMAP},{GRADE},scale={{}}:flags=lanczos,fps=30000/1001,format=yuv420p,setsar=1"
    for name, scale, crf in (("720", "720:1280", "27"), ("1080", "1080:1920", "28")):
        mp4 = OUT / f"tour-{name}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-map", "0:v:0", "-an", "-vf", vf.format(scale),
             "-c:v", "libx264", "-preset", "slow", "-crf", crf, "-profile:v", "high", "-pix_fmt", "yuv420p",
             "-g", "60", "-movflags", "+faststart",
             "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", str(mp4)])
        png = OUT / f"_tour-{name}.png"
        run(["ffmpeg", "-v", "error", "-y", "-ss", "10.5", "-i", str(mp4), "-frames:v", "1", str(png)])
        im = Image.open(png).convert("RGB")
        png.unlink()
        base = OUT / f"tour-poster-{name}"
        im.save(f"{base}.avif", "AVIF", quality=55, speed=4)
        im.save(f"{base}.webp", "WEBP", quality=75, method=6)
        im.save(f"{base}.jpg", "JPEG", quality=76, optimize=True, progressive=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(OUT / "tour-720.mp4"), "-an", "-c:v", "libvpx-vp9", "-b:v", "0",
         "-crf", "38", "-row-mt", "1", "-deadline", "good", "-cpu-used", "2", "-g", "60", str(OUT / "tour-720.webm")])
    for f in sorted(OUT.glob("tour-*")):
        print(f"  {f.name:<28} {f.stat().st_size / 1024:8.0f} KB")


def main():
    import sys
    if "--tour" in sys.argv:
        return tour()
    OUT.mkdir(parents=True, exist_ok=True)
    inputs = []
    for start, dur, _ in SHOTS:
        inputs += ["-ss", str(start), "-t", str(dur), "-i", str(SRC)]
    for name, v in VARIANTS.items():
        fg, total = graph(v)
        mp4 = OUT / f"hero-{name}.mp4"
        run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fg, "-map", "[out]", "-an",
             "-c:v", "libx264", "-preset", "slow", "-crf", "24" if name == "land-1080" else "25",
             "-profile:v", "high", "-pix_fmt", "yuv420p", "-g", "60", "-movflags", "+faststart",
             "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", str(mp4)])
        if name != "land-1080":
            run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-an", "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "36",
                 "-row-mt", "1", "-deadline", "good", "-cpu-used", "2", "-g", "60", str(OUT / f"hero-{name}.webm")])
        # Poster = exact first frame of the loop
        png = OUT / f"_poster-{name}.png"
        run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-frames:v", "1", str(png)])
        im = Image.open(png).convert("RGB")
        png.unlink()
        sizes = {"land-1080": [("land-1920", 1920), ("land-1280", 1280)], "port-720": [("port-720", 720)]}.get(name, [])
        for pname, w in sizes:
            p = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            base = OUT / f"hero-poster-{pname}"
            p.save(f"{base}.avif", "AVIF", quality=55, speed=4)
            p.save(f"{base}.webp", "WEBP", quality=75, method=6)
            p.save(f"{base}.jpg", "JPEG", quality=76, optimize=True, progressive=True)
        print(f"{name}: {total:.2f}s")
    for f in sorted(OUT.iterdir()):
        print(f"  {f.name:<28} {f.stat().st_size / 1024:8.0f} KB")


if __name__ == "__main__":
    main()
