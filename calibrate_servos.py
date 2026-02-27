from gpiozero import AngularServo
from time import sleep
from signal import pause

# --- PIN CONFIGURATION ---
# 90 Degree Group
pin_servo1 = 4   # Physical Pin 7
pin_servo2 = 24  # Physical Pin 18
pin_servo3 = 6   # Physical Pin 31
pin_servo4 = 13  # Physical Pin 33 (Moved from 36 to fix error)

# 0 Degree Group
pin_servo5_6 = 26 # Physical Pin 37

# Organize them into lists for easy control
pins_at_90 = [pin_servo1, pin_servo2, pin_servo3, pin_servo4]
pin_at_0   = pin_servo5_6

servos = []

print("Initializing Servos...")

try:
    # 1. Setup the 90-degree servos
    for pin in pins_at_90:
        s = AngularServo(pin, min_angle=0, max_angle=180, 
                         min_pulse_width=0.0005, max_pulse_width=0.0025)
        s.angle = 90  # Set to 90 immediately
        servos.append(s)

    # 2. Setup the 0-degree servo (Pin 37)
    s_zero = AngularServo(pin_at_0, min_angle=0, max_angle=180, 
                          min_pulse_width=0.0005, max_pulse_width=0.0025)
    s_zero.angle = 0  # Set to 0 immediately
    servos.append(s_zero)

    print("--------------------------------")
    print("STATUS:")
    print(f"-> Servos on pins {pins_at_90} are LOCKED at 90°")
    print(f"-> Servo on pin {pin_at_0} is LOCKED at 0°")
    print("--------------------------------")
    print("Motors are powered. Press Ctrl+C to stop.")

    # Keep the script running to maintain holding torque
    pause()

except KeyboardInterrupt:
    print("\nStopping...")
    # Detach all servos to stop the signal
    for s in servos:
        s.detach()
    print("Motors released.")
