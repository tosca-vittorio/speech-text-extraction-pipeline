import whisper
import torch
import os
import subprocess
from datetime import datetime, timedelta
import time
import platform

def get_csproduct_name():
    if platform.system().lower() != "windows":
        return platform.node()
    try:
        result = subprocess.run(
            ["wmic", "csproduct", "get", "name"],
            capture_output=True, text=True, check=True
        )
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        if len(lines) >= 2:
            return lines[1]
    except Exception as e:
        print(f"⚠️ WMIC non ha risposto: {e}; uso fallback {platform.node()}")
        return platform.node()

HOSTNAME = get_csproduct_name()

def stampa_orario():
    print(f"\n🕒 Ora attuale: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def ask_choice(prompt, options):
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt}")
    while True:
        choice = input("Scelta: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("❌ Input non valido. Riprova.")

def list_audio_files():
    exts = (".mp3", ".mp4", ".wav", ".m4a")
    return [f for f in os.listdir() if f.lower().endswith(exts)]

def valida_timestamp(ts):
    try:
        parts = [int(p) for p in ts.strip().split(":")]
        if len(parts) == 2:
            m, s = parts
            return f"00:{m:02}:{s:02}"
        elif len(parts) == 3:
            h, m, s = parts
            return f"{h:02}:{m:02}:{s:02}"
    except ValueError:
        pass
    return None

def timestamp_in_secondi(ts):
    h, m, s = [int(p) for p in ts.strip().split(":")]
    return h * 3600 + m * 60 + s

def taglia_audio(input_file, inizio, fine, output_file="clip_temp.wav"):
    comando = [
        "ffmpeg", "-y",
        "-ss", inizio,
        "-to", fine,
        "-i", input_file,
        output_file
    ]
    try:
        subprocess.run(comando, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_file
    except subprocess.CalledProcessError:
        print("❌ Errore nel taglio dell'audio con ffmpeg.")
        exit(1)

def get_audio_duration(file_path):
    try:
        import wave
        import contextlib
        if file_path.endswith(".wav"):
            with contextlib.closing(wave.open(file_path, 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
                return str(timedelta(seconds=round(duration)))
        else:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            duration = float(result.stdout.decode().strip())
            return str(timedelta(seconds=round(duration)))
    except Exception:
        return "N/A"

def trascrivi(file_audio, modello, device, lang="it", tipo="completa"):
    print(f"\n🔄 Caricamento modello '{modello}' su {device}...")
    model = whisper.load_model(modello, device=device)

    # Determina il device effettivamente usato
    actual_device = next(model.parameters()).device

    print("\n🧠 Come vuoi gestire la trascrizione?")
    print("1. Standard – più leggibile, Whisper filtra automaticamente (consigliata per testo scorrevole)")
    print("2. Accurata – più fedele, nessun filtro, adatta a sottotitoli o NLP")

    while True:
        scelta_modalita = input("Scelta (1 o 2): ").strip()
        if scelta_modalita in ("1", "2"):
            break
        print("❌ Scelta non valida. Inserisci 1 o 2.")

    print(f"🎧 Inizio trascrizione di: {file_audio}")
    start_time = time.perf_counter()

    if scelta_modalita == "2":
        result = model.transcribe(
            file_audio,
            language=lang,
            temperature=0,
            condition_on_previous_text=False,
            compression_ratio_threshold=10.0,
            logprob_threshold=-1.0,
            no_speech_threshold=0.05
        )
    else:
        result = model.transcribe(file_audio, language=lang)

    end_time = time.perf_counter()

    duration_sec = end_time - start_time
    minutes, seconds = divmod(duration_sec, 60)
    durata_audio = get_audio_duration(file_audio)

    txt_filename = os.path.splitext(file_audio)[0] + "_trascritto.txt"
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(result["text"])

    print(f"\n✅ Trascrizione completata! Salvata in: {txt_filename}")
    print(f"🕐 Tempo impiegato: {int(minutes)} min {seconds:.2f} sec")
    print(f"📏 Durata audio trascritto: {durata_audio}")
    print(f"🧠 Device effettivamente usato: {actual_device}")

    parola_count = len(result["text"].split())
    modalita_descr = "Accurata" if scelta_modalita == "2" else "Standard"
    tempo_log = f"{int(minutes)}m {seconds:.2f}s"

    with open("whisper_benchmark.log", "a", encoding="utf-8") as log:
        log.write(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Host: {HOSTNAME} | "
            f"File: {file_audio} | Modello: {modello} | Device richiesto: {device} | Device effettivamente usato: {actual_device} | "
            f"Modalità: {modalita_descr} | Tipo: {tipo} | Durata audio: {durata_audio} | "
            f"Tempo elaborazione: {tempo_log} | Parole trascritte: {parola_count}\n"
        )



# --- MAIN ---
stampa_orario()

files = list_audio_files()
if not files:
    print("❌ Nessun file audio/video trovato nella cartella.")
    exit(1)

file_audio = ask_choice("🎵 Seleziona il file da trascrivere:", files)
modello = ask_choice("🤖 Scegli il modello Whisper:", ["tiny", "base", "small", "medium"])
device = ask_choice("💻 Vuoi usare CUDA (GPU) o CPU?", ["cuda", "cpu"])
if device == "cuda" and not torch.cuda.is_available():
    print("⚠️ CUDA non disponibile. Passaggio automatico a CPU.")
    device = "cpu"

modalita = ask_choice("📌 Vuoi trascrivere tutto o solo una parte dell’audio?", ["Tutto", "Solo una parte"])

if modalita == "Tutto":
    trascrivi(file_audio, modello, device, tipo="completa")
else:
    print("\nInserisci il minutaggio di INIZIO (es. 1:30 o 00:01:30)")
    while True:
        inizio = valida_timestamp(input("Da (minutaggio): "))
        if inizio: break
        print("❌ Formato non valido. Usa mm:ss o hh:mm:ss")

    print("Inserisci il minutaggio di FINE (es. 2:45 o 00:02:45)")
    while True:
        fine = valida_timestamp(input("A (minutaggio): "))
        if fine: break
        print("❌ Formato non valido. Usa mm:ss o hh:mm:ss")

    durata_attuale = get_audio_duration(file_audio)
    if durata_attuale == "N/A":
        print("❌ Impossibile determinare la durata del file.")
        exit(1)

    durata_sec = timestamp_in_secondi(durata_attuale)
    inizio_sec = timestamp_in_secondi(inizio)
    fine_sec = timestamp_in_secondi(fine)

    if inizio_sec >= fine_sec:
        print("❌ Il minutaggio di inizio deve essere inferiore a quello di fine.")
        exit(1)
    if fine_sec > durata_sec:
        print(f"❌ Il minutaggio di fine ({fine}) supera la durata del file ({durata_attuale}).")
        exit(1)

    clip = taglia_audio(file_audio, inizio, fine)
    trascrivi(clip, modello, device, tipo="parziale")

    scelta_clip = ask_choice("🗂️  Vuoi conservare la clip tagliata?", ["Sì", "No"])
    if scelta_clip == "No":
        os.remove(clip)
        print("🗑️ Clip temporanea eliminata.")
    else:
        print("✅ Clip salvata come:", clip)
