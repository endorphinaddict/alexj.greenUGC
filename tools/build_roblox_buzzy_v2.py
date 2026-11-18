#!/usr/bin/env python3
"""Buzzy Roblox Shorts, second build (Nov 18 footage), from the Notion page "Roblox Shorts" (Inspiration: example-vid.mp4).

Clips (all his, no burned-in text): hook = DJI 0594 "every day, every week, every month", 0604, 0608 | demo = the four Buzzy
clips 0531, 0532, 0535, 0540 (Nov 17; his Nov 18 `1118.mp4` is the same demo with captions burned in, so the raw clips are used
and captioned in the permanent style) | ending = 0610 ("...post twice a day and you'll start seeing payouts like this") and
0609 ("...comment buzz and I'll send it to you").

His instructions for this build:
 1. hook row, top left: his picture `roblox2.jfif` (Roblox) + Buzzy bee = money bag
 2. the ending emoji of the row is the money bag PNG from the Example Video folder (not the face emoji)
 3. captions: permanent style (tools/captions.py), baseline y 1500
 4. a caption at the very top, visible from the first to the last frame
 5. when he says "comment buzz", the top caption changes to "COMMENT BUZZY" (the bottom captions keep running)
 6. clips come from Footage/ and Footage/Example Video/
Plus the permanent rules: tight cuts, revenue card for the whole "payouts like this" clip (centred, 640 px, top y 110),
metallic riser stopping on the cut into the demo, music from 4.45 s.

Usage: EDIT_WORKDIR=/path build_roblox_buzzy_v2.py OUTFILE
EDIT_WORKDIR holds b2/new/*.MP4 (Nov 18 clips), b2/tr.json (their word timings), bz/new/*.MP4 + bz/new.json (demo clips and timings),
b2/ex/roblox2.jfif + moneybag.png, bz/buzzy_logo.png, bz/rev_oct.png ($7,165.77), assets/music.mp3 + riser_metallic.mp4,
fonts/Lato-Bold.ttf + Montserrat-SemiBold.ttf.
"""
import glob, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ai_influencer as bai
import captions as capstyle

S, W, H, FPS = bai.S, bai.W, bai.H, bai.FPS
B2, BZ, A = f"{S}/b2", f"{S}/bz", f"{S}/assets"
OV = f"{B2}/ov"
os.makedirs(OV, exist_ok=True)

HOOK, DEMO, END = ["0594", "0604", "0608"], ["0531", "0532", "0535", "0540"], ["0610", "0609"]
TOP_TEXT, TOP_TEXT_END = "ROBLOX SHORTS WITH BUZZY", "COMMENT BUZZY"
END_TAIL = 0.25          # let the last word finish
TOP_Y = 62               # centre of the top caption (above the hook row, the revenue card starts at y 110)
ROW_CY = 270             # centre of the hook row; hair top is ~y 500 in the hook clips


def clip_path(cid):
    return (glob.glob(f"{B2}/new/*_{cid}_D.MP4") + glob.glob(f"{BZ}/new/*_{cid}_D.MP4"))[0]


def fix_words(words, cid):
    w = [dict(x) for x in words]
    for x in w:
        if x["w"].lower().startswith(".now"):
            x["w"] = ".now," if x["w"].rstrip().endswith(",") else ".now"
    return w


def build_plan():
    allw = json.load(open(f"{BZ}/new.json"))
    for k, v in json.load(open(f"{B2}/tr.json")).items():
        allw[k.replace(".wav", ".MP4")] = v
    clips, f0 = [], 0
    for cid in HOOK + DEMO + END:
        path = clip_path(cid)
        dur, fps, _ = bai.cds.probe(path)
        audio = bai.cds.load_audio(path)
        keeps, _ = bai.tight_keeps(audio, dur, fps)
        words = fix_words(allw[os.path.basename(path)], cid)
        if cid == END[-1]:      # never clip the last word: run to its end + END_TAIL
            ks, ke = keeps[-1]
            keeps[-1] = (ks, min(math.floor(dur * fps) / fps, max(ke, math.ceil((words[-1]["e"] + END_TAIL) * fps) / fps)))
        sl = np.concatenate([audio[int(s * 16000): int(e * 16000)] for s, e in keeps])
        rms = 20 * math.log10(float(np.sqrt((sl ** 2).mean())) + 1e-9)
        gain = max(-12.0, min(12.0, bai.VOICE_RMS_TARGET - rms))
        pieces, o = [], f0
        for ks, ke in keeps:
            n = max(1, round((ke - ks) * FPS))
            pieces.append((ks, ke, o, n))
            o += n

        def out_frame(ts, pieces=pieces, end=o):
            for ks, ke, o0, n in pieces:
                if ts < ks:
                    return o0
                if ts <= ke:
                    return min(o0 + round((ts - ks) * FPS), o0 + n)
            return end

        caps = capstyle.group_captions(words, bai.display_tokens)
        out_caps = []
        for j, (text, a, b) in enumerate(caps):
            fa = f0 if j == 0 else out_frame(words[a]["s"])
            fb = out_frame(words[caps[j + 1][1]]["s"]) if j + 1 < len(caps) else o
            out_caps.append((text, fa, fb))
        clips.append(dict(cid=cid, path=path, pieces=pieces, f0=f0, f1=o, gain=gain, caps=out_caps, words=words, of=out_frame))
        f0 = o
    return clips, f0


