# src/package/logger.py

"""
Logging applicativo.

Gestisce la scrittura del log benchmark delle trascrizioni in modo stabile
e riproducibile (host, file, modello, device, modalità, tipo, parole, lingua).
"""

from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from datetime import datetime

from package.config import LOG_DIR, LOG_FILE


@dataclass(frozen=True)
class DeviceInfo:
    """Coppia device richiesto / device effettivo."""

    requested: str
    actual: str


@dataclass(frozen=True)
class TranscriptionMetrics:
    """Metriche della trascrizione."""

    durata_audio: str
    duration_proc: float
    parola_count: int


@dataclass(frozen=True)
class OutputInfo:
    """Informazioni accessorie di output."""

    txt_filename: str = ""
    lang: str | None = None


@dataclass(frozen=True)
class LogTranscriptionParams:
    """
    Parametri aggregati per il logger.

    La struttura raggruppa concetti coesi:
    - contesto input/modello
    - device
    - metriche
    - output
    """

    file_audio: str
    modello: str
    modalita: str
    tipo: str
    device: DeviceInfo
    metrics: TranscriptionMetrics
    output: OutputInfo = OutputInfo()

    @classmethod
    def from_legacy(cls, **kwargs) -> "LogTranscriptionParams":
        """
        Costruisce i parametri aggregati a partire dai keyword args legacy.

        Supporta alias storici:
        - lingua -> lang
        - proc_time -> duration_proc
        """
        lang = kwargs.get("lang")
        if lang is None:
            lang = kwargs.get("lingua")

        duration_proc = kwargs.get("duration_proc")
        if duration_proc is None:
            duration_proc = kwargs.get("proc_time")

        return cls(
            file_audio=kwargs["file_audio"],
            modello=kwargs["modello"],
            modalita=kwargs["modalita"],
            tipo=kwargs["tipo"],
            device=DeviceInfo(
                requested=kwargs["device_req"],
                actual=kwargs["device_act"],
            ),
            metrics=TranscriptionMetrics(
                durata_audio=kwargs["durata_audio"],
                duration_proc=duration_proc,
                parola_count=kwargs["parola_count"],
            ),
            output=OutputInfo(
                txt_filename=kwargs.get("txt_filename", ""),
                lang=lang,
            ),
        )


def log_transcription(*args, params: LogTranscriptionParams | None = None, **kwargs) -> None:
    """
    Logga i dettagli della trascrizione.

    Contratto nuovo:
    - log_transcription(params=LogTranscriptionParams(...))

    Compatibilità legacy:
    - log_transcription(file_audio=..., modello=..., ...)
    """
    if args:
        raise TypeError(
            "log_transcription() non accetta più argomenti posizionali. "
            "Usa params=LogTranscriptionParams(...) oppure keyword args legacy."
        )

    if params is None:
        params = LogTranscriptionParams.from_legacy(**kwargs)

    hostname = kwargs.get("hostname") or platform.node()

    riga = (
        f"[{datetime.now():%Y-%m-%d %H:%M:%S}] "
        f"Host: {hostname} | "
        f"File: {params.file_audio} | "
        f"Modello: {params.modello} | "
        f"Device richiesto: {params.device.requested} | "
        f"Device effettivo: {params.device.actual} | "
        f"Modalità: {params.modalita} | "
        f"Tipo: {params.tipo} | "
        f"Durata audio: {params.metrics.durata_audio} | "
        f"Tempo elaborazione: {params.metrics.duration_proc} | "
        f"Parole trascritte: {params.metrics.parola_count}"
    )

    if params.output.lang:
        riga += f" | Lingua: {params.output.lang}"

    if params.output.txt_filename:
        riga += f" | Output: {params.output.txt_filename}"

    riga += "\n"

    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(riga)
