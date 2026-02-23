# 📝 Whisper AI Transcriber

---

## 📦 Requisiti

Sistema di trascrizione automatica audio/video basato su OpenAI Whisper.  
➡️ Versione attuale: **v2.0.0 “Hyper-Whisper”**

- Windows 10+ (con `ffmpeg`)
- Python 3.10+
- Chocolatey (opzionale, per installare ffmpeg)
- Ambiente virtuale Python (`venv`)
- Pacchetti Python elencati in `requirements.txt`

---

## ⚙️ Setup iniziale

### 1. Installare Chocolatey

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; 
[System.Net.ServicePointManager]::SecurityProtocol = 
[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; 
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### 2. Installare ffmpeg

```powershell
choco install ffmpeg
```

---

## 🐍 Ambiente Virtuale Python

### 3. Crea l’ambiente virtuale

```bash
py -3.10 -m venv venv
```

### 4. Attiva il venv

```bash
.\venv\Scripts\activate
```

### 5. Installa i pacchetti richiesti

```bash
pip install -r requirements.txt
```

---

## 📂 Struttura del progetto

```plaintext
/01_WHISPER_AI/
│
├── audio/                        # 🎧 Audio originali da trascrivere
│
├── doc/
│   ├── 00_Virtual Environment/  # Setup ambiente virtuale (documentazione)
│   ├── 01_WhisperAI/            # Specifiche progettuali
│   ├── 02_Strategy/             # Strategie di trascrizione
│   ├── 03_Transcriptions/       # 📄 Trascrizioni (.txt) + clip tagliate (.wav)
│   └── 04_Requirements/         # Requisiti e specifiche tecniche
│
├── log/
│   ├── bank_log.log             # Log esterni o legacy
│   └── whisper_benchmark.log    # 🧠 Log prestazioni/benchmark in formato testo
│
├── src/
│   ├── package/                 # 📦 Codice sorgente modulare
│   │   ├── __init__.py
│   │   ├── audio.py             # 🎵 Gestione file audio, taglio, durata, timestamp
│   │   ├── cli_utils.py         # ⌨️ Funzioni di interazione CLI (prompt, scelta, orario)
│   │   ├── config.py            # ⚙️ Percorsi, costanti e configurazioni globali
│   │   ├── core.py              # 🧠 Chiamata a Whisper e generazione trascrizioni
│   │   ├── errors.py            # 🚨 Eccezioni custom per dominio Transcriber
│   │   ├── logger.py            # 📝 Logging su file whisper_benchmark.log
│   │   ├── naming.py            # 🏷️ Generazione nomi output standardizzati
│   │   └── transcriber.py       # 🚀 Entry-point CLI (main)
│   │
│   └── tests/                   # ✅ Test automatici con Pytest
│       ├── resources/           # 🎯 File audio di test + output attesi (golden)
│       ├── tmp/                 # 📦 Directory temporanea isolata nei test
│       ├── test_audio.py
│       ├── test_cli_utils.py
│       ├── test_config.py
│       ├── test_core.py
│       ├── test_logger.py
│       ├── test_naming.py
│       └── test_transcriber.py
│
├── versions/                    # 🕰️ Versioni storiche del transcriber CLI
│   ├── v0.0.0/                  # Prot. originario (non modulare)
│   │   ├── CHANGELOG.md
│   │   └── transcriber_v0.0.0.py
│   ├── v1.0.0/                  # Versione stabile attuale
│   │   ├── CHANGELOG.md
│   │   └── transcriber_v1.0.0.py
│   └── v1.1.0/                  # Modalità refactor + test + naming migliorato
│       └── CHANGELOG.md
│
├── README.md                    # 📘  Documentazione del progetto
├── CHANGELOG.md                 # 🗒️  Registro aggiornamenti
├── toDo.md                      # 📌 Lista attività in corso o future
├── pytest.ini, conftest.py      # ⚙️ Configurazione e setup Pytest
└── venv/                        # 🐍 Ambiente virtuale Python
```

### 🔹Separazione delle responsabilità (Single Responsibility Principle)

#### 📦 Modularizzazione in sottocomponenti
| Modulo            | Responsabilità |
|-------------------|----------------|
| `cli.py`          | CLI e parsing argomenti (`argparse` / `click`) |
| `core.py`         | Funzione centrale `transcribe(...)` |
| `audio.py`        | Utility audio: taglio, durata, validazione |
| `naming.py`       | Generazione nomi coerenti |
| `logger.py`       | Logging centralizzato |
| `config.py`       | Costanti di configurazione, percorsi, opzioni menu |
| `errors.py`       | Eccezioni personalizzate |

---

## 🚀 Come si esegue: da "src/"

### Interattivo

```bash
python -m package.transcriber
```

Segui i prompt:

1. Seleziona file `[🎧]` o `[🧪]`
2. Scegli modello (`tiny`, `base`, `small`, `medium`)
3. Modalità (`Standard` o `Accurata`)
4. Scope (`Tutto` o `Solo una parte`)
5. In caso di taglio → inserisci timestamp `hh:mm:ss`
6. Conferma se salvare la clip
7. In caso di file esistenti → prompt: sovrascrivere?

### Non-interattivo (CLI)

```bash
python -m package.transcriber --file input.wav --model small --device cpu --overwrite yes
```

---

## 🧰 Funzionalità principali

- ✂️ Supporto taglio parziale da timestamp `--start --end`
- 🎯 Nome coerente output: `nome (mmss_mmss)(mod_mode).wav/txt`
- ❗️ Protezione sovrascrittura (`--overwrite=no`, prompt interattivo)
- 🧪 Test 100% coverage CLI, naming, audio, core, logger, transcriber
- 📂 Gestione output e file di test in cartelle ben distinte
- 🧠 Logging benchmark centrale `whisper_benchmark.log`

* ✂️ Taglio preciso di porzioni audio con `ffmpeg`
* 🧠 Modalità doppia:

  * **Standard** → output leggibile
  * **Accurata** → output fedele all’audio
* 💾 Output coerente:

  * `video (0005_0010)(sml_acc).txt`
  * `video (0005_0010)(sml_acc).wav`
* 🔐 Protezione overwrite:

  * `--overwrite yes/no` o prompt interattivo
* 📑 Logging dettagliato in `log/whisper_benchmark.log`
* 🧪 Supporto audio test `[🧪]` da `tests/resources`
* 📈 Copertura test > 95%, CI ready

### 🔹 Best Practices

✅ Type hint e docstring coerenti  
✅ Logging con `logging`, formattazione leggibile, livelli configurabili  
✅ Modularità con responsabilità ben definite  
✅ CLI interattiva + supporto argomenti da riga di comando  
✅ Error handling centralizzato  
✅ Test `pytest` su ogni modulo (fixture, golden, mocking Whisper)  

---

## 🧠 Suggerimenti per miglior qualità

* Preferire `Accurata` su audio puliti
* Modello consigliato: `small` o `medium`
* Forzare lingua `"it"`
* Input consigliato: 48kHz, 128kbps+, stereo

---

## 📝 Esempio output log

```
[2025-05-29 14:55:10] Host: ACER | File: video_(0005_0010)(sml_acc).wav | Modello: small | Device richiesto: cpu | Device usato: cpu | Modalità: Accurata | Tipo: parziale | Durata audio: 0:00:05 | Tempo elaborazione: 0m 1.23s | Parole: 42
```

---

## 🧪 Stato Test

* 🔬 47 test automatici → `pytest`
* ✅ Tutti verdi (CI/CD compatibile)
* 🎯 Test interattivi: flussi CLI (completi/parziali, sovrascrittura, errori)
* 🧪 Test golden output

---

## 🔁 Differenze vs Versione 1.0.0

| Feature                | v1.0.0    | v2.0.0 “Hyper-Whisper” |
| ---------------------- | --------- | ---------------------- |
| Monolitico             | ✅         | ❌ package modulare     |
| Naming coerente        | ❌ manuale | ✅ automatico           |
| Protezione overwrite   | ❌ nessuna | ✅ gestita + CLI        |
| Clip salvata “a parte” | ❌         | ✅ naming sincrono      |
| Audio test `[🧪]`      | ❌         | ✅ nel menu             |
| Logging dettagliato    | parziale  | ✅ full JSON-line       |
| Copertura test         | assente   | ✅ 95%+                 |
| Pronto per CI          | ❌         | ✅ sì                   |

---

## 🔭 Roadmap futura (esempio)

* `v2.1` → supporto SRT/VTT
* `v2.2` → modalità traduzione (→ en)
* `v3.0` → interfaccia grafica Streamlit + API Whisper

---

## 📌 Autore

Realizzato da **Ing. Toscano Vittorio** con ❤️
Powered by [OpenAI Whisper](https://openai.com/research/whisper)

---

## 🔹 Sviluppi Futuri

- [ ] Documentazione Tecnica progetto (`doc/01_WhisperAI`)
- [ ] 
- [ ] 
- [ ] 
- [ ] 

> Il `README.md` è aggiornato alla versione 2.0.0
> Riflette *tutte* le funzionalità e i flussi di lavoro correnti


# WHISPER_AI Project Setup (ACER & ASUS)

Benvenuto nella guida rapida per configurare correttamente l'ambiente di sviluppo su nuovi computer.

---

## Requisiti di Sistema

- **Windows 10 o superiore**
- **Python 3.10** installato (non usare 3.13)
- **Chocolatey** installato


## Procedura Step-by-Step

### 1. Installare Chocolatey

Aprire **PowerShell come amministratore** e lanciare il comando ufficiale:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

Verificare l'installazione:

```bash
choco --version
```

### 2. Installare strumenti di sistema

Usare Chocolatey per installare `ffmpeg`:

```bash
choco install ffmpeg
```

Verificare l'installazione:

```bash
ffmpeg -version
```


### 3. Creare l'ambiente virtuale (venv)

Spostarsi nella cartella del progetto sincronizzata (es. `01_WHISPER_AI`) e creare il venv:

```bash
py -3.10 -m venv venv
```

Attivare il venv:

```bash
.\venv\Scripts\activate
```

### 4. Installare i pacchetti Python

Con il venv attivo, installare tutti i pacchetti richiesti:

```bash
pip install -r requirements.txt
```


### 5. Verifica finale

Controllare che tutto sia configurato correttamente:

- `python --version` deve restituire 3.10.x
- `pip list` deve mostrare `torch`, `openai-whisper`, ecc.
- `ffmpeg -version` deve funzionare.


---

## Note Finali

- Non sincronizzare la cartella `venv` tramite Syncthing.
- Ogni computer deve avere il suo venv locale.
- Aggiornare `requirements.txt` se si installano nuovi pacchetti Python.

---

# Buon lavoro con WHISPER_AI! 🚀

