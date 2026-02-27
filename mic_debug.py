import speech_recognition as sr

print("--- MICROPHONE TEST ---")
r = sr.Recognizer()
r.energy_threshold = 300  # Force sensitivity

try:
    # We use Index 0 as verified before
    mic = sr.Microphone(device_index=0)
    
    with mic as source:
        print("Adjusting for noise... (Please be quiet)")
        r.adjust_for_ambient_noise(source, duration=1)
        print("Current Energy Threshold:", r.energy_threshold)
        
        print("\nSPEAK NOW! (Say 'Hello')")
        audio = r.listen(source, timeout=5)
        print("Got audio! Recognizing...")
        
        text = r.recognize_google(audio)
        print(f"SUCCESS! I heard: '{text}'")

except sr.WaitTimeoutError:
    print("ERROR: Timeout. The mic is on, but heard nothing (Volume too low?)")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
