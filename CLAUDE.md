# Video editing rules for this repo

## START HERE (new session checklist)

1. Read this file and `.claude/skills/captions/SKILL.md` fully before editing anything.
2. Run on the `alexj-greenUGC` cloud environment (allows the Hugging Face hosts faster-whisper needs).
3. Fetch the raw clips: `git fetch origin footage`, then `git show origin/footage:"Footage/<file>" > local file`
   (the folder `Footage/Example Video/` holds his reference videos). Notion file links expire after 5 minutes: download at once with curl.
4. Make a working folder (`EDIT_WORKDIR`, in the scratchpad) with `fonts/Lato-Bold.ttf` (`npm pack @fontsource/lato`, convert the
   latin-700 woff2 with fontTools), `fonts/Montserrat-SemiBold.ttf`, `assets/` (music, metallic riser, Apple emoji PNGs from
   `npm pack emoji-datasource-apple`) and the clips. The Notion page for the format lists the other assets.
5. Pick the format section below (or the nearest one), reuse its `tools/build_*.py`, transcribe with `tools/transcribe_clips.py`.
6. Before sending: re-transcribe the output, check frames at every cut, nothing over his face, no dead space, last word finished.
7. Send the video with SendUserFile, remind him to download it, then save new rules to this file and push.

**The four rules he repeats most (never break them):**
1. Cut dead space down to a fraction of a second (a few frames between clips, no pauses).
2. Captions: the permanent style in `.claude/skills/captions` / `tools/captions.py` (matches his 1117 opening
   captions: Lato Bold 92 px, 4 px black outline, one line, 2-3 words, lowercase). Never restyle them.
3. Never put a picture over his face; place it beside, above or below the head.
4. If he is pointing, put the picture where he points.

Alexander's UGC videos are edited by Claude from raw clips, a Notion brief and a reference video.
Follow these on every edit. They come from his direct feedback.

## Placement: never cover the face

- **Never put an asset, picture, card or pop-up in front of his face.** Place each one *adjacent*
  to the face: beside the head, above it, or below the chin.
- Find the head zone per clip before placing anything. In the DJI talking clips at 1080x1920 the head
  (hair and face) is roughly x 100-710, y 260-1000. Hair top is as low as y=380 in some clips.
- Keep the top hook row and the top call-to-action text above the hair line (they live at y < 240).
- Pop-ups with a 9:16 shape (e.g. the dance clip) go to the side of the head, 320px wide. In the hook
  clip he holds the pen up at x ~690-735, y ~740-1000: place the AI influencer clip **on top of the
  pen, covering it** (top-left at x=660, y=440), which still leaves ~90px clear of his face.
- **Match each picture to where he is pointing, whenever he is pointing.** Look at the frames while
  he speaks the line: if he points to the top of the screen, the picture goes at the top (above his
  head); if he points to the side, it goes at that side. Only fall back to the default spots when
  he is not pointing. Still never over his face.
- Default card spots when he is not pointing: below the chin (y ~1290, ending above y 1420 to clear the captions). Pointing up: above the
  head (y ~55).
- **Captions (permanent, his rule): bottom quarter of the screen, baseline y 1500 (close-ups 1640).** Cards placed
  below the chin must end above y ~1420 so they never sit under a caption.

## Caption font

**Permanent, decided by him: use the captions from the opening of `1117 (2).mp4` on every video.** The full recipe is the
skill `.claude/skills/captions/SKILL.md`; the code is `tools/captions.py` (all build scripts use it). Summary: one
line, white, 4 px black outline, **Lato Bold 92 px** (measured best match to the opening; Montserrat was visibly
off), lowercase, no punctuation, 2-3 words, **baseline y 1500, the bottom quarter of the screen (y 1640 on low close-ups)**. Older caption rules
(Montserrat at 50/66/76 px, shadows, 1-2 words) are obsolete. The top "Comment "AI"..." text still uses SemiBold at 56 px.

## Assets that must appear

- Earnings picture on "thousands of dollars".
- **Permanent rule (his words: "commit this to memory"):** whenever a CTA clip says "start posting [N] a day / post
  these ... (and) get payouts like this", the **estimated-revenue card is on screen for that ENTIRE clip**, from its
  first frame to its last, **horizontally centred at the top, 640 px wide (top y ~110)**, above his hair and never
  over his face. Implemented in build_buzzy_roblox.py, build_gta_shorts.py and build_ai_influencer.py.
- Views picture on "millions of views".
- Riser sound effect leading into the screen section; background music kept low under his voice.
  Use his **metallic high riser** (`metallic_high_riser.mp4`, not the Notion `riser_sfx.mp3`). Its
  sound runs 1.2-3.0s into the file and stops dead at 3.0s: place it so that stop lands exactly on
  the cut into the screen section.

## Cutting

- **Absolutely no dead space.** The moment he finishes talking, cut to the next clip. A join between
  clips should carry no more than ~0.1s of quiet in total (a few frames), and any pause longer than
  0.15s inside a clip is cut out.
- Find edges from his voice level, not from a fixed pad: "talking" is within ~15 dB of his median
  speech level, edges may extend through softer word tails (down to ~20 dB below) by at most 0.04s,
  plus a 0.01-0.02s pad. `tools/cut_dead_space.py` is the looser first version of this.
- After cutting, re-transcribe the cut voice track and confirm every word of the script is still
  there, so no word endings were clipped.
- Run it on raw footage before captions and overlays go on.
- **One exception he asked for:** the opening hook clip ("you've probably seen videos like this")
  holds ~1s after its last word, so the AI influencer pop-up plays longer (he tried 2s, then
  settled on 1s). The pop-up comes in right on the word "this" (find the word's onset in the audio,
  not just the transcript timing), plays through the hold, and disappears on the exact frame of the
  cut to the next clip.

## Music

- Open the video on the music's high point, not its intro. For `background_music.mp3` that is
  4.45s into the track (the build peaks at ~4.5s); trim the track to start there with only a
  de-click fade, so it hits within the first fraction of a second.

## Workflow

- Raw clips arrive on the `footage` branch, in the `Footage/` folder, pushed with GitHub Desktop.
  Fetch the branch by name. The repo is public, so offer to delete the clips from it afterwards.
- Run sessions on the `alexj-greenUGC` cloud environment: it allows the Hugging Face hosts that the
  speech-to-text model (faster-whisper `small.en`) needs to download.
- The Google Drive connector cannot download files over 10MB; Notion file links have no such limit.
- Follow the reference video's structure one-to-one: hook row, talking, screen section, talking,
  call-to-action text. Confirm the clip order from the transcript, not the file names.

## How to rebuild the edit (the saved skill)

