# src/package/logger.py

import os
from datetime import datetime

from package.config import LOG_DIR, LOG_FILE

def log_transcription(
    hostname: str,
    file_audio: str,
    modello: str,
    device_req: str,
    device_act: str,
    modalita: str,
    tipo: str,
    durata_audio: str,
    proc_time: str,
    parola_count: int,
    lingua: str | None = None,  # parametro opzionale aggiunto
) -> None:
    """
    Appende una riga a LOG_FILE con il seguente formato:
      [YYYY-MM-DD HH:MM:SS] Host: ... | File: ... | Modello: ... | ... | Parole trascritte: N [| Lingua: <codice>]

    Mantiene esattamente lo stesso formato di prima; se 'lingua' non è None,
    aggiunge " | Lingua: <codice>" alla fine.

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
        lingua:        codice ISO della lingua (es. "it", "en"); se None, non aggiunge il tag lingua
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
        f"Parole trascritte: {parola_count}"
    )

    if lingua:
        riga += f" | Lingua: {lingua}"

    riga += "\n"

    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(riga)
