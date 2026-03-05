# src/tests/test_lang_utils.py

import pytest
import package.lang_utils as lang_mod
from package.lang_utils import select_language


def test_select_language_returns_code(monkeypatch):
    # Patchiamo il simbolo usato da select_language(): package.lang_utils.ask_choice
    def fake_ask_choice(prompt, options, max_retries=3):
        assert "In quale lingua" in prompt
        assert any(opt.startswith("en (Inglese)") for opt in options)
        return "en (Inglese)"

    monkeypatch.setattr(lang_mod, "ask_choice", fake_ask_choice)

    lang_code = select_language()
    assert lang_code == "en"
