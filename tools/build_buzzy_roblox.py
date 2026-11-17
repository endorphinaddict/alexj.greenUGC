#!/usr/bin/env python3
"""Buzzy Roblox video: reuse the hook and CTA of his finished edit `Footage/Example Video/1117 (2).mp4`,
replace its OpenArt demo with the new Buzzy demo clips, and swap "YT Shorts" in the hook row for the Buzzy logo.

Usage: EDIT_WORKDIR=/path build_buzzy_roblox.py OUTFILE
EDIT_WORKDIR/bz holds: ex/ex1117.mp4, new/*.MP4 (demo clips), new.json (word timings), audio1.mp3 (the music,
same track as background_music.mp3), riser_notion.mp3, buzzy_logo.png; fonts in EDIT_WORKDIR/fonts.
"""
import glob, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ai_influencer as bai   # tight_keeps, phrase_captions, cds

S = os.environ.get("EDIT_WORKDIR", os.path.abspath("work"))
B = f"{S}/bz"
OV = f"{B}/ov"
os.makedirs(OV, exist_ok=True)
W, H, FPS = 1080, 1920, 30
EX = f"{B}/ex/ex1117.mp4"

HOOK_END = 11.0        # example: cut from the hook to the demo ("...$5,000 course." ends 10.88)
CTA_START = 26.267     # example: cut to the CTA ("So make sure to save this video..." starts 26.30)
EX_END = 30.07
MUSIC_OFFSET = 4.333   # music time = example time + 4.333 (measured by cross-correlation)
MUSIC_GAIN_DB = -10.2  # music level in the example
RISER_START = 8.90     # Notion riser.mp3 starts at 8.90 in the example and peaks at the hook->demo cut

DEMO = ["0531", "0532", "0535", "0540"]   # chat -> copy -> buzzy.now video generator -> result
# His change: the example's "make sure to save this video..." ending is removed; two new close-up clips replace it.
END = ["0543", "0545"]   # 0543 "Start posting these twice a day and you'll start getting payouts like this" (points up)
                         # 0545 "And if you want the prompt that I use, just comment AI and I'll send it to you."
END_CAP_Y = 1580         # close-ups: chin/mic sit around y 1250-1450, so captions go below (saved close-up rule)
TAIL_AFTER_LAST_WORD = 0.25   # never clip the last word of the video
REV_CARD = "rev_nov.png"      # "Estimated revenue $3,287.17" (the same figure already in the hook)

# Hook row: "YT Shorts" text is burned in at x 335-705, y 222-318; erase it and put the Buzzy logo there.
TEXT_BOX = (330, 218, 712, 322)
LOGO_SIZE, LOGO_CX, LOGO_CY = 300, 528, 250   # logo width (300x190); clears his hair (top ~y 355); sits between the + (x~325) and = (x~735)

CAP_Y = 1295           # example's caption centre on the demo footage
FONT_BOLD = f"{S}/fonts/Montserrat-Bold.ttf"


def run(cmd):
    subprocess.run(cmd, check=True)


