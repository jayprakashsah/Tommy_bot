import time
import board
import digitalio

print("Initializing Sensors...")

# --- SETUP SENSORS ---

# Touch Sensor 1 (Physical Pin 16 -> GPIO 23)
try:
    touch1 = digitalio.DigitalInOut(board.D23)
    touch1.direction = digitalio.Direction.INPUT
    touch1.pull = digitalio.Pull.DOWN # Default to Low (0)
    print("Touch 1 (GPIO 23) Ready.")
except Exception as e:
    print(f"Error Touch 1: {e}")

# Touch Sensor 2 (Physical Pin 15 -> GPIO 22)
try:
    touch2 = digitalio.DigitalInOut(board.D22)
    touch2.direction = digitalio.Direction.INPUT
    touch2.pull = digitalio.Pull.DOWN
    print("Touch 2 (GPIO 22) Ready.")
except Exception as e:
    print(f"Error Touch 2: {e}")

# Vibration Sensor (GPIO 26 -> Physical Pin 37)
# You didn't specify the pin for vibration in the recent list, 
# but your original code used D26. If you have it connected there:
try:
    vibe = digitalio.DigitalInOut(board.D26)
    vibe.direction = digitalio.Direction.INPUT
    vibe.pull = digitalio.Pull.DOWN
    print("Vibration (GPIO 26) Ready.")
except:
    print("Skipping Vibration (Not connected or Error)")

print("\n--- SENSOR TEST STARTED ---")
print("Press Ctrl+C to stop.")

try:
    while True:
        # Check Touch 1
        if touch1.value:
            print(">>> TOUCH 1 DETECTED!")
            time.sleep(0.2) # Debounce

        # Check Touch 2
        if touch2.value:
            print(">>> TOUCH 2 DETECTED!")
            time.sleep(0.2)

        # Check Vibration (Optional)
        try:
            if vibe.value:
                print(">>> VIBRATION HIT!")
                time.sleep(0.5)
        except: pass

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nTest Stopped.")
