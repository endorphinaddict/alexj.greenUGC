#!/usr/bin/env python3
"""Buzzy "monetize YT Shorts" (Roblox) video, one version per shirt (Nov 22 footage).

Reference (copied 1:1): `Footage/Example Video/Its never been easier to monetize YT shorts, buzzy.now is printing rn.mp4` (29.07 s):
  0.00-11.0  HOOK  three talking clips, hook row on top for the whole hook: Roblox tile + Buzzy bee = money-mouth face.
             "you've probably seen videos like this" -> he holds ~1.9 s while the Roblox story pop-up plays ("In this town, there is only
             one rule.", the pop-up's own sound) -> "actually getting millions of views and generating thousands of dollars"
             (the 9M views picture on "millions of views", the estimated-revenue card on "thousands of dollars") ->
             "let me show you how you can make the same exact video before someone else puts it behind a $5,000 course".
  11.0-23.2  DEMO  `Footage/demo.mp4` (screen demo with his voice-over and its own burned-in captions), metallic riser stops on the cut.
  23.2-29.07 CTA   "start posting these twice a day ... payouts like this" (revenue card on screen the WHOLE clip) and
             "if you want the prompt that I use, just comment buzz and I'll DM it to you".
  Music under everything (from its peak, 4.45 s into the track). Captions in the permanent style (tools/captions.py).

Usage: EDIT_WORKDIR=/path build_buzzy_shirts.py GROUP OUTFILE      GROUP = white | red | blackgold | blackpolo
EDIT_WORKDIR holds bs/clips/NNNN.mp4 (the Nov 22 clips), bs/demo.mp4, bs/tr.json (word timings from transcribe_clips.py),
bs/pics/ (images.jpg, money-mouth-face_1f911.png, views-9M.png, rev_nov.png, buzzy_logo.png, roblox_story.mp4),
assets/music.mp3 + riser_metallic.mp4, fonts/Lato-Bold.ttf.
Audio rule (his): his voice is left exactly as recorded (no gain, no filters). Only the music and riser get a level.
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ai_influencer as bai
import captions as capstyle

S, W, H, FPS = bai.S, bai.W, bai.H, bai.FPS
BS, A = f"{S}/bs", f"{S}/assets"

# shirt -> clips in script order: line 1 | line 2 | line 3 | payouts CTA | comment CTA   (checked on frames, one shirt per group)
GROUPS = {
    "white":     ["0773", "0774", "0777", "0778", "0780"],
    "red":       ["0783", "0784", "0785", "0786", "0787"],
    "blackgold": ["0789", "0790", "0794", "0796", "0797"],   # black henley with the gold pattern on the lower half
    "blackpolo": ["0799", "0802", "0805", "0806", "0807"],   # black polo with the chain collar
}
# His new Roblox shorts replace the Notion story clip as the pop-up (the pop-up plays with its own sound while his face holds; the hold ends
# exactly where the pop-up sentence ends, so there is no silent time). Alternating by shirt.
POPS = {"white": ("short1", 1.72), "red": ("short2", 1.85), "blackgold": ("short1", 1.72), "blackpolo": ("short2", 1.85)}   # (file in bs/pics, seconds used)
HOLD_S = None            # set per group from POPS
DEMO_END = 12.2          # seconds of demo.mp4 used
END_TAIL = 0.25          # last word of the video finishes + this much
POP_W, POP_X, POP_Y = 320, 30, 396     # Roblox story pop-up (9:16): left of his head (he sits right of centre), under the hook row
CARD_W, CARD_Y = 420, 1540            # views and revenue cards: centred, JUST UNDER the captions (his request; caption baseline 1500)
ROW_CY = 255             # hook row centre (hair top is >= y 445 in every hook take)


def clip_path(cid):
    return f"{BS}/demo.mp4" if cid == "demo" else f"{BS}/clips/{cid}.mp4"


def clean_words(cid, words):
    w = [dict(x) for x in words]
    for x in w:
        x["w"] = x["w"].replace(",", "") if x["w"].strip().lower().strip(".,") in ("comment", "buzz") else x["w"]
    return w


def build_plan(group):
    global HOLD_S
    HOLD_S = POPS[group][1]
    allw = {k.replace(".wav", ""): v for k, v in json.load(open(f"{BS}/tr.json")).items()}
    ids = GROUPS[group]
    order = [("L1", ids[0]), ("L2", ids[1]), ("L3", ids[2]), ("DEMO", "demo"), ("P1", ids[3]), ("P2", ids[4])]
    clips, f0 = [], 0
    for role, cid in order:
        path = clip_path(cid)
        dur, fps, _ = bai.cds.probe(path)
        audio = bai.cds.load_audio(path)
        keeps, _ = bai.tight_keeps(audio, dur, fps)
        words = clean_words(cid, allw[cid])
        ks, ke = keeps[0][0], keeps[-1][1]
        if role == "DEMO":
            ke = DEMO_END      # his voice ends 12.18 s; the picture goes black at 12.25 s (the rest of demo.mp4 is black / a still card)
        if role == "P2":                                    # let the last word finish
            ke = min(math.floor(dur * fps) / fps, max(ke, math.ceil((words[-1]["e"] + END_TAIL) * fps) / fps))
        keeps = [(ks, ke)] if len(keeps) == 1 or role in ("DEMO", "P2") else keeps
        pieces, o = [], f0
        for a, b in keeps:
            n = max(1, round((b - a) * FPS))
            pieces.append((a, b, o, n))
            o += n
        hold = None
        if role == "L1":                                     # hold on his face while the Roblox story plays
            n = round(HOLD_S * FPS)
            hold = (pieces[-1][1], o, n)                     # (source start, out frame, frames)
            pieces.append((pieces[-1][1], pieces[-1][1] + n / FPS, o, n))
            o += n

        def of(ts, pieces=pieces, end=o):
            for a, b, o0, n in pieces:
                if ts < a:
                    return o0
                if ts <= b:
                    return min(o0 + round((ts - a) * FPS), o0 + n)
            return end

        out_caps = []
        if role != "DEMO":                                   # the demo carries his own burned-in captions
            caps = capstyle.group_captions(words, bai.display_tokens)
            for j, (text, a, b) in enumerate(caps):
                fa = f0 if j == 0 else of(words[a]["s"])
                fb = of(words[caps[j + 1][1]]["s"]) if j + 1 < len(caps) else o
                out_caps.append((text, fa, fb))
        clips.append(dict(role=role, cid=cid, path=path, pieces=pieces, f0=f0, f1=o, words=words, caps=out_caps, of=of, hold=hold))
        f0 = o
    return clips, f0


def stage_a(clips, base, tag):
    segs = []
    for cl in clips:
        for k, (a, b, o0, n) in enumerate(cl["pieces"]):
            d = n / FPS
            p = f"{OV}/{tag}_{cl['role']}_{k:02d}.mkv"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.6f}", "-i", cl["path"], "-map", "0:v:0", "-map", "0:a:0",
                            "-frames:v", str(n), "-vf", f"fps={FPS},scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p",
                            "-af", f"aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={d:.6f},atrim=0:{d:.6f}",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-c:a", "pcm_s16le", p], check=True)
            segs.append(p)
    open(f"{OV}/{tag}_segs.txt", "w").write("".join(f"file '{p}'\n" for p in segs))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OV}/{tag}_segs.txt", "-c", "copy", base], check=True)


def rounded(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=r, fill=255)
    im = im.convert("RGBA")
    im.putalpha(m)
    return im


def hook_row_png(path):
    """[blue Roblox tile] + [YouTube Shorts logo] = [money-mouth face], centred, "+" and "=" in the caption font (reference hook row)."""
    f = ImageFont.truetype(capstyle._font_path(), 84)
    tile = rounded(Image.open(f"{BS}/pics/images.jpg").convert("RGB").resize((230, 230), Image.LANCZOS), 50)
    bee = Image.open(f"{BS}/pics/youtube_shorts_cutout.png").convert("RGBA")             # his request: YouTube Shorts logo instead of the yellow bee
    bee = bee.crop(bee.split()[3].point(lambda v: 255 if v > 40 else 0).getbbox())
    bee = bee.resize((round(bee.width * 250 / bee.height), 250), Image.LANCZOS)
    face = Image.open(f"{BS}/pics/money-mouth-face_1f911.png").convert("RGBA").resize((170, 170), Image.LANCZOS)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    pw, ew = tmp.textlength("+", font=f), tmp.textlength("=", font=f)
    gap = 22
    items = [("img", tile), ("txt", "+", pw), ("img", bee), ("txt", "=", ew), ("img", face)]
    total = sum(it[1].width if it[0] == "img" else it[2] for it in items) + gap * (len(items) - 1)
    cv = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    cy = 150
    sh = Image.new("RGBA", cv.size, (0, 0, 0, 0))
    x, pos = (W - total) / 2, []
    for it in items:
        if it[0] == "img":
            pos.append((it[1], round(x), cy - it[1].height // 2))
            x += it[1].width + gap
        else:
            pos.append((it[1], x + it[2] / 2, cy))
            x += it[2] + gap
    for p in pos:
        if isinstance(p[0], Image.Image):
            sh.paste((0, 0, 0, 255), (p[1], p[2] + 5), p[0].split()[3].point(lambda v: int(v * 0.5)))
    cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(cv)
    for p in pos:
        if isinstance(p[0], Image.Image):
            cv.alpha_composite(p[0], (p[1], p[2]))
        else:
            d.text((p[1], p[2]), p[0], font=f, fill=(255, 255, 255, 255), stroke_width=capstyle.STROKE, stroke_fill=(0, 0, 0, 255), anchor="mm")
    cv.save(path)


def fit_png(src, width, path):
    im = Image.open(src).convert("RGBA")
    im.resize((width, round(im.height * width / im.width)), Image.LANCZOS).save(path)


def rms_of(path, t0, t1):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", path, "-vn", "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    return 20 * math.log10(float(np.sqrt((a ** 2).mean())) + 1e-9)


def main():
    global OV
    group, out = sys.argv[1], sys.argv[2]
    OV = f"{BS}/ov_{group}"
    os.makedirs(OV, exist_ok=True)
    clips, F = build_plan(group)
    total = F / FPS
    by = {c["role"]: c for c in clips}
    f_demo = by["DEMO"]["f0"]
    print(f"[{group}] {[c['cid'] for c in clips]} -> {F} frames = {total:.2f}s | demo at {f_demo / FPS:.2f}s", flush=True)
    base = f"{OV}/base.mkv"
    if not os.environ.get("SKIP_A"):
        stage_a(clips, base, group)

    layers = []   # (png, x, y, fa, fb) frames [fa, fb)
    hook_row_png(f"{OV}/hook_row.png")
    layers.append((f"{OV}/hook_row.png", 0, ROW_CY - 150, 0, f_demo))
    # 9M views on "millions of views", revenue card on "thousands of dollars" (clip 2)
    c2 = by["L2"]
    wi = lambda key: next(i for i, w in enumerate(c2["words"]) if w["w"].lower().strip(".,").startswith(key))
    f_mill, f_thou = c2["of"](c2["words"][wi("millions")]["s"]), c2["of"](c2["words"][wi("thousands")]["s"])
    fit_png(f"{BS}/pics/views-9M.png", CARD_W, f"{OV}/views.png")
    fit_png(f"{BS}/pics/rev_nov.png", CARD_W, f"{OV}/rev_small.png")
    layers.append((f"{OV}/views.png", (W - CARD_W) // 2, CARD_Y, f_mill, f_thou))
    layers.append((f"{OV}/rev_small.png", (W - CARD_W) // 2, CARD_Y, f_thou, c2["f1"]))
    # permanent rule: payouts CTA clip carries the revenue card for the ENTIRE clip, centred, 640 px, top y 110
    fit_png(f"{BS}/pics/rev_nov.png", 640, f"{OV}/rev_top.png")
    layers.append((f"{OV}/rev_top.png", (W - 640) // 2, 110, by["P1"]["f0"], by["P1"]["f1"]))
    # captions (permanent style); close-ups (the two CTA clips) use the lower baseline
    for cl in clips:
        for j, (text, fa, fb) in enumerate(cl["caps"]):
            if fb <= fa:
                continue
            p = f"{OV}/cap_{cl['role']}_{j}.png"
            capstyle.render(text, p)
            layers.append((p, 0, capstyle.OVERLAY_Y_CLOSEUP if cl["role"] in ("P1", "P2") else capstyle.OVERLAY_Y, fa, fb))

    # Roblox story pop-up (video + its own sound) during the hold
    hs, hf0, hn = by["L1"]["hold"]
    pop = f"{OV}/pop.mkv"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{BS}/pics/{POPS[group][0]}.mp4", "-t", f"{(hn + 4) / FPS:.4f}", "-vf",      # a few spare frames: the enable window ends the pop-up exactly
                    
                    f"fps={FPS},scale={POP_W}:-2:flags=lanczos,setsar=1,format=yuv420p", "-an", "-c:v", "libx264", "-crf", "12", pop], check=True)
    pop_h = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=height", "-of", "csv=p=0", pop],
                               capture_output=True, text=True).stdout.strip())

    # Pop-up layer with exact frame times: transparent for F frames, the pop-up on frames [hf0, hf0+hn). (Time-based `enable` on the overlay
    # was off by a frame depending on timestamp drift, and n-based `enable` dropped the pop-up, so no `enable` is used.)
    pop_layer = f"{OV}/pop_layer.mkv"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black@0.0:s={POP_W}x{pop_h}:r={FPS}:d={total + 1:.3f},format=yuva420p",
                    "-i", pop, "-filter_complex",
                    f"[0:v]setpts=N/({FPS}*TB)[bg];[1:v]trim=end_frame={hn},format=yuva420p,setpts=N/({FPS}*TB)+{hf0}/({FPS}*TB)[pv];"
                    f"[bg][pv]overlay=0:0:eof_action=pass:format=auto,format=yuva420p[o]", "-map", "[o]", "-frames:v", str(F + 2),
                    "-c:v", "ffv1", "-pix_fmt", "yuva420p", pop_layer], check=True)

    cmd = ["ffmpeg", "-v", "error", "-stats", "-y", "-i", base]
    for l in layers:
        cmd += ["-i", l[0]]
    pop_i, st_i, mus_i, ris_i = 1 + len(layers), 2 + len(layers), 3 + len(layers), 4 + len(layers)
    cmd += ["-i", pop_layer, "-i", f"{BS}/pics/{POPS[group][0]}.mp4", "-i", f"{A}/music.mp3", "-i", f"{A}/riser_metallic.mp4"]
    parts, prev = [f"[0:v]setpts=N/({FPS}*TB)[b0]"], "b0"      # exact frame times: the concatenated base drifts a few ms, which moved time-based overlay edges by a frame
    for k, (p, x, y, fa, fb) in enumerate(layers):
        parts.append(f"[{prev}][{1 + k}:v]overlay={x}:{y}:enable='between(n,{fa},{fb - 1})'[o{k}]")
        prev = f"o{k}"
    parts.append(f"[{pop_i}:v]setpts=N/({FPS}*TB),format=yuva420p[pv]")
    parts.append(f"[{prev}][pv]overlay={POP_X}:{POP_Y}:shortest=0:eof_action=pass:format=auto[vout]")

    v_rms = rms_of(base, 0, total)                              # his voice level as recorded: music and riser sit under it
    m_gain = (v_rms - 14.0) - rms_of(f"{A}/music.mp3", bai.MUSIC_START, bai.MUSIC_START + total)
    r_gain = (v_rms - 8.0) - rms_of(f"{A}/riser_metallic.mp4", 1.2, 3.0)
    riser_start = max(0.0, f_demo / FPS - 3.0)                 # the riser stops dead 3.0 s into the file: on the cut into the demo
    parts.append(f"[{mus_i}:a]atrim=start={bai.MUSIC_START:.3f}:end={bai.MUSIC_START + total + 1:.2f},asetpts=PTS-STARTPTS,"
                 f"aformat=channel_layouts=stereo,aresample=48000,volume={m_gain:.2f}dB,afade=t=in:d=0.03,afade=t=out:st={total - 0.8:.2f}:d=0.8[mus]")
    parts.append(f"[{ris_i}:a]aformat=channel_layouts=stereo,aresample=48000,volume={r_gain:.2f}dB,atrim=0:3.0,"
                 f"adelay={int(riser_start * 1000)}|{int(riser_start * 1000)}[ris]")
    parts.append(f"[{st_i}:a]atrim=0:{hn / FPS:.4f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,afade=t=out:st={hn / FPS - 0.03:.4f}:d=0.03,"
                 f"adelay={int(hf0 / FPS * 1000)}|{int(hf0 / FPS * 1000)}[sto]")
    parts.append("[0:a]aresample=48000,aformat=channel_layouts=stereo[voice]")
    parts.append("[voice][sto][mus][ris]amix=inputs=4:duration=first:normalize=0[aout]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    json.dump(dict(group=group, clips=[(c["role"], c["cid"], c["f0"], c["f1"]) for c in clips], hold=(hf0, hn), pop_h=pop_h,
                   views=(f_mill, f_thou), caps=[(c["role"], c["caps"]) for c in clips]), open(f"{BS}/plan_{group}.json", "w"), indent=1)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
