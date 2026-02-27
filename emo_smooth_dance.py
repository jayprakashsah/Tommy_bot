import time
import math
from gpiozero import AngularServo

# --- CONFIGURATION & PINS ---
PIN_L_HIP  = 4   # Pin 7
PIN_L_FOOT = 24  # Pin 18
PIN_R_HIP  = 6   # Pin 31
PIN_R_FOOT = 13  # Pin 33
PIN_L_HAND = 26  # Pin 37
PIN_R_HAND = 12  # Pin 32

# --- SERVO SETUP ---
def make_servo(pin):
    # High Precision for smoothness
    return AngularServo(pin, min_angle=0, max_angle=180, 
                        min_pulse_width=0.0005, max_pulse_width=0.0025)

s_lh = make_servo(PIN_L_HIP)
s_lf = make_servo(PIN_L_FOOT)
s_rh = make_servo(PIN_R_HIP)
s_rf = make_servo(PIN_R_FOOT)
s_lhand = make_servo(PIN_L_HAND)
s_rhand = make_servo(PIN_R_HAND)

class EmoRobot:
    def __init__(self):
        # Resting Positions
        self.home = 90
        self.home_l_hand = 0    # Left rests at 0
        self.home_r_hand = 180  # Right rests at 180
        
        self.offset = {
            'lh': 0, 'lf': 0, 
            'rh': 0, 'rf': 0,
            'lhand': 0, 'rhand': 0
        }
        
        self.soft_start()

    def set_angle(self, servo, name, angle):
        target = angle + self.offset.get(name, 0)
        target = max(0, min(180, target))
        servo.angle = target

    def soft_start(self):
        print("Emo: Waking up...")
        self.set_angle(s_lh, 'lh', 90)
        self.set_angle(s_rh, 'rh', 90)
        self.set_angle(s_lf, 'lf', 90)
        self.set_angle(s_rf, 'rf', 90)
        # Hands to Rest
        self.set_angle(s_lhand, 'lhand', self.home_l_hand) 
        self.set_angle(s_rhand, 'rhand', self.home_r_hand)
        time.sleep(1.0)

    def _oscillate(self, A, O, T, phase_diff):
        steps = 100 # Smoothness Factor
        start_time = time.time()
        
        for i in range(steps):
            # Sine Wave Calculation
            # Legs & Feet
            ang_lh = O[0] + A[0] * math.sin(2 * math.pi * (i/steps) + phase_diff[0])
            ang_rh = O[1] + A[1] * math.sin(2 * math.pi * (i/steps) + phase_diff[1])
            ang_lf = O[2] + A[2] * math.sin(2 * math.pi * (i/steps) + phase_diff[2])
            ang_rf = O[3] + A[3] * math.sin(2 * math.pi * (i/steps) + phase_diff[3])
            
            # --- OPPOSITE HAND LOGIC ---
            # To make hands alternate, we use a Phase Shift of PI/2
            # abs(sin(x)) peaks at PI/2
            # abs(sin(x + PI/2)) peaks at 0 (or PI)
            
            raw_sin_l = math.sin(2 * math.pi * (i/steps) + phase_diff[4])
            raw_sin_r = math.sin(2 * math.pi * (i/steps) + phase_diff[5])
            
            # Left Hand (0 -> 30)
            ang_lhand = O[4] + abs(A[4] * raw_sin_l) 
            
            # Right Hand (180 -> 150)
            ang_rhand = O[5] - abs(A[5] * raw_sin_r)

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
        
        # Amplitudes
        A = [25, 25, 20, 20, 30, 30] 
        O = [90, 90, 90, 90, 0, 180]
        
        # --- PHASE LOGIC ---
        # Legs: Standard Walk
        # Hands: Offset by PI/2 to create Alternating "Marching" swing
        
        if dir == 1: # Forward
            phase = [0, 0, math.pi/2, math.pi/2, 0, math.pi/2]
        else: # Backward
            phase = [0, 0, -math.pi/2, -math.pi/2, 0, math.pi/2]
            
        for _ in range(steps):
            self._oscillate(A, O, T, phase)

    def happy_dance(self, steps=3):
        print(">> Happy Dance!")
        # Wiggle dance with alternating hands
        A = [0, 0, 30, 30, 40, 40] 
        O = [90, 90, 90, 90, 0, 180]
        # Hands strictly opposite
        phase = [0, 0, 0, math.pi, 0, math.pi/2] 
        
        for _ in range(steps*3):
            # Faster T=0.4 for energy
            self._oscillate(A, O, 0.4, phase)
        self.soft_start()

    def twist(self, steps=3):
        print(">> Twist")
        for _ in range(steps):
            # Smooth Twist: Manually move to positions
            # Left Twist
            self.set_angle(s_lh, 'lh', 60)
            self.set_angle(s_rh, 'rh', 60)
            self.set_angle(s_lhand, 'lhand', 40)  # Left Hand Fwd
            self.set_angle(s_rhand, 'rhand', 180) # Right Hand Back
            time.sleep(0.3)
            
            # Right Twist
            self.set_angle(s_lh, 'lh', 120)
            self.set_angle(s_rh, 'rh', 120)
            self.set_angle(s_lhand, 'lhand', 0)   # Left Hand Back
            self.set_angle(s_rhand, 'rhand', 140) # Right Hand Fwd
            time.sleep(0.3)
        self.soft_start()

    def hi(self):
        """Standard Wave"""
        print(">> Hi!")
        self.set_angle(s_rhand, 'rhand', 120) # Lift
        time.sleep(0.5)
        for _ in range(3):
            self.set_angle(s_rhand, 'rhand', 120)
            time.sleep(0.2)
            self.set_angle(s_rhand, 'rhand', 160)
            time.sleep(0.2)
        self.soft_start()

# --- MAIN ---
if __name__ == "__main__":
    bot = EmoRobot()
    print("\n--- EMO: SMOOTH & OPPOSITE HANDS ---")
    print("w/s: Walk Fwd/Back | h: Happy Dance")
    print("k: Twist           | i: Wave (Hi)")
    print("q: Quit")
    
    try:
        while True:
            cmd = input("Cmd: ").lower()
            if cmd == 'w': bot.walk(4, T=1.0, dir=1)
            elif cmd == 's': bot.walk(4, T=1.0, dir=-1)
            elif cmd == 'h': bot.happy_dance()
            elif cmd == 'k': bot.twist()
            elif cmd == 'i': bot.hi()
            elif cmd == 'q': 
                bot.soft_start()
                break
    except KeyboardInterrupt:
        bot.soft_start()
