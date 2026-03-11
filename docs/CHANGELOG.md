## Branch: [development]

### [Unreleased]
> Scope corrente: **post-A4.2** — chiusura hard gate Pylint su `src/package`, riallineamento documentale owner, baseline A4.3 raccolta su `src/tests` e apertura pianificazione A4.4 / A5.

#### A4.3 — Pylint quality gate sui test (progressivo)

- **`c2e21cd` — chore(tests): clean test_config pylint cheap wins**
  - **Type:** CHANGED · **Categoria:** Test / Lint
  - **Cosa cambia:** pulizia mirata di `src/tests/test_config.py` con aggiunta di module docstring, rimozione di import inutilizzati e spezzatura di assert troppo lunghe.
  - **Impatto:** eliminati i cheap wins locali del file senza alterare la suite; `python -m pytest -q` resta verde (**49 passed**) e `python -m pylint src/tests/test_config.py` raggiunge **10.00/10** con exit code **0**.

- **`0b5b4b4` — chore(tests): clean src/tests conftest pylint warnings**
  - **Type:** CHANGED · **Categoria:** Test / Lint
  - **Cosa cambia:** pulizia mirata di `src/tests/conftest.py` con aggiunta di module docstring, rimozione di un import inutilizzato e ripristino della newline finale.
  - **Impatto:** eliminati i warning locali del file senza alterare il comportamento della suite; `python -m pytest` resta verde (**49 passed**) e il rating di `python -m pylint src/tests` migliora da **6.82/10** a **6.89/10**.

#### A4.2 — Pylint burn-down (cheap wins + hardening)
> Ordinamento: **git log (più recente → più vecchio)** · principio **truth-first**: qui è riportato solo ciò che è committato.

- **`5619e52` — refactor(logger,transcriber): close pylint gate with param objects and flow extraction**
  - **Type:** CHANGED · **Categoria:** Refactor
  - **Cosa cambia:** introdotti oggetti parametrici nel logger (`DeviceInfo`, `TranscriptionMetrics`, `OutputInfo`, `LogTranscriptionParams`), estratte le helper `_select_input_file()` e `_transcribe_partial_scope()` nel transcriber, riallineato il logging finale e aggiornati i test.
  - **Impatto:** chiusi i warning residui di `logger.py` e `transcriber.py`; `python -m pylint src/package` raggiunge **10.00/10** con exit code **0**. Contestualmente `pyproject.toml` diventa fonte unica per la configurazione Pylint del repository.

- **`faba031` — refactor(core): group output filename params to reduce arguments**
  - **Type:** CHANGED · **Categoria:** Refactor
  - **Cosa cambia:** introdotto `OutputTxtNameParams` + helper `_build_output_txt_filename(params)` per evitare firme con troppi argomenti.
  - **Impatto:** `core.py` raggiunge **10.00/10**; nessun cambio di contract su naming output.

- **`a2dce6a` — refactor(core): add TranscribeParams and update call sites/tests**
  - **Type:** CHANGED · **Categoria:** Refactor
  - **Cosa cambia:** `core.transcribe()` ora accetta un unico oggetto `TranscribeParams`; call-site e test riallineati.
  - **Impatto:** riduce superficie API e prepara refactor successivi; test invariati e verdi.

- **`09d42cd` — docs(timeline): record A4.2.6.h NamingParams refactor progress**
  - **Type:** CHANGED · **Categoria:** Docs
  - **Cosa cambia:** aggiornato `docs/TIMELINE.md` con chiusura e evidenze del subtask `A4.2.6.h`.
  - **Impatto:** audit trail coerente (truth-first).

- **`797399c` — refactor(naming): introduce NamingParams and update call sites**
  - **Type:** CHANGED · **Categoria:** Refactor
  - **Cosa cambia:** introdotta dataclass immutabile `NamingParams`; `genera_nome_file_output()` passa a singolo argomento; aggiornati call-site e test.
  - **Impatto:** `naming.py` passa a **10.00/10** eliminando `too-many-arguments/too-many-positional-arguments` sul modulo.

- **`13b3e57` — docs(timeline): close A4.2.4 canonical soft pylint command**
  - **Type:** CHANGED · **Categoria:** Docs
  - **Cosa cambia:** fissato comando canonico di lint **soft** (`--exit-zero`) e distinto dal run hard come metrica.
  - **Impatto:** gate documentato, riproducibile e auditabile durante il burn-down.