def text_removed_region():
    """Erase the burned-in "YT Shorts" frame by frame: inpaint the letters (and their outline) from whatever is
    really behind them in that frame - the wall, or the Roblox clip pop-up when it is on screen. A static wall
    patch painted the wall over the pop-up's corner. Writes the cleaned region as raw video + the logo PNG."""
    import cv2
    x0, y0, x1, y1 = TEXT_BOX
    w, h = x1 - x0, y1 - y0
    raw = subprocess.run(["ffmpeg", "-v", "error", "-t", f"{HOOK_END}", "-i", EX, "-vf", f"crop={w}:{h}:{x0}:{y0}",
                          "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, dtype=np.uint8).reshape(-1, h, w, 3)
    med = np.median(fr[::10], axis=0)
    lum = med.mean(axis=2)
    mask = ((lum > 175) | (lum < 75)).astype(np.uint8) * 255        # the white letters and their black outline
    mask = cv2.dilate(mask, np.ones((7, 7), np.uint8))
    soft = cv2.GaussianBlur(mask.astype(np.float32) / 255, (0, 0), 1.5)[..., None]
    out = np.empty_like(fr)
    for k, f in enumerate(fr):
        bgr = cv2.cvtColor(f, cv2.COLOR_RGB2BGR)
        filled = cv2.inpaint(bgr, mask, 9, cv2.INPAINT_TELEA)
        filled = cv2.GaussianBlur(filled, (0, 0), 2.0)
        filled = cv2.cvtColor(filled, cv2.COLOR_BGR2RGB).astype(np.float32)
        out[k] = (f * (1 - soft) + filled * soft).astype(np.uint8)
    out.tofile(f"{OV}/text_removed.rgb")
    logo = Image.open(f"{B}/buzzy_logo.png").convert("RGBA")
    logo = logo.crop(logo.split()[3].getbbox())            # the PNG has wide transparent padding around the bug
    lw = LOGO_SIZE
    lh = round(logo.height * lw / logo.width)
    logo = logo.resize((lw, lh), Image.NEAREST)           # pixel art: keep the pixels crisp
    lx, ly = LOGO_CX - lw // 2, LOGO_CY - lh // 2
    canvas = Image.new("RGBA", (W, 400), (0, 0, 0, 0))
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (lx, ly + 5), logo.split()[3].point(lambda v: int(v * 0.55)))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    canvas.alpha_composite(logo, (lx, ly))
    canvas.save(f"{OV}/buzzy_logo_row.png")
    return w, h, len(fr)


def caption_png(text, path):
    """Match the example's burned-in captions: bold white, thick black outline, one line."""
    f = ImageFont.truetype(FONT_BOLD, 66)
    img = Image.new("RGBA", (W, 160), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((W // 2, 80), text, font=f, fill="white", stroke_width=7, stroke_fill="black", anchor="mm")
    img.save(path)


def fix_words(words, cid=None):
    w = [dict(x) for x in words]
    for x in w:
        if x["w"].lower().startswith(".now"):
            x["w"] = ".now"
    if cid == "0545":       # whisper hears "just call in AI"; he says "just comment AI"
        i = next(k for k, x in enumerate(w) if x["w"].lower().startswith("call"))
        w[i]["w"] = "comment"
        w[i]["e"] = w[i + 1]["e"]
        del w[i + 1]
    return w


def demo_plan():
    allw = json.load(open(f"{B}/new.json"))
    allw.update(json.load(open(f"{B}/end.json")))
    clips, f0 = [], 0
    for cid in DEMO + END:
        path = (glob.glob(f"{B}/new/*_{cid}_D.MP4") + glob.glob(f"{B}/end/*_{cid}_D.MP4"))[0]
        dur, fps, _ = bai.cds.probe(path)
        audio = bai.cds.load_audio(path)
        keeps, level = bai.tight_keeps(audio, dur, fps)
        words = fix_words(allw[os.path.basename(path)], cid)
        if cid == END[-1]:      # last clip of the video: let the final word finish, then a little room tone
            ks_, ke_ = keeps[-1]
            keeps[-1] = (ks_, min(math.floor(dur * fps) / fps, math.ceil((words[-1]["e"] + TAIL_AFTER_LAST_WORD) * fps) / fps))
        sl = np.concatenate([audio[int(s * 16000): int(e * 16000)] for s, e in keeps])
        rms = 20 * math.log10(float(np.sqrt((sl ** 2).mean())) + 1e-9)
        gain = max(-12.0, min(12.0, -20.0 - rms))
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
        caps = bai.phrase_captions(words)
        out = []
        for j, (text, a, b) in enumerate(caps):
            fa = f0 if j == 0 else out_frame(words[a]["s"])
            fb = out_frame(words[caps[j + 1][1]]["s"]) if j + 1 < len(caps) else o
            out.append((text, fa, fb))
        wf = [out_frame(x["s"]) for x in words]
        clips.append(dict(cid=cid, path=path, pieces=pieces, f0=f0, f1=o, gain=gain, caps=out, wf=wf, words=words))
        f0 = o
    return clips, f0


def main():
    out = sys.argv[1]
    rw, rh, rn = text_removed_region()
    # ---- 1. hook: the example's first 11.0 s, "YT Shorts" erased, Buzzy logo in its place
    hook = f"{OV}/hook.mkv"
    run(["ffmpeg", "-v", "error", "-y", "-i", EX,
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{rw}x{rh}", "-r", str(FPS), "-i", f"{OV}/text_removed.rgb",
         "-i", f"{OV}/buzzy_logo_row.png", "-filter_complex",
         f"[0:v]trim=end={HOOK_END},setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS,format=yuv420p[tr];"
         f"[v0][tr]overlay={TEXT_BOX[0]}:{TEXT_BOX[1]}:eof_action=pass[v1];[v1][2:v]overlay=0:0,format=yuv420p[v];"
         f"[0:a]atrim=end={HOOK_END},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-r", str(FPS),
         "-c:a", "pcm_s16le", hook])
    # ---- 3. demo: new clips, tight cuts, captions, voice + music + riser tail
    clips, F = demo_plan()
    D = F / FPS
    D_demo = next(c for c in clips if c["cid"] == DEMO[-1])["f1"] / FPS
    music_start = (CTA_START + MUSIC_OFFSET) - D_demo     # music continuity: where the example's music was at the old CTA cut
    riser_from = HOOK_END - RISER_START                  # riser tail continues from the cut
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for c in clips:
        cmd += ["-i", c["path"]]
    caps = []   # (png, first frame, last frame + 1, y centre, x)
    for c in clips:
        cy = END_CAP_Y if c["cid"] in END else CAP_Y
        for j, (text, fa, fb) in enumerate(c["caps"]):
            p = f"{OV}/cap_{c['cid']}_{j}.png"
            caption_png(text, p)
            caps.append((p, fa, fb, cy, 0))
    # estimated-revenue card at the top of the screen, above his head, on "payouts like this" (he points up)
    c43 = next(c for c in clips if c["cid"] == "0543")
    k_pay = next(i for i, w in enumerate(c43["words"]) if w["w"].lower().startswith("payouts"))
    rev = Image.open(f"{B}/{REV_CARD}").convert("RGB")
    rev = rev.resize((420, round(rev.height * 420 / rev.width)), Image.LANCZOS)
    rev.save(f"{OV}/rev_top.png")
    caps.append((f"{OV}/rev_top.png", c43["wf"][k_pay], c43["f1"], 55 + 80, 30))   # y top 55, x 30 (above the fingertip)
    for p, *_ in caps:
        cmd += ["-i", p]
    mi = len(clips) + len(caps)
    cmd += ["-i", f"{B}/audio1.mp3", "-i", f"{B}/riser_notion.mp3"]
    g, lab = [], []
    for i, c in enumerate(clips):
        k = len(c["pieces"])
        g.append(f"[{i}:v]split={k}" + "".join(f"[sv{i}_{j}]" for j in range(k)))
        g.append(f"[{i}:a]asplit={k}" + "".join(f"[sa{i}_{j}]" for j in range(k)))
        for j, (ks, ke, o0, n) in enumerate(c["pieces"]):
            d = n / FPS
            g.append(f"[sv{i}_{j}]trim=start={ks:.6f}:end={ks + (n + 3) / FPS:.6f},setpts=PTS-STARTPTS,fps={FPS},"
                     f"trim=end_frame={n},scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p[pv{i}_{j}]")
            g.append(f"[sa{i}_{j}]atrim=start={ks:.6f}:end={ks + d:.6f},asetpts=PTS-STARTPTS,aresample=48000,"
                     f"aformat=channel_layouts=stereo,volume={c['gain']:.2f}dB,apad=whole_dur={d:.6f},atrim=0:{d:.6f},"
                     f"afade=t=in:d=0.008,afade=t=out:st={max(0, d - 0.008):.4f}:d=0.008[pa{i}_{j}]")
            lab.append(f"[pv{i}_{j}][pa{i}_{j}]")
    g.append("".join(lab) + f"concat=n={len(lab)}:v=1:a=1[base][voice]")
    prev = "base"
    for k, (p, fa, fb, cy, cx) in enumerate(caps):
        g.append(f"[{prev}][{len(clips) + k}:v]overlay={cx}:{cy - 80}:enable='between(n,{fa},{fb - 1})'[c{k}]")
        prev = f"c{k}"
    g.append(f"[{mi}:a]atrim=start={music_start:.3f}:end={music_start + D + 0.5:.3f},asetpts=PTS-STARTPTS,aresample=48000,"
             f"aformat=channel_layouts=stereo,volume={MUSIC_GAIN_DB}dB,atrim=0:{D:.4f},afade=t=out:st={D - 0.8:.3f}:d=0.8[mus]")
    g.append(f"[{mi + 1}:a]atrim=start={riser_from:.3f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[ris]")
    g.append("[voice][mus][ris]amix=inputs=3:duration=first:normalize=0[da]")
    demo = f"{OV}/demo.mkv"
    cmd += ["-filter_complex", ";".join(g), "-map", f"[{prev}]", "-map", "[da]", "-t", f"{D:.4f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-r", str(FPS), "-c:a", "pcm_s16le", demo]
    run(cmd)
    print(f"hook {HOOK_END:.2f}s + demo and new ending {D:.2f}s; music from {music_start:.2f}s", flush=True)
    for c in clips:
        print(f"  {c['cid']}: {(c['f1'] - c['f0']) / FPS:.2f}s  " + " | ".join(t for t, *_ in c["caps"]))
    # ---- 4. join the hook and the demo/ending
    run(["ffmpeg", "-v", "error", "-y", "-i", hook, "-i", demo, "-filter_complex",
         "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a0];[a0]alimiter=limit=0.89:level=disabled[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])

if __name__ == "__main__":
    main()
