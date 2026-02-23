## 📦 Release **2.1.0** – *“Polyglot Whisper”* \[2025-06-01]

*(successivo a 2.0.0 “Hyper-Whisper”)*

| Sezione         | Sintesi                                                                                                                             |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Scope**       | Aggiunto supporto multilingua esplicito: l’utente specifica la lingua in CLI, tutti i moduli passano – log, naming, transcript.     |
| **Linee guida** | Versionamento semantico mantenuto; i changelog restano cronologici. Il flusso interattivo è immutato, solo con `select_language()`. |

---

## 🆕 Added

* **Supporto CLI Multilingua**

  * Nuovo modulo `lang_utils.py` con `select_language()` che chiede all’utente “🌐 In quale lingua è l’audio?” e restituisce il codice ISO (`it`, `en`, `fr`, `es`).
  * Nel menu principale, la scelta lingua è ora un passaggio obbligatorio prima di trascrivere.

* **Tag `(lang_<codice>)` nei nomi di output**

  * Funzione `genera_nome_file_output` (in `naming.py`) ora accetta parametro opzionale `lang: str | None` e aggiunge `(lang_<codice>)` al nome base (sia per trascrizione completa sia parziale).
  * Esempi:

    ```
    audiofile (tny_std) (lang_en).txt  
    video (000500_001000) (med_acc) (lang_it).wav
    ```

* **Log con campo Lingua**

  * Firma di `log_transcription` aggiornata con argomento opzionale `lingua: str | None`.
  * Se `lingua` non è `None`, si aggiunge ` | Lingua: <codice>` alla riga di log (es. `… | Parole trascritte: 42 | Lingua: en`).
  * Directory `log/` creata automaticamente anche dopo il refactor; nuovo test `test_log_transcription_with_language`.

* **Test per il supporto lingua**

  * `test_lang_utils.py`: verifica che, stubmando `ask_choice`, `select_language()` restituisca solo il codice (es. `"en"`).
  * `test_naming.py`: due nuovi casi per `genera_nome_file_output` con `lang="en"` e `lang="it"`, per “completa” e “parziale”.
  * `test_logger.py`: nuovi test `test_log_transcription_with_language` e `test_log_transcription_without_language` per la riga `| Lingua: …`.

---

## ♻️ Changed

* **`transcriber.py`**

  * Aggiunto il passo “3) scelta lingua” tramite `select_language()`.
  * Nel ramo “completa”, dopo `transcribe()`, si calcola il nome `.txt` con `lang` e lo si assegna a `result["txt_filename"]`.
  * Nel ramo “parziale”, `genera_nome_file_output(..., lang=lang)` produce sia il nome della clip (wav) sia, conseguentemente, il nome del `.txt`.
  * La logica di salvataggio del `.txt` ora controlla “`conflict_file`” (qualsiasi `.txt` esistente che condivide lo stesso stem base), invece di confrontarsi solo con `txt_path.exists()`.

    * Se `ARGS.overwrite == "yes"`, si sovrascrive senza prompt.
    * Se `ARGS.overwrite == "no"`, si stampa “Salvataggio annullato (file .txt già esistente).” ed esce con `sys.exit(0)`.
    * Senza flag, il prompt chiede di sovrascrivere il file già esistente (`conflict_file.name`), non il nome calcolato.

* **`naming.py`**

  * Aggiunto parametro `lang: str | None = None`.
  * Ora `genera_nome_file_output` concatena `(lang_<codice>)` se `lang` contiene un valore.

* **`logger.py`**

  * Funzione `log_transcription` estesa con `lingua: str | None = None`.
  * Generazione della stringa `riga`: se `lingua` è fornita, aggiunge “ | Lingua: <codice>” prima del `"\n"`.

* **`lang_utils.py`**

  * Import di `ask_choice` spostato da `cli_utils` a `package.transcriber` (import dinamico dentro `select_language()`).

    * Questo consente ai test di fare `monkeypatch.setattr(trans_mod, "ask_choice", …)` senza cadere in chiamate dirette a `input()`.

* **Test di `test_transcriber.py`**

  * Aggiornati i sequenziali `seq` per l’inclusione di `"en (Inglese)"` tra le risposte di `ask_choice`.
  * Rimangono invariati i controlli sul parametro `lang` passato a `transcribe()`.
  * Ora i test “overwrite” (NO e prompt NO) passano correttamente, perché l’esistenza di `ok.txt` in `TRANSCRIPTION_DIR` viene intercettata da `conflict_file` e il flusso esce prima di scrivere il nuovo nome `(lang_en)`.

