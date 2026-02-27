#!/usr/bin/env bash
# =====================
# CLEAN_PROJECT.SH
# Pulizia progetto Python (SAFE by default, output compatto)
# =====================

set -Eeuo pipefail

SCRIPT_VERSION="1.4.5"
echo "clean_project.sh v$SCRIPT_VERSION"

# ---------------------
# CONFIG (env flags)
# ---------------------
DRY_RUN="${DRY_RUN:-false}"               # DRY_RUN=true tools/clean_project.sh
VERBOSE="${VERBOSE:-false}"               # VERBOSE=true tools/clean_project.sh
REQUIRE_ROOT_MARKERS="${REQUIRE_ROOT_MARKERS:-true}"

# Opt-in (OFF di default)
CLEAN_VENV="${CLEAN_VENV:-false}"         # pulizia soft dentro .venv/ (pycache + pyc)
PURGE_LOGS="${PURGE_LOGS:-false}"         # pulisce logs/*.log (mantiene .gitkeep)
PURGE_OUTPUT="${PURGE_OUTPUT:-false}"     # pulisce output/** (rischioso)

echo "DEBUG: DRY_RUN='$DRY_RUN' VERBOSE='$VERBOSE' CLEAN_VENV='$CLEAN_VENV' PURGE_LOGS='$PURGE_LOGS' PURGE_OUTPUT='$PURGE_OUTPUT'"

# ---------------------
# LOG
# ---------------------
log()    { echo "[INFO]   $*"; }
warn()   { echo "[WARN]   $*" >&2; }
action() { echo "[ACTION] $*"; }
err()    { echo "[ERROR]  $*" >&2; }

is_true() {
  case "${1,,}" in
    true|1|yes|y|on) return 0 ;;
    *) return 1 ;;
  esac
}

# ---------------------
# ROOT GUARD
# ---------------------
if is_true "$REQUIRE_ROOT_MARKERS"; then
  if [[ ! -f README.md || ! -d src || ! -d tools ]]; then
    err "Esegui lo script dalla root del progetto (README.md + src/ + tools/)."
    exit 1
  fi
fi

ROOT_PWD="$(pwd)"
log "Avvio pulizia del progetto in: $ROOT_PWD (dry-run=$DRY_RUN)"

# ---------------------
# COUNTERS
# ---------------------
ITEMS=0
SECTION_BEFORE=0

section_begin() {
  local title="$1"
  SECTION_BEFORE="$ITEMS"
  log "$title"
}

section_end() {
  local delta=$((ITEMS - SECTION_BEFORE))
  log " -> items: $delta"
}

# ---------------------
# SAFE RM
# ---------------------
safe_rm() {
  local target="$1"
  [[ -z "$target" ]] && return 0

  if [[ -e "$target" || -L "$target" ]]; then
    if is_true "$DRY_RUN"; then
      ((ITEMS+=1))
      is_true "$VERBOSE" && echo "[DRY-RUN] rm -rf -- '$target'"
      return 0
    fi

    # IMPORTANT: su Windows può fallire per file lock -> NON nascondere.
    if rm -rf -- "$target" 2>/dev/null; then
      ((ITEMS+=1))
      is_true "$VERBOSE" && action "Rimosso: $target"
    else
      warn "Impossibile rimuovere (file lock / permessi?): $target"
      return 1
    fi
  else
    is_true "$VERBOSE" && log "Non trovato: $target"
  fi
}

# Find mirata (NON su "."): solo dove serve davvero
find_and_rm() {
  local base="$1"; shift
  [[ -e "$base" ]] || { is_true "$VERBOSE" && log "Base non trovata: $base"; return 0; }

  while IFS= read -r -d '' p; do
    safe_rm "$p" || true
  done < <(find "$base" "$@" -print0 2>/dev/null || true)
}

# ---------------------
# RUN (SAFE allowlist)
# ---------------------

# 0) Root-level (senza find globale)
section_begin "0) Root-level cache (SAFE)..."
safe_rm "__pycache__"     || true
safe_rm ".pytest_cache"   || true
safe_rm ".mypy_cache"     || true
safe_rm ".ruff_cache"     || true
safe_rm ".coverage"       || true
safe_rm "coverage.xml"    || true
safe_rm "htmlcov"         || true
safe_rm ".tox"            || true
safe_rm ".nox"            || true
safe_rm "build"           || true
safe_rm "dist"            || true
# egg-info può essere anche in root (teniamo scan molto shallow)
find_and_rm . -maxdepth 2 -type d -name "*.egg-info"
section_end

