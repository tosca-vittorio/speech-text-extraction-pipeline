# 🎙️ Speech Text Extraction Pipeline 🚀

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-CLI-lightgrey)
![Tests](https://img.shields.io/badge/tests-49%20passed-brightgreen)

Pipeline CLI Python per trascrivere audio/video tramite Whisper, con flusso guidato, gestione clip parziali, naming consistente degli output e logging benchmark.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux / macOS

pip install -r docs/requirements/requirements.txt
python -m package.transcriber
```

> Nota: se vuoi un setup CPU-only o CUDA, usa i file in `docs/requirements/`.

---

## 1) Stato attuale del progetto (AS-IS)

Il progetto è un **tool CLI locale** (non web app) con architettura modulare sotto `src/package`.

Caratteristiche operative attuali:

- Trascrizione **completa** o **parziale** (taglio clip via ffmpeg)
- Scelta modello Whisper (`tiny`, `base`, `small`, `medium`)
- Scelta device (`cpu`, `cuda`, con fallback automatico a CPU)
- Selezione lingua (`it`, `en`, `fr`, `es`)
- Naming output con tag lingua `(lang_<codice>)`
- Protezione sovrascrittura (`--overwrite yes|no` o prompt)
- Logging benchmark persistente in `logs/`
- Suite test eseguibile sia da root sia da `src/` tramite `python -m pytest`

---

## 2) Prerequisiti

- Python 3.10+
- `ffmpeg` disponibile nel `PATH`
- Ambiente virtuale raccomandato

Verifica:

```bash
python --version
ffmpeg -version
```

---

## 3) Installazione

### 3.1 Setup ambiente virtuale

```bash
python -m venv .venv
```

Attivazione:

- Windows:
```bash
.venv\Scripts\activate
```

- Linux / macOS:
```bash
source .venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

---

### 3.2 Installazione dipendenze

Le requirements sono suddivise per profilo in `docs/requirements/`.

#### Standard

```bash
pip install -r docs/requirements/requirements.txt
```

#### CPU-only

```bash
pip install -r docs/requirements/requirements-cpu.txt
```

#### CUDA

```bash
pip install -r docs/requirements/requirements-cuda.txt
```

> Assicurarsi che il profilo combaci con il proprio ambiente (driver GPU, wheel torch compatibili).

---

## 4) Esecuzione

### Modalità interattiva (attuale)

Da root repository:

```bash
python -m package.transcriber
```

Oppure da `src/`:

```bash
cd src
python -m package.transcriber
```

> Nota: attualmente il progetto utilizza layout `src/` non installabile.
> In una futura milestone (A3) verrà introdotto `pyproject.toml` con installazione editable.

---

### Flag disponibili

```bash
python -m package.transcriber --overwrite yes
python -m package.transcriber --overwrite no
```

Semantica:

- `--overwrite yes` → sovrascrive automaticamente
- `--overwrite no` → non sovrascrive mai
- senza flag → chiede conferma via prompt

---

## 5) Flusso CLI reale

All’avvio:

1. Azione (`Trascrivi` / `Esci`)
2. Selezione file da `input/`
3. Modello Whisper
4. Device (`cuda` / `cpu`)
5. Lingua audio
6. Modalità (`Standard` / `Accurata`)
7. Scope (`Tutto` / `Solo una parte`)

Se scope parziale:

- Validazione timestamp
- Taglio clip via ffmpeg
- Possibilità di conservare o eliminare la clip temporanea

Al termine:

- Salvataggio `.txt` in `output/transcriptions/`
- Scrittura riga benchmark in `logs/whisper_benchmark.log`
- Riepilogo console (tempo, durata, device, lingua)

---

## 6) Struttura repository

```text
.
├── README.md
├── .gitignore
├── pytest.ini
│
├── docs/
│   ├── CHANGELOG.md
│   ├── TIMELINE.md
│   ├── ARCHITECTURE.md
│   └── requirements/
│       ├── requirements.txt
│       ├── requirements-cpu.txt
│       └── requirements-cuda.txt
│
├── input/
│   └── audio/
│       └── .gitkeep
│
├── output/
│   ├── audio/
│   │   └── .gitkeep
│   └── transcriptions/
│       └── .gitkeep
│
├── logs/
│   └── .gitkeep
│
├── tools/
│   └── clean_project.sh
│
└── src/
    ├── package/
    │   ├── __init__.py
    │   ├── transcriber.py
    │   ├── core.py
    │   ├── audio.py
    │   ├── naming.py
    │   ├── logger.py
    │   ├── cli_utils.py
    │   ├── lang_utils.py
    │   ├── config.py
    │   └── errors.py
    │
    └── tests/
        ├── __init__.py
        ├── conftest.py
        ├── test_audio.py
        ├── test_cli_utils.py
        ├── test_config.py
        ├── test_core.py
        ├── test_lang_utils.py
        ├── test_logger.py
        ├── test_naming.py
        ├── test_transcriber.py
        │
        └── resources/
            └── *.wav
```
---

## 7) Path runtime importanti

Definiti centralmente in `src/package/config.py`.

- Input media: `input/audio/`
- Output trascrizioni: `output/transcriptions/`
- Log benchmark: `logs/whisper_benchmark.log`
- Temp pytest: `src/tests/tmp/` (non versionata; path forzato via `src/tests/conftest.py`)

---

## 8) Testing

La suite è **cwd-agnostic**: eseguibile sia da root sia da `src/`:

Da root:

```bash
python -m pytest
```

Attualmente: **49 test passed**

---

## 9) Script di pulizia

Script sicuro in:

```bash
tools/clean_project.sh
```

Modalità preview:

```bash
DRY_RUN=true VERBOSE=true tools/clean_project.sh
```

Comportamento:

- Pulisce cache Python, pytest, build artifacts
- NON cancella file `.txt` o media utente
- Output e logs sono opt-in

---

## 10) Convenzioni naming output

Gestite da `naming.py`.

I file includono:

- nome base input
- modello
- modalità
- intervallo (se parziale)
- lingua `(lang_<codice>)`

Questo garantisce tracciabilità completa.

---

## 11) Documentazione correlata

- Architettura tecnica: `docs/ARCHITECTURE.md`
- Storico modifiche: `docs/CHANGELOG.md`
- Timeline ingegneristica: `docs/TIMELINE.md`

---

## 12) Roadmap tecnica (estratto)

Prossime milestone:

- Packaging installabile (`pyproject.toml`)
- Docker CPU baseline
- Modalità batch non interattiva
- Smoke test E2E
- CI minimale

---

© Speech Text Extraction Pipeline
