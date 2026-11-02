"""Build your pixel font from glyphs.json (the one source).

Writes <Name>-Regular.ttf and .woff2, named from "name" in glyphs.json. Edit the JSON (draw script or pixel editor), never the exports.

One em = 20 cells = 1000 units, one cell = 50 units: crisp at 20, 40, 80, 120 px.
Thai marks are zero width and drawn right-aligned over the letter before, so they land right
with no shaping at all. GPOS (thai and DFLT) adds what plain placement can't:
  mark  upper marks and tones move left past a tail flick (ช ซ ศ ษ ส ฮ, 2 cells) or an ascender (ป ฝ ฟ ฬ, 3)
        lower vowels drop 3 rows under letters with a descender (ฎ ฏ ฐ ญ ฤ ฦ)
  mkmk  a tone after an upper vowel or nikhahit rises 3 rows (8..9 -> 11..12)
This replaces the 2005-era trick of swapping marks for private-use variants, which modern browsers break.

python3 build.py
"""
import json
import re
from pathlib import Path

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import woff2

HERE = Path(__file__).resolve().parent
SRC = HERE / "glyphs.json"
UNIT = 50
ASC, DESC = 13 * UNIT, -7 * UNIT
SHIFT = {**dict.fromkeys("ชซศษสฮ", 2), **dict.fromkeys("ปฝฟฬ", 3)}  # cells left: clear the tail flick / ascender
DROP = set("ฎฏฐญฤฦ")
UPPER = "ัิีึื็ํ"
TONE = "่้๊๋์๎"
LOWER = "ฺุู"
TRACK = 1  # default letter spacing in cells, added to every letter (half each side); glyphs.json "track" overrides
ATTACH_LEFT = set("ำ")  # its ring sits over the letter before: keep it there, add spacing on its right only


def stem(name):
    """File and PostScript name: the font name in ASCII letters and digits, plus -Regular (the editor does the same)."""
    return (re.sub(r"[^A-Za-z0-9]", "", name) or "PixelFont") + "-Regular"


def offset(c, track):
    """Font units to move a letter right inside its wider box: half the spacing, or back by half for ำ."""
    return (-1 if c in ATTACH_LEFT else 1) * track * UNIT // 2

def contours(px):
    """Union of pixels -> closed outlines (clockwise outer, counter-clockwise holes)."""
    edges = {}
    for x, y in px:
        for a, b in (((x, y), (x, y + 1)), ((x, y + 1), (x + 1, y + 1)), ((x + 1, y + 1), (x + 1, y)), ((x + 1, y), (x, y))):
            if (b, a) in edges:
                del edges[(b, a)]
            else:
                edges[(a, b)] = True
    nxt = {}
    for a, b in edges:
        nxt.setdefault(a, []).append(b)
    loops = []
    while nxt:
        start = next(iter(nxt))
        loop, cur, prev = [start], start, None
        while True:
            outs = nxt[cur]
            if len(outs) > 1 and prev is not None:  # pinch point: turn right to keep shapes apart
                din = (cur[0] - prev[0], cur[1] - prev[1])
                outs.sort(key=lambda b: -(din[0] * (b[1] - cur[1]) - din[1] * (b[0] - cur[0])))
            b = outs.pop(0)
            if not outs:
                del nxt[cur]
            prev, cur = cur, b
            if cur == start:
                break
            loop.append(cur)
        pts = [p for i, p in enumerate(loop)
               if (loop[i - 1][0] - p[0]) * (loop[(i + 1) % len(loop)][1] - p[1])
               != (loop[i - 1][1] - p[1]) * (loop[(i + 1) % len(loop)][0] - p[0])]
        loops.append(pts)
    return loops


def gname(ch):
    return "space" if ch == " " else "uni%04X" % ord(ch)


def outline(g, off=0):
    top = g["y"] + len(g["px"]) - 1
    px = {(g["x"] + k, top - r) for r, row in enumerate(g["px"]) for k, v in enumerate(row) if v == "#"}
    pen = TTGlyphPen(None)
    for loop in contours(px):
        pen.moveTo((loop[0][0] * UNIT + off, loop[0][1] * UNIT))
        for x, y in loop[1:]:
            pen.lineTo((x * UNIT + off, y * UNIT))
        pen.closePath()
    return pen.glyph()


