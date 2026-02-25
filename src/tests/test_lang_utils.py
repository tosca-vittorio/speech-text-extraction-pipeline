# src/tests/test_lang_utils.py

import pytest
from package.lang_utils import select_language

def test_select_language_returns_code(monkeypatch):
    # Patchiamo nel punto giusto: package.cli_utils.ask_choice
    import package.cli_utils as cli_mod

    def fake_ask_choice(prompt, options, max_retries=3):
        assert "In quale lingua" in prompt
        assert any(opt.startswith("en (Inglese)") for opt in options)
        return "en (Inglese)"

    monkeypatch.setattr(cli_mod, "ask_choice", fake_ask_choice)

    lang_code = select_language()
    assert lang_code == "en"
