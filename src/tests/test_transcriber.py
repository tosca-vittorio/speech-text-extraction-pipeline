import os
from pathlib import Path
import pytest

import package.transcriber as trans_mod

# ------------------------------------------------------------------ #
# Fixture di isolamento globale                                      #
# ------------------------------------------------------------------ #
@pytest.fixture(autouse=True)
def isolate(monkeypatch, tmp_path):
    """
    • Re-indirizza AUDIO_DIR e TRANSCRIPTION_DIR in tmp_path
    • Stub di funzioni I/O + cattura chiamate
    • Reimposta trans_mod.ARGS.overwrite su None a ogni test
    """
    monkeypatch.setattr(trans_mod, "AUDIO_DIR", str(tmp_path))
    monkeypatch.setattr(trans_mod, "TRANSCRIPTION_DIR", str(tmp_path))
    trans_mod.ARGS.overwrite = None                                      # reset

    wav_in   = tmp_path / "ok.wav"
    txt_out  = tmp_path / "ok.txt"           # nome segnaposto; il naming reale cambia
    clip_out = tmp_path / "ok_clip.wav"
    wav_in.touch()

    # ---- list_audio_files → un solo file ----
    monkeypatch.setattr(trans_mod, "list_audio_files", lambda _d: [wav_in.name])

    # ---- durata costante ----
    monkeypatch.setattr(trans_mod, "get_audio_duration", lambda _p: "0:01:00")

    # ---- os.path.exists valida solo i nostri artefatti ----
    valid = {str(wav_in), str(txt_out), str(clip_out)}
    monkeypatch.setattr(trans_mod.os.path, "exists", lambda p: str(p) in valid)

    # ---- stub transcribe / logger / taglio ----
    calls = {}

    def fake_transcribe(audio_path, **kwargs):
        calls["transcribe"] = (audio_path, kwargs)
        return {
            "text": "TESTO",
            "txt_filename": str(txt_out),
            "duration_proc": 1.23,
            "durata_audio": "0:00:10",
            "device": "fake-cpu",
            "parola_count": 42,
        }

    monkeypatch.setattr(trans_mod, "transcribe", fake_transcribe)
    monkeypatch.setattr(trans_mod, "log_transcription",
                        lambda **kw: calls.setdefault("log", kw))

    def fake_cut(_in, _ini, _fine, output_file=None, *_a, **_kw):
        out = Path(output_file or clip_out)
        out.touch()
        return str(out)

    monkeypatch.setattr(trans_mod, "taglia_audio", fake_cut)

    return calls


# ------------------------------------------------------------------ #
# Helper: esegue main() e cattura stdout / exit code                 #
# ------------------------------------------------------------------ #
def run_and_capture(capsys):
    with pytest.raises(SystemExit) as exc:
        trans_mod.main()
    out, err = capsys.readouterr()
    return exc.value.code, out, err


# ------------------------------------------------------------------ #
# ► 1. Uscita immediata                                              #
# ------------------------------------------------------------------ #
def test_exit_immediate(monkeypatch, capsys):
    monkeypatch.setattr(trans_mod, "ask_choice", lambda *_: "Esci")
    code, out, _ = run_and_capture(capsys)
    assert code == 0 and "Arrivederci" in out


# ------------------------------------------------------------------ #
# ► 2. Flusso completo                                               #
# ------------------------------------------------------------------ #
def test_flusso_completa(monkeypatch, capsys, isolate):
    seq = iter([
        "Trascrivi",               # Menu iniziale
        "ok.wav",                  # Selezione file
        "tiny",                    # Scelta modello
        "cpu",                     # Scelta device
        "en (Inglese)",            # <<< NUOVO: scelta lingua
        "Standard – filtro automatico",  # Modalità
        "Tutto",                   # Ambito
        "Esci"                     # Uscita finale
    ])
    monkeypatch.setattr(trans_mod, "ask_choice", lambda *_: next(seq))
    code, out, _ = run_and_capture(capsys)

    audio_path, kwargs = isolate["transcribe"]
    assert audio_path.endswith(".wav") and kwargs["modello"] == "tiny"
    assert kwargs["lang"] == "en"                              # Verifica lingua passata
    assert isolate["log"]["parola_count"] == 42
    assert ".txt" in out and code == 0