Scripts live in `tools/`: `cut_dead_space.py` (first-pass cutter), `transcribe_clips.py`
(faster-whisper word timings), `build_ai_influencer.py` (full build: tight cuts, hook row, pop-ups,
cards, captions, music, riser). Steps for a new video:

1. Fetch the `footage` branch; extract the clips. Set `EDIT_WORKDIR` to a working folder holding
   `clips/Footage/`, `assets/` (face.png, emoji.png, views.jpg, earnings.jpg, dance.mp4,
   music.mp3, riser_metallic.mp4), `fonts/Montserrat-SemiBold.ttf`.
2. `python3 tools/transcribe_clips.py $EDIT_WORKDIR/clips/Footage $EDIT_WORKDIR/transcripts.json`
3. Confirm clip order from the transcripts; edit `ORDER` (clip name + caption token counts) and the
   named picks in `stage_b` (which clip has "millions of views", "payouts like this", etc.).
4. `python3 tools/build_ai_influencer.py OUT OUT/video.mp4 --stage A` (tight cut), then `--stage B`
   (overlays + audio). Check frames at every cut and every pop-up edge before sending.
5. Re-transcribe the cut voice track to confirm no words were clipped.

Gotchas learned the hard way:
- Overlay `enable` times can be off by a frame in the final render. For a pop-up that must end on a
  cut, bake it into that clip before the clips are joined (stage A does this for the hook clip).
- Use half-open intervals and a half-frame shift for overlays that end at cuts.
- Whisper's first-word timestamps are unreliable; measure speech onset from the audio itself.
- No face detector model is available offline: mark the head zone by eye on a gridded frame.
- The Instagram logo is drawn in code (no asset supplied); swap in the real PNG if he has it.
- Edited videos only live in the chat unless saved; remind him to download them.

## Format: "Claude YouTube" — no-talking version (12s, music only)

Source: Notion page "Claude YouTube" (no-talking example, 720x1280, 12.3s). Build at 1080x1920, 30fps.
No speech, so there is nothing to transcribe: cuts follow the steps below, not his voice. The tight-cut
spirit still applies (no idle frames; each clip trimmed to the action).

Hard rules from the brief:
- The video must use ONE approved Quick Start: Explainer, Short Film, Product Ad or Ad Remake
  (the example uses **Explainer**). Never the plain text prompt box or any other Quick Start.
- The results screen must be his **real** numbers. Never invent or edit revenue.
- The "$453/day" in the title is the example's title; do not present it as a promised rate.

Timeline (reference cut points; durations in seconds):
| Time | Clip | On-screen text |
|---|---|---|
| 0.00-2.33 | Face-cam hook: shocked, pulling glasses down; no talking | Claude + Shorts graphic and title "= $453/day 🤑" |
| 2.33-3.37 | Screen recording, stylus pointing: claude.ai | "Go to Claude" |
| 3.37-4.80 | Claude with the prompt | "Copy this prompt" |
| 4.80-6.03 | Claude's output (ideas/scripts) | "Copy your favorite script" |
| 6.03-7.43 | Typing openart.ai/direct in the browser | "Go to openart.ai/direct" |
| 7.43-9.10 | OpenArt Quick Starts, pointing at Explainer | "Go to Quick Start" / "> Explainer" (2 lines) |
| 9.10-10.27 | Explainer form, pasting the script | "Paste script" |
| 10.27-11.47 | The generated video playing | "RESULTS 🔥" |
| 11.47-12.30 | His real revenue/results screen | "post everyday and get payouts like these 💰" (2 lines) |

Layout (1080x1920 coordinates, measured off the reference):
- Hook graphic `Claude-Shorts-hook.png` (2137x736 RGBA; opaque area x 90-2086, y 24-719): about 700px
  wide, spanning x ~180-880. In the reference it sits at y ~160-430 with the title "= $453/day 🤑"
  centred just under it (y ~530). **Keep both above his hair line** (never over his face).
- Step labels: centred horizontally, white semibold with a dark outline/soft shadow (CapCut "Classic"
  look, ~60px), centre at y ~610 (about 30% from the top). Two-line labels use ~75px line spacing
  (y ~727 and ~803 for the Quick Start step). "RESULTS 🔥" sits at y ~550 over the video; the final
  CTA is two lines at y ~477 and ~550.
- No pop-up pictures in this format: the screen recordings carry the content. If a label would cover
  his stylus/pointing target, nudge it so it does not hide what he is pointing at.
- Audio: music only. Use `Claude-YouTube-no-talking-song-12s.mp3` (12.2s, loud and steady, mean
  about -11.5 dB), no riser, no voice. Fade out in the last ~0.4s.

Footage needed from him: one hook face-cam clip, one screen-recording clip per step above (8 clips
of ~1-1.7s of useful action), the generated video, and his real results screen. Identify each clip by
looking at the frames (there is no speech to transcribe), and tell him if a step is missing.

**Decided by him: copy this video 1:1.** Use the reference's label wording exactly as written
(3-5 word steps, two-line labels where the reference has two lines). The "1-2 words per caption" rule
is only for talking videos; it does not apply to this no-talking format. Match timing, positions,
text style and structure to the reference as closely as possible.

### Built once already (Claude YouTube no-talking, Nov 17 footage)

- Script: `tools/build_claude_youtube.py` (set `EDIT_WORKDIR`; needs `cyt/` clips, `assets/`
  claude_shorts_hook.png, emoji.png (money-mouth), fire.png, moneybag.png, song12.mp3, and the font).
  Run `python3 tools/build_claude_youtube.py OUT.mp4`; it renders in one pass (frame-accurate overlays).
- Clip -> step mapping used (identified from the frames, no speech): 0427 hook (face-cam, hands to
  head), 0430 Claude, 0434 prompt, 0435 script output, 0440 openart.ai/direct, 0443 Quick Starts
  (pointing at Explainer), 0444 Explainer form, 0445 generated video, 0446 results screen.
- Each segment uses the reference's exact frame count (70,31,43,37,42,50,35,36,25 = 369 frames = 12.3s);
  pick the moment inside each clip where he is pointing at the thing the label names.
- `Claude-Shorts-hook.png` has faint stray pixels, so crop it to x 338-1799, y 124-602 (the tiles and
  plus), not to the alpha bounding box. Scale to ~702px wide at x 189, y ~150.
- Title "= $453/day 🤑" sits at y ~470 (just above his hair), not at the reference's y ~530.
- Emoji: Apple-style PNGs from `npm pack emoji-datasource-apple` (img/apple/64/1f525.png fire,
  1f4b0.png money bag); money-mouth is his Drive `money-mouth-face_1f911.png`.
