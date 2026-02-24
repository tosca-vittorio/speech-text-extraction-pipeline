# src/package/lang_utils.py

def select_language() -> str:
    """
    Prompt interattivo per chiedere all'utente la lingua dell'audio.
    Ritorna il codice ISO della lingua scelta (es. "it", "en", "fr", "es").
    """
    from package.cli_utils import ask_choice  # import dinamico per consentire il monkeypatch
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
