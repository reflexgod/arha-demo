#!/bin/sh
# Lighthouse mobile (simulated slow 4G, 4x CPU), N runs, prints each run and the median by Performance.
#   sh tools/qa/lh.sh <outdir> <url> [runs]     e.g. sh tools/qa/lh.sh /tmp/lh http://127.0.0.1:8080/ 3
# Serve the site with tools/qa/gzserve.py first (GitHub Pages gzips; http.server does not).
out=$1; url=$2; runs=${3:-3}
mkdir -p "$out"
for i in $(seq 1 "$runs"); do
  npx --yes lighthouse@12 "$url" --quiet --output=json --output-path="$out/run-$i.json" \
    --chrome-path="C:/Program Files/Google/Chrome/Application/chrome.exe" --chrome-flags="--headless=new" >/dev/null 2>&1
done
node -e '
const fs=require("fs");const [out,runs]=process.argv.slice(1);
const rows=[];for(let i=1;i<=+runs;i++){const r=JSON.parse(fs.readFileSync(`${out}/run-${i}.json`));const c=r.categories,a=r.audits;
rows.push({perf:Math.round(c.performance.score*100),a11y:Math.round(c.accessibility.score*100),bp:Math.round(c["best-practices"].score*100),seo:Math.round(c.seo.score*100),fcp:a["first-contentful-paint"].numericValue,lcp:a["largest-contentful-paint"].numericValue,tbt:a["total-blocking-time"].numericValue,cls:a["cumulative-layout-shift"].numericValue});}
const f=r=>`perf ${r.perf} a11y ${r.a11y} bp ${r.bp} seo ${r.seo} | FCP ${(r.fcp/1000).toFixed(1)}s LCP ${(r.lcp/1000).toFixed(1)}s TBT ${Math.round(r.tbt)}ms CLS ${r.cls.toFixed(3)}`;
rows.forEach((r,i)=>console.log(`run ${i+1}: ${f(r)}`));
const med=rows.map(r=>r.perf).sort((a,b)=>a-b)[Math.floor(rows.length/2)];
console.log(`median: ${f(rows.find(r=>r.perf===med))}`);
' "$out" "$runs"