- The reference hook has her pulling glasses down; he wears none, so the hook is his shocked reaction.
- Before sending: confirm the revenue on the results screen is his own real figure.
- **His change after seeing it:** hold the final results clip (revenue screen + CTA text) **1 second
  longer than the reference** (25 -> 55 frames, total 399 frames = 13.3s). Everything else stays 1:1.
  The song is only 12.2s, so its start is looped in with a 0.3s crossfade under the extra second, then
  fades out over the last 0.4s. (Add the song as two separate ffmpeg inputs; `asplit` into
  `acrossfade` silently truncated the audio to 2.7s.) Start the results clip at ~0.34s so the stylus
  stays off the revenue number for the whole hold.

## Format: "OpenArt + YouTube is going to be crazy" (GTA 6 / YT Shorts talking video, ~35s)

Source: his example `Footage/Example Video/OpenArt and Youtube is going to be crazy #openartpartner.mp4`
(720x1280, 34.7s, talking, no Notion page). Same family as the AI Influencer format.

Structure (reference cut points): talking hook 0-13.5s -> screen section 13.5-29.4s (tablet/laptop
with stylus, voiceover) -> talking 29.4-34.7s. Screen cuts at 16.6, 18.9, 20.0, 22.1, 24.0, 26.3.
Script (word for word): "Every day, every week, every month. You only have 14 days to learn YouTube
automation cause when GTA 6 drops, it's gonna be the biggest opportunity for everyone that already has
this skill. So let me show you how you can start in less than 30 seconds before you get left behind.
Go to YouTube and find an animated channel pulling millions of views. Cause this is how much YouTube
pays per million views. So screenshot the page, then go to openart.ai/direct, scroll down to
quickstarts and click explainer. Type a prompt like this with the screenshot for reference. It's gonna
vibe direct you YouTube shorts like this up to five minutes long. Now start posting these twice a day
to start getting payouts like this. If you want the prompt I use, comment AI and I'll DM it to you."

Overlays in the example:
- Hook row at the top for the whole talking hook: a GTA 6 key-art image, then "+ YT Shorts =", then 🤑.
- Payout counter cards stacked at the left beside his face while he says "every day, every week,
  every month": $500, then $3,500, then $15,000 (one appears per phrase, all stay). Keep them beside
  his face, never over it.
- Earnings card ("Your estimated revenue $13,682.08") appears at the top, above his head, on
  "getting payouts like this" (he points up).
- Final CTA: top text `Comment "ai" for the full prompt` (two lines) over the last line.
- Captions are 1-2 words (matches his rule).

His clips for this (pushed Nov 17, 01:30-02:23), in script order, identified from transcripts and frames:
0453 "Every day, every week, every month" | 0458 "You only have 14 days to learn YouTube automation" |
0469 "Because when GTA 6 drops..." | 0471 "So let me show you... left behind" |
0476/0477/0478 three takes of "Go to YouTube and find an animated channel..." (screen) |
0481 "Because this is how much YouTube pays per million views" (Google results) |
0483 "So screenshot the page" | 0485 "Then go to openart.ai/direct" | 0486 "Scroll down to quickstarts
and click explainer" | 0489 "Type a prompt like this with the screenshot for reference" |
0490/0493 two takes of "It's gonna vibe direct... five minutes long" (generated video) |
0495 "Now start posting these twice a day... payouts like this" | 0497 CTA "If you want the prompt I use,
comment AI and I'll DM it to you."
Duplicate takes: pick one per line (prefer the cleanest, usually the last).
Assets still needed from him: the GTA 6 image, the $500 / $3,500 / $15,000 cards, the music/riser.

### Built once already (OpenArt + YouTube / GTA 6, Nov 17 clips)

- Script: `tools/build_gta_shorts.py` (set `EDIT_WORKDIR`; needs `rb/` clips, `rb.json` word timings from
  `transcribe_clips.py`, `assets/` music.mp3 + riser_metallic.mp4, `assets_gta/` gta.png, card1-3.png,
  emoji.png, earnings.jpg, and the font). Single pass; overlays are enabled by frame number.
- He told me to copy the GTA 6 image and the payout cards straight out of the example video. Crops
  (example is 720x1280): GTA image box (50,135,316,284); cards from the frame at t=2.3s:
  card1 (73,396,320,507), card2 (73,562,320,695), card3 (73,748,320,883). They are low-res (~250px) and
  scaled to 300px wide.
- Takes used: 0478 (of 0476/0477/0478) and 0493 (of 0490/0493). Fixes: whisper wrote "openr .ai -direct"
  for openart.ai/direct and "boasting" for "posting" in the final clip; patched in `fix_words`.
- Placement from the head-zone check: in the hook clips his head is x ~80-560, hair top y ~500. The three
  payout cards go **exactly above his fingertip** at each phrase ("every day / week / month"), centred
  on the fingertip with ~25px clearance, all gone at the cut. Measured fingertips (1080x1920): day
  (904, 715), week (895, 1065), month (840, 1320). Always measure the fingertip on frames at each
  phrase; never use fixed spots when he is pointing; hook row at y ~90-240; earnings card on
  "payouts" above his head (x 330, y 55, 420px wide); `Comment "ai" for the full prompt` at the top over
  the last clip. In the close-up end clips (0495, 0497) his face and chin are low, so captions sit at
  y 1580 instead of 1222.
- Audio reused from the AI Influencer setup (he did not specify): music from 4.45s, metallic riser ending
  on the cut into the screen section.
- Check: re-transcribe the final mix and confirm the whole script is still there (it was).
- **Cutter fix (his feedback: dead space after "...YouTube automation"):** a short blip (mouth click, breath,
  tap, under 80 ms and 80+ ms away from the speech) at the start or end of a speech group is NOT speech.
  `tight_keeps` now drops such blips; before, a 30 ms click 0.12 s after the last word merged into the
  group and left ~0.15 s of silence. Check the tail of every clip: the cut should land ~0.05 s after the
  voice stops, not after the last click.
- **Payout cards, his follow-up:** all three calculator cards must be the **same size** and in **one straight
  column** (same x = 730, 300x162 each, evenly spaced; the first and last sit directly above the
  fingertip at their phrase, the middle one halfway between), still never over his face. The raw crops
  differ (card1 has no small "500x7" line, so it is shorter): pad card1's top with black and trim card3's
  last rows so all are 247x133 before scaling.
- **Even tighter on "...YouTube automation":** he asked for the cut a fraction of a second sooner, right after the
  last word. The clip (0458) now ends at 2.75s of the source (his voice is at -34 dB there and silent by
  2.78s) via `END_OVERRIDE` in `build_gta_shorts.py`; the default tight cut left ~0.05s more. When he says
  "cut it right after I finish", end the clip where the voice falls to about -35 dB, not at the pad.