- **`16d4e4b` — docs(changelog): record A4.2 pylint burn-down and repo hardening history**
  - **Type:** CHANGED · **Categoria:** Docs
  - **Cosa cambia:** aggiornamento storico/riordino del changelog per il ciclo A4.2.
  - **Impatto:** tracciabilità consolidata.

- **`22613bf` — docs(timeline): record A4.2 lint burn-down cheap wins**
  - **Type:** CHANGED · **Categoria:** Docs
  - **Cosa cambia:** aggiornata `docs/TIMELINE.md` con subtask `A4.2.6.c` → `A4.2.6.g` e relative evidenze.
  - **Impatto:** formalizzazione del completamento cheap wins; warning residui solo strutturali (`too-many-*`).

- **`0a53f8f` — chore(lint): annotate intentional broad catch in cli entrypoint**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** annotato il `catch-all` finale nel wrapper CLI con disable mirato Pylint.
  - **Impatto:** rimosso warning `W0718` residuo nel wrapper CLI; nessuna soppressione globale.

- **`ceefa41` — chore(lint): replace local lambda with helper in naming**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** sostituita lambda locale in `naming.py` con helper `def`.
  - **Impatto:** rimozione `C3001 unnecessary-lambda-assignment` senza cambiare comportamento.

- **`12f30f8` — chore(lint): rename local languages mapping in lang utils**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** rinominata variabile locale `LANGUAGES` → `languages` in `lang_utils.py`.
  - **Impatto:** rimozione `C0103 invalid-name` senza cambiare API/contratto.

- **`70d7977` — test(lang): align monkeypatch targets with toplevel ask_choice import**
  - **Type:** CHANGED · **Categoria:** Test
  - **Cosa cambia:** riallineati i test al binding realmente usato (`package.lang_utils.ask_choice`) e patch coerente nei test end-to-end.
  - **Impatto:** risolti failure da stdin/StopIteration emersi dopo refactor lint-driven.

- **`b51b701` — chore(lint): narrow exceptions in csproduct lookup**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** in `cli_utils.get_csproduct_name()` sostituito `except Exception` con catch specifici.
  - **Impatto:** rimozione `W0718` locale mantenendo fallback su `platform.node()`.

- **`8d4f2e7` — chore(lint): add transcriber module and main docstrings**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** aggiunti module docstring in `transcriber.py` e docstring a `main()`.
  - **Impatto:** migliore leggibilità/documentazione del punto d’ingresso CLI.

- **`26bc282` — chore(lint): move subprocess import to toplevel in cli utils**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** spostato `import subprocess` a livello top-level in `cli_utils.py`.
  - **Impatto:** allineamento a import hygiene / regole lint.

- **`871a002` — chore(lint): add exception chaining in transcriber errors**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** introdotto `raise ... from exc` nei percorsi di errore del transcriber.
  - **Impatto:** migliorata tracciabilità delle cause senza cambiare il flusso utente.

- **`0728d73` — docs(timeline): record A4.2 burn-down progress and audio duration hardening**
  - **Type:** CHANGED · **Categoria:** Docs
  - **Cosa cambia:** aggiornato tracking A4.2 + evidenze intermedie e hardening `get_audio_duration()`.
  - **Impatto:** audit trail coerente del burn-down.

- **`0e06f64` — fix(audio): return N/A on invalid wav and ffprobe failures**
  - **Type:** FIXED · **Categoria:** Fix
  - **Cosa corregge:** hardening di `get_audio_duration()` su WAV invalidi / failure `ffprobe` con ritorno `"N/A"`.
  - **Impatto:** pipeline più robusta su input corrotti e test stub.

- **`7e6ed0a` — chore(lint): add missing module docstrings**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** aggiunte module docstring ai moduli base (`audio/cli_utils/config/errors/lang_utils/logger`).
  - **Impatto:** rimozione `missing-module-docstring`.

- **`bb686ed` — chore(lint): wrap config MODALITA_OPTIONS into multiline list**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** spezzata `MODALITA_OPTIONS` in lista multiline in `config.py`.
  - **Impatto:** conformità lint su linee lunghe.

- **`dfb3cdf` — chore(lint): split long clip path construction in transcriber**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** spezzata la costruzione del path clip in `transcriber.py`.
  - **Impatto:** migliore leggibilità e riduzione warning `line-too-long`.

- **`3038fcd` — chore(lint): wrap long logger docstring line**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** wrapping di una riga lunga nel docstring di `log_transcription()`.
  - **Impatto:** conformità `line-too-long`.

