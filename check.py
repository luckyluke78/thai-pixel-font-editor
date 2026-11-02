"""Check the font: zones, look-alike distances, and a proof page for headless Chrome.

Look-alike rule for this grid: two letters differ in at least MIN cells at their best overlap
(slide ±2 columns). Pairs where a letter is still blank are skipped.

python3 check.py            # report; exit 1 on a failing pair
python3 check.py --proof    # also write the proof page and render it with Chrome
"""
import json
import subprocess
import sys
from pathlib import Path

from build import stem

HERE = Path(__file__).resolve().parent
SRC = HERE / "glyphs.json"
MIN = 3
PAIRS = ["คด", "ดต", "คฅ", "ขฃ", "ถภ", "ดถ", "คถ", "บป", "บน", "ขบ", "ขช", "ชซ", "ผพ", "พฟ", "ผฝ", "ฎฏ", "ฒพ",
         "ศส", "ลส", "อฮ", "มน", "รจ", "วจ", "ทภ", "ทบ", "ยบ", "ทฑ", "หฬ", "ณฌ", "ณญ", "ฤถ", "ฦภ", "ฐร", "ฆม",
         "ใไ", "โไ", "๐o", "อo", "กn", "0O", "1I", "Il", "1l", "5S", "2Z", "6G", "8B"]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
WORDS = ["สวัสดีครับ ฟอนต์ของฉัน", "ปั้น กี่ ญี่ปุ่น ฐาน น้ำ", "ป่า ฝั่ง ฟื้น ปี่ ฎีกา ฎุ ญู ส้ม ช่วย",
         "กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธน", "บปผฝพฟภมยรฤลฦวศษสหฬอฮ ะาำเแโใไๆฯ",
         "Hello pixel font. 0O 1Il 5S 2Z", "๐๑๒๓๔๕๖๗๘๙ 2026 ฿100 100%"]


def cells(g):
    top = g["y"] + len(g["px"]) - 1
    return {(top - r, g["x"] + c) for r, row in enumerate(g["px"]) for c, v in enumerate(row) if v == "#"}


def distance(a, b):
    A, B = cells(a), cells(b)
    return min(len(A ^ {(r, c + dx) for r, c in B}) for dx in range(-2, 3))


def main():
    glyphs = json.loads(SRC.read_text("utf-8"))["glyphs"]
    fails = []
    out = []
    for p in PAIRS:
        if p[0] in glyphs and p[1] in glyphs and glyphs[p[0]]["px"] and glyphs[p[1]]["px"]:
            d = distance(glyphs[p[0]], glyphs[p[1]])
            out.append(f"{p[0]}/{p[1]} {d}")
            if d < MIN:
                fails.append(p)
    print("look-alike distance (cells): " + " · ".join(out))
    shapes = {}
    for c, g in glyphs.items():
        if g["px"]:
            shapes.setdefault(frozenset(cells(g)), []).append(c)
    same = [v for v in shapes.values() if len(v) > 1]
    print("identical shapes:", same or "none")
    print("FAIL:" if fails else "all pairs >=", " ".join(fails) if fails else MIN)
    if "--proof" in sys.argv:
        html = HERE / "proof.html"
        lines = "".join(f"<p>{w}</p>" for w in WORDS)
        html.write_text(
            "<!doctype html><meta charset=utf-8><style>@font-face{font-family:F;src:url(" + stem(json.loads(SRC.read_text("utf-8")).get("name") or "My Pixel Font") + ".ttf)}"
            "body{margin:0;padding:24px;background:#fff;color:#1A1714;font-family:F;font-size:80px;line-height:1.75;"
            "background-image:linear-gradient(#e8eefa 1px,transparent 1px),linear-gradient(90deg,#e8eefa 1px,transparent 1px);"
            "background-size:4px 4px}p{margin:0;white-space:nowrap}</style>" + lines + "\n", "utf-8")
        png = HERE / "proof.png"
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--window-size=2400,1080",
                        f"--screenshot={png}", html.as_uri()], capture_output=True)
        print("proof:", png.name)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
