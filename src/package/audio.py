# src/package/audio.py
import os
import subprocess
import wave
import contextlib
from datetime import timedelta
from pathlib import Path

from package.config import AUDIO_DIR, AUDIO_EXTS

# -------------------------------------------------------------------------------------- #
# Utility                                                                                 #
# -------------------------------------------------------------------------------------- #
def list_audio_files(directory: str | None = None) -> list[str]:
    """
    Restituisce i nomi dei file audio presenti in `directory`
    (default: AUDIO_DIR) filtrando per estensioni in AUDIO_EXTS.
    """
    dir_to_scan = directory or AUDIO_DIR
    return [
        f
        for f in os.listdir(dir_to_scan)
        if f.lower().endswith(AUDIO_EXTS)
    ]


def valida_timestamp(ts: str) -> str | None:
    """
    Valida e normalizza una stringa mm:ss o hh:mm:ss → hh:mm:ss.
    Ritorna None se il formato non è corretto.
    """
    try:
        parts = [int(p) for p in ts.strip().split(":")]
        if len(parts) == 2:
            m, s = parts
            return f"00:{m:02}:{s:02}"
        if len(parts) == 3:
            h, m, s = parts
            return f"{h:02}:{m:02}:{s:02}"
    except ValueError:
        pass
    return None


def timestamp_in_secondi(ts: str) -> int:
    """Converte hh:mm:ss in secondi interi."""
    h, m, s = [int(p) for p in ts.strip().split(":")]
    return h * 3600 + m * 60 + s


# -------------------------------------------------------------------------------------- #
# Operazioni audio                                                                        #
# -------------------------------------------------------------------------------------- #
def taglia_audio(
    input_file: str,
    inizio: str,
    fine: str,
    output_file: str | None = None,
) -> str:
    """
    Estrae, tramite ffmpeg, il segmento [inizio-fine] da `input_file`.

    Se `output_file` è None, salva nella stessa cartella di `input_file`
    con nome  <stem>_clip.wav  (es.  video.mp4 → video_clip.wav).
    Ritorna il percorso completo del file generato.
    """
    if output_file is None:
        inp_path = Path(input_file)
        output_file = str(inp_path.with_name(f"{inp_path.stem}_clip.wav"))

    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        inizio,
        "-to",
        fine,
        "-i",
        input_file,
        output_file,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_file


def get_audio_duration(file_path: str) -> str:
    """
    Ritorna la durata del file audio sotto forma "hh:mm:ss".

    • Per .wav si usa il modulo wave.  
    • Per gli altri formati si interroga ffprobe.  
    Se qualcosa va storto restituisce "N/A".
    """
    try:
        # --- caso WAV (senza ffprobe) --------------------------------------------------
        if file_path.lower().endswith(".wav"):
            with contextlib.closing(wave.open(file_path, "r")) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                return str(timedelta(seconds=round(frames / rate)))

        # --- altri formati: ffprobe ----------------------------------------------------
        res = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                file_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        text = res.stdout.decode().strip() if isinstance(res.stdout, bytes) else str(res.stdout).strip()
        dur = float(text)
        return str(timedelta(seconds=round(dur)))

    except Exception:
        return "N/A"