def features(glyphs, track):
    marks = [c for c in glyphs if glyphs[c].get("mark")]
    bases = [c for c in glyphs if c not in marks and c != " "]
    cls = lambda chars: "[" + " ".join(gname(c) for c in chars if c in glyphs) + "]"
    lines = ["languagesystem DFLT dflt;", "languagesystem thai dflt;",
             f"markClass {cls(UPPER)} <anchor 0 0> @UPPER;",
             f"markClass {cls(TONE)} <anchor 0 0> @TONE;",
             f"markClass {cls(LOWER)} <anchor 0 0> @LOWER;",
             "feature mark {"]
    for c in bases:
        adv = glyphs[c]["w"] * UNIT + offset(c, track)  # marks sit where the letter's ink is, not at its wider box
        top = adv - SHIFT.get(c, 0) * UNIT
        low = -3 * UNIT if c in DROP else 0
        lines.append(f"  pos base {gname(c)} <anchor {top} 0> mark @UPPER <anchor {top} 0> mark @TONE"
                     f" <anchor {adv} {low}> mark @LOWER;")
    lines += ["} mark;", "feature mkmk {", f"  pos mark {cls(UPPER)} <anchor 0 {3 * UNIT}> mark @TONE;", "} mkmk;",
              "table GDEF {", f"  GlyphClassDef {cls(bases)}, , {cls(marks)}, ;", "} GDEF;"]
    return "\n".join(lines)


def main():
    data = json.loads(SRC.read_text("utf-8"))
    glyphs = data["glyphs"]
    name = data.get("name") or "My Pixel Font"
    OUT = HERE / (stem(name) + ".ttf")
    track = data.get("track", TRACK)
    order = [".notdef"] + [gname(c) for c in glyphs]
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap({ord(c): gname(c) for c in glyphs})
    notdef = TTGlyphPen(None)
    for x0, y0, x1, y1 in ((0, 0, 300, 350), (50, 50, 250, 300)):
        notdef.moveTo((x0, y0)); notdef.lineTo((x0, y1)); notdef.lineTo((x1, y1)); notdef.lineTo((x1, y0)); notdef.closePath()
    shapes, metrics = {".notdef": notdef.glyph()}, {".notdef": (350, 0)}
    for c, g in glyphs.items():
        spaced = g["w"] > 0
        shapes[gname(c)] = outline(g, offset(c, track) if spaced else 0)
        extra = track * UNIT if spaced and c not in ATTACH_LEFT else 0
        metrics[gname(c)] = (g["w"] * UNIT + extra, g["x"] * UNIT if g["px"] else 0)
    fb.setupGlyf(shapes)
    for name in order:
        fb.font["glyf"][name].recalcBounds(fb.font["glyf"])
        metrics[name] = (metrics[name][0], getattr(fb.font["glyf"][name], "xMin", 0))
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASC, descent=DESC)
    fb.setupOS2(sTypoAscender=ASC, sTypoDescender=DESC, sTypoLineGap=0, usWinAscent=ASC, usWinDescent=-DESC,
                sxHeight=7 * UNIT, sCapHeight=8 * UNIT, fsType=0, ulUnicodeRange1=1 | (1 << 24))
    fb.setupNameTable({
        "familyName": name, "styleName": "Regular",
        "copyright": data.get("copyright", "Drawn by hand in Thai Pixel Font Editor."),
        "uniqueFontIdentifier": stem(name) + "-0.1", "version": "Version 0.100",
        "psName": stem(name),
    })
    fb.setupPost()
    addOpenTypeFeaturesFromString(fb.font, features(glyphs, track))
    fb.save(OUT)
    woff2.compress(str(OUT), str(OUT.with_suffix(".woff2")))
    print(f"{len(glyphs)} glyphs -> {OUT.name}, {OUT.with_suffix('.woff2').name}")


if __name__ == "__main__":
    main()
