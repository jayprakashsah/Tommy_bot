import os
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import sys
import json
import numpy as np

# --- VOICEHAT STICKY SETTINGS ---
DEVICE_INDEX = 0      
SAMPLE_RATE = 48000   # Hardware rate
CHANNELS = 2          # MUST BE 2 for VoiceHAT
DTYPE = 'int32'       # Hardware format from your arecord test

model = Model("model")
rec = KaldiRecognizer(model, SAMPLE_RATE)
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(f"Status: {status}", file=sys.stderr)
    
    # indata is currently (8000, 2) in int32
    # 1. Take only the Left channel [:, 0]
    # 2. Convert to int16 for Vosk
    mono_16 = (indata[:, 0] >> 16).astype(np.int16)
    q.put(mono_16.tobytes())

try:
    with sd.InputStream(samplerate=SAMPLE_RATE, 
                        device=DEVICE_INDEX, 
                        channels=CHANNELS, 
                        dtype=DTYPE, 
                        callback=callback):
        
        print(f"\n--- VOICEHAT I2S FIXED ---")
        print("Say 'Tommy' clearly...")
        
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    print(f"\nFinal Result: {text}")
                    if "tommy" in text:
                        print(">>> TOMMY DETECTED! <<<")
            else:
                partial = json.loads(rec.PartialResult())
                p_text = partial.get("partial", "")
                if p_text:
                    print(f"Hearing: {p_text}          ", end='\r')

except Exception as e:
    print(f"I2S Driver Error: {e}")
