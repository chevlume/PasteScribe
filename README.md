# PasteScribe

🇬🇧 English · 🇪🇸 [Español](README.es.md)

Types text you paste **letter by letter**, as if you were typing it yourself. Two versions:

| | Where it types | Folder |
|---|---|---|
| **Desktop app** | Into any program, window or form on your computer that has focus | [`desktop-app/`](desktop-app) |
| **Chrome extension** | Only into the tab that is open in the browser at that moment | [`chrome-extension/`](chrome-extension) |

## Desktop app (Windows, macOS, Linux/X11)

The interface is in **English by default**; switch to Spanish with the *Language* selector in the window (your choice is remembered).

### Windows: a single `.exe`, no console window

Build it once on your Windows PC (needs Python 3.9+ installed):

1. Double-click **`desktop-app\build_windows.bat`**. It installs what it needs, builds and self-tests the app.
2. Take **`desktop-app\dist\PasteScribe.exe`** and copy it wherever you like (e.g. your desktop). Double-click it: it opens **without a console window**.

No Windows PC at hand? Open the *Actions* tab on GitHub → *Build Windows exe* → *Run workflow*, then download `PasteScribe-windows` from the run's *Artifacts*.

Heads-up: the `.exe` is not code-signed, so Windows SmartScreen may show "Windows protected your PC" (click *More info* → *Run anyway*), and some antivirus programs flag any program that types keys for you (a false positive). If an error happens, the details are saved in `%USERPROFILE%\.pastescribe.log`.

### Run it from source (any system)

Requirements: Python 3.9+ with `tkinter` and `pynput`.

```bash
cd desktop-app
python -m pip install -r requirements.txt
python pastescribe.py
```

On Windows you can also double-click `iniciar_windows.bat`, which installs the dependencies and opens the app (no console window left open).

### Using it

1. Paste your text into the window (Ctrl+V / Cmd+V, or *Paste from clipboard*).
2. Set the pause between letters, the countdown, and whether you want irregular pauses (random variation).
3. Press **Start** and, during the countdown, **click the target field** (in any application).
4. It starts typing. **Esc** (system-wide) or the *Stop* button stops it instantly.

Safety:
- **Line breaks** (default: *Turn into a space*): pressing Enter in a search box or form submits it and breaks the typing. Choose *Press Enter* only for multi-line fields (editors, `textarea`).
- If you switch windows while it types (Alt+Tab, or another window grabbing focus), typing stops by itself (Windows only).
- On Windows, Esc is detected by polling the keyboard, without hooking the system's input.
- If something gets out of hand: Esc; if the system doesn't respond, close the app from Task Manager (Ctrl+Shift+Esc).

Notes:
- **macOS**: grant your terminal/Python *Accessibility* and *Input Monitoring* permissions (System Settings → Privacy & Security), otherwise the system ignores the keystrokes.
- **Linux**: works on X11. Under Wayland, programs cannot inject keystrokes into other windows; use an Xorg session.
- Tabs are typed as the Tab key (in a web form, Tab moves to the next field) and, with *Press Enter*, a code editor's auto-indent can add extra spaces.
- The minimum pause between letters is 10 ms (5 ms in the extension). With no pause, the system receives thousands of keystrokes at once: the text appears "in a block", the target program keeps typing after PasteScribe has finished, and Esc cannot stop it.
- On Linux, if you type many unusual characters at once, use a pause of **30 ms or more** (default 60 ms).

## Chrome extension (Manifest V3)

The interface is in **English by default**; switch to Spanish with the EN/ES selector in the panel (your choice is remembered).

Install (developer mode):

1. Open `chrome://extensions` and turn on **Developer mode**.
2. **Load unpacked** → choose the `chrome-extension/` folder.

Use:

1. Click the field on the page where you want to type (text box, `textarea`, password field or `contenteditable` editor).
2. Open the extension, paste your text, adjust the speed and press **Type**. The panel closes and typing begins.
3. If no field was focused, the extension waits (up to 60 s) for you to click one.
4. **Esc** on the page, the *Stop* button of the on-screen notice, or *Stop* in the panel, stops it. If the field loses focus, typing stops so it doesn't type where it shouldn't.

Privacy: it only acts on the active tab when you press the icon (`activeTab` permission), sends nothing to any server, and your text is only kept for the browser session. Permissions: `activeTab`, `scripting`, `storage`.

Limitations:
- It does not work on internal pages (`chrome://…`, the Chrome Web Store) or in cross-origin iframes.
- Editors that draw their own text (e.g. Google Docs) don't use standard text fields and may ignore it.
- In single-line fields, line breaks are turned into spaces.
- Draft.js editors (such as X's post box) get each character as a paste event instead of normal typing, because they break when the browser edits their text directly. This is tested against a real Draft.js editor locally, not against x.com itself. If a site misbehaves, the desktop app works everywhere.

## Publishing to the Chrome Web Store

All the material is ready; you only need your developer account. The listing texts, permission justifications and privacy answers are in [`CHROMEWEBSTORE.md`](CHROMEWEBSTORE.md) (English and Spanish listings).

1. Put your email in [`docs/privacy-policy.en.md`](docs/privacy-policy.en.md) (English) and [`docs/privacy-policy.md`](docs/privacy-policy.md) (Spanish) and publish them at a **public URL** (for example, the same file on GitHub if the repository is public, or a public Gist).
2. Build the package: `tools/package_extension.sh` (creates `dist/pastescribe-v<version>.zip`). Without Bash, zip **the contents** of `chrome-extension/` (so `manifest.json` is at the root of the ZIP).
3. Go to the [Developer Dashboard](https://chrome.google.com/webstore/devconsole), accept the agreement and pay the one-time registration fee (US$5).
4. *New item* → upload the ZIP → complete *Store listing*, *Privacy* and *Distribution* as `CHROMEWEBSTORE.md` indicates. Images are in `store-assets/en/` and `store-assets/es/` (regenerate with `LANG_UI=en node tools/make_store_assets.js`). The extension is translated into English (default) and Spanish.
5. *Submit for review*. A first review usually takes 1–3 business days.

For each update: bump `version` in `chrome-extension/manifest.json`, rebuild the ZIP and upload it as a new version.

## Tests

```bash
cd desktop-app && python -m unittest discover -s tests     # typing engine, translations, window logic
xvfb-run -a python tests/gui_real_test.py                  # the real window (needs tkinter + an X server; Linux)
npm i playwright && LANG_UI=en node tests/extension/content.test.js && LANG_UI=es node tests/extension/content.test.js   # content script in Chromium
```

Draft.js editor regression test (X's post box uses Draft.js): `cd tests/extension/draft && npm install && npm test`.

`python tools/make_icons.py` regenerates the extension icons.
