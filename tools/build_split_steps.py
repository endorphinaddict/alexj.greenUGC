#!/usr/bin/env python3
"""Build a 'split-screen steps' video (format of Footage/Example Video/fixed.mp4) for a new campaign.

Usage: EDIT_WORKDIR=/path build_split_steps.py OUTFILE
EDIT_WORKDIR holds: fd/in/ns1.mp4 (screen recording), fd/in/ns2.mp4 (face-cam for the top half),
fd/in/ns3.mp4 (hook), assets/loudly_crying.png (😭), fonts/Montserrat-SemiBold.ttf.

Layout (1080x1920, black background), measured off the example:
  HOOK   : title (2 lines) above the face-cam, which fills x 0-1080, y 520-1560.
  STEPS  : face-cam on top (y 0-900), black label band (y 900-1140), screen recording below (y 1140-1920).
No music: room sound from the face-cam (clicks, typing), his own sounds in the hook.
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

S = os.environ.get("EDIT_WORKDIR", os.path.abspath("work"))
IN, A, OV = f"{S}/fd/in", f"{S}/assets", f"{S}/overlays_fd"
FONT = f"{S}/fonts/Montserrat-SemiBold.ttf"
os.makedirs(OV, exist_ok=True)
W, H, FPS = 1080, 1920, 30

TITLE = ["Making a passive income business", "in less than 40 seconds"]   # 😭 after line 2, as in the example

# Hook cuts in ns3 (his direction): sitting down -> cracking open the drink -> countdown, ending on the
# finger snap at the camera (snap transient at 8.94s).
HOOK = [(1.00, 2.25), (2.45, 3.60), (5.60, 9.03)]
HOOK_CROP = (400, 0, 1121, 1080)        # x, y, w, h in the 1920x1080 hook clip -> scaled to 1080x1040

# Steps: (label lines, screen-recording start, end, speed, crop x, y, w) ; crop h = w * 780/1080
STEPS = [
    (["Step 1: go to chatgpt"],                                12.6, 16.6, 1.25, 310, 60, 1300),
    (["Step 2: search unsaturated", "businesses in your area"], 17.2, 28.0, 3.0, 485, 40, 1350),
    (["Step 3: pick one you like"],                            32.5, 38.5, 1.5, 485, 40, 1350),
    (["Step 4: go to foundable.com"],                          93.3, 95.2, 1.0, 310, 70, 1300),   # clean landing on the home page
    (["Step 5: paste your prompt"],                            49.6, 51.8, 1.0, 310, 70, 1300),   # paste at 49.9s, prompt shown until the page leaves at 51.85s
    (["Step 6: let it cook"],                                  61.8, 88.0, 7.0, 605, 20, 1315),   # crop keeps "$0.00" out
    (["Step 7: passive income achieved"],                     107.5, 118.5, 2.0, 650, 75, 1270),
]
TOP_CAM_START = 26.0                     # continuous face-cam take for the top half (ns2)
TOP_CROP = (312, 0, 1296, 1080)          # -> 1080x900


def fit_font(lines, max_w, start):
    size = start
    while size > 30:
        f = ImageFont.truetype(FONT, size)
        d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
        if all(d.textlength(l, font=f) <= max_w for l in lines):
            return f, size
        size -= 2
    return ImageFont.truetype(FONT, size), size


def title_png(path):
    f, size = fit_font([TITLE[0], TITLE[1] + "  XX"], 1010, 60)
    img = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ys = [62, 132]
    d.text((W // 2, ys[0]), TITLE[0], font=f, fill="white", anchor="mm")
    emo = Image.open(f"{A}/loudly_crying.png").convert("RGBA").resize((size, size), Image.LANCZOS)
    tw = d.textlength(TITLE[1], font=f)
    x = (W - (tw + 10 + size)) / 2
    d.text((x, ys[1]), TITLE[1], font=f, fill="white", anchor="lm")
    img.alpha_composite(emo, (int(x + tw + 10), int(ys[1] - size / 2)))
    img.save(path)


def label_png(lines, path):
    f, size = fit_font(lines, 1010, 68 if len(lines) == 1 else 62)
    img = Image.new("RGBA", (W, 240), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    gap = size + 14
    y0 = 120 - (len(lines) - 1) * gap / 2
    for k, l in enumerate(lines):
        d.text((W // 2, y0 + k * gap), l, font=f, fill="white", anchor="mm")
    img.save(path)


def main():
    out = sys.argv[1]
    title_png(f"{OV}/title.png")
    hook_frames = [round((b - a) * FPS) for a, b in HOOK]
    step_frames = [round((e - s) / sp * FPS) for _, s, e, sp, *_ in STEPS]
    HF, SF = sum(hook_frames), sum(step_frames)
    total = (HF + SF) / FPS

    cmd = ["ffmpeg", "-v", "error", "-stats", "-y",
           "-i", f"{IN}/ns3.mp4", "-i", f"{IN}/ns1.mp4", "-i", f"{IN}/ns2.mp4", "-i", f"{OV}/title.png"]
    for k, st in enumerate(STEPS):
        label_png(st[0], f"{OV}/label_{k}.png")
        cmd += ["-i", f"{OV}/label_{k}.png"]
    p = []
    # ---- hook: three cuts, face-cam in the middle band, title above
    hx, hy, hw, hh = HOOK_CROP
    for i, ((a, b), n) in enumerate(zip(HOOK, hook_frames)):
        p.append(f"[0:v:0]trim=start={a:.4f}:end={b + 0.1:.4f},setpts=PTS-STARTPTS,fps={FPS},trim=end_frame={n},"
                 f"crop={hw}:{hh}:{hx}:{hy},scale=1080:1040:flags=lanczos,setsar=1,format=yuv420p[hv{i}]")
        p.append(f"[0:a]atrim=start={a:.4f}:end={a + n / FPS:.4f},asetpts=PTS-STARTPTS,aresample=48000,"
                 f"aformat=channel_layouts=stereo,afade=t=in:d=0.01,afade=t=out:st={n / FPS - 0.01:.4f}:d=0.01[ha{i}]")
    p.append("".join(f"[hv{i}]" for i in range(len(HOOK))) + f"concat=n={len(HOOK)}:v=1:a=0[hookcam]")
    p.append("".join(f"[ha{i}]" for i in range(len(HOOK))) + f"concat=n={len(HOOK)}:v=0:a=1[hooka]")
    p.append(f"color=c=black:s={W}x{H}:r={FPS}:d={HF / FPS:.4f},format=yuv420p[hbg]")
    p.append("[hbg][hookcam]overlay=0:520:shortest=1[hk1]")
    p.append("[hk1][3:v]overlay=0:322[hookv]")        # title lines centred at y ~384 and ~454, above the video
    # ---- steps: screen recording (bottom), face-cam (top), label (middle)
    for i, ((lines, s, e, sp, cx, cy, cw), n) in enumerate(zip(STEPS, step_frames)):
        ch = round(cw * 780 / 1080)
        p.append(f"[1:v:0]trim=start={s:.4f}:end={e + 0.5:.4f},setpts=(PTS-STARTPTS)/{sp},fps={FPS},trim=end_frame={n},"
                 f"crop={cw}:{ch}:{cx}:{cy},scale=1080:780:flags=lanczos,setsar=1,format=yuv420p[sv{i}]")
    p.append("".join(f"[sv{i}]" for i in range(len(STEPS))) + f"concat=n={len(STEPS)}:v=1:a=0[screen]")
    tx, ty, tw, th = TOP_CROP
    p.append(f"[2:v:0]trim=start={TOP_CAM_START:.4f}:end={TOP_CAM_START + SF / FPS + 0.5:.4f},setpts=PTS-STARTPTS,"
             f"fps={FPS},trim=end_frame={SF},crop={tw}:{th}:{tx}:{ty},scale=1080:900:flags=lanczos,setsar=1,format=yuv420p[top]")
    p.append(f"[2:a]atrim=start={TOP_CAM_START:.4f}:end={TOP_CAM_START + SF / FPS:.4f},asetpts=PTS-STARTPTS,aresample=48000,"
             f"aformat=channel_layouts=stereo,volume=6dB[stepa]")
    p.append(f"color=c=black:s={W}x{H}:r={FPS}:d={SF / FPS:.4f},format=yuv420p[sbg]")
    p.append("[sbg][top]overlay=0:0:shortest=1[s1]")
    p.append("[s1][screen]overlay=0:1140:shortest=1[s2]")
    prev, f0 = "s2", 0
    for i, n in enumerate(step_frames):
        p.append(f"[{prev}][{4 + i}:v]overlay=0:900:enable='between(n,{f0},{f0 + n - 1})'[l{i}]")
        prev, f0 = f"l{i}", f0 + n
    p.append(f"[{prev}]null[stepsv]")
    p.append("[hookv][hooka][stepsv][stepa]concat=n=2:v=1:a=1[v][a0]")
    p.append("[a0]alimiter=limit=0.7:level=disabled[a]")   # can crack / snap transients overshoot after AAC; -3 dB keeps true peak under 0
    cmd += ["-filter_complex", ";".join(p), "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    print(f"hook {HF} frames ({HF / FPS:.2f}s) + steps {SF} frames ({SF / FPS:.2f}s) = {total:.2f}s; "
          f"step starts: " + ", ".join(f"{(HF + sum(step_frames[:k])) / FPS:.2f}" for k in range(len(STEPS))), flush=True)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
