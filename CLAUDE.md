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
