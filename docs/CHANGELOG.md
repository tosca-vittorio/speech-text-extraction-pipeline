# CHANGELOG — `speech-text-extraction-pipeline` (Python · Whisper CLI)

> Type legend:
> **ADDED** = introduzione di elementi nuovi (scaffold/moduli/feature),
> **CHANGED** = modifica/refactor/docs/hardening,
> **FIXED** = correzione puntuale (bug/regressione/typo).

Principi:
- **Truth-first**: qui dentro è “fatto” solo ciò che è **committato** su Git.

---

## Stakeholder Summary — Hardening & Repo Hygiene (Unreleased)

### Overview
Nel ciclo corrente il repository `speech-text-extraction-pipeline` è stato consolidato con interventi mirati a:
- rendere l’esecuzione test **riproducibile** e **cwd-agnostic** (root e `src/`),
- standardizzare la gestione di cartelle runtime (`logs/`, `output/`, `input/`) tramite placeholder versionati,
- migliorare igiene repo (`.gitignore`) e coerenza tra naming/IO e test suite.

### Obiettivi strategici
- Eliminare regressioni legate alla working directory (casi `cd src && pytest`).
- Rendere la pipeline più “CI/Docker-ready” (percorsi deterministici e temporanei controllati).
- Ridurre drift tra runtime artifacts e repository (placeholder + ignore rules).

### Stato attuale
- Test suite: **green** (`49 passed`) sia da root che da `src/` con soluzione cwd-agnostic basata su `conftest.py`.
- Logging: standardizzato su `logs/` e creazione directory spostata “on write” (evita side-effect a import-time).
- `.gitignore`: aggiornato per ignorare runtime e tmp, mantenendo placeholder necessari (`logs/.gitkeep`, `output/**/.gitkeep`, `input/**/.gitkeep`).

---

## Branch: [development]

### [Unreleased]
> Scope: hardening test/logging + repo hygiene (commit-based)

---

- **`eecde6e` — build(packaging): add pyproject and installable transcriber entrypoint**
  - **Type:** CHANGED
  - **Cosa cambia:** il progetto diventa **installabile** (layout `src/`) e introduce un entrypoint CLI stabile `transcriber`.
  - **Dettagli:**
    - Aggiunto `pyproject.toml` (setuptools) con `package-dir` su `src/` e package discovery `where = ["src"]`
    - Definito `console script`: `transcriber = package.transcriber:main`
    - `transcriber --help` ora è **non-interattivo** (fast-path `-h/--help` → stampa help e termina)
  - **Impatto:** elimina la necessità di workaround tipo `PYTHONPATH=src`; rende la pipeline più pronta per CI/Docker.
  - **Evidenze:** `python -m pip install -e .` ✅ · `transcriber --help` ✅ · `python -m pytest` ✅ (49 passed)

---

- **`e60b0ad` — chore(tools): harden clean_project script (safe-by-default)**
  - **Type:** CHANGED
  - **Cosa cambia:** riscrittura hardenizzata di `tools/clean_project.sh` con approccio SAFE-by-default.
  - **Dettagli:**
    - Allowlist mirata (root cache + `src/` + `tools/` + `src/tests/tmp/**`)
    - Opt-in espliciti (OFF di default): `PURGE_LOGS`, `PURGE_OUTPUT`, `CLEAN_VENV`
    - Root guard (`README.md` + `src/` + `tools/`) per prevenire esecuzioni fuori repository
    - Output strutturato (sezioni + contatori) e modalità `DRY_RUN` / `VERBOSE`
  - **Impatto:** pulizia deterministica, auditabile e CI/Docker-ready senza rischio di cancellazioni accidentali.
  - **Evidenze:** `DRY_RUN=true VERBOSE=true tools/clean_project.sh` ✅ · `python -m pytest` ✅ (49 passed)

---

- **`4d25b47` — fix(pytest): force basetemp to src/tests/tmp cwd-agnostic**
  - **Type:** FIXED
  - **Cosa corregge:** elimina i failure in esecuzione test da sottocartelle (es. `cd src && python -m pytest`) dovuti a `--basetemp=src/tests/tmp` interpretato come path relativo a cwd.
  - **Come:** introdotto `src/tests/conftest.py` che forza `--basetemp` a un path assoluto ancorato alla project root; mantenuto `testpaths = src/tests`.
  - **Impatto:** test suite stabile indipendentemente dalla cwd.
  - **Evidenze:** `python -m pytest` ✅ (root), `cd src && python -m pytest` ✅ (49 passed)

---

- **`2d2668e` — fix(logging): use logs dir and create it on write**
  - **Type:** FIXED
  - **Cosa corregge:** standardizza la directory dei log su `logs/` (al posto di `log/`) e sposta `os.makedirs(LOG_DIR, exist_ok=True)` dentro la funzione di scrittura (no side-effect a import).
  - **Impatto:** logging più pulito e prevedibile; supporto naturale a placeholder `logs/.gitkeep`.
  - **Evidenze:** test suite ✅ (49 passed)

