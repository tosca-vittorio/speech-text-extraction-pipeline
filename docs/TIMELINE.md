# TIMELINE — `speech-text-extraction-pipeline` (Python · Whisper CLI)

## Scopo
Questo documento governa l’avanzamento del progetto **speech-text-extraction-pipeline**.
La timeline è organizzata in step sequenziali con **Definition of Done (DoD)** verificabile.

Principi:
- **Truth-first**: niente ✅ senza evidenza.
- **Progressione**: hardening → riproducibilità → Docker → modalità batch → Kubernetes → CI.
- **Anti-ridondanza**: i dettagli “owner” vivono in `docs/ARCHITECTURE.md`, `docs/CHANGELOG.md`, `README.md`.

---

## Legenda stati
- ✅ = completato e verificato
- 🟡 = presente ma da verificare/chiudere (parziale)
- ⬜ = da fare

---

## Baseline: evidenze standard richieste (per ogni step)
Minimo:
- `git status -sb`
- `python -m pytest`  (comando canonico, cwd-agnostic)
Se lo step tocca Docker:
- `docker build ...`
- `docker run ... python -m pytest`

---

# A — Consolidamento & Hardening (PRIORITÀ P0)


## ✅ A0 — Snapshot stato attuale (AS-IS)
**Obiettivo:** fissare punto di partenza reale, difetti noti e rischi.

**Evidenze (raccolte):**
- Da root:
  - `python -m pytest` → ✅ (49 passed)
- Da `src/`:
  - `cd src && python -m pytest` → ✅ (49 passed)

**Rischio storico (risolto in A1):**
- In precedenza la test suite era **cwd-sensitive** a causa di `--basetemp=src/tests/tmp` definito in `pytest.ini` (path relativo).
  - Esecuzione da `src/` tentava di creare `src/src/tests/tmp` → errori.

**Rischi dichiarati (aggiornati):**
- ✅ Blocco “cwd-agnostic test execution” risolto (A1).
- ✅ Hardening `tools/clean_project.sh` completato  (A2).
- ✅ Packaging installabile + entrypoint CLI (A3).

---

## ✅ A1 — Rendere i test cwd-agnostic (root-safe e src-safe)
**Obiettivo:** la test suite deve funzionare indipendentemente dalla working directory.

**Implementazione (fix applicato):**
- `pytest.ini`: configurazione minimale con `testpaths = src/tests` (niente `basetemp` relativo).
- `src/tests/conftest.py`: forzato `basetemp` a un path **assoluto** sotto repo:
  - `<repo_root>/src/tests/tmp`
  - cartella project-local, untracked (gestita via `.gitignore`)

**Commit di chiusura:**
- `4d25b47` — `fix(pytest): force basetemp to src/tests/tmp cwd-agnostic`

**DoD (A1) — raggiunto:**
- Da root: `python -m pytest` → ✅ (49 passed)
- Da `src/`: `cd src && python -m pytest` → ✅ (49 passed)
- Nessun path tmp si “doppia” (`src/src/...`) al variare della cwd.

**Evidenze:**
```bash
# root
python -m pytest
# -> 49 passed

# src/
cd src
python -m pytest
# -> 49 passed
cd ..
```

---

## ✅ A2 — Hardening `tools/clean_project.sh` (SAFE by default)

**Obiettivo:** avere uno script di pulizia **sicuro**, **mirato**, con output **verificabile** e opt-in per aree rischiose.

**Commit di chiusura:**
- `e60b0ad` — `chore(tools): harden clean_project script (safe-by-default)`

**Cambiamenti (high-level):**
- SAFE-by-default: allowlist mirata (root cache + `src/` + `tools/` + `src/tests/tmp/**`).
- Opt-in espliciti (OFF di default): `PURGE_LOGS`, `PURGE_OUTPUT`, `CLEAN_VENV`.
- Root guard (marker `README.md` + `src/` + `tools/`) per evitare esecuzioni fuori repo.
- Output strutturato (sezioni + contatori) e modalità `DRY_RUN`/`VERBOSE`.

