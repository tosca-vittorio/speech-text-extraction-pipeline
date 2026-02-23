# Changelog

## [0.0.0]
### Added
- Script monolitico `transcriber.py` con
  - Selezione interattiva del file audiovideo
  - Scelta del modello Whisper (`tiny`, `base`, `small`, `medium`)
  - Selezione del device (`cuda` o `cpu`)
  - Opzione per trascrivere tutto o solo una parte tramite timestamp
  - Funzione `taglia_audio` basata su `ffmpeg`
  - Output trascrizione salvato in `.txt`

### Known Limitations
- Nessun test automatico
- Codice non modulare
- Nessun controllo degli errori avanzato
- Funzionamento esclusivamente interattivo da terminale
