"""The permanent caption style. Every video uses this module; never restyle captions by hand.

Measured off the opening captions of his finished edit `Footage/Example Video/1117 (2).mp4`:
  - one line, white text, thick black outline, no drop shadow
  - font: Lato Bold, 92 px (best match of 15 free fonts to the opening's letter shapes, IoU 0.75;
    Montserrat scored lowest, 0.58, and looked visibly wider)
  - outline: black, 4 px
  - all lowercase, no punctuation, numbers spelled out ("a five thousand dollar course")
  - 1-3 words per caption (4 only when they are all short, e.g. "let me show you"), never wider than ~860 px
  - a caption appears on its first word and holds until the next caption starts
  - text baseline at y = 1325 on a 1080x1920 frame (below the chin); close-up clips use 1610
See .claude/skills/captions/SKILL.md for the full recipe and checks.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = 1080
CAP_H = 200            # caption canvas height
BASELINE = 130         # baseline position inside the canvas
FONT_SIZE = 92
STROKE = 4
MAX_WIDTH = 860        # px, keeps a caption well inside the frame
MAX_WORDS = 4
BASELINE_Y = 1325      # where the baseline lands on the frame for normal footage
BASELINE_Y_CLOSEUP = 1610   # when his face/chin/mic sit low (close-ups)
OVERLAY_Y = BASELINE_Y - BASELINE            # y to overlay a caption canvas at
OVERLAY_Y_CLOSEUP = BASELINE_Y_CLOSEUP - BASELINE

LEADS = {"a", "an", "the", "of", "to", "my", "your", "and", "in", "on", "at", "for", "with", "or", "so",
         "you", "i", "it", "that", "this", "is", "are", "if", "then", "its", "our", "his", "her",
         "by", "from", "into", "about", "as", "up", "down", "out", "over", "but", "than", "how", "what",
         "when", "because", "go", "come", "tell", "give", "put", "let", "can", "will", "want", "get"}
NUMBER_WORDS = {"$5,000": "five thousand dollars", "5,000": "five thousand", "$500": "five hundred dollars",
                "$3,500": "thirty five hundred dollars", "$15,000": "fifteen thousand dollars",
                "9m": "nine million", "30": "thirty", "14": "fourteen", "40": "forty", "5": "five", "2": "two"}


def _font_path():
    for p in (os.environ.get("CAPTION_FONT"),
              os.path.join(os.environ.get("EDIT_WORKDIR", "work"), "fonts", "Lato-Bold.ttf"),
              "fonts/Lato-Bold.ttf"):
        if p and os.path.exists(p):
            return p
    raise FileNotFoundError("Lato-Bold.ttf missing: `npm pack @fontsource/lato`, take "
                            "files/lato-latin-700-normal.woff2 and convert it to TTF with fontTools "
                            "(see .claude/skills/captions/SKILL.md)")


_font_cache = {}


def font():
    if "f" not in _font_cache:
        _font_cache["f"] = ImageFont.truetype(_font_path(), FONT_SIZE)
    return _font_cache["f"]


def text_width(text):
    f = font()
    return f.getlength(text)


def clean(token):
    t = token.strip().lower().strip(".,!?\"")
    return NUMBER_WORDS.get(t, t)


def render(text, path):
    """One caption PNG (1080x200, transparent). Overlay it at y = OVERLAY_Y (or OVERLAY_Y_CLOSEUP)."""
    img = Image.new("RGBA", (W, CAP_H), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((W // 2, BASELINE), text, font=font(), fill=(255, 255, 255, 255),
                             stroke_width=STROKE, stroke_fill=(0, 0, 0, 255), anchor="ms")
    img.save(path)


def group_captions(words, display_tokens):
    """words: whisper words [{'w','s','e'}]. display_tokens: bai.display_tokens(words) -> [(text, first, last)].
    Returns [(caption text, first word index, last word index)] in the opening-caption style."""
    toks = [(clean(t), a, b) for t, a, b in display_tokens(words)]
    # break phrases at commas / sentence ends so a caption never spans one
    phrases, cur = [], []
    for tok in toks:
        cur.append(tok)
        if words[tok[2]]["w"].strip().endswith((",", ".", "?", "!")):
            phrases.append(cur)
            cur = []
    if cur:
        phrases.append(cur)
    out = []
    for ph in phrases:
        n = len(ph)
        best = [0.0] + [math.inf] * n
        how = [0] * (n + 1)
        for i in range(1, n + 1):
            for k in range(1, min(MAX_WORDS, i) + 1):
                grp = ph[i - k:i]
                text = " ".join(t for t, _, _ in grp)
                wd = text_width(text)
                if wd > MAX_WIDTH and k > 1:
                    continue
                cost = best[i - k] + 1.0                          # every caption costs a little: fewer is better
                cost += {1: 1.2, 2: 0.0, 3: 0.1, 4: 2.2}[k]     # prefer 2-3 words (the opening's rhythm)
                if grp[-1][0] in LEADS:
                    cost += 2.6                                   # avoid ending a caption on "of / to / the ..."
                if k == 1 and i == n and n > 1:
                    cost += 0.8                                   # avoid a lone last word
                if cost < best[i]:
                    best[i], how[i] = cost, k
        i, groups = n, []
        while i > 0:
            groups.append(ph[i - how[i]:i])
            i -= how[i]
        for g in reversed(groups):
            out.append((" ".join(t for t, _, _ in g), g[0][1], g[-1][2]))
    return out
