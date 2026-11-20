"""v5 media: crop photos and cut videos to the slots in content/media.yaml.

Usage:  .venv/Scripts/python -I tools/v5_media.py [images|videos|all] [name ...]
Writes static/img/<name>-<w>.{avif,webp,jpg}, static/video/<name>-<w>.{mp4,webm} + poster images, and
static/media.json (sizes for width/height attributes, kind real/stock, alt). Sources are never modified.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pillow_heif
import yaml
from PIL import Image, ImageFilter, ImageOps

pillow_heif.register_heif_opener()
ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "static" / "img"
VID = ROOT / "static" / "video"
MANIFEST = ROOT / "static" / "media.json"


def stock_grade(im):
    """One grade for all stock (20 Nov 2026, smile pass: a premium cosmetic-dentistry studio look). Soft, bright and
    slightly desaturated: a light grey-world white balance so every source lands on the same neutral palette, then
    saturation -15%, a whisper of warmth, soft contrast, lifted blacks, held-back highlights (the studio backdrop stays
    off-white, never clipped) and a gentle midtone lift. Teeth are never retouched or whitened."""
    x = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    mean = x.reshape(-1, 3).mean(0)
    x = x * (1 + 0.35 * (mean.mean() / np.maximum(mean, 1e-3) - 1))
    lum = (x @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    x = lum + (x - lum) * 0.85
    x = x * np.array([1.01, 1.0, 0.985], np.float32)
    x = 0.5 + (x - 0.5) * 0.94
    x = 0.045 + x * (0.975 - 0.045)
    x = np.clip(x, 0, 1) ** 0.93
    return Image.fromarray(np.clip(x * 255, 0, 255).astype(np.uint8))


def crop_to(im, ratio, focus, zoom=1.0, place=(0.5, 0.5)):
    """Largest crop of ratio (w, h) that puts the focus point at `place` in the frame (centre by default), as far as
    the edges allow. zoom > 1 takes a tighter crop, which leaves room to move the subject (e.g. clear of a text card)."""
    rw, rh = ratio
    W, H = im.size
    if W / H > rw / rh:
        h, w = H, round(H * rw / rh)
    else:
        w, h = W, round(W * rh / rw)
    w, h = round(w / zoom), round(h / zoom)
    cx, cy = focus[0] * W, focus[1] * H
    left = min(max(0, round(cx - w * place[0])), W - w)
    top = min(max(0, round(cy - h * place[1])), H - h)
    return im.crop((left, top, left + w, top + h))


def save_set(im, name, widths, out=IMG, sharpen=None):
    out.mkdir(parents=True, exist_ok=True)
    done = []
    for w in widths:
        if w > im.width:  # never upscale
            print(f"  ! {name}: source only {im.width}px wide, skipping {w}")
            continue
        h = round(im.height * w / im.width)
        r = im.resize((w, h), Image.LANCZOS)
        if sharpen:
            r = r.filter(ImageFilter.UnsharpMask(radius=sharpen[0], percent=sharpen[1], threshold=sharpen[2]))
        elif w < im.width:
            r = r.filter(ImageFilter.UnsharpMask(radius=0.7, percent=30, threshold=2))
        base = out / f"{name}-{w}"
        r.save(f"{base}.avif", "AVIF", quality=58, speed=4)
        r.save(f"{base}.webp", "WEBP", quality=78, method=6)
        r.save(f"{base}.jpg", "JPEG", quality=80, optimize=True, progressive=True)
        done.append(w)
    return done


def do_image(spec):
    im = ImageOps.exif_transpose(Image.open(ROOT / spec["src"])).convert("RGB")
    if spec.get("flip"):
        im = ImageOps.mirror(im)
    if spec.get("box"):
        # pre-crop to a region of the source, as fractions [left, top, right, bottom]
        l, t, r, b = spec["box"]
        im = im.crop((round(l * im.width), round(t * im.height), round(r * im.width), round(b * im.height)))
    if spec.get("extend_right"):
        # widen a plain studio backdrop so the subject can sit clear of a text card (the added strip lies under the card):
        # each row's backdrop colour at the right edge, smoothed down the column, blended into the photo over a band of
        # columns that are still all backdrop, so no seam shows. The photo itself is never altered past that band.
        e = round(im.width * spec["extend_right"])
        img = np.asarray(im).astype(np.float32)
        col = img[:, -12:].mean(axis=1)  # (H, 3) right-edge colour per row
        ref = np.median(col[: max(2, im.height // 7)], axis=0)  # the backdrop, from the top rows
        ok = np.abs(col - ref).sum(1) <= 30  # rows where the edge is backdrop (not hair, shoulder or clothing)
        ys = np.arange(im.height)
        if ok.sum() >= 2:
            col = np.stack([np.interp(ys, ys[ok], col[ok, c]) for c in range(3)], 1)
        else:
            col = np.repeat(ref[None], im.height, 0)
        sig = im.height / 25
        k = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2); k /= k.sum()
        col = np.stack([np.convolve(np.pad(col[:, c], len(k) // 2, mode="edge"), k, mode="valid")[:im.height] for c in range(3)], 1)
        # fade the last columns into that backdrop colour: invisible over backdrop, a soft falloff over a shoulder or
        # hair that runs off the edge (the plan keeps this band clear of the face)
        bl = max(1, round(im.width * spec.get("extend_fade", 0.12)))
        x = np.linspace(0, 1, bl)
        w = (1 - x * x * (3 - 2 * x))[None, :, None]
        img[:, -bl:] = img[:, -bl:] * w + col[:, None, :] * (1 - w)
        strip = np.repeat(col[:, None, :], e, axis=1)
        im = Image.fromarray(np.clip(np.concatenate([img, strip], 1), 0, 255).astype(np.uint8))
        spec = {**spec, "focus": [spec.get("focus", [0.5, 0.5])[0] * (im.width - e) / im.width, spec.get("focus", [0.5, 0.5])[1]]}
    if spec.get("extend_top"):
        # headroom for tightly framed sources on a plain or blurred backdrop (never above a head that touches the top:
        # slots.py checks): the top row's backdrop colour, interpolated past anything that is not backdrop and blurred
        # along the row, then blended into the photo over a tall band so no seam shows
        t = round(im.height * spec["extend_top"])
        top = np.asarray(im.crop((0, 0, im.width, 12))).astype(np.float32).mean(axis=0)  # (W, 3)
        med = np.median(top, axis=0)
        ok = np.abs(top - med).sum(1) <= 30  # backdrop columns; hair or a frame at the top edge is not copied upward
        xs = np.arange(im.width)
        if ok.sum() >= 2:
            top = np.stack([np.interp(xs, xs[ok], top[ok, c]) for c in range(3)], 1)
        else:
            top = np.repeat(med[None], im.width, 0)
        sig = im.width / 20  # very soft along the row: a wall, no columns
        k = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2); k /= k.sum()
        top = np.stack([np.convolve(np.pad(top[:, c], len(k) // 2, mode="edge"), k, mode="valid")[:im.width] for c in range(3)], 1)
        strip = np.repeat(top[None], t, axis=0)
        img = np.asarray(im).astype(np.float32)
        bl = min(img.shape[0] // 8, max(40, t // 2))  # blend the seam over a tall band so it never shows as a line
        dev = (np.abs(img - med).sum(2) > 45).any(1)  # ...but only through rows that are still all backdrop (never into hair)
        clear = int(np.argmax(dev)) if dev.any() else img.shape[0]
        bl = max(1, min(bl, clear - 4))
        w = (np.linspace(0, 1, bl) ** 1.5)[:, None, None]
        img[:bl] = img[:bl] * w + np.repeat(top[None], bl, 0) * (1 - w)
        tall = Image.fromarray(np.clip(np.concatenate([strip, img], 0), 0, 255).astype(np.uint8))
        focus = spec.get("focus", [0.5, 0.5])
        spec = {**spec, "focus": [focus[0], (focus[1] * im.height + t) / tall.height]}  # focus stays in source fractions
        im = tall
    im = crop_to(im, spec["ratio"], spec.get("focus", [0.5, 0.5]), spec.get("zoom", 1.0), spec.get("place", [0.5, 0.5]))
    if spec["kind"] == "stock":
        im = stock_grade(im)
    if spec.get("grade"):
        im = ffmpeg_grade(im, spec["grade"])
    widths = save_set(im, spec["name"], spec["widths"], sharpen=spec.get("sharpen"))
    rw, rh = spec["ratio"]
    out = {"kind": spec["kind"], "alt": spec["alt"], "widths": widths, "ratio": [rw, rh], "src": spec["src"]}
    if spec.get("pos"):  # object-position for boxes whose shape differs from the file (e.g. phone heroes)
        out["pos"] = spec["pos"]
    return out


def ffmpeg_grade(im, filters):
    """Apply an ffmpeg filter chain (the same grade strings the videos use) to a still."""
    a, b = IMG / "_grade-in.png", IMG / "_grade-out.png"
    IMG.mkdir(parents=True, exist_ok=True)
    im.save(a)
    ffmpeg("-i", str(a), "-vf", filters, str(b))
    out = Image.open(b).convert("RGB")
    out.load()
    a.unlink(); b.unlink()
    return out


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def probe_size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    st = json.loads(out)["streams"][0]
    w, h = st["width"], st["height"]
    rot = next((abs(int(sd.get("rotation", 0))) for sd in st.get("side_data_list", []) if "rotation" in sd), 0)
    return (h, w) if rot in (90, 270) else (w, h)


def do_video(spec):
    src = ROOT / spec["src"]
    W, H = probe_size(src)
    cw, ch = spec["crop"]
    zoom = spec.get("zoom", 1.0)            # > 1 = tighter crop (scaled back up to the output sizes)
    cw, ch = round(cw / zoom), round(ch / zoom)
    grade = ("," + spec["grade"]) if spec.get("grade") else ""   # ffmpeg filters, e.g. eq=contrast=1.1
    if cw > W or ch > H:
        raise SystemExit(f"{spec['name']}: crop {cw}x{ch} larger than source {W}x{H}")
    fx, fy = spec.get("focus", [0.5, 0.5])
    x = min(max(0, round(fx * W - cw / 2)), W - cw)
    y = min(max(0, round(fy * H - ch / 2)), H - ch)
    VID.mkdir(parents=True, exist_ok=True)
    trim = ["-ss", str(spec["start"]), "-t", str(spec["duration"]), "-i", str(src)]
    crf = str(spec.get("crf", 27))
    # audio: true keeps the soundtrack (click-to-play embeds); background loops are always silent
    a264 = ["-c:a", "aac", "-b:a", "96k"] if spec.get("audio") else ["-an"]
    sizes = []
    for w, h in spec["sizes"]:
        vf = f"crop={cw}:{ch}:{x}:{y}{grade},scale={w}:{h}:flags=lanczos,fps=30,format=yuv420p"
        base = VID / f"{spec['name']}-{w}"
        ffmpeg(*trim, *a264, "-vf", vf, "-c:v", "libx264", "-preset", "slow", "-crf", crf, "-profile:v", "high",
               "-movflags", "+faststart", f"{base}.mp4")
        if not spec.get("audio"):  # embeds play the mp4 (AAC works everywhere); loops also get a smaller WebM
            ffmpeg(*trim, "-an", "-vf", vf, "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", str(int(crf) + 11), "-row-mt", "1",
                   "-deadline", "good", "-cpu-used", "2", f"{base}.webm")
        sizes.append([w, h])
    # Poster = the first frame of the cut, so the video starts without a jump; poster_at (seconds into the cut) picks
    # another frame for click-to-play embeds, where the poster is removed when the film starts.
    tmp = VID / f"_{spec['name']}-poster.png"
    big = spec["sizes"][-1]
    ptrim = ["-ss", str(spec["start"] + spec["poster_at"]), "-i", str(src)] if spec.get("poster_at") else trim
    ffmpeg(*ptrim, "-frames:v", "1", "-vf", f"crop={cw}:{ch}:{x}:{y}{grade},scale={big[0]}:{big[1]}:flags=lanczos", str(tmp))
    poster = Image.open(tmp).convert("RGB")
    tmp.unlink()
    pw = save_set(poster, f"{spec['name']}-poster", spec["poster_widths"])
    return {"kind": spec["kind"], "sizes": sizes, "poster_widths": pw, "ratio": list(spec["crop"]), "src": spec["src"],
            "audio": bool(spec.get("audio")), "alt": spec.get("alt", "")}


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    only = set(sys.argv[2:])
    spec = yaml.safe_load((ROOT / "content" / "media.yaml").read_text(encoding="utf-8"))
    man = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"images": {}, "videos": {}}
    for kind in ("images", "videos"):  # a slot deleted from media.yaml leaves the site too (e.g. a doctor photo taken back out)
        keep = {s["name"] for s in spec.get(kind, [])}
        for gone in [n for n in man[kind] if n not in keep]:
            print("dropped", kind, gone)
            del man[kind][gone]
    if what in ("images", "all"):
        for s in spec["images"]:
            if only and s["name"] not in only:
                continue
            print("image", s["name"])
            man["images"][s["name"]] = do_image(s)
    if what in ("videos", "all"):
        for s in spec["videos"]:
            if only and s["name"] not in only:
                continue
            print("video", s["name"])
            man["videos"][s["name"]] = do_video(s)
    MANIFEST.write_text(json.dumps(man, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
