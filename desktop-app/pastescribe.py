#!/usr/bin/env python3
"""PasteScribe: escribe un texto pegado, letra por letra, en cualquier
aplicación o campo de texto que tengas abierto en el equipo.

Uso: pega el texto, pulsa «Iniciar», haz clic en el campo de destino
durante la cuenta atrás y deja que PasteScribe escriba. Esc detiene.
"""

from __future__ import annotations

import queue
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from keyboard_backend import ForegroundGuard, PynputBackend, make_stop_hotkey
from typer_core import (NEWLINE_ENTER, NEWLINE_SKIP, NEWLINE_SPACE, apply_newline_mode,
                        normalize_text, type_text)

APP_TITLE = "PasteScribe"

NEWLINE_CHOICES = {
    "Convertir en espacio (seguro)": NEWLINE_SPACE,
    "Pulsar Enter (textos de varias líneas)": NEWLINE_ENTER,
    "Eliminar": NEWLINE_SKIP,
}


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.events: "queue.Queue[tuple]" = queue.Queue()
        self.stop_flag = threading.Event()
        self.worker: threading.Thread | None = None

        root.title(APP_TITLE)
        root.geometry("560x480")
        root.minsize(480, 420)
        self._build_ui()
        self.root.after(50, self._poll_events)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- interfaz ----------
    def _build_ui(self) -> None:
        frm = ttk.Frame(self.root, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Texto a escribir (pega aquí con Ctrl+V / Cmd+V):").pack(anchor="w")
        self.text = scrolledtext.ScrolledText(frm, wrap="word", height=12, undo=True)
        self.text.pack(fill="both", expand=True, pady=(4, 8))

        row = ttk.Frame(frm)
        row.pack(fill="x")
        ttk.Button(row, text="Pegar del portapapeles", command=self._paste_clipboard).pack(side="left")
        ttk.Button(row, text="Borrar", command=lambda: self.text.delete("1.0", "end")).pack(side="left", padx=6)

        opts = ttk.LabelFrame(frm, text="Opciones", padding=8)
        opts.pack(fill="x", pady=8)

        self.delay_ms = tk.IntVar(value=60)
        self.countdown = tk.IntVar(value=5)
        self.humanize = tk.BooleanVar(value=True)
        self.minimize = tk.BooleanVar(value=False)
        self.newline = tk.StringVar(value=next(iter(NEWLINE_CHOICES)))

        ttk.Label(opts, text="Pausa entre letras (ms):").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(opts, from_=0, to=2000, increment=10, width=6, textvariable=self.delay_ms).grid(
            row=0, column=1, padx=6, sticky="w")
        ttk.Label(opts, text="Cuenta atrás (s):").grid(row=0, column=2, sticky="w", padx=(16, 0))
        ttk.Spinbox(opts, from_=1, to=60, width=4, textvariable=self.countdown).grid(
            row=0, column=3, padx=6, sticky="w")
        ttk.Label(opts, text="Saltos de línea:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Combobox(opts, textvariable=self.newline, values=list(NEWLINE_CHOICES), state="readonly",
                     width=36).grid(row=1, column=1, columnspan=3, padx=6, sticky="w", pady=(6, 0))
        ttk.Checkbutton(opts, text="Ritmo humano (variación aleatoria)", variable=self.humanize).grid(
            row=2, column=0, columnspan=4, sticky="w", pady=(6, 0))
        ttk.Checkbutton(opts, text="Minimizar esta ventana mientras escribe (solo se detiene con Esc)",
                        variable=self.minimize).grid(row=3, column=0, columnspan=4, sticky="w")

        btns = ttk.Frame(frm)
        btns.pack(fill="x")
        self.start_btn = ttk.Button(btns, text="Iniciar", command=self.start)
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(btns, text="Detener (Esc)", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=6)

        self.progress = ttk.Progressbar(frm, mode="determinate")
        self.progress.pack(fill="x", pady=(10, 2))
        self.status = tk.StringVar(
            value="Pega el texto, pulsa Iniciar y haz clic en el campo de destino.")
        ttk.Label(frm, textvariable=self.status, wraplength=520).pack(anchor="w")

    def _paste_clipboard(self) -> None:
        try:
            clip = self.root.clipboard_get()
        except tk.TclError:
            self.status.set("El portapapeles está vacío o no contiene texto.")
            return
        self.text.delete("1.0", "end")
        self.text.insert("1.0", clip)

    # ---------- ejecución ----------
    def start(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        text = apply_newline_mode(
            normalize_text(self.text.get("1.0", "end-1c")), NEWLINE_CHOICES[self.newline.get()])
        if not text.strip():
            messagebox.showinfo(APP_TITLE, "Pega primero el texto que quieres escribir.")
            return
        try:
            delay = max(0, int(self.delay_ms.get()))
            countdown = max(1, int(self.countdown.get()))
        except (tk.TclError, ValueError):
            messagebox.showerror(APP_TITLE, "La pausa y la cuenta atrás deben ser números enteros.")
            return

        try:
            backend = PynputBackend()
            hotkey = make_stop_hotkey(self.stop_flag.set)
            hotkey.start()
        except Exception as exc:  # pynput ausente, sin servidor X, etc.
            messagebox.showerror(
                APP_TITLE,
                f"No se pudo iniciar el control del teclado:\n{exc}\n\n"
                "Instala las dependencias con:\n"
                f'"{sys.executable}" -m pip install -r requirements.txt')
            return

        self.stop_flag.clear()
        self.progress.configure(value=0, maximum=len(text))
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
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
                self.events.put(("status", f"Empieza en {remaining} s… haz clic en el campo de destino (Esc cancela)."))
                end = time.monotonic() + 1
                while time.monotonic() < end and not self.stop_flag.is_set():
                    time.sleep(0.02)
            if self.stop_flag.is_set():
                self.events.put(("done", "Cancelado antes de empezar."))
                return

            self.events.put(("status", "Escribiendo… (Esc para detener)"))
            guard = ForegroundGuard()
            guard.arm()  # si cambia la ventana activa, se deja de escribir
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
                why = " (cambió la ventana activa)" if window_changed.is_set() else ""
                msg = f"Detenido{why}: {result.typed} de {result.total} caracteres escritos."
            else:
                msg = f"Listo: {result.typed} caracteres escritos."
            if result.skipped:
                msg += f" ({result.skipped} no se pudieron escribir.)"
            self.events.put(("done", msg))
        except Exception as exc:
            self.events.put(("done", f"Error: {exc}"))
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
                    self.root.deiconify()
                    self.root.lift()
        except queue.Empty:
            pass
        self.root.after(50, self._poll_events)

    def _on_close(self) -> None:
        self.stop_flag.set()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
