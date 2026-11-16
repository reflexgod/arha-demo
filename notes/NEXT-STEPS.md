# Arha v5: next steps (read this first)

Updated 13 Nov 2026 (after Step 4) so a fresh session can continue with no chat history. Branch `v5`.
Preview: https://arha-v5.pages.dev (Cloudflare Pages builds `python tools/build.py` -> `dist/` on every push to `v5`;
noindexed).

## 0. 16 Nov 2026: owner fixes (alignment, images, polish), pushed to v5
- **Cards:** every card grid has one 4:3 media box (object-fit: cover); home cards, blog cards and "more from the blog" use
  CSS subgrid, so headings, body text and buttons start on the same line across a row (flex fallback without subgrid).
  The home film is re-cut at 4:3. Related-treatment and team cards push their button to the bottom.
- **Blog listing:** topic chips in one centred row above an even 3/2/1-column grid; quiet meta line (small sans,
  category + minutes), sentence-case chips, small outlined "Read more" button. The same meta line is on the posts.
- **Images:** all Western studio stock is gone. Stock is now Indian patients and families (Unsplash only) in one warm grade
  (stock_grade in tools/v5_media.py); real clinic photos on the root-canal home card and the general-dentistry hub.
  Full list with source URLs and licences: notes/IMAGE-SOURCES.md (the v4 list is in IMAGE-SOURCES-v4-archive.md).
  New Unsplash originals are src-assets/stock/v5/in-*.jpg; the people library is src-assets/stock/people/ (provenance
  in `git show c45ca34:tools/people.json`).
- **QA:** a card-row alignment audit (media heights, heading tops, button tops per row) is clean on all 30 pages at
  1440/1280/768/390, with no horizontal overflow.

## 1. Current state (done)
- **Pages (35):** home, the practice (gallery + walk-through), treatments hub + 12 treatment pages, emergency page,
  for-patients, contact, referrals, International & NRI hub (noindex, not linked yet), blog index + 7 posts,
  2 doctor profiles (/doctors/dr-nikhil-v-jain/, /doctors/dr-vasant-p-jain/), 5 policies, 404.
- **Step 4 (13 Nov):**
  - Blog engine: author byline, reading time, FAQ accordion + FAQPage, related treatments, booking CTA band.
  - Four seed posts from the keyword map, 1,037–1,120 words each: implant timeline, root canal pain, a child's first
    visit, implant cost (no prices).
  - Doctor profile pages: ProfilePage + full Person schema, logo placeholder portrait.
  - Reviews band ON (13 Nov, Viraaj approved), homepage only: 8 featured Google reviews word for word from
    content/google-reviews.json, header "5.0 on Google · 33 reviews", Read more toggle, no review schema.
  - Parity checklist finished (notes/parity-checklist.md).
  - JSON-LD validator: `tools/qa/jsonld_check.py`.
- **"Medically reviewed by" line:** each post has `reviewed: ""`. The line and the MedicalWebPage reviewedBy schema only
  appear once Dr. Nikhil V. Jain has read the post and the date is filled in. Do not launch the blog before that.
- **Stock-photo rule on posts and profiles:** blog heroes on posts signed by Dr. Nikhil are people-free, and the
  treatment cards on doctor pages are text-only, so no stock dentist ever sits next to a doctor's name.
- **Forms backend live** (7df4825): Google Apps Script web app (`tools/forms/arha-forms.gs`). Turnstile site key is in
  site.yaml; the secret is only in Apps Script properties. GA4 `G-J6TW5GWFYL` loads only after cookie consent.
  The Sheet and Drive folders are on Svayra's Google account for now.
- **Real media:** clinic photos, the 1:24 walk-through and the 8 s home clip (IMG_2303). Stock is free Unsplash/Pexels
  only (notes/image-credits.md, no duplicates).
- **TBC hiding:**
  - Write `[[TBC: note || fallback]]`. Public pages show only the fallback.
  - `?review=1` shows the tags; `ARHA_REVIEW=1` builds with them visible everywhere.
  - `tools/tbc_list.py` writes the list into notes/TO-CONFIRM.md.
  - The build now fails if a raw [[TBC]] slips through without the `| tbc` filter.