**Evidenze (A2) — raggiunto:**
```bash
# dry-run auditabile
DRY_RUN=true VERBOSE=true tools/clean_project.sh | head -n 120

# esecuzione reale safe (default: nessun opt-in)
DRY_RUN=false VERBOSE=true tools/clean_project.sh

# qualità repo
python -m pytest
# -> 49 passed
```

---

## ✅ A3 — Packaging minimale + entrypoint CLI installabile (P0)

**Obiettivo:** eliminare dipendenze da `PYTHONPATH=src` e ottenere **un comando unico** stabile (host/CI/Docker).

**Implementazione (packaging):**
- Aggiunto `pyproject.toml` (setuptools) con layout `src/`:
  - `[tool.setuptools] package-dir = {"" = "src"}`
  - `[tool.setuptools.packages.find] where = ["src"]`
  - `[project.scripts] transcriber = "package.transcriber:main"`

**Implementazione (CLI help non-interattivo):**
- `src/package/transcriber.py`: aggiunto fast-path su `-h/--help` per stampare help ed uscire **senza prompt interattivi**.

**Commit di chiusura:**
- `eecde6e` — `build(packaging): add pyproject and installable transcriber entrypoint`

**DoD (A3) — raggiunto (host):**
- Install editable: `python -m pip install -e .` → ✅
- CLI entrypoint: `transcriber --help` → ✅ (stampa help e termina senza menu)
- Qualità: `python -m pytest` → ✅ (49 passed)

**Note (truth-first):**
- `python -m package.transcriber --help` da root può ancora fallire senza installazione (layout `src/`): il comando canonico “installabile” è `transcriber`.

## 🟡 A4 — Documentation alignment + Pylint + menu “clean” in Python (P0)

### ✅ A4.1 — README + ARCHITECTURE: allineamento comandi e flusso (truth-first)

**Obiettivo:** README senza istruzioni che falliscono + aggiornamento `docs/ARCHITECTURE.md` allo stato reale.

**DoD:**
- README: comandi canonici realmente funzionanti (host).
- `tools/clean_project.sh` documentato con esempi `DRY_RUN/VERBOSE` + opt-in.
- `docs/ARCHITECTURE.md` aggiornata su confini moduli e flusso attuale.

**Evidenze (host):**
```bash
# entrypoint canonico
transcriber --help

# qualità repo invariata
python -m pytest

# clean script (doc examples)
DRY_RUN=true VERBOSE=true tools/clean_project.sh | head -n 120
```


### 🟡 A4.2 — Pylint quality gate (baseline + burn-down verso 10/10)

**Obiettivo:** introdurre static analysis **riproducibile** e **auditabile** come quality gate aggiuntivo (prima “soft”, poi “hard” quando il codice è allineato).

**Decisione (truth-first):** allo stato attuale il run “hard” fallisce (exit code non-zero), quindi adottiamo **gate soft** (`--exit-zero`) per non bloccare lo sviluppo, mentre facciamo burn-down incrementale verso **10/10**.

#### Macro-area: Lint Hardening (subtask)

##### ✅ A4.2.1 — Installazione Pylint (host)
**Evidenza:**
```bash
python -m pip install -U pylint
python -m pylint --version
# pylint 4.0.5 (host)
```

##### ✅ A4.2.2 — Baseline lint (hard run) su `src/package`

**Evidenza:**

```bash
python -m pylint src/package
echo $?   # osservato: 28 (hard fail)
```

**Nota:** rating corrente osservato: **8.74/10**.

##### ✅ A4.2.3 — Gate “soft” (non bloccante) su `src/package`

**Evidenza:**

```bash
python -m pylint --exit-zero src/package
echo $?   # osservato: 0
```

##### ✅ A4.2.4 — Standardizzare “comando canonico” di lint (repo-level)

**Decisione:** il comando canonico di lint (repo-level, non bloccante durante burn-down strutturale) è:

```bash
python -m pylint --exit-zero src/package
```

**Perché:** consente un gate stabile, riproducibile e auditabile anche con warning strutturali ancora aperti (`too-many-*`), evitando hard fail durante la fase incrementale.