def stage_a(clips, base):
    segs = []
    for cl in clips:
        for k, (ks, ke, o0, n) in enumerate(cl["pieces"]):
            d = n / FPS
            p = f"{OV}/seg_{cl['cid']}_{k:02d}.mkv"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ks:.6f}", "-i", cl["path"], "-map", "0:v:0", "-map", "0:a:0",
                            "-frames:v", str(n), "-vf", f"fps={FPS},scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p",
                            "-af", f"aresample=48000,aformat=channel_layouts=stereo,volume={cl['gain']:.2f}dB,apad=whole_dur={d:.6f},"
                                   f"atrim=0:{d:.6f},afade=t=in:d=0.006,afade=t=out:st={max(0, d - 0.006):.4f}:d=0.006",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-c:a", "pcm_s16le", p], check=True)
            segs.append(p)
    open(f"{OV}/segs.txt", "w").write("".join(f"file '{p}'\n" for p in segs))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OV}/segs.txt", "-c", "copy", base], check=True)


# ---------- overlay art ----------
def hook_row_png(path):
    """[his Roblox picture] + [Buzzy bee] = [money bag], centred, "+" and "=" in the caption font."""
    f = ImageFont.truetype(capstyle._font_path(), 84)
    rb = Image.open(f"{B2}/ex/roblox2.jfif").convert("RGBA").resize((200, 200), Image.LANCZOS)
    mask = Image.new("L", rb.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 199, 199), radius=44, fill=255)   # rounded tile like the Inspiration's logo
    rb.putalpha(mask)
    bee = Image.open(f"{BZ}/buzzy_logo.png").convert("RGBA")
    bee = bee.crop(bee.split()[3].getbbox())
    bee = bee.resize((250, round(bee.height * 250 / bee.width)), Image.NEAREST)       # pixel art stays crisp
    bag = Image.open(f"{B2}/ex/moneybag.png").convert("RGBA")
    bag = bag.crop(bag.split()[3].getbbox())
    bag = bag.resize((round(bag.width * 190 / bag.height), 190), Image.LANCZOS)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    pw, ew = tmp.textlength("+", font=f), tmp.textlength("=", font=f)
    gap = 22
    items = [("img", rb), ("txt", "+", pw), ("img", bee), ("txt", "=", ew), ("img", bag)]
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
            d.text((p[1], p[2]), p[0], font=f, fill=(255, 255, 255, 255), stroke_width=capstyle.STROKE,
                   stroke_fill=(0, 0, 0, 255), anchor="mm")
    cv.save(path)


