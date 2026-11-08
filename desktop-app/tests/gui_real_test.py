"""Prueba la ventana REAL de PasteScribe (necesita tkinter y un servidor X: xvfb-run).

    xvfb-run -a python3 tests/gui_real_test.py
"""
import os
import sys
import tempfile
import time
import tkinter as tk
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
cfg = Path(tempfile.mkdtemp()) / "pastescribe.json"
os.environ["PASTESCRIBE_CONFIG"] = str(cfg)
log = Path(tempfile.mkdtemp()) / "pastescribe.log"
os.environ["PASTESCRIBE_LOG"] = str(log)

import i18n  # noqa: E402
import pastescribe  # noqa: E402

failures = 0


def check(name, got, want):
    global failures
    ok = got == want
    failures += (not ok)
    print("PASS" if ok else "FAIL", name, "" if ok else f"got={got!r} want={want!r}")


def widget_texts(root):
    out = []

    def walk(w):
        for c in w.winfo_children():
            try:
                v = c.cget("text")
                if v and not str(v).startswith("PY_VAR"):
                    out.append(str(v))
            except tk.TclError:
                pass
            walk(c)
    walk(root)
    return out


def new_app():
    root = tk.Tk()
    app = pastescribe.App(root)
    root.update()
    return root, app


# 1) por defecto: inglés, sin ninguna cadena en español
root, app = new_app()
texts = widget_texts(root)
check("default language is English", app.lang, "en")
check("start button in English", app.start_btn.cget("text"), "Start")
check("no Spanish UI strings by default", [t for t in texts if t in i18n.STRINGS["es"].values()], [])
check("language selector shows English", app.lang_combo.get(), "English")
check("title has version", root.title(), f"PasteScribe {pastescribe.__version__}")
check("nothing saved yet", cfg.exists(), False)

# 2) cambiar a español: textos, texto pegado y opciones se conservan
app.text.insert("1.0", "texto de prueba\nsegunda línea")
app.delay_ms.set(77)
app.countdown.set(3)
app.humanize.set(False)
app.newline_combo.current(1)
app.newline_combo.event_generate("<<ComboboxSelected>>")
root.update()
check("newline choice recorded", app.newline_index.get(), 1)
app.lang_combo.current(1)
app.lang_combo.event_generate("<<ComboboxSelected>>")
root.update()
check("language is now es", app.lang, "es")
check("start button in Spanish", app.start_btn.cget("text"), "Iniciar")
check("stop button in Spanish", app.stop_btn.cget("text"), "Detener (Esc)")
check("status in Spanish", app.status.get(), i18n.STRINGS["es"]["status_idle"])
check("no English UI strings after switch", [t for t in widget_texts(root) if t in i18n.STRINGS["en"].values()], [])
check("pasted text preserved", app.text.get("1.0", "end-1c"), "texto de prueba\nsegunda línea")
check("delay preserved", app.delay_ms.get(), 77)
check("countdown preserved", app.countdown.get(), 3)
check("humanize preserved", app.humanize.get(), False)
check("newline option preserved & translated", app.newline_combo.get(), i18n.STRINGS["es"]["newline_enter"])
check("language saved to file", i18n.load_lang(cfg), "es")
app._on_close()

# 3) recuerda el idioma al reabrir
root, app = new_app()
check("remembered Spanish on restart", (app.lang, app.start_btn.cget("text")), ("es", "Iniciar"))

# 4) el selector queda bloqueado mientras escribe y vuelve a activarse
class FakeBackend:
    unsupported_errors = ()
    def __init__(self): self.sent = []
    def send_char(self, ch): self.sent.append(ch)
class FakeHotkey:
    def start(self): pass
    def stop(self): pass
backend = FakeBackend()
app.text.insert("1.0", "abc")
app.countdown.set(1)
with mock.patch.object(pastescribe, "PynputBackend", lambda: backend), \
     mock.patch.object(pastescribe, "make_stop_hotkey", lambda cb: FakeHotkey()):
    app.start_btn.invoke()
    root.update()
    check("language selector locked while typing", str(app.lang_combo.cget("state")), "disabled")
    app._change_language("en")  # debe ignorarse mientras escribe
    check("language change ignored while typing", app.lang, "es")
    deadline = time.time() + 15
    while app.worker.is_alive() and time.time() < deadline:
        root.update(); time.sleep(0.02)
    for _ in range(20):
        root.update(); time.sleep(0.02)
check("typed the text (spaces for newlines not needed here)", "".join(backend.sent), "abc")
check("selector unlocked after typing", str(app.lang_combo.cget("state")), "readonly")
check("final message in Spanish", app.status.get(), "Listo: 3 caracteres escritos.")

# 5) volver a inglés y mensajes de error traducidos
app.lang_combo.current(0)
app.lang_combo.event_generate("<<ComboboxSelected>>")
root.update()
check("back to English", (app.lang, app.start_btn.cget("text")), ("en", "Start"))
check("English remembered", i18n.load_lang(cfg), "en")
app.text.delete("1.0", "end")
with mock.patch.object(pastescribe.messagebox, "showinfo") as info:
    app.start_btn.invoke()
check("empty-text message in English", info.call_args[0][1], "Paste the text you want to type first.")
app.text.insert("1.0", "x")
def boom(): raise ModuleNotFoundError("No module named 'pynput'")
with mock.patch.object(pastescribe, "PynputBackend", boom), mock.patch.object(pastescribe.messagebox, "showerror") as err:
    app.start_btn.invoke()
msg = err.call_args[0][1]
check("keyboard error message in English with pip command",
      msg.startswith("Could not start keyboard control:") and "-m pip install -r requirements.txt" in msg, True)

# 6) modos de salto de línea desde la interfaz real
for idx, expected in ((0, "uno dos"), (2, "unodos")):
    app._on_close()
    root, app = new_app()
    backend = FakeBackend()
    app.text.insert("1.0", "uno\ndos")
    app.countdown.set(1)
    app.newline_combo.current(idx)
    app.newline_combo.event_generate("<<ComboboxSelected>>")
    with mock.patch.object(pastescribe, "PynputBackend", lambda: backend), \
         mock.patch.object(pastescribe, "make_stop_hotkey", lambda cb: FakeHotkey()):
        app.start_btn.invoke()
        deadline = time.time() + 15
        while app.worker.is_alive() and time.time() < deadline:
            root.update(); time.sleep(0.02)
    check(f"newline mode index {idx}", "".join(backend.sent), expected)
app._on_close()

# 7) un error dentro de la ventana se guarda en el registro y se avisa (en el .exe no hay consola)
root, app = new_app()
with mock.patch.object(pastescribe.messagebox, "showerror") as shown:
    root.after(0, lambda: 1 / 0)
    root.update()
check("unexpected error is logged", "ZeroDivisionError" in log.read_text(encoding="utf-8"), True)
check("unexpected error is shown to the user",
      shown.call_args[0][1].startswith("Unexpected error: division by zero") and str(log) in shown.call_args[0][1], True)
app._on_close()

print("GUI ALL PASSED" if not failures else f"GUI {failures} FAILED")
sys.exit(1 if failures else 0)
