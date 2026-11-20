"""v5 stock photographs from Unsplash (official API), dental subjects only.

Usage:
  .venv/Scripts/python -I tools/v5_stock.py search <results.json> key="search words" [key2="..."] [--per 20] [--orientation landscape]
      Searches (Unsplash+ / premium results are skipped: they are not under the free licence), saves the results and
      writes a numbered contact sheet <results>.jpg for choosing by eye.
  .venv/Scripts/python -I tools/v5_stock.py pick <results.json> name=key:index [...]
      Calls each photo's download_location (required by the API guidelines), saves the original to
      src-assets/stock/v5/<name>.jpg and records photographer + page in src-assets/stock/v5/credits.json.
      Crops and the site-wide grade are done by tools/v5_media.py from content/media.yaml.

Needs UNSPLASH_ACCESS_KEY in the git-ignored .env (50 API requests an hour on a demo key).
Rules: dental subjects only; licensed (Unsplash License) only; stock people are never presented as Arha's patients,
doctors or staff; no before/after or "result" images.
"""
import io
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stock import api, fetch  # noqa: E402  (same API client and CDN fetch as the earlier stock tool)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src-assets" / "stock" / ("smile" if __import__("os").environ.get("STOCK_SMILE") else "v5")
CREDITS = OUT / "credits.json"


def search(path, queries, per=20, orientation=None):
    results = json.loads(path.read_text()) if path.exists() else {}
    for key, q in queries.items():
        params = {"query": q, "per_page": 30, "content_filter": "high"}
        if orientation:
            params["orientation"] = orientation
        data = api("/search/photos", **params)
        keep = [r for r in data["results"] if not r.get("premium") and not r.get("plus")
                and "plus.unsplash.com" not in r["urls"]["raw"]]
        results[key] = [{"id": r["id"], "raw": r["urls"]["raw"], "thumb": r["urls"]["small"], "page": r["links"]["html"],
                         "download": r["links"]["download_location"], "author": r["user"]["name"],
                         "alt": r.get("alt_description") or "", "size": [r["width"], r["height"]]} for r in keep[:per]]
        print(f"{key}: kept {len(results[key])} of {len(data['results'])} (API left: {api.remaining})")
    path.write_text(json.dumps(results, indent=1))
    sheet(path, list(queries), per)


def sheet(path, rows, per):
    results = json.loads(path.read_text())
    tw, th = 260, 180
    im = Image.new("RGB", (tw * 5, th * ((per + 4) // 5) * len(rows)), "white")
    d = ImageDraw.Draw(im)
    y0 = 0
    for key in rows:
        for i, item in enumerate(results[key][:per]):
            t = Image.open(io.BytesIO(fetch(item["thumb"]))).convert("RGB")
            t.thumbnail((tw - 4, th - 4))
            x, y = (i % 5) * tw, y0 + (i // 5) * th
            im.paste(t, (x + 2, y + 2))
            d.rectangle([x + 2, y + 2, x + 100, y + 16], fill="black")
            d.text((x + 5, y + 3), f"{key}:{i}", fill="white")
        y0 += ((len(results[key][:per]) + 4) // 5) * th
    im = im.crop((0, 0, im.width, y0))
    im.save(path.with_suffix(".jpg"), quality=82)
    print("contact sheet:", path.with_suffix(".jpg"))


def pick(path, picks):
    results = json.loads(path.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    credits = json.loads(CREDITS.read_text(encoding="utf-8")) if CREDITS.exists() else {}
    for name, (key, idx) in picks.items():
        item = results[key][idx]
        if credits.get(name, {}).get("id") != item["id"]:
            api(item["download"])  # download tracking, required by the Unsplash API guidelines
            (OUT / f"{name}.jpg").write_bytes(fetch(item["raw"] + "&w=2400&q=85&fm=jpg"))
        credits[name] = {"id": item["id"], "author": item["author"], "page": item["page"], "licence": "Unsplash License",
                         "alt": item["alt"]}
        print(f"{name:<24} {item['author']}  (API left: {getattr(api, 'remaining', '?')})")
    CREDITS.write_text(json.dumps(credits, indent=1, ensure_ascii=False), encoding="utf-8")


def main():
    cmd, path = sys.argv[1], Path(sys.argv[2])
    args = [a for a in sys.argv[3:] if "=" in a]
    if cmd == "search":
        per = int(sys.argv[sys.argv.index("--per") + 1]) if "--per" in sys.argv else 20
        orient = sys.argv[sys.argv.index("--orientation") + 1] if "--orientation" in sys.argv else None
        search(path, dict(a.split("=", 1) for a in args), per, orient)
    elif cmd == "pick":
        picks = {}
        for a in args:
            name, spec = a.split("=", 1)
            key, idx = spec.split(":")
            picks[name] = (key, int(idx))
        pick(path, picks)


if __name__ == "__main__":
    main()