- **GTA 6 picture size:** he asked for it bigger. It is now 210px tall (about 375px wide, up from 150px), with
  "+ YT Shorts =" and the emoji unchanged, the row centred at y ~190 (still above the hair line, y < 300).
  The picture is cropped from low-res example frames, so a larger size gets softer; ask for the real
  GTA 6 art if he wants it bigger still.

## Format: "Split-screen steps" (GTA 6 rent video, `Footage/Example Video/fixed.mp4`)

His next template to replicate with new wording/campaign (he will say what to change). Analysis of the
example (1080x1920, 30fps, 35.64s, h264 ~10 Mbps, black background). This is the same format as the earlier
Notion page "Money In 123" (no-talking split screen, 10 steps, comment-"direct"/"AI" CTA).

Timeline (seconds):
| Time | Layout | Text |
|---|---|---|
| 0.00-4.87 | HOOK: face-cam video fills y ~520-1560 (1080 wide) on black; title above it | "Using GTA 6 to earn next months rent / in under 40 seconds 😭" (2 lines, y ~417 and ~483, ~58px, white, centred) |
| 4.87-32.60 | SPLIT SCREEN (see below) | step labels |
| 32.60-35.64 | CTA: top text, face-cam zoomed below (y ~540-1380) | `Comment "AI" if you / want the guide I follow` (2 lines, y ~400 and ~480, ~76px, white with dark outline) |

Hook detail: he reacts, then counts down with his fingers while saying "Oh, three, two, one" (voice at
0.0, 1.2, 3.1, 3.7s). A cut at 1.33s goes from the first reaction shot to the counting shot.

Split screen (4.87-32.6), three stacked zones, the face is never covered:
- TOP (y 0-900, 1080x900): the same continuous face-cam shot of him sitting, glancing at the screen.
- MIDDLE label band (y ~900-1140, plain black): one step label, white semibold (CapCut "Classic" look),
  centred, no visible outline, sized to fit: 2-line labels ~60-80px (y ~975 and ~1050), 1-line ~68px
  (y ~1010). Label text changes at each step.
- BOTTOM (y ~1140-1920, 1080x780): screen recording of that step, filling the width.

Step labels and the times they change (copy this wording style; he will give new wording):
4.87 "Step 1: search when gta 6 comes out" | 8.63 "Step 2: check how much youtube pays" |
11.47 "step 3: search rain sounds" (lowercase "step") | 13.07 "Step 4: Notice the millions of views" |
15.50 "Step 5: go to openart.ai/direct" | 18.03 "Step 6: Scroll to quick starts" |
21.17 "Step 7: pick short film and enter your details" | 26.40 "Step 8: Watch the result" |
30.50 "Step 10: post to youtube" (the example skips step 9; ask him whether to copy that) | 32.60 CTA.
Step lengths run 1.6-5.2s (shortest step 3, longest step 7 while he fills in the form).

Audio: NO music. Mostly quiet room sound with typing/sighing (about -30 to -50 dB) under the whole
split screen; his voice only in the hook count and the CTA (-16 to -21 dB). CTA line spoken:
"And if you want the workflow that I use, comment AI and I'll send it to you." (32.5-35.4s).
Overall -20.2 LUFS, peak -0.5 dBFS. No riser. No timer is visible in this version (the old Notion page
mentioned a timer overlay with blend mode Screen; ask before adding one).

Rules that carry over: tight cuts, nothing over his face (the layout keeps text/screens in their own
zones), verify any revenue numbers are real. The 1-2-word caption rule does NOT apply here: step
labels are full phrases, as in the example.

### Built once already (Foundable "passive income business" campaign, split-screen steps)

- Script: `tools/build_split_steps.py` (set `EDIT_WORKDIR`; needs `fd/in/ns1.mp4` screen recording,
  `fd/in/ns2.mp4` face-cam for the top half, `fd/in/ns3.mp4` hook, `assets/loudly_crying.png` (😭, Apple PNG
  1f62d from `emoji-datasource-apple`), and the font). One pass, ~30s output.
- His footage: `Footage/new save.mp4` = 2-min desktop screen recording (1920x1074, silent);
  `Footage/new save 2.mp4` = 106s face-cam of him sitting (room sound with clicks/typing);
  `Footage/new save 3.mp4` = 13s hook. Use video stream `0:v:0` (the files carry an extra cover-image stream).
- Title: "Making a passive income business / in less than 40 seconds 😭" (his wording, emoji kept).
- Hook cuts, his direction: sitting down (1.00-2.25s) -> cracking open the drink **and taking a sip** (2.45-4.70;
  crack at 2.85, can reaches his lips at 4.2; he asked for the cut to the countdown half a second into the sip) -> countdown "mmm" x3 with fingers (5.60-9.03) ending right after the finger snap at the camera (8.94s).
- Steps (labels exactly): "Step 1: go to chatgpt" | "Step 2: search unsaturated / businesses in your area"
  | "Step 3: pick one you like" | "Step 4: go to foundable.com" (his spelling of the site) | "Step 5: paste
  your prompt" | "Step 6: let it cook" | "Step 7: passive income achieved". No step skipped.
- Screen-recording windows (src s, speed): 1: 13.05-16.6 x1.25 (starts when the face-cam starts, so it has
  synced sound; `adelay` padding before it made the step audio 0.3 s short) (Google -> ChatGPT) | 2: 17.2-28.0 x3 (typing
  and sending the search) | 3: 36.5-37.83 x1 (his call: no scrolling, only him highlighting the business, 37.0-37.85) | 4: 93.3-95.2 x1 (clean
  landing on the foundable.com home page; the first visit at 48.7 has the prompt pasted almost at once) |
  5: 49.6-51.8 x1 (empty box, paste at 49.9, prompt shown until 51.85) | 6: 61.8-88.0 x7 (the build) |
  7: 107.5-115.3 x2 (the finished pet-grooming website scrolling; he asked for it shorter, so it ends as the
  scroll stops at 115.05 — after that the page sits still).
- Each step crop is a 1080:780 window on the 1920x1074 recording, centred on the action; the step 6 crop
  keeps the dashboard's "Revenue $0.00" out of frame (it would contradict "passive income achieved").
  The ChatGPT crops also keep his name in the sidebar out of frame.
- Top half: one continuous take from `new save 2.mp4` starting at 26s, cropped to 1080x900; its room
  sound (+6 dB) runs under the steps, as in the example (no music).
- No ending: he adds his own CTA.
- **Audio gotcha:** ffmpeg's `alimiter` normalises its output UP to the limit by default (`level=enabled`).
  Use `alimiter=limit=0.7:level=disabled` to actually cap transients; with the default, the true peak came
  out above 0 dBFS.
