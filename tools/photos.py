"""Process the clinic photos: honest corrections + responsive exports.

Usage: .venv/Scripts/python -I tools/photos.py [--only <substring>] [--debug <dir>]
Reads src-assets/*.jpg|*.jpeg (real JPEG or iPhone HEIC), writes assets/img/<name>-<w>.{avif,webp,jpg}.

Corrections (only what is honest, nothing is retouched):
  1. Display P3 -> sRGB using the embedded ICC profile; EXIF (incl. GPS) is stripped.
  2. Straighten verticals: near-vertical edges give the vertical vanishing point, the virtual camera
     is rotated level (H = K R K^-1, focal length from EXIF) and the result cropped to the valid area.
  3. Gentle white balance (neutral-highlight reference, max +/-6% per channel) and exposure.
"""
import argparse
import io
import json
from pathlib import Path

import cv2
import numpy as np
import pillow_heif
from PIL import Image, ImageCms, ImageFilter, ImageOps

pillow_heif.register_heif_opener()

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "src-assets", ROOT / "assets" / "img"
WIDTHS = (640, 1280, 1920)
SRGB = ImageCms.createProfile("sRGB")

# Per-photo settings. upright: correct verticals; crop: extra (left, top, right, bottom) fractions.
PHOTOS = {
    "arha-dental-care-exterior-dental-clinic-peddar-road": {"wb": (0.9, 0.14)},  # warm tungsten cast on a white wall
    "arha-dental-care-logo-dental-clinic-peddar-road": {"upright": False},
    "arha-dental-care-reception-south-mumbai-dental-clinic-01": {},
    "arha-dental-care-reception-south-mumbai-dental-clinic-02": {},
    "autoclave-pantry-equipment-arha-dental-care-mumbai": {},
    "dental-dentistry-equipment-arha-dental-care-mumbai": {"upright": False},
    "dental-implant-equipment-arha-dental-care-mumbai": {},
    "dental-operatory-arha-dental-care-peddar-road-01": {},
    "dental-operatory-arha-dental-care-peddar-road-02": {},
    "dental-operatory-arha-dental-care-peddar-road-04": {},
    "dental-operatory-arha-dental-care-peddar-road-06": {},
    # Lower two-thirds of reception-01 for the full-bleed "calm" band (the wall logo sits at the photo's
    # top edge and would otherwise show cut off at some widths)
    "arha-dental-care-reception-south-mumbai-dental-clinic-01-lower": {
        "src": "arha-dental-care-reception-south-mumbai-dental-clinic-01.jpg", "crop": (0, 0.36, 0, 0)},
    # Still from the walkthrough video (IMG_2303.MOV @ ~76-78.6 s, sharpest frame, HLG tone-mapped)
    "arha-dental-care-lounge-peddar-road": {"src": "derived/arha-dental-care-lounge-peddar-road.png", "upright": False},
}


def load_srgb(path):
    im = Image.open(path)
    f35 = im.getexif().get_ifd(0x8769).get(0xA405)
    icc = im.info.get("icc_profile")
    im = ImageOps.exif_transpose(im).convert("RGB")
    if icc:
        im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), SRGB,
                                       renderingIntent=ImageCms.Intent.PERCEPTUAL, outputMode="RGB")
    return im, f35


