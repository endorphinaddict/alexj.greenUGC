---
name: captions
description: The permanent caption style for all of Alexander's videos. Use on every edit that has talking-head or voiceover captions (and when the caption look, size, position, grouping or font comes up). Matches the opening captions of his finished edit "1117 (2).mp4". Never restyle captions by hand.
---

# Permanent caption style

He decided: these captions are used **permanently, on everything**. They are measured off the opening captions
of `Footage/Example Video/1117 (2).mp4` (the hook, 0-11 s). All code lives in `tools/captions.py`; every build
script (`build_ai_influencer.py`, `build_gta_shorts.py`, `build_buzzy_roblox.py`) already calls it.

## The look
- **One line**, white text, **black outline 4 px**, no drop shadow, no background box.
- Font: **Lato Bold, 92 px**. Chosen by measurement: 15 free fonts were scored against the white letter shapes of four
  real opening captions ("seen videos", "make the same", "someone else", "exact videos"); Lato Bold won (IoU 0.745),
  Figtree SemiBold was close (0.728), Montserrat was the worst (0.58, visibly wider and rounder; he noticed). Get it:
  `npm pack @fontsource/lato`, take `files/lato-latin-700-normal.woff2`, convert to TTF with fontTools, save as
  `$EDIT_WORKDIR/fonts/Lato-Bold.ttf` (or set `CAPTION_FONT`).
- **All lowercase, no punctuation**, numbers spelled out ("a five thousand dollar course"). Keep `buzzy.now`, `i'll`.
- Centred horizontally. **Position (his rule, permanent): the bottom quarter of the screen, text baseline at y = 1500**
  on the 1080x1920 frame (lower than the 1117 opening's 1325; he asked for "just down a little bit more"). On close-up
  clips where his chin/mic sit low, the baseline is **1640**. Overlay the 1080x200 caption PNG at `OVERLAY_Y` (1370)
  or `OVERLAY_Y_CLOSEUP` (1510).
- Cards and pictures placed "below the chin" must end **above y ~1420** so they never sit under the caption line.
- Captions already burned into reused footage (the 1117 hook) cannot be moved: erasing them by inpainting left visible
  smudges on his shirt/neck. Ask him for a caption-free export of that footage instead.

## Wording and timing
- **2-3 words per caption** (the opening: "you've probably / seen videos / like this / actually getting / millions /
  of views / and generating / thousands of / dollars"). Four only if all are short ("let me show you"). Never wider
  than ~760 px. Break at commas and sentence ends. Avoid ending a caption on "of / to / the / a / and / by...".
  `group_captions()` does this with a small optimiser.
- A caption appears when its **first word starts** and holds until the next caption starts; the last one holds to the
  end of the clip. Word times come from faster-whisper (fix mishears like "call in AI" -> "comment AI" by hand).

## Do not
- Do not use other fonts, sizes, outlines, shadows or two-line captions. (Earlier versions used Montserrat SemiBold
  50 px with a soft shadow, Montserrat Bold 66 px, then Montserrat SemiBold 76 px; all were replaced because he saw they
  did not match the opening.)
- Do not touch the captions burned into reused footage (e.g. the hook/CTA of 1117); new captions must match THEM.
- The no-talking split-screen formats (Claude YouTube, Foundable steps) use full-phrase step labels copied from their
  reference video; this skill is for spoken-word captions.

## Check before sending
0. If a new reference video arrives, re-run the font fit (`scratchpad` recipe: crop its captions at y 1230-1400, mask
   pixels with min(R,G,B) > 225, score fonts/sizes/baselines by IoU) rather than eyeballing.
1. Put a frame from the reference captions next to a frame from the new captions (same crop, y 1230-1390): size,
   outline and position must look identical.
2. Look at one frame in each section (hook, demo, ending) for any caption sitting on his face or on a card.