- **Typing sound synced (his feedback):** the face-cam (`new save 2.mp4`) and the screen recording (`new save.mp4`)
  were filmed together; screen time = face-cam time + 13.03s (`SYNC`), found by matching each letter appearing
  in ChatGPT's box and the URL bar to his key clicks. Each step's room sound now comes from the same moment
  as its screen footage and is sped up with it (`atempo`), so clicks land on the typing; the top face-cam
  picture stays one continuous take. Check: in step 2 the clicks run 9.06-9.83s and the letters appear
  9.13-9.86s. When a face-cam and a screen recording are filmed together, always sync them this way.
- **CTA ending added:** his clip `DJI_20261117143144_0519_D.MP4` (3840x2160, "Comment AI and I'll send you the
  website"; whisper mishears it as "Call me on AI"). Speech 0.21-1.96s; use 0.18-2.18s (to the clip end) so the last word is never clipped — he heard
  "website" cut off when the cut was at 1.98. Face cropped 1080:840 at y 540-1380 on
  black, text `Comment "AI" and I'll / send you the website` above (y ~370-450), like the example's ending.
- **Memory gotchas:** feed a 4K clip into the final graph only via a pre-rendered 1080x1920 segment, and render
  far-apart audio ranges of a file in their own audio-only pass. Otherwise ffmpeg buffers decoded frames
  waiting for later concat segments and the kernel kills it (it happened twice).
- **End of a video:** always let the final word finish and keep ~0.2s of room tone after it; check the last
  10 ms of audio in the final file, not just the planned cut. Sped-up step audio must be cut from extra source
  (end + 0.5 s x speed) then trimmed, or `apad` fills the shortfall with digital silence (a 0.3 s dead gap).

## Format: "Edit This" (GTA 6 + Buzzy, Notion "Faceless YouTube Channel")

He assembles the edit himself (`Footage/edit this.mp4`, 1080x1920, no captions or overlays) and I finish it in the style
of `Footage/Example Video/AQMq...mp4` (720x1280): talking hook -> screen demo -> close-up CTA.
- Script: `tools/build_edit_this.py` (set `EDIT_WORKDIR`; needs `et/in/edit_this.mp4`, `et/in.json`, `et/na/gta2.webp`
  + `buzzy_logo.png` (Notion page assets), `et/cards/card1-3.png` + `rev_cta.png`, `assets/` music, riser, emoji).
  Two passes: each tight-cut piece is rendered on its own and concatenated (no `split` of a 1080x1920 source), then overlays + audio.
- Hook row (whole talking hook): GTA 6 art + "+" + Buzzy bee logo + "=" + 🤑, with "+" and "=" in the caption font. The
  example says "YT Shorts"; his direction is the bee logo instead.
- Revenue cards ($619.83, $3,287.17, $16,796.88, cropped from the example at t=1s, padded to the same size): in the example
  all three sit at the left. He points with a **pen** on the right, so they go in one column at x 690, 360 px wide, each
  appearing on its "every day / week / month" above the pen tip, and all gone at the cut after "month". The "month" pen tip
  is low (y ~1530), so that card stops at y 1415, above the captions.
- CTA "Post two of these a day to start getting payouts like this": the $7,165.77 card is on screen for the whole clip, centred,
  640 px, top y 110 (permanent rule). Close-up CTA captions sit at baseline 1640.
- Section cuts in his file: demo at 17.067s, CTA at 38.933s, second CTA clip at 41.933s. After "just like this one" there are 8s
  of quiet result footage; that is dead space and is cut.
- His follow-up: the clip after "now you have a video just like this one" plays 3 s longer (`RESULT_HOLD`); the caption ends with the words, no caption over the hold.
- Captions: "6" is spelled "six", and "gta six" / "two weeks" are kept in one caption (`KEEP_TOGETHER`).

## Format: Buzzy Roblox (reuse a finished edit, swap the demo)

His direction: take the hook and CTA straight out of his finished edit `Footage/Example Video/1117 (2).mp4`
(NOT `yt shorts.mp4`), replace only the demo with the new Buzzy clips, and in the hook row change
"YT Shorts" to the Buzzy logo ("Roblox logo + Buzzy logo = 🤑").

- Script: `tools/build_buzzy_roblox.py` (set `EDIT_WORKDIR`; needs `bz/ex/ex1117.mp4`, `bz/new/*.MP4`, `bz/new.json`
  word timings, `bz/audio1.mp3` (= background_music.mp3), `bz/riser_notion.mp3`, `bz/buzzy_logo.png`, and
  `fonts/Montserrat-Bold.ttf` from `@fontsource/montserrat` files/montserrat-latin-700-normal.woff2).
- 1117 example (1080x1920, 30.07s, captions and overlays burned in): hook 0-11.0 (cut at 11.0, "...$5,000
  course." ends 10.88) | OpenArt demo 11.0-26.27 | CTA 26.267-30.07 ("So make sure to save this video and
  comment the word AI and I'll send you my step-by-step guide.").
- New demo clips (Nov 17, 16:12-16:20): 0531 "Go to chat, tell it to give you a scene by scene breakdown of a
  Roblox story" | 0532 "copy everything it gives you" | 0535 "Then go to buzzy.now, come down to video
  generator and put in the prompt chat gave you" | 0540 "It's going to vibe direct to YouTube Shorts like this".
  Tight-cut, scaled 1728x3072 -> 1080x1920, captions in the permanent style (tools/captions.py), which matches the burned-in hook captions.
- Hook row in the example: Roblox tile x 33-275 y 135-380, "+" x 280-325, "YT Shorts" x 335-705 y 222-318,
  "=" x 735-780, 🤑 x 805-980. "YT Shorts" is erased **per frame** with cv2.inpaint (the Roblox pop-up overlaps
  its corner at 1.5-3.2s, so a static wall patch would paint over the pop-up), then the Buzzy logo (cropped to
  the bug, 300x190, nearest-neighbour scaling, soft shadow) sits at centre (528, 250), clear of his hair.
- Audio: the music under the example is background_music.mp3 at (example time + 4.333s), -10.2 dB; the Notion
  riser.mp3 starts at 8.90 and peaks at the 11.0 cut. Under the new demo: his voice (tight cuts), the riser's
  tail (from 2.1s into the file), and the music placed so it lines up with the CTA's music at the end (the one
  small jump in the music sits under the riser at the hook->demo cut).
- Section loudness matched the example within ~1 LU (hook -17.4, new demo -16.8, example demo -17.7).
- **Ending replaced (his feedback):** the example's "So make sure to save this video..." clip is gone. The video now
  ends with two new close-up clips: `DJI_20261117165145_0543_D.MP4` ("Start posting these twice a day and you'll start
  getting payouts like this", he points up) and `DJI_20261117165328_0545_D.MP4` ("And if you want the prompt that I
  use, just comment AI and I'll send it to you"; whisper hears "call in AI", fixed in `fix_words`). Total 29.07s.
  The "Estimated revenue $3,287.17" card (Notion "Revenue overlay", same figure as the hook; the other asset is
  "Your estimated revenue $7,165.77") sits at the top, 420px wide at x 30, y 55, above his head and left of his
  raised finger, from the word "payouts" to the end of that clip. Captions on these two close-ups sit at y 1580.
  The last clip ends 0.25 s after the last word; the music continues from the demo and fades out over the last 0.8 s.
- **Captions made permanent (his feedback):** demo and ending captions had been 66 px Bold, visibly smaller than the
  opening's. They now use `tools/captions.py` (measured widths of the opening captions: "you've probably" 651 px,
  "seen videos" 471, "millions" 293, "dollars" 260 -> best fit Montserrat SemiBold ~76 px, 6 px outline). The grouping
  was tightened to the opening's 2-3 word rhythm; `build_ai_influencer.caption_png/phrase_captions` now delegate to it,
  so the AI Influencer and GTA builds use it too. Keep the comma in patched tokens (".now,") or captions run across it.
- **Revenue card, his follow-up:** bigger and more central. Now 640 px wide (was 420), centred horizontally (x 220), top y 110,
  so it sits above his hair (hair top ~y 520 in clip 0543) and clear of his face and raised finger; it appears on the word
  "start" of "start getting payouts like this" (24.6s) and stays to the end of that clip. "Middle of the screen" means
  horizontally centred at the top: the vertical middle is his face, which pictures must never cover.

## Format: "Claude YouTube" TALKING version (voice from a separate DJI clip)

His direction: keep his original no-talking video (clips, labels, music) and put the audio of `Footage/Dji ... 0593 D.mp4`
(its picture is not used) on it, matched to the clips like the example `Footage/Example Video/Claude-YouTube-talking-16s.mp4`
(the hook is silent over the music, each voice line starts on the cut to its clip, music ducked under the voice).
- Script: `tools/build_claude_youtube_voice.py` (reuses `build_claude_youtube.py` for labels/layout; needs `cyt/` clips, `cy/in/dji.mp4`).
- The DJI voice has 9 lines: go to claude | enter this prompt | copy your favorite script | go to openart.ai/direct | go to quick start |
  select short film | paste in your prompt | post the video | post every day and get payouts like these. `tight_keeps` finds all 9
  (whisper's word timestamps are smeared in this clip; use the audio edges). Each clip lasts exactly as long as its line; "quick start" +
  "select short film" share the one Quick Start clip (gap cut from the audio, picture continuous). Last line keeps 0.25 s after the word.
- Output 14.03 s: hook 70 frames, then 25, 34, 47, 65, 59, 27, 27, 67 frames. Raw clips are short, so start times are chosen so each
  window fits (0435 starts 0.35 s, 0440 0.30 s, 0443 1.20 s, 0446 0.0 s so the stylus stays off the revenue number).
- Labels were left as in his original ("Copy this prompt", "Paste script", "RESULTS"), although the voice says "enter this prompt",
  "paste in your prompt", "post the video"; ask him if he wants the labels to follow the voice.

## Format: Buzzy Roblox Shorts, second build (Nov 18 footage, Notion "Roblox Shorts" with Inspiration `example-vid.mp4`)

- Script: `tools/build_roblox_buzzy_v2.py`. Clips: hook DJI 0594/0604/0608 (Nov 18), demo = the four Buzzy clips 0531/0532/0535/0540
  (his `1118.mp4` is the same demo with captions burned in, so the raw clips are used and captioned in the permanent style;
  `1118_captions_lower.mp4` shows the lowered caption position = baseline ~1500), ending 0610 ("...payouts like this") + 0609 ("comment buzz").
- Hook row: his `Example Video/roblox2.jfif` (black Roblox logo, rounded tile) + Buzzy bee = money bag PNG (`Glossy Golden Money Bag Emoji.png`,
  not the face emoji), row centre y 270, "+" and "=" in the caption font.
- Top caption on every frame (Montserrat SemiBold 56, y ~62, above the hook row and the revenue card): "ROBLOX SHORTS WITH BUZZY" (wording was my
  placeholder; he gave none); from the word "comment" in 0609 it becomes "COMMENT BUZZY", bottom captions keep running.
- Revenue card $7,165.77 for the whole 0610 clip (permanent rule). 34.03 s total. Not used from the Inspiration: the Roblox story pop-up and the
  9M views picture (the new script has no matching lines).

## Format: Split-screen steps, "GTA 6 pays my rent" (Nov 19 footage, example `Example Video/I bet so many people are gonna print with GTA 6 and Openart...mp4`)

- Script: `tools/build_split_gta6.py`. Same layout as the Foundable split-screen build, copied 1:1 from the example (44.5 s): hook 0-6.4 (title y 425/482, face-cam y 528-1515),
  split 6.4-42.3 (face-cam y 0-790 with a timer box x 345-735 y 630-790 "00:03.51" in thin Lato, label band y 790-1058, screen y 1058-1920), ending 42.3-44.5
  (`Comment "Free" for the Guide ✅✅`, face-cam y 520-1560). Timer = example time - 6.49 s. Label change times: 6.40, 9.67, 15.67, 19.43, 22.33, 25.73, 30.37, 34.87, 40.30.
- His footage: 0695 (hook, 1920x1080: use 5.25-11.65 = sip -> "three, two, one" -> finger at the camera), 0696 (43 s face-cam for the top half, window from 3.93 s), 0697 (4K ending, 0-2.17 s).
  He had NO screen recording, so his instruction was: use the screen recording from the example video itself (crop its bottom 575 px, y 705-1280, x1.5).
- **Typing sound sync (his request):** his face-cam audio has key-click bursts (0696: 3.9-7.2, 7.7-12.7, 16.2-18.5, 20.9-24.9, 29.1-33.7 s). The bed (room sound, his reactions, the sip)
  comes from the continuous 0696 window with those bursts ducked -32 dB, and each burst is re-placed to start and end exactly with the typing on the example's screen (windows in `TYPING`:
  google 9.7-13.3, youtube search 19.2-20.4, url 22.0-22.8, film prompt 30.5-32.6, "GTA 6" 33.9-34.6). Check: high-passed peak level per 0.5 s is high only inside those windows.
  Detecting on-screen typing: crop the search box and view frames every 1/3 s; frame differencing was too noisy.
- Loudness matched to the example per section: hook +6 dB, bed +7.6 dB, ending +9 dB (the example is -15.9 / -25.5 / -9.2 LUFS).
- Labels are the example's words ("GTA 6 comes out Today!!" etc.); the example's "Free" guide wording was kept as he says "free guide".
- **His follow-ups (GTA 6 split-screen):** (1) more cuts at the start to keep attention: the hook is now four hard cuts of 0695, all inside the example's 6.4 s:
  sitting down into the chair (0.75 s, 0.9 s long) -> popping the cup open (3.75 s, 1.0 s; the pop is at 4.2 s) -> drinking (5.5 s, 1.4 s) -> counting down (8.6 s, 3.1 s, ends with the finger at the camera) (`HOOK_CUTS`).
  (2) **consistent audio levels, no ups and downs:** the sections were -17 / -26 / -10 LUFS and the typing bursts were far louder than the gaps. Now: each section gain-matched to -18 LUFS, a steady
  room-tone floor (-47 dBFS soft noise) under the split screen so gaps never go dead quiet, then `acompressor` + `dynaudnorm` + `loudnorm I=-16`. Result: -16.1 LUFS, LRA 2.8 LU,
  2-second RMS std 1.8 dB (was 9.3). Always check 2 s RMS across the whole video, not just integrated loudness.
- **His follow-up: audio was scratchy / "too much feedback" (v6).** Causes: the synthetic noise floor and `dynaudnorm`/6:1 compression boosted hiss and clicks by 15-20 dB, and the typing clicks were +7.6 dB hot.
  Now: no synthetic noise; in the click bursts only the highs (>1 kHz, band split in numpy) are ducked -32 dB while the lows (his real room tone) keep -6 dB; inserted clicks at +1.6 dB; final chain
  `highpass 80, afftdn nr=10, acompressor 2.5:1, loudnorm I=-16 LRA 11, alimiter`; the ending line 3 dB lower. Scratchiness proxy (energy share above 4 kHz) fell 0.46 -> 0.25 while 2 s RMS std stayed 2.2 dB.
  Never use heavy compression/`dynaudnorm` on quiet room-tone material: it raises the hiss to the level of the voice.
- **His follow-up (v9-v13): audio still inconsistent/scratchy; "use only the audio from my footage, none from the example".** Audio is now ONLY his own: hook from 0695, the split section from his continuous 0696 take
  (reactions and sip stay in lip sync), ending from 0697. His own click bursts are replaced by looped room tone from the same take (0696 25.00-25.95 s, 80 ms crossfades, no ducking), and his typing sound is placed on the
  example's on-screen typing windows. (The example's audio is never used; only its picture, for the screen recording.) Split section chain: highpass 90, `afftdn nr=30`, `acompressor 8:1 makeup 12`, lowpass 7 kHz
  (2 s level std 7.0 -> 2.0 dB); then every section is set to the same integrated loudness (-17 LUFS target) and a light 2:1 compressor + limiter closes the mix. Result: -19.8 LUFS, LRA 3.8, 2 s level std 1.4 dB.
  His face-cam mic is quiet and hissy, so a quiet room-sound section can only be made even with strong compression; never boost it plainly to voice level.
