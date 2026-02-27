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
- 🟡 Hardening `tools/clean_project.sh` in corso (A2).
- ⬜ Packaging installabile + entrypoint CLI (A3).

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

## 🟡 A2 — Hardening `tools/clean_project.sh` (SAFE by default)

**Obiettivo:** avere uno script di pulizia **sicuro**, **mirato**, con output **verificabile** e opt-in per aree rischiose.

**Stato attuale:**

* Modifiche di hardening presenti **localmente** su `tools/clean_project.sh` ma **non ancora versionate** (work in progress).
* `git status -sb` mostra: `M tools/clean_project.sh`.

**Decisioni consolidate (repo):**

* `logs/` è tracciata solo come placeholder:

  * `.gitignore` ignora `logs/**` ma include `logs/.gitkeep`.
* `tmp/` è ignorata (project-local, untracked) e non richiede `.gitkeep`.

**DoD (A2) — da chiudere:**

* Committare lo script hardenizzato.
* Evidenze:

```bash
DRY_RUN=true VERBOSE=true tools/clean_project.sh | head -n 120
git status -sb
python -m pytest
```

---

## ⬜ A3 — Packaging minimale + entrypoint CLI installabile (P0)

**Obiettivo:** eliminare dipendenze da `PYTHONPATH=src` e ottenere **un comando unico** stabile (host/CI/Docker).

**Problema strutturale:** layout `src/` ma progetto non installabile ⇒ `python -m package.transcriber` da root può fallire senza `pythonpath`/workaround.

**Strategia (best practice):**
- Introdurre `pyproject.toml` (setuptools) con `package-dir` su `src/`.
- Installazione editable: `python -m pip install -e .`
- Definire `console_scripts` per eseguire la CLI via comando unico (es. `transcriber`).

**Attività:**
1) Aggiungere `pyproject.toml` in root con:
   - `[tool.setuptools] package-dir = {"" = "src"}`
   - `[tool.setuptools.packages.find] where = ["src"]`
   - `[project.scripts] transcriber = "package.transcriber:main"`
2) Garantire `main()` in `src/package/transcriber.py`:
   - `main()` deve essere il punto di ingresso stabile.
3) In venv: `python -m pip install -e .`
4) Verifiche: `transcriber --help` e run minima.

**DoD (A3):**
- Da root, dopo `pip install -e .`, funziona:
  - `transcriber --help`
  - `transcriber` (run minima)
- Nessuna istruzione richiede `PYTHONPATH`.
- README aggiornato con il comando canonico.

**Evidenze richieste:**
```bash
python -m pip install -e .
transcriber --help
transcriber
python -m pytest
```

## ⬜ A4 — Documentation alignment + Pylint + menu “clean” in Python (P0)

### ✅ A4.1 — README + ARCHITECTURE: allineamento comandi e flusso (truth-first)

**Obiettivo:** README senza istruzioni che falliscono + aggiornamento `docs/ARCHITECTURE.md` allo stato reale.

**DoD:**
- README: comandi canonici realmente funzionanti (host).
- `tools/clean_project.sh` documentato con esempi `DRY_RUN/VERBOSE` + opt-in.
- `docs/ARCHITECTURE.md` aggiornata su confini moduli e flusso attuale.

**Evidenze:**
```bash
python -m pytest
DRY_RUN=true VERBOSE=true tools/clean_project.sh | head -n 120
```

### ⬜ A4.2 — Introdurre Pylint come quality gate (evidenza extra)

**Obiettivo:** static analysis riproducibile come qualità aggiuntiva allo snapshot.

**Scelte:**

* Config unica: `.pylintrc` oppure `pyproject.toml` (una sola fonte).
* Target iniziale: `src/package` (scope ridotto).

**DoD / Evidenze:**

```bash
python -m pylint src/package
```

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
