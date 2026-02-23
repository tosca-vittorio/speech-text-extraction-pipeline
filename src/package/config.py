# src/package/config.py

import os

# Base directory del progetto (dove risiedono cartelle audio/, log/, src/)
# Partendo da config.py, saliamo di due directory:
# src/package/config.py → src/package → src → project-root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Percorso cartella audio e lista estensioni supportate
AUDIO_DIR  = os.path.join(BASE_DIR, "audio")
AUDIO_EXTS = (".mp3", ".mp4", ".wav", ".m4a")

# eventuale cartella con audio-test
TEST_AUDIO_DIR = os.path.join(BASE_DIR, "src", "tests", "resources")

# Percorso cartella log e file di log
LOG_DIR  = os.path.join(BASE_DIR, "log")
LOG_FILE = os.path.join(LOG_DIR, "whisper_benchmark.log")

TRANSCRIPTION_DIR = os.path.join(BASE_DIR, "doc", "03_Transcriptions")
os.makedirs(TRANSCRIPTION_DIR, exist_ok=True)

# Parametri di default per la trascrizione
DEFAULT_LANG     = "it"
MODEL_OPTIONS    = ["tiny", "base", "small", "medium"]
DEVICE_OPTIONS   = ["cuda", "cpu"]
MODALITA_OPTIONS = ["Standard – più leggibile, Whisper filtra automaticamente (consigliata per testo scorrevole)", "Accurata – più fedele, nessun filtro, adatta a sottotitoli o NLP"]
SCOPE_OPTIONS    = ["Tutto", "Solo una parte"]







