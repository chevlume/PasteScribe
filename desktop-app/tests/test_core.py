import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from typer_core import (NEWLINE_ENTER, NEWLINE_SKIP, NEWLINE_SPACE, apply_newline_mode,  # noqa: E402
                        MIN_DELAY_MS, char_delay, normalize_text, type_text)


class NoSleep:
    def __init__(self):
        self.total = 0.0

    def __call__(self, s):
        self.total += s


class TypeTextTests(unittest.TestCase):
    def test_types_every_char_in_order(self):
        out = []
        r = type_text("Hola, ñandú!", out.append, delay_ms=0, sleep=NoSleep())
        self.assertEqual("".join(out), "Hola, ñandú!")
        self.assertEqual((r.typed, r.skipped, r.total, r.stopped), (12, 0, 12, False))

    def test_normalizes_newlines(self):
        out = []
        type_text("a\r\nb\rc\nd", out.append, delay_ms=0, sleep=NoSleep())
        self.assertEqual(out, list("a\nb\nc\nd"))
        self.assertEqual(normalize_text("x\r\ny"), "x\ny")

    def test_stop_midway(self):
        out = []
        r = type_text("abcdef", out.append, delay_ms=0, sleep=NoSleep(),
                      should_stop=lambda: len(out) >= 3)
        self.assertEqual(out, list("abc"))
        self.assertTrue(r.stopped)
        self.assertEqual(r.typed, 3)

    def test_stop_during_delay(self):
        out = []
        calls = {"n": 0}

        def stop():
            calls["n"] += 1
            return len(out) >= 1 and calls["n"] > 5

        r = type_text("abc", out.append, delay_ms=1000, sleep=NoSleep(), should_stop=stop)
        self.assertEqual(out, ["a"])
        self.assertTrue(r.stopped)

    def test_unsupported_chars_are_skipped_not_fatal(self):
        class Bad(Exception):
            pass

        def send(ch):
            if ch == "x":
                raise Bad()

        r = type_text("axb", send, delay_ms=0, sleep=NoSleep(), skip_errors=(Bad,))
        self.assertEqual((r.typed, r.skipped), (2, 1))

    def test_other_errors_propagate(self):
        def send(ch):
            raise RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            type_text("a", send, delay_ms=0, sleep=NoSleep())

    def test_progress_reported(self):
        seen = []
        type_text("abc", lambda c: None, delay_ms=0, sleep=NoSleep(),
                  on_progress=lambda d, t: seen.append((d, t)))
        self.assertEqual(seen, [(1, 3), (2, 3), (3, 3)])

    def test_fixed_delay_total_time(self):
        s = NoSleep()
        type_text("abcd", lambda c: None, delay_ms=100, sleep=s)
        # 3 pausas entre 4 caracteres (no hay pausa tras el último)
        self.assertAlmostEqual(s.total, 0.3, places=6)

    def test_humanize_varies_and_is_bounded(self):
        rng = random.Random(1)
        vals = {char_delay(100, True, "a", rng) for _ in range(50)}
        self.assertGreater(len(vals), 10)
        self.assertTrue(all(0.05 <= v <= 0.15 for v in vals))
        self.assertGreater(char_delay(100, True, ".", random.Random(1)),
                           char_delay(100, True, "a", random.Random(1)))

    def test_delay_never_below_minimum(self):
        # Con 0 ms se vuelcan las teclas de golpe: debe aplicarse la pausa mínima.
        s = NoSleep()
        type_text("abcd", lambda c: None, delay_ms=0, sleep=s)
        self.assertAlmostEqual(s.total, 3 * MIN_DELAY_MS / 1000, places=6)
        self.assertEqual(char_delay(-5, False, "a", random.Random(1)), MIN_DELAY_MS / 1000)

    def test_empty_text(self):
        r = type_text("", lambda c: None, sleep=NoSleep())
        self.assertEqual((r.typed, r.total, r.stopped), (0, 0, False))


class NewlineModeTests(unittest.TestCase):
    def test_enter_keeps_newlines(self):
        self.assertEqual(apply_newline_mode("a\nb\n\nc", NEWLINE_ENTER), "a\nb\n\nc")

    def test_space_never_leaves_newlines_and_collapses_runs(self):
        out = apply_newline_mode("linea1\nlinea2\n\n\nlinea3", NEWLINE_SPACE)
        self.assertEqual(out, "linea1 linea2 linea3")
        self.assertNotIn("\n", out)

    def test_skip_removes_newlines(self):
        self.assertEqual(apply_newline_mode("a\nb\n", NEWLINE_SKIP), "ab")

    def test_unknown_mode_fails_loudly(self):
        with self.assertRaises(ValueError):
            apply_newline_mode("a", "otro")

    def test_safe_mode_means_enter_is_never_sent(self):
        sent = []
        text = apply_newline_mode(normalize_text("Notas:\r\n- uno\r\n- dos\r\n"), NEWLINE_SPACE)
        type_text(text, sent.append, delay_ms=0, sleep=NoSleep())
        self.assertNotIn("\n", sent)


class WindowsHelpersTests(unittest.TestCase):
    def test_esc_poller_stops_when_pressed(self):
        import threading
        from keyboard_backend import WindowsEscPoller

        fired = threading.Event()
        state = {"n": 0}

        def pressed():
            state["n"] += 1
            return state["n"] >= 3

        poller = WindowsEscPoller(fired.set, is_pressed=pressed, interval=0.001)
        poller.start()
        self.assertTrue(fired.wait(2))
        poller.stop()

    def test_esc_poller_stop_before_press_never_fires(self):
        import threading
        from keyboard_backend import WindowsEscPoller

        fired = threading.Event()
        poller = WindowsEscPoller(fired.set, is_pressed=lambda: False, interval=0.001)
        poller.start()
        poller.stop()
        self.assertFalse(fired.wait(0.05))

    def test_foreground_guard(self):
        from keyboard_backend import ForegroundGuard

        current = {"w": 100}
        g = ForegroundGuard(get_foreground=lambda: current["w"])
        self.assertFalse(g.changed())  # sin armar no indica cambio
        g.arm()
        self.assertFalse(g.changed())
        current["w"] = 200
        self.assertTrue(g.changed())

    def test_foreground_guard_noop_when_unsupported(self):
        from keyboard_backend import ForegroundGuard

        g = ForegroundGuard(get_foreground=lambda: None)
        g.arm()
        self.assertFalse(g.changed())


if __name__ == "__main__":
    unittest.main()
