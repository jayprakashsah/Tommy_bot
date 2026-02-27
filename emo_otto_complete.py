import time
import math
from gpiozero import AngularServo

# --- CONFIGURATION & PINS ---
# We use GPIO numbers (BCM), not physical pin numbers.

# Legs (The Movers)
PIN_L_HIP  = 4   # Physical Pin 7
PIN_L_FOOT = 24  # Physical Pin 18
PIN_R_HIP  = 6   # Physical Pin 31
PIN_R_FOOT = 13  # Physical Pin 33

# Hands (The Actors)
PIN_L_HAND = 26  # Physical Pin 37
PIN_R_HAND = 12  # Physical Pin 32

# --- SERVO SETUP ---
def make_servo(pin):
    # Standard MG90S Pulse Widths (0.5ms to 2.5ms)
    return AngularServo(pin, min_angle=0, max_angle=180, 
                        min_pulse_width=0.0005, max_pulse_width=0.0025)

# Initialize Motors
s_lh = make_servo(PIN_L_HIP)
s_lf = make_servo(PIN_L_FOOT)
s_rh = make_servo(PIN_R_HIP)
s_rf = make_servo(PIN_R_FOOT)
s_lhand = make_servo(PIN_L_HAND)
s_rhand = make_servo(PIN_R_HAND)