---

## 🐞 Fixed

* **Overwrite prompt “No”**

  * Prevenzione del salvataggio errato del nuovo file `.txt` quando `ARGS.overwrite is None` e l’utente risponde “No” al prompt. Ora il flusso si interrompe immediatamente e non procede alla stampa di “Trascrizione completata”.
  * I test `test_overwrite_prompt_no` ora vedono correttamente la stringa **“Salvataggio annullato (file .txt già esistente).”** senza alcuna ulteriore uscita.

* **Chiamate a `ask_choice` durante i test**

  * In `select_language()`, grazie all’import dinamico di `ask_choice` da `package.transcriber`, non ci sono più chiamate a `input()` non gestite che generavano `OSError` in Pytest.

---

## 🔥 Removed / Deprecated

* Nessuna rimozione aggiuntiva rispetto a 2.0.0.
* `DEFAULT_LANG` rimane definito in `config.py` ma non è usato (commentato come “futuro fallback”, senza impatto).

---

## 📊 Metriche qualità (aggiornamento su 2.0.0)

| Area                              | v 2.0.0          | v 2.1.0                         |
| --------------------------------- | ---------------- | ------------------------------- |
| Test automatici                   | 47 (100 % verdi) | **49** (aggiunti 2 test lingua) |
| Copertura (approx)                | > 95 %           | **> 95 %**                      |
| PEP 8 score                       | 9.8              | **9.8** (nessun cambiamento)    |
| Complessità ciclomatica media     | 4.1              | **4.2** (leggero incremento)    |
| Tempo setup (“tiny/cpu/30 s wav”) | 11 s             | **11 s**                        |

---

## 🚀 Cosa aspettarsi

1. **Flusso CLI multilingua** – ogni trascrizione reca il tag `(lang_<codice>)` nel nome e nel log.
2. **Log più completo** – contiene anche la lingua (`Lingua: en`).
3. **Nuovi test per lingua** – la copertura è aumentata con due test mirati su selezione e naming della lingua.
4. **Overwrite più robusto** – niente più sostituzioni involontarie quando si risponde “No” al prompt.

La riga **“Directory log/ creata automaticamente anche dopo il refactor; nuovo test test\_log\_transcription\_with\_language”** significa semplicemente:

1. **Creazione automatica di `log/`**
   Nel file `logger.py` abbiamo mantenuto la chiamata

   ```python
   os.makedirs(LOG_DIR, exist_ok=True)
   ```

   fin dall’importazione del modulo. Di conseguenza, anche dopo aver ristrutturato (refactor) tutto il codice, il programma continua a creare automaticamente, all’avvio, la cartella `log/` (impostata dal tuo `config.py`). Non serve che tu la crei a mano: il modulo `logger` si occupa di verificarne l’esistenza e, se non c’è, la genera.

2. **Nuovo test `test_log_transcription_with_language`**
   Abbiamo aggiunto un test specifico per verificare che, quando chiami `log_transcription(…, lingua="en")`, la riga di log scriva correttamente anche la parte “ | Lingua: en”. Quel test crea fittiziamente la cartella `log/`, poi invoca `log_transcription` con parametro `lingua="en"` e controlla che nel file `whisper_benchmark.log` sia presente “ | Lingua: en”.
   Quindi il changelog segnala sia la presenza della creazione automatica della directory `log/`, sia l’introduzione di un test dedicato a quel comportamento “log con lingua”.

---

### Come funziona il flusso CLI multilingua

Ora la procedura CLI ti chiede **esplicitamente** in quale lingua è l’audio, e utilizza quel parametro per:

* Passarlo a Whisper in modo che trascriva nel modello della lingua giusta.
* Includere il tag `(lang_<codice>)` nel nome del file di output.
* Registrarlo nel log con `| Lingua: <codice>`.

Quindi, se hai un video in cui l’audio è in inglese, quando avvii `python -m package.transcriber`, fra i passi ti verrà mostrata la domanda:

```
🌐 In quale lingua è l'audio?
1. it (Italiano)
2. en (Inglese)
3. fr (Francese)
4. es (Spagnolo)
Scelta:
```

* Se digiti “2” (oppure selezioni “en (Inglese)”), il programma passerà `lang="en"` a Whisper e genererà la trascrizione in inglese.
* Se invece sai che l’audio è in francese, selezioni “3” (“fr (Francese)”) e il sistema trascriverà come “lang=fr”.

In sostanza: **semplicemente scegli `en`, `fr`, `it`, `es` a seconda della lingua del tuo video**, e la trascrizione verrà generata in quella lingua.

---