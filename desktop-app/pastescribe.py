#!/usr/bin/env python3
"""PasteScribe: types pasted text, letter by letter, into any application or
text field you have open on your computer.

Usage: paste your text, press "Start", click the target field during the
countdown and let PasteScribe type. Esc stops it.
"""

from __future__ import annotations

import os
import queue
import sys
import threading
import traceback
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk

from i18n import LANGUAGES, load_lang, save_lang, tr
from keyboard_backend import ForegroundGuard, PynputBackend, make_stop_hotkey
from typer_core import (NEWLINE_ENTER, NEWLINE_SKIP, NEWLINE_SPACE, apply_newline_mode,
                        MIN_DELAY_MS, normalize_text, type_text)

__version__ = "1.4.0"
APP_TITLE = "PasteScribe"

def log_path() -> Path:
    """Where unexpected errors are saved, so they can be reported."""
    return Path(os.environ.get("PASTESCRIBE_LOG") or Path.home() / ".pastescribe.log")


def log_error(text: str) -> None:
    try:
        with open(log_path(), "a", encoding="utf-8") as fh:
            fh.write(text + "\n")
    except OSError:
        pass


# Order of the entries in the "Line breaks" selector: (mode, text key)
NEWLINE_OPTIONS = [
    (NEWLINE_SPACE, "newline_space"),
    (NEWLINE_ENTER, "newline_enter"),
    (NEWLINE_SKIP, "newline_skip"),
]


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.lang = load_lang()
        self.events: "queue.Queue[tuple]" = queue.Queue()
        self.stop_flag = threading.Event()
        self.worker: threading.Thread | None = None

        # Options live here (not in the widgets) so they survive a language change.
        self.delay_ms = tk.IntVar(value=60)
        self.countdown = tk.IntVar(value=5)
        self.humanize = tk.BooleanVar(value=True)
        self.minimize = tk.BooleanVar(value=False)
        self.newline_index = tk.IntVar(value=0)

        root.report_callback_exception = self._report_error
        root.title(f"{APP_TITLE} {__version__}")
        root.geometry("560x520")
        root.minsize(480, 460)
        self.frame = None
        self._build_ui()
        self._poll_job = self.root.after(50, self._poll_events)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _report_error(self, exc_type, value, tb) -> None:
        """Errors inside Tk callbacks: save the details and tell the user."""
        log_error("".join(traceback.format_exception(exc_type, value, tb)))
        try:
            messagebox.showerror(APP_TITLE, self.t("err_unexpected", error=value, log=log_path()))
        except Exception:
            pass

    def t(self, key: str, **values) -> str:
        return tr(self.lang, key, **values)

    # ---------- interface ----------
    def _build_ui(self) -> None:
        self.frame = frm = ttk.Frame(self.root, padding=12)
        frm.pack(fill="both", expand=True)

        top = ttk.Frame(frm)
        top.pack(fill="x")
        ttk.Label(top, text=self.t("text_label")).pack(side="left")
        codes = list(LANGUAGES)
        self.lang_combo = ttk.Combobox(top, values=[LANGUAGES[c] for c in codes], state="readonly", width=9)
        self.lang_combo.current(codes.index(self.lang))
        self.lang_combo.pack(side="right")
        self.lang_combo.bind("<<ComboboxSelected>>", lambda _e: self._change_language(codes[self.lang_combo.current()]))
        ttk.Label(top, text=self.t("language")).pack(side="right", padx=(0, 4))

        self.text = scrolledtext.ScrolledText(frm, wrap="word", height=12, undo=True)
        self.text.pack(fill="both", expand=True, pady=(4, 8))

        row = ttk.Frame(frm)
        row.pack(fill="x")
        ttk.Button(row, text=self.t("paste_clipboard"), command=self._paste_clipboard).pack(side="left")
        ttk.Button(row, text=self.t("clear"), command=lambda: self.text.delete("1.0", "end")).pack(side="left", padx=6)

        opts = ttk.LabelFrame(frm, text=self.t("options"), padding=8)
        opts.pack(fill="x", pady=8)

        ttk.Label(opts, text=self.t("pause_label")).grid(row=0, column=0, sticky="w")
        ttk.Spinbox(opts, from_=10, to=2000, increment=10, width=6, textvariable=self.delay_ms).grid(
            row=0, column=1, padx=6, sticky="w")
        ttk.Label(opts, text=self.t("countdown_label")).grid(row=0, column=2, sticky="w", padx=(16, 0))
        ttk.Spinbox(opts, from_=1, to=60, width=4, textvariable=self.countdown).grid(
            row=0, column=3, padx=6, sticky="w")
        ttk.Label(opts, text=self.t("newline_label")).grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.newline_combo = ttk.Combobox(
            opts, values=[self.t(key) for _mode, key in NEWLINE_OPTIONS], state="readonly", width=36)
        self.newline_combo.current(self.newline_index.get())
        self.newline_combo.bind(
            "<<ComboboxSelected>>", lambda _e: self.newline_index.set(self.newline_combo.current()))
        self.newline_combo.grid(row=1, column=1, columnspan=3, padx=6, sticky="w", pady=(6, 0))
        ttk.Checkbutton(opts, text=self.t("irregular"), variable=self.humanize).grid(
            row=2, column=0, columnspan=4, sticky="w", pady=(6, 0))
        ttk.Checkbutton(opts, text=self.t("minimize"), variable=self.minimize).grid(
            row=3, column=0, columnspan=4, sticky="w")

        btns = ttk.Frame(frm)
        btns.pack(fill="x")
        self.start_btn = ttk.Button(btns, text=self.t("start"), command=self.start)
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(btns, text=self.t("stop"), command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=6)

        self.progress = ttk.Progressbar(frm, mode="determinate")
        self.progress.pack(fill="x", pady=(10, 2))
        self.status = tk.StringVar(value=self.t("status_idle"))
        ttk.Label(frm, textvariable=self.status, wraplength=520).pack(anchor="w")

    def _change_language(self, lang: str) -> None:
        """Switches the interface language, keeping the pasted text and the options."""
        if lang == self.lang or (self.worker and self.worker.is_alive()):
            return
        self.lang = lang
        save_lang(lang)
        pasted = self.text.get("1.0", "end-1c")
        self.frame.destroy()
        self._build_ui()
        self.text.insert("1.0", pasted)

    def _paste_clipboard(self) -> None:
        try:
            clip = self.root.clipboard_get()
        except tk.TclError:
            self.status.set(self.t("clipboard_empty"))
            return
        self.text.delete("1.0", "end")
        self.text.insert("1.0", clip)

    # ---------- typing ----------
    def start(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        mode = NEWLINE_OPTIONS[self.newline_index.get()][0]
        text = apply_newline_mode(normalize_text(self.text.get("1.0", "end-1c")), mode)
        if not text.strip():
            messagebox.showinfo(APP_TITLE, self.t("err_no_text"))
            return
        try:
            delay = max(MIN_DELAY_MS, int(self.delay_ms.get()))
            countdown = max(1, int(self.countdown.get()))
        except (tk.TclError, ValueError):
            messagebox.showerror(APP_TITLE, self.t("err_numbers"))
            return

        try:
            backend = PynputBackend()
            hotkey = make_stop_hotkey(self.stop_flag.set)
            hotkey.start()
        except Exception as exc:  # pynput missing, no X server, etc.
            messagebox.showerror(APP_TITLE, self.t("err_keyboard", error=exc, python=sys.executable))
            return

        self.stop_flag.clear()
        self.progress.configure(value=0, maximum=len(text))
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.lang_combo.configure(state="disabled")
        if self.minimize.get():
            self.root.iconify()

        self.worker = threading.Thread(
            target=self._run, args=(text, delay, countdown, self.humanize.get(), backend, hotkey),
            daemon=True)
        self.worker.start()

    def stop(self) -> None:
        self.stop_flag.set()

    def _run(self, text, delay, countdown, humanize, backend, hotkey) -> None:
        import time

        try:
            for remaining in range(countdown, 0, -1):
                if self.stop_flag.is_set():
                    break
                self.events.put(("status", self.t("countdown", n=remaining)))
                end = time.monotonic() + 1
                while time.monotonic() < end and not self.stop_flag.is_set():
                    time.sleep(0.02)
            if self.stop_flag.is_set():
                self.events.put(("done", self.t("cancelled")))
                return

            self.events.put(("status", self.t("typing")))
            guard = ForegroundGuard()
            guard.arm()  # if the active window changes, stop typing
            window_changed = threading.Event()

            def should_stop() -> bool:
                if self.stop_flag.is_set():
                    return True
                if guard.changed():
                    window_changed.set()
                    return True
                return False

            result = type_text(
                text,
                backend.send_char,
                delay_ms=delay,
                humanize=humanize,
                should_stop=should_stop,
                on_progress=lambda d, t: self.events.put(("progress", d)),
                skip_errors=backend.unsupported_errors,
            )
            if result.stopped:
                key = "stopped_window" if window_changed.is_set() else "stopped"
                msg = self.t(key, typed=result.typed, total=result.total)
            else:
                msg = self.t("done", typed=result.typed)
            if result.skipped:
                msg += self.t("skipped", n=result.skipped)
            self.events.put(("done", msg))
        except Exception as exc:
            self.events.put(("done", self.t("error", error=exc)))
        finally:
            hotkey.stop()

    def _poll_events(self) -> None:
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "status":
                    self.status.set(value)
                elif kind == "progress":
                    self.progress.configure(value=value)
                elif kind == "done":
                    self.status.set(value)
                    self.start_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
                    self.lang_combo.configure(state="readonly")
                    self.root.deiconify()
                    self.root.lift()
        except queue.Empty:
            pass
        self._poll_job = self.root.after(50, self._poll_events)

    def _on_close(self) -> None:
        self.stop_flag.set()
        self.root.after_cancel(self._poll_job)
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