class EmoRobot:
    def __init__(self):
        # Default Resting Positions
        self.home = 90
        self.home_r_hand = 180 # Fixed as requested
        
        # Calibration Offsets (Adjust if robot stands crooked)
        # Positive (+) moves angle up, Negative (-) moves down
        self.offset = {
            'lh': 0, 'lf': 0, 
            'rh': 0, 'rf': 0,
            'lhand': 0, 'rhand': 0
        }
        
        self.soft_start()

    def set_angle(self, servo, name, angle):
        """Moves a servo safely with offset applied"""
        target = angle + self.offset.get(name, 0)
        # Safety Clamp (Keep between 0 and 180)
        target = max(0, min(180, target))
        servo.angle = target

    def soft_start(self):
        """Slowly moves everything to starting position"""
        print("Emo: Waking up...")
        self.set_angle(s_lh, 'lh', 90)
        self.set_angle(s_rh, 'rh', 90)
        self.set_angle(s_lf, 'lf', 90)
        self.set_angle(s_rf, 'rf', 90)
        
        # Hands
        self.set_angle(s_lhand, 'lhand', 90)  # Left hand normal
        self.set_angle(s_rhand, 'rhand', 180) # Right hand FIXED to 180
        
        time.sleep(1.0)
        print("Emo: Ready.")

    def _oscillate(self, A, O, T, phase_diff):
        """
        The Otto Oscillator Engine (Sine Wave Generator)
        A = Amplitude List [LH, RH, LF, RF, LHand, RHand]
        O = Offset (Center) List
        """
        steps = 50 
        start_time = time.time()
        
        for i in range(steps):
            # Calculate Angles using Sine Wave
            # Angle = Center + Amplitude * sin(2*PI*t + phase)
            
            # Legs & Feet
            ang_lh = O[0] + A[0] * math.sin(2 * math.pi * (i/steps) + phase_diff[0])
            ang_rh = O[1] + A[1] * math.sin(2 * math.pi * (i/steps) + phase_diff[1])
            ang_lf = O[2] + A[2] * math.sin(2 * math.pi * (i/steps) + phase_diff[2])
            ang_rf = O[3] + A[3] * math.sin(2 * math.pi * (i/steps) + phase_diff[3])
            
            # Hands
            ang_lhand = O[4] + A[4] * math.sin(2 * math.pi * (i/steps) + phase_diff[4])
            ang_rhand = O[5] + A[5] * math.sin(2 * math.pi * (i/steps) + phase_diff[5])

            # Move Motors
            self.set_angle(s_lh, 'lh', ang_lh)
            self.set_angle(s_rh, 'rh', ang_rh)
            self.set_angle(s_lf, 'lf', ang_lf)
            self.set_angle(s_rf, 'rf', ang_rf)
            self.set_angle(s_lhand, 'lhand', ang_lhand)
            self.set_angle(s_rhand, 'rhand', ang_rhand)
            
            time.sleep(T / steps)

    # --- MOVES ---

    def walk(self, steps=1, T=1.0, dir=1):
        print(f"Walking {'Forward' if dir==1 else 'Backward'}")
        
        # Amplitudes: [LH, RH, LF, RF, LHand, RHand]
        # Note: RHand Amplitude is 0 (Fixed)
        A = [25, 25, 20, 20, 30, 0] 
        O = [90, 90, 90, 90, 90, 180] # Right hand center is 180
        
        # I SWAPPED THE PHASES HERE TO FIX THE "BACKWARD" BUG
        if dir == 1:
            # New Forward Logic (Swapped from previous)
            phase = [0, 0, math.pi/2, math.pi/2, math.pi, 0]
        else:
            # New Backward Logic
            phase = [0, 0, -math.pi/2, -math.pi/2, math.pi, 0]
            
        for _ in range(steps):
            self._oscillate(A, O, T, phase)

    def turn(self, steps=1, T=1.0, dir=1):
        print(f"Turning {'Left' if dir==1 else 'Right'}")
        A = [20, 20, 20, 20, 0, 0]
        O = [90, 90, 90, 90, 90, 180]
        
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

    def moonwalk(self, steps=1, T=1.0):
        print("Moonwalking!")
        # Only feet tilt, legs stay straight
        A = [0, 0, 40, 40, 10, 0] 
        O = [90, 90, 90, 90, 90, 180]
        
        # Special phase for sliding look
        phase = [0, 0, -math.pi/2, math.pi/2, 0, 0]
        
        for _ in range(steps):
            self._oscillate(A, O, T, phase)

    def twist(self, steps=1, T=0.5):
        """Twist hips without lifting feet"""
        print("Twisting!")
        # We manually move servos here for sharp twist
        for _ in range(steps):
            self.set_angle(s_lh, 'lh', 70)
            self.set_angle(s_rh, 'rh', 70)
            self.set_angle(s_lhand, 'lhand', 110)
            time.sleep(T/2)
            
            self.set_angle(s_lh, 'lh', 110)
            self.set_angle(s_rh, 'rh', 110)
            self.set_angle(s_lhand, 'lhand', 70)
            time.sleep(T/2)
        self.soft_start()

    def up_down(self, steps=1, T=0.5):
        """Jump / Squat"""
        print("Up and Down")
        for _ in range(steps):
            # Squat (Feet Out)
            self.set_angle(s_lf, 'lf', 70)
            self.set_angle(s_rf, 'rf', 110)
            self.set_angle(s_lhand, 'lhand', 130) # Hands Up
            time.sleep(T)
            
            # Stand (Feet In)
            self.set_angle(s_lf, 'lf', 90)
            self.set_angle(s_rf, 'rf', 90)
            self.set_angle(s_lhand, 'lhand', 90)  # Hands Down
            time.sleep(T)

    def reset(self):
        self.soft_start()

# --- MAIN LOOP ---
if __name__ == "__main__":
    bot = EmoRobot()
    print("\n--- EMO COMPLETE CONTROLLER ---")
    print("w: Walk Forward | s: Walk Backward")
    print("a: Turn Left    | d: Turn Right")
    print("m: Moonwalk     | k: Twist")
    print("j: Jump/Up-Down | q: Quit")
    
    try:
        while True:
            cmd = input("Command: ").lower()
            if cmd == 'w': bot.walk(4, T=1.0, dir=1)
            elif cmd == 's': bot.walk(4, T=1.0, dir=-1)
            elif cmd == 'a': bot.turn(3, dir=1)
            elif cmd == 'd': bot.turn(3, dir=-1)
            elif cmd == 'm': bot.moonwalk(3)
            elif cmd == 'k': bot.twist(4)
            elif cmd == 'j': bot.up_down(3)
            elif cmd == 'q': 
                bot.reset()
                break
    except KeyboardInterrupt:
        bot.reset()
        print("\nStopped.")