---

- **`9c79cc6` — chore(gitignore): ignore tmp and keep logs placeholder**
  - **Type:** CHANGED
  - **Cosa cambia:** aggiorna `.gitignore` per gestire `logs/**` ignorando i file runtime ma mantenendo `logs/.gitkeep`; conferma ignorare `tmp/` senza placeholder.
  - **Impatto:** repository più pulito, senza log accidentali versionati.

---

- **`77d4aa3` — chore(logs): track logs dir via gitkeep**
  - **Type:** ADDED
  - **Cosa introduce:** `logs/.gitkeep` per versionare la directory `logs/` senza versionare i log reali.
  - **Impatto:** struttura repo stabile e coerente tra macchine/CI.

---

- **`88ca4ae` — fix(pytest): set basetemp to src/tests/tmp**
  - **Type:** FIXED
  - **Nota:** intervento iniziale su `pytest.ini` che imposta `--basetemp=src/tests/tmp`; successivamente hardenizzato per cwd-agnostic con `4d25b47`.
  - **Impatto:** controllo dei temporanei pytest “dentro repo” (untracked).

---

- **`c82a247` — docs(changelog): record test suite alignment to current contracts**
  - **Type:** CHANGED
  - **Cosa cambia:** aggiornamento documentale per registrare l’allineamento della test suite ai contratti correnti.
  - **Impatto:** audit trail (docs).

---

- **`c060632` — test: align config and transcriber flows with new dirs and language prompt**
  - **Type:** CHANGED
  - **Cosa cambia:** riallinea test/contratti su percorsi e flussi aggiornati (directory e prompt lingua).
  - **Impatto:** riduzione drift tra codice e suite.

---

- **`408a302` — test(core): expect lang tag in output filenames**
  - **Type:** CHANGED
  - **Cosa cambia:** i test si adeguano al naming che include il tag lingua nei file generati.
  - **Impatto:** enforcement del contract di naming.

---

- **`71578d1` — chore(repo): add output/audio placeholder**
  - **Type:** ADDED
  - **Cosa introduce:** placeholder per mantenere la directory `output/audio/` in repo senza versionare output reali.
  - **Impatto:** struttura output consistente.

---

- **`d62a384` — chore(repo): remove legacy clean_project.sh from root**
  - **Type:** CHANGED
  - **Cosa cambia:** rimozione dello script legacy dalla root per ridurre ambiguità e centralizzare tooling.
  - **Impatto:** repo più ordinato.

---

- **`13381aa` — chore(gitignore): ignore runtime output audio/video folders**
  - **Type:** CHANGED
  - **Cosa cambia:** regole `.gitignore` per evitare versionamento accidentale di output runtime (audio/video).
  - **Impatto:** igiene repo.

---

- **`14ea605` — chore(tools): move clean script under tools/**
  - **Type:** CHANGED
  - **Cosa cambia:** consolidamento dello script di clean sotto `tools/`.
  - **Impatto:** struttura tooling più chiara.

---

- **`dec3330` — chore(repo): remove legacy audio placeholder**
  - **Type:** CHANGED
  - **Cosa cambia:** rimozione placeholder legacy non più coerente con la struttura definitiva.
  - **Impatto:** riduzione residui.

---

- **`0c53a7f` — chore(repo): align gitignore and placeholders for input/output structure**
  - **Type:** CHANGED
  - **Cosa cambia:** riallineamento di placeholder e ignore rules per la struttura `input/` e `output/`.
  - **Impatto:** percorso verso Docker/CI più pulito.

---

- **`bd2e6ab` — refactor(naming): include language in generated output filenames**
  - **Type:** CHANGED
  - **Cosa cambia:** naming degli output include la lingua (tag) per disambiguare e rendere tracciabile l’esecuzione.
  - **Impatto:** output più leggibili e deterministici.

---

- **`b7805af` — feat(io): read media from input audio+video and write transcripts to output/transcriptions**
  - **Type:** ADDED
  - **Cosa introduce:** supporto IO su input audio+video e scrittura trascrizioni su `output/transcriptions/`.
  - **Impatto:** pipeline IO coerente per batch/containers.

---

- **`83996b2` — refactor(lang): import ask_choice from cli_utils to avoid circular dependency**
  - **Type:** FIXED
  - **Cosa corregge:** evita dipendenze circolari nella gestione selezione lingua.
  - **Impatto:** stabilità import e run.

---

- **`26d683a` — chore(git): keep audio dir**
  - **Type:** ADDED
  - **Cosa introduce:** placeholder per mantenere directory necessarie (audio) nel repo.
  - **Impatto:** struttura stabile.

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
