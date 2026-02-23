# Changelog

## [1.0.0] – 2025-03-26
### Added
- Estesa funzione `trascrivi` con due modalità: **Standard** (testo leggibile) e **Accurata** (per NLP/sottotitoli)
- Log dettagliato in `whisper_benchmark.log` con host, modello, device, durata, tempo e parole
- Calcolo della durata audio con `wave` (per .wav) e `ffprobe` (per altri)
- Scelta interattiva se mantenere o eliminare la clip audio tagliata
- Nuova funzione `timestamp_in_secondi` per confronti tra timestamp
- Identificazione host via `platform` o `wmic` (Windows)

### Changed
- Maggiori controlli sui timestamp e sulla durata dell'audio
- Migliorata robustezza nell’uso di `CUDA` (fallback automatico se non disponibile)
- Messaggi utente più esplicativi e chiari

### Fixed
- Gestione fallback se `ffprobe` o `wave` non riescono a determinare la durata
