# src/package/errors.py

class TranscriberError(Exception):
    """Classe base per le eccezioni di trascrizione."""

class InvalidChoiceError(TranscriberError):
    """Sollevata quando l'utente non fornisce una scelta valida."""

class AudioProcessingError(TranscriberError):
    """Sollevata in caso di problemi durante il taglio o la lettura audio."""

class ConfigError(TranscriberError):
    """Sollevata in caso di problemi con le cartelle audio/log."""
