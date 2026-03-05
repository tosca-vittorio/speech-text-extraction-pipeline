"""
Logica per costruire nomi coerenti di clip e trascrizioni.
"""

from dataclasses import dataclass

from package.errors import ConfigError

MODEL_SHORT = {
    "tiny": "tny",
    "base": "bse",
    "small": "sml",
    "medium": "med",
}

MODALITA_SHORT = {
    "standard": "std",
    "accurata": "acc",
}


@dataclass(frozen=True)
class NamingParams:
    """Parametri per generare il nome file output."""

    base_name: str
    modello: str
    modalita: str
    tipo: str
    inizio: str | None = None
    fine: str | None = None
    lang: str | None = None


def genera_nome_file_output(params: NamingParams) -> str:
    """
    Restituisce il nome *senza* estensione, secondo la convenzione:

    • completa → `{base} (<mod>_<mode>) [(lang_<codice>)]`
    • parziale → `{base} (<start>_<end>) (<mod>_<mode>) [(lang_<codice>)]`

    Args:
        params: parametri di naming aggregati in `NamingParams`.

    Raises:
        ConfigError: se tipo="parziale" ma inizio o fine è None

    Returns:
        Nome del file senza estensione, es. "audio (sml_acc) (lang_en)" o
        "audio (000005_000010) (med_std) (lang_it)"
    """
    # Shortcode per modello e modalità
    mod_short = MODEL_SHORT.get(params.modello, params.modello)
    mode_short = MODALITA_SHORT.get(params.modalita, params.modalita)
    mod_blocco = f"{mod_short}_{mode_short}"

    if params.tipo == "parziale":
        if not params.inizio or not params.fine:
            raise ConfigError("Per tipo='parziale' servono timestamp inizio/fine")

        # Converte "hh:mm:ss" in "hhmmss" (ma senza le ore se sono "00")
        def fmt(ts: str) -> str:
            return "".join(f"{int(part):02}" for part in ts.split(":")[1:])

        start, end = fmt(params.inizio), fmt(params.fine)
        name_core = f"{params.base_name} ({start}_{end}) ({mod_blocco})"
    else:
        # completa
        name_core = f"{params.base_name} ({mod_blocco})"

    # Aggiunge tag lingua se presente
    if params.lang:
        name_core += f" (lang_{params.lang})"

    return name_core
