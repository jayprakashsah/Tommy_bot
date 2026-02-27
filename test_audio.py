import os
import time

print("Testing Audio Output...")

# Create a dummy sound file (just a beep) using system tools
# This command generates a 1kHz sine wave for 2 seconds
os.system("speaker-test -t sine -f 1000 -c 2 -l 1 &")

print("You should hear a tone now.")
print("If you hear it, the wiring is correct.")
