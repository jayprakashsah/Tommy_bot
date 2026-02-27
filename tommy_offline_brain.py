import os
import json
import queue
import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from piper.voice import PiperVoice
from scipy import signal
import ollama

class TommyOfflineBrain:
    def __init__(self, device_index=0):
        # 1. Setup Local Ears (Vosk)
        self.stt_model = Model("model")
        self.rec = KaldiRecognizer(self.stt_model, 48000)
        self.audio_q = queue.Queue()
        self.device_index = device_index
        
        # 2. Setup Local Voice (Piper)
        self.voice = PiperVoice.load("en_US-lessac-medium.onnx")
        
        # 3. Local LLM Settings
        self.llm_model = 'llama3.2:1b'

    def listen(self):
        """Listens for a command and returns the text."""
        with sd.InputStream(samplerate=48000, device=self.device_index, 
                            channels=2, dtype='int32') as stream:
            print("Listening...")
            while True:
                data, overflowed = stream.read(4000)
                # Convert 32-bit stereo to 16-bit mono for Vosk
                mono_16 = (data[:, 0] >> 16).astype(np.int16)
                if self.rec.AcceptWaveform(mono_16.tobytes()):
                    result = json.loads(self.rec.Result())
                    return result.get("text", "")

    def think(self, user_input):
        """Sends text to Ollama and returns the AI response."""
        prompt = f"You are Tommy, a friendly robot. Respond to: {user_input}"
        response = ollama.chat(model=self.llm_model, messages=[
            {'role': 'user', 'content': prompt},
        ])
        return response['message']['content']

    def speak(self, text):
        """Plays text through the VoiceHAT using Piper."""
        with sd.OutputStream(samplerate=48000, device=self.device_index, 
                            channels=2, dtype='int16') as stream:
            for item in self.voice.synthesize(text):
                # Using the float array method we discovered
                float_data = item.audio_float_array
                int_data = (float_data * 32767).astype(np.int16)
                # Resample 22k -> 48k
                num_samples = int(len(int_data) * 48000 / 22050)
                resampled = signal.resample(int_data, num_samples).astype(np.int16)
                stereo = np.stack((resampled, resampled), axis=-1)
                stream.write(stereo)
