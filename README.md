# 🎙️ Speech Text Extraction Pipeline

Pipeline CLI Python per trascrivere audio/video con Whisper, con flusso guidato, gestione clip parziali, naming consistente degli output e logging benchmark.

## 1) Stato attuale del progetto (AS-IS)

Il progetto è un **tool CLI locale** (non web app) con architettura modulare in `src/package`.

Funzionalità operative attuali:
- trascrizione **completa** o **parziale** (con taglio clip),
- scelta modello Whisper (`tiny`, `base`, `small`, `medium`),
- scelta device (`cpu`, `cuda`, con fallback automatico a CPU se CUDA non disponibile),
- scelta lingua (`it`, `en`, `fr`, `es`) usata sia in trascrizione sia nel naming/log,
- protezione sovrascrittura output via `--overwrite yes|no` o prompt interattivo,
- log benchmark su file dedicato.

## 2) Prerequisiti

- Python 3.10+
- `ffmpeg` disponibile nel `PATH`
- dipendenze Python in `docs/requirements/`

### Verifica rapida prerequisiti

```bash
python --version
ffmpeg -version
```

## 3) Installazione

### 3.1 Setup ambiente virtuale

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
```

### 3.2 Installazione dipendenze

#### Opzione standard

```bash
pip install -r docs/requirements/requirements.txt
```

#### Opzione CPU-only

```bash
pip install -r docs/requirements/requirements-cpu.txt
```

#### Opzione CUDA

```bash
pip install -r docs/requirements/requirements-cuda.txt
```

> Nota: se installi profilo CPU/CUDA, assicurati che combaci con il tuo ambiente locale (driver/runtime GPU, wheel torch compatibili).

## 4) Esecuzione

### 4.1 Modalità interattiva (consigliata)

Da root repository:

```bash
PYTHONPATH=src python -m package.transcriber
```

In alternativa da `src/`:

```bash
cd src
python -m package.transcriber
```

### 4.2 Flag disponibili

```bash
python -m package.transcriber --overwrite yes
python -m package.transcriber --overwrite no
```

Semantica:

* `--overwrite yes`: sovrascrive automaticamente file di output in conflitto,
* `--overwrite no`: non sovrascrive mai,
* senza flag: chiede conferma via prompt.

## 5) Flusso CLI reale

All'avvio il tool chiede, in sequenza:

1. azione (`Trascrivi` / `Esci`),
2. file audio (da `audio/` o `src/tests/resources/`),
3. modello Whisper,
4. device (`cuda`/`cpu`),
5. lingua audio,
6. modalità (`Standard` / `Accurata`),
7. scope (`Tutto` / `Solo una parte`).

Se scope è parziale:

* valida timestamp inizio/fine,
* taglia la clip via ffmpeg,
* opzionalmente conserva o elimina la clip tagliata.

Infine:

* salva il `.txt` in cartella trascrizioni,
* scrive riga benchmark su log,
* stampa riepilogo con tempo, durata audio, device e lingua.

## 6) Struttura repository (essenziale)

```text
.
├── README.md
├── ARCHITECTURE.md
├── docs/
│   ├── CHANGELOG.md
│   └── requirements/
├── src/
│   ├── package/
│   │   ├── transcriber.py
│   │   ├── core.py
│   │   ├── audio.py
│   │   ├── naming.py
│   │   ├── logger.py
│   │   ├── cli_utils.py
│   │   ├── lang_utils.py
│   │   ├── config.py
│   │   └── errors.py
│   └── tests/
├── conftest.py
└── pytest.ini
```

## 7) Path runtime importanti

Configurati centralmente in `src/package/config.py`:

* input utente: `audio/`
* input test: `src/tests/resources/`
* output trascrizioni: `doc/03_Transcriptions/`
* log benchmark: `log/whisper_benchmark.log`

## 8) Testing

Dal root repository:

```bash
PYTHONPATH=src pytest -q
```

Se mancano `torch` o `whisper`, i test che importano quei moduli possono fallire già in fase di collection.

## 9) Convenzioni output (alto livello)

La generazione nomi output è gestita da `naming.py` e include metadati utili (modello, modalità, intervallo e lingua quando disponibile) per mantenere tracciabilità dei file trascritti.

## 10) Documentazione correlata

* Architettura tecnica: [`ARCHITECTURE.md`](./ARCHITECTURE.md)
* Storico modifiche: [`docs/CHANGELOG.md`](./docs/CHANGELOG.md)

---
