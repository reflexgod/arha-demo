"""Studio-portrait screening for Arha stock (20 Nov 2026 brief: originally studio-shot photos only, no cutouts).

  python screen.py search POOL.json key="search words" [...] [--pages 2]   Unsplash API (1 call per page per query)
  python screen.py addpool POOL.json OTHER.json                              merge an earlier results file (no API calls)
  python screen.py addpexels POOL.json key=ID,ID,...                         add Pexels photo ids (CDN only, no API)
  python screen.py measure POOL.json                                         thumbnails + measurements (no API calls)
  python screen.py sheet POOL.json OUT.jpg [--all]                           numbered sheet of photos that pass the
                                                                             measured checks (or of all with --all)

Measured checks (they only pre-sort; every pick is still judged by eye against the rules):
  - backdrop: the frame's outer band (top 10%, sides 8% above the shoulders) is light (mean L >= 165) and plain
    (std <= 22): rule 1, a photo shot on a plain light-grey, white or pale backdrop
  - one face (OpenCV YuNet), whose box is at least 14% of the frame height (head-and-shoulders, not a full figure)
Thumbnails are cached in src-assets/stock/studio/thumbs/ (git-ignored with the rest of src-assets).
"""
import io
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from stock import api, fetch  # noqa: E402

THUMBS = ROOT / "src-assets/stock/studio/thumbs"
MODEL = str(ROOT / "tools/stock_smile/models/face_detection_yunet_2023mar.onnx")


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8")) if Path(p).exists() else {}


def save(p, d):
    Path(p).write_text(json.dumps(d, indent=1), encoding="utf-8")


def search(pool, queries, pages=1):
    d = load(pool)
    for key, q in queries.items():
        for page in range(1, pages + 1):
            data = api("/search/photos", query=q, per_page=30, page=page, content_filter="high")
            n = 0
            for r in data["results"]:
                if r.get("premium") or r.get("plus") or "plus.unsplash.com" in r["urls"]["raw"]:
                    continue  # Unsplash+ is not under the free licence
                pid = "u-" + r["id"]
                if pid not in d:
                    d[pid] = {"src": "unsplash", "q": key, "raw": r["urls"]["raw"], "thumb": r["urls"]["small"],
                              "page": r["links"]["html"], "download": r["links"]["download_location"],
                              "author": r["user"]["name"], "alt": r.get("alt_description") or "", "size": [r["width"], r["height"]]}
                    n += 1
            print(f"{key} p{page}: +{n} (total {data['total']}, API left {api.remaining})")
    save(pool, d)


def addpool(pool, other):
    d, o = load(pool), load(other)
    n = 0
    for key, items in o.items():
        for r in items:
            pid = "u-" + r["id"]
            if pid not in d:
                d[pid] = {"src": "unsplash", "q": "old-" + key, "raw": r["raw"], "thumb": r["thumb"], "page": r["page"],
                          "download": r.get("download", ""), "author": r.get("author", ""), "alt": r.get("alt", ""), "size": r.get("size")}
                n += 1
    save(pool, d)
    print("added", n)


def addpexels(pool, groups):
    d = load(pool)
    for key, ids in groups.items():
        for i in ids.split(","):
            i = i.strip()
            if i and "p-" + i not in d:
                d["p-" + i] = {"src": "pexels", "q": key, "raw": f"https://images.pexels.com/photos/{i}/pexels-photo-{i}.jpeg",
                               "thumb": f"https://images.pexels.com/photos/{i}/pexels-photo-{i}.jpeg?auto=compress&w=400",
                               "page": f"https://www.pexels.com/photo/{i}/", "author": "", "alt": ""}
    save(pool, d)


def face(im):
    a = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
    det = cv2.FaceDetectorYN_create(MODEL, "", (a.shape[1], a.shape[0]), 0.7)
    _, fs = det.detect(a)
    return [] if fs is None else [tuple(map(float, f[:4])) for f in fs if f[2] * f[3] > a.shape[0] * a.shape[1] * 0.004]


def measure(pool):
    d = load(pool)
    THUMBS.mkdir(parents=True, exist_ok=True)
    for pid, r in d.items():
        if "m" in r:
            continue
        f = THUMBS / f"{pid}.jpg"
        try:
            if not f.exists():
                f.write_bytes(fetch(r["thumb"]))
            im = Image.open(f).convert("RGB")
        except Exception as e:  # noqa: BLE001
            r["m"] = {"err": str(e)[:80]}
            continue
        g = np.asarray(im.convert("L")).astype(np.float32)
        H, W = g.shape
        fs = face(im)
        band = np.concatenate([g[: int(H * 0.10)].ravel(), g[: int(H * 0.45), : int(W * 0.08)].ravel(), g[: int(H * 0.45), -int(W * 0.08):].ravel()])
        r["m"] = {"bg_l": round(float(band.mean()), 1), "bg_sd": round(float(band.std()), 1), "faces": len(fs),
                  "fh": round(max((f[3] for f in fs), default=0) / H, 3), "wh": [W, H]}
    save(pool, d)
    ok = [p for p, r in d.items() if passes(r)]
    print(len(d), "photos,", len(ok), "pass the measured checks")


def passes(r):
    m = r.get("m", {})
    return m.get("faces") == 1 and m.get("bg_l", 0) >= 165 and m.get("bg_sd", 99) <= 22 and m.get("fh", 0) >= 0.14


def sheet(pool, out, allp=False):
    d = load(pool)
    ids = [p for p, r in d.items() if allp or passes(r)]
    tw, th, cols = 230, 290, 8
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    pages = [ids[i:i + 48] for i in range(0, len(ids), 48)] or [[]]
    outs = []
    for n, chunk in enumerate(pages):
        rows = (len(chunk) + cols - 1) // cols or 1
        s = Image.new("RGB", (cols * tw, rows * th), "white")
        dr = ImageDraw.Draw(s)
        for i, pid in enumerate(chunk):
            im = Image.open(THUMBS / f"{pid}.jpg").convert("RGB")
            im.thumbnail((tw - 6, th - 26))
            x, y = (i % cols) * tw, (i // cols) * th
            s.paste(im, (x + 3, y + 22))
            dr.text((x + 3, y + 3), f"{n * 48 + i} {pid}", fill="black", font=font)
        o = Path(out).with_name(Path(out).stem + f"-{n + 1}.jpg")
        s.save(o, quality=82)
        outs.append(o)
    idx = Path(out).with_suffix(".json")
    idx.write_text(json.dumps(ids, indent=0))
    print(len(ids), "on", len(outs), "sheets:", *outs)


if __name__ == "__main__":
    cmd, pool, *rest = sys.argv[1:]
    if cmd == "search":
        pages = int(rest[rest.index("--pages") + 1]) if "--pages" in rest else 1
        search(pool, dict(a.split("=", 1) for a in rest if "=" in a), pages)
    elif cmd == "addpool":
        addpool(pool, rest[0])
    elif cmd == "addpexels":
        addpexels(pool, dict(a.split("=", 1) for a in rest))
    elif cmd == "measure":
        measure(pool)
    elif cmd == "sheet":
        sheet(pool, rest[0], "--all" in rest)
