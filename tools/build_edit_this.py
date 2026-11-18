#!/usr/bin/env python3
"""Build the "Edit This" video (GTA 6 + Buzzy, Notion page "Faceless YouTube Channel").

He assembles the edit himself (`Footage/edit this.mp4`: talking hook -> Buzzy screen demo -> close-up CTA),
and this script finishes it in the style of his example `Footage/Example Video/AQMq...mp4`:
  - tight cuts on his voice (no dead space), final word kept + ~0.25 s
  - hook row at the top for the whole talking hook: GTA 6 art + "+" + Buzzy bee logo + "=" + money-mouth emoji
    (the example says "YT Shorts"; his direction: the Buzzy bee logo instead; the Notion hook is "GTA + (Buzzy Logo) = 🤑")
  - three estimated-revenue cards ($619.83, $3,287.17, $16,796.88, cropped from the example) on
    "every day / every week / every month", one straight column above his pen tip (he points with a pen)
  - the estimated-revenue card ($7,165.77, as in the example) for the ENTIRE "post two of these a day ... payouts
    like this" clip, centred at the top, 640 px wide (his permanent rule)
  - captions in the permanent style (tools/captions.py), close-up CTA captions lower
  - music from 4.45 s, metallic riser ending on the cut into the screen demo

Usage: EDIT_WORKDIR=/path build_edit_this.py OUTFILE
EDIT_WORKDIR holds: et/in/edit_this.mp4, et/in.json (word timings from transcribe_clips.py), et/na/gta2.webp and
et/na/buzzy_logo.png (Notion assets), et/cards/card1-3.png + rev_cta.png, assets/music.mp3, assets/riser_metallic.mp4,
assets/emoji.png, fonts/Lato-Bold.ttf.
Two passes: (A) cut pieces -> base.mkv (no ffmpeg split buffering of a 1080x1920 source), (B) overlays + audio.
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ai_influencer as bai
import captions as capstyle

S, W, H, FPS = bai.S, bai.W, bai.H, bai.FPS
ET, A = f"{S}/et", f"{S}/assets"
OV = f"{ET}/ov"
os.makedirs(OV, exist_ok=True)
SRC = f"{ET}/in/edit_this.mp4"

# Section boundaries in his assembled file (scene cuts): hook talking | Buzzy screen demo | close-up CTA
DEMO_START = 17.0667
CTA_START = 38.9333
CTA2_START = 41.9333          # "And if you want the exact prompt..."
END_TAIL = 0.25              # keep this much after the last word ends (never clip the final word)

# Pen tip measured on gridded frames (1080x1920) while he says each phrase. Head is x ~80-560.
TIP = {"day": (800, 620), "week": (800, 1060), "month": (830, 1530)}
CARD_W, CARD_X = 360, 690    # one straight column, same size; right of his head, over where the pen points
CARD_GAP = 25
CARD_MAX_BOTTOM = 1415       # cards must end above the caption band (baseline 1500)


def run(cmd):
    subprocess.run(cmd, check=True)


def plan():
    words = [dict(w) for w in json.load(open(f"{ET}/in.json"))["edit_this.mp4"]]
    for w in words:                      # captions spell numbers out ("gta six", not "gta 6")
        if w["w"].strip() == "6":
            w["w"] = " six"
    for i in range(1, len(words)):       # "...when GTA 6 comes out, it's going to be..." (whisper dropped the comma)
        if words[i]["w"].strip() == "out" and words[i - 1]["w"].strip() == "comes":
            words[i]["w"] = " out,"
    dur, fps, _ = bai.cds.probe(SRC)
    audio = bai.cds.load_audio(SRC)
    keeps, _ = bai.tight_keeps(audio, dur, fps)
    # never clip the final word: run to last word + END_TAIL
    last_e = words[-1]["e"]
    ks, ke = keeps[-1]
    keeps[-1] = (ks, min(math.floor(dur * fps) / fps, max(ke, math.ceil((last_e + END_TAIL) * fps) / fps)))
    # a keep must not straddle a section cut (the riser and the revenue card land on those cuts)
    out = []
    for ks, ke in keeps:
        for c in (DEMO_START, CTA_START, CTA2_START):
            if ks < c - 0.5 / fps and ke > c + 0.5 / fps:
                out.append((ks, round(c * fps) / fps))
                ks = round(c * fps) / fps
        out.append((ks, ke))
    pieces, o = [], 0
    for ks, ke in out:
        n = max(1, round((ke - ks) * FPS))
        pieces.append((ks, ke, o, n))
        o += n

    def out_frame(ts):
        for ks, ke, o0, n in pieces:
            if ts < ks:
                return o0
            if ts <= ke:
                return min(o0 + round((ts - ks) * FPS), o0 + n)
        return o

    def first_frame_after(t):       # output frame where source time t (a section cut) starts
        return next(o0 for ks, ke, o0, n in pieces if ks >= t - 0.5 / FPS)

    return words, audio, pieces, o, out_frame, first_frame_after


KEEP_TOGETHER = [("gta", "six"), ("two", "weeks")]   # never split these across two captions


def display_tokens(words):
    """bai.display_tokens, plus pairs that must share a caption (joined with a no-break space, drawn as a space)."""
    toks = bai.display_tokens(words)
    out = []
    for t in toks:
        if out and (out[-1][0], t[0]) in KEEP_TOGETHER:
            out[-1] = (out[-1][0] + " " + t[0], out[-1][1], t[2])
        else:
            out.append(t)
    return out


def section_gains(audio, pieces):
    """One voice gain per section (hook / demo / CTA), normalised to bai.VOICE_RMS_TARGET."""
    gains = {}
    for name, a, b in (("hook", 0, DEMO_START), ("demo", DEMO_START, CTA_START), ("cta", CTA_START, 1e9)):
        sl = [audio[int(ks * 16000): int(ke * 16000)] for ks, ke, _, _ in pieces if a - 0.02 <= ks < b - 0.02]
        sl = np.concatenate(sl)
        rms = 20 * math.log10(float(np.sqrt((sl ** 2).mean())) + 1e-9)
        gains[name] = max(-12.0, min(12.0, bai.VOICE_RMS_TARGET - rms))
    return gains


def section_of(ks):
    return "hook" if ks < DEMO_START - 0.02 else ("demo" if ks < CTA_START - 0.02 else "cta")


def stage_a(pieces, gains, base):
    segs = []
    for k, (ks, ke, o0, n) in enumerate(pieces):
        d = n / FPS
        p = f"{OV}/seg_{k:03d}.mkv"
        g = gains[section_of(ks)]
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ks:.6f}", "-i", SRC, "-frames:v", str(n),
             "-vf", f"fps={FPS},scale={W}:{H},setsar=1,format=yuv420p",
             "-af", f"aresample=48000,aformat=channel_layouts=stereo,volume={g:.2f}dB,apad=whole_dur={d:.6f},"
                    f"atrim=0:{d:.6f},afade=t=in:d=0.006,afade=t=out:st={max(0, d - 0.006):.4f}:d=0.006",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-c:a", "pcm_s16le", p])
        segs.append(p)
    lst = f"{OV}/segs.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in segs))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base])


# ---------- overlay art ----------
def hook_row_png(path):
    """GTA 6 art + '+' + Buzzy bee logo + '=' + money-mouth emoji, centred, above his hair line."""
    f = capstyle.font()                                   # "+" and "=" in the caption font (his earlier ask)
    g = Image.open(f"{ET}/na/gta2.webp").convert("RGBA")
    gh = 200
    g = g.resize((round(g.width * gh / g.height), gh), Image.LANCZOS)
    logo = Image.open(f"{ET}/na/buzzy_logo.png").convert("RGBA")
    logo = logo.crop(logo.split()[3].getbbox())
    lw = 200
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.NEAREST)   # pixel art stays crisp
    emo = Image.open(f"{A}/emoji.png").convert("RGBA").resize((130, 130), Image.LANCZOS)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    pw, ew = tmp.textlength("+", font=f), tmp.textlength("=", font=f)
    gap = 18
    items = [("img", g), ("txt", "+", pw), ("img", logo), ("txt", "=", ew), ("img", emo)]
    total = sum((it[1].width if it[0] == "img" else it[2]) for it in items) + gap * (len(items) - 1)
    cv = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
    cy = 130
    sh = Image.new("RGBA", cv.size, (0, 0, 0, 0))
    x = (W - total) / 2
    pos = []
    for it in items:
        if it[0] == "img":
            im = it[1]
            pos.append((im, round(x), cy - im.height // 2))
            x += im.width + gap
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


def card_png(src, path, width, same=None):
    """Scale a revenue card; `same`=(w, h) first pads it with its own background so all cards match in size."""
    im = Image.open(src).convert("RGB")
    if same:
        bg = tuple(int(v) for v in np.median(np.asarray(im)[:4].reshape(-1, 3), axis=0))
        cv = Image.new("RGB", same, bg)
        cv.paste(im.crop((0, 0, min(im.width, same[0]), min(im.height, same[1]))),
                 (0, (same[1] - min(im.height, same[1])) // 2))
        im = cv
    h = round(im.height * width / im.width)
    im.resize((width, h), Image.LANCZOS).save(path)
    return h


def main():
    out = sys.argv[1]
    words, audio, pieces, F, out_frame, ffa = plan()
    total = F / FPS
    f_demo, f_cta, f_cta2 = ffa(DEMO_START), ffa(CTA_START), ffa(CTA2_START)
    gains = section_gains(audio, pieces)
    print(f"{len(pieces)} pieces, {F} frames = {total:.2f}s | demo at {f_demo / FPS:.2f}s | CTA at {f_cta / FPS:.2f}s | gains {gains}", flush=True)
    base = f"{OV}/base.mkv"
    if not os.environ.get("SKIP_A"):
        stage_a(pieces, gains, base)

    layers = []  # (png, x, y, fa, fb)  frames [fa, fb)
    hook_row_png(f"{OV}/hook_row.png")
    layers.append((f"{OV}/hook_row.png", 0, 55, 0, f_demo))           # row y ~85-315, above his hair (y >= ~390)

    # revenue cards on "every day / every week / every month": same size, one column, each above the pen tip at
    # its phrase (the "month" tip is low, so that card stops above the captions); all go at the cut after "month"
    sizes = [Image.open(f"{ET}/cards/card{i}.png").size for i in (1, 2, 3)]
    same = (min(s[0] for s in sizes), max(s[1] for s in sizes))
    ch = 0
    for i in (1, 2, 3):
        ch = card_png(f"{ET}/cards/card{i}.png", f"{OV}/card{i}.png", CARD_W, same)
    y1 = TIP["day"][1] - CARD_GAP - ch
    y3 = min(TIP["month"][1] - CARD_GAP, CARD_MAX_BOTTOM) - ch
    ys = [y1, (y1 + y3) // 2, y3]
    month_i = next(i for i, w in enumerate(words) if w["w"].lower().startswith("month"))
    f_after_month = next(o0 for ks, ke, o0, n in pieces if ks > words[month_i]["e"])
    for k, wi in enumerate((0, 2, 4)):               # word indexes of the three "every"
        layers.append((f"{OV}/card{k + 1}.png", CARD_X, ys[k], out_frame(words[wi]["s"]), f_after_month))

    # permanent rule: the CTA clip "post two of these a day to start getting payouts like this" carries the
    # estimated-revenue card for the ENTIRE clip, centred at the top, 640 px wide, top y 110
    card_png(f"{ET}/cards/rev_cta.png", f"{OV}/rev_cta.png", 640)
    layers.append((f"{OV}/rev_cta.png", (W - 640) // 2, 110, f_cta, f_cta2))

    # captions (permanent style); close-up CTA clips use the lower baseline
    caps = capstyle.group_captions(words, display_tokens)
    for j, (text, a, b) in enumerate(caps):
        fa = 0 if j == 0 else out_frame(words[a]["s"])
        fb = out_frame(words[caps[j + 1][1]]["s"]) if j + 1 < len(caps) else F
        # a caption never hangs over a section cut
        for c in (f_demo, f_cta):
            if fa < c < fb:
                fb = c
        if fb <= fa:
            continue
        p = f"{OV}/cap_{j:03d}.png"
        capstyle.render(text, p)
        y = capstyle.OVERLAY_Y_CLOSEUP if fa >= f_cta else capstyle.OVERLAY_Y
        layers.append((p, 0, y, fa, fb))

    # ---------- pass B ----------
    cmd = ["ffmpeg", "-v", "error", "-stats", "-y", "-i", base]
    for l in layers:
        cmd += ["-i", l[0]]
    mus_i, ris_i = 1 + len(layers), 2 + len(layers)
    cmd += ["-i", f"{A}/music.mp3", "-i", f"{A}/riser_metallic.mp4"]
    parts, prev = [], "0:v"
    for k, (p, x, y, fa, fb) in enumerate(layers):
        parts.append(f"[{prev}][{1 + k}:v]overlay={x}:{y}:enable='between(n,{fa},{fb - 1})'[o{k}]")
        prev = f"o{k}"
    m_rms = bai_rms(f"{A}/music.mp3", bai.MUSIC_START, bai.MUSIC_START + total)
    r_rms = bai_rms(f"{A}/riser_metallic.mp4", 1.2, 3.0)
    m_gain = (bai.VOICE_RMS_TARGET - 14.0) - m_rms
    r_gain = (bai.VOICE_RMS_TARGET - 8.0) - r_rms
    t_cut = f_demo / FPS
    riser_start = max(0.0, t_cut - 3.0)                 # the riser stops dead 3.0 s into the file: on the cut
    parts.append(f"[{mus_i}:a]atrim=start={bai.MUSIC_START:.3f}:end={bai.MUSIC_START + total + 1:.2f},asetpts=PTS-STARTPTS,"
                 f"aformat=channel_layouts=stereo,aresample=48000,volume={m_gain:.2f}dB,afade=t=in:d=0.03,"
                 f"afade=t=out:st={total - 0.8:.2f}:d=0.8[mus]")
    parts.append(f"[{ris_i}:a]aformat=channel_layouts=stereo,aresample=48000,volume={r_gain:.2f}dB,"
                 f"atrim=0:3.0,adelay={int(riser_start * 1000)}|{int(riser_start * 1000)}[ris]")
    parts.append("[0:a]aresample=48000,aformat=channel_layouts=stereo[voice];"
                 "[voice][mus][ris]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.9:level=disabled[aout]")
    cmd += ["-filter_complex", ";".join(parts), "-map", f"[{prev}]", "-map", "[aout]", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    json.dump(dict(pieces=pieces, F=F, f_demo=f_demo, f_cta=f_cta, f_cta2=f_cta2,
                   layers=[(os.path.basename(l[0]),) + tuple(l[1:]) for l in layers]),
              open(f"{ET}/plan.json", "w"), indent=1)
    run(cmd)


def bai_rms(path, t0, t1):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", path, "-vn", "-ac", "1",
                          "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    return 20 * math.log10(float(np.sqrt((a ** 2).mean())) + 1e-9)


if __name__ == "__main__":
    main()
