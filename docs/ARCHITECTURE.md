# 🏗️ ARCHITECTURE

Documento architetturale sintetico ma operativo, allineato allo stato attuale del repository.

## 1) Contesto e obiettivo

Il sistema fornisce una pipeline CLI locale per convertire audio/video in testo usando Whisper.

Obiettivi principali:
- esperienza d'uso semplice (flusso guidato),
- separazione chiara delle responsabilità,
- output riproducibili e tracciabili,
- facilità di test e manutenzione.

## 2) Stile architetturale

Pattern adottato: **Modular Monolith con orchestrazione CLI**.

Layer logici:
1. **Presentation/Orchestration**: gestione input utente e percorso applicativo.
2. **Domain Services**: trascrizione, audio processing, naming.
3. **Infrastructure**: filesystem paths, logging, dipendenze runtime.
4. **Error Handling**: modello eccezioni centralizzato.

## 3) Mappa moduli e responsabilità

### `src/package/transcriber.py`
- Entry point (`python -m package.transcriber`).
- Orchestrazione end-to-end del flusso CLI.
- Gestione scelte utente, validazioni di percorso e policy overwrite.
- Invocazione servizi di trascrizione e logging finale.

### `src/package/core.py`
- Integrazione Whisper (`load_model`, `transcribe`).
- Configurazione parametri standard/accurata.
- Raccolta metriche runtime (tempo processo, durata audio, word count).
- Restituzione payload strutturato per livello orchestrativo.

### `src/package/audio.py`
- Discovery file audio supportati.
- Validazione/parsing timestamp.
- Taglio clip via ffmpeg.
- Lettura durata media/audio per controlli e reporting.

### `src/package/naming.py`
- Costruzione nomi output coerenti con metadati operativi:
  - modello,
  - modalità,
  - scope/intervallo,
  - lingua (quando disponibile).

### `src/package/logger.py`
- Persistenza benchmark su file (`whisper_benchmark.log`).
- Tracciamento contesto esecuzione (host, file, device, modalità, tempi, lingua, ecc.).

### `src/package/config.py`
- Source of truth per path e opzioni CLI.
- Definizione directory operative e costanti condivise.

### `src/package/cli_utils.py`
- Utility di interazione testuale (prompt, menu, info runtime).

### `src/package/lang_utils.py`
- Selezione lingua audio da opzioni supportate.

### `src/package/errors.py`
- Eccezioni dominio specifiche per distinguere errori utente/config/elaborazione.

## 4) Flusso runtime (sequence)

1. Avvio CLI.
2. Scelta file input e parametri trascrizione.
3. (Opzionale) taglio clip per scope parziale.
4. Invocazione `core.transcribe()`.
5. Salvataggio output `.txt` in cartella trascrizioni.
6. Scrittura record benchmark in log.
7. Terminazione con riepilogo esecuzione.

## 5) Boundary tecnici

- **Persistenza**: filesystem locale (nessun DB).
- **Interfaccia**: solo CLI (nessuna API HTTP/UI web).
- **Runtime esterno**: ffmpeg + whisper + torch.
- **Configurazione**: centralizzata in `config.py`.

## 6) Invarianti funzionali da preservare

1. Il comando di avvio CLI deve restare stabile e documentato.
2. Output naming deve restare coerente con metadati della run.
3. Policy overwrite deve prevenire sovrascritture involontarie.
4. Log benchmark deve essere sempre scritto a fine run riuscita.
5. Path runtime devono derivare da `config.py` (evitare hardcode sparsi).

## 7) Test strategy (stato attuale)

Test in `src/tests/` coprono principalmente:
- orchestrazione CLI,
- naming,
- utility audio,
- logger/config,
- comportamenti core (con monkeypatch/mock dove utile).

Nota operativa:
- in ambienti senza `torch`/`whisper`, alcuni test possono fallire in collection/import.

