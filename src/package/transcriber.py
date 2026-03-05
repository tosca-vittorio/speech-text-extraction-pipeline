"""
Entry-point CLI per la trascrizione automatica con Whisper.
Esegui:  python -m package.transcriber [--overwrite yes|no]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import torch

from package.config import (
    INPUT_VIDEO_DIR,
    INPUT_AUDIO_DIR,
    TEST_AUDIO_DIR,
    TRANSCRIPTION_DIR,
    MODEL_OPTIONS,
    DEVICE_OPTIONS,
    MODALITA_OPTIONS,
    SCOPE_OPTIONS,
)
from package.cli_utils import get_csproduct_name, stampa_orario, ask_choice
from package.audio import (
    list_audio_files,
    valida_timestamp,
    timestamp_in_secondi,
    taglia_audio,
    get_audio_duration,
)
from package.core import transcribe
from package.logger import log_transcription
from package.errors import (
    TranscriberError,
    InvalidChoiceError,
    AudioProcessingError,
    ConfigError,
)
from package.lang_utils import select_language  # import per scelta lingua

# ───────────────────────── Arg-parsing ──────────────────────────────
def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument(
        "--overwrite",
        choices=["yes", "no"],
        help=(
            "yes = sovrascrive senza chiedere; "
            "no = non sovrascrive mai; "
            "se omesso, viene chiesto all’utente"
        ),
    )
    return p.parse_known_args()[0]          # ignoriamo altri argomenti

ARGS     = _parse_args()
HOSTNAME = get_csproduct_name()
os.makedirs(TRANSCRIPTION_DIR, exist_ok=True)

# ──────────────────────── helper overwrite ─────────────────────────
def _should_overwrite(path: str) -> bool:
    """Stabilisce se il file può essere sovrascritto."""
    if not Path(path).exists():
        return True
    if ARGS.overwrite == "yes":
        return True
    if ARGS.overwrite == "no":
        return False
    # prompt
    return ask_choice(
        f"⚠️  Il file '{Path(path).name}' esiste già. Sovrascriverlo?",
        ["Sì", "No"],
    ) == "Sì"

# ─────────────────────────── main CLI ──────────────────────────────
def main() -> None:
    # Fast-path per help: evita prompt interattivi quando si invoca -h/--help
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print(
            "speech-text-extraction-pipeline (transcriber)\n\n"
            "Uso:\n"
            "  transcriber [--overwrite yes|no]\n\n"
            "Opzioni:\n"
            "  --overwrite {yes,no}   yes=sovrascrive senza chiedere; no=mai; se omesso chiede\n"
            "  -h, --help            mostra questo help e termina\n"
        )
        return

    stampa_orario()

    # Menu iniziale
    if ask_choice("🔹 Cosa vuoi fare?", ["Trascrivi", "Esci"]) == "Esci":
        print("Arrivederci!")
        sys.exit(0)

    # 1) elenco file
    files = (
        [f"[🎧] {f}" for f in list_audio_files(INPUT_AUDIO_DIR)]
      + [f"[🎬] {f}" for f in list_audio_files(INPUT_VIDEO_DIR)]
      + [f"[🧪] {f}" for f in list_audio_files(TEST_AUDIO_DIR)]
)
    if not files:
        raise ConfigError("Nessun file in input/audio, input/video o tests/resources.")

    scelta = ask_choice("🎵 Seleziona il file da trascrivere:", files)
    if scelta.startswith("[🎧]"):
        file_audio = os.path.join(INPUT_AUDIO_DIR, scelta[4:].strip())
    elif scelta.startswith("[🎬]"):
        file_audio = os.path.join(INPUT_VIDEO_DIR, scelta[4:].strip())
    elif scelta.startswith("[🧪]"):
        file_audio = os.path.join(TEST_AUDIO_DIR, scelta[4:].strip())
    else:
        raise InvalidChoiceError("Scelta file non valida.")

    # 2) modello e device
    modello = ask_choice("🤖 Scegli il modello Whisper:", MODEL_OPTIONS)
    device  = ask_choice("💻 Vuoi usare CUDA (GPU) o CPU?", DEVICE_OPTIONS)
    if device == "cuda" and not torch.cuda.is_available():
        print("⚠️  CUDA non disponibile: uso CPU.")
        device = "cpu"

    # 3) scelta lingua
    lang = select_language()

    # 4) modalità
    modalita_acc = ask_choice("🧠 Modalità trascrizione:", MODALITA_OPTIONS).strip()\
        .startswith("Accurata")

    # 5) ambito
    scope = ask_choice("📌 Trascrivi tutto o solo una parte?", SCOPE_OPTIONS)

    clip_path: str | None = None     # per logging finale

    # ───────────── trascrizione COMPLETA ─────────────────────
    if scope == "Tutto":
        result = transcribe(
            audio_path   = file_audio,
            modello      = modello,
            device       = device,
            lang         = lang,
            modalita_acc = modalita_acc,
            tipo         = "completa",
        )

    # ───────────── trascrizione PARZIALE ─────────────────────
    else:
        # timestamp inizio/fine con validazione
        while True:
            inizio = valida_timestamp(input("Da (mm:ss o hh:mm:ss): ").strip())
            if inizio:
                break
            print("❌ Formato non valido. Riprova.")
        while True:
            fine = valida_timestamp(input("A (mm:ss o hh:mm:ss): ").strip())
            if fine:
                break
            print("❌ Formato non valido. Riprova.")

        durata_tot = get_audio_duration(file_audio) or "99:59:59"
        if timestamp_in_secondi(inizio) >= timestamp_in_secondi(fine):
            raise InvalidChoiceError("Il timestamp di inizio deve precedere quello di fine.")
        if timestamp_in_secondi(fine) > timestamp_in_secondi(durata_tot):
            raise InvalidChoiceError(f"Fine ({fine}) supera durata file ({durata_tot}).")

        safe_inizio = inizio.replace(":", "")
        safe_fine = fine.replace(":", "")
        clip_name = f"{Path(file_audio).stem}_{safe_inizio}-{safe_fine}_clip.wav"
        clip_path = str(Path(TRANSCRIPTION_DIR) / clip_name)

        # eventuale sovrascrittura clip
        if not _should_overwrite(clip_path):
            print("Operazione annullata (clip già esistente).")
            sys.exit(0)

        # estrai segmento
        try:
            taglia_audio(file_audio, inizio, fine, output_file=clip_path)
        except Exception as exc:
            raise AudioProcessingError(f"Errore taglio audio: {exc}")

        # trascrivi la clip
        result = transcribe(
            audio_path   = clip_path,
            modello      = modello,
            device       = device,
            lang         = lang,
            modalita_acc = modalita_acc,
            tipo         = "parziale",
            inizio       = inizio,
            fine         = fine,
        )

        # rimozione clip se richiesto
        if ask_choice("🗂️  Conservi la clip tagliata?", ["Sì", "No"]) == "No":
            try:
                os.remove(clip_path)
                clip_path = None
            except OSError as exc:
                print(f"⚠️  Impossibile eliminare clip: {exc}")

    # ───────────── salvataggio testo ─────────────────────────
    txt_path = Path(TRANSCRIPTION_DIR) / Path(result["txt_filename"]).name

    # Se esiste già lo stesso file di output, gestisce overwrite secondo policy
    if txt_path.exists():
        if ARGS.overwrite == "yes":
            pass
        elif ARGS.overwrite == "no":
            print("Salvataggio annullato (file .txt già esistente).")
            sys.exit(0)
        else:
            response = ask_choice(
                f"⚠️  Il file '{txt_path.name}' esiste già. Sovrascriverlo?",
                ["Sì", "No"],
            )
            if response != "Sì":
                print("Salvataggio annullato (file .txt già esistente).")
                sys.exit(0)

    try:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
    except Exception as exc:
        raise AudioProcessingError(f"Errore salvataggio trascrizione: {exc}")

    # ───────────── riepilogo + log ───────────────────────────
    m, s = divmod(result["duration_proc"], 60)
    print(
        "\n✅ Trascrizione completata!\n"
        f"   📄 {txt_path}\n"
        f"🕐 Tempo: {int(m)}m {s:.2f}s | "
        f"📏 Durata audio: {result['durata_audio']} | "
        f"🧠 Device: {result['device']} | "
        f"🌐 Lingua: {lang}"
    )

    log_transcription(
        hostname     = HOSTNAME,
        file_audio   = clip_path or file_audio,
        modello      = modello,
        device_req   = device,
        device_act   = result["device"],
        modalita     = "Accurata" if modalita_acc else "Standard",
        tipo         = scope.lower(),
        durata_audio = result["durata_audio"],
        proc_time    = f"{int(m)}m {s:.2f}s",
        parola_count = result["parola_count"],
        lingua       = lang,  # nuovo parametro lingua
    )

    sys.exit(0)

# ────────────────────────── avvio standalone ───────────────────────
if __name__ == "__main__":
    try:
        main()
    except (InvalidChoiceError, ConfigError,
            AudioProcessingError, TranscriberError) as e:
        print(f"❌ {e.__class__.__name__}: {e}")
    except Exception as e:
        print(f"❌ Errore imprevisto: {e}")
