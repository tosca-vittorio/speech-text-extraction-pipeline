# src/package/core.py

"""
Modulo core: gestisce la trascrizione audio tramite Whisper,
calcola le metriche di performance e genera il nome del file di output.
"""

import os
import time

import whisper

from package.audio import get_audio_duration
from package.naming import genera_nome_file_output

def transcribe(
    audio_path: str,
    modello: str,
    device: str,
    lang: str = "it",
    modalita_acc: bool = False,
    tipo: str = "completa",
    inizio: str = None,
    fine: str = None
) -> dict:
    """
    Esegue la trascrizione di `audio_path` con Whisper e raccoglie:
      - text: il testo trascritto
      - txt_filename: nome del file .txt generato (senza path)
      - duration_proc: tempo di elaborazione in secondi
      - durata_audio: durata del file audio in hh:mm:ss
      - device: device effettivamente usato
      - parola_count: numero di parole trascritte

    Raises:
        TypeError: se tipo='parziale' ma mancano inizio o fine
    """
    # Verifica parametri per trascrizione parziale
    if tipo == "parziale" and (inizio is None or fine is None):
        raise TypeError("Per trascrizione parziale servono parametri 'inizio' e 'fine'.")

    # Caricamento modello e determinazione device attivo
    model = whisper.load_model(modello, device=device)
    actual_device = next(model.parameters()).device

    # Parametri aggiuntivi per modalità accurata
    params = {"language": lang}
    if modalita_acc:
        params.update(
            temperature=0,
            condition_on_previous_text=False,
            compression_ratio_threshold=10.0,
            logprob_threshold=-1.0,
            no_speech_threshold=0.05,
        )

    print(f"🎧 Inizio trascrizione di: {audio_path}")
    # Esecuzione trascrizione e misurazione tempo
    start_time = time.perf_counter()
    result = model.transcribe(audio_path, **params)
    duration_proc = time.perf_counter() - start_time

    # Durata audio
    durata_audio = get_audio_duration(audio_path)

    # Conteggio parole
    parole = len(result["text"].split())

    # Generazione nome base del file di output (senza estensione e senza path)
    base = os.path.basename(audio_path)
    base_name = os.path.splitext(base)[0]
    modalita = "accurata" if modalita_acc else "standard"
    nome_base = genera_nome_file_output(
        base_name=base_name,
        modello=modello,
        modalita=modalita,
        tipo=tipo,
        inizio=inizio,
        fine=fine,
        lang=lang,
    )
    txt_filename = f"{nome_base}.txt"

    return {
        "text": result["text"],
        "txt_filename": txt_filename,
        "duration_proc": duration_proc,
        "durata_audio": durata_audio,
        "device": actual_device,
        "parola_count": parole,
    }
