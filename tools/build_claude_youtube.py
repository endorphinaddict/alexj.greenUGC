#!/usr/bin/env python3
"""Build the 'Claude YouTube' no-talking video (12.3s, music only), copying the Notion example 1:1.

Usage: EDIT_WORKDIR=/path build_claude_youtube.py OUTFILE
EDIT_WORKDIR holds: cyt/ (the nine DJI clips), assets/ (claude_shorts_hook.png, emoji.png [money-mouth],
fire.png, moneybag.png, song12.mp3) and fonts/Montserrat-SemiBold.ttf.

Timeline and positions are measured off the reference (see CLAUDE.md).
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = os.environ.get("EDIT_WORKDIR", os.path.abspath("work"))
CLIPS, A, OV = f"{S}/cyt", f"{S}/assets", f"{S}/overlays_cyt"
FONT = f"{S}/fonts/Montserrat-SemiBold.ttf"
os.makedirs(OV, exist_ok=True)
W, H, FPS = 1080, 1920, 30

# (clip id, start second inside the clip, frames at 30fps, label lines, label centre y of the first line)
# Frame counts are the reference's cut points: 0, 2.333, 3.367, 4.80, 6.033, 7.433, 9.10, 10.267, 11.467, 12.30
SEGMENTS = [
    ("0427", 0.60, 70, None, None),                                   # hook: hands to head, shocked
    ("0430", 0.40, 31, ["Go to Claude"], 610),
    ("0434", 0.10, 43, ["Copy this prompt"], 612),
    ("0435", 0.50, 37, ["Copy your favorite script"], 612),
    ("0440", 0.50, 42, ["Go to openart.ai/direct"], 612),
    ("0443", 1.57, 50, ["Go to Quick Start", "> Explainer"], 727),    # pointing at Explainer at the end
    ("0444", 0.30, 35, ["Paste script"], 606),
    ("0445", 3.60, 36, ["RESULTS"], 550),                              # + fire emoji, over the generated video
    ("0446", 0.50, 25, ["post everyday and", "get payouts like these"], 477),  # + money bag emoji
]
LINE_GAP = 76
HOOK_TITLE_Y = 470        # centre of the title line; the hook graphic sits above it
HOOK_GRAPHIC = (189, 150, 702)  # x, y, width (reference: x ~178-880, y ~162-437)


def find_clip(cid):
    return next(f"{CLIPS}/{f}" for f in sorted(os.listdir(CLIPS)) if f"_{cid}_" in f)


def text_block(lines, emoji=None, size=60, width=W, pad=40):
    """White Montserrat SemiBold, thin dark outline + soft shadow (CapCut 'Classic' look)."""
    f = ImageFont.truetype(FONT, size)
    h = LINE_GAP * len(lines) + pad * 2
    shadow = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    img = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    sd, d = ImageDraw.Draw(shadow), ImageDraw.Draw(img)
    for k, ln in enumerate(lines):
        cy = pad + LINE_GAP / 2 + k * LINE_GAP
        tw = d.textlength(ln, font=f)
        extra = 0
        if emoji and k == len(lines) - 1:
            extra = size + 12
        x = width / 2 - (tw + extra) / 2
        sd.text((x, cy + 3), ln, font=f, fill=(0, 0, 0, 200), stroke_width=4, stroke_fill=(0, 0, 0, 200), anchor="lm")
        d.text((x, cy), ln, font=f, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(20, 20, 20, 255), anchor="lm")
        if emoji and k == len(lines) - 1:
            e = Image.open(emoji).convert("RGBA").resize((size + 4, size + 4), Image.LANCZOS)
            img.alpha_composite(e, (int(x + tw + 12), int(cy - (size + 4) / 2)))
    out = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    out.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(4)))
    out.alpha_composite(img)
    return out


def make_overlays():
    items = []  # (png, x, y, frame_a, frame_b)
    # hook graphic + title (frames 0..69), kept above his hair line
    g = Image.open(f"{A}/claude_shorts_hook.png").convert("RGBA")
    g = g.crop((338, 124, 1799, 602))  # the two logo tiles + plus; the PNG has faint stray pixels beyond this
    gx, gy, gw = HOOK_GRAPHIC
    g = g.resize((gw, round(g.height * gw / g.width)), Image.LANCZOS)
    g.save(f"{OV}/hook_graphic.png")
    items.append((f"{OV}/hook_graphic.png", gx, gy, 0, SEGMENTS[0][2]))
    # title "= $453/day 🤑"
    title = text_block(["= $453/day"], emoji=f"{A}/emoji.png", size=72)
    title.save(f"{OV}/hook_title.png")
    items.append((f"{OV}/hook_title.png", 0, HOOK_TITLE_Y - title.height // 2, 0, SEGMENTS[0][2]))
    # step labels
    f0 = SEGMENTS[0][2]
    for cid, _, n, lines, cy in SEGMENTS[1:]:
        emoji = {"0445": f"{A}/fire.png", "0446": f"{A}/moneybag.png"}.get(cid)
        blk = text_block(lines, emoji=emoji)
        p = f"{OV}/label_{cid}.png"
        blk.save(p)
        y = round(cy - (LINE_GAP / 2 + 40))
        items.append((p, 0, y, f0, f0 + n))
        f0 += n
    return items, f0


def main():
    out = sys.argv[1]
    items, total_frames = make_overlays()
    total = total_frames / FPS
    cmd = ["ffmpeg", "-v", "error", "-stats", "-y"]
    for cid, *_ in SEGMENTS:
        cmd += ["-i", find_clip(cid)]
    for it in items:
        cmd += ["-i", it[0]]
    cmd += ["-i", f"{A}/song12.mp3"]
    parts, lab = [], []
    for i, (cid, st, n, *_r) in enumerate(SEGMENTS):
        parts.append(f"[{i}:v]trim=start={st:.4f}:end={st + (n + 2) / FPS:.4f},setpts=PTS-STARTPTS,fps={FPS},"
                     f"trim=end_frame={n},scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p[v{i}]")
        lab.append(f"[v{i}]")
    parts.append("".join(lab) + f"concat=n={len(SEGMENTS)}:v=1:a=0[base]")
    prev, base_idx = "base", len(SEGMENTS)
    for k, (p, x, y, a, b) in enumerate(items):
        nxt = f"o{k}"
        # frame-accurate: enable on the frame counter so nothing lingers past a cut
        parts.append(f"[{prev}][{base_idx + k}:v]overlay={x}:{y}:enable='between(n,{a},{b - 1})'[{nxt}]")
        prev = nxt
    song_i = base_idx + len(items)
    parts.append(f"[{song_i}:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo,"
                 f"aresample=48000,afade=t=out:st={total - 0.4:.3f}:d=0.4,alimiter=limit=0.97[aout]")
    cmd += ["-filter_complex", ";".join(parts), "-map", f"[{prev}]", "-map", "[aout]", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    print(f"{total_frames} frames = {total:.3f}s", flush=True)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
