# Video editing rules for this repo

**The four rules he repeats most (never break them):**
1. Cut dead space down to a fraction of a second (a few frames between clips, no pauses).
2. Captions: CapCut "Classic" look (Montserrat SemiBold), **one line, 1-2 words** at a time.
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
- Default card spots when he is not pointing: below the chin (y ~1290). Pointing up: above the
  head (y ~55).
- Captions sit at y ~1222, below the chin.

## Caption font

- Use CapCut's **"Classic"** font. That is Proxima Nova Semibold (paid), so render with its free
  look-alike **Montserrat SemiBold** (OFL): `npm pack @fontsource/montserrat`, take
  `files/montserrat-latin-600-normal.woff2` and convert it to TTF with fontTools.
- Caption look (matched to a reference he supplied): Montserrat SemiBold 50px, white, thin ~3px
  near-black outline plus a soft drop shadow (blurred, offset ~3px down).
- **One line, 1-2 words per caption** (his latest call; he tried 2-line phrase captions first).
  Pair words by phrase: "of"/"to"/"the"/"my"... lead into the next word, so a caption should not
  end on one; never pair across a comma or sentence end; keep pairs short (<= 18 characters).
- All lowercase, no punctuation (keep "$5,000", "buzzy.now", "i'll").
- Each caption appears when its first word starts and holds until the next caption.
- The caption line is centred at y ~1222: below the chin and clear of the cards at y ~1290.
- The top "Comment "AI" for the full guide" text uses the same font at 56px.
- The "+" and "=" in the hook row are typed in the caption font and caption style (72px, white,
  thin outline, soft shadow), not drawn shapes.

## Assets that must appear

- Earnings picture on "thousands of dollars" **and** on "get payouts like this" (he points up at the
  top of the screen there, so put it at the top, above his head).
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
  Tight-cut, scaled 1728x3072 -> 1080x1920, captions 1-2 words in the example's own caption look (bold white,
  thick 7px black outline, Montserrat Bold 66px, centre y 1295) so they match the burned-in hook/CTA captions.
- Hook row in the example: Roblox tile x 33-275 y 135-380, "+" x 280-325, "YT Shorts" x 335-705 y 222-318,
  "=" x 735-780, 🤑 x 805-980. "YT Shorts" is erased **per frame** with cv2.inpaint (the Roblox pop-up overlaps
  its corner at 1.5-3.2s, so a static wall patch would paint over the pop-up), then the Buzzy logo (cropped to
  the bug, 300x190, nearest-neighbour scaling, soft shadow) sits at centre (528, 250), clear of his hair.
- Audio: the music under the example is background_music.mp3 at (example time + 4.333s), -10.2 dB; the Notion
  riser.mp3 starts at 8.90 and peaks at the 11.0 cut. Under the new demo: his voice (tight cuts), the riser's
  tail (from 2.1s into the file), and the music placed so it lines up with the CTA's music at the end (the one
  small jump in the music sits under the riser at the hook->demo cut).
- Section loudness matched the example within ~1 LU (hook -17.4, new demo -16.8, example demo -17.7).
