import whisper
import torch
import os
import subprocess
from datetime import datetime

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
    # accetta formato hh:mm:ss oppure mm:ss
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

def taglia_audio(input_file, inizio, fine, output_file="clip_temp.wav"):
    comando = [
        "ffmpeg", "-y",  # -y sovrascrive senza chiedere
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

def trascrivi(file_audio, modello, device, lang="italian"):
    print(f"\n🔄 Caricamento modello '{modello}' su {device}...")
    model = whisper.load_model(modello, device=device)

    print(f"🎧 Trascrizione di: {file_audio}")
    result = model.transcribe(file_audio, language=lang)

    txt_filename = os.path.splitext(file_audio)[0] + "_trascritto.txt"
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(result["text"])

    print(f"\n✅ Trascrizione completata! Salvata in: {txt_filename}")

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
    trascrivi(file_audio, modello, device)
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

    clip = taglia_audio(file_audio, inizio, fine)
    trascrivi(clip, modello, device)
    os.remove(clip)  # elimina clip temporaneo
