# Arha v5: next steps (read this first)

Written 13 Nov 2026 so a fresh session can continue with no chat history. Branch `v5`. Preview: https://arha-v5.pages.dev
(Cloudflare Pages builds `python tools/build.py` -> `dist/` on every push to `v5`; noindexed). Last code commit: `5e14274`.

## 1. Current state (done)
- **Pages (30):** home, the practice (with "Inside the practice" gallery), 12 treatments + hub, for-patients, contact,
  referrals, emergency, International & NRI hub (noindex, not linked yet), blog index + 4 implant posts, 5 policies, 404.
- **Forms backend live** (commit 7df4825): Google Apps Script web app (`tools/forms/arha-forms.gs`, uses `ss_()` =
  SHEET_ID property or the bound sheet), Cloudflare Turnstile (live site key in `content/site.yaml`; secret only in the
  Apps Script properties), GA4 `G-J6TW5GWFYL` (loads only after cookie consent). Sheet "Arha website enquiries" and the
  Drive folders are on Svayra's Google account for now. Script properties: NOTIFY_TO, TURNSTILE_SECRET, SHEET_ID,
  REFERRALS_FOLDER_ID, XRAY_FOLDER_ID.
- **Real media:** clinic photos (practice hero/story, gallery, visit block door, contact, heroes) and the 1:24 walk-through
  (`src-assets/IMG_2303.MOV`: gallery film + 8 s clip on the home implants card). No stock video anywhere.
- **Stock:** free Unsplash + 2 Pexels photos, one cool-neutral grade, no duplicates (`notes/image-credits.md`; source of
  truth `src-assets/stock/v5/credits.json`, git-ignored). Adobe Stock is not being bought.
- **Confirmed facts in SITE:** phone/WhatsApp +91 99755 07714, Mon–Sat 9:30 AM–6:30 PM (Sun closed), 107 Doctor House,
  14 Peddar Road (Dr Gopalrao Deshmukh Marg), Opp. Jaslok Hospital, Mumbai 400026; Invisalign offered (no provider tier);
  braces + clear aligners for children, teens, adults; both doctors' credentials.
- **TBC hiding:** write `[[TBC: note || fallback]]`. Public pages show only the fallback (elements with no fallback are
  hidden). `?review=1` on any URL shows the yellow tags for the browser session (`?review=0` off); `ARHA_REVIEW=1` build
  shows them everywhere. `tools/tbc_list.py` (after a build) rewrites the full list in `notes/TO-CONFIRM.md`.
- QA at last commit: no horizontal overflow 1920–360, `tools/qa_mobile.py 390|360` OK, Lighthouse home mobile ~99.

## 2. Next: Step 4 (in this order; commit as you go, push `v5`)
1. **Blog engine:** blog index + post template in the reference blog layout: Article schema, author Dr. Nikhil V. Jain,
   "Medically reviewed by" line, date, reading time, related treatments, booking CTA. Seed 4 posts from
   `notes/keyword-map.md` (the 4 with the clearest local demand; 4 implant posts already exist in `content/blog/`, so
   decide whether they count or add new ones). 900–1,400 words, question headings, short FAQ, no invented stats or
   claims, DCI-safe. Free light-studio images only, no duplicates (`tools/v5_stock.py`, then `tools/v5_media.py images`).
2. **Doctor pages:** `/doctors/dr-nikhil-v-jain/` and `/doctors/dr-vasant-p-jain/`: team-card + bio-modal style plus a
   full page each, Person schema. Credentials: "B.D.S., M.D.S., Prosthodontist & Implantologist, ITI Scholar (London)"
   and "B.D.S., Dental Surgeon". Photo slot = clean logo placeholder (no stock face); flag in TO-CONFIRM.
3. **Reviews on the home page:** real Google reviews only, character for character, link to the Google profile, re-check
   rating and count. Build it but keep it OFF (`show_reviews: false` in `content/site.yaml`) until the clinic agrees in
   writing (TO-CONFIRM cites the NMC ethical-advertising guidelines and a National Dental Commission advisory). If the
   reviews can't be read reliably, say so.
4. **Parity:** finish `notes/parity-checklist.md`: every reference page/element gets ✅ / 🔁 (reason) / ⏳ clinic.
   Build anything still missing.
5. **JSON-LD:** validate on every page type (home, treatment, blog post, doctor, contact) and fix errors.
6. **Test** at 1440 and 390, **Lighthouse mobile** on home + one blog post + one doctor page, push `v5`, send the
   summary with screenshots of the blog index, one post and one doctor page.

## 3. Manual items for Viraaj
- Test the 4 forms on the preview with "TEST – ignore" data: enquiry (any treatment page), booking (/contact/),
  referral with a small PDF (/referrals/), X-ray upload (/international-patients/). Turnstile shows automated browsers a
  checkbox, so this needs a person (or Cloudflare's testing key pair temporarily). Check each adds a row in the Sheet.
- Clinic items (`notes/TO-CONFIRM.md`, generated list at the end): doctor photos, registration numbers, parking/lift,
  payment methods/EMI, same-day emergency policy, reviews consent, clinic story, year opened, fees.

## 4. Launch checklist (only after "ship")
- GoDaddy: delegate access for the domain. Never touch MX/email records.
- Move the Sheet, the 2 Drive folders (referrals, X-rays) and the GA4 property to the clinic's own Google account;
  update the Apps Script properties (SHEET_ID, folder IDs, NOTIFY_TO) and redeploy the script (new version).
- Add the production hostname to the Turnstile widget.
- Redirects: `content/redirects.txt` (from `notes/redirect-map.csv`), check every old URL.
- Remove noindex: `preview: false` in `content/site.yaml`, rebuild, check robots.txt and the sitemap.
- Custom domain on Cloudflare Pages; merge to `main` only when Viraaj writes "ship".

## 5. Standing rules
- Never name or link the reference site anywhere (site, code, comments, commits, README, these notes).
- No invented reviews, results, ratings, awards, years, prices, credentials, or "best/painless/guaranteed" claims;
  unknown facts get `[[TBC: …]]`. No before/after, no NHS, no facial aesthetics. DCI Code of Ethics applies.
- Stock people are never presented as Arha patients, doctors or staff (no captions/alt text implying it); the footer
  says so. Real clinic photos and both doctors stay real.
- Never show "n8n" publicly; no API keys in the repo (Unsplash key in git-ignored `.env`); Turnstile secret only in
  Apps Script properties.
- Push only `git push origin v5`. No merge to `main`, no production push, no DNS change until "ship".

## Commands
- Build: `.venv/Scripts/python -I tools/build.py` (checks titles ≤60, descriptions ≤155, one H1, alt text, dead links)
- Images/video: `.venv/Scripts/python -I tools/v5_media.py images|videos [names]` (specs in `content/media.yaml`)
- Stock search/pick: `.venv/Scripts/python -I tools/v5_stock.py search|pick …` (Unsplash, 50 calls/hour)
- TBC list: `.venv/Scripts/python -I tools/tbc_list.py`
- Mobile QA: `.venv/Scripts/python -I tools/qa_mobile.py 390` (and 360)
- Side-by-side with the reference captures: `.venv/Scripts/python -I tools/compare.py`
