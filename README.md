# Suyash Goswami — content library

Backup of every raw clip, photo, edit, ad, voiceover, script and plan made for **suyash.live** (Beyond Branding Media).
This branch (`content-archive`) is separate from the website on `main`, and Vercel deploys are switched off for it (`vercel.json`).

## Rebuild the split 4K files
GitHub caps files at 100 MB, so the two 4K originals are split into 90 MB parts:
```
cat raw/stage-originals/IMG_1782_stage_bw_4k.mov.part* > IMG_1782_stage_bw_4k.mov
cat raw/stage-originals/IMG_1783_stage_purple_closeup_4k.mov.part* > IMG_1783_stage_purple_closeup_4k.mov
```
They're HDR (HLG). The scripts tone-map them with the ffmpeg `zscale … tonemap=mobius` chain in `scripts/ad3.py`.

## Folders
| Folder | What's inside |
|---|---|
| `raw/stage-originals` | Camera originals from the stage gigs (4K/1080p HDR) |
| `raw/instagram` | His Instagram posts, downloaded (filename = post ID) |
| `raw/pexels` | Stock crowd clips (Pexels licence, mood shots only) |
| `photos/stage-bw` | Black-and-white stage photos |
| `photos/face-refs` | Real face stills taken from his videos (for any image work) |
| `edits/reels` | Finished reels (compressed archive copies) |
| `edits/ads` | Enquiry ads: 15 s master, 8 s story, FM 91.65, earlier versions |
| `edits/pinned-grid` | 3-tile pinned grid (website theme + editorial version) |
| `edits/feed-and-kit` | Launch carousel, highlight covers, feed preview, Instagram guide |
| `voiceover` | ElevenLabs voiceover takes |
| `scripts` | Python/ffmpeg scripts that build every edit (re-runnable) |
| `plans` | Ad plans, storyboard, next-reels plan, reference PDF |

## Raw clip inventory
| File | Length · size | Notes |
|---|---|---|
| `raw/stage-originals/A098A7A0_stage_purple.mov` | 16s · 720×1280 | Purple stage (same set). Sign visible. |
| `raw/stage-originals/BA2D7CCA_stage_purple.mov` | 16s · 720×1280 | Purple stage (same set). Sign visible. |
| `raw/stage-originals/IMG_1782_stage_bw_4k.mov` |  | ⭐ B&W stage, 4K HDR, best audio. Ohlio sign top-right: crop below y≈1100 (portrait 2160×3840). |
| `raw/stage-originals/IMG_1783_stage_purple_closeup_4k.mov` |  | Purple close-up 4K. Sign enters frame after ~2.8 s; hands crop is always clean. |
| `raw/stage-originals/IMG_8298_stage_purple_wide_1080p.mov` | 33s · 1920×1080 | Purple wide stage. Sign right above his head; hard to crop. |
| `raw/instagram/DM-eZ_8THGS.mp4` | 177s · 1080×1920 | Window light, sunglasses, burned-in text. |
| `raw/instagram/DMswv-3zKLC.mp4` | 103s · 720×1280 | Emotional unplugged, letterboxed. |
| `raw/instagram/DNQefHCCo_1.mp4` | 134s · 638×360 | 360p landscape home guitar. |
| `raw/instagram/DNq2YHMz-lK.mp4` | 164s · 720×1280 | No guitar, 'Part 2' text. |
| `raw/instagram/DOYhkwTk62l.mp4` | 149s · 360×640 | 360p, film posters in frame. |
| `raw/instagram/DPHsUn9k9De.mp4` | 82s · 1080×1920 | 'Aye Zindagi' slow version, text overlays. |
| `raw/instagram/DRZe_XDgg3E.mp4` | 132s · 720×1280 | ⭐ Harmonium + tabla mehfil, clean (no text). |
| `raw/instagram/DSamz6ojTkM.mp4` | 48s · 720×1280 | ⭐ Wedding-style venue, band setup, singing with mic. Confirm it's Suyash. |
| `raw/instagram/DT5zze-Av_S.mp4` | 54s · 720×1280 | Nusrat tribute — other performers (not Suyash on vocals?). |
| `raw/instagram/DTIvUFwgorQ.mp4` | 61s · 720×1280 | 'A song from another time', text burned in. |
| `raw/instagram/DTa_Z_5jfCP.mp4` | 60s · 720×1280 | Sunday session — verify it's Suyash. |
| `raw/instagram/DTnD7FLAoPM.mp4` | 121s · 720×1280 | Room jam, English lyrics burned in, dark. |
| `raw/instagram/DVRrQpKgpEV.mp4` | 130s · 720×1280 | Duo with female singer at Ohlio (sign). |
| `raw/instagram/DVaNOTUgnrk.mp4` | 107s · 1280×720 | Ohlio wide stage duo. |
| `raw/instagram/DYfRK-vz6Vm.mp4` | 100s · 720×1280 | 2014 throwback 'Kyun main jaagoon', POV text. |
| `raw/instagram/DaD9RMJCd09.mp4` | 166s · 720×1280 | Ghazal 'Gulon mein rang bhare' with Hindi lyrics burned in (crop top). |
| `raw/instagram/DaEA4mGC79R.mp4` | 73s · 720×1280 | Same ghazal session (shorter). |
| `raw/instagram/DcMlmu1iSMn.mp4` | 46s · 720×1280 | Ohlio duo, caption burned in. |
| `raw/instagram/De7SLggiXCi.mp4` | 94s · 720×1280 | Unplugged guitar close-up at home, clean. |
| `raw/instagram/DfxTRK1OpAv.mp4` | 10s · 720×1280 | 'AI vs live' reel. |
| `raw/pexels/pexels_13003413_crowd_phones.mp4` | 13s · 1920×1080 | Stock (Pexels licence): crowd with phones, faces. Mood only. |
| `raw/pexels/pexels_13003417_crowd_torches.mp4` | 12s · 1920×1080 | Stock (Pexels licence): crowd, phone torches. Use as mood only, never as 'his' audience. |

## Rules we've settled on
- **Ohlio branding:** keep it out of ads (crop or paint out).
- **His audio:** keep the original. Only gain/level-matching is allowed. Never put home-session audio over stage footage.
- **Faces:** no AI-generated faces of Suyash, only real footage and photos.
- **Stock crowds:** mood or "your guests" framing only, never shown as his audience.
- **Ad text:** keep it between y 270 and 1245 px on a 1080×1920 frame (Reels safe zone).
- **Palette:** `#120d0a` `#efe6db` `#b9a898` `#e8692a`. Fonts: Urbanist, DM Mono, Instrument Serif.