**Nota operativa:** il comando hard resta usato come metrica di avanzamento/monitoraggio qualità:

```bash
python -m pylint src/package
```

**Evidenza (snapshot corrente):**

* `python -m pytest` → **49 passed**
* `python -m pylint src/package` → **9.63/10**, exit code **8** (warning residui strutturali)

---

##### ⬜ A4.2.5 — Definire config unica (UNA sola fonte)

**Scelte (da chiudere):**

* `.pylintrc` **oppure** `pyproject.toml` (no duplicazioni)
* target iniziale: `src/package` (scope ridotto, burn-down controllabile)

##### ⬜ A4.2.6 — Burn-down chirurgico verso 10/10 (incrementale)

###### ✅ A4.2.6.a — Add module docstrings (batch su moduli base)
**Scopo:** eliminare `missing-module-docstring` in modo massivo ma conservativo.

**File toccati:**
- `src/package/audio.py`
- `src/package/cli_utils.py`
- `src/package/config.py`
- `src/package/errors.py`
- `src/package/lang_utils.py`
- `src/package/logger.py`

**Evidenze:**
```bash
python -m pytest
# -> 49 passed

python -m pylint src/package
# -> rating osservato ~9.22/10 (hard exit code resta non-zero)
```

**Regole:**

* 1 warning alla volta, commit atomico.
* Prima: fix “cheap wins” (newline, trailing newline, line-too-long locali, import order).
* Poi: warning strutturali (broad-exception, raise-from, subprocess.run check).
* Infine: refactor controllati (too-many-branches/locals/statements) **solo** se motivato e con test invariati.

**DoD finale A4.2 (per passare a ✅):**

* Gate soft documentato come comando canonico.
* Config unica scelta e applicata (se necessaria).
* Target iniziale raggiunge **10/10** (o policy esplicita di rating minimo) con evidenze registrate.

###### ✅ A4.2.6.b — Hardening `get_audio_duration`: fallback "N/A" su WAV invalidi e failure ffprobe
**Contesto:** i test usano WAV “stub” (header incompleto) e possono generare `EOFError`/`wave.Error`. Inoltre, `ffprobe` può fallire/sollevare eccezioni (anche se `check=False`).

**Decisione:** la funzione deve essere **safe** e restituire `"N/A"` su errori gestibili, senza propagare eccezioni.

**Evidenze:**
```bash
python -m pytest
# -> 49 passed

python -m pylint src/package
# -> rating osservato ~9.30/10 (hard exit code osservato: 28)
```

###### ✅ A4.2.6.c — Fix broad-exception in `cli_utils.get_csproduct_name()` (narrow exceptions)
**Scopo:** eliminare `W0718 broad-exception-caught` mantenendo identico comportamento di fallback.

**Decisione:** sostituito `except Exception` con catch specifico per failure OS/subprocess/parsing:
- `FileNotFoundError`, `OSError` → `wmic` assente / problemi OS
- `subprocess.CalledProcessError` → esecuzione comando fallita (quando usato `check=True`)
- `ValueError` → output/parsing inatteso (difensivo)

**Commit di chiusura:**
- `b51b701` — `chore(lint): narrow exceptions in csproduct lookup`

**Evidenze:**
```bash
python -m pytest
# -> 49 passed

python -m pylint src/package
# -> rating osservato >= 9.48/10 (hard exit code non-zero)
```

###### ✅ A4.2.6.d — Stabilizzare monkeypatch `ask_choice` (import toplevel) + fix test transcriber

**Problema:** spostando `ask_choice` a import toplevel in `lang_utils`, i test che patchavano
`package.cli_utils.ask_choice` non intercettavano più la chiamata reale (simbolo già “bound” in `lang_utils`),
causando `pytest: reading from stdin` e `StopIteration` nei test end-to-end del transcriber.

**Decisione:** mantenere `ask_choice` importato a toplevel (best practice per lint e leggibilità) e
allineare i test a patchare il simbolo effettivamente usato:

* `package.lang_utils.ask_choice`
* nei test transcriber: patch in parallelo `trans_mod.ask_choice` e `lang_mod.ask_choice` con la stessa sequenza.

