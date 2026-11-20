# Image sources (Arha v5)

Generated 20 Nov 2026 by `tools/image_sources.py` from `content/media.yaml`, `src-assets/stock/v5/credits.json` and the people library's provenance
(`git show c45ca34:tools/people.json`). Every image on the v5 site is listed once. Rerun it after any image change.

**Style (20 Nov 2026):** stock people are free studio portraits (Pexels/Unsplash) chosen to look like the stock on
chesshousedental.com: European models on a plain light-grey or white backdrop, soft light, light clothing, full smiles,
one person per photo, one soft bright grade. Each photo is used once (some models appear in more than one frame).
Real clinic photos and the doctors' photos are unchanged. Stock people are never presented as Arha patients.

**Licence:** every stock photo is from Unsplash under the **Unsplash License** (https://unsplash.com/license): free for
commercial and non-commercial use, no permission or attribution needed. Unsplash+ (paid) results were filtered out of every
search, and each download was tracked through the official API as its guidelines require. Some photos are from Pexels under the Pexels License (https://www.pexels.com/license/), same terms. Stock people are never presented as Arha's patients, doctors or staff (alt text describes the photo only).

**Grade:** one warm, natural grade for all stock (`tools/v5_media.py stock_grade`). The clinic's own photos are
not graded. Files: AVIF + WebP + JPEG at each listed width, served with content-hashed names; below-the-fold images lazy-load.

**Checks:** no stock file is used by two slots (the generator fails if one is). Every face and head was checked in frame
at 1440, 768 and 390 px (`tools/qa/crops.py` contact sheets, by eye).

## Stock (33)

| Slot | Photographer | Source | Licence | Alt text |
|---|---|---|---|---|
| `home-card-fmr` | Christian Buehner | https://unsplash.com/photos/smiling-man-with-glasses-and-beard-portrait-DItYlc26zVI | Unsplash License | A smiling man with curly hair, a beard and round glasses |
| `home-card-kids` | azra melek | https://www.pexels.com/photo/40706578/ | Pexels License | A young girl grinning with her hands on her head |
| `hero-implants` | Moe Magners | https://www.pexels.com/photo/5335295/ | Pexels License | A smiling older woman with white hair against a light grey studio backdrop |
| `hero-fmr` | BOOM 💥 Photography | https://www.pexels.com/photo/12644998/ | Pexels License | A smiling older woman with short grey hair in a teal top |
| `hero-rct` | Dennis Kemmerling | https://www.pexels.com/photo/31863054/ | Pexels License | A relaxed, smiling woman with long dark hair |
| `hero-kids` | RDNE Stock project | https://www.pexels.com/photo/6182755/ | Pexels License | A young girl with a bob haircut and a gap-toothed smile |
| `cta-kids` | Anna Shvets | https://www.pexels.com/photo/3905793/ | Pexels License | A young boy with fair hair grinning |
| `hero-dentures` | Alex Green | https://www.pexels.com/photo/6625732/ | Pexels License | A smiling woman in her sixties with fair wavy hair, on a pale backdrop |
| `hero-missing-teeth` | Samuel Yongbo Kwon | https://unsplash.com/photos/a-man-with-a-beard-and-a-blue-shirt-uHwT183HKSw | Unsplash License | A smiling man with a short beard in a denim shirt |
| `hero-teeth-whitening` | bishenova | https://www.pexels.com/photo/35696288/ | Pexels License | A young woman with long dark hair and a bright smile |
| `hero-smile-design` | Jean-Paul Wright | https://www.pexels.com/photo/8069910/ | Pexels License | A young woman with long fair hair smiling |
| `hero-gum-care` | Marcus Aurelius | https://www.pexels.com/photo/9788575/ | Pexels License | A young woman brushing her teeth |
| `hero-aligners` | nrd | https://unsplash.com/photos/person-laughing-in-blue-shirt-y3kC_7Qhmjk | Unsplash License | A young adult with a wide, open smile |
| `cta-dentures` | PodMatch | https://unsplash.com/photos/a-smiling-man-poses-for-the-camera-sNuQ3EhnfYQ | Unsplash License | A smiling man in a dark short-sleeved shirt against a white wall |
| `cta-missing-teeth` | Anna Tarazevich | https://www.pexels.com/photo/4928703/ | Pexels License | A woman with her hair tied back, laughing, in a black T-shirt |
| `cta-teeth-whitening` | Carlos Gil | https://unsplash.com/photos/a-man-with-his-arms-crossed-smiling-S4CXgCbs9BE | Unsplash License | A smiling bearded man in a white T-shirt |
| `cta-smile-design` | Derick McKinney | https://unsplash.com/photos/man-in-gray-polo-shirt-smiling-QuwQYDBI6sI | Unsplash License | A young man with fair hair smiling broadly |
| `cta-gum-care` | Wenny Chen | https://unsplash.com/photos/a-woman-holding-a-toothbrush-in-her-right-hand-u7qidb2tNDA | Unsplash License | A young woman with fair hair holding a toothbrush, smiling |
| `cta-aligners` | Elena Golubeva | https://unsplash.com/photos/young-man-in-a-peach-polo-shirt-smiling-CEwGm-PCgOM | Unsplash License | A young man in a pink polo shirt smiling |
| `fp-kids` | Andrea Piacquadio | https://www.pexels.com/photo/5067133/ | Pexels License | A little girl in a blue T-shirt smiling |
| `hub-implants` | Lucas Calloch | https://unsplash.com/photos/a-man-with-a-beard-smiling-at-the-camera-jhIAP6Le4OY | Unsplash License | A smiling man with a short beard in a white T-shirt |
| `hub-restorative` | Kaboompics.com | https://www.pexels.com/photo/8107620/ | Pexels License | A smiling woman with curly dark hair and thin-framed glasses |
| `hub-cosmetic` | Ionela Mat | https://unsplash.com/photos/a-woman-posing-for-a-picture-in-a-white-shirt-mXFcQsECFWw | Unsplash License | A smiling young woman resting her chin on her hand |
| `hub-children` | Jessica Pope | https://www.pexels.com/photo/20759603/ | Pexels License | A young boy in a blue shirt grinning |
| `hero-childrens-orthodontics` | Bruno Curly | https://www.pexels.com/photo/12743818/ | Pexels License | A girl of about ten with long brown hair smiling |
| `cta-childrens-orthodontics` | KoolShooters | https://www.pexels.com/photo/7330622/ | Pexels License | A girl with long dark hair laughing |
| `blog-implant-timeline` | George Dagerotip | https://unsplash.com/photos/a-person-smiling-for-the-camera-pTHEQXiz0Ks | Unsplash License | A woman with a dark bob haircut and a wide smile |
| `blog-implant-vs-bridge` | Kaboompics.com | https://www.pexels.com/photo/8558897/ | Pexels License | A smiling woman in her sixties with auburn hair and round glasses |
| `blog-implant-aftercare` | DIEGO SÁNCHEZ | https://unsplash.com/photos/woman-in-white-satin-halter-top-0ZyDJJyzH14 | Unsplash License | A smiling woman with sleek dark hair on a grey studio backdrop |
| `blog-implants-right-for-me` | Tima Miroshnichenko | https://www.pexels.com/photo/8727477/ | Pexels License | Close portrait of a smiling older woman with short fair hair |
| `blog-root-canal` | Maxwell Araujo | https://www.pexels.com/photo/23285900/ | Pexels License | A smiling woman with dark hair pulled back, on a light grey backdrop |
| `blog-child-first-visit` | cottonbro studio | https://www.pexels.com/photo/4709845/ | Pexels License | A young girl laughing, showing a gap where a baby tooth was |
| `blog-implant-cost` | cottonbro studio | https://www.pexels.com/photo/7225159/ | Pexels License | A smiling older woman in a cream roll-neck jumper, in soft window light |

## Arha's own photos and video (27)

| Slot | Source file | Origin | Rights |
|---|---|---|---|
| `home-card-rct` | `assets/img/arha-dental-care-consultation-desk-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `home-commitment` | `assets/img/arha-dental-care-reception-south-mumbai-dental-clinic-02-1920.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `cta-implants` | `src-assets/dental-implant-equipment-arha-dental-care-mumbai.jpeg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `cta-fmr` | `assets/img/arha-dental-care-reception-desk-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `cta-rct` | `assets/img/arha-dental-care-operatory-laptop-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `practice-hero` | `assets/img/arha-dental-care-reception-south-mumbai-dental-clinic-01-1920.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `practice-story` | `src-assets/arha-dental-care-reception-sign-retouched.png` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `contact-photo` | `src-assets/dental-operatory-arha-dental-care-peddar-road-04.jpeg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `hero-emergency` | `src-assets/dental-operatory-arha-dental-care-peddar-road-02.jpeg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `cta-emergency` | `assets/img/arha-dental-care-planning-room-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `fp-smile` | `assets/img/arha-dental-care-planning-room-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `hub-general` | `assets/img/arha-dental-care-operatory-chair-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `hero-for-patients` | `src-assets/dental-operatory-arha-dental-care-peddar-road-01.jpeg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `home-hero` | `src-assets/arha-dental-care-reception-sign-retouched.png` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `gallery-reception` | `assets/img/arha-dental-care-reception-wide-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `gallery-lounge` | `assets/img/arha-dental-care-lounge-peddar-road-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `gallery-operatory` | `src-assets/dental-operatory-arha-dental-care-peddar-road-06.jpeg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `gallery-chair-window` | `assets/img/arha-dental-care-chair-window-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `gallery-glass-door` | `assets/img/arha-dental-care-operatory-glass-door-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `gallery-xray` | `assets/img/arha-dental-care-xray-room-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `gallery-steriliser` | `assets/img/arha-dental-care-steriliser-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `gallery-scan` | `assets/img/arha-dental-care-scan-screen-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `gallery-sterilisation` | `assets/img/autoclave-pantry-equipment-arha-dental-care-mumbai-1920.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `gallery-unit` | `assets/img/arha-dental-care-delivery-unit-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `visit-door` | `assets/img/arha-dental-care-entrance-door-1080.jpg` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `home-film` | `src-assets/IMG_2303.MOV` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |
| `practice-tour` | `src-assets/IMG_2303.MOV` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |

## Replaced on 20 Nov 2026 (owner follow-up; compared with 4d4cb13)

| Slot | Before | Now | Alt text now |
|---|---|---|---|
| `home-card-fmr` | Leo_Visions, https://unsplash.com/photos/a-woman-in-a-shawl-is-talking-to-another-woman-uPxjncijudM | Christian Buehner, https://unsplash.com/photos/smiling-man-with-glasses-and-beard-portrait-DItYlc26zVI | A smiling man with curly hair, a beard and round glasses |
| `home-card-kids` | setengah limasore, https://unsplash.com/photos/a-boy-shows-off-his-missing-tooth-DNKGiUUoVkc | azra melek, https://www.pexels.com/photo/40706578/ | A young girl grinning with her hands on her head |
| `hero-implants` | Ashwini Chaudhary(Monty), https://unsplash.com/photos/smiling-woman-in-white-button-up-shirt-FKKh90ufXfo | Moe Magners, https://www.pexels.com/photo/5335295/ | A smiling older woman with white hair against a light grey studio backdrop |
| `hero-fmr` | The Unmistakables, https://unsplash.com/photos/a-man-and-a-woman-sitting-on-a-couch-KT-msulBvtg | BOOM 💥 Photography, https://www.pexels.com/photo/12644998/ | A smiling older woman with short grey hair in a teal top |
| `hero-rct` | SoyBreno, https://unsplash.com/photos/a-woman-getting-her-teeth-checked-by-a-dentist-z8BIWPwV3zo | Dennis Kemmerling, https://www.pexels.com/photo/31863054/ | A relaxed, smiling woman with long dark hair |
| `hero-kids` | Yogendra Singh, https://unsplash.com/photos/woman-in-blue-long-sleeve-shirt-carrying-girl-in-blue-denim-jacket--ByDh99Sfww | RDNE Stock project, https://www.pexels.com/photo/6182755/ | A young girl with a bob haircut and a gap-toothed smile |
| `cta-implants` | Faraz Ghori, https://unsplash.com/photos/a-man-with-a-mustache-and-a-white-shirt-ZrdfMqs9tJ4 | `src-assets/dental-implant-equipment-arha-dental-care-mumbai.jpeg` | The panoramic X-ray unit at Arha Dental Care |
| `cta-fmr` | Massimo Zanardi Landi, https://unsplash.com/photos/a-man-smiling-for-the-camera-UB3W9g-bJLM | `assets/img/arha-dental-care-reception-desk-1080.jpg` | The reception desk at Arha Dental Care, Peddar Road |
| `cta-rct` | Mahir Velani, https://unsplash.com/photos/a-man-wearing-glasses-and-a-plaid-shirt-cZxNs7ZS1O0 | `assets/img/arha-dental-care-operatory-laptop-1080.jpg` | A treatment room at Arha Dental Care |
| `cta-kids` | LJ, https://unsplash.com/photos/smiling-girl-standing-near-wall-jhu22nvxxCw | Anna Shvets, https://www.pexels.com/photo/3905793/ | A young boy with fair hair grinning |
| `hero-dentures` | Anil Sharma, https://unsplash.com/photos/a-woman-in-a-yellow-shirt-and-a-pink-and-white-checkered-sari-tmyF9jQ6Ff0 | Alex Green, https://www.pexels.com/photo/6625732/ | A smiling woman in her sixties with fair wavy hair, on a pale backdrop |
| `hero-missing-teeth` | Wilfred Sequeira, https://unsplash.com/photos/close-up-photo-of-man-in-white-shirt-smiling-while-taking-photo-tXNjCm4bN8Y | Samuel Yongbo Kwon, https://unsplash.com/photos/a-man-with-a-beard-and-a-blue-shirt-uHwT183HKSw | A smiling man with a short beard in a denim shirt |
| `hero-teeth-whitening` | Othman El Marzak, https://unsplash.com/photos/a-close-up-of-a-person-with-a-smile-on-their-face-P4VXFXKyOQM | bishenova, https://www.pexels.com/photo/35696288/ | A young woman with long dark hair and a bright smile |
| `hero-smile-design` | Arnab De, https://unsplash.com/photos/a-smiling-woman-sitting-at-a-table-with-a-laptop-s7PbPYb5w7k | Jean-Paul Wright, https://www.pexels.com/photo/8069910/ | A young woman with long fair hair smiling |
| `hero-gum-care` | SoyBreno, https://unsplash.com/photos/a-woman-getting-her-teeth-brushed-by-a-dentist-7n50uixCBV8 | Marcus Aurelius, https://www.pexels.com/photo/9788575/ | A young woman brushing her teeth |
| `hero-aligners` | Harold Hisona, https://unsplash.com/photos/woman-adjusting-clear-dental-aligners-on-teeth-uTUsnv_UCSQ | nrd, https://unsplash.com/photos/person-laughing-in-blue-shirt-y3kC_7Qhmjk | A young adult with a wide, open smile |
| `cta-dentures` | Ajay Thakur, https://unsplash.com/photos/a-man-with-a-red-turban-is-posing-for-a-picture-eoMCmOmW0SI | PodMatch, https://unsplash.com/photos/a-smiling-man-poses-for-the-camera-sNuQ3EhnfYQ | A smiling man in a dark short-sleeved shirt against a white wall |
| `cta-missing-teeth` | Yogendra Singh, https://unsplash.com/photos/man-in-black-suit-jacket-smiling-HrpYHchKb5Y | Anna Tarazevich, https://www.pexels.com/photo/4928703/ | A woman with her hair tied back, laughing, in a black T-shirt |
| `cta-teeth-whitening` | manish_ jadhav_photography05, https://unsplash.com/photos/woman-wearing-traditional-nose-ring-VHTZ4x8TmKE | Carlos Gil, https://unsplash.com/photos/a-man-with-his-arms-crossed-smiling-S4CXgCbs9BE | A smiling bearded man in a white T-shirt |
| `cta-smile-design` | Pargat Dhillon, https://unsplash.com/photos/woman-in-black-leather-jacket-smiling-DmGzwwuLPG8 | Derick McKinney, https://unsplash.com/photos/man-in-gray-polo-shirt-smiling-QuwQYDBI6sI | A young man with fair hair smiling broadly |
| `cta-gum-care` | Athul Krishna, https://unsplash.com/photos/a-woman-wearing-glasses-is-smiling-and-holding-a-cell-phone-WWa5JkR6HaU | Wenny Chen, https://unsplash.com/photos/a-woman-holding-a-toothbrush-in-her-right-hand-u7qidb2tNDA | A young woman with fair hair holding a toothbrush, smiling |
| `cta-aligners` | Matthew Tkocz, https://unsplash.com/photos/person-holding-bubbles-q697-Akhwkc | Elena Golubeva, https://unsplash.com/photos/young-man-in-a-peach-polo-shirt-smiling-CEwGm-PCgOM | A young man in a pink polo shirt smiling |
| `cta-emergency` | Naim Ahmed, https://unsplash.com/photos/man-wearing-blue-and-yellow-floral-scarf-tD6fOGWessk | `assets/img/arha-dental-care-planning-room-1080.jpg` | The consultation room at Arha Dental Care |
| `hub-implants` | Kashish Jain, https://unsplash.com/photos/a-person-pointing-at-another-man--sxso1V_8-o | Lucas Calloch, https://unsplash.com/photos/a-man-with-a-beard-smiling-at-the-camera-jhIAP6Le4OY | A smiling man with a short beard in a white T-shirt |
| `hub-restorative` | Ranjana Rajput, https://unsplash.com/photos/a-man-and-a-woman-sitting-next-to-each-other-EMKM2qkIzRg | Kaboompics.com, https://www.pexels.com/photo/8107620/ | A smiling woman with curly dark hair and thin-framed glasses |
| `hub-cosmetic` | Pranav Kumar Jain, https://unsplash.com/photos/selective-focus-photography-of-smiling-woman-wearing-red-shirt-afve0fsW7Fw | Ionela Mat, https://unsplash.com/photos/a-woman-posing-for-a-picture-in-a-white-shirt-mXFcQsECFWw | A smiling young woman resting her chin on her hand |
| `hub-children` | Nilanka Kariyawasam, https://unsplash.com/photos/a-family-posing-for-a-picture-AKk37Avu6o8 | Jessica Pope, https://www.pexels.com/photo/20759603/ | A young boy in a blue shirt grinning |
| `hero-childrens-orthodontics` | Nehal Patel, https://unsplash.com/photos/boy-in-black-and-white-striped-shirt-aho7nVdauuc | Bruno Curly, https://www.pexels.com/photo/12743818/ | A girl of about ten with long brown hair smiling |
| `cta-childrens-orthodontics` | Ozkan Guner, https://unsplash.com/photos/close-up-of-a-persons-mouth-YKqYvUYzw0w | KoolShooters, https://www.pexels.com/photo/7330622/ | A girl with long dark hair laughing |
| `blog-implant-timeline` | Sai Nigham, https://unsplash.com/photos/a-boy-and-man-smile-together-for-a-photo-Wpjdzp6IYRk | George Dagerotip, https://unsplash.com/photos/a-person-smiling-for-the-camera-pTHEQXiz0Ks | A woman with a dark bob haircut and a wide smile |
| `blog-implant-vs-bridge` | Calvin christian, https://unsplash.com/photos/man-with-hand-on-womens-shoulder-Xcg9mkJRwpU | Kaboompics.com, https://www.pexels.com/photo/8558897/ | A smiling woman in her sixties with auburn hair and round glasses |
| `blog-implant-aftercare` | Rupinder Singh, https://unsplash.com/photos/a-woman-sitting-at-a-table-looking-at-her-cell-phone-Wkp0U_iHF5g | DIEGO SÁNCHEZ, https://unsplash.com/photos/woman-in-white-satin-halter-top-0ZyDJJyzH14 | A smiling woman with sleek dark hair on a grey studio backdrop |
| `blog-implants-right-for-me` | rajat sarki, https://unsplash.com/photos/man-in-blue-dress-shirt-and-woman-in-yellow-and-green-sari-dress-77ooeCGz8J4 | Tima Miroshnichenko, https://www.pexels.com/photo/8727477/ | Close portrait of a smiling older woman with short fair hair |
| `blog-root-canal` | Pratik Mohapatra, https://unsplash.com/photos/a-person-smiling-for-the-camera-0OIdQOWiFww | Maxwell Araujo, https://www.pexels.com/photo/23285900/ | A smiling woman with dark hair pulled back, on a light grey backdrop |
| `blog-child-first-visit` | Vivek Kumar, https://unsplash.com/photos/woman-and-child-laughing-on-sofa-a-_1PPjnbUg | cottonbro studio, https://www.pexels.com/photo/4709845/ | A young girl laughing, showing a gap where a baby tooth was |
| `blog-implant-cost` | Abrar Mohd, https://unsplash.com/photos/couple-reading-a-book-together-on-a-couch-6UUIsN2hIGA | cottonbro studio, https://www.pexels.com/photo/7225159/ | A smiling older woman in a cream roll-neck jumper, in soft window light |

New slots: `fp-kids` (Andrea Piacquadio, https://www.pexels.com/photo/5067133/); `fp-smile` (`assets/img/arha-dental-care-planning-room-1080.jpg`).

No slot kept its photo with a new crop.

## Replaced on 17 Nov 2026 (night pass: implants hero with one person, for-patients cards without repeated people; compared with 2f9f377)

| Slot | Before | Now | Alt text now |
|---|---|---|---|
| `hero-implants` | Leo_Visions, https://unsplash.com/photos/a-woman-in-a-shawl-is-talking-to-another-woman-uPxjncijudM | Nikhil Pillai, https://unsplash.com/photos/a-woman-sitting-in-a-room-with-her-eyes-closed-qydn--loUZs | An older woman in a sari sitting quietly at home, eyes lowered |

New slots: `fp-kids` (Roman Marchenko, https://unsplash.com/photos/a-close-up-of-a-person-holding-a-toothbrush-JlGiW2aDbxo); `fp-smile` (`assets/img/arha-dental-care-planning-room-1080.jpg`).

No slot kept its photo with a new crop.

## Replaced on 17 Nov 2026 (editorial pass: calm daylight, interiors and details, one warm grade; compared with 5b2356f)

| Slot | Before | Now | Alt text now |
|---|---|---|---|
| `home-card-fmr` | Ashwini Chaudhary(Monty), https://unsplash.com/photos/smiling-woman-in-white-button-up-shirt-FKKh90ufXfo | kabita Darlami, https://unsplash.com/photos/man-in-black-hat-kissing-woman-in-orange-tank-top-qy4jFZ-k-c0 | A woman applying a tilak to an older man at a family celebration |
| `home-card-kids` | Rajesh Rajput, https://unsplash.com/photos/girl-in-pink-crew-neck-t-shirt-smiling-ZbK45T1LjRg | gang coo, https://unsplash.com/photos/girl-playing-with-man-boaX2uniuK8 | A little girl laughing in a garden |
| `hero-fmr` | The Unmistakables, https://unsplash.com/photos/a-man-and-a-woman-sitting-on-a-couch-KT-msulBvtg | Dev Benjamin, https://unsplash.com/photos/a-couple-embracing-in-a-lush-green-garden-setting-OGEWjSR-4OQ | An older couple sharing a laugh in a garden |
| `hero-rct` | SoyBreno, https://unsplash.com/photos/a-woman-getting-her-teeth-checked-by-a-dentist-z8BIWPwV3zo | Ozkan Guner, https://unsplash.com/photos/a-dental-room-with-a-chair-and-a-monitor-p7eQ6uf2KSE | A dental chair under a soft treatment light |
| `hero-kids` | Yogendra Singh, https://unsplash.com/photos/woman-in-blue-long-sleeve-shirt-carrying-girl-in-blue-denim-jacket--ByDh99Sfww | Abhi Sathvik, https://unsplash.com/photos/a-mother-and-daughter-share-a-loving-embrace-rHbqGCFvzEY | A mother hugging her young daughter outdoors |
| `cta-implants` | Faraz Ghori, https://unsplash.com/photos/a-man-with-a-mustache-and-a-white-shirt-ZrdfMqs9tJ4 | `src-assets/dental-implant-equipment-arha-dental-care-mumbai.jpeg` | The panoramic X-ray unit at Arha Dental Care |
| `cta-fmr` | Massimo Zanardi Landi, https://unsplash.com/photos/a-man-smiling-for-the-camera-UB3W9g-bJLM | `assets/img/arha-dental-care-reception-desk-1080.jpg` | The reception desk at Arha Dental Care, Peddar Road |
| `cta-rct` | Mahir Velani, https://unsplash.com/photos/a-man-wearing-glasses-and-a-plaid-shirt-cZxNs7ZS1O0 | `assets/img/arha-dental-care-operatory-laptop-1080.jpg` | A treatment room at Arha Dental Care |
| `cta-kids` | LJ, https://unsplash.com/photos/smiling-girl-standing-near-wall-jhu22nvxxCw | v3dont, https://unsplash.com/photos/a-woman-holding-a-small-child-in-her-arms-XdBmpEcGy38 | A mother holding her son in the sunshine |
| `hero-dentures` | Anil Sharma, https://unsplash.com/photos/a-woman-in-a-yellow-shirt-and-a-pink-and-white-checkered-sari-tmyF9jQ6Ff0 | Manoj Kulkarni, https://unsplash.com/photos/a-woman-reading-a-newspaper-while-sitting-on-a-couch-WFGSa_dIJzE | An older woman reading the morning paper at home |
| `hero-missing-teeth` | Gyan Shahane, https://unsplash.com/photos/woman-in-purple-hijab-smiling-KxNDW0-e-54 | Nilanka Kariyawasam, https://unsplash.com/photos/a-family-posing-for-a-picture-AKk37Avu6o8 | Parents and their baby smiling together outdoors |
| `hero-teeth-whitening` | Zulfugar Karimov, https://unsplash.com/photos/a-woman-sits-by-a-window-holding-a-straw-hat-bz7tACuFbWk | Dhruv vishwakarma, https://unsplash.com/photos/young-woman-sitting-and-sketching-outdoors-rv4x3H1TnMM | A woman reading in a sunlit archway |
| `hero-smile-design` | Raju Kumar, https://unsplash.com/photos/a-young-woman-smiling-at-the-camera-outdoors-LaVkBRG1_qE | Zulfugar Karimov, https://unsplash.com/photos/a-woman-sits-by-a-window-holding-a-straw-hat-bz7tACuFbWk | A woman smiling by a window, holding a straw hat |
| `hero-aligners` | Harold Hisona, https://unsplash.com/photos/woman-adjusting-clear-dental-aligners-on-teeth-uTUsnv_UCSQ | CNordic Nordic, https://unsplash.com/photos/a-person-holding-a-remote-control-in-their-hand-YwfKjBx7AJY | Hands opening a clear aligner case |
| `cta-dentures` | Rajiv Perera, https://unsplash.com/photos/woman-in-brown-blazer-standing-beside-man-in-white-dress-shirt-ldfJJtpsrYU | charlesdeluvio, https://unsplash.com/photos/a-hospital-room-with-a-bed-and-a-window-S5meg_j_W1U | Daylight through blinds on a treatment couch |
| `cta-missing-teeth` | Yogendra Singh, https://unsplash.com/photos/man-in-black-suit-jacket-smiling-HrpYHchKb5Y | Jon Tyson, https://unsplash.com/photos/white-plastic-tray-kpLEaeScdHY | Instruments laid out on a tray by the window |
| `cta-teeth-whitening` | manish_ jadhav_photography05, https://unsplash.com/photos/woman-wearing-traditional-nose-ring-VHTZ4x8TmKE | Dollar Gill, https://unsplash.com/photos/woman-in-gray-blazer-sitting-on-chair-Ff-B_2_5W7k | A woman reading in soft window light |
| `cta-smile-design` | Pargat Dhillon, https://unsplash.com/photos/woman-in-black-leather-jacket-smiling-DmGzwwuLPG8 | bovin wook, https://unsplash.com/photos/woman-in-gray-long-sleeve-shirt-sitting-by-the-table-rchrOE87Hvs | A woman working at a desk by an open window |
| `cta-gum-care` | Athul Krishna, https://unsplash.com/photos/a-woman-wearing-glasses-is-smiling-and-holding-a-cell-phone-WWa5JkR6HaU | sunny, https://unsplash.com/photos/sunlight-streams-through-a-window-onto-tiled-wall-Q6KZShplUY4 | Morning light through a bathroom window |
| `cta-emergency` | Naim Ahmed, https://unsplash.com/photos/man-wearing-blue-and-yellow-floral-scarf-tD6fOGWessk | `assets/img/arha-dental-care-planning-room-1080.jpg` | The consultation room at Arha Dental Care |
| `hub-restorative` | Ranjana Rajput, https://unsplash.com/photos/a-man-and-a-woman-sitting-next-to-each-other-EMKM2qkIzRg | Yogendra Singh, https://unsplash.com/photos/man-in-black-jacket-hugging-woman-in-blue-and-white-plaid-dress-shirt-Uh14pWkgsyg | A father lifting his toddler at home |
| `hub-cosmetic` | Ashwini Chaudhary(Monty), https://unsplash.com/photos/woman-in-black-and-white-floral-dress-beside-woman-in-red-dress-k83qsiDlAb8 | Amrit Das, https://unsplash.com/photos/a-young-woman-looks-up-by-windows-with-greenery-RQEhdtjgP04 | A young woman pausing at a table by the window |
| `hub-children` | Nilanka Kariyawasam, https://unsplash.com/photos/a-family-posing-for-a-picture-AKk37Avu6o8 | Napendra Singh, https://unsplash.com/photos/woman-carrying-baby-aSzsf-OBneE | A mother and her daughter sharing a quiet moment |
| `hero-childrens-orthodontics` | Nehal Patel, https://unsplash.com/photos/boy-in-black-and-white-striped-shirt-aho7nVdauuc | Rajesh Rajput, https://unsplash.com/photos/girl-in-pink-crew-neck-t-shirt-smiling-ZbK45T1LjRg | A smiling girl in a pink top outdoors |
| `blog-implant-timeline` | Sai Nigham, https://unsplash.com/photos/a-boy-and-man-smile-together-for-a-photo-Wpjdzp6IYRk | Kanishk Agarwal, https://unsplash.com/photos/a-couple-of-women-standing-next-to-each-other-XdfxVAmE9ZE | Two friends laughing on a veranda |
| `blog-implant-vs-bridge` | Calvin christian, https://unsplash.com/photos/man-with-hand-on-womens-shoulder-Xcg9mkJRwpU | Abrar Mohd, https://unsplash.com/photos/couple-reading-a-book-together-on-a-couch-6UUIsN2hIGA | A couple laughing over a book on the sofa |
| `blog-implant-aftercare` | Rupinder Singh, https://unsplash.com/photos/a-woman-sitting-at-a-table-looking-at-her-cell-phone-Wkp0U_iHF5g | Odile, https://unsplash.com/photos/people-relax-in-a-cozy-living-room-setting-LcFozmjuHa4 | A quiet, sunlit living room in the afternoon |
| `blog-implants-right-for-me` | rajat sarki, https://unsplash.com/photos/man-in-blue-dress-shirt-and-woman-in-yellow-and-green-sari-dress-77ooeCGz8J4 | Sushanta Rokka, https://unsplash.com/photos/elderly-couple-talking-while-sitting-on-steps--97-s9ePuJI | An older couple talking on their doorstep |
| `blog-child-first-visit` | Vivek Kumar, https://unsplash.com/photos/woman-and-child-laughing-on-sofa-a-_1PPjnbUg | Aron Weerakoon, https://unsplash.com/photos/a-man-writes-while-a-young-girl-watches-him-intently-88jCpuCJAlw | A father drawing with his daughter on the sofa |
| `blog-implant-cost` | Abrar Mohd, https://unsplash.com/photos/couple-reading-a-book-together-on-a-couch-6UUIsN2hIGA | Oosman Exptal., https://unsplash.com/photos/a-person-holding-a-baby-2_lHgY_ZvQo | A father and his little daughter at home |

Same photo, re-framed for headroom or to keep a face in frame: `hero-implants`.

## Replaced on 16 Nov 2026 (round 2, owner follow-up; compared with 4d4cb13)

| Slot | Before | Now | Alt text now |
|---|---|---|---|
| `home-card-fmr` | Leo_Visions, https://unsplash.com/photos/a-woman-in-a-shawl-is-talking-to-another-woman-uPxjncijudM | Ashwini Chaudhary(Monty), https://unsplash.com/photos/smiling-woman-in-white-button-up-shirt-FKKh90ufXfo | An older woman with white hair smiling at home |
| `home-card-kids` | setengah limasore, https://unsplash.com/photos/a-boy-shows-off-his-missing-tooth-DNKGiUUoVkc | Rajesh Rajput, https://unsplash.com/photos/girl-in-pink-crew-neck-t-shirt-smiling-ZbK45T1LjRg | A smiling girl in a pink top outdoors |
| `hero-implants` | Ashwini Chaudhary(Monty), https://unsplash.com/photos/smiling-woman-in-white-button-up-shirt-FKKh90ufXfo | Leo_Visions, https://unsplash.com/photos/a-woman-in-a-shawl-is-talking-to-another-woman-uPxjncijudM | An older woman in a shawl smiling as she talks with a friend |
| `hero-missing-teeth` | Wilfred Sequeira, https://unsplash.com/photos/close-up-photo-of-man-in-white-shirt-smiling-while-taking-photo-tXNjCm4bN8Y | Gyan Shahane, https://unsplash.com/photos/woman-in-purple-hijab-smiling-KxNDW0-e-54 | An older woman in a lilac headscarf, smiling |
| `hero-teeth-whitening` | Othman El Marzak, https://unsplash.com/photos/a-close-up-of-a-person-with-a-smile-on-their-face-P4VXFXKyOQM | Zulfugar Karimov, https://unsplash.com/photos/a-woman-sits-by-a-window-holding-a-straw-hat-bz7tACuFbWk | A woman smiling by a window, holding a straw hat |
| `hero-smile-design` | Arnab De, https://unsplash.com/photos/a-smiling-woman-sitting-at-a-table-with-a-laptop-s7PbPYb5w7k | Raju Kumar, https://unsplash.com/photos/a-young-woman-smiling-at-the-camera-outdoors-LaVkBRG1_qE | A young woman smiling outdoors |
| `hero-gum-care` | SoyBreno, https://unsplash.com/photos/a-woman-getting-her-teeth-brushed-by-a-dentist-7n50uixCBV8 | nacer eddine, https://unsplash.com/photos/a-woman-brushing-her-teeth-in-front-of-a-mirror-dnyTnpvYkm0 | A woman brushing her teeth in front of the bathroom mirror |
| `cta-dentures` | Ajay Thakur, https://unsplash.com/photos/a-man-with-a-red-turban-is-posing-for-a-picture-eoMCmOmW0SI | Rajiv Perera, https://unsplash.com/photos/woman-in-brown-blazer-standing-beside-man-in-white-dress-shirt-ldfJJtpsrYU | An older man in a white shirt, smiling |
| `hub-implants` | Kashish Jain, https://unsplash.com/photos/a-person-pointing-at-another-man--sxso1V_8-o | WorldSikhOrg, https://unsplash.com/photos/a-group-of-people-sitting-on-a-couch-gNRPalzjEhY | A grandfather and his family talking together at home |
| `hub-cosmetic` | Pranav Kumar Jain, https://unsplash.com/photos/selective-focus-photography-of-smiling-woman-wearing-red-shirt-afve0fsW7Fw | Ashwini Chaudhary(Monty), https://unsplash.com/photos/woman-in-black-and-white-floral-dress-beside-woman-in-red-dress-k83qsiDlAb8 | Two friends smiling outdoors |
| `blog-root-canal` | Pratik Mohapatra, https://unsplash.com/photos/a-person-smiling-for-the-camera-0OIdQOWiFww | Bruno Dias, https://unsplash.com/photos/a-man-with-a-beard-sits-in-a-wooden-chair-1aGepbUTPLM | A man relaxing in a wooden chair at home |

Same photo, re-framed for headroom or to keep a face in frame: `hero-rct`, `hero-kids`, `hero-dentures`, `hub-restorative`, `blog-implant-vs-bridge`, `blog-implants-right-for-me`, `blog-implant-cost`.

## Removed on 16 Nov 2026 (owner feedback on the preview)
- Grey-haired woman on the crowns / full-mouth card (home-card-fmr): replaced by an older woman in a shawl, smiling.
- Toothbrushes with crystals (blog-child-first-visit): replaced by a mother and daughter laughing together.
- Floating 3D tooth (blog-root-canal): replaced by a young man with a calm smile.
- Also replaced: every other studio portrait of non-Indian models, the 3D implant renders and the toothbrush still life.
  The clear-aligner and braces close-ups (lips and hands only) stay, regraded.
