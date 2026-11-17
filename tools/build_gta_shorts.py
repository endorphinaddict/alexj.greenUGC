#!/usr/bin/env python3
"""Build the 'OpenArt + YouTube (GTA 6 / YT Shorts)' talking video, copying his example's structure.

Usage: EDIT_WORKDIR=/path build_gta_shorts.py OUTFILE
EDIT_WORKDIR holds: rb/ (the DJI clips), rb.json (word timings from transcribe_clips.py),
assets/ (music.mp3, riser_metallic.mp4, emoji.png, earnings.jpg), assets_gta/ (gta.png, card1-3.png cropped
from the example), fonts/Montserrat-SemiBold.ttf.

Reuses the tight-cutting and 1-2 word caption logic from build_ai_influencer.py.
Everything is frame-accurate: overlays are enabled by frame number on one concatenated base.
"""
import glob, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ai_influencer as bai

S, W, H, FPS = bai.S, bai.W, bai.H, bai.FPS
RB, A, AG, OV = f"{S}/rb", f"{S}/assets", f"{S}/assets_gta", f"{S}/overlays_gta"
os.makedirs(OV, exist_ok=True)

# Script order. Duplicate takes: the last take of each line (0478, 0493).
ORDER = ["0453", "0458", "0469", "0471", "0478", "0481", "0483", "0485", "0486", "0489", "0493", "0495", "0497"]
HOOK_CLIPS = ORDER[:4]          # talking hook: hook row at the top
SCREEN_FIRST = "0478"           # riser lands on the cut into this clip
CAPTION_Y = {"0495": 1580, "0497": 1580}   # close-ups: face (and chin) sit lower, so keep captions below it
CAPTION_Y_DEFAULT = 1222


def clip_path(cid):
    return glob.glob(f"{RB}/*_{cid}_D.MP4")[0]


def fix_words(cid, words):
    w = [dict(x) for x in words]
    if cid == "0485":   # whisper: "openr" ".ai" "-direct"  ->  one token
        i = next(k for k, x in enumerate(w) if x["w"].lower().startswith("openr"))
        w[i:i + 3] = [dict(s=w[i]["s"], e=w[i + 2]["e"], w="openart.ai/direct")]
    if cid == "0495":
        for x in w:
            if x["w"].lower().startswith("boasting"):
                x["w"] = "posting"
    return w


def build_plan():
    allw = json.load(open(f"{S}/rb.json"))
    clips, f0 = [], 0
    for cid in ORDER:
        path = clip_path(cid)
        dur, fps, _ = bai.cds.probe(path)
        audio = bai.cds.load_audio(path)
        keeps, level = bai.tight_keeps(audio, dur, fps)
        sl = np.concatenate([audio[int(s * 16000): int(e * 16000)] for s, e in keeps])
        rms = 20 * math.log10(float(np.sqrt((sl ** 2).mean())) + 1e-9)
        gain = max(-12.0, min(12.0, bai.VOICE_RMS_TARGET - rms))
        pieces, o = [], f0
        for ks, ke in keeps:
            n = max(1, round((ke - ks) * FPS))
            pieces.append((ks, ke, o, n))
            o += n
        words = fix_words(cid, allw[os.path.basename(path)])

        def out_frame(ts, pieces=pieces, f0=f0, end=o):
            for ks, ke, o0, n in pieces:
                if ts < ks:
                    return o0
                if ts <= ke:
                    return min(o0 + round((ts - ks) * FPS), o0 + n)
            return end

        caps = bai.phrase_captions(words)
        out_caps = []
        for j, (text, a, b) in enumerate(caps):
            fa = f0 if j == 0 else out_frame(words[a]["s"])
            fb = out_frame(words[caps[j + 1][1]]["s"]) if j + 1 < len(caps) else o
            out_caps.append((text, fa, fb))
        wf = [out_frame(x["s"]) for x in words]
        clips.append(dict(cid=cid, path=path, pieces=pieces, f0=f0, f1=o, gain=gain, caps=out_caps, wf=wf, words=words))
        f0 = o
    return clips, f0


