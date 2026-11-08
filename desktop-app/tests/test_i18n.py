import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import i18n  # noqa: E402


def fields(text):
    return set(re.findall(r"{(\w+)}", text))


class TranslationTests(unittest.TestCase):
    def test_both_languages_have_the_same_keys(self):
        self.assertEqual(set(i18n.STRINGS["en"]), set(i18n.STRINGS["es"]))

    def test_placeholders_match_between_languages(self):
        for key, en in i18n.STRINGS["en"].items():
            self.assertEqual(fields(en), fields(i18n.STRINGS["es"][key]), key)

    def test_every_language_is_listed_and_default_is_english(self):
        self.assertEqual(set(i18n.LANGUAGES), set(i18n.STRINGS))
        self.assertEqual(i18n.DEFAULT_LANG, "en")

    def test_no_empty_strings(self):
        for lang, table in i18n.STRINGS.items():
            for key, text in table.items():
                self.assertTrue(text.strip(), f"{lang}.{key}")

    def test_tr_formats_and_falls_back_to_english(self):
        self.assertEqual(i18n.tr("en", "done", typed=5), "Done: 5 characters typed.")
        self.assertEqual(i18n.tr("es", "done", typed=5), "Listo: 5 caracteres escritos.")
        self.assertEqual(i18n.tr("fr", "start"), "Start")  # unknown language -> English

    def test_every_key_formats_with_realistic_values(self):
        values = dict(error="boom", python="C:\\py\\python.exe", n=3, typed=1, total=2, log="~/.pastescribe.log")
        for lang in i18n.STRINGS:
            for key in i18n.STRINGS[lang]:
                needed = fields(i18n.STRINGS[lang][key])
                i18n.tr(lang, key, **{k: values[k] for k in needed}) if needed else i18n.tr(lang, key)


class RememberLanguageTests(unittest.TestCase):
    def setUp(self):
        self.path = Path(tempfile.mkdtemp()) / "cfg.json"

    def test_default_when_no_file(self):
        self.assertEqual(i18n.load_lang(self.path), "en")

    def test_roundtrip(self):
        i18n.save_lang("es", self.path)
        self.assertEqual(i18n.load_lang(self.path), "es")
        i18n.save_lang("en", self.path)
        self.assertEqual(i18n.load_lang(self.path), "en")

    def test_corrupt_or_unknown_values_fall_back_to_english(self):
        for content in ("not json", "[]", '{"lang": "xx"}', '{"lang": 5}', ""):
            self.path.write_text(content, encoding="utf-8")
            self.assertEqual(i18n.load_lang(self.path), "en", content)

    def test_unknown_language_is_not_saved_and_unwritable_path_is_ignored(self):
        i18n.save_lang("xx", self.path)
        self.assertFalse(self.path.exists())
        i18n.save_lang("es", Path("/nonexistent-dir/cfg.json"))  # must not raise

    def test_saved_file_is_valid_json(self):
        i18n.save_lang("es", self.path)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), {"lang": "es"})


if __name__ == "__main__":
    unittest.main()
