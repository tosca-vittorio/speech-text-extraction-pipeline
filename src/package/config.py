# src/package/config.py

import os

# Base directory del progetto (dove risiedono cartelle audio/, log/, src/)
# Partendo da config.py, saliamo di due directory:
# src/package/config.py → src/package → src → project-root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# INPUT
# Percorso cartella audio e lista estensioni supportate
INPUT_AUDIO_DIR = os.path.join(BASE_DIR, "input", "audio")
INPUT_VIDEO_DIR = os.path.join(BASE_DIR, "input", "video")

# OUTPUT (trascrizioni)
TRANSCRIPTION_DIR = os.path.join(BASE_DIR, "output", "transcriptions")

# Estensioni supportate (audio + container video con audio)
MEDIA_EXTS = (".mp3", ".mp4", ".wav", ".m4a")

# TEST AUDIO
TEST_AUDIO_DIR = os.path.join(BASE_DIR, "src", "tests", "resources")

# LOG
LOG_DIR  = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "whisper_benchmark.log")

# Parametri di default per la trascrizione
DEFAULT_LANG     = "it"
MODEL_OPTIONS    = ["tiny", "base", "small", "medium"]
DEVICE_OPTIONS   = ["cuda", "cpu"]
MODALITA_OPTIONS = ["Standard – più leggibile, Whisper filtra automaticamente (consigliata per testo scorrevole)", "Accurata – più fedele, nessun filtro, adatta a sottotitoli o NLP"]
SCOPE_OPTIONS    = ["Tutto", "Solo una parte"]
