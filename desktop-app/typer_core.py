"""Motor de escritura de PasteScribe.

No depende de ninguna interfaz gráfica ni de ninguna librería de teclado:
recibe una función ``send_char`` que sabe pulsar un carácter. Así se puede
probar sin pantalla y reutilizar con cualquier backend.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, Optional

SLICE_SECONDS = 0.02  # granularidad con la que se comprueba "detener"


def normalize_text(text: str) -> str:
    """Unifica los saltos de línea a ``\\n``."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


@dataclass
class TypingResult:
    typed: int       # caracteres enviados correctamente
    skipped: int     # caracteres que el backend no pudo escribir
    total: int
    stopped: bool    # True si el usuario lo detuvo antes de terminar


def interruptible_sleep(
    seconds: float,
    should_stop: Callable[[], bool],
    sleep: Callable[[float], None] = time.sleep,
) -> bool:
    """Duerme ``seconds`` en trozos pequeños. Devuelve True si se pidió parar."""
    remaining = seconds
    while remaining > 0:
        if should_stop():
            return True
        step = min(SLICE_SECONDS, remaining)
        sleep(step)
        remaining -= step
    return should_stop()


def char_delay(
    delay_ms: float,
    humanize: bool,
    ch: str,
    rng: random.Random,
) -> float:
    """Pausa (en segundos) a aplicar tras escribir ``ch``."""
    delay = max(0.0, delay_ms) / 1000.0
    if not humanize:
        return delay
    delay *= rng.uniform(0.5, 1.5)
    if ch in " \n":
        delay *= 1.8  # se "piensa" un poco más entre palabras
    elif ch in ".,;:!?":
        delay *= 2.5
    return delay


def type_text(
    text: str,
    send_char: Callable[[str], None],
    *,
    delay_ms: float = 50,
    humanize: bool = False,
    should_stop: Callable[[], bool] = lambda: False,
    on_progress: Optional[Callable[[int, int], None]] = None,
    sleep: Callable[[float], None] = time.sleep,
    rng: Optional[random.Random] = None,
    skip_errors: tuple = (),
) -> TypingResult:
    """Escribe ``text`` carácter a carácter usando ``send_char``.

    ``skip_errors``: excepciones que se consideran "carácter no soportado"
    (se cuenta y se sigue con el siguiente). Cualquier otra se propaga.
    """
    rng = rng or random.Random()
    text = normalize_text(text)
    total = len(text)
    typed = skipped = 0
    stopped = False

    for index, ch in enumerate(text):
        if should_stop():
            stopped = True
            break
        try:
            send_char(ch)
            typed += 1
        except skip_errors:
            skipped += 1
        if on_progress:
            on_progress(index + 1, total)
        if index < total - 1:
            if interruptible_sleep(char_delay(delay_ms, humanize, ch, rng), should_stop, sleep):
                stopped = True
                break

    return TypingResult(typed=typed, skipped=skipped, total=total, stopped=stopped)
