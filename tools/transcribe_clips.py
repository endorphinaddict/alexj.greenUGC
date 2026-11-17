import json, subprocess, sys, glob, os
import numpy as np
from faster_whisper import WhisperModel

src_dir, out_json = sys.argv[1], sys.argv[2]
model = WhisperModel("small.en", device="cpu", compute_type="int8")
result = {}
for path in sorted(glob.glob(os.path.join(src_dir, "*"))):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
        check=True, capture_output=True).stdout
    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    segs, _ = model.transcribe(audio, word_timestamps=True, vad_filter=False, language="en")
    words = [dict(s=round(w.start, 2), e=round(w.end, 2), w=w.word.strip())
             for s in segs for w in s.words]
    result[os.path.basename(path)] = words
    print(os.path.basename(path), "->", " ".join(w["w"] for w in words) or "(no speech)", flush=True)
json.dump(result, open(out_json, "w"), indent=1)
