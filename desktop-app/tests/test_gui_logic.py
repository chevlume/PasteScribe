"""Logic tests for pastescribe.App without a screen (fake backend, fake widgets)."""
import os
import queue
import sys
import threading
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# tkinter may not be installed where the tests run: simulate it only in that case
try:
    import tkinter  # noqa: F401
except ImportError:
    for name in ("tkinter", "tkinter.ttk", "tkinter.messagebox", "tkinter.scrolledtext"):
        sys.modules[name] = mock.MagicMock()
    sys.modules["tkinter"].TclError = type("TclError", (Exception,), {})

import pastescribe  # noqa: E402


class FakeBackend:
    unsupported_errors = ()

    def __init__(self):
        self.sent = []

    def send_char(self, ch):
        self.sent.append(ch)


class FakeHotkey:
    def __init__(self):
        self.stopped = False

    def stop(self):
        self.stopped = True


def make_app():
    app = pastescribe.App.__new__(pastescribe.App)
    app.events = queue.Queue()
    app.stop_flag = threading.Event()
    app.lang = "en"
    return app


def drain(app):
    items = []
    while not app.events.empty():
        items.append(app.events.get())
    return items


class RunTests(unittest.TestCase):
    def test_types_text_and_reports_done(self):
        app, backend, hotkey = make_app(), FakeBackend(), FakeHotkey()
        app._run("hola mundo", 0, 1, False, backend, hotkey)
        self.assertEqual("".join(backend.sent), "hola mundo")
        self.assertTrue(hotkey.stopped)
        done = [v for k, v in drain(app) if k == "done"]
        self.assertEqual(done, ["Done: 10 characters typed."])

    def test_esc_stops_typing(self):
        app, backend, hotkey = make_app(), FakeBackend(), FakeHotkey()
        threading.Timer(1.3, app.stop_flag.set).start()  # tras la cuenta atrás de 1 s
        app._run("x" * 500, 20, 1, False, backend, hotkey)
        self.assertTrue(0 < len(backend.sent) < 500)
        done = [v for k, v in drain(app) if k == "done"][0]
        self.assertTrue(done.startswith("Stopped:"))

    def test_stop_during_countdown_types_nothing(self):
        app, backend, hotkey = make_app(), FakeBackend(), FakeHotkey()
        app.stop_flag.set()
        app._run("abc", 0, 3, False, backend, hotkey)
        self.assertEqual(backend.sent, [])
        self.assertIn(("done", "Cancelled before starting."), drain(app))

    def test_window_change_stops_typing(self):
        app, backend, hotkey = make_app(), FakeBackend(), FakeHotkey()
        state = {"w": 1}

        class Guard(pastescribe.ForegroundGuard):
            def __init__(self):
                super().__init__(get_foreground=lambda: state["w"])

        threading.Timer(1.3, lambda: state.update(w=2)).start()
        with mock.patch.object(pastescribe, "ForegroundGuard", Guard):
            app._run("y" * 500, 20, 1, False, backend, hotkey)
        self.assertTrue(0 < len(backend.sent) < 500)
        done = [v for k, v in drain(app) if k == "done"][0]
        self.assertIn("the active window changed", done)

    def test_start_default_never_sends_enter(self):
        """With the default option, multi-line text never presses Enter."""
        app = make_app()
        app.worker = None
        app.text = mock.MagicMock()
        app.text.get.return_value = "Notes:\n- one\n- two\n"
        app.newline_index = mock.MagicMock(get=lambda: 0)  # default: turn line breaks into spaces
        app.lang_combo = mock.MagicMock()
        app.delay_ms = mock.MagicMock(get=lambda: 0)
        app.countdown = mock.MagicMock(get=lambda: 1)
        app.humanize = mock.MagicMock(get=lambda: False)
        app.minimize = mock.MagicMock(get=lambda: False)
        app.progress = mock.MagicMock()
        app.start_btn = mock.MagicMock()
        app.stop_btn = mock.MagicMock()
        app.root = mock.MagicMock()
        backend, hotkey = FakeBackend(), mock.MagicMock()
        with mock.patch.object(pastescribe, "PynputBackend", lambda: backend), \
             mock.patch.object(pastescribe, "make_stop_hotkey", lambda cb: hotkey):
            app.start()
            app.worker.join(10)
        self.assertEqual("".join(backend.sent), "Notes: - one - two ")
        self.assertNotIn("\n", backend.sent)

    def test_start_without_pynput_shows_pip_command(self):
        app = make_app()
        app.worker = None
        app.text = mock.MagicMock(get=lambda *a: "hello")
        app.newline_index = mock.MagicMock(get=lambda: 0)
        app.delay_ms = mock.MagicMock(get=lambda: 0)
        app.countdown = mock.MagicMock(get=lambda: 1)

        def boom():
            raise ModuleNotFoundError("No module named 'pynput'")

        with mock.patch.object(pastescribe, "PynputBackend", boom), \
             mock.patch.object(pastescribe.messagebox, "showerror") as err:
            app.start()
        msg = err.call_args[0][1]
        self.assertTrue(msg.startswith("Could not start keyboard control:"))
        self.assertIn(sys.executable, msg)
        self.assertIn("-m pip install -r requirements.txt", msg)


if __name__ == "__main__":
    unittest.main()
