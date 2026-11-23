#!/usr/bin/env python3
"""Swap two things in his finished edit `Footage/sound up .mp4` (1080x1920, 27.97 s, captions/pop-ups burned in):
 1. the yellow Buzzy bee in the middle of the hook row -> the YouTube Shorts logo (bee erased per frame with cv2.inpaint, logo laid on top)
 2. the demo section (10.433-22.633 s, the ChatGPT / Buzzy screen part) -> `Footage/demo.mp4` (0-12.2 s, the middle part of the four shirt videos)
Usage: EDIT_WORKDIR=/path build_soundup_swap.py OUT.mp4   (needs bs/soundup.mp4, bs/demo.mp4, bs/pics/youtube_shorts_cutout.png, assets/music.mp3)
Audio: hook and ending are his original track untouched; the demo section is demo.mp4's own voice-over (as in the shirt videos) with the music under it.
"""
import math, os, subprocess, sys
import numpy as np
import cv2
from PIL import Image

S = os.environ.get("EDIT_WORKDIR", "work"); BS = f"{S}/bs"; OV = f"{BS}/ov_soundup"; os.makedirs(OV, exist_ok=True)
SRC, DEMO = f"{BS}/soundup.mp4", f"{BS}/demo.mp4"
FPS, W, H = 30, 1080, 1920
F_A, F_B = 313, 679            # hook = frames [0,313), demo = [313,679), ending = [679,end)   (10.433 s, 22.633 s)
BOX = (405, 120, 280, 210)     # x, y, w, h around the bee
LOGO_H, LOGO_CX, LOGO_CY = 230, 545, 222


def run(c): subprocess.run(c, check=True)


def bee_mask(box):
    """Everything in the box that differs clearly from the wall colour (median of the box's border) is bee: yellow body, white/grey wings, dark outline."""
    edge = np.concatenate([box[:6].reshape(-1, 3), box[-6:].reshape(-1, 3), box[:, :6].reshape(-1, 3), box[:, -6:].reshape(-1, 3)])
    wall = np.median(edge, axis=0)
    d = np.abs(box.astype(int) - wall.astype(int)).sum(-1)
    m = (d > 55).astype(np.uint8) * 255
    return cv2.dilate(m, np.ones((9, 9), np.uint8))


def main():
    out = sys.argv[1]
    x, y, w, h = BOX
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-frames:v", str(F_A), "-vf", f"crop={w}:{h}:{x}:{y}", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).copy()
    for k in range(len(fr)):
        bgr = cv2.cvtColor(fr[k], cv2.COLOR_RGB2BGR)
        fr[k] = cv2.cvtColor(cv2.inpaint(bgr, bee_mask(fr[k]), 6, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)
    fr.tofile(f"{OV}/patch.rgb")
    logo = Image.open(f"{BS}/pics/youtube_shorts_cutout.png").convert("RGBA")
    logo = logo.crop(logo.split()[3].point(lambda v: 255 if v > 40 else 0).getbbox())
    logo = logo.resize((round(logo.width * LOGO_H / logo.height), LOGO_H), Image.LANCZOS)
    cv = Image.new("RGBA", (W, 400), (0, 0, 0, 0)); cv.alpha_composite(logo, (LOGO_CX - logo.width // 2, LOGO_CY - LOGO_H // 2)); cv.save(f"{OV}/logo.png")

    # hook: original video with the bee patched out and the logo on top; original audio
    run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS), "-i", f"{OV}/patch.rgb", "-i", f"{OV}/logo.png",
         "-filter_complex", f"[0:v]trim=end_frame={F_A},setpts=N/({FPS}*TB)[v0];[1:v]setpts=N/({FPS}*TB),format=yuv420p[p];[v0][p]overlay={x}:{y}:eof_action=pass[v1];[v1][2:v]overlay=0:0,format=yuv420p[v];"
                            f"[0:a]atrim=end={F_A / FPS},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-c:a", "pcm_s16le", f"{OV}/hook.mkv"])
    # demo: demo.mp4 0-12.2 s (366 frames) with music under its voice
    n = F_B - F_A
    raw = subprocess.run(["ffmpeg", "-v", "error", "-t", "12.2", "-i", DEMO, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    v_rms = 20 * math.log10(float(np.sqrt((a ** 2).mean())) + 1e-9)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "15", "-t", "12", "-i", f"{S}/assets/music.mp3", "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    m = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    m_gain = (v_rms - 14.0) - 20 * math.log10(float(np.sqrt((m ** 2).mean())) + 1e-9)
    run(["ffmpeg", "-v", "error", "-y", "-i", DEMO, "-ss", "15", "-i", f"{S}/assets/music.mp3", "-filter_complex",
         f"[0:v]trim=end_frame={n},setpts=N/({FPS}*TB),fps={FPS},scale={W}:{H},setsar=1,format=yuv420p[v];"
         f"[0:a]atrim=0:{n / FPS:.4f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={n / FPS:.4f}[va];"
         f"[1:a]atrim=0:{n / FPS:.4f},asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo,aresample=48000,volume={m_gain:.2f}dB[mu];"
         "[va][mu]amix=inputs=2:duration=first:normalize=0[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-c:a", "pcm_s16le", f"{OV}/demo.mkv"])
    # ending: original
    run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex",
         f"[0:v]trim=start_frame={F_B},setpts=N/({FPS}*TB),format=yuv420p[v];[0:a]atrim=start={F_B / FPS:.5f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-c:a", "pcm_s16le", f"{OV}/end.mkv"])
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{OV}/hook.mkv", "-i", f"{OV}/demo.mkv", "-i", f"{OV}/end.mkv", "-filter_complex",
         "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])


if __name__ == "__main__":
    main()
