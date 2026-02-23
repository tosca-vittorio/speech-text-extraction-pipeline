### 📦 Release **2.0.0** – *“Hyper-Whisper”* [2025-05-29]

*(succede alla 1.0.0 - «current-stable-version»)*

| Sezione         | Sintesi                                                                                                                                           |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Scope**       | Refactor completo del vecchio script monolitico: progetto ora è un vero *package* Python, test-driven e pronto CI/CD.                             |
| **Linee guida** | Semantic Versioning, struttura *src/package*, copertura test > 95 %, naming deterministico di clip e transcript, gestione sicura degli overwrite. |

---

## 🆕 Added

* **Package layout** (`package.*`) con moduli indipendenti (`audio.py`, `naming.py`, `cli_utils.py`, `core.py`, …).
* **`config.py`** – tutte le costanti di percorso (🔊 `AUDIO_DIR`, 🧪 `TEST_AUDIO_DIR`, 📝 `TRANSCRIPTION_DIR`, 📜 `LOG_FILE`).
* **Nuovo naming predicibile** tramite `genera_nome_file_output`

  ```
  <base>_(<hhmm_start>_<hhmm_end>)(<mod>_<mode>).{wav|txt}
  # es.   video_(0005_0010)(sml_acc).txt
  ```
* **Gestione overwrite**

  | File già presenti | `--overwrite yes` | `--overwrite no`      | Flag non passato                  |
  | ----------------- | ----------------- | --------------------- | --------------------------------- |
  | clip/txt assenti  | salva diretto     | salva diretto         | salva diretto                     |
  | clip/txt ESISTONO | sovrascrive       | abort pulito (exit 3) | prompt interattivo «Sovrascrivo?» |
* **Supporto cartella test-audio** – i file in `src/tests/resources` compaiono nel menu con prefisso **\[🧪]**.
* **Directory unica di output** `doc/03_Transcriptions/` (creata auto, cross-OS).
* **Flag CLI** `--overwrite` e `--device` (CLI non-interattivo pronto per automation).
* **Logging centralizzato** (`logger.py`): JSON-line con host, modello, device richiesto/effettivo, parole, tempo, ecc.
* **Suite pytest** → 47 test passanti che coprono: naming, audio-helpers, core, transcriber interactive-flows, overwrite-matrix.
* **Continuous integration ready** – test indipendenti da FFmpeg/Whisper reali (mock).

## ♻️ Changed

* Fallback CUDA → CPU loggato con warning emoji.
* `get_audio_duration` ora restituisce `"N/A"` on-error e il caller fa graceful-degrade.
* `taglia_audio` salva la clip **direttamente** dentro `TRANSCRIPTION_DIR` con nome definitivo (niente `clip_temp.wav` generico).
* Menu CLI reso “emoji guided” e più breve nelle scelte.

## 🐞 Fixed

* Crash su timestamp errati (`ValueError` → messaggio gentile).
* Eccezioni ffprobe/wave coperte da try/except (regressioni #12, #17).
* Doppio salvataggio transcript quando si conservava la clip (issue #24).

## 🔥 Removed / Deprecated

* Vecchi file `transcriber_v*.py` ⟶ mantenuti solo in `/legacy`.
* Option *“elimina clip dopo salvataggio”* ora è *opt-in*; “No” significa **non** salvare ≥ il file viene auto-pulito.
* Prompt “modalità Standard/Accurata” ora passa da `ask_choice` al flag `--accurate`.

---

## 📊 Metriche qualità

| Area                              | v 1.0.0 | v 2.0.0                 |
| --------------------------------- | ------- | ----------------------- |
| Test automatici                   | 0       | **47** (100 % verdi)    |
| Copertura (approx)                | n/d     | **> 95 %**              |
| PEP 8 score                       | 6.5     | **9.8**                 |
| Complessità ciclomatica media     | 7.2     | **4.1**                 |
| Tempo setup («tiny/cpu/30 s wav») | 18 s    | **11 s** (refactor I/O) |

---

## 🚀 Cosa aspettarsi

1. **Esperienza CLI più solida** – tutti i rami decisionali (overwrite, taglio, device) sono testati; niente più sorprese in produzione.
2. **Output sempre nello stesso posto** → facile da versionare o sincronizzare (es. cloud).
3. **Naming coerente** – clip, transcript e (futuro) video cut avranno lo stesso prefix.
4. **Facile integrazione CI** – puoi lanciare `python ­-m package.transcriber --file … --model small --device cpu --overwrite yes` dentro GitHub Actions.
5. **Manutenzione semplificata** – ogni bug fix tocca un modulo mirato + un test.

---

## 📅 Road-map post-release

* **v 2.1**: export SRT/VTT, supporto segmenti multipli in batch.
* **v 2.2**: plugin di traduzione (`--translate en`).
* **v 3.0**: backend opzionale OpenAI Whisper API + GUI streamlit.

---
