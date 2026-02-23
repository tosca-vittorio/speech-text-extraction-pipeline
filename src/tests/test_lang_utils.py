# src/tests/test_lang_utils.py

import pytest
from package.lang_utils import select_language

def test_select_language_returns_code(monkeypatch):
    # Simulo che ask_choice (in package.transcriber) torni "en (Inglese)"
    responses = iter(["en (Inglese)"])
    def fake_ask_choice(prompt, options):
        assert "In quale lingua" in prompt
        assert any(opt.startswith("en (Inglese)") for opt in options)
        return next(responses)

    # Monkey‐patch di ask_choice dentro a package.transcriber
    import package.transcriber as trans_mod
    monkeypatch.setattr(trans_mod, "ask_choice", fake_ask_choice)

    # La funzione deve restituire solo "en"
    lang_code = select_language()
    assert lang_code == "en"
