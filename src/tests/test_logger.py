import os
import re
import pytest

import package.logger as logger_mod

def test_log_transcription(tmp_path, monkeypatch):
    """
    Verifica che log_transcription appenda una riga con il formato corretto
    nel file LOG_FILE, usando LOG_DIR/LOG_FILE patchati.
    """
    # Preparo un fake log dir/file
    fake_dir  = tmp_path / "log"
    fake_file = fake_dir / "whisper_benchmark.log"

    # Monkeypatch della variabile LOG_DIR e LOG_FILE nel modulo logger
    monkeypatch.setattr(logger_mod, "LOG_DIR", str(fake_dir))
    monkeypatch.setattr(logger_mod, "LOG_FILE", str(fake_file))

    # Creo manualmente la cartella (logger.py la crea a import, ma noi l'abbiamo sovrascritta)
    fake_dir.mkdir()

    # Chiamo la funzione con parametri di test
    logger_mod.log_transcription(
        hostname="HostX",
        file_audio="audio/test.mp3",
        modello="medium",
        device_req="cpu",
        device_act="cuda",
        modalita="Standard",
        tipo="completa",
        durata_audio="0:02:30",
        proc_time="0m1.23s",
        parola_count=123
    )

    # Il file di log deve esistere e contenere la riga con il pattern atteso
    assert fake_file.exists(), "Il file di log non è stato creato"

    # Leggiamo con encoding esplicito UTF-8 per evitare problemi su Windows
    text = fake_file.read_text(encoding="utf-8")

    # Costruiamo un regex per verificare il contenuto
    pattern = (
        r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] "
        r"Host: HostX \| "
        r"File: audio/test\.mp3 \| "
        r"Modello: medium \| "
        r"Device richiesto: cpu \| "
        r"Device effettivo: cuda \| "
        r"Modalità: Standard \| "
        r"Tipo: completa \| "
        r"Durata audio: 0:02:30 \| "
        r"Tempo elaborazione: 0m1\.23s \| "
        r"Parole trascritte: 123"
    )
    assert re.search(pattern, text), f"Contenuto log non corrisponde: {text}"