**Commit di chiusura:**

* `70d7977` — `test(lang): align monkeypatch targets with toplevel ask_choice import`

**Evidenze:**

```bash
python -m pytest
# -> 49 passed
```

###### ✅ A4.2.6.e — Fix `invalid-name` in lang utils (LANGUAGES → languages)

**Scopo:** eliminare `C0103 invalid-name` senza cambiare il contratto della funzione.

**Commit di chiusura:**

* `12f30f8` — `chore(lint): rename local languages mapping in lang utils`

**Evidenze:**

```bash
python -m pytest
# -> 49 passed

python -m pylint src/package
# -> rating osservato 9.56/10
```

###### ✅ A4.2.6.f — Remove `unnecessary-lambda-assignment` in naming (lambda → helper)

**Scopo:** eliminare `C3001 unnecessary-lambda-assignment` sostituendo la lambda locale con una helper `def`.

**Commit di chiusura:**

* `ceefa41` — `chore(lint): replace local lambda with helper in naming`

**Evidenze:**

```bash
python -m pytest
# -> 49 passed

python -m pylint src/package
# -> rating osservato 9.59/10
```

###### ✅ A4.2.6.g — Annotare broad catch intenzionale nel wrapper CLI (`__main__`)

**Contesto:** nel blocco `if __name__ == "__main__":` è accettabile un catch-all finale per stampare
un messaggio “Errore imprevisto” e terminare in modo controllato (entrypoint CLI).

**Decisione:** mantenere `except Exception` ma documentare/annotare l’intento con disable mirato Pylint
sulla singola riga (no soppressione globale).

**Commit di chiusura:**
- `0a53f8f` — `chore(lint): annotate intentional broad catch in cli entrypoint`

**Evidenze:**

```bash
python -m pytest
# -> 49 passed

python -m pylint src/package
echo $?
# -> rating osservato 9.63/10 (exit code osservato: 8)
```

---

### ⬜ A4.3 — Avviare “pulizia” dal programma Python (menu/command)

**Obiettivo:** poter eseguire “pulisci (SAFE)” dalla CLI Python.

**Nota implementativa:**

* Default: pulizia SAFE (allowlist).
* Azioni rischiose restano opt-in (output/logs/venv) + conferma esplicita.

**DoD / Evidenze:**

```bash
transcriber
# -> menu include "Pulisci (safe)"
```

---

# B — Docker (CORE GOAL)

## ⬜ B1 — Dockerfile CPU-only (baseline riproducibile)

**Obiettivo:** build e test in container.

**Attività:**

* `Dockerfile` con:

  * `python:3.10-slim` (o compatibile)
  * install `ffmpeg`
  * install requirements CPU (`docs/requirements/requirements-cpu.txt` o equivalente)
  * `WORKDIR /app`
  * esecuzione test

**DoD (B1):**
- `docker build` ok
- `docker run ... python -m pytest` green (in container)
- I test in container devono essere eseguiti dalla root (`/app`) per coerenza con l’esecuzione canonica.

**Evidenze richieste:**
```bash
docker build -t speech-pipeline:dev .
docker run --rm speech-pipeline:dev python -m pytest
```

---

## ⬜ B2 — Volumi: input/output/log + cache modelli

**Obiettivo:** container stateless, dati persistenti su host.

**Attività:**

* Montare:

  * `./input:/app/input`
  * `./output:/app/output`
  * `./log:/app/log`
* Valutare un volume per cache modelli (se Whisper scarica).

**DoD (B2):**

* Output `.txt` generato in `output/transcriptions/` su host.
* Log scritto su host.
* Nessun file generato “a sorpresa” nel layer dell’immagine.

---

## ⬜ B3 — `.dockerignore` + hardening build context

**Obiettivo:** ridurre dimensioni e rischio leak.

**DoD (B3):**

* `.venv/`, `.git/`, cache, `__pycache__/`, `.pytest_cache/` esclusi.
* Build context minimale.

---

# C — Modalità Batch (necessaria per Docker serio & K8s)

