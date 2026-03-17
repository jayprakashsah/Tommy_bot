import time
from gpiozero import AngularServo

# --- CONFIGURATION ---
# Left Hand = GPIO 26 (Physical Pin 37)
# Right Hand = GPIO 12 (Physical Pin 32)
PIN_L_HAND = 26
PIN_R_HAND = 12

# --- SETUP ---
def make_servo(pin):
    # Using the same pulse widths as before
    return AngularServo(pin, min_angle=0, max_angle=180, 
                        min_pulse_width=0.0005, max_pulse_width=0.0025)

print("Initializing Hands...")
left_hand = make_servo(PIN_L_HAND)
right_hand = make_servo(PIN_R_HAND)

# --- HELPER FUNCTION ---
def set_hand(hand_name, angle):
    # Safety Clamp: Prevent angles less than 0 or more than 180
    safe_angle = max(0, min(180, int(angle)))
    
    if hand_name == 'l':
        print(f"Moving LEFT Hand to {safe_angle}°")
        left_hand.angle = safe_angle
    elif hand_name == 'r':
        print(f"Moving RIGHT Hand to {safe_angle}°")
        right_hand.angle = safe_angle

# --- MAIN LOOP ---
if __name__ == "__main__":
    print("\n--- MANUAL HAND TESTER ---")
    print("Type 'l <angle>' for Left Hand (e.g., 'l 0' or 'l 30')")
    print("Type 'r <angle>' for Right Hand (e.g., 'r 180' or 'r 150')")
    print("Type 'q' to Quit")
    
    # 1. Start at safe positions
    print("Setting to Safe Defaults (L=0, R=180)...")
    left_hand.angle = 0
    right_hand.angle = 180
    time.sleep(1)

    try:
        while True:
            cmd = input("\nEnter Command: ").strip().lower()
            
            if cmd == 'q':
                break
            
            try:
                # Split command: "l 45" -> part[0]='l', part[1]='45'
                parts = cmd.split()
                side = parts[0]
                val = int(parts[1])
                
                if side in ['l', 'r']:
                    set_hand(side, val)
                else:
                    print("Error: Use 'l' or 'r'")
                    
            except (IndexError, ValueError):
                print("Invalid format. Try: 'l 30' or 'r 150'")

    except KeyboardInterrupt:
        print("\nExiting.")
