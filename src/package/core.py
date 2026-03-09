# src/package/core.py

"""
Modulo core: gestisce la trascrizione audio tramite Whisper,
calcola le metriche di performance e genera il nome del file di output.
"""

import os
import time
from dataclasses import dataclass

import whisper

from package.audio import get_audio_duration
from package.naming import NamingParams, genera_nome_file_output


@dataclass(frozen=True)
class TranscribeParams:
    """Parametri per la trascrizione Whisper (core.transcribe)."""

    audio_path: str
    modello: str
    device: str
    lang: str = "it"
    modalita_acc: bool = False
    tipo: str = "completa"
    intervallo: tuple[str, str] | None = None


def _build_whisper_params(lang: str, modalita_acc: bool) -> dict:
    """Costruisce i parametri per Whisper in base a lingua e modalità."""
    params: dict = {"language": lang}
    if modalita_acc:
        params.update(
            temperature=0,
            condition_on_previous_text=False,
            compression_ratio_threshold=10.0,
            logprob_threshold=-1.0,
            no_speech_threshold=0.05,
        )
    return params


def _build_output_txt_filename(
    audio_path: str,
    modello: str,
    modalita_acc: bool,
    tipo: str,
    inizio: str | None,
    fine: str | None,
    lang: str,
) -> str:
    """Genera il nome del file .txt di output (senza path)."""
    base = os.path.basename(audio_path)
    base_name = os.path.splitext(base)[0]
    modalita = "accurata" if modalita_acc else "standard"

    nome_base = genera_nome_file_output(
        NamingParams(
            base_name=base_name,
            modello=modello,
            modalita=modalita,
            tipo=tipo,
            inizio=inizio,
            fine=fine,
            lang=lang,
        )
    )
    return f"{nome_base}.txt"

def transcribe(req: TranscribeParams) -> dict:
    """
    Esegue la trascrizione di `req.audio_path` con Whisper e raccoglie:
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
    if req.tipo == "parziale" and req.intervallo is None:
        raise TypeError("Per trascrizione parziale servono parametri 'inizio' e 'fine'.")


    inizio, fine = (req.intervallo if req.intervallo is not None else (None, None))

    # Caricamento modello e determinazione device attivo
    model = whisper.load_model(req.modello, device=req.device)
    actual_device = next(model.parameters()).device

    # Parametri Whisper
    params = _build_whisper_params(req.lang, req.modalita_acc)

    print(f"🎧 Inizio trascrizione di: {req.audio_path}")
    start_time = time.perf_counter()
    result = model.transcribe(req.audio_path, **params)
    duration_proc = time.perf_counter() - start_time

    durata_audio = get_audio_duration(req.audio_path)
    parole = len(result["text"].split())

    txt_filename = _build_output_txt_filename(
        audio_path=req.audio_path,
        modello=req.modello,
        modalita_acc=req.modalita_acc,
        tipo=req.tipo,
        inizio=inizio,
        fine=fine,
        lang=req.lang,
    )

    return {
        "text": result["text"],
        "txt_filename": txt_filename,
        "duration_proc": duration_proc,
        "durata_audio": durata_audio,
        "device": actual_device,
        "parola_count": parole,
    }
