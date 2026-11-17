#!/usr/bin/env python3
"""Build the AI-Influencer-Equation edit, matched to Marcus's reference layout.

See CLAUDE.md ("How to rebuild the edit"). Set EDIT_WORKDIR to the working folder.
Usage: build_ai_influencer.py OUTDIR OUTFILE [--stage A|B|all|none]
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cut_dead_space as cds

S = os.environ.get("EDIT_WORKDIR", os.path.abspath("work"))  # holds clips/Footage, assets/, fonts/, transcripts.json
CLIPS = f"{S}/clips/Footage"
A = f"{S}/assets"
OV = f"{S}/overlays"
os.makedirs(OV, exist_ok=True)
W, H, FPS = 1080, 1920, 30
FONT_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
# CapCut's "Classic" text font is Proxima Nova Semibold; Montserrat SemiBold (OFL) is its free look-alike.
FONT_CAP = f"{S}/fonts/Montserrat-SemiBold.ttf"

ORDER = [
    ("DJI_20261115191119_0356_D.MP4", [("you've probably", 2), ("seen videos", 2), ("like this", 2)]),
    ("DJI_20261115175847_0323_D.MP4", [("they're actually", 2), ("getting millions", 2), ("of views", 2),
                                       ("and generating", 2), ("thousands", 1), ("of dollars", 2)]),
    ("DJI_20261115180021_0328_D.MP4", [("so let me", 3), ("show you how", 3), ("you can make", 3),
                                       ("the same exact", 3), ("video before", 2), ("someone else", 2),
                                       ("puts it behind", 3), ("a $5,000", 3), ("course", 1)]),
    ("IMG_8835.mov", [("go to buzzy.now", 5), ("hover over skills", 3), ("and then come over", 4),
                      ("to ai influencer", 3), ("generator", 1)]),
    ("IMG_8836.mov", [("download your", 2), ("reference image", 2)]),
    ("IMG_8837.mov", [("drop the reference", 3), ("and then type", 3), ("this in the prompt", 4)]),
    ("IMG_8834.mov", [("now if you", 3), ("got videos", 2), ("just like that", 3)]),
    ("DJI_20261115180747_0341_D.MP4", [("now all you", 3), ("need to do", 3), ("is post", 2),
                                       ("consistently", 1), ("to get payouts", 3), ("like this", 2)]),
    ("DJI_20261115180807_0342_D.MP4", [("if you want", 3), ("my full guide", 3), ("just comment ai", 3),
                                       ("below and", 2), ("i'll dm you", 3), ("my full guide", 3)]),
]
VOICE_RMS_TARGET = -20.0
MUSIC_START = 4.45  # seconds into the track: right on the build's peak hit, so the video opens on it
# Requested exception to the no-dead-space rule: hold the hook clip after its last word so the
# AI influencer pop-up plays longer.
EXTEND = {"DJI_20261115191119_0356_D.MP4": 1.0}
POPUP_AT_SRC = 1.51  # source time in the hook clip where he starts saying "this"
POPUP_X, POPUP_Y = 660, 440  # over the raised pen (x~690-735, y~740-1000), ~90px clear of the face

# Tight cutting (his rule: no dead space at all; cut the moment he stops talking).
CORE_DB = 15.0      # "talking" = within 15 dB of his median speech level
TAIL_DB = 20.0      # edges may extend through softer sound (word tails) down to 20 dB below
MAX_GAP = 0.15      # any pause longer than this inside a clip is cut out
EDGE_IN, EDGE_OUT = 0.03, 0.04   # how far an edge may extend through soft sound
PAD_IN, PAD_OUT = 0.01, 0.02     # tiny pads so first/last consonants are never clipped


def tight_keeps(audio, dur, fps):
    db = cds.loudness(audio)                      # 10 ms frames
    vad = cds.speech_segments(audio, 0.5)
    vmask = np.zeros(len(db), bool)
    for s, e in vad:
        vmask[max(0, int(s * 100) - 10): int(e * 100) + 10] = True
    level = float(np.median(db[vmask])) if vmask.any() else float(np.median(db))
    core = (db > level - CORE_DB) & vmask
    runs, i = [], 0
    while i < len(core):
        if core[i]:
            j = i
            while j < len(core) and core[j]:
                j += 1
            runs.append([i, j])
            i = j
        else:
            i += 1
    merged = []
    for r in runs:                                   # natural word gaps (< MAX_GAP) stay joined
        if merged and (r[0] - merged[-1][1]) / 100 < MAX_GAP:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    merged = [r for r in merged if (r[1] - r[0]) >= 6]   # drop blips under 60 ms
    soft = db > level - TAIL_DB
    keeps = []
    for a, b in merged:
        lo = max(0, a - int(EDGE_IN * 100))
        while a > lo and soft[a - 1]:
            a -= 1
        hi = min(len(db), b + int(EDGE_OUT * 100))
        while b < hi and soft[b]:
            b += 1
        s = max(0.0, a / 100 - PAD_IN)
        e = min(dur, b / 100 + PAD_OUT)
        s, e = math.floor(s * fps) / fps, min(math.floor(dur * fps) / fps, math.ceil(e * fps) / fps)
        if keeps and s <= keeps[-1][1] + 1 / fps:
            keeps[-1] = (keeps[-1][0], e)
        else:
            keeps.append((s, e))
    return keeps, level


CAP_LINE_CHARS = 26   # reference style: phrase captions, up to 2 lines of ~26 characters
PAIR_MAX_CHARS = 18   # two words share a caption only if they fit on one short line


def display_tokens(words):
    """Whisper tokens -> caption words: lowercase, no punctuation, fixes like '$5' ',000' -> '$5,000'."""
    out = []  # (text, first_word_idx, last_word_idx)
    i = 0
    while i < len(words):
        w = words[i]["w"].strip()
        if out and w.startswith(",") and w[1:].isdigit():          # ",000" joins the number before it
            t, a, _ = out[-1]
            out[-1] = (t + w, a, i)
        elif w.lower().strip(".,") == "dot" and out and i + 1 < len(words):   # "buzzy dot now" -> buzzy.now
            t, a, _ = out[-1]
            out[-1] = (t + "." + words[i + 1]["w"].strip().strip(".,!?").lower(), a, i + 1)
            i += 1
        elif w.startswith(".") and out:                              # "buzzy" ".now"
            t, a, _ = out[-1]
            out[-1] = (t + w.rstrip(".,!?").lower(), a, i)
        else:
            out.append((w.lower().strip(".,!?\"").replace(" ", ""), i, i))
        i += 1
    return out


def phrase_captions(words):
    """Group words into reference-style captions: fill up to two lines, break at sentence ends."""
    toks = display_tokens(words)
    caps, cur = [], []

    def fits(tokens):
        lines, line = [], ""
        for t, _, _ in tokens:
            cand = (line + " " + t).strip()
            if len(cand) <= CAP_LINE_CHARS or not line:
                line = cand
            else:
                lines.append(line)
                line = t
        lines.append(line)
        return len(lines) <= 2

    # split into sentences, then cut each sentence into the fewest evenly sized captions that fit
    sentences, cur = [], []
    for tok in toks:
        cur.append(tok)
        if words[tok[2]]["w"].strip().endswith((".", "?", "!")):
            sentences.append(cur)
            cur = []
    if cur:
        sentences.append(cur)
    # His rule: one line, 1-2 words per caption. Pair words within a sentence; a word stays on its
    # own when the pair would be long (> PAIR_MAX_CHARS), and a sentence never ends on a lone word
    # if it can be avoided by shifting the pairing.
    # Phrase-aware pairing (dynamic programming): words like "of"/"to"/"the" lead into the next word,
    # so a caption should not end on one, and a pair never spans a comma.
    LEADS = {"a", "an", "the", "of", "to", "my", "your", "and", "in", "on", "at", "for", "with", "or"}
    phrases, cur = [], []
    for sent in sentences:
        for tok in sent:
            cur.append(tok)
            if words[tok[2]]["w"].strip().endswith((",", ".", "?", "!")):
                phrases.append(cur)
                cur = []
        if cur:
            phrases.append(cur)
            cur = []
    for ph in phrases:
        n = len(ph)
        best = [0.0] + [math.inf] * n
        how = [0] * (n + 1)
        for i in range(1, n + 1):
            w1 = ph[i - 1][0]
            # single word; a lone word at the very end of a phrase costs a little extra
            c1 = best[i - 1] + 1.5 + (3.0 if w1 in LEADS else 0.0) + (1.0 if i == n else 0.0)
            if c1 < best[i]:
                best[i], how[i] = c1, 1
            if i >= 2:
                w0 = ph[i - 2][0]
                if len(w0) + 1 + len(w1) <= PAIR_MAX_CHARS:
                    c2 = best[i - 2] + (3.0 if w1 in LEADS else 0.0)            # pair
                    if c2 < best[i]:
                        best[i], how[i] = c2, 2
        groups, i = [], n
        while i > 0:
            groups.append(ph[i - how[i]: i])
            i -= how[i]
        caps.extend(reversed(groups))
    return [(" ".join(t for t, _, _ in c), c[0][1], c[-1][2]) for c in caps]


# ---------- timeline ----------
def make_plan():
    words_all = json.load(open(f"{S}/transcripts.json"))
    segs = []
    t = 0.0
    for name, chunks in ORDER:
        path = f"{CLIPS}/{name}"
        dur, fps, _ = cds.probe(path)
        audio = cds.load_audio(path)
        keeps, level = tight_keeps(audio, dur, fps)
        sl = np.concatenate([audio[int(s * 16000): int(e * 16000)] for s, e in keeps])
        rms = 20 * math.log10(float(np.sqrt((sl ** 2).mean())) + 1e-9)
        gain = max(-12.0, min(12.0, VOICE_RMS_TARGET - rms))
        if name in EXTEND:
            s_last, e_last = keeps[-1]
            keeps[-1] = (s_last, min(math.floor(dur * fps) / fps, math.floor((e_last + EXTEND[name]) * fps) / fps))
        d = sum(e - s for s, e in keeps)
        starts, acc = [], t
        for s, e in keeps:
            starts.append(acc)
            acc += e - s

        def out_time(ts, t=t, keeps=keeps, starts=starts):
            # map a source time into output time; times inside a removed pause snap to the next kept part
            for (s, e), o in zip(keeps, starts):
                if ts < s:
                    return o
                if ts <= e:
                    return o + (ts - s)
            return starts[-1] + (keeps[-1][1] - keeps[-1][0])

        words = words_all[name]
        assert sum(n for _, n in chunks) == len(words), (name, len(words))
        caps = [[text, words[a]["s"], words[b]["e"]] for text, a, b in phrase_captions(words)]
        out_caps = []
        for j, (text, s0, e0) in enumerate(caps):
            a = t if j == 0 else out_time(s0)
            b = out_time(caps[j + 1][1]) if j + 1 < len(caps) else t + d
            out_caps.append((text, a, b))
        wt = {k: (out_time(w["s"]), out_time(w["e"])) for k, w in enumerate(words)}
        segs.append(dict(name=name, path=path, keeps=keeps, d=d, t0=t, gain=gain, rms=rms, level=level,
                         caps=out_caps, wt=wt, words=words))
        t += d
    return segs, t


# ---------- overlay art ----------
def font(path, size):
    return ImageFont.truetype(path, size)


def stroked_text(img, xy, text, f, fill=(255, 255, 255, 255), stroke=6, anchor="mm"):
    d = ImageDraw.Draw(img)
    d.text(xy, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 235), anchor=anchor)


CAP_H = 200        # caption canvas height; the text block is centred in it
CAP_CENTER_Y = 1222  # block centre on the 1080x1920 frame (below the chin, above the cards at y=1290)


def caption_png(text, path):
    """Reference style: white semibold, thin dark outline + soft drop shadow, up to two centred lines."""
    from PIL import ImageFilter
    f = font(FONT_CAP, 50)
    words, lines, line = text.split(), [], ""
    for w_ in words:
        cand = (line + " " + w_).strip()
        if len(cand) <= CAP_LINE_CHARS or not line:
            line = cand
        else:
            lines.append(line)
            line = w_
    lines.append(line)
    lh = 58
    ys = [CAP_H / 2 - (len(lines) - 1) * lh / 2 + k * lh for k in range(len(lines))]
    shadow = Image.new("RGBA", (W, CAP_H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for ln, y in zip(lines, ys):
        sd.text((W // 2, y + 3), ln, font=f, fill=(0, 0, 0, 200), stroke_width=4, stroke_fill=(0, 0, 0, 200), anchor="mm")
    shadow = shadow.filter(ImageFilter.GaussianBlur(4))
    img = Image.new("RGBA", (W, CAP_H), (0, 0, 0, 0))
    img.alpha_composite(shadow)
    d = ImageDraw.Draw(img)
    for ln, y in zip(lines, ys):
        d.text((W // 2, y), ln, font=f, fill=(255, 255, 255, 255), stroke_width=3,
               stroke_fill=(20, 20, 20, 255), anchor="mm")
    img.save(path)


def top_png(path):
    # Kept in the top ~220px so it never overlaps the hair (hair top is ~y=260 in the outro clips).
    img = Image.new("RGBA", (W, 190), (0, 0, 0, 0))
    f = font(FONT_CAP, 56)
    stroked_text(img, (W // 2, 50), 'Comment "AI"', f, stroke=6)
    stroked_text(img, (W // 2, 128), "for the full guide", f, stroke=6)
    img.save(path)


def insta_icon(size):
    ss = 4
    n = size * ss
    grad = Image.new("RGB", (n, n))
    px = grad.load()
    stops = [(0.0, (254, 218, 117)), (0.25, (250, 126, 30)), (0.5, (214, 41, 118)),
             (0.75, (150, 47, 191)), (1.0, (79, 91, 213))]

    def col(u):
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if u <= b:
                k = (u - a) / (b - a)
                return tuple(int(ca[i] + (cb[i] - ca[i]) * k) for i in range(3))
        return stops[-1][1]
    for y in range(n):
        for x in range(n):
            u = ((x / n) + (1 - y / n)) / 2  # bottom-left -> top-right
            px[x, y] = col(min(1.0, max(0.0, u)))
    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, n - 1, n - 1], radius=int(n * 0.26), fill=255)
    icon = grad.convert("RGBA")
    icon.putalpha(mask)
    d = ImageDraw.Draw(icon)
    c = n / 2
    s = n * 0.30  # half width of the glyph body
    sw = int(n * 0.062)
    d.rounded_rectangle([c - s, c - s, c + s, c + s], radius=int(n * 0.17), outline="white", width=sw)
    r = n * 0.145
    d.ellipse([c - r, c - r, c + r, c + r], outline="white", width=sw)
    rd = n * 0.036
    cx, cy = c + s * 0.62, c - s * 0.62
    d.ellipse([cx - rd, cy - rd, cx + rd, cy + rd], fill="white")
    return icon.resize((size, size), Image.LANCZOS)


HOOK_TOP = 85  # row sits above the hair line (hair top is >= y=316 in the intro clips)


def hook_png(path):
    # Marcus's layout, scaled down and raised so it never overlaps the head.
    k = 0.76
    x0 = (W - 816 * k) / 2
    img = Image.new("RGBA", (W, 190), (0, 0, 0, 0))
    isz = round(198 * k)
    img.alpha_composite(insta_icon(isz), (round(x0), 0))
    face = Image.open(f"{A}/face.png").convert("RGBA").resize((isz, round(200 * k)), Image.LANCZOS)
    img.alpha_composite(face, (round(x0 + 339 * k), 0))
    esz = round(126 * k)
    emo = Image.open(f"{A}/emoji.png").convert("RGBA").resize((esz, esz), Image.LANCZOS)
    img.alpha_composite(emo, (round(x0 + 691 * k), round(33 * k)))
    # "+" and "=" are set in the caption font and caption style (white, thin outline, soft shadow).
    from PIL import ImageFilter
    cy = 99 * k
    f = font(FONT_CAP, 72)
    signs = [("+", x0 + 267 * k), ("=", x0 + 624 * k)]
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for ch, cx in signs:
        sd.text((cx, cy + 3), ch, font=f, fill=(0, 0, 0, 200), stroke_width=4, stroke_fill=(0, 0, 0, 200), anchor="mm")
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(4)))
    d = ImageDraw.Draw(img)
    for ch, cx in signs:
        d.text((cx, cy), ch, font=f, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(20, 20, 20, 255), anchor="mm")
    img.save(path)
    return HOOK_TOP


def card_png(src, path, width=480):
    im = Image.open(src).convert("RGB")
    h = round(im.height * width / im.width)
    im.resize((width, h), Image.LANCZOS).save(path)
    return h


# ---------- ffmpeg ----------
def run(cmd):
    print(" ".join(cmd)[:300], "...", flush=True)
    subprocess.run(cmd, check=True)


def stage_a(segs, base):
    cmd = ["ffmpeg", "-v", "error", "-stats", "-y"]
    for s in segs:
        cmd += ["-i", s["path"]]
    cmd += ["-i", f"{A}/dance.mp4"]  # burned into the hook clip itself, so it ends exactly at its last frame
    dance_idx = len(segs)
    parts, lab = [], []
    for i, s in enumerate(segs):
        keeps = s["keeps"]
        k = len(keeps)
        parts.append(f"[{i}:v]split={k}" + "".join(f"[sv{i}_{j}]" for j in range(k)))
        parts.append(f"[{i}:a]asplit={k}" + "".join(f"[sa{i}_{j}]" for j in range(k)))
        sub = []
        for j, (ks, ke) in enumerate(keeps):
            d = ke - ks
            parts.append(f"[sv{i}_{j}]trim=start={ks:.6f}:end={ke:.6f},setpts=PTS-STARTPTS,fps={FPS},"
                         f"scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p[pv{i}_{j}]")
            parts.append(f"[sa{i}_{j}]atrim=start={ks:.6f}:end={ke:.6f},asetpts=PTS-STARTPTS,"
                         f"aresample=48000,aformat=channel_layouts=stereo,volume={s['gain']:.2f}dB,"
                         f"afade=t=in:d=0.008,afade=t=out:st={max(0, d - 0.008):.4f}:d=0.008[pa{i}_{j}]")
            sub.append(f"[pv{i}_{j}][pa{i}_{j}]")
        vl = "v0pre" if i == 0 else f"v{i}"
        parts.append("".join(sub) + f"concat=n={k}:v=1:a=1[{vl}][a{i}]")
        if i == 0:
            # AI influencer clip starts right on "this" and ends on the hook clip's last frame.
            # Onset of "this" measured from the audio: 1.51s in the source (after the dip that ends "like").
            ds = max(0.0, POPUP_AT_SRC - keeps[0][0])
            ds = round(ds * FPS) / FPS
            parts.append(f"[{dance_idx}:v]trim=start=0:end=6,setpts=PTS-STARTPTS+{ds:.4f}/TB,fps={FPS},"
                         f"scale=320:569,setsar=1,format=yuv420p[dn]")
            parts.append(f"[v0pre][dn]overlay={POPUP_X}:{POPUP_Y}:shortest=1:enable='gte(t,{ds - 0.001:.4f})',format=yuv420p[v0]")
            print(f"pop-up starts at {ds:.3f}s (on 'this')")
        lab.append(f"[v{i}][a{i}]")
    parts.append("".join(lab) + f"concat=n={len(segs)}:v=1:a=1[v][a]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "10", "-pix_fmt", "yuv420p",
            "-c:a", "pcm_s16le", base]
    run(cmd)


def stage_b(segs, total, base, out, preview=None):
    # overlays
    layers = []  # (png, x, y, a, b)
    by = {s["name"].split("_")[-2] if s["name"].startswith("DJI") else s["name"][:8]: s for s in segs}
    hook_s, views_s, buzzy_s = by["0356"], by["0323"], by["IMG_8835"]
    payouts_s, cta_s = by["0341"], by["0342"]
    top = hook_png(f"{OV}/hook.png")
    t_after_intro = buzzy_s["t0"]
    layers.append((f"{OV}/hook.png", 0, top, 0.0, t_after_intro))
    cap_y = CAP_CENTER_Y - CAP_H // 2
    for k, s in enumerate(segs):
        for j, (text, a, b) in enumerate(s["caps"]):
            p = f"{OV}/cap_{k}_{j}.png"
            caption_png(text, p)
            layers.append((p, 0, cap_y, a, b))
    top_png(f"{OV}/cta.png")
    layers.append((f"{OV}/cta.png", 0, 40, cta_s["t0"], total))
    # 0323 tokens: 0 they're 1 actually 2 getting 3 millions 4 of 5 views 6 and 7 generating 8 thousands 9 of 10 dollars
    wt = views_s["wt"]
    card_png(f"{A}/views.jpg", f"{OV}/views.png")
    card_png(f"{A}/earnings.jpg", f"{OV}/earn.png")
    layers.append((f"{OV}/views.png", 300, 1290, wt[3][0], wt[5][1] + 0.1))
    layers.append((f"{OV}/earn.png", 300, 1290, wt[8][0], views_s["t0"] + views_s["d"]))
    # 0341 tokens: 0 now 1 all 2 you 3 need 4 to 5 do 6 is 7 post 8 consistently 9 to 10 get 11 payouts 12 like 13 this
    # Where he points at the top of the screen: card sits above his head, clear of the face.
    pw = payouts_s["wt"]
    card_png(f"{A}/earnings.jpg", f"{OV}/earn_top.png", width=420)
    layers.append((f"{OV}/earn_top.png", 330, 55, pw[11][0], payouts_s["t0"] + payouts_s["d"]))
    print(f"dance popup 0.00-{hook_s['d']:.2f} (baked into hook clip); "
          f"payouts card {pw[11][0]:.2f}-{payouts_s['t0'] + payouts_s['d']:.2f}")

    music_len = total + 1.0
    # levels
    def rms_of(path, t0, t1):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", path, "-vn",
                              "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
        a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
        return 20 * math.log10(float(np.sqrt((a ** 2).mean())) + 1e-9)
    m_rms = rms_of(f"{A}/music.mp3", MUSIC_START, MUSIC_START + total)
    # Metallic high riser (his upload): sound runs 1.2-3.0s in the file and stops dead at 3.0s.
    # Line that stop up with the cut into the screen section.
    RISER, RISER_ON, RISER_END = f"{A}/riser_metallic.mp4", 1.2, 3.0
    r_rms = rms_of(RISER, RISER_ON, RISER_END)
    m_gain = (VOICE_RMS_TARGET - 14.0) - m_rms
    r_gain = (VOICE_RMS_TARGET - 8.0) - r_rms
    print(f"music rms {m_rms:.1f} dB -> gain {m_gain:.1f}; riser rms {r_rms:.1f} dB -> gain {r_gain:.1f}")
    riser_start = max(0.0, t_after_intro - RISER_END)
    print(f"riser: file placed at {riser_start:.2f}s, audible {riser_start + RISER_ON:.2f}-{t_after_intro:.2f}s")

    cmd = ["ffmpeg", "-v", "error", "-stats", "-y", "-i", base, "-i", f"{A}/dance.mp4"]
    for l in layers:
        cmd += ["-i", l[0]]
    cmd += ["-i", f"{A}/music.mp3", "-i", RISER]
    n_layers = len(layers)
    mus_i = 2 + n_layers
    ris_i = mus_i + 1
    f = ["[0:v]null[o0]"]  # dance pop-up is already baked into the hook clip (see stage_a)
    prev = "o0"
    for k, (p, x, y, a, b) in enumerate(layers):
        nxt = f"o{k + 1}"
        # Half-frame shift + half-open interval, so an overlay never lingers a frame past a cut.
        f.append(f"[{prev}][{2 + k}:v]overlay={x}:{y}:enable='gte(t,{a - 0.017:.3f})*lt(t,{b - 0.017:.3f})'[{nxt}]")
        prev = nxt
    f.append(f"[{prev}]format=yuv420p[vout]")
    # Music opens on the hit (MUSIC_START), with only a 30 ms de-click fade so it lands immediately.
    f.append(f"[{mus_i}:a]atrim=start={MUSIC_START:.3f}:end={MUSIC_START + music_len:.2f},asetpts=PTS-STARTPTS,"
             f"aformat=channel_layouts=stereo,aresample=48000,volume={m_gain:.2f}dB,"
             f"afade=t=in:d=0.03,afade=t=out:st={total - 1.2:.2f}:d=1.2[mus]")
    f.append(f"[{ris_i}:a]aformat=channel_layouts=stereo,aresample=48000,volume={r_gain:.2f}dB,"
             f"adelay={int(riser_start * 1000)}|{int(riser_start * 1000)}[ris]")
    f.append(f"[0:a][mus][ris]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.97[aout]")
    cmd += ["-filter_complex", ";".join(f), "-map", "[vout]", "-map", "[aout]", "-t", os.environ.get("STAGEB_T", f"{total:.3f}")]
    if preview:
        pass
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    run(cmd)


def main():
    work, out = sys.argv[1], sys.argv[2]
    stage = "all"
    if "--stage" in sys.argv:
        stage = sys.argv[sys.argv.index("--stage") + 1]
    segs, total = make_plan()
    for s in segs:
        print(f"{s['name']:34s} t0={s['t0']:6.2f} d={s['d']:5.2f} level {s['level']:.1f}dB gain {s['gain']:+.1f} "
              f"keeps " + " ".join(f"{a:.3f}-{b:.3f}" for a, b in s["keeps"]))
        print("    " + " | ".join(f"{t}@{a:.2f}-{b:.2f}" for t, a, b in s["caps"]))
    print(f"total {total:.2f}s")
    json.dump([{k: v for k, v in s.items() if k not in ("wt", "words")} for s in segs],
              open(f"{work}/plan.json", "w"), indent=1)
    base = f"{work}/base.mkv"
    if stage in ("A", "all"):
        stage_a(segs, base)
    if stage in ("B", "all"):
        stage_b(segs, total, base, out)


if __name__ == "__main__":
    main()