- **His final instruction on this video (v14): "Just don't do anything with the audio. Keep the audio how it was originally."** So the audio is the raw audio of his footage, cut only where the picture is cut:
  hook = the four 0695 cuts (their own audio), split section = the raw 0696 window from `TOP_START` (his real typing, reactions and sip), ending = raw 0697. NO gain, loudness matching, compression, denoise, ducking,
  typing re-placement or limiter. (Everything described in the audio follow-ups above, v1-v13, is superseded: it made the audio worse.) Default for every future edit: leave the audio of his footage as recorded unless he asks otherwise.
  Result is naturally uneven (-26 LUFS, LRA 21 LU: loud voice in the hook and ending, quiet room sound in between), as in his example.
- **Final audio rule for this video (v15):** "don't change the audio at all, just match WHEN he types to when typing shows on screen." So: cut-and-slide only, raw sound, no gain / filter / compression / limiter / added noise.
  The continuous 0696 take keeps his reactions and sip in lip sync; his click bursts are cut out and covered with raw room tone from the same take (0696 25.00-25.95 s looped, 80 ms crossfades); each raw burst is placed on the
  example's typing windows (`TYPING`). Check with `clicks.py`-style detection: 101 of 112 clicks in the split fall inside the typing windows (the rest are single natural ticks). Hook and ending audio untouched.
  Supersedes the v14 "completely untouched" version, which left his typing out of sync with the screen.