def vertical_fit(rgb):
    """Fit slope k = a*x0 + b over near-vertical segments (x0 = x at the centre row, centred coords)."""
    h, w = rgb.shape[:2]
    s = 1600 / max(h, w)
    gray = cv2.cvtColor(cv2.resize(rgb, None, fx=s, fy=s, interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    segs = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD).detect(gray)[0]
    if segs is None:
        return None
    x1, y1, x2, y2 = (segs.reshape(-1, 4) / s).T
    dx, dy = x2 - x1, y2 - y1
    length = np.hypot(dx, dy)
    keep = (length > 0.06 * min(w, h)) & (np.abs(dx) < np.tan(np.radians(18)) * np.abs(dy))
    if keep.sum() < 6:
        return None
    sgn = np.sign(dy[keep])
    dx, dy, length = dx[keep] * sgn, dy[keep] * sgn, length[keep]
    k = dx / dy
    xm, ym = (x1[keep] + x2[keep]) / 2 - w / 2, (y1[keep] + y2[keep]) / 2 - h / 2
    x0 = xm - k * ym
    rng = np.random.default_rng(7)
    best, best_score = None, -1
    for _ in range(3000):
        i, j = rng.choice(len(k), 2, replace=False)
        if abs(x0[i] - x0[j]) < 0.08 * w:
            continue
        a = (k[i] - k[j]) / (x0[i] - x0[j])
        b = k[i] - a * x0[i]
        inl = np.abs(k - (a * x0 + b)) < 0.006
        score = length[inl].sum()
        if score > best_score:
            best, best_score = inl, score
    if best is None or best.sum() < 5:
        return None
    A = np.stack([x0[best], np.ones(best.sum())], 1) * length[best, None]
    a, b = np.linalg.lstsq(A, k[best] * length[best], rcond=None)[0]
    return a, b, int(best.sum()), int(len(k))


def upright(im, f35):
    rgb = np.asarray(im)
    h, w = rgb.shape[:2]
    fit = vertical_fit(rgb)
    if fit is None:
        return im, "no fit"
    a, b, n_in, n = fit
    f = (f35 or 26) * np.hypot(w, h) / 43.27
    u = np.array([-b, -1.0, a * f])
    u /= np.linalg.norm(u)
    t = np.array([0.0, -1.0, 0.0])
    v, c = np.cross(u, t), float(u @ t)
    sv = np.linalg.norm(v)
    pitch, roll = np.degrees(np.arctan(a * f)), np.degrees(np.arctan(b))
    if sv < 1e-6 or abs(pitch) > 22 or abs(roll) > 6:
        return im, f"skipped (pitch {pitch:.1f}, roll {roll:.1f})"
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    R = np.eye(3) + vx + vx @ vx * ((1 - c) / sv ** 2)
    K = np.array([[f, 0, w / 2], [0, f, h / 2], [0, 0, 1]])
    H = K @ R @ np.linalg.inv(K)
    corners = cv2.perspectiveTransform(np.float32([[[0, 0]], [[w, 0]], [[w, h]], [[0, h]]]), H).reshape(4, 2)
    tl, tr, br, bl = corners
    left, right = max(tl[0], bl[0]), min(tr[0], br[0])
    top, bottom = max(tl[1], tr[1]), min(bl[1], br[1])
    T = np.array([[1, 0, -left], [0, 1, -top], [0, 0, 1]])
    ow, oh = int(right - left), int(bottom - top)
    out = cv2.warpPerspective(rgb, T @ H, (ow, oh), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(out), f"pitch {pitch:+.1f} deg, roll {roll:+.2f} deg, {n_in}/{n} edges, kept {ow * oh / (w * h):.0%}"


def tone(im, strength=0.6, limit=0.06):
    """Gentle white balance + exposure."""
    x = np.asarray(im).astype(np.float32)
    lum = x @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    chroma = x.max(2) - x.min(2)
    bright = lum > np.percentile(lum, 55)
    cand = bright & (chroma <= np.percentile(chroma[bright], 30))
    means = x[cand].mean(0)
    gains = np.clip(1 + strength * (means.mean() / means - 1), 1 - limit, 1 + limit)
    x *= gains
    lum = x @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    lo, hi = np.percentile(lum, 0.3), np.percentile(lum, 99.7)
    white = np.clip(hi / 250, 0.9, 1.0) * 255 if hi < 250 else 255.0
    black = min(lo, 6.0) * 0.5
    x = (x - black) * (255 / (white - black))
    note = f"wb gains {np.round(gains, 3).tolist()}, levels black {black:.1f} white {white:.0f}"
    return Image.fromarray(np.clip(x, 0, 255).astype(np.uint8)), note


def export(im, name):
    files = {}
    widths = [w for w in WIDTHS if w < im.width] + ([im.width] if im.width < WIDTHS[-1] else [])
    for w in widths[:3]:
        h = round(im.height * w / im.width)
        r = im.resize((w, h), Image.LANCZOS)
        if w < im.width:
            r = r.filter(ImageFilter.UnsharpMask(radius=0.8, percent=35, threshold=2))
        base = OUT / f"{name}-{w}"
        r.save(f"{base}.avif", "AVIF", quality=60, speed=4)
        r.save(f"{base}.webp", "WEBP", quality=78, method=6)
        r.save(f"{base}.jpg", "JPEG", quality=78, optimize=True, progressive=True)
        files[w] = {ext: round((Path(f"{base}.{ext}").stat().st_size) / 1024) for ext in ("avif", "webp", "jpg")}
    return files, (im.width, im.height)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--debug")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for name, opts in PHOTOS.items():
        if args.only and args.only not in name:
            continue
        src = SRC / opts["src"] if "src" in opts else next(SRC.glob(name + ".*"))
        im, f35 = load_srgb(src)
        before = im
        note_u = "upright off"
        if opts.get("upright", True):
            im, note_u = upright(im, f35)
        if "crop" in opts:
            l, t, r, b = opts["crop"]
            im = im.crop((round(l * im.width), round(t * im.height), round(im.width * (1 - r)), round(im.height * (1 - b))))
        im, note_t = tone(im, *opts.get("wb", (0.6, 0.06)))
        files, size = export(im, name)
        manifest[name] = {"size": size, "files_kb": files, "upright": note_u, "tone": note_t}
        print(f"{name[:48]:<48} {size[0]}x{size[1]}  {note_u}  |  {note_t}  |  1280: {files.get(1280)}")
        if args.debug:
            d = Path(args.debug)
            d.mkdir(parents=True, exist_ok=True)
            a, b = before.copy(), im.copy()
            a.thumbnail((900, 900))
            b.thumbnail((900, 900))
            pair = Image.new("RGB", (a.width + b.width + 20, max(a.height, b.height)), "white")
            pair.paste(a, (0, 0))
            pair.paste(b, (a.width + 20, 0))
            pair.save(d / f"{name}.jpg", quality=80)
    manifest_path.write_text(json.dumps(manifest, indent=1))


if __name__ == "__main__":
    main()
