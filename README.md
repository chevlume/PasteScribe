# PasteScribe

🇬🇧 English · 🇪🇸 [Español](README.es.md)

Types text you paste **letter by letter**, as if you were typing it yourself. Two versions:

| | Where it types | Folder |
|---|---|---|
| **Desktop app** | Into any program, window or form on your computer that has focus | [`desktop-app/`](desktop-app) |
| **Chrome extension** | Only into the tab that is open in the browser at that moment | [`chrome-extension/`](chrome-extension) |

## Desktop app (Windows, macOS, Linux/X11)

The interface is in **English by default**; switch to Spanish with the *Language* selector in the window (your choice is remembered).

### Windows

Download **`PasteScribe.exe`** from the [Releases](https://github.com/chevlume/PasteScribe/releases) page and double-click it. It is a single file and opens **without a console window**.

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
- **Line breaks** (default: *Turn into a space*): pressing Enter in a search box or form submits it and breaks the typing. Choose *Press Enter* only for multi-line fields (editors, text areas).
- If you switch windows while it types (Alt+Tab, or another window grabbing focus), typing stops by itself (Windows only).
- If something gets out of hand: Esc; if the system doesn't respond, close the app from Task Manager (Ctrl+Shift+Esc).

Notes:
- **macOS**: grant your terminal/Python *Accessibility* and *Input Monitoring* permissions (System Settings → Privacy & Security), otherwise the system ignores the keystrokes.
- **Linux**: works on X11. Under Wayland, programs cannot inject keystrokes into other windows; use an Xorg session.
- Tabs are typed as the Tab key (in a web form, Tab moves to the next field) and, with *Press Enter*, a code editor's auto-indent can add extra spaces.
- The minimum pause between letters is 10 ms (5 ms in the extension): with no pause, the system receives thousands of keystrokes at once and the text appears in a block that can't be stopped.
- On Linux, if you type many unusual characters at once, use a pause of **30 ms or more** (default 60 ms).

## Chrome extension (Manifest V3)

The interface is in **English by default**; switch to Spanish with the EN/ES selector in the panel (your choice is remembered).

Install (developer mode):

1. Open `chrome://extensions` and turn on **Developer mode**.
2. **Load unpacked** → choose the `chrome-extension/` folder.

Use:

1. Click the field on the page where you want to type (text box, text area, password field or rich-text editor such as X's post box).
2. Open the extension, paste your text, adjust the speed and press **Type**. The panel closes and typing begins.
3. If no field was focused, the extension waits (up to 60 s) for you to click one.
4. **Esc** on the page, the *Stop* button of the on-screen notice, or *Stop* in the panel, stops it. If the field loses focus, typing stops so it doesn't type where it shouldn't.

Privacy: it only acts on the active tab when you press the icon, sends nothing to any server, and your text is only kept for the browser session. Permissions: `activeTab`, `scripting`, `storage`. Full policy: [English](docs/privacy-policy.en.md) · [Español](docs/privacy-policy.md).

Limitations:
- It does not work on internal pages (`chrome://…`, the Chrome Web Store) or in cross-origin iframes.
- Editors that draw their own text (e.g. Google Docs) don't use standard text fields and may ignore it.
- In single-line fields, line breaks are turned into spaces.
- If a site misbehaves, the desktop app works everywhere.

## Support

If you find PasteScribe useful, follow me on X to support me and see my upcoming projects: [@chevlume](https://x.com/chevlume)

## License

Apache License 2.0 — see [LICENSE](LICENSE).
