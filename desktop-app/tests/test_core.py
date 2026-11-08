import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from typer_core import char_delay, normalize_text, type_text  # noqa: E402


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

    def test_empty_text(self):
        r = type_text("", lambda c: None, sleep=NoSleep())
        self.assertEqual((r.typed, r.total, r.stopped), (0, 0, False))


if __name__ == "__main__":
    unittest.main()