## Format: Buzzy "monetize YT Shorts" (Roblox story) in 4 shirts (Nov 22 footage)

Reference `Footage/Example Video/Its never been easier to monetize YT shorts, buzzy.now is printing rn.mp4` (720x1280, 29.07 s). Script: `tools/build_buzzy_shirts.py GROUP OUT` (GROUP = white | red | blackgold | blackpolo);
one script, same structure for every shirt, only the takes differ. Render the four one after another (memory).
Reference timeline (seconds): 0-1.36 line 1 "you've probably seen videos like this" | 1.36-3.3 he HOLDS ~1.9 s while the Roblox story pop-up plays with its own sound ("In this town, there is only one rule.", first 1.9 s of the Notion
asset `Roblox-YouTube-story.mp4`) | 3.3-6.27 line 2 "actually getting millions of views and generating thousands of dollars" (9M views picture from "millions" to "thousands"; $3,287.17 revenue card on "thousands of dollars") |
6.27-11.0 line 3 "let me show you how you can make the same exact video before someone else puts it behind a $5,000 course" | 11.0-23.2 DEMO (`Footage/demo.mp4`, his voice-over + burned-in captions; riser stops on the cut) |
23.2-26.0 "start posting these twice a day ... payouts like this" (revenue card the WHOLE clip, rule) | 26.0-29.07 "if you want the prompt that I use, just comment buzz and I'll DM it". Hook row (blue Roblox tile `images.jpg` + Buzzy bee = money-mouth face `money-mouth-face_1f911.png`)
on top from 0 to the demo cut; no top text. Music from its peak under everything.
- Shirts (checked on a frame of every clip): white tee `0773 0774 0777 0778 0780` | red tee `0783 0784 0785 0786 0787` | black henley with gold lower pattern `0789 0790 0794 0796 0797` | black chain-collar polo `0799 0802 0805 0806 0807`.
  Each group is exactly one take per line (no duplicates). Their wording differs slightly (white: "consistently to start getting payouts", "the same exact prompt I used ... Buzzy"; red "Now to start posting"; polo "So I'm gonna show you"); never borrow a clip from another shirt.
