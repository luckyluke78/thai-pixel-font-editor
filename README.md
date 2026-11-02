# Thai Pixel Font Editor

ทำฟอนต์พิกเซลภาษาไทยของคุณเอง แค่คลิกทีละช่อง แล้วกด Export ได้ไฟล์ฟอนต์ไปใช้ใน Keynote, Canva, Figma หรือ Word ได้ทันที ใช้ฟรี (MIT)

Make your own Thai and Latin pixel font by clicking pixels, then export a real font file for Keynote, Canva, Figma or Word. Free (MIT).

---

## ภาษาไทย

### 1. วางข้อความนี้ใน Claude Code เพื่อติดตั้ง

เปิด Claude Code แล้ววางข้อความทั้งก้อนนี้ลงไป:

```text
ช่วยติดตั้ง Thai Pixel Font Editor ให้หน่อย:
1. clone https://github.com/luckyluke78/thai-pixel-font-editor ไว้ในโฟลเดอร์ Documents
2. ติดตั้ง Python packages: fonttools brotli pillow
3. เปิด server.py ในโฟลเดอร์นั้นแล้วเปิด http://127.0.0.1:8720 ใน Chrome ให้ฉัน
```

### 2. เริ่มใช้!

- เลือกตัวอักษรจากรายการด้านซ้าย แล้ว **คลิก** ช่องเพื่อเติมพิกเซล คลิกซ้ำเพื่อลบ **ลาก** เพื่อระบายหลายช่อง **Shift-ลาก** เพื่อลบ **⌘Z** ย้อนกลับ
- **← → ↑ ↓** เลื่อนทั้งตัวอักษร **[ ]** ปรับความกว้าง
- **Select (V)** ลากกรอบเลือกพิกเซลบางส่วน (หรือ **⌘A** เลือกทั้งหมด) แล้วลากหรือกดลูกศรเพื่อย้าย
- ตั้งชื่อฟอนต์ในช่อง **Font name** ด้านบน
- กด **Export font (.ttf)** ได้ไฟล์ฟอนต์ ดับเบิลคลิกเพื่อติดตั้ง แล้วเลือกใช้ในแอปไหนก็ได้
- ทุกการแก้ไขบันทึกเองและสร้างฟอนต์ใหม่ภายในประมาณ 1 วินาที ดูผลจริงได้ในกล่อง **Real font** ด้านล่าง

ครั้งต่อไปที่จะใช้ บอก Claude Code ว่า "เปิด Thai Pixel Font Editor" หรือพิมพ์ใน Terminal:

```bash
cd ~/Documents/thai-pixel-font-editor && python3 server.py
```

---

## English

### 1. Paste this into Claude Code to install

Open Claude Code and paste this whole block:

```text
Please install Thai Pixel Font Editor for me:
1. Clone https://github.com/luckyluke78/thai-pixel-font-editor into my Documents folder
2. Install the Python packages fonttools brotli pillow
3. Start server.py in that folder and open http://127.0.0.1:8720 in Chrome for me
```

### 2. Run!

- Pick a letter in the list. **Click** a cell to add a pixel, click again to remove it. **Drag** to paint, **Shift-drag** to erase, **⌘Z** to undo.
- **← → ↑ ↓** move the whole letter; **[ ]** set its width.
- **Select (V)**: drag a box round some pixels (or **⌘A** for all), then drag them or use the arrow keys to move them.
- Name your font in the **Font name** box at the top.
- **Export font (.ttf)** downloads the font. Double-click it to install, then pick it in any app.
- Every change saves itself and rebuilds the font in about a second; the **Real font** box at the bottom shows it.

Next time, tell Claude Code "open Thai Pixel Font Editor", or run in Terminal:

```bash
cd ~/Documents/thai-pixel-font-editor && python3 server.py
```

---

## How it works

- `glyphs.json` is the font: every glyph as rows of `#` and `.`. It starts blank (172 Thai and Latin glyphs). Everything else is built from it.
- One em = 20 cells = 1000 units, so the font is pixel-sharp at 20, 40, 80 and 120 px. Coloured lines in the editor mark the baseline, the body top (row 7), upper vowels (8), a tone over a vowel (11) and lower vowels (−2).
- Thai vowels and tones (zero-width marks) show over a grey ghost letter. `build.py` adds OpenType mark positioning so they stack right in modern apps and browsers.
- Every letter gets 1 cell of spacing when the font is built; change it with `"track"` in `glyphs.json`.
- The look-alike check (under the buttons) turns red when two similar letters (ด/ต, บ/ป, 0/O…) differ by fewer than 3 pixels.

| File | Job |
|---|---|
| `glyphs.json` | The font itself, the one source |
| `server.py` | Local server on 127.0.0.1: the editor, autosave, rebuild, check |
| `editor.html` | The click editor |
| `build.py` | `glyphs.json` → `.ttf` and `.woff2` with Thai mark positioning |
| `check.py` | Look-alike distances; `--proof` renders a proof page in Chrome |
| `sheet.py` | `sheet.png`: every glyph on its grid, for review by eye |

## License

MIT. See [LICENSE](LICENSE). The fonts you draw are yours.