# ------------------------------------------------------------------ #
# ► 3. Flusso parziale                                               #
# ------------------------------------------------------------------ #
def test_flusso_parziale(monkeypatch, capsys, isolate):
    seq = iter([
        "Trascrivi",               # Menu iniziale
        "ok.wav",                  # Selezione file
        "tiny",                    # Scelta modello
        "cpu",                     # Scelta device
        "en (Inglese)",            # <<< NUOVO: scelta lingua
        "Standard – filtro automatico",  # Modalità
        "Solo una parte",          # Ambito
        "No"                       # Risposta al prompt “Conservi clip?”
    ])
    monkeypatch.setattr(trans_mod, "ask_choice", lambda *_: next(seq))
    inputs = iter(["00:00:05", "00:00:10"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    code, out, _ = run_and_capture(capsys)

    _, kwargs = isolate["transcribe"]
    # Verifica che inizio/fine siano passati correttamente
    assert kwargs["inizio"] == "00:00:05" and kwargs["fine"] == "00:00:10"
    assert kwargs["lang"] == "en"                              # Verifica lingua passata
    assert ".txt" in out and code == 0


# ------------------------------------------------------------------ #
# ► 4. Gestione errore da transcribe                                 #
# ------------------------------------------------------------------ #
def test_error_handling_and_recovery(monkeypatch):
    seq = iter([
        "Trascrivi",               # Menu iniziale
        "ok.wav",                  # Selezione file
        "tiny",                    # Scelta modello
        "cpu",                     # Scelta device
        "en (Inglese)",            # <<< NUOVO: scelta lingua
        "Standard – filtro automatico",  # Modalità
        "Solo una parte",          # Ambito
        "No"                       # Risposta al prompt “Conservi clip?”
    ])
    monkeypatch.setattr(trans_mod, "ask_choice", lambda *_: next(seq))
    monkeypatch.setattr(
        trans_mod, "transcribe",
        lambda *_a, **_k: (_ for _ in ()).throw(TypeError("Parametri mancanti"))
    )
    inputs = iter(["00:00:05", "00:00:10"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))
    with pytest.raises(TypeError):
        trans_mod.main()


# ------------------------------------------------------------------ #
# ► 5. Overwrite flag: YES                                           #
# ------------------------------------------------------------------ #
def test_overwrite_yes(monkeypatch, capsys, isolate, tmp_path):
    trans_mod.ARGS.overwrite = "yes"
    # pre-creo un txt per simulare conflitto
    (tmp_path / "ok.txt").write_text("vecchio")

    seq = iter([
        "Trascrivi",               # Menu iniziale
        "ok.wav",                  # Selezione file
        "tiny",                    # Scelta modello
        "cpu",                     # Scelta device
        "en (Inglese)",            # <<< NUOVO: scelta lingua
        "Standard – filtro automatico",  # Modalità
        "Tutto",                   # Ambito
        "Esci"                     # Uscita finale
    ])
    monkeypatch.setattr(trans_mod, "ask_choice", lambda *_: next(seq))
    code, out, _ = run_and_capture(capsys)

    # deve aver sovrascritto senza prompt
    assert "Salvataggio annullato" not in out
    assert code == 0


# ------------------------------------------------------------------ #
# ► 6. Overwrite flag: NO                                            #
# ------------------------------------------------------------------ #
def test_overwrite_no(monkeypatch, capsys, isolate, tmp_path):
    trans_mod.ARGS.overwrite = "no"
    (tmp_path / "ok.txt").write_text("vecchio")

    seq = iter([
        "Trascrivi",               # Menu iniziale
        "ok.wav",                  # Selezione file
        "tiny",                    # Scelta modello
        "cpu",                     # Scelta device
        "en (Inglese)",            # <<< NUOVO: scelta lingua
        "Standard – filtro automatico",  # Modalità
        "Tutto",                   # Ambito
        "Esci"                     # Uscita finale
    ])
    monkeypatch.setattr(trans_mod, "ask_choice", lambda *_: next(seq))
    code, out, _ = run_and_capture(capsys)

    # salvataggio rifiutato
    assert "Salvataggio annullato" in out
    assert code == 0


# ------------------------------------------------------------------ #
# ► 7. Prompt overwrite → utente risponde No                          #
# ------------------------------------------------------------------ #
def test_overwrite_prompt_no(monkeypatch, capsys, isolate, tmp_path):
    # flag assente → ARGS.overwrite None (già reset)
    (tmp_path / "ok.txt").write_text("vecchio")

    # prima parte normale, poi alla domanda di overwrite rispondi "No"
    seq = iter([
        "Trascrivi",               # Menu iniziale
        "ok.wav",                  # Selezione file
        "tiny",                    # Scelta modello
        "cpu",                     # Scelta device
        "en (Inglese)",            # <<< NUOVO: scelta lingua
        "Standard – filtro automatico",  # Modalità
        "Tutto",                   # Ambito
        "No"                       # Risposta al prompt overwrite
    ])
    monkeypatch.setattr(trans_mod, "ask_choice", lambda *_: next(seq))

    code, out, _ = run_and_capture(capsys)
    assert "Salvataggio annullato" in out and code == 0


# ------------------------------------------------------------------ #
# ► 8. Prompt overwrite → utente risponde Sì                          #
# ------------------------------------------------------------------ #
def test_overwrite_prompt_yes(monkeypatch, capsys, isolate, tmp_path):
    (tmp_path / "ok.txt").write_text("vecchio")

    seq = iter([
        "Trascrivi",               # Menu iniziale
        "ok.wav",                  # Selezione file
        "tiny",                    # Scelta modello
        "cpu",                     # Scelta device
        "en (Inglese)",            # <<< NUOVO: scelta lingua
        "Standard – filtro automatico",  # Modalità
        "Tutto",                   # Ambito
        "Sì"                       # accetta sovrascrittura
    ])
    monkeypatch.setattr(trans_mod, "ask_choice", lambda *_: next(seq))

    code, out, _ = run_and_capture(capsys)
    assert "Salvataggio annullato" not in out and code == 0