# 1) Cache sotto src/ e tools/ (scansione mirata, veloce)
section_begin "1) Cache Python + build artifacts sotto src/ e tools/ (SAFE)..."
find_and_rm "src"   -type d -name "__pycache__"
find_and_rm "tools" -type d -name "__pycache__"
find_and_rm "src"   -type d -name "*.egg-info"
find_and_rm "tools" -type d -name "*.egg-info"
section_end

# 2) Compilati Python solo sotto src/ e tools/ (SAFE)
section_begin "2) File compilati Python (*.pyc, *.pyo) sotto src/ e tools/..."
find_and_rm "src"   -type f \( -name "*.pyc" -o -name "*.pyo" \)
find_and_rm "tools" -type f \( -name "*.pyc" -o -name "*.pyo" \)
section_end

# 3) tmp test: svuota src/tests/tmp/** (SAFE)
section_begin "3) tmp test: svuota src/tests/tmp/** (SAFE)..."
TMP_DIR="src/tests/tmp"
if [[ -d "$TMP_DIR" ]]; then
  if is_true "$DRY_RUN"; then
    # In dry-run mostra cosa verrebbe rimosso
    while IFS= read -r -d '' p; do
      safe_rm "$p" || true
    done < <(find "$TMP_DIR" -mindepth 1 -print0 2>/dev/null || true)
  else
    # In reale: elimina tutto sotto tmp in un colpo solo.
    # dotglob: include hidden files; nullglob: se vuota non espande pattern letterali.
    shopt -s dotglob nullglob

    # Conta entry immediate sotto tmp (best-effort, bash-native)
    tmp_items=( "$TMP_DIR"/* )
    tmp_count="${#tmp_items[@]}"

    # Elimina tutto (file/dir) sotto tmp
    rm -rf -- "$TMP_DIR"/* 2>/dev/null || true

    shopt -u dotglob nullglob

    # Aggiorna contatore (best-effort: entry immediate sotto tmp)
    ITEMS=$((ITEMS + tmp_count))

    is_true "$VERBOSE" && action "Svuotato: $TMP_DIR/** (entries=$tmp_count)"
  fi
else
  is_true "$VERBOSE" && log "$TMP_DIR non presente"
fi
section_end

# ---------------------
# OPT-IN
# ---------------------

if is_true "$PURGE_LOGS"; then
  section_begin "4) PURGE_LOGS=true: pulizia logs/*.log (opt-in)..."
  if [[ -d logs ]]; then
    while IFS= read -r -d '' p; do
      case "$p" in
        */.gitkeep) : ;;
        *) safe_rm "$p" || true ;;
      esac
    done < <(find logs -type f -name "*.log" -print0 2>/dev/null || true)
  fi
  section_end
else
  log "4) SKIP logs/: per pulire logs/*.log -> PURGE_LOGS=true"
fi

if is_true "$PURGE_OUTPUT"; then
  section_begin "5) PURGE_OUTPUT=true: pulizia output/** (opt-in, rischioso)..."
  if [[ -d output ]]; then
    while IFS= read -r -d '' p; do
      case "$p" in
        */.gitkeep) : ;;
        *) safe_rm "$p" || true ;;
      esac
    done < <(find output -mindepth 1 -print0 2>/dev/null || true)
  fi
  section_end
else
  log "5) SKIP output/: per pulire output/** -> PURGE_OUTPUT=true"
fi

if is_true "$CLEAN_VENV"; then
  section_begin "6) CLEAN_VENV=true: pulizia soft venv (pycache + pyc, opt-in)..."
  if [[ -d .venv ]]; then
    find_and_rm ".venv" -type d -name "__pycache__"
    find_and_rm ".venv" -type f \( -name "*.pyc" -o -name "*.pyo" \)
  elif [[ -d venv ]]; then
    find_and_rm "venv" -type d -name "__pycache__"
    find_and_rm "venv" -type f \( -name "*.pyc" -o -name "*.pyo" \)
  fi
  section_end
else
  log "6) SKIP venv/: per pulire __pycache__/pyc in venv -> CLEAN_VENV=true"
fi

log "Pulizia completata. items_removed_or_proposed=$ITEMS (dry-run=$DRY_RUN)"
