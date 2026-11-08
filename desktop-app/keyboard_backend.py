"""Backend de teclado real (pynput) y atajo global para detener."""

from __future__ import annotations

import inspect
import sys
import textwrap
import threading
import time


def _simple_keyboard_mapping(display) -> dict:
    """Tabla keysym -> (tecla, estado) usando solo los niveles normal y Mayús.

    La tabla propia de pynput también considera niveles de AltGr/grupo 2 y en
    X11 puede elegir una tecla equivocada (p. ej. envía «|» por la tecla «<>»
    y el servidor lo interpreta como «>»). Los caracteres que no estén en esos
    dos niveles se escriben "prestando" una tecla libre, que es fiable.
    """
    mapping: dict = {}
    first = display.display.info.min_keycode
    count = display.display.info.max_keycode - first + 1
    for offset, row in enumerate(display.get_keyboard_mapping(first, count)):
        for level in (0, 1):
            keysym = row[level] if level < len(row) else 0
            if not keysym:
                continue
            state = 1 if level else 0  # 1 = ShiftMask
            known = mapping.get(keysym)
            if known is not None and known[1] <= state:
                continue
            mapping[keysym] = (first + offset, state)
    return mapping


def _patch_x11() -> bool:
    """Corrige dos fallos de pynput al escribir caracteres en X11 (Linux).

    1. Tabla de teclas: ver ``_simple_keyboard_mapping``.
    2. Reutilización de teclas prestadas: para escribir caracteres que no están
       en el teclado (p. ej. «í» con distribución US) pynput los "presta" a
       teclas libres. Al reutilizar una tecla ya prestada puede usar los niveles
       2 y 3, que solo se resuelven con AltGr; sin ese nivel la aplicación
       recibe otro carácter (por ejemplo «é» en lugar de «í»). Limitar la
       reutilización a los niveles 0 y 1 lo evita.

    Se aplica solo en Linux y si la estructura interna de pynput es la esperada;
    en cualquier otro caso no hace nada. Devuelve True si se aplicó.
    """
    if not sys.platform.startswith("linux"):
        return False
    try:
        from pynput.keyboard import _xorg

        cls = _xorg.Controller
        if getattr(cls, "_pastescribe_patched", False):
            return True
        source = textwrap.dedent(inspect.getsource(cls._resolve_borrowing))
        needle = "for index in range(4):"
        if source.count(needle) != 1:
            return False
        namespace: dict = {}
        exec(compile(source.replace(needle, "for index in range(2):"), "<pastescribe-patch>", "exec"),
             _xorg.__dict__, namespace)
        cls._resolve_borrowing = namespace["_resolve_borrowing"]
        _xorg.keyboard_mapping = _simple_keyboard_mapping
        cls._pastescribe_patched = True
        return True
    except Exception:  # sin Xlib, sin código fuente, versión distinta...
        return False


class PynputBackend:
    """Pulsa caracteres en la ventana que tenga el foco del sistema."""

    def __init__(self) -> None:
        from pynput.keyboard import Controller

        self._settle = 0.015 if _patch_x11() else 0.0
        self._kb = Controller()

    @property
    def unsupported_errors(self) -> tuple:
        from pynput.keyboard import Controller

        return (Controller.InvalidCharacterException,)

    def send_char(self, ch: str) -> None:
        # Controller.type convierte "\n" en Enter y "\t" en Tab.
        self._kb.type(ch)
        if self._settle and ord(ch) > 127:
            # En X11 la tecla prestada se remapea justo antes de pulsarla; esta
            # pausa deja que la aplicación asimile el cambio antes del siguiente.
            time.sleep(self._settle)


class WindowsEscPoller:
    """Detecta Esc consultando el estado del teclado cada pocos milisegundos.

    A diferencia de un "hook" global, no se interpone en la entrada del
    sistema: aunque la app vaya lenta, no retrasa el teclado del usuario.
    """

    VK_ESCAPE = 0x1B

    def __init__(self, on_stop, is_pressed=None, interval: float = 0.02) -> None:
        self._on_stop = on_stop
        self._is_pressed = is_pressed or self._win_is_pressed
        self._interval = interval
        self._done = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)

    @staticmethod
    def _win_is_pressed() -> bool:
        import ctypes

        return bool(ctypes.windll.user32.GetAsyncKeyState(WindowsEscPoller.VK_ESCAPE) & 0x8000)

    def _loop(self) -> None:
        while not self._done.wait(self._interval):
            if self._is_pressed():
                self._on_stop()
                return

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._done.set()


class ForegroundGuard:
    """Detecta que la ventana activa cambió desde ``arm()`` (solo Windows).

    Evita seguir escribiendo si el usuario cambia de programa o si otra
    ventana roba el foco. En otros sistemas nunca indica cambio.
    """

    def __init__(self, get_foreground=None) -> None:
        self._get = get_foreground or self._win_foreground
        self._initial = None

    @staticmethod
    def _win_foreground():
        if sys.platform != "win32":
            return None
        import ctypes

        return ctypes.windll.user32.GetForegroundWindow()

    def arm(self) -> None:
        self._initial = self._get()

    def changed(self) -> bool:
        if self._initial is None:
            return False
        return self._get() != self._initial


def make_stop_hotkey(on_stop):
    """Esc global: consulta directa en Windows, escucha con pynput en el resto."""
    if sys.platform == "win32":
        return WindowsEscPoller(on_stop)
    return StopHotkey(on_stop)


class StopHotkey:
    """Escucha la tecla Esc en todo el sistema y avisa con un callback."""

    def __init__(self, on_stop) -> None:
        from pynput.keyboard import Key, Listener

        self._key = Key.esc

        def on_press(key):
            if key == self._key:
                on_stop()

        self._listener = Listener(on_press=on_press)

    def start(self) -> None:
        self._listener.start()

    def stop(self) -> None:
        self._listener.stop()