- **`347e275` — chore(lint): reorder imports in core to satisfy pylint**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** riordino import in `core.py` secondo stdlib/third-party/first-party.
  - **Impatto:** riduzione warning lint senza impatto funzionale.

- **`a6d4989` — chore(lint): split long ternary in audio duration parsing**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** refactor ternaria lunga in `audio.py`.
  - **Impatto:** migliore leggibilità e conformità `line-too-long`.

- **`a4932f3` — chore(lint): normalize trailing newlines in config**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** normalizzazione newline finali in `config.py`.
  - **Impatto:** coerenza stile.

- **`11b0bfd` — chore(lint): add missing final newline in package init**
  - **Type:** CHANGED · **Categoria:** Lint
  - **Cosa cambia:** aggiunta newline finale mancante in `src/package/__init__.py`.
  - **Impatto:** allineamento a regole stile.

- **`4110064` — docs(timeline): expand A4.2 pylint gate into macro-subtasks and record evidences**
  - **Type:** CHANGED · **Categoria:** Docs
  - **Cosa cambia:** espanse macro-sezioni A4.2 e formato evidenze in `docs/TIMELINE.md`.
  - **Impatto:** tracking più rigoroso e auditabile del quality gate lint.

##### Quality gates (snapshot corrente)
- Test suite: `python -m pytest` → **49 passed**
- Pylint (hard-run): `python -m pylint src/package` → **10.00/10**, **exit code 0**
- Warning residui sul target `src/package`: **nessuno**
- Stato del blocco: **A4.2 chiuso**

#### Historical context (pre-A4.2 / hardening, packaging, repo hygiene) [ordine cronologico]

##### Foundation / IO / naming / repo layout
- **`26d683a` — chore(git): keep audio dir**
  - **Type:** ADDED
  - **Cosa introduce:** placeholder per mantenere directory necessarie (audio) nel repo.
  - **Impatto:** struttura stabile.

- **`83996b2` — refactor(lang): import ask_choice from cli_utils to avoid circular dependency**
  - **Type:** CHANGED
  - **Cosa cambia:** refactor della gestione lingua per importare `ask_choice` da `cli_utils` ed evitare dipendenze circolari.
  - **Impatto:** stabilità import e run.

- **`b7805af` — feat(io): read media from input audio+video and write transcripts to output/transcriptions**
  - **Type:** ADDED
  - **Cosa introduce:** supporto IO su input audio+video e scrittura trascrizioni su `output/transcriptions/`.
  - **Impatto:** pipeline IO coerente per batch/containers.

- **`bd2e6ab` — refactor(naming): include language in generated output filenames**
  - **Type:** CHANGED
  - **Cosa cambia:** naming degli output include il tag lingua per disambiguare e tracciare l’esecuzione.
  - **Impatto:** output più leggibili e deterministici.

- **`0c53a7f` — chore(repo): align gitignore and placeholders for input/output structure**
  - **Type:** CHANGED
  - **Cosa cambia:** riallineamento placeholder e ignore rules per la struttura `input/` / `output/`.
  - **Impatto:** repo hygiene e base più pulita per Docker/CI.

- **`dec3330` — chore(repo): remove legacy audio placeholder**
  - **Type:** CHANGED
  - **Cosa cambia:** rimozione placeholder legacy non più coerente con la struttura definitiva.
  - **Impatto:** riduzione residui e ambiguità.

