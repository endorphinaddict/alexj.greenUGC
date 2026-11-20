#!/usr/bin/env python3
"""Split-screen steps, "GTA 6 pays my rent" version (Nov 19 footage), copied 1:1 from his example
`Footage/Example Video/I bet so many people are gonna print with GTA 6 and Openart...mp4` (720x1280, 44.5 s).

His direction: use his footage (hook 0695, face-cam 0696, ending 0697) in the example's layout, take the SCREEN RECORDING
from the example itself (he had none), and match the sound of his typing to what is typed on screen.

Layout, measured off the example (x1.5 -> 1080x1920, black background):
  HOOK   0-6.4 s    title (2 lines, y ~425/482) above the face-cam (y 528-1515): sip, then the finger countdown "three, two, one"
  SPLIT  6.4-42.3 s face-cam y 0-790 with a timer box (x 345-735, y 630-790, thin "00:03.51"), label band y 790-1058,
                    the example's screen recording y 1058-1920 (cropped from the example's own bottom 575 px)
  CTA    42.3-44.5  `Comment "Free" for the Guide ✅✅` (y 352/438) above the zoomed face-cam (y 520-1560)
Labels / change times (example seconds): 6.40 "GTA 6 comes out Today!!" | 9.67 Step 1 | 15.67 Step 2 | 19.43 Step 2 (views) |
22.33 Step 3 | 25.73 Step 3 (scroll) | 30.37 Step 4 | 34.87 Step 4 (wait) | 40.30 Step 4 (check) | 42.30 CTA.
Timer = example time - 6.49 s.

TYPING SOUND (his request): his face-cam audio has key-click bursts at his own times. The bed (his room sound, his reactions
"what / damn / okay", the sip) is taken from one continuous window of 0696 with those bursts ducked, and each burst
is re-placed so that it starts and ends exactly when the typing on the example's screen starts and ends (TYPING below).

Usage: EDIT_WORKDIR=/path build_split_gta6.py OUTFILE
EDIT_WORKDIR holds g6/in/0695.mp4 0696.mp4 0697.mp4, g6/ex/example.mp4, assets/loudly_crying.png + check.png, fonts/Montserrat-SemiBold.ttf + Lato-300.ttf.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

S = os.environ.get("EDIT_WORKDIR", os.path.abspath("work"))
G, A, F = f"{S}/g6", f"{S}/assets", f"{S}/fonts"
OV = f"{G}/ov"
os.makedirs(OV, exist_ok=True)
W, H, FPS = 1080, 1920, 30
SR = 48000
TARGET_LUFS = -18.0               # every section is brought to this integrated loudness (his request: no level jumps)

# 0695 hook, his direction: MORE CUTS at the start to keep attention: sitting down into the chair -> popping the cup open (pop at 4.2 s)
# -> drinking -> counting down "three, two, one" (ends with the finger at the camera). (start second, seconds); total 6.4 s like the example.
HOOK_CUTS = [(0.75, 0.9), (3.75, 1.0), (5.5, 1.4), (8.6, 3.1)]
HOOK_CROP = (100, 0, 1182, 1080)  # -> 1080x987
EX_SPLIT = (6.4, 42.3)            # example seconds of the split screen
TOP_START = 3.93                  # 0696 window start: his "what?" lands on the example's first reaction, his sip near its sip
TOP_CROP = (0, 0, 1476, 1080)     # -> 1080x790
CTA_SRC = (0.0, 2.17)             # 0697: "Comment down below if you want my free guide" (word ends 1.92) + 0.25 s tail
CTA_CROP = (300, 0, 2243, 2160)   # -> 1080x1040
TITLE = ["Using GTA 6 to pay my next months", "rent in under 40 seconds"]
CTA_TEXT = ["Comment “Free” for the", "Guide"]

LABELS = [  # (example start second, lines)
    (6.40, ["GTA 6 comes out Today!!"]),
    (9.67, ["Step 1: Check how much", "YouTube pays"]),
    (15.67, ["Step 2: Go to YouTube &", "search Rain Sounds"]),
    (19.43, ["Step 2: Look at the views!"]),
    (22.33, ["Step 3: Now go to", "openart.ai/direct"]),
    (25.73, ["Step 3: Scroll down to Quick", "starts & press Short film"]),
    (30.37, ["Step 4: Enter the prompt you", "want & press direct"]),
    (34.87, ["Step 4: Wait for the video to", "generate"]),
    (40.30, ["Step 4: Check if it's okay &", "then post it on YouTube"]),
]

# typing on the example's screen (example seconds) <- his click bursts in 0696 (his seconds)
TYPING = [
    ((9.70, 13.30), (8.00, 11.60)),    # google: "How much does youtube pay for a million views"
    ((19.20, 20.40), (16.30, 17.50)),  # youtube search: "Rain sounds"
    ((22.00, 22.80), (20.87, 21.67)),  # url bar: openart.ai/direct
    ((30.50, 32.60), (29.12, 31.22)),  # film prompt: "make me a gta 6 rain sound video"
    ((33.90, 34.60), (32.00, 32.70)),  # visual style: "GTA 6"
]
# his own click bursts in 0696 (his seconds): ducked in the bed, because every burst is re-placed above
BURSTS = [(3.78, 7.30), (7.60, 12.72), (14.20, 14.95), (16.10, 18.60), (20.75, 25.05), (27.10, 28.50), (29.00, 33.85), (34.20, 35.50)]


def run(cmd):
    subprocess.run(cmd, check=True)


def fit(text_lines, max_w, start, path):
    size = start
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    while size > 30:
        f = ImageFont.truetype(path, size)
        if all(d.textlength(t, font=f) <= max_w for t in text_lines):
            return f, size
        size -= 2
    return ImageFont.truetype(path, size), size


def title_png(lines, emoji_png, n_emoji, ys, size_w, path, spacing_hint=None):
    f, size = fit([lines[0]], size_w, 80, f"{F}/Montserrat-SemiBold.ttf")
    img = Image.new("RGBA", (W, 230), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((W // 2, ys[0]), lines[0], font=f, fill="white", anchor="mm")
    emo = Image.open(emoji_png).convert("RGBA").resize((size, size), Image.LANCZOS)
    tw = d.textlength(lines[1], font=f)
    total = tw + 8 + n_emoji * (size + 4)
    x = (W - total) / 2
    d.text((x, ys[1]), lines[1], font=f, fill="white", anchor="lm")
    for k in range(n_emoji):
        img.alpha_composite(emo, (int(x + tw + 8 + k * (size + 4)), int(ys[1] - size / 2)))
    img.save(path)


def label_png(lines, path):
    f, size = fit(lines, 1000, 64, f"{F}/Montserrat-SemiBold.ttf")
    img = Image.new("RGBA", (W, 268), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    gap = 82
    y0 = 134 + 6 - (len(lines) - 1) * gap / 2
    for k, l in enumerate(lines):
        d.text((W // 2, y0 + k * gap), l, font=f, fill="white", anchor="mm")
    img.save(path)


def read_audio(path, t0, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0:.4f}", "-t", f"{dur:.4f}", "-i", path, "-vn", "-ac", "2", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32).reshape(-1, 2) / 32768
    need = int(round(dur * SR))
    if len(a) < need:
        a = np.concatenate([a, np.zeros((need - len(a), 2), np.float32)])
    return a[:need]


def write_wav(a, path):
    pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", path], input=pcm.tobytes(), check=True)


def fade(a, ms=8):
    n = int(SR * ms / 1000)
    a = a.copy()
    a[:n] *= np.linspace(0, 1, n)[:, None]
    a[-n:] *= np.linspace(1, 0, n)[:, None]
    return a


def split_audio(n_frames, path):
    dur = n_frames / FPS
    bed = read_audio(f"{G}/in/0696.mp4", TOP_START, dur) * 2.4          # +6 dB room sound, as in the earlier split-screen builds
    env = np.ones(len(bed), np.float32)
    duck = 10 ** (-32 / 20)
    for b0, b1 in BURSTS:
        i0, i1 = int((b0 - TOP_START) * SR), int((b1 - TOP_START) * SR)
        if i1 <= 0 or i0 >= len(env):
            continue
        i0, i1 = max(0, i0), min(len(env), i1)
        env[i0:i1] = np.minimum(env[i0:i1], duck)
    k = np.ones(int(0.03 * SR)) / int(0.03 * SR)                           # 30 ms ramps
    env = np.convolve(env, k, mode="same").astype(np.float32)
    # band-split: key clicks are mostly above ~1 kHz, his room tone is low, so duck the highs hard and the lows only a little.
    # (An earlier version ducked everything and filled the gaps with synthetic noise, which sounded scratchy once the level was evened out.)
    n = 255
    t = np.arange(n) - n // 2
    lp = np.sinc(2 * 1000 / SR * t) * np.hanning(n)
    lp /= lp.sum()
    low = np.stack([np.convolve(bed[:, c], lp, mode="same") for c in range(2)], axis=1)
    high = bed - low
    low_env = np.maximum(env, 10 ** (-6 / 20))
    bed = low * low_env[:, None] + high * env[:, None]
    for (e0, e1), (h0, h1) in TYPING:
        seg = read_audio(f"{G}/in/0696.mp4", h0, h1 - h0) * 1.2
        want = int(round((e1 - e0) * SR))
        if abs(len(seg) - want) > 1:                                        # same length by construction; guard anyway
            seg = seg[:want]
        i0 = int(round((e0 - EX_SPLIT[0]) * SR))
        seg = fade(seg)
        bed[i0:i0 + len(seg)] += seg[: len(bed) - i0]
    write_wav(bed, path)


def main():
    out = sys.argv[1]
    hook_n = [round(d * FPS) for _, d in HOOK_CUTS]
    n_hook = sum(hook_n)
    n_split = round((EX_SPLIT[1] - EX_SPLIT[0]) * FPS)
    n_cta = round((CTA_SRC[1] - CTA_SRC[0]) * FPS)
    total = (n_hook + n_split + n_cta) / FPS
    print(f"hook {n_hook} + split {n_split} + cta {n_cta} frames = {total:.2f}s", flush=True)

    # ---- hook segment
    title_png(TITLE, f"{A}/loudly_crying.png", 2, (80, 137), 893, f"{OV}/title.png")
    hx, hy, hw, hh = HOOK_CROP
    k = len(HOOK_CUTS)
    g = []
    for i, ((a, _d), n) in enumerate(zip(HOOK_CUTS, hook_n)):
        g.append(f"[0:v:0]trim=start={a:.4f}:end={a + n / FPS + 0.1:.4f},setpts=PTS-STARTPTS,fps={FPS},trim=end_frame={n},"
                 f"crop={hw}:{hh}:{hx}:{hy},scale=1080:987:flags=lanczos,setsar=1,format=yuv420p[hv{i}]")
        g.append(f"[0:a]atrim=start={a:.4f}:end={a + n / FPS:.4f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
                 f"volume=6dB,afade=t=in:d=0.008,afade=t=out:st={n / FPS - 0.008:.4f}:d=0.008[ha{i}]")
    g.append("".join(f"[hv{i}]" for i in range(k)) + f"concat=n={k}:v=1:a=0[cam]")
    g.append("".join(f"[ha{i}]" for i in range(k)) + f"concat=n={k}:v=0:a=1[a]")
    g.append(f"color=c=black:s={W}x{H}:r={FPS}:d={n_hook / FPS:.4f},format=yuv420p[bg];[bg][cam]overlay=0:528:shortest=1[c1];[c1][1:v]overlay=0:345,format=yuv420p[v]")
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{G}/in/0695.mp4", "-i", f"{OV}/title.png", "-filter_complex", ";".join(g),
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "10", "-c:a", "pcm_s16le", f"{OV}/hook.mkv"])

    # ---- ending (4K source pre-rendered to 1080x1920)
    title_png(CTA_TEXT, f"{A}/check.png", 2, (80, 166), 897, f"{OV}/cta_title.png")
    cx, cy, cw, ch = CTA_CROP
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{CTA_SRC[0]:.4f}", "-i", f"{G}/in/0697.mp4", "-i", f"{OV}/cta_title.png", "-filter_complex",
         f"[0:v:0]fps={FPS},trim=end_frame={n_cta},crop={cw}:{ch}:{cx}:{cy},scale=1080:1040:flags=lanczos,setsar=1,format=yuv420p[cam];"
         f"color=c=black:s={W}x{H}:r={FPS}:d={n_cta / FPS:.4f},format=yuv420p[bg];[bg][cam]overlay=0:520:shortest=1[c1];[c1][1:v]overlay=0:272,format=yuv420p[v];"
         f"[0:a]atrim=0:{n_cta / FPS:.4f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume=9dB,"
         f"afade=t=in:d=0.01,afade=t=out:st={n_cta / FPS - 0.02:.4f}:d=0.02[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "10", "-c:a", "pcm_s16le", f"{OV}/cta.mkv"])

    # ---- split screen
    split_audio(n_split, f"{OV}/split_audio.wav")
    tx, ty, tw, th = TOP_CROP
    cmd = ["ffmpeg", "-v", "error", "-stats", "-y", "-ss", f"{TOP_START:.4f}", "-i", f"{G}/in/0696.mp4",
           "-ss", f"{EX_SPLIT[0]:.4f}", "-i", f"{G}/ex/example.mp4", "-i", f"{OV}/split_audio.wav"]
    for k, (_, lines) in enumerate(LABELS):
        label_png(lines, f"{OV}/label_{k}.png")
        cmd += ["-i", f"{OV}/label_{k}.png"]
    ft = ImageFont.truetype(f"{F}/Lato-300.ttf", 84)
    tw0 = ImageDraw.Draw(Image.new("RGBA", (10, 10))).textlength("00:00.00", font=ft)
    open(f"{OV}/timer.txt", "w").write("%{eif:floor(max(t-0.09,0)/60):d:2}:%{eif:mod(floor(max(t-0.09,0)),60):d:2}.%{eif:floor(mod(max(t-0.09,0),1)*100):d:2}")
    p = [f"[0:v:0]fps={FPS},trim=end_frame={n_split},crop={tw}:{th}:{tx}:{ty},scale=1080:790:flags=lanczos,setsar=1,format=yuv420p[top]",
         f"[1:v:0]fps={FPS},trim=end_frame={n_split},crop=720:575:0:705,scale=1080:862:flags=lanczos,setsar=1,format=yuv420p[scr]",
         f"color=c=black:s={W}x{H}:r={FPS}:d={n_split / FPS:.4f},format=yuv420p[bg]",
         "[bg][top]overlay=0:0:shortest=1[a1]", "[a1][scr]overlay=0:1058:shortest=1[a2]",
         f"[a2]drawbox=x=345:y=630:w=390:h=160:color=black:t=fill,drawtext=fontfile={F}/Lato-300.ttf:textfile={OV}/timer.txt:expansion=normal:"
         f"fontsize=84:fontcolor=white:x={540 - tw0 / 2:.1f}:y=670[a3]"]
    prev = "a3"
    starts = [round((t - EX_SPLIT[0]) * FPS) for t, _ in LABELS] + [n_split]
    for k in range(len(LABELS)):
        p.append(f"[{prev}][{3 + k}:v]overlay=0:790:enable='between(n,{starts[k]},{starts[k + 1] - 1})'[l{k}]")
        prev = f"l{k}"
    p.append(f"[{prev}]format=yuv420p[v]")
    p.append("[2:a]asetpts=PTS-STARTPTS[a]")
    cmd += ["-filter_complex", ";".join(p), "-map", "[v]", "-map", "[a]", "-t", f"{n_split / FPS:.4f}", "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "10", "-c:a", "pcm_s16le", f"{OV}/split.mkv"]
    run(cmd)

    # ---- join. His request: audio levels consistent all the way through. Each section is first brought to the same
    # integrated loudness (they were -18 / -26 / -11 LUFS), then a light compressor evens out the key clicks and voice peaks.
    gains = []
    for name in ("hook", "split", "cta"):
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{OV}/{name}.mkv", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
        lufs = float(r.split("Integrated loudness:")[-1].split("I:")[1].split("LUFS")[0])
        gains.append(max(-14.0, min(14.0, TARGET_LUFS - lufs - (3.0 if name == "cta" else 0.0))))   # the ending line is a close shout over room tone: 3 dB lower sits level with the rest
        print(f"{name}: {lufs:.1f} LUFS -> gain {gains[-1]:+.1f} dB", flush=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{OV}/hook.mkv", "-i", f"{OV}/split.mkv", "-i", f"{OV}/cta.mkv", "-filter_complex",
         "[0:a]volume=%.2fdB[a0];[1:a]volume=%.2fdB[a1];[2:a]volume=%.2fdB[a2];" % tuple(gains) +
         "[0:v][a0][1:v][a1][2:v][a2]concat=n=3:v=1:a=1[v][a3];"
         "[a3]highpass=f=80,afftdn=nr=10:nf=-48,acompressor=threshold=0.1:ratio=2.5:attack=10:release=300:makeup=2,loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.9:level=disabled[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])

if __name__ == "__main__":
    main()
