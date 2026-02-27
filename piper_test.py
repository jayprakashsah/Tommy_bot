import numpy as np
import sounddevice as sd
from piper.voice import PiperVoice
from scipy import signal
import os

# --- CONFIG ---
MODEL_PATH = "en_US-lessac-medium.onnx"
DEVICE_INDEX = 0      # VoiceHAT
HW_SAMPLE_RATE = 48000
PIPER_SAMPLE_RATE = 22050 

if not os.path.exists(MODEL_PATH):
    print("Voice model file not found!")
else:
    voice = PiperVoice.load(MODEL_PATH)
    text = "Hello Jay. I am finally speaking. We have successfully bypassed the audio chunk error using the float array."

    with sd.OutputStream(samplerate=HW_SAMPLE_RATE, 
                        device=DEVICE_INDEX, 
                        channels=2, 
                        dtype='int16') as stream:
        
        print("Tommy is speaking (Float Array Mode)...")
        
        for item in voice.synthesize(text):
            # 1. Grab the float array directly from the debugged attribute
            # We convert it to int16 immediately for processing
            float_data = item.audio_float_array
            int_data = (float_data * 32767).astype(np.int16)
            
            # 2. Resample from 22050 to 48000
            num_samples = int(len(int_data) * HW_SAMPLE_RATE / PIPER_SAMPLE_RATE)
            resampled_data = signal.resample(int_data, num_samples).astype(np.int16)
            
            # 3. Stereo conversion for VoiceHAT
            stereo_data = np.stack((resampled_data, resampled_data), axis=-1)
            
            # 4. Write to VoiceHAT
            stream.write(stereo_data)
