#!/bin/bash
# =====================
# CLEAN_PROJECT.SH
# Pulizia sicura del progetto Python con struttura standardizzata
# =====================

SCRIPT_VERSION="1.0.0"
echo "clean_project.sh v$SCRIPT_VERSION"

# === CONFIGURAZIONE ===
# Imposta a true per simulare senza cancellare:
#   DRY_RUN=true ./clean_project.sh
DRY_RUN="${DRY_RUN:-false}"
echo "DEBUG: DRY_RUN is '$DRY_RUN'"

# Verifica di essere nella root del progetto (README.md e src/)
if [[ ! -f README.md || ! -d src ]]; then
  echo "❌ Esegui lo script dalla root del progetto (dove c'è README.md e src/)."
  exit 1
fi

log_action() { echo "[ACTION] $1"; }

safe_remove() {
  if [ "$DRY_RUN" = "true" ]; then
    [ -e "$1" ] || [ -L "$1" ] && echo "[DRY-RUN] rm -rf $1"
  else
    if [ -e "$1" ] || [ -L "$1" ]; then
      rm -rf "$1" 2>/dev/null
      log_action "Rimosso: $1"
    fi
  fi
}

safe_find_remove() {
  local base=$1; shift
  while IFS= read -r -d '' item; do
    safe_remove "$item"
  done < <(find "$base" "$@" -print0)
}

echo "Avvio pulizia del progetto... (dry-run=$DRY_RUN)"

echo "1) Pulizia cache Python (__pycache__, .pytest_cache, ecc.)..."
safe_find_remove . -type d -name '__pycache__'
safe_remove .pytest_cache
safe_remove .mypy_cache
safe_find_remove . -type d -name '*.egg-info'
safe_remove build

echo "2) Pulizia file .pyc..."
safe_find_remove . -type f -name '*.pyc'

echo "3) Svuotamento cartella src/tests/tmp/ ..."
safe_find_remove src/tests/tmp -type f
safe_find_remove src/tests/tmp -type d ! -path 'src/tests/tmp'

echo "4) Pulizia .txt e .wav temporanei (esclusi doc/ e resources/)..."
while IFS= read -r -d '' file; do
  safe_remove "$file"
done < <(find . -type f \( -name '*.txt' -o -name '*.wav' \) \
           ! -path './doc/*' \
           ! -path './src/tests/resources/*' -print0)

echo "5) Rimozione file .log fuori da /log..."
while IFS= read -r -d '' file; do
  safe_remove "$file"
done < <(find . -type f -name '*.log' ! -path './log/*' -print0)

echo "6) Pulizia soft di venv (__pycache__ e .pyc)..."
safe_find_remove ./venv -type d -name '__pycache__'
safe_find_remove ./venv -type f -name '*.pyc'

echo "Pulizia completata con successo."
