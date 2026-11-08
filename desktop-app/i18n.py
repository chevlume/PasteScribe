"""Interface texts for PasteScribe (English by default, Spanish available).

The chosen language is remembered in a small JSON file in the user's home
folder (``~/.pastescribe.json``; override with ``PASTESCRIBE_CONFIG``).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

DEFAULT_LANG = "en"
LANGUAGES = {"en": "English", "es": "Español"}  # code -> name shown in the selector

STRINGS = {
    "en": {
        "language": "Language:",
        "text_label": "Text to type (paste it here with Ctrl+V / Cmd+V):",
        "paste_clipboard": "Paste from clipboard",
        "clear": "Clear",
        "options": "Options",
        "pause_label": "Pause between letters (ms):",
        "countdown_label": "Countdown (s):",
        "newline_label": "Line breaks:",
        "newline_space": "Turn into a space (safe)",
        "newline_enter": "Press Enter (multi-line text)",
        "newline_skip": "Remove",
        "irregular": "Irregular pauses (random variation)",
        "minimize": "Minimize this window while typing (only Esc stops it)",
        "start": "Start",
        "stop": "Stop (Esc)",
        "status_idle": "Paste your text, press Start and click the target field.",
        "clipboard_empty": "The clipboard is empty or doesn't contain text.",
        "err_no_text": "Paste the text you want to type first.",
        "err_numbers": "The pause and the countdown must be whole numbers.",
        "err_keyboard": ("Could not start keyboard control:\n{error}\n\n"
                         "Install the dependencies with:\n\"{python}\" -m pip install -r requirements.txt"),
        "countdown": "Starting in {n} s… click the target field (Esc cancels).",
        "cancelled": "Cancelled before starting.",
        "typing": "Typing… (Esc to stop)",
        "stopped": "Stopped: {typed} of {total} characters typed.",
        "stopped_window": "Stopped (the active window changed): {typed} of {total} characters typed.",
        "done": "Done: {typed} characters typed.",
        "skipped": " ({n} could not be typed.)",
        "error": "Error: {error}",
        "err_unexpected": "Unexpected error: {error}\n\nDetails were saved in:\n{log}",
    },
    "es": {
        "language": "Idioma:",
        "text_label": "Texto a escribir (pégalo aquí con Ctrl+V / Cmd+V):",
        "paste_clipboard": "Pegar del portapapeles",
        "clear": "Borrar",
        "options": "Opciones",
        "pause_label": "Pausa entre letras (ms):",
        "countdown_label": "Cuenta atrás (s):",
        "newline_label": "Saltos de línea:",
        "newline_space": "Convertir en espacio (seguro)",
        "newline_enter": "Pulsar Enter (textos de varias líneas)",
        "newline_skip": "Eliminar",
        "irregular": "Pausas irregulares (variación aleatoria)",
        "minimize": "Minimizar esta ventana mientras escribe (solo se detiene con Esc)",
        "start": "Iniciar",
        "stop": "Detener (Esc)",
        "status_idle": "Pega el texto, pulsa Iniciar y haz clic en el campo de destino.",
        "clipboard_empty": "El portapapeles está vacío o no contiene texto.",
        "err_no_text": "Pega primero el texto que quieres escribir.",
        "err_numbers": "La pausa y la cuenta atrás deben ser números enteros.",
        "err_keyboard": ("No se pudo iniciar el control del teclado:\n{error}\n\n"
                         "Instala las dependencias con:\n\"{python}\" -m pip install -r requirements.txt"),
        "countdown": "Empieza en {n} s… haz clic en el campo de destino (Esc cancela).",
        "cancelled": "Cancelado antes de empezar.",
        "typing": "Escribiendo… (Esc para detener)",
        "stopped": "Detenido: {typed} de {total} caracteres escritos.",
        "stopped_window": "Detenido (cambió la ventana activa): {typed} de {total} caracteres escritos.",
        "done": "Listo: {typed} caracteres escritos.",
        "skipped": " ({n} no se pudieron escribir.)",
        "error": "Error: {error}",
        "err_unexpected": "Error inesperado: {error}\n\nLos detalles se guardaron en:\n{log}",
    },
}


def tr(lang: str, key: str, **values) -> str:
    """Text for ``key`` in ``lang`` (falls back to English), formatted with ``values``."""
    table = STRINGS.get(lang) or STRINGS[DEFAULT_LANG]
    text = table.get(key) or STRINGS[DEFAULT_LANG][key]
    return text.format(**values) if values else text


def config_path() -> Path:
    return Path(os.environ.get("PASTESCRIBE_CONFIG") or Path.home() / ".pastescribe.json")


def load_lang(path: Optional[Path] = None) -> str:
    """Saved language, or English if there is none or the file is unreadable."""
    try:
        data = json.loads((path or config_path()).read_text(encoding="utf-8"))
        lang = data.get("lang")
        return lang if lang in LANGUAGES else DEFAULT_LANG
    except (OSError, ValueError, AttributeError):
        return DEFAULT_LANG


def save_lang(lang: str, path: Optional[Path] = None) -> None:
    """Remember ``lang``. Failing to save is not important, so errors are ignored."""
    if lang not in LANGUAGES:
        return
    try:
        (path or config_path()).write_text(json.dumps({"lang": lang}), encoding="utf-8")
    except OSError:
        pass
