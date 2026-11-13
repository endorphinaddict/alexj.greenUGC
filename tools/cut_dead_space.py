#!/usr/bin/env python3
"""Cut every stretch of a talking-head clip where nobody is speaking.

    python3 tools/cut_dead_space.py IN.mp4 OUT.mp4            # cut and encode
    python3 tools/cut_dead_space.py IN.mp4 OUT.mp4 --dry-run  # print the cut list only

How it decides what is "talking":
  1. Silero VAD (the neural voice detector bundled with `pip install faster-whisper`)
     marks speech. Unlike a plain volume gate, it ignores room tone, hum and music.
  2. Each speech edge is nudged outward while the audio is still above the room's
     noise floor, so soft word endings ("s", "f", trailing breath) are not clipped.
  3. A small pad is kept either side of every phrase, so cuts land in silence.
  4. A gap is cut only if more than --min-cut seconds would actually be removed.
     Shorter pauses are breaths between words, and cutting them just adds a visible
     jump for no gain.
  5. Cut points snap to whole video frames, so audio and picture stay in sync across
     dozens of cuts.
"""

import argparse
import json
import math
import subprocess
import sys

import numpy as np

SR = 16000          # analysis sample rate
HOP = 160           # 10 ms loudness frames
MAX_REACH = 0.15    # how far (s) an edge may be extended past the VAD boundary
FADE = 0.008        # per-segment audio fade (s), stops clicks at the joins


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,avg_frame_rate", "-of", "json", path],
        check=True, capture_output=True, text=True).stdout
    info = json.loads(out)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    num, den = (int(x) for x in video["avg_frame_rate"].split("/"))
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    return float(info["format"]["duration"]), num / den, has_audio


def load_audio(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR),
         "-f", "s16le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def speech_segments(audio, threshold):
    from faster_whisper.vad import VadOptions, get_speech_timestamps
    opts = VadOptions(threshold=threshold, min_silence_duration_ms=120,
                      speech_pad_ms=0, min_speech_duration_ms=80)
    return [(t["start"] / SR, t["end"] / SR) for t in get_speech_timestamps(audio, opts)]


def loudness(audio):
    n = len(audio) // HOP
    rms = np.sqrt((audio[: n * HOP].reshape(n, HOP) ** 2).mean(axis=1))
    return 20 * np.log10(rms + 1e-9)


def refine(segs, db):
    """Snap each VAD edge to where the sound actually starts and stops.

    The VAD works in 32 ms windows and smooths its output, so its edges can sit a
    tenth of a second inside silence or a little inside a fading word. Each edge
    is first pulled in past any frames at or below the noise floor, then pushed out
    while the audio is still above it.
    """
    speech = np.zeros(len(db), bool)
    for s, e in segs:
        speech[int(s * 100): int(e * 100) + 1] = True
    quiet = db[~speech]
    floor = max(-50.0, float(np.median(quiet)) + 6) if quiet.size else -50.0
    reach = int(MAX_REACH * 100)
    out = []
    for s, e in segs:
        i, j = int(s * 100), min(int(e * 100), len(db) - 1)
        lo, hi = max(0, i - reach), min(len(db) - 1, j + reach)
        while i < j and i < lo + 2 * reach and db[i] <= floor:
            i += 1
        while j > i and j > hi - 2 * reach and db[j] <= floor:
            j -= 1
        while i > lo and db[i - 1] > floor:
            i -= 1
        while j < hi and db[j + 1] > floor:
            j += 1
        out.append((i / 100, (j + 1) / 100))
    return out, floor


def plan(segs, duration, fps, pad, min_cut):
    keep = []
    for s, e in segs:
        s, e = max(0.0, s - pad), min(duration, e + pad)
        if keep and s - keep[-1][1] < min_cut:
            keep[-1] = (keep[-1][0], e)          # gap too small to bother cutting
        else:
            keep.append((s, e))
    frames = []
    for s, e in keep:
        fs, fe = math.floor(s * fps), min(math.ceil(e * fps), math.floor(duration * fps))
        if frames and fs <= frames[-1][1]:
            frames[-1] = (frames[-1][0], fe)
        elif fe > fs:
            frames.append((fs, fe))
    return [(fs / fps, fe / fps) for fs, fe in frames]


def render(src, dst, keep, fps, crf):
    parts, labels = [], []
    for k, (s, e) in enumerate(keep):
        d = e - s
        parts.append(f"[0:v]trim=start={s:.6f}:end={e:.6f},setpts=PTS-STARTPTS[v{k}]")
        parts.append(f"[0:a]atrim=start={s:.6f}:end={e:.6f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d={FADE},afade=t=out:st={max(0, d - FADE):.6f}:d={FADE}[a{k}]")
        labels.append(f"[v{k}][a{k}]")
    parts.append(f"{''.join(labels)}concat=n={len(keep)}:v=1:a=1[v][a]")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-stats", "-y", "-i", src,
         "-filter_complex", ";".join(parts), "-map", "[v]", "-map", "[a]",
         "-r", f"{fps:g}", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
         "-movflags", "+faststart", dst], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--pad", type=float, default=0.05,
                    help="silence kept either side of each phrase, seconds (default 0.05)")
    ap.add_argument("--min-cut", type=float, default=0.10,
                    help="only cut a gap if at least this much would go, seconds (default 0.10)")
    ap.add_argument("--threshold", type=float, default=0.5,
                    help="VAD speech probability; lower keeps more quiet speech (default 0.5)")
    ap.add_argument("--crf", type=int, default=20, help="x264 quality, lower is better (default 20)")
    ap.add_argument("--dry-run", action="store_true", help="print the cut list and stop")
    a = ap.parse_args()

    duration, fps, has_audio = probe(a.src)
    if not has_audio:
        sys.exit("No audio track, so there is no speech to find.")
    audio = load_audio(a.src)
    raw = speech_segments(audio, a.threshold)
    if not raw:
        sys.exit("No speech detected. Try a lower --threshold.")
    segs, floor = refine(raw, loudness(audio))
    keep = plan(segs, duration, fps, a.pad, a.min_cut)

    kept = sum(e - s for s, e in keep)
    print(f"noise floor {floor:.1f} dB | {len(keep)} segments | {fps:g} fps")
    prev = 0.0
    for s, e in keep:
        if s - prev > 1e-6:
            print(f"  cut  {prev:7.3f} - {s:7.3f}  ({s - prev:.2f}s)")
        print(f"  keep {s:7.3f} - {e:7.3f}  ({e - s:.2f}s)")
        prev = e
    if duration - prev > 1e-6:
        print(f"  cut  {prev:7.3f} - {duration:7.3f}  ({duration - prev:.2f}s)")
    print(f"{duration:.2f}s -> {kept:.2f}s  (removed {duration - kept:.2f}s)")

    if not a.dry_run:
        render(a.src, a.dst, keep, fps, a.crf)
        print(f"wrote {a.dst}")


if __name__ == "__main__":
    main()
