import os
import re
import pytest

import package.logger as logger_mod

def test_log_transcription_without_language(tmp_path, monkeypatch):
    """
    Verifica che log_transcription appenda una riga con il formato corretto
    nel file LOG_FILE, usando LOG_DIR/LOG_FILE patchati, quando lingua=None.
    """
    # Preparo un fake log dir/file
    fake_dir  = tmp_path / "log"
    fake_file = fake_dir / "whisper_benchmark.log"

    # Monkeypatch della variabile LOG_DIR e LOG_FILE nel modulo logger
    monkeypatch.setattr(logger_mod, "LOG_DIR", str(fake_dir))
    monkeypatch.setattr(logger_mod, "LOG_FILE", str(fake_file))

    # Ricreo la cartella, dato che logger.py l'ha creata a import time con il vecchio valore
    fake_dir.mkdir()

    # Chiamo la funzione con parametri di test (senza lingua)
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
        parola_count=123,
        lingua=None
    )

    # Il file di log deve esistere e contenere la riga con il pattern atteso (senza "Lingua:")
    assert fake_file.exists(), "Il file di log non è stato creato"

    # Leggiamo con encoding esplicito UTF-8 per evitare problemi su Windows
    text = fake_file.read_text(encoding="utf-8")

    # Costruiamo un regex per verificare il contenuto (senza parte "Lingua:")
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
    assert "Lingua:" not in text, "Non dovrebbe esserci il campo 'Lingua:' quando lingua=None"


def test_log_transcription_with_language(tmp_path, monkeypatch):
    """
    Verifica che log_transcription appenda una riga con il formato corretto
    nel file LOG_FILE, includendo "| Lingua: <codice>" quando lingua è specificata.
    """
    # Preparo un fake log dir/file
    fake_dir  = tmp_path / "log"
    fake_file = fake_dir / "whisper_benchmark.log"

    # Monkeypatch della variabile LOG_DIR e LOG_FILE nel modulo logger
    monkeypatch.setattr(logger_mod, "LOG_DIR", str(fake_dir))
    monkeypatch.setattr(logger_mod, "LOG_FILE", str(fake_file))

    # Ricreo la cartella, dato che logger.py l'ha creata a import time con il vecchio valore
    fake_dir.mkdir()

    # Chiamo la funzione con parametri di test, specificando lingua="en"
    logger_mod.log_transcription(
        hostname="HostY",
        file_audio="audio/test2.wav",
        modello="large",
        device_req="cuda",
        device_act="cuda",
        modalita="Accurata",
        tipo="parziale",
        durata_audio="0:05:00",
        proc_time="0m5.00s",
        parola_count=456,
        lingua="en"
    )

    # Il file di log deve esistere e contenere la riga con il pattern atteso (con "Lingua: en")
    assert fake_file.exists(), "Il file di log non è stato creato"

    # Leggiamo con encoding esplicito UTF-8
    text = fake_file.read_text(encoding="utf-8")

    # Costruiamo un regex per verificare il contenuto (inclusa parte "Lingua: en")
    pattern = (
        r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] "
        r"Host: HostY \| "
        r"File: audio/test2\.wav \| "
        r"Modello: large \| "
        r"Device richiesto: cuda \| "
        r"Device effettivo: cuda \| "
        r"Modalità: Accurata \| "
        r"Tipo: parziale \| "
        r"Durata audio: 0:05:00 \| "
        r"Tempo elaborazione: 0m5\.00s \| "
        r"Parole trascritte: 456 \| "
        r"Lingua: en"
    )
    assert re.search(pattern, text), f"Contenuto log non corrisponde: {text}"
