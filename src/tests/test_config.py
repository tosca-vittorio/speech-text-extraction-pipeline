# tests/test_config.py

import os
import importlib
import pytest

import package.config as cfg

def test_paths_exist_and_consistent(tmp_path, monkeypatch):
    """
    Verifica che AUDIO_DIR e LOG_DIR puntino a cartelle reali quando BASE_DIR è corretto.
    """
    # 1) Override di BASE_DIR su tmp_path
    monkeypatch.setattr(cfg, "BASE_DIR", str(tmp_path))

    # 2) Creazione delle cartelle previste
    (tmp_path / "audio").mkdir()
    (tmp_path / "log").mkdir()

    # 3) Ricarica il modulo config per ri-calcolare AUDIO_DIR e LOG_DIR
    importlib.reload(cfg)

    # 4) Verifica che i path esistano
    assert os.path.isdir(cfg.AUDIO_DIR), f"AUDIO_DIR non trovato: {cfg.AUDIO_DIR}"
    assert os.path.isdir(cfg.LOG_DIR),   f"LOG_DIR non trovato:   {cfg.LOG_DIR}"

    # 5) Verifica che LOG_FILE sia dentro LOG_DIR
    assert cfg.LOG_FILE.startswith(cfg.LOG_DIR), "LOG_FILE non in LOG_DIR"
    assert cfg.LOG_FILE.endswith("whisper_benchmark.log")

    # 6) Controlla che AUDIO_EXTS sia una tupla di stringhe
    assert isinstance(cfg.AUDIO_EXTS, tuple)
    assert all(isinstance(ext, str) for ext in cfg.AUDIO_EXTS)

def test_default_options_valid():
    """
    Verifica che le opzioni di default siano definite, del tipo corretto e non vuote.
    """
    # Lingua di default
    assert hasattr(cfg, "DEFAULT_LANG"), "Manca DEFAULT_LANG"
    assert isinstance(cfg.DEFAULT_LANG, str), "DEFAULT_LANG deve essere una stringa"
    assert cfg.DEFAULT_LANG, "DEFAULT_LANG non può essere vuota"

    # Collezioni di opzioni
    for attr in ("MODEL_OPTIONS", "DEVICE_OPTIONS", "MODALITA_OPTIONS", "SCOPE_OPTIONS"):
        assert hasattr(cfg, attr), f"Manca attributo {attr}"
        opts = getattr(cfg, attr)
        assert isinstance(opts, (list, tuple)), f"{attr} deve essere lista o tupla"
        assert len(opts) > 0, f"{attr} non può essere vuoto"
        assert all(isinstance(opt, str) for opt in opts), f"Tutti gli elementi di {attr} devono essere stringhe"
