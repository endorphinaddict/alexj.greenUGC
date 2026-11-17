# Video editing rules for this repo

Alexander's UGC videos are edited by Claude from raw clips, a Notion brief and a reference video.
Follow these on every edit. They come from his direct feedback.

## Placement: never cover the face

- **Never put an asset, picture, card or pop-up in front of his face.** Place each one *adjacent*
  to the face: beside the head, above it, or below the chin.
- Find the head zone per clip before placing anything. In the DJI talking clips at 1080x1920 the head
  (hair and face) is roughly x 100-710, y 260-1000. Hair top is as low as y=380 in some clips.
- Keep the top hook row and the top call-to-action text above the hair line (they live at y < 240).
- Pop-ups with a 9:16 shape (e.g. the dance clip) go to the side of the head (x >= 730, 320px wide).
- Cards (views, earnings) go below the chin (y ~1290) or, when he points to the top of the screen,
  above the head (y ~55).
- Captions sit at y ~1242, below the chin.

## Assets that must appear

- Earnings picture on "thousands of dollars" **and** on "get payouts like this" (he points up at the
  top of the screen there, so put it at the top, above his head).
- Views picture on "millions of views".
- Riser sound effect leading into the screen section; background music kept low under his voice.

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
