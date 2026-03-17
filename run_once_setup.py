# run_once_setup.py
from gtts import gTTS
import os

print("Generating static audio files...")

# 1. The Wake Response (The most important one for speed)
tts = gTTS(text="Ji?", lang='en', tld='co.in')
tts.save("sfx_wake.mp3")

# 2. Ready sound
tts = gTTS(text="System Ready.", lang='en', tld='co.in')
tts.save("sfx_ready.mp3")

# 3. Processing/Thinking sound (Optional: you can download a beep sound instead)
tts = gTTS(text="Hmm...", lang='en', tld='co.in')
tts.save("sfx_think.mp3")

print("Done! Files saved.")
