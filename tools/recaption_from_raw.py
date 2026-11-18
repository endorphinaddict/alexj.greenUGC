#!/usr/bin/env python3
"""Move the burned-in captions of a finished edit (one of our builds, re-exported by him) to a new height.

Burned-in captions cannot be erased cleanly (inpainting smudges), so the picture is rebuilt caption-free from the
raw clips: every frame of the edit is matched to its raw-clip frame, then the same captions (same words, same
frames, permanent style from tools/captions.py) are drawn at the new baseline. The edit's audio is copied as is.

Usage:
  EDIT_WORKDIR=W recaption_from_raw.py EDIT.mp4 RAW_DIR TEXTS.json OUT.mp4 [--baseline 1500] [--old-baseline 1325]
TEXTS.json: list of the captions shown in the edit, read off its frames (e.g. ["go to chat", "tell it to give", ...]).
RAW_DIR: the raw clips the edit was cut from (restore deleted ones from the footage branch history with git show).
Prints the frame mapping and the caption timing it found; check frames before sending.
"""
import argparse, glob, json, os, subprocess, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import captions as cs

TW, TH = 72, 128          # matching thumbnails
SW, SH = 540, 960         # caption analysis size


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "json", path], capture_output=True, text=True).stdout
    s = json.loads(out)["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return s["width"], s["height"], int(n) / int(d)


def gray(path, w, h, fw, fh):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:v:0", "-vf",
                          f"scale={fw}:{fh}:flags=lanczos,scale={w}:{h}:flags=area,format=gray", "-vsync", "0",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("edit"); ap.add_argument("raw_dir"); ap.add_argument("texts"); ap.add_argument("out")
    ap.add_argument("--baseline", type=int, default=cs.BASELINE_Y)
    ap.add_argument("--old-baseline", type=int, default=1325)
    a = ap.parse_args()
    work = os.environ.get("EDIT_WORKDIR", os.path.abspath("work")) + "/recap"
    os.makedirs(work, exist_ok=True)
    FW, FH, efps = probe(a.edit)
    raws = sorted(p for p in glob.glob(f"{a.raw_dir}/*") if p.lower().endswith((".mp4", ".mov")))
    names = [os.path.basename(p) for p in raws]
    texts = json.load(open(a.texts))
    old_top, old_bot = a.old_baseline - 80, a.old_baseline + 30   # old caption rows (cap height + descenders)

    # 1. match every edit frame to a raw frame (old caption rows and the top strip are masked out)
    E = gray(a.edit, TW, TH, FW, FH)
    R = [gray(p, TW, TH, FW, FH) for p in raws]
    mask = np.ones((TH, TW), bool)
    mask[int(old_top * TH / FH) - 1:int(old_bot * TH / FH) + 2] = False
    mask[:int(220 * TH / FH)] = False
    dup = int(round(1 / max(1e-6, 1 - (np.abs(np.diff(E, axis=0)).mean(axis=(1, 2)) < 0.3).mean())))
    best = []
    for f in E:
        cand = []
        for c, r in enumerate(R):
            e = (((r - f) ** 2) * mask).sum(axis=(1, 2)) / mask.sum()
            cand.append((float(e.min()), c, int(e.argmin())))
        best.append(min(cand))
    runs, s = [], 0
    for i in range(1, len(best) + 1):
        if i == len(best) or best[i][1] != best[s][1] or not 0 <= best[i][2] - best[i - 1][2] <= 3:
            runs.append((s, i, best[s][1])); s = i
    plan = []
    for s, e, c in runs:
        sfps = probe(raws[c])[2]
        fit = None
        for phase in range(dup):
            for s0 in np.arange(max(0, best[s][2] - 2), best[s][2] + 2, 0.25):
                idx = [int(round(s0 + ((i - s + phase) // dup) * sfps * dup / efps)) for i in range(s, e)]
                if idx[-1] >= len(R[c]):
                    continue
                err = sum((((R[c][j] - E[i]) ** 2) * mask).sum() for i, j in zip(range(s, e), idx)) / mask.sum()
                if fit is None or err < fit[0]:
                    fit = (err, idx)
        plan.append(dict(a=s, b=e, clip=c, idx=fit[1]))
        print(f"edit frames {s:4d}-{e - 1:4d} <- {names[c]} frames {fit[1][0]}..{fit[1][-1]}  err {fit[0] / (e - s):.2f}")

    # 2. which caption is on each frame: composite each candidate on the clean frame, keep the best fit
    y0, y1 = old_top * SH // FH - 10, old_bot * SH // FH + 10
    Eb = gray(a.edit, SW, SH, FW, FH)[:, y0:y1]
    cache, clean = {}, np.zeros_like(Eb)
    for p in plan:
        if p["clip"] not in cache:
            cache[p["clip"]] = gray(raws[p["clip"]], SW, SH, FW, FH)[:, y0:y1]
        for i, j in zip(range(p["a"], p["b"]), p["idx"]):
            clean[i] = cache[p["clip"]][j]
    cands = []
    for k, t in enumerate(texts):
        cs.render(t, f"{work}/old_{k}.png")
        canvas = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
        canvas.paste(Image.open(f"{work}/old_{k}.png"), (0, a.old_baseline - cs.BASELINE))
        sm = np.asarray(canvas.resize((SW, SH), Image.BOX)).astype(np.float32)[y0:y1]
        cands.append((sm[..., 3] / 255.0, sm[..., 0]))
    labels = []
    for i in range(len(Eb)):
        errs = [float(((Eb[i] - (clean[i] * (1 - al) + lum * al)) ** 2).mean()) for al, lum in cands]
        none = float(((Eb[i] - clean[i]) ** 2).mean())
        k = int(np.argmin(errs))
        labels.append(k if errs[k] < 0.5 * none else None)
    segs, s = [], 0
    for i in range(1, len(labels) + 1):
        if i == len(labels) or labels[i] != labels[s]:
            if labels[s] is not None:
                segs.append((texts[labels[s]], s, i))
            print(f"  frames {s:4d}-{i - 1:4d}  {texts[labels[s]] if labels[s] is not None else '(no caption)'}")
            s = i

    # 3. render: clean raw frames + captions at the new baseline (composited in YUV, bt709 tv range)
    YS, CS = FW * FH, (FW // 2) * (FH // 2)
    oy = a.baseline - cs.BASELINE
    caps, cap_at = {}, {}
    for text, s, e in segs:
        if text not in caps:
            cs.render(text, f"{work}/new.png")
            im = np.asarray(Image.open(f"{work}/new.png").convert("RGBA")).astype(np.float32)
            al = im[..., 3] / 255.0
            caps[text] = (al, 16 + 219 * im[..., 0] / 255.0, al.reshape(cs.CAP_H // 2, 2, FW // 2, 2).mean(axis=(1, 3)))
        for i in range(s, e):
            cap_at[i] = text
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", f"{FW}x{FH}",
                            "-r", f"{efps:g}", "-i", "-", "-i", a.edit, "-map", "0:v", "-map", "1:a",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-profile:v", "high", "-pix_fmt", "yuv420p",
                            "-color_range", "tv", "-colorspace", "bt709", "-color_trc", "bt709", "-color_primaries", "bt709",
                            "-c:a", "copy", "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    for p in plan:
        lo, hi = p["idx"][0], p["idx"][-1]
        dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", raws[p["clip"]], "-map", "0:v:0", "-vf",
                                f"trim=start_frame={lo}:end_frame={hi + 1},scale={FW}:{FH}:flags=lanczos,format=yuv420p",
                                "-vsync", "0", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
        cur, buf = lo - 1, None
        for i, j in zip(range(p["a"], p["b"]), p["idx"]):
            while cur < j:
                buf = np.frombuffer(dec.stdout.read(YS + 2 * CS), np.uint8); cur += 1
            fr = buf.copy()
            if i in cap_at:
                al, ycap, al2 = caps[cap_at[i]]
                Y = fr[:YS].reshape(FH, FW)
                Y[oy:oy + cs.CAP_H] = np.clip(Y[oy:oy + cs.CAP_H] * (1 - al) + ycap * al + 0.5, 0, 255).astype(np.uint8)
                for off in (YS, YS + CS):
                    C = fr[off:off + CS].reshape(FH // 2, FW // 2)
                    r = C[oy // 2:oy // 2 + cs.CAP_H // 2]
                    C[oy // 2:oy // 2 + cs.CAP_H // 2] = np.clip(r * (1 - al2) + 128 * al2 + 0.5, 0, 255).astype(np.uint8)
            enc.stdin.write(fr.tobytes())
        dec.stdout.close(); dec.wait()
    enc.stdin.close(); enc.wait()
    print(f"wrote {a.out}: captions at baseline y {a.baseline} (were {a.old_baseline})")


if __name__ == "__main__":
    main()
