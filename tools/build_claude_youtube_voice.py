#!/usr/bin/env python3
"""Claude YouTube, TALKING version: his no-talking edit with a voiceover recorded in a separate DJI clip.

His direction: take the audio of the DJI clip (`Dji ... 0593 D.mp4`, the picture is irrelevant: only his voice lines are
used) and match it to the clips of his original video, like the example `Claude-YouTube-talking-16s.mp4`: the hook plays
silent over the music, then each voice line starts exactly on the cut to its clip and the clip ends when the line ends.
The voice has 9 lines: go to claude | enter this prompt | copy your favorite script | go to openart.ai/direct |
go to quick start | select short film | paste in your prompt | post the video | post every day and get payouts like these.
"Quick start" and "select short film" share ONE clip (his original has a single Quick Start clip), and the gap between the
two lines is cut out of the audio while the picture runs on continuously.

Usage: EDIT_WORKDIR=/path build_claude_youtube_voice.py OUTFILE
EDIT_WORKDIR holds: cyt/ (the nine raw clips), assets/ (as for build_claude_youtube.py), fonts/, and cy/in/dji.mp4.
Labels and layout come from build_claude_youtube.py (unchanged); only the segment lengths follow the voice.
"""
import math, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ai_influencer as bai
import build_claude_youtube as cy

S, A, FPS = cy.S, cy.A, cy.FPS
DJI = f"{S}/cy/in/dji.mp4"
HOOK_FRAMES = 70
FINAL_TAIL = 0.25          # let his last word finish, keep a little room tone after it
MUSIC_UNDER_VOICE_DB = -11.0   # music sits this far below its hook level while he talks (example: music ducked)

# (clip, start second in the clip, label lines, label y, [voice line indexes])   -- start is kept for the picture
PLAN = [
    ("0430", 0.40, ["Go to Claude"], 610, [0]),
    ("0434", 0.10, ["Copy this prompt"], 612, [1]),
    ("0435", 0.35, ["Copy your favorite script"], 612, [2]),
    ("0440", 0.30, ["Go to openart.ai/direct"], 612, [3]),
    ("0443", 1.20, ["Go to Quick Start", "> Explainer"], 727, [4, 5]),
    ("0444", 0.30, ["Paste script"], 606, [6]),
    ("0445", 3.60, ["RESULTS"], 550, [7]),
    ("0446", 0.00, ["post everyday and", "get payouts like these"], 477, [8]),
]


def rms_db(x):
    return 20 * math.log10(float(np.sqrt((x ** 2).mean())) + 1e-9)


