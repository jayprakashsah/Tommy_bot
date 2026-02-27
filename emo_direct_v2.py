import time
import math
from gpiozero import AngularServo

#On Pi 5, gpiozero automatically uses the best driver (lgpio)
# We don't need to define a factory manually anymore.

# --- CONFIGURATION ---

# Helper to create a servo safely with specific Pulse Widths for MG90S
def make_servo(pin):
    # min_pulse_width=0.0005 (0.5ms) and max=0.0025 (2.5ms) are standard for SG90/MG90S
    return AngularServo(pin, min_angle=0, max_angle=180, 
                        min_pulse_width=0.0005, max_pulse_width=0.0025)

# --- PIN MAPPING (User Config) ---
# Note: We use GPIO numbers here (e.g. 4), NOT physical pin numbers (e.g. 7)
servo_l_hip = make_servo(4)   # Pin 7 (GPIO 4)
servo_l_foot = make_servo(24) # Pin 18 (GPIO 24)
servo_r_hip = make_servo(6)   # Pin 31 (GPIO 6)
servo_r_foot = make_servo(13) # Pin 33 (GPIO 13)

# Hands
servo_l_hand = make_servo(26) # Pin 37 (GPIO 26)
servo_r_hand = make_servo(12) # Pin 32 (GPIO 12)

class EmoRobot:
    def __init__(self):
        self.home = 90
        
        # Calibration Offsets (Adjust if legs are crooked)
        # Positive adds angle, Negative subtracts
        self.offset = {
            'lh': 0, 'lf': 0, 
            'rh': 0, 'rf': 0,
            'lhand': 0, 'rhand': 0
        }
        
        self.soft_start()

    def set_angle(self, servo, name, angle):
        """Moves a servo safely with offset applied"""
        target = angle + self.offset.get(name, 0)
        target = max(0, min(180, target)) # Safety Clamp
        servo.angle = target

    def soft_start(self):
        """Slowly moves everything to Home (90) to prevent falling"""
        print("Emo: Waking up...")
        
        # Move everything to 90
        self.set_angle(servo_l_hip, 'lh', 90)
        self.set_angle(servo_r_hip, 'rh', 90)
        self.set_angle(servo_l_foot, 'lf', 90)
        self.set_angle(servo_r_foot, 'rf', 90)
        self.set_angle(servo_l_hand, 'lhand', 90) 
        self.set_angle(servo_r_hand, 'rhand', 90)
        time.sleep(1.0)
        print("Emo: Ready.")

    def _oscillate(self, A, O, T, phase_diff):
        """
        The Sine Wave Generator. 
        A = Amplitude [L_Hip, R_Hip, L_Foot, R_Foot, L_Hand, R_Hand]
        """
        steps = 50 
        start_time = time.time()
        
        for i in range(steps):
            # Calculate current position in time loop
            elapsed = time.time() - start_time
            
            # Calculate Angles
            # Legs & Feet
            ang_lh = O[0] + A[0] * math.sin(2 * math.pi * (i/steps) + phase_diff[0])
            ang_rh = O[1] + A[1] * math.sin(2 * math.pi * (i/steps) + phase_diff[1])
            ang_lf = O[2] + A[2] * math.sin(2 * math.pi * (i/steps) + phase_diff[2])
            ang_rf = O[3] + A[3] * math.sin(2 * math.pi * (i/steps) + phase_diff[3])
            
            # Hands (Swing opposite to legs for realism)
            ang_lhand = O[4] + A[4] * math.sin(2 * math.pi * (i/steps) + phase_diff[4])
            ang_rhand = O[5] + A[5] * math.sin(2 * math.pi * (i/steps) + phase_diff[5])

            # Send Commands
            self.set_angle(servo_l_hip, 'lh', ang_lh)
            self.set_angle(servo_r_hip, 'rh', ang_rh)
            self.set_angle(servo_l_foot, 'lf', ang_lf)
            self.set_angle(servo_r_foot, 'rf', ang_rf)
            self.set_angle(servo_l_hand, 'lhand', ang_lhand)
            self.set_angle(servo_r_hand, 'rhand', ang_rhand)
            
            time.sleep(T / steps)

    def walk(self, steps=1, T=1.0, dir=1):
        print(f"Walking {'Forward' if dir==1 else 'Backward'}")
        
        # --- GAIT CONFIGURATION ---
        # Amplitudes: [LH, RH, LF, RF, LHand, RHand]
        A = [25, 25, 20, 20, 30, 30]
        O = [90, 90, 90, 90, 90, 90]
        
        if dir == 1:
            # Forward Logic
            phase = [0, 0, -math.pi/2, -math.pi/2, math.pi, math.pi]
        else:
            phase = [0, 0, math.pi/2, math.pi/2, math.pi, math.pi]
            
        for _ in range(steps):
            self._oscillate(A, O, T, phase)

    def turn(self, steps=1, T=1.0, dir=1):
        print(f"Turning {'Left' if dir==1 else 'Right'}")
        A = [20, 20, 20, 20, 0, 0]
        O = [90, 90, 90, 90, 90, 90]
        
        if dir == 1: # Left
            phase = [0, 0, -math.pi/2, -math.pi/2, 0, 0]
            A[0] = 10 
            A[1] = 25
        else: # Right
            phase = [0, 0, -math.pi/2, -math.pi/2, 0, 0]
            A[0] = 25
            A[1] = 10
            
        for _ in range(steps):
            self._oscillate(A, O, T, phase)

    def hi(self):
        """Emo Wave Gesture"""
        print("Emo: Hi!")
        self.set_angle(servo_r_hand, 'rhand', 30) # Raise hand
        time.sleep(0.5)
        for _ in range(3):
            self.set_angle(servo_r_hand, 'rhand', 30)
            time.sleep(0.2)
            self.set_angle(servo_r_hand, 'rhand', 60)
            time.sleep(0.2)
        self.set_angle(servo_r_hand, 'rhand', 90) # Return

    def reset(self):
        print("Resting...")
        self.soft_start()

# --- MAIN LOOP ---
if __name__ == "__main__":
    bot = EmoRobot()
    print("\n--- EMO DIRECT GPIO MODE ---")
    print("w: Walk | s: Back | a/d: Turn | h: Hi/Wave | q: Quit")
    
    try:
        while True:
            cmd = input("Cmd: ").lower()
            if cmd == 'w': bot.walk(4, T=1.0, dir=1)
            elif cmd == 's': bot.walk(4, T=1.0, dir=-1)
            elif cmd == 'a': bot.turn(3, dir=1)
            elif cmd == 'd': bot.turn(3, dir=-1)
            elif cmd == 'h': bot.hi()
            elif cmd == 'q': 
                bot.reset()
                break
    except KeyboardInterrupt:
        bot.reset()
        print("\nStopped.")