- **QA at Step 4:**
  - no horizontal overflow on any of the 35 pages at 1920/1440/1024/768/390/360;
  - JSON-LD OK on all pages;
  - Lighthouse mobile (median of 3, local gzip server): home 96, root-canal post 93, Dr. Nikhil profile 97. Accessibility,
    best practices: 100. SEO 69 only because of the preview noindex (is-crawlable). LCP 1.8–2.3 s, CLS ≤0.004.

## 2. Next
1. Viraaj reviews the Step 4 screenshots.
2. Clinic sign-off on the posts. Then set `reviewed:` on each post.
3. Doctor portraits replace the placeholders. Media specs go in content/media.yaml, then run `tools/v5_media.py images`.
4. Later posts from notes/keyword-map.md ("Next posts"): 2–4 a week after launch.

## 3. Manual items for Viraaj
- **Test the 4 forms** on the preview with "TEST – ignore" data, and check each adds a row in the Sheet:
  - enquiry (any treatment page);
  - booking (/contact/);
  - referral with a small PDF (/referrals/);
  - X-ray upload (/international-patients/).

  Turnstile shows automated browsers a checkbox, so this needs a person.
- **Clinic items** (notes/TO-CONFIRM.md, Step 4 section + generated list):
  - doctor portraits, registration numbers, languages;
  - Dr. Vasant's treatments and bio;
  - Dr. Nikhil's sign-off on all 7 posts;
  - parking/lift, payment methods/EMI, same-day emergency policy;

## 4. Launch checklist (only after "ship")
- GoDaddy: delegate access for the domain. Never touch MX/email records.
- Move the Sheet, the 2 Drive folders (referrals, X-rays) and the GA4 property to the clinic's own Google account.
  Update the Apps Script properties (SHEET_ID, folder IDs, NOTIFY_TO) and redeploy the script as a new version.
- Add the production hostname to the Turnstile widget.
- Redirects: `content/redirects.txt` (from `notes/redirect-map.csv`). Check every old URL.
- Remove noindex: `preview: false` in `content/site.yaml`, rebuild, check robots.txt and the sitemap.
- Custom domain on Cloudflare Pages. Merge to `main` only when Viraaj writes "ship".

## 5. Standing rules
- Never name or link the reference site anywhere (site, code, comments, commits, README, these notes).
- No invented reviews, results, ratings, awards, years, prices or credentials, and no "best/painless/guaranteed"
  claims. Unknown facts get `[[TBC: …]]`. No before/after, no NHS, no facial aesthetics. DCI Code of Ethics applies.
- Stock people are never presented as Arha patients, doctors or staff. That means no captions or alt text implying it,
  and no stock dentist next to a doctor's name. Real clinic photos and both doctors stay real.
- Never show "n8n" publicly. No API keys in the repo: the Unsplash key stays in the git-ignored `.env`, and the
  Turnstile secret stays only in Apps Script properties.
- Push only with `git push origin v5`. No merge to `main`, no production push and no DNS change until "ship".

## Commands
- Build: `.venv/Scripts/python -I tools/build.py`. It checks titles ≤60, descriptions ≤155, one H1, alt text, dead
  links, banned words and raw TBCs.
- JSON-LD: `.venv/Scripts/python -I tools/qa/jsonld_check.py <schemaorg-current-https.jsonld>` (download the vocabulary
  from schema.org first).
- Images/video: `.venv/Scripts/python -I tools/v5_media.py images|videos [names]`
- Stock: `.venv/Scripts/python -I tools/v5_stock.py search|pick …` (Unsplash, 50 calls/hour)
- TBC list: `.venv/Scripts/python -I tools/tbc_list.py`
- Mobile QA: `.venv/Scripts/python -I tools/qa_mobile.py 390` (and 360)
- Lighthouse: serve dist with `tools/qa/gzserve.py 8090 dist`, then `sh tools/qa/lh.sh <out> http://localhost:8090/ 3`
- Git Bash: prefix commands that pass URL paths like `/blog/` with `MSYS_NO_PATHCONV=1`.
