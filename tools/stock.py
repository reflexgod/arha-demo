"""Demo stock photography from Unsplash, through the official API.

Usage:
  .venv/Scripts/python -I tools/stock.py search <results.json> key="search words" [key2="..."] [--per 12] [--orientation portrait]
      Searches, keeps the results and writes a numbered contact sheet (<results>.jpg) for choosing.
  .venv/Scripts/python -I tools/stock.py sheet <results.json>
      Rebuilds the contact sheet from saved results (no API calls; the demo key allows 50 an hour).
  .venv/Scripts/python -I tools/stock.py pick <results.json> name=key:index:"where it is used" [...]
      For each pick: calls the photo's download_location (Unsplash API guidelines: a download must be
      tracked), downloads the original to src-assets/stock/<name>.jpg, applies the one stock grade
      (photos.stock_grade), exports assets/img/stock-<name>-<w>.{avif,webp,jpg} and adds the
      photographer credit to notes/credits.md.

The access key is read from UNSPLASH_ACCESS_KEY in .env (a file, or text files in a .env folder),
which is git-ignored. Stock is for the demo only; it is never presented as Arha's patients or doctors.
Selection rules: natural light, muted warm palette, South Asian / Indian faces where people appear,
no over-whitened smiles. Arha's own clinic photos come first wherever they fit.
"""
import http.client
import io
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from photos import export, stock_grade  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src-assets" / "stock"
API = "https://api.unsplash.com"
UTM = "?utm_source=arha_dental_care_demo&utm_medium=referral"


def access_key():
    env = ROOT / ".env"
    files = [env] if env.is_file() else sorted(env.glob("*")) if env.is_dir() else []
    for f in files:
        for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = re.match(r"\s*UNSPLASH_ACCESS_KEY\s*[=:]\s*(\S+)", line)
            if m:
                return m.group(1).strip("'\"")
    raise SystemExit("UNSPLASH_ACCESS_KEY not found in .env")


def api(path, **params):
    url = path if path.startswith("http") else f"{API}{path}"
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Client-ID {access_key()}", "Accept-Version": "v1"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            api.remaining = r.headers.get("X-Ratelimit-Remaining")
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            raise SystemExit("Unsplash rate limit reached (demo keys allow 50 requests an hour). Try again later.")
        raise


def search(out, queries, per=12, orientation=None):
    results = json.loads(out.read_text()) if out.exists() else {}
    for key, q in queries.items():
        params = {"query": q, "per_page": 30, "content_filter": "high"}
        if orientation:
            params["orientation"] = orientation
        data = api("/search/photos", **params)
        results[key] = [{"id": r["id"], "raw": r["urls"]["raw"], "thumb": r["urls"]["small"], "page": r["links"]["html"],
                         "download": r["links"]["download_location"], "author": r["user"]["name"],
                         "profile": r["user"]["links"]["html"], "alt": r.get("alt_description") or "",
                         "size": [r["width"], r["height"]]} for r in data["results"][:per]]
        print(f"{key}: {len(results[key])} of {data['total']}")
    out.write_text(json.dumps(results, indent=1))
    sheet(out, list(queries), per)


def fetch(url, tries=3):
    """Image bytes from Unsplash's CDN (not an API call), retried on a dropped connection."""
    for n in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "arha-demo"})
            return urllib.request.urlopen(req, timeout=120).read()
        except (OSError, http.client.IncompleteRead):
            if n == tries - 1:
                raise


def sheet(out, rows=None, per=12):
    """Numbered contact sheet (<results>.jpg) of saved search results; no API calls."""
    results = json.loads(out.read_text())
    rows = rows or list(results)
    tw, th = 240, 180
    sheet = Image.new("RGB", (tw * per, th * len(rows)), "white")
    d = ImageDraw.Draw(sheet)
    for y, key in enumerate(rows):
        for x, item in enumerate(results[key][:per]):
            im = Image.open(io.BytesIO(fetch(item["thumb"]))).convert("RGB")
            im.thumbnail((tw - 4, th - 4))
            sheet.paste(im, (x * tw + 2, y * th + 2))
            d.rectangle([x * tw + 2, y * th + 2, x * tw + 92, y * th + 16], fill="black")
            d.text((x * tw + 5, y * th + 3), f"{key}:{x}", fill="white")
    sheet.save(out.with_suffix(".jpg"), quality=80)
    print("contact sheet:", out.with_suffix(".jpg"))


def pick(results_path, picks):
    results = json.loads(Path(results_path).read_text())
    SRC.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, (key, idx, use) in picks.items():
        item = results[key][idx]
        api(item["download"])  # required by the API guidelines when a photo is downloaded
        src = SRC / f"{name}.jpg"
        if not src.exists():
            src.write_bytes(fetch(item["raw"] + "&w=2400&q=85&fm=jpg"))
        im = stock_grade(Image.open(src).convert("RGB"))
        files, size = export(im, f"stock-{name}")
        rows.append(f"| `assets/img/stock-{name}-*` | {use} | [{item['author']}]({item['profile']}{UTM}) | {item['page']}{UTM} (Unsplash License) |")
        print(f"{name:<22} {size[0]}x{size[1]}  {item['author']}  (API calls left this hour: {api.remaining})")
    credits = ROOT / "notes" / "credits.md"
    text = credits.read_text(encoding="utf-8") if credits.exists() else ""
    head = "\n## v2 stock (Unsplash API, graded with photos.stock_grade)\n\n| File | Used for | Photographer | Source |\n|---|---|---|---|\n"
    new = [r for r in rows if r.split("|")[1] not in text]
    if new:
        if head.strip() not in text:
            text = text.rstrip() + "\n" + head
        credits.write_text(text.rstrip() + "\n" + "\n".join(new) + "\n", encoding="utf-8", newline="\n")


def main():
    cmd, path = sys.argv[1], Path(sys.argv[2])
    args = [a for a in sys.argv[3:] if "=" in a]
    if cmd == "search":
        per = int(sys.argv[sys.argv.index("--per") + 1]) if "--per" in sys.argv else 12
        orient = sys.argv[sys.argv.index("--orientation") + 1] if "--orientation" in sys.argv else None
        search(path, dict(a.split("=", 1) for a in args), per, orient)
    elif cmd == "sheet":
        sheet(path)
    elif cmd == "pick":
        picks = {}
        for a in args:
            name, spec = a.split("=", 1)
            key, idx, use = spec.split(":", 2)
            picks[name] = (key, int(idx), use)
        pick(path, picks)


if __name__ == "__main__":
    main()
