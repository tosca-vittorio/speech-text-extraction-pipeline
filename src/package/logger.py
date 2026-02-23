# src/package/logger.py

import os
from datetime import datetime

from package.config import LOG_DIR, LOG_FILE

# Assicuriamoci che la cartella di log esista
os.makedirs(LOG_DIR, exist_ok=True)

def log_transcription(hostname: str,
                      file_audio: str,
                      modello: str,
                      device_req: str,
                      device_act: str,
                      modalita: str,
                      tipo: str,
                      durata_audio: str,
                      proc_time: str,
                      parola_count: int) -> None:
    """
    Appende una riga a LOG_FILE con il seguente formato:
      [YYYY-MM-DD HH:MM:SS] Host: ... | File: ... | Modello: ... | ...
    Mantiene esattamente lo stesso formato di prima, ma
    scrive su LOG_FILE (in log/whisper_benchmark.log).

    Args:
        hostname:      nome della macchina
        file_audio:    path del file audio trascritto
        modello:       modello Whisper utilizzato
        device_req:    device richiesto (cuda/cpu)
        device_act:    device effettivamente usato
        modalita:      "Standard" o "Accurata"
        tipo:          "completa" o "parziale"
        durata_audio:  durata del file audio (hh:mm:ss)
        proc_time:     tempo di elaborazione (es. "1m23.45s")
        parola_count:  numero di parole trascritte
    """
    riga = (
        f"[{datetime.now():%Y-%m-%d %H:%M:%S}] "
        f"Host: {hostname} | "
        f"File: {file_audio} | "
        f"Modello: {modello} | "
        f"Device richiesto: {device_req} | "
        f"Device effettivo: {device_act} | "
        f"Modalità: {modalita} | "
        f"Tipo: {tipo} | "
        f"Durata audio: {durata_audio} | "
        f"Tempo elaborazione: {proc_time} | "
        f"Parole trascritte: {parola_count}\n"
    )
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(riga)
