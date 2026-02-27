import pvporcupine
from pvrecorder import PvRecorder

# You can get a free Access Key from Picovoice Console
access_key = "YOUR_ACCESS_KEY" 

porcupine = pvporcupine.create(access_key=access_key, keywords=['picovoice']) # Testing with 'picovoice' first
recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

try:
    recorder.start()
    print("Listening for 'Picovoice'...")
    while True:
        pcm = recorder.read()
        keyword_index = porcupine.process(pcm)
        if keyword_index >= 0:
            print("Detected!")
finally:
    recorder.delete()
    porcupine.delete()
