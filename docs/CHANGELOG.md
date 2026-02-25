# Changelog

Tutte le modifiche rilevanti del progetto sono registrate in questo file.

Formato ispirato a [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/) con versione semantica.

## [2.1.1]

### Changed
- Riscritta la documentazione principale (`README.md`) in versione più dettagliata e coerente con lo stato attuale del progetto (setup, esecuzione, flusso CLI, path runtime, testing).
- Rifinita la struttura del changelog per mantenerlo leggibile e incrementale, evitando sezioni verbose non manutenibili.

### Added
- Creato `ARCHITECTURE.md` con descrizione estesa di layer, moduli, flusso runtime, invarianti e possibili evoluzioni.

### Documentation
- Allineati i riferimenti incrociati tra README, ARCHITECTURE e CHANGELOG.

### Tests
- Allineata la suite ai contract correnti:
  - path config aggiornati (`INPUT_AUDIO_DIR`, `MEDIA_EXTS`);
  - naming output con tag lingua `(lang_<codice>)`;
  - flow CLI: scelta lingua via `package.cli_utils.ask_choice` e menu file prefissato (`[🎧]/[🎬]/[🧪]`). (408a302, c060632)

---

## [2.1.0] - 2025-01-13

### Added
- Selezione lingua esplicita nel flusso CLI (`it`, `en`, `fr`, `es`).
- Propagazione della lingua alla chiamata Whisper.
- Naming output esteso con tag lingua `(lang_<codice>)`.
- Logging esteso con campo lingua.
- Nuovi test legati a lingua e gestione overwrite.

### Fixed
- Corretto comportamento overwrite quando l'utente nega la sovrascrittura in modalità prompt.
- Migliorata testabilità di `select_language()` evitando chiamate `input()` non mockate nei test.

---

## [2.0.0] - 2025-01-12

### Changed
- Refactor in package modulare (`audio`, `core`, `naming`, `logger`, `config`, `cli_utils`, `errors`, `transcriber`).
- Migliorata separazione responsabilità e copertura test.

---

## [1.1.0]

### Changed
- Consolidamento progressivo della versione refactor con focus su stabilità CLI e qualità test.

---

## [1.0.0]

### Added
- Prima versione stabile del transcriber CLI.

---

## [0.0.0]

### Added
- Prototipo iniziale del transcriber monolitico.

---