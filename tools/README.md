# Tools — clean_project.sh

Questo repository include lo script `tools/clean_project.sh` per la pulizia **sicura** del progetto Python.

## Obiettivo

Ridurre rumore e artefatti locali (cache, bytecode, tmp dei test) mantenendo:
- comportamento **SAFE by default**
- output **comprensibile e verificabile**
- compatibilità con Git Bash / MSYS2 su Windows

Lo script non richiede dipendenze extra: usa `bash` (Git Bash/MSYS2) + `find` + `rm`.

---

## Root guard (sicurezza)

Per default (`REQUIRE_ROOT_MARKERS=true`) lo script rifiuta l’esecuzione se non trova i marker:
- `README.md`
- `src/`
- `tools/`

Questo evita cancellazioni accidentali se lanciato dalla cartella sbagliata.

Disabilitabile (sconsigliato):
```bash
REQUIRE_ROOT_MARKERS=false tools/clean_project.sh
```

---

## Cosa pulisce (SAFE, default)

Senza alcun flag opt-in, lo script pulisce **solo**:

1. **Root-level cache/artifacts**
   - `__pycache__/`
   - `.pytest_cache/`
   - `.mypy_cache/`
   - `.ruff_cache/`
   - `.coverage`, `coverage.xml`, `htmlcov/`
   - `.tox/`, `.nox/`
   - `build/`, `dist/`
   - `*.egg-info/` (fino a maxdepth 2 nella root)

2. **Cache/bytecode sotto `src/` e `tools/`**
   - `__pycache__/`
   - `*.pyc`, `*.pyo`
   - `*.egg-info/`

3. **Tmp dei test**
   - svuota il **contenuto** di `src/tests/tmp/**` (la directory `src/tests/tmp/` resta presente)

> Nota: `src/tests/tmp` è considerata area “effimera” per test, quindi è safe eliminarne il contenuto.
> Importante: dopo aver rieseguito `python -m pytest`, è normale che `src/tests/tmp/` venga ricreata e ripopolata dai test.

---

## Cosa NON pulisce (default)

Per ridurre rischi, NON vengono toccati **a meno di opt-in**:
- `logs/` (potrebbe contenere log utili)
- `output/` (potrebbe contenere output importanti)
- `.venv/` o `venv/` (la venv è ripristinabile ma può essere costosa da ricreare)

---

## Flags (via variabili d’ambiente)

### Quick reference

| Variabile | Default | Effetto |
|---|---:|---|
| `DRY_RUN` | `false` | Simula le rimozioni senza cancellare nulla |
| `VERBOSE` | `false` | Stampa le singole azioni (oltre ai contatori) |
| `REQUIRE_ROOT_MARKERS` | `true` | Blocca l’esecuzione fuori dalla root repo |
| `PURGE_LOGS` | `false` | Opt-in: pulisce `logs/*.log` (mantiene `.gitkeep`) |
| `PURGE_OUTPUT` | `false` | Opt-in: pulisce `output/**` (mantiene `.gitkeep`) |
| `CLEAN_VENV` | `false` | Opt-in: pulizia soft in `.venv/` o `venv/` (pycache/pyc/pyo) |

### Modalità consigliata: dry-run
Mostra cosa verrebbe eliminato senza toccare nulla impostato a `true`.

> Default: `DRY_RUN=false` (esecuzione reale).

```bash
DRY_RUN=true tools/clean_project.sh
```

### Verbose

Stampa ogni singola rimozione (utile come evidenza).

```bash
DRY_RUN=true VERBOSE=true tools/clean_project.sh
```

---

## Opt-in (comportamenti potenzialmente rischiosi)

### PURGE_LOGS=true

Pulisce `logs/*.log`
```bash
PURGE_LOGS=true DRY_RUN=true VERBOSE=true tools/clean_project.sh
PURGE_LOGS=true DRY_RUN=false VERBOSE=true tools/clean_project.sh
```

**Quando usarlo:** quando i log sono solo artefatti di run/test e non servono più.

---

### PURGE_OUTPUT=true

Pulisce `output/**` (mantiene eventuale `.gitkeep` se presente).

```bash
PURGE_OUTPUT=true DRY_RUN=true VERBOSE=true tools/clean_project.sh
PURGE_OUTPUT=true DRY_RUN=false VERBOSE=true tools/clean_project.sh
```

**Attenzione:** `output/` può contenere risultati importanti. Usalo solo se sei certo che sia rigenerabile.

---

### CLEAN_VENV=true

Pulizia “soft” dentro `.venv/` o `venv/` rimuovendo solo:

* `__pycache__/`
* `*.pyc`, `*.pyo`

```bash
CLEAN_VENV=true DRY_RUN=true VERBOSE=true tools/clean_project.sh
CLEAN_VENV=true DRY_RUN=false VERBOSE=true tools/clean_project.sh
```

**È safe?** In generale sì: `pyc` e `__pycache__` sono ricostruibili.
**Tradeoff:** su Windows può produrre molte righe e impiegare tempo, ma non rompe l’ambiente.

---

## Workflow “truth-first” consigliato

Prima:

```bash
git status -sb
python -m pytest -q
```

Dry-run (evidenza):

```bash
DRY_RUN=true VERBOSE=true tools/clean_project.sh | head -n 250
```

**Cosa aspettarsi in output (audit):**
- Sezioni numerate (`0)`, `1)`, `2)`, …)
- Per ogni sezione: `-> items: N` (numero di target rimossi/proposti)
- Footer: `items_removed_or_proposed=N` (somma best-effort)
  
> Nota sui contatori: `items_removed_or_proposed` è best-effort.
> In particolare, per `src/tests/tmp/**` il conteggio `entries=N` indica le **entry di primo livello** sotto `src/tests/tmp/` (directory/file), non il numero totale di file ricorsivi.

# run reale SIMULATION (default, output compatto)
tools/clean_project.sh

# run reale (REALITY)

```bash
DRY_RUN=false VERBOSE=true tools/clean_project.sh
```

Dopo:

```bash
find src/tests/tmp -mindepth 1 -print 2>/dev/null | head -n 50
python -m pytest -q
git status -sb
```

---

## Troubleshooting

### `src/tests/tmp` sembra non svuotarsi

Verifica **quando** stai guardando la cartella:

- Subito dopo `tools/clean_project.sh` (run reale) → deve risultare vuota (a parte la directory `src/tests/tmp/`).
- Dopo `python -m pytest` → è normale che venga **ripopolata** dai test.

Se anche **subito dopo** lo script restano file/dir, quasi sempre significa:
- file lock su Windows (processo Python/ffmpeg rimasto aperto),
- permessi.

Soluzione:
- chiudi processi che tengono lock,
- rilancia lo script,
- verifica con:
```bash
find src/tests/tmp -mindepth 1 -print 2>/dev/null | head -n 50
```

### Output “troppo lungo”

Usa `VERBOSE=false` (default) e affidati ai contatori `items:` e `items_removed_or_proposed`.

---

## File location

* Script: `tools/clean_project.sh`
* Documentazione: `tools/README.md`

---