# ---------- overlay art ----------
def hook_row_png(path):
    """GTA 6 image + '+ YT Shorts =' + money-mouth emoji (his example's hook row), above the hair line."""
    f = bai.font(bai.FONT_CAP, 64)
    g = Image.open(f"{AG}/gta.png").convert("RGBA")
    gh = 150
    g = g.resize((round(g.width * gh / g.height), gh), Image.LANCZOS)
    emo = Image.open(f"{AG}/emoji.png").convert("RGBA").resize((96, 96), Image.LANCZOS)
    text = "+ YT Shorts ="
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = tmp.textlength(text, font=f)
    gap = 22
    total = g.width + gap + tw + gap + emo.width
    x0 = (W - total) / 2
    cv = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
    cy = 100
    cv.alpha_composite(g, (round(x0), cy - gh // 2))
    shadow = Image.new("RGBA", cv.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((x0 + g.width + gap, cy + 3), text, font=f, fill=(0, 0, 0, 200),
                                stroke_width=4, stroke_fill=(0, 0, 0, 200), anchor="lm")
    cv.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(4)))
    ImageDraw.Draw(cv).text((x0 + g.width + gap, cy), text, font=f, fill=(255, 255, 255, 255),
                            stroke_width=3, stroke_fill=(20, 20, 20, 255), anchor="lm")
    cv.alpha_composite(emo, (round(x0 + g.width + gap + tw + gap), cy - 48))
    cv.save(path)


def cta_png(path):
    """Top call-to-action text (kept above the hair line)."""
    f = bai.font(bai.FONT_CAP, 56)
    img = Image.new("RGBA", (W, 190), (0, 0, 0, 0))
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    lines = [('Comment "ai"', 50), ("for the full prompt", 128)]
    for t, y in lines:
        ImageDraw.Draw(shadow).text((W // 2, y + 3), t, font=f, fill=(0, 0, 0, 200), stroke_width=4,
                                    stroke_fill=(0, 0, 0, 200), anchor="mm")
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(4)))
    d = ImageDraw.Draw(img)
    for t, y in lines:
        d.text((W // 2, y), t, font=f, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(20, 20, 20, 255), anchor="mm")
    img.save(path)


def card(src, path, width=300):
    im = Image.open(src).convert("RGB")
    im.resize((width, round(im.height * width / im.width)), Image.LANCZOS).save(path)
    return round(im.height * width / im.width)


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
    layers = []  # (png, x, y, fa, fb)

    hook_row_png(f"{OV}/hook_row.png")
    layers.append((f"{OV}/hook_row.png", 0, 90, 0, by[HOOK_CLIPS[-1]]["f1"]))

    # payout cards: one per phrase of "every day, every week, every month", to the right of his head
    # where he points (head is x ~80-560 in this clip); they stay until the cut.
    c0 = by["0453"]
    y = 520
    for k, (tok, name) in enumerate(((0, "card1"), (2, "card2"), (4, "card3"))):
        h = card(f"{AG}/{name}.png", f"{OV}/{name}.png")
        layers.append((f"{OV}/{name}.png", 700, y, c0["wf"][tok], c0["f1"]))
        y += h + 18

    # earnings card above his head on "payouts like this"
    c = by["0495"]
    tok = next(i for i, w in enumerate(c["words"]) if w["w"].lower().startswith("payouts"))
    h = card(f"{AG}/earnings.jpg", f"{OV}/earn_top.png", width=420)
    layers.append((f"{OV}/earn_top.png", 330, 55, c["wf"][tok], c["f1"]))

    # CTA text at the top for the last clip
    cta_png(f"{OV}/cta.png")
    layers.append((f"{OV}/cta.png", 0, 40, by["0497"]["f0"], F))

    # captions
    for k, cl in enumerate(clips):
        cy = CAPTION_Y.get(cl["cid"], CAPTION_Y_DEFAULT)
        for j, (text, fa, fb) in enumerate(cl["caps"]):
            p = f"{OV}/cap_{k}_{j}.png"
            bai.caption_png(text, p)
            layers.append((p, 0, cy - bai.CAP_H // 2, fa, fb))

    # ---------- ffmpeg ----------
    cmd = ["ffmpeg", "-v", "error", "-stats", "-y"]
    for cl in clips:
        cmd += ["-i", cl["path"]]
    for l in layers:
        cmd += ["-i", l[0]]
    n_clips, n_layers = len(clips), len(layers)
    mus_i = n_clips + n_layers
    ris_i = mus_i + 1
    cmd += ["-i", f"{A}/music.mp3", "-i", f"{A}/riser_metallic.mp4"]

    parts, lab = [], []
    for i, cl in enumerate(clips):
        k = len(cl["pieces"])
        parts.append(f"[{i}:v]split={k}" + "".join(f"[sv{i}_{j}]" for j in range(k)))
        parts.append(f"[{i}:a]asplit={k}" + "".join(f"[sa{i}_{j}]" for j in range(k)))
        for j, (ks, ke, o0, n) in enumerate(cl["pieces"]):
            d = n / FPS
            parts.append(f"[sv{i}_{j}]trim=start={ks:.6f}:end={ks + (n + 3) / FPS:.6f},setpts=PTS-STARTPTS,fps={FPS},"
                         f"trim=end_frame={n},scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p[pv{i}_{j}]")
            parts.append(f"[sa{i}_{j}]atrim=start={ks:.6f}:end={ks + d:.6f},asetpts=PTS-STARTPTS,aresample=48000,"
                         f"aformat=channel_layouts=stereo,volume={cl['gain']:.2f}dB,apad=whole_dur={d:.6f},atrim=0:{d:.6f},"
                         f"afade=t=in:d=0.008,afade=t=out:st={max(0, d - 0.008):.4f}:d=0.008[pa{i}_{j}]")
            lab.append(f"[pv{i}_{j}][pa{i}_{j}]")
    parts.append("".join(lab) + f"concat=n={len(lab)}:v=1:a=1[base][voice]")

    prev = "base"
    for k, (p, x, yy, fa, fb) in enumerate(layers):
        nxt = f"o{k}"
        parts.append(f"[{prev}][{n_clips + k}:v]overlay={x}:{yy}:enable='between(n,{fa},{fb - 1})'[{nxt}]")
        prev = nxt

    m_rms = rms_of(f"{A}/music.mp3", bai.MUSIC_START, bai.MUSIC_START + total)
    r_rms = rms_of(f"{A}/riser_metallic.mp4", 1.2, 3.0)
    m_gain = (bai.VOICE_RMS_TARGET - 14.0) - m_rms
    r_gain = (bai.VOICE_RMS_TARGET - 8.0) - r_rms
    t_cut = by[SCREEN_FIRST]["f0"] / FPS
    riser_start = max(0.0, t_cut - 3.0)
    print(f"{F} frames = {total:.2f}s | screen section starts {t_cut:.2f}s | riser file placed at {riser_start:.2f}s", flush=True)
    parts.append(f"[{mus_i}:a]atrim=start={bai.MUSIC_START:.3f}:end={bai.MUSIC_START + total + 1:.2f},asetpts=PTS-STARTPTS,"
                 f"aformat=channel_layouts=stereo,aresample=48000,volume={m_gain:.2f}dB,afade=t=in:d=0.03,"
                 f"afade=t=out:st={total - 1.2:.2f}:d=1.2[mus]")
    parts.append(f"[{ris_i}:a]aformat=channel_layouts=stereo,aresample=48000,volume={r_gain:.2f}dB,"
                 f"adelay={int(riser_start * 1000)}|{int(riser_start * 1000)}[ris]")
    parts.append("[voice][mus][ris]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.97[aout]")
    cmd += ["-filter_complex", ";".join(parts), "-map", f"[{prev}]", "-map", "[aout]", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    json.dump([dict(cid=c["cid"], f0=c["f0"], f1=c["f1"], caps=c["caps"]) for c in clips], open(f"{S}/gta_plan.json", "w"), indent=1)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
