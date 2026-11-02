# Thai Pixel Font Editor · for Claude Code

The user wants to draw their own pixel font. Most users are not programmers: do the setup for them, in plain words, in their language (Thai if they write Thai).

## Install and run (when the user pastes the GitHub link or says "run", "open", "เปิด", "ติดตั้ง")
1. If this folder isn't on their computer yet: `git clone https://github.com/luckyluke78/thai-pixel-font-editor ~/Documents/thai-pixel-font-editor`, then work in that folder.
2. Start the editor in the background: `python3 server.py`. The first run makes `.venv/` and installs fontTools, brotli and pillow there (about a minute, nothing system-wide), builds the font, then opens http://127.0.0.1:8720 in the browser. Leave it running.
3. Tell the user it's open and how to start: pick a letter, click cells to draw, set the name in **Font name**, press **Export font (.ttf)** and double-click the file to install it.

If `python3` is missing, tell the user to install Python 3 from python.org (on a Mac, `xcode-select --install` also gives it) and try again. If port 8720 is taken, the editor is already running: the server opens the browser on it and exits. Another port: `PORT=8730 python3 server.py`.

## Rules
- `glyphs.json` is the font and the one source; the server writes it on every click. Don't edit it while the server runs; stop the server first.
- Never delete the user's `glyphs.json`, and never reset or overwrite their drawn glyphs. Before a risky change, copy it to `glyphs-backup-YYYY-MM-DD.json`.
- The `.ttf` and `.woff2` files are built output: rebuild with `.venv/bin/python build.py`, never edit them.
- The server listens on 127.0.0.1 only. Use `HOST=0.0.0.0` (phone or iPad on the same Wi-Fi) only when the user asks, and say that anyone on that Wi-Fi can reach it.
