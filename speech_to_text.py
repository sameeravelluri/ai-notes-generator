import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
model = whisper.load_model("base")
def listen_chunk():
    duration = 5  # seconds
    print("🎤 Recording chunk...")
    audio = sd.rec(int(duration * 16000), samplerate=16000, channels=1)
    sd.wait()
    wav.write("temp.wav", 16000, audio)
    result = model.transcribe("temp.wav")
    print("You said:", result["text"])
    return result["text"]