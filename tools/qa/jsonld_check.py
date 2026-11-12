"""Validate the JSON-LD on every built page (dist/) against the schema.org vocabulary and Google's rich-result rules.

Usage: .venv/Scripts/python -I tools/qa/jsonld_check.py <schemaorg-current-https.jsonld>
  The vocabulary file comes from https://schema.org/version/latest/schemaorg-current-https.jsonld (not kept in the repo).

Checks, per page:
  - every <script type="application/ld+json"> parses as JSON;
  - every @type is a schema.org type, and every property is defined for that type (or a supertype);
  - every {"@id": ...} reference points at a node defined on the same page, or is a full URL;
  - Google's required fields: Article (headline, image, datePublished, author.name), FAQPage (Question.name +
    acceptedAnswer.text), BreadcrumbList (position, name, item), ProfilePage (mainEntity), LocalBusiness (name, address),
    Person (name);
  - no AggregateRating / Review markup (self-serving reviews are not allowed, and we have no verified reviews).
Exits 1 on any error. Prints the page types it found.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
S = "schema:"


def load_vocab(path):
    g = json.loads(Path(path).read_text(encoding="utf-8"))["@graph"]
    types, supers, props = set(), {}, {}
    for n in g:
        t = n.get("@type")
        t = t if isinstance(t, list) else [t]
        nid = n["@id"]
        if not nid.startswith(S):
            continue
        name = nid[len(S):]
        if "rdfs:Class" in t:
            types.add(name)
            sc = n.get("rdfs:subClassOf", [])
            sc = sc if isinstance(sc, list) else [sc]
            supers[name] = [x["@id"][len(S):] for x in sc if x["@id"].startswith(S)]
        if "rdf:Property" in t:
            dom = n.get("schema:domainIncludes", [])
            dom = dom if isinstance(dom, list) else [dom]
            props[name] = {d["@id"][len(S):] for d in dom}
        if any(x in t for x in ("schema:DataType",)) or name in ("Text", "URL", "Date", "DateTime", "Number", "Boolean", "Integer"):
            types.add(name)
    return types, supers, props


def ancestors(t, supers, seen=None):
    seen = seen or set()
    for s in supers.get(t, []):
        if s not in seen:
            seen.add(s)
            ancestors(s, supers, seen)
    return seen | {t}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    types, supers, props = load_vocab(sys.argv[1])
    errors, found = [], Counter()
    pages = sorted(DIST.rglob("*.html"))
    for f in pages:
        url = "/" + f.relative_to(DIST).as_posix().replace("index.html", "")
        html = f.read_text(encoding="utf-8")
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        if not blocks and "noindex" not in url and url != "/404.html":
            pass
        ids, refs, nodes = set(), [], []
        for raw in blocks:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                errors.append(f"{url}: JSON does not parse: {e}")
                continue

            def walk(n, parent_types=None):
                if isinstance(n, list):
                    for x in n:
                        walk(x, parent_types)
                    return
                if not isinstance(n, dict):
                    return
                if set(n) == {"@id"}:
                    refs.append(n["@id"])
                    return
                t = n.get("@type")
                tl = t if isinstance(t, list) else ([t] if t else [])
                if "@id" in n:
                    ids.add(n["@id"])
                if tl:
                    nodes.append((tl, n))
                for x in tl:
                    found[x] += 1
                    if x not in types:
                        errors.append(f"{url}: unknown type {x}")
                allowed = set()
                for x in tl:
                    allowed |= ancestors(x, supers)
                for k, v in n.items():
                    if k.startswith("@"):
                        continue
                    if k not in props:
                        errors.append(f"{url}: unknown property {k} on {tl}")
                    elif tl and not (props[k] & allowed):
                        errors.append(f"{url}: property {k} is not defined for {tl}")
                    walk(v, tl)

            walk(data.get("@graph", data))
        for r in refs:
            if r not in ids and not r.startswith("http"):
                errors.append(f"{url}: @id reference {r} is not defined on the page")
            elif r not in ids:
                errors.append(f"{url}: @id reference {r} has no node on this page (Google can't join it)")
        for tl, n in nodes:
            def need(cond, what):
                if not cond:
                    errors.append(f"{url}: {tl[0]} missing {what}")
            if "Article" in tl:
                need(n.get("headline"), "headline"); need(n.get("image"), "image"); need(n.get("datePublished"), "datePublished")
                need(isinstance(n.get("author"), dict) and n["author"].get("name"), "author.name")
                need(len(n.get("headline", "")) <= 110, "headline ≤ 110 chars")
            if "FAQPage" in tl:
                for q in n.get("mainEntity", []):
                    need(q.get("@type") == "Question" and q.get("name"), "Question.name")
                    need(q.get("acceptedAnswer", {}).get("text"), "acceptedAnswer.text")
            if "BreadcrumbList" in tl:
                for i, li in enumerate(n.get("itemListElement", [])):
                    need(li.get("position") == i + 1 and li.get("name") and li.get("item"), "ListItem position/name/item")
            if "ProfilePage" in tl:
                need(n.get("mainEntity"), "mainEntity")
            if "LocalBusiness" in tl:
                need(n.get("name") and n.get("address"), "name/address")
            if "Person" in tl:
                need(n.get("name"), "name")
            if {"AggregateRating", "Review"} & set(tl):
                errors.append(f"{url}: review/rating markup is not allowed")
    print(f"{len(pages)} pages, types found: " + ", ".join(f"{k}×{v}" for k, v in sorted(found.items())))
    if errors:
        print("\n".join("  ERROR " + e for e in sorted(set(errors))))
        sys.exit(1)
    print("JSON-LD OK")


if __name__ == "__main__":
    main()