def main():
    out = sys.argv[1]
    audio = bai.cds.load_audio(DJI)
    dur, fps, _ = bai.cds.probe(DJI)
    lines, _ = bai.tight_keeps(audio, dur, fps)
    assert len(lines) == 9, f"expected 9 voice lines, found {len(lines)}: {lines}"
    gain = max(-12.0, min(12.0, bai.VOICE_RMS_TARGET - rms_db(np.concatenate([audio[int(s * 16000): int(e * 16000)] for s, e in lines]))))

    segs = [("0427", 0.60, None, None, HOOK_FRAMES, [])]        # hook: shocked reaction, no voice
    seg_audio = []                                              # (src start, frames) pieces for the voice track
    for cid, st, lab, ly, idx in PLAN:
        pieces = []
        for k in idx:
            s, e = lines[k]
            if k == 8:
                e = min(dur, e + FINAL_TAIL)
            pieces.append((s, max(1, round((e - s) * FPS))))
        n = sum(p[1] for p in pieces)
        segs.append((cid, st, lab, ly, n, pieces))
    cy.SEGMENTS[:] = [(cid, st, n, lab, ly) for cid, st, lab, ly, n, _ in segs]
    items, total_frames = cy.make_overlays()
    total = total_frames / FPS
    print(f"{total_frames} frames = {total:.2f}s; segment frames {[s[4] for s in segs]}", flush=True)

    cmd = ["ffmpeg", "-v", "error", "-stats", "-y"]
    for s in cy.SEGMENTS:
        cmd += ["-i", cy.find_clip(s[0])]
    for it in items:
        cmd += ["-i", it[0]]
    cmd += ["-i", f"{A}/song12.mp3", "-i", f"{A}/song12.mp3", "-i", DJI]
    n_seg, n_it = len(cy.SEGMENTS), len(items)
    song_i, dji_i = n_seg + n_it, n_seg + n_it + 2

    parts, lab = [], []
    for i, (cid, st, n, *_r) in enumerate(cy.SEGMENTS):
        parts.append(f"[{i}:v]trim=start={st:.4f}:end={st + (n + 2) / FPS:.4f},setpts=PTS-STARTPTS,fps={FPS},"
                     f"trim=end_frame={n},scale={cy.W}:{cy.H}:flags=lanczos,setsar=1,format=yuv420p[v{i}]")
        lab.append(f"[v{i}]")
    parts.append("".join(lab) + f"concat=n={n_seg}:v=1:a=0[base]")
    prev = "base"
    for k, (p, x, y, a, b) in enumerate(items):
        parts.append(f"[{prev}][{n_seg + k}:v]overlay={x}:{y}:enable='between(n,{a},{b - 1})'[o{k}]")
        prev = f"o{k}"

    # voice track: silence over the hook, then each voice line back to back
    vparts = [f"anullsrc=r=48000:cl=stereo,atrim=0:{HOOK_FRAMES / FPS:.6f}[vh]"]
    vlab, j = ["[vh]"], 0
    for _cid, _st, _lab, _ly, _n, pieces in segs[1:]:
        for s, n in pieces:
            d = n / FPS
            vparts.append(f"[{dji_i}:a]atrim=start={s:.6f}:end={s + d:.6f},asetpts=PTS-STARTPTS,aresample=48000,"
                          f"aformat=channel_layouts=stereo,volume={gain:.2f}dB,apad=whole_dur={d:.6f},atrim=0:{d:.6f},"
                          f"afade=t=in:d=0.006,afade=t=out:st={max(0, d - 0.006):.4f}:d=0.006[vl{j}]")
            vlab.append(f"[vl{j}]")
            j += 1
    parts += vparts
    parts.append("".join(vlab) + "concat=n=%d:v=0:a=1[voice]" % len(vlab))

    # music: loud over the hook (his original level), ducked while he talks; its start loops in if the video is longer
    m_raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{A}/song12.mp3", "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                           capture_output=True, check=True).stdout
    m_rms = rms_db(np.frombuffer(m_raw, np.int16).astype(np.float32) / 32768)
    m_gain = (bai.VOICE_RMS_TARGET + 1.0) - m_rms
    t_voice = HOOK_FRAMES / FPS
    duck = f"if(lt(t,{t_voice - 0.1:.3f}),1,if(lt(t,{t_voice + 0.2:.3f}),1-(t-{t_voice - 0.1:.3f})/0.3*(1-{10 ** (MUSIC_UNDER_VOICE_DB / 20):.4f}),{10 ** (MUSIC_UNDER_VOICE_DB / 20):.4f}))"
    parts.append(f"[{song_i}:a]aformat=channel_layouts=stereo,aresample=48000[sa]")
    parts.append(f"[{song_i + 1}:a]aformat=channel_layouts=stereo,aresample=48000,atrim=0:3,asetpts=PTS-STARTPTS[sb2]")
    parts.append("[sa][sb2]acrossfade=d=0.3:c1=tri:c2=tri[sx]")
    parts.append(f"[sx]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,volume={m_gain:.2f}dB,volume='{duck}':eval=frame,"
                 f"afade=t=out:st={total - 0.5:.3f}:d=0.5[mus]")
    parts.append("[voice][mus]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.9:level=disabled[aout]")

    cmd += ["-filter_complex", ";".join(parts), "-map", f"[{prev}]", "-map", "[aout]", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