## ⬜ C1 — CLI non-interattiva (argparse)

**Obiettivo:** esecuzione senza prompt, adatta a CI/container/job.

**Attività:**

* Flags minimi:

  * `--input <file>`
  * `--model`
  * `--device`
  * `--lang`
  * `--mode standard|accurata`
  * `--scope tutto|parziale` (+ `--start/--end`)
  * `--overwrite yes|no`
* Mantenere modalità interattiva come default se nessun flag.

**DoD (C1):**

* Comando batch produce output senza input() e senza menu.
* Test minimi per parsing args.

---

# D — Kubernetes (learning + applicazione corretta)

## ⬜ D1 — Concetti K8s + caso d’uso corretto (Job)

**Obiettivo:** usare K8s come orchestratore **per batch job**, non per “servizio sempre acceso” inutile.

**Attività:**

* Documentare concetti base: Pod, Job, Deployment, ConfigMap, PVC.
* Decidere: Job con volume output vs log-only.

**DoD (D1):**

* Documento `docs/k8s-concepts.md` (sintetico ma operativo).
* Scelta architetturale motivata (Job vs Deployment).

---

## ⬜ D2 — Manifest minimi (kind/minikube)

**DoD (D2):**

* `job.yaml` esegue 1 trascrizione batch.
* Output/log verificabili.
* Run locale documentata.

---

# E — Smoke test & CI (quality gates)

## ⬜ E1 — Smoke test E2E ufficiale

**Obiettivo:** 1 comando che valida integrità base.

**DoD (E1):**

* Script `tools/smoke_test.sh` (o equivalente) che:

  * usa un file audio test
  * genera una trascrizione
  * verifica output non vuoto
* Eseguibile sia su host che in Docker.

---

## ⬜ E2 — CI minimale (pytest + docker build)

**DoD (E2):**
- Pipeline che esegue:
  - `python -m pytest`
- (Quando B1 è attivo) build Docker su branch principali.

---

# F — Evoluzioni architetturali (post-Docker, post-batch, post-smoke)

## ⬜ F1 — Estrarre service layer puro (senza I/O)
**Obiettivo:** aumentare testabilità e ridurre accoppiamento tra CLI e logica applicativa.

**Strategia (incrementale, conservativa):**
- Identificare funzioni “pure” in `core.py`/`transcriber.py` e separarle da file-system/logging.
- Introdurre un modulo application/service (es. `src/package/services/*`) che:
  - riceve input già risolti (path, config),
  - restituisce risultati (testo, metadata) senza side-effect.
- CLI resta adapter: parsing args + scelta input + chiamata service + write output/log.

**DoD (F1):**
- Test suite invariata e verde (host + docker quando già attivo).
- Nessun cambiamento di contract output senza decisione in SoT.
- `docs/ARCHITECTURE.md` aggiornata (confini: CLI adapter vs service layer).

---

# G — Documentation Alignment & Architecture Review (HARD GATE)

## ⬜ G1 — Full documentation truth-alignment

**Obiettivo:** garantire che documentazione e stato reale del repo siano coerenti al 100%.

Questa fase va eseguita:
- Dopo A (hardening chiuso)
- Dopo B (Docker baseline stabile)
- Dopo D (K8s applicato)
- Prima di dichiarare milestone stabile

**Checklist obbligatoria:**

- `README.md`
  - Comandi canonici funzionano realmente
  - Nessun riferimento obsoleto (PYTHONPATH manuale, ecc.)
- `docs/ARCHITECTURE.md`
  - Confini moduli coerenti con codice reale
  - Service layer (se introdotto) documentato
- `docs/TIMELINE.md`
  - Stati step corretti (no falsi ✅)
  - Debito tecnico aggiornato
- `docs/CHANGELOG.md`
  - Coerente con commit reali
- Struttura repo:
  - Nessuna cartella “orfana”
  - Nessuna doc fantasma

**DoD (G1):**
- Nessuna incoerenza tra doc e codice.
- Nessuna istruzione nel README che fallisce.
- Nessun riferimento a path o flussi non più esistenti.
