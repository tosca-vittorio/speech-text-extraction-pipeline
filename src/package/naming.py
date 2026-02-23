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
) -> str:
    """
    Restituisce il nome *senza* estensione, secondo la convenzione:

    • completa → `{base} (<mod>_<mode>)`
    • parziale → `{base} (<start>_<end>) (<mod>_<mode>)`

    Args:
        tipo: "completa" oppure "parziale".
    """
    mod_short  = MODEL_SHORT.get(modello,   modello)
    mode_short = MODALITA_SHORT.get(modalita, modalita)
    mod_blocco = f"{mod_short}_{mode_short}"

    if tipo == "parziale":
        if not inizio or not fine:
            raise ConfigError("Per tipo='parziale' servono timestamp inizio/fine")
        fmt = lambda ts: "".join(f"{int(p):02}" for p in ts.split(":")[1:])
        start, end = fmt(inizio), fmt(fine)
        return f"{base_name} ({start}_{end}) ({mod_blocco})"

    # completa
    return f"{base_name} ({mod_blocco})"
