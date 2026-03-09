import os
import re
import types
import pytest

from package.core import TranscribeParams, transcribe

# ------------------------------------------------------------------ #
# DummyModel per patchare whisper.load_model                         #
# ------------------------------------------------------------------ #
class DummyModel:
    def __init__(self, device):
        self._device = device

    def parameters(self):
        yield types.SimpleNamespace(device=self._device)

    def transcribe(self, path, **_):
        base = os.path.basename(path)
        return {"text": f"TRANSCRIBED-{base.upper()}"}


@pytest.fixture(autouse=True)
def patch_whisper(monkeypatch):
    """Sostituisce whisper.load_model con DummyModel."""
    import package.core as core_mod
    monkeypatch.setattr(
        core_mod.whisper,
        "load_model",
        lambda name, device: DummyModel(device=f"fake-{device}"),
    )

# ------------------------------------------------------------------ #
# 1) Trascrizione COMPLETA                                           #
# ------------------------------------------------------------------ #
def test_transcribe_completa_keys_and_values(tmp_path):
    audio_path = tmp_path / "file.wav"
    audio_path.write_bytes(b"RIFF.")

    res = transcribe(
        TranscribeParams(
            audio_path=str(audio_path),
            modello="small",
            device="cpu",
            lang="it",
            modalita_acc=False,
            tipo="completa",
        )
    )

    # chiavi e tipi attesi
    expected = {
        "text", "txt_filename", "duration_proc",
        "durata_audio", "device", "parola_count",
    }
    assert set(res.keys()) == expected
    assert res["text"] == "TRANSCRIBED-FILE.WAV"
    assert res["device"] == "fake-cpu"

    # nuovo formato: spazio prima della parentesi
    assert res["txt_filename"] == "file (sml_std) (lang_it).txt"

# ------------------------------------------------------------------ #
# 2) Trascrizione PARZIALE – pattern del nome                        #
# ------------------------------------------------------------------ #
def test_transcribe_parziale_pattern(tmp_path):
    audio_path = tmp_path / "clip.wav"
    audio_path.write_bytes(b"RIFF.")

    res = transcribe(
        TranscribeParams(
            audio_path=str(audio_path),
            modello="base",
            device="cuda",
            lang="it",
            modalita_acc=True,
            tipo="parziale",
            intervallo=("00:00:03", "00:00:08"),
        )
    )

    assert res["text"] == "TRANSCRIBED-CLIP.WAV"
    assert res["device"] == "fake-cuda"

    # nome file atteso: clip (0003_0008) (bse_acc).txt
    assert re.match(r"^clip \(0003_0008\) \(bse_acc\) \(lang_it\)\.txt$", res["txt_filename"])

# ------------------------------------------------------------------ #
# 3) Parziale senza timestamp => TypeError                           #
# ------------------------------------------------------------------ #
def test_transcribe_parziale_missing_timestamps(tmp_path):
    path = tmp_path / "x.wav"
    path.write_bytes(b"")

    with pytest.raises(TypeError):
        transcribe(
            TranscribeParams(
                audio_path=str(path),
                modello="base",
                device="cpu",
                tipo="parziale",
                intervallo=None,
            )
        )

# ------------------------------------------------------------------ #
# 4) Golden-file: modello restituisce testo pre-definito             #
# ------------------------------------------------------------------ #
def test_transcribe_with_golden_text(tmp_path):
    test_dir   = os.path.dirname(__file__)
    golden_ref = os.path.join(test_dir, "resources",
                              "test_expected_golden_output.txt")
    assert os.path.exists(golden_ref), f"Golden file non trovato: {golden_ref}"

    golden_txt     = tmp_path / "golden.txt"
    golden_content = open(golden_ref, encoding="utf-8").read()
    golden_txt.write_text(golden_content, encoding="utf-8")

    import package.core as core_mod
    mp = pytest.MonkeyPatch()

    class GM(DummyModel):
        def transcribe(self, *_a, **_k):
            return {"text": golden_txt.read_text(encoding="utf-8")}

    mp.setattr(core_mod.whisper,
               "load_model",
               lambda name, device: GM(device=f"fake-{device}"))

    try:
        res = transcribe(
            TranscribeParams(
                audio_path=str(golden_txt),
                modello="tiny",
                device="cpu",
                lang="it",
                modalita_acc=False,
                tipo="completa",
            )
        )
        assert res["text"] == golden_content
    finally:
        mp.undo()
