"""Zoom sheet of every glyph, for review by eye.

Each glyph sits on its cell grid with the zones tinted (body, upper marks, raised tones, lower
vowels, descenders), the baseline in orange and the advance in grey. Marks are shown over a
ghost ก so their place is visible. Look-alike pairs get their own row, side by side.

python3 sheet.py [--cell 12]
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SRC = HERE / "glyphs.json"
OUT = HERE / "sheet.png"
C = int(sys.argv[sys.argv.index("--cell") + 1]) if "--cell" in sys.argv else 12
TOP, BOT = 12, -7
LABEL = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", max(12, C + 4))
TITLE = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", max(16, C + 10))
INK, GHOST, BASE = (26, 23, 20), (205, 200, 195), (250, 90, 20)
ZONES = [((0, 6), (255, 244, 236)), ((8, 9), (238, 247, 232)), ((11, 12), (245, 236, 252)),
         ((-4, -2), (253, 246, 220)), ((-7, -5), (250, 240, 214))]
SECTIONS = [
    ("Thai consonants", "กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤลฦวศษสหฬอฮ"),
    ("Thai vowels and signs", "ะาำเแโใไๅๆฯ฿"),
    ("Marks (over a ghost ก)", "ัิีึื็ํ่้๊๋์๎ฺุู"),
    ("Thai digits", "๐๑๒๓๔๕๖๗๘๙"),
    ("Latin capitals", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    ("Latin lowercase", "abcdefghijklmnopqrstuvwxyz"),
    ("Digits and punctuation", "0123456789.,:;!?-_'\"()/%&+=@#*<>[]|"),
    ("Look-alike pairs", "คด ดต คฅ ขฃ ขช ชซ บป บน ขบ ถภ ทบ ทฑ ผพ พฟ ฎฏ ศส ลส อฮ ใไ กn อo ๐o 0O 1Il 5S 8B"),
]


def cells(g):
    top = g["y"] + len(g["px"]) - 1
    return {(top - r, g["x"] + c) for r, row in enumerate(g["px"]) for c, v in enumerate(row) if v == "#"}


def tile(ch, glyphs):
    g = glyphs[ch]
    ghost = set()
    adv = g["w"]
    if g.get("mark"):
        base = glyphs["ก"]
        adv = base["w"]
        ghost = cells(base)
        ink = {(r, c + adv) for r, c in cells(g)}
    else:
        ink = cells(g)
    cols = [c for _, c in ink | ghost] or [0]
    c0, c1 = min(min(cols), 0) - 1, max(max(cols) + 1, adv) + 1
    im = Image.new("RGB", ((c1 - c0) * C, (TOP - BOT + 1) * C + C * 2 + 4), "white")
    d = ImageDraw.Draw(im)
    for r in range(BOT, TOP + 1):
        for c in range(c0, c1):
            fill = next((col for (a, b), col in ZONES if a <= r <= b), (255, 255, 255))
            if not 0 <= c < adv:
                fill = tuple(int(v * 0.94) for v in fill)
            if (r, c) in ink:
                fill = INK
            elif (r, c) in ghost:
                fill = GHOST
            x, y = (c - c0) * C, (TOP - r) * C
            d.rectangle([x, y, x + C - 1, y + C - 1], fill=fill, outline=(226, 226, 226))
    y0 = (TOP + 1) * C
    d.line([(0, y0), (im.width, y0)], fill=BASE, width=2)
    label = f"{ch} {g['w']}" if not g.get("mark") else f"◌{ch}"
    d.text((2, (TOP - BOT + 1) * C + 2), label, font=LABEL, fill=(60, 56, 52))
    return im


def main():
    glyphs = json.loads(SRC.read_text("utf-8"))["glyphs"]
    width, gap = 2400, C
    blocks = []
    for title, chars in SECTIONS:
        tiles = []
        for ch in chars:
            if ch == " ":
                tiles.append(None)
            elif ch in glyphs:
                tiles.append(tile(ch, glyphs))
        rows, cur, w = [], [], 0
        for t in tiles:
            tw = (t.width if t else C * 3) + gap
            if w + tw > width - 2 * gap:
                rows.append(cur)
                cur, w = [], 0
            cur.append(t)
            w += tw
        rows.append(cur)
        th = (TOP - BOT + 1) * C + C * 2 + 4
        sec = Image.new("RGB", (width, C * 3 + len(rows) * (th + gap)), "white")
        d = ImageDraw.Draw(sec)
        d.text((gap, 4), title, font=TITLE, fill=INK)
        for i, row in enumerate(rows):
            x = gap
            for t in row:
                if t:
                    sec.paste(t, (x, C * 3 + i * (th + gap)))
                x += (t.width if t else C * 3) + gap
        blocks.append(sec)
    sheet = Image.new("RGB", (width, sum(b.height for b in blocks)), "white")
    y = 0
    for b in blocks:
        sheet.paste(b, (0, y))
        y += b.height
    sheet.save(OUT)
    print(f"{OUT.name}: {sheet.width}x{sheet.height}, {C} px per cell")


if __name__ == "__main__":
    main()