- **`14ea605` — chore(tools): move clean script under tools/**
  - **Type:** CHANGED
  - **Cosa cambia:** consolidamento dello script di clean sotto `tools/`.
  - **Impatto:** struttura tooling più chiara.

- **`13381aa` — chore(gitignore): ignore runtime output audio/video folders**
  - **Type:** CHANGED
  - **Cosa cambia:** regole `.gitignore` per evitare versionamento accidentale di output runtime (audio/video).
  - **Impatto:** igiene repo.

- **`d62a384` — chore(repo): remove legacy clean_project.sh from root**
  - **Type:** CHANGED
  - **Cosa cambia:** rimozione dello script legacy dalla root per ridurre ambiguità e centralizzare tooling.
  - **Impatto:** repo più ordinato.

- **`71578d1` — chore(repo): add output/audio placeholder**
  - **Type:** ADDED
  - **Cosa introduce:** placeholder per mantenere `output/audio/` in repo senza versionare output reali.
  - **Impatto:** struttura output consistente.

##### Test alignment / pytest temp handling / logs hygiene
- **`408a302` — test(core): expect lang tag in output filenames**
  - **Type:** CHANGED
  - **Cosa cambia:** i test si adeguano al naming che include il tag lingua nei file generati.
  - **Impatto:** enforcement del contract di naming.

- **`c060632` — test: align config and transcriber flows with new dirs and language prompt**
  - **Type:** CHANGED
  - **Cosa cambia:** riallinea test/contratti su percorsi e flussi aggiornati (directory e prompt lingua).
  - **Impatto:** riduzione drift tra codice e suite.

- **`c82a247` — docs(changelog): record test suite alignment to current contracts**
  - **Type:** CHANGED
  - **Cosa cambia:** aggiornamento documentale per registrare l’allineamento della test suite ai contratti correnti.
  - **Impatto:** audit trail (docs).

- **`88ca4ae` — fix(pytest): set basetemp to src/tests/tmp**
  - **Type:** FIXED
  - **Nota:** intervento iniziale su `pytest.ini` che imposta `--basetemp=src/tests/tmp`; successivamente hardenizzato per cwd-agnostic con `4d25b47`.
  - **Impatto:** controllo dei temporanei pytest “dentro repo” (untracked).

- **`77d4aa3` — chore(logs): track logs dir via gitkeep**
  - **Type:** ADDED
  - **Cosa introduce:** `logs/.gitkeep` per versionare la directory `logs/` senza versionare i log reali.
  - **Impatto:** struttura repo stabile e coerente tra macchine/CI.

- **`9c79cc6` — chore(gitignore): ignore tmp and keep logs placeholder**
  - **Type:** CHANGED
  - **Cosa cambia:** aggiorna `.gitignore` per gestire `logs/**` ignorando i file runtime ma mantenendo `logs/.gitkeep`; conferma ignorare `tmp/` senza placeholder.
  - **Impatto:** repository più pulito, senza log accidentali versionati.

- **`2d2668e` — fix(logging): use logs dir and create it on write**
  - **Type:** FIXED
  - **Cosa corregge:** standardizza la directory dei log su `logs/` (al posto di `log/`) e sposta `os.makedirs(LOG_DIR, exist_ok=True)` dentro la funzione di scrittura (no side-effect a import).
  - **Impatto:** logging più pulito e prevedibile; supporto naturale a placeholder `logs/.gitkeep`.
  - **Evidenze:** test suite ✅ (49 passed).

- **`4d25b47` — fix(pytest): force basetemp to src/tests/tmp cwd-agnostic**
  - **Type:** FIXED
  - **Cosa corregge:** elimina failure dei test da sottocartelle (es. `cd src && python -m pytest`) dovuti a `--basetemp=src/tests/tmp` interpretato come path relativo alla cwd.
  - **Come:** introdotto `src/tests/conftest.py` che forza `--basetemp` a un path assoluto ancorato alla project root; mantenuto `testpaths = src/tests`.
  - **Impatto:** test suite stabile indipendentemente dalla cwd.
  - **Evidenze:** `python -m pytest` ✅ (root), `cd src && python -m pytest` ✅ (49 passed).

##### Tooling hardening / packaging / docs alignment
- **`2086deb` — docs: align README/ARCH/CHANGELOG/TIMELINE to current repo state**
  - **Type:** CHANGED
  - **Cosa cambia:** riallineamento documentazione principale allo stato reale del repository.
  - **Impatto:** riduzione drift documentale.

- **`e60b0ad` — chore(tools): harden clean_project script (safe-by-default)**
  - **Type:** CHANGED
  - **Cosa cambia:** riscrittura hardenizzata di `tools/clean_project.sh` con approccio SAFE-by-default.
  - **Dettagli:**
    - allowlist mirata (root cache + `src/` + `tools/` + `src/tests/tmp/**`);
    - opt-in espliciti (OFF di default): `PURGE_LOGS`, `PURGE_OUTPUT`, `CLEAN_VENV`;
    - root guard (`README.md` + `src/` + `tools/`) per prevenire esecuzioni fuori repository;
    - output strutturato (sezioni + contatori) e modalità `DRY_RUN` / `VERBOSE`.
  - **Impatto:** pulizia deterministica, auditabile e CI/Docker-ready senza rischio di cancellazioni accidentali.
  - **Evidenze:** `DRY_RUN=true VERBOSE=true tools/clean_project.sh` ✅ · `python -m pytest` ✅ (49 passed).

- **`a017ee0` — docs: close A2 and record clean_project hardening**
  - **Type:** CHANGED
  - **Cosa cambia:** chiusura documentale step A2 e registrazione evidenze hardening clean script.
  - **Impatto:** timeline/docs coerenti con stato reale.

- **`c201bd3` — chore(tools): improve tmp purge counting and glob safety**
  - **Type:** CHANGED
  - **Cosa cambia:** migliorati conteggi purge tmp e sicurezza nei glob dello script di clean.
  - **Impatto:** maggiore robustezza e auditabilità dello script.

- **`f418ce8` — docs(tools): document clean_project usage and flags**
  - **Type:** CHANGED
  - **Cosa cambia:** documentato uso di `tools/clean_project.sh`, flag e modalità operative.
  - **Impatto:** onboarding/uso più chiaro.

- **`eecde6e` — build(packaging): add pyproject and installable transcriber entrypoint**
  - **Type:** ADDED
  - **Cosa introduce:** progetto installabile (layout `src/`) con entrypoint CLI stabile `transcriber`.
  - **Dettagli:**
    - aggiunto `pyproject.toml` (setuptools) con `package-dir` su `src` e discovery `where = ["src"]`;
    - definito `console script`: `transcriber = package.transcriber:main`;
    - `transcriber --help` reso non-interattivo (fast-path `-h/--help`).
  - **Impatto:** elimina workaround tipo `PYTHONPATH=src`; base più solida per CI/Docker.
  - **Evidenze:** `python -m pip install -e .` ✅ · `transcriber --help` ✅ · `python -m pytest` ✅ (49 passed).

- **`10b932f` — docs: close A3 packaging and installable transcriber entrypoint**
  - **Type:** CHANGED
  - **Cosa cambia:** chiusura documentale step A3 con evidenze packaging/entrypoint.
  - **Impatto:** allineamento timeline/docs con stato reale del repo.

- **`b370f72` — docs(readme): align quick start to installable transcriber entrypoint**
  - **Type:** CHANGED
  - **Cosa cambia:** aggiorna README per rendere `transcriber` il comando canonico post-packaging e rimuovere riferimenti obsoleti.
  - **Dettagli:**
    - Quick Start aggiornato con `python -m pip install -e .`;
    - introdotto `transcriber --help` come verifica non-interattiva;
    - sezione esecuzione riallineata (comando canonico + fallback).
  - **Impatto:** documentazione coerente con stato reale, pronta per host/CI/Docker.
  - **Evidenze:** `transcriber --help` ✅ · `python -m pytest` ✅ (49 passed).

- **`e488b0d` — docs(timeline): reflect A4 progress and record host evidences**
  - **Type:** CHANGED
  - **Cosa cambia:** aggiornamento `docs/TIMELINE.md` con progressi A4 ed evidenze host.
  - **Impatto:** audit trail documentale più accurato.

- **`cc99303` — docs(changelog): record README alignment for transcriber entrypoint**
  - **Type:** CHANGED
  - **Cosa cambia:** aggiornamento `docs/CHANGELOG.md` per registrare il riallineamento README al nuovo entrypoint.
  - **Impatto:** tracciabilità documentale delle modifiche A3/A4.

- **`b345053` — docs(architecture): record transcriber canonical entrypoint and installable packaging**
  - **Type:** CHANGED
  - **Cosa cambia:** aggiornamento `docs/ARCHITECTURE.md` sui confini del packaging installabile e sull’entrypoint canonico `transcriber`.
  - **Impatto:** architettura documentata in modo coerente con il codice.

---

## Branch: [main]

### [v2.1.0]
- **`da2c3bc` — Merge PR #3 (release v2.1.0)**
  - **Type:** CHANGED
  - **Contenuto:** consolidamento baseline + requirements files e aggiornamenti documentali associati.

### [v2.0.0]
- **`fe7a49f` — Merge PR #2 (release v2.0.0)**
  - **Type:** CHANGED
  - **Contenuto:** evoluzione CLI + language selection, riorganizzazione e stabilizzazione.

### [v1.0.0]
- **`c8e9ee0` — Merge PR #1 (release v1.0.0)**
  - **Type:** CHANGED
  - **Contenuto:** milestone iniziale stabile della CLI.

### [v0.0.0]
- **`cd50726` — chore: initial import (baseline)**
  - **Type:** ADDED
  - **Contenuto:** snapshot iniziale della codebase.

---
