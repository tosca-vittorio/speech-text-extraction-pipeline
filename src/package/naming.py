"""
Logica per costruire nomi coerenti di clip e trascrizioni.
"""

from package.errors import ConfigError

MODEL_SHORT = {
    "tiny":   "tny",
    "base":   "bse",
    "small":  "sml",
    "medium": "med",
}

MODALITA_SHORT = {
    "standard": "std",
    "accurata": "acc",
}


def genera_nome_file_output(
    base_name: str,
    modello: str,
    modalita: str,
    tipo: str,
    inizio: str | None = None,
    fine:   str | None = None,
    lang:   str | None = None,   # nuovo parametro opzionale
) -> str:
    """
    Restituisce il nome *senza* estensione, secondo la convenzione:

    • completa → `{base} (<mod>_<mode>) [(lang_<codice>)]`
    • parziale → `{base} (<start>_<end>) (<mod>_<mode>) [(lang_<codice>)]`

    Args:
        base_name: nome base del file audio (senza estensione)
        modello:   modello Whisper utilizzato (es. "tiny", "base", ...)
        modalita:  "standard" oppure "accurata"
        tipo:      "completa" oppure "parziale"
        inizio:    timestamp di inizio "hh:mm:ss" (richiesto per "parziale")
        fine:      timestamp di fine   "hh:mm:ss" (richiesto per "parziale")
        lang:      codice ISO lingua (es. "it", "en"); se None, non aggiunge il tag lingua

    Raises:
        ConfigError: se tipo="parziale" ma inizio o fine è None

    Returns:
        Nome del file senza estensione, es. "audio (sml_acc) (lang_en)" o
        "audio (000005_000010) (med_std) (lang_it)"
    """
    # Shortcode per modello e modalità
    mod_short  = MODEL_SHORT.get(modello, modello)
    mode_short = MODALITA_SHORT.get(modalita, modalita)
    mod_blocco = f"{mod_short}_{mode_short}"

    if tipo == "parziale":
        if not inizio or not fine:
            raise ConfigError("Per tipo='parziale' servono timestamp inizio/fine")
        # Converte "hh:mm:ss" in "hhmmss" (ma senza le ore se sono "00")
        def fmt(ts: str) -> str:
            return "".join(f"{int(part):02}" for part in ts.split(":")[1:])

        start, end = fmt(inizio), fmt(fine)
        name_core = f"{base_name} ({start}_{end}) ({mod_blocco})"

    else:
        # completa
        name_core = f"{base_name} ({mod_blocco})"

    # Aggiunge tag lingua se presente
    if lang:
        name_core += f" (lang_{lang})"

    return name_core