def top_png(text, path):
    """The top caption: Montserrat SemiBold 56 px white, soft shadow (his top-text style)."""
    f = ImageFont.truetype(f"{S}/fonts/Montserrat-SemiBold.ttf", 56)
    img = Image.new("RGBA", (W, 110), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((W // 2, 58), text, font=f, fill=(0, 0, 0, 200), stroke_width=4, stroke_fill=(0, 0, 0, 200), anchor="mm")
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    ImageDraw.Draw(img).text((W // 2, 55), text, font=f, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(20, 20, 20, 255), anchor="mm")
    img.save(path)


def rms_of(path, t0, t1):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", path, "-vn", "-ac", "1",
                          "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    return 20 * math.log10(float(np.sqrt((a ** 2).mean())) + 1e-9)


def main():
    out = sys.argv[1]
    clips, F = build_plan()
    total = F / FPS
    by = {c["cid"]: c for c in clips}
    f_demo, f_end = by[DEMO[0]]["f0"], by[END[0]]["f0"]
    print(f"{F} frames = {total:.2f}s | demo at {f_demo / FPS:.2f}s | ending at {f_end / FPS:.2f}s", flush=True)
    base = f"{OV}/base.mkv"
    if not os.environ.get("SKIP_A"):
        stage_a(clips, base)

    layers = []   # (png, x, y, fa, fb) frames [fa, fb)
    # 4/5: top caption for the whole video; it becomes COMMENT BUZZY from the word "comment" in the last clip
    c9 = by[END[-1]]
    wi = next(i for i, w in enumerate(c9["words"]) if w["w"].lower().startswith("comment"))
    f_comment = c9["of"](c9["words"][wi]["s"])
    top_png(TOP_TEXT, f"{OV}/top1.png")
    top_png(TOP_TEXT_END, f"{OV}/top2.png")
    layers.append((f"{OV}/top1.png", 0, TOP_Y - 55, 0, f_comment))
    layers.append((f"{OV}/top2.png", 0, TOP_Y - 55, f_comment, F))
    # 1/2: hook row for the talking hook
    hook_row_png(f"{OV}/hook_row.png")
    layers.append((f"{OV}/hook_row.png", 0, ROW_CY - 150, 0, f_demo))
    # permanent rule: revenue card for the ENTIRE "...payouts like this" clip, centred, 640 px, top y 110
    rev = Image.open(f"{BZ}/rev_oct.png").convert("RGB")
    rev.resize((640, round(rev.height * 640 / rev.width)), Image.LANCZOS).save(f"{OV}/rev.png")
    layers.append((f"{OV}/rev.png", (W - 640) // 2, 110, by[END[0]]["f0"], by[END[0]]["f1"]))
    # 3: captions in the permanent style
    for k, cl in enumerate(clips):
        for j, (text, fa, fb) in enumerate(cl["caps"]):
            if fb <= fa:
                continue
            p = f"{OV}/cap_{k}_{j}.png"
            capstyle.render(text, p)
            layers.append((p, 0, capstyle.OVERLAY_Y, fa, fb))

    cmd = ["ffmpeg", "-v", "error", "-stats", "-y", "-i", base]
    for l in layers:
        cmd += ["-i", l[0]]
    mus_i, ris_i = 1 + len(layers), 2 + len(layers)
    cmd += ["-i", f"{A}/music.mp3", "-i", f"{A}/riser_metallic.mp4"]
    parts, prev = [], "0:v"
    for k, (p, x, y, fa, fb) in enumerate(layers):
        parts.append(f"[{prev}][{1 + k}:v]overlay={x}:{y}:enable='between(n,{fa},{fb - 1})'[o{k}]")
        prev = f"o{k}"
    m_gain = (bai.VOICE_RMS_TARGET - 14.0) - rms_of(f"{A}/music.mp3", bai.MUSIC_START, bai.MUSIC_START + total)
    r_gain = (bai.VOICE_RMS_TARGET - 8.0) - rms_of(f"{A}/riser_metallic.mp4", 1.2, 3.0)
    riser_start = max(0.0, f_demo / FPS - 3.0)          # the riser stops dead 3.0 s into the file: on the cut into the demo
    parts.append(f"[{mus_i}:a]atrim=start={bai.MUSIC_START:.3f}:end={bai.MUSIC_START + total + 1:.2f},asetpts=PTS-STARTPTS,"
                 f"aformat=channel_layouts=stereo,aresample=48000,volume={m_gain:.2f}dB,afade=t=in:d=0.03,"
                 f"afade=t=out:st={total - 0.8:.2f}:d=0.8[mus]")
    parts.append(f"[{ris_i}:a]aformat=channel_layouts=stereo,aresample=48000,volume={r_gain:.2f}dB,atrim=0:3.0,"
                 f"adelay={int(riser_start * 1000)}|{int(riser_start * 1000)}[ris]")
    parts.append("[0:a]aresample=48000,aformat=channel_layouts=stereo[voice];"
                 "[voice][mus][ris]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.9:level=disabled[aout]")
    cmd += ["-filter_complex", ";".join(parts), "-map", f"[{prev}]", "-map", "[aout]", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    json.dump([dict(cid=c["cid"], f0=c["f0"], f1=c["f1"], caps=c["caps"]) for c in clips], open(f"{B2}/plan.json", "w"), indent=1)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
