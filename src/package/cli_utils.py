# src/package/cli_utils.py

"""
Utility CLI.

Contiene helper per input utente, validazione delle scelte e funzioni di
supporto al flusso interattivo del transcriber.
"""

import platform
import subprocess
from datetime import datetime
from package.errors import InvalidChoiceError

def get_csproduct_name() -> str:
    """
    Ritorna il nome del prodotto della macchina (hostname o WMIC su Windows).
    """
    if platform.system().lower() != "windows":
        return platform.node()
    try:
        result = subprocess.run(
            ["wmic", "csproduct", "get", "name"],
            capture_output=True, text=True, check=True
        )
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        return lines[1] if len(lines) >= 2 else platform.node()
    except Exception:
        return platform.node()

def stampa_orario() -> None:
    """
    Stampa a video l'orario attuale nel formato YYYY-MM-DD HH:MM:SS.
    """
    print(f"\n🕒 Ora attuale: {datetime.now():%Y-%m-%d %H:%M:%S}")

def ask_choice(prompt: str,
               options: list[str],
               max_retries: int = 3) -> str:
    """
    Mostra un menu numerato con `options`, chiede all'utente di scegliere.
    Se la scelta non è valida riprova fino a max_retries volte, poi solleva InvalidChoiceError.
    """
    if not options:
        raise InvalidChoiceError(f"Nessuna opzione disponibile per '{prompt}'")

    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt}")

    attempts = 0
    while True:
        choice = input("Scelta: ").strip()
        attempts += 1

        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]

        print("❌ Input non valido. Riprova.")
        if attempts >= max_retries:
            raise InvalidChoiceError(
                f"Sono stati forniti troppi input non validi ({attempts}) per '{prompt}'"
            )