- `demo.mp4` is shared by all four: 0-12.2 s is the demo (voice ends 12.18 s, picture goes black at 12.25 s); the rest of the file is black plus a $7,165.77 card still. Use `DEMO_END = 12.2`.
- Pictures supplied but not in the reference: `roblox 5.png` (red Roblox logo), `youtube_shorts_cutout.png`. The bee logo, the $3,287.17 card and the Roblox story clip are not in this folder: taken from his Notion "Roblox Shorts" page / earlier builds.
- Placement (his rule: beside the head, where he points): in every hook take he sits right of centre (head x ~430-950) and gestures low with the pen/item, so the pop-up (320 wide, x 30, y 396), the views card and the small revenue card (380 wide, x 30, y 640)
  all go on his left, above his hand, under the hook row. Close-ups: revenue card centred, 640 wide, y 110 (hair top >= y 445 in all four CTA takes).
- Audio: his voice exactly as recorded (no gain/filters); music at (voice rms - 14 dB), riser at (voice rms - 8 dB); the story pop-up's own sound plays during the hold. Result -14 to -15 LUFS, peak -0.5 dBFS.
- ffmpeg gotchas: overlaying the pop-up video with `enable='between(n,...)'` silently drops it; use a TIME window (`between(t, hold_start/30 - 0.002, hold_end/30 + 0.02)`, the +0.02 makes the last hold frame show) and make the pop-up clip a few frames longer than the hold.
- Lengths: white 31.23 s, red 30.10 s, black gold 30.63 s, black polo 29.93 s.
- **His follow-up on the four shirt videos (Nov 22):** (1) the yellow Buzzy bee in the hook row is now the **YouTube Shorts logo** (`youtube_shorts_cutout.png`, 250 px tall); (2) the 9M views picture and the hook revenue card sit
  **just under the captions** (centred, 420 px wide, top y 1540; caption baseline 1500) - this supersedes the earlier "beside his head on the left" placement for those two cards (the Roblox pop-up stays on the left, and the
  CTA revenue card stays centred at the top); (3) the Roblox pop-up now plays his two new clips `Footage/roblox short 1 .mp4` (3.4 s, "In this town, you can't make a sound...") and `Footage/short 2 .mp4` (4.7 s, "In this town,
  everyone is blind. Except me...") instead of the Notion story clip, alternating by shirt (white + black gold = short 1, first 1.72 s; red + black polo = short 2, first 1.85 s; both cut at the end of the first sentence);
  (4) **no dead space while he talks:** each cut lands where his voice stops (measured: 0.02-0.03 s of quiet at every join, no pause over 0.1 s inside any clip, last word + 0.25 s). The only silent stretch of his own track is the hold on
  his face while the pop-up speaks, and it ends the moment the pop-up sentence ends (`POPS`). Check: `silencedetect -42 dB 0.12 s` on the voice-only base track shows only the hold and the final tail.
- **ffmpeg gotcha (pop-up edges):** `overlay` with `enable='between(n,..)'` drops the pop-up, and a time-based `enable` was one frame off depending on timestamp drift of the concatenated base. Fix: pre-build a transparent `ffv1` yuva420p layer of
  exactly F frames with the pop-up on frames [hold_start, hold_end) (`setpts=N/(30*TB)` on every stream), then overlay it with no `enable`. Verify with a frame diff against the base on frames hold_start-1, hold_start, hold_end-1, hold_end.
- **His follow-up (Nov 23): pop-up timing and place.** The Roblox pop-up now starts 3 frames (0.1 s, `POP_DELAY_F`) after he says "this" (the hold starts at his last word) and sits **right above the pen/item he points with** (bottom 25 px above its tip,
  centred on it): tips measured on gridded frames of the hold `POP_TIP` = white (294,985), red (280,1090), black gold (252,1115), black polo (200,1165). Supersedes the fixed left position (x 30, y 396). Edges verified by frame diff (off,on,on,off).
- **His follow-up (Nov 23, later): pop-up comes up AS he says "this"** (onset of the last word of line 1, frame from the word start), not after it. It still plays one full sentence (`POPS`), so the silent hold on his face shrinks
  to what is left after his voice ends (hold = pop start + sentence frames - voice end). Position unchanged (above the pen). Videos got 0.6-0.7 s shorter (white 30.43, red 29.43, black gold 29.87, black polo 29.27 s).
- **His follow-up (Nov 23): top text on the very last clip.** The last clip ("comment buzz", role P2) carries the text `comment "buzz"` (curly quotes) at the top, in the caption font (`capstyle.render`, Lato Bold 92, 4 px outline, overlay y 110 = baseline 240, above the hair line y >= 445),
  from the clip's first frame to its last frame, nothing before it (the revenue card on the clip before sits at y 110 too, so they never overlap).

## Format: "sound up" swap (Nov 23, `Footage/sound up .mp4`, his finished edit, 1080x1920, 27.97 s, captions/pop-ups burned in)

Script `tools/build_soundup_swap.py`. His ask: (1) the yellow Buzzy bee in the middle of the hook row -> the YouTube Shorts logo (`youtube_shorts_cutout.png`, 230 px tall, centre (545,222)); the bee is erased per frame with cv2.inpaint
(mask = pixels differing from the wall colour = median of the box border, dilated 9 px, box x405 y120 280x210; a colour-threshold mask left grey wing remnants), then the logo is laid on top; (2) the demo section (frames 313-679, 10.433-22.633 s, 12.2 s)
-> `Footage/demo.mp4` 0-12.2 s (the ChatGPT part used in the four shirt videos; same length). Hook/ending audio untouched; demo section uses demo.mp4's own voice-over with `assets/music.mp3` under it (his original music track is mixed into the
burned-in audio and cannot be separated). Hook/ending video keeps its burned-in captions, 9M card, revenue card, "COMMENT "BLOX"" text.

## Briefs for his human editor (Google Drive folder "Video Editor Briefs", Nov 26)

He also hands videos to a human editor. His Drive folder "Video Editor Briefs" holds: `00 Editing rules (read before every video)`
(the standing rules from this file, written in plain editor language), `01 Brief template (make a copy for each video)`, and one
`Brief: <video name>` doc per video. When he dictates instructions for the editor, rewrite them as short, plain, unambiguous
instructions (exact on-screen wording in quotes, what to keep, where to cut) and put them in that video's brief; leave anything he
did not say as `[to add]` rather than guessing. Only the Google Drive connector is available, which can create docs but not edit them:
changes to an existing brief need the Google Docs connector, or a new copy.
- First brief: "Using Roblox to buy Christmas presents". No music. Hook title exactly "using Roblox to buy Christmas presents in under
  30 seconds". Keep the whole countdown including the finger snap, and cut to the next clip immediately after the snap.
