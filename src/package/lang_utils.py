# src/package/lang_utils.py

"""
Gestione lingue.

Espone le lingue supportate e funzioni helper per selezione/normalizzazione
del codice lingua usato da Whisper e dalla naming strategy.
"""

from package.cli_utils import ask_choice


def select_language() -> str:
    """
    Prompt interattivo per chiedere all'utente la lingua dell'audio.
    Ritorna il codice ISO della lingua scelta (es. "it", "en", "fr", "es").
    """
    LANGUAGES = {
        "it": "Italiano",
        "en": "Inglese",
        "fr": "Francese",
        "es": "Spagnolo",
        # In futuro puoi aggiungere altri codici cartellati qui (es. "de": "Tedesco", ecc.)
    }

    # Costruisco la lista di opzioni nel formato "it (Italiano)", "en (Inglese)", ecc.
    choices = [f"{code} ({name})" for code, name in LANGUAGES.items()]

    # Chiedo all'utente di scegliere una di queste stringhe
    selection = ask_choice("🌐 In quale lingua è l'audio?", choices)

    # La prima "parola" restituita è il codice ISO (es. "en")
    return selection.split()[0]
