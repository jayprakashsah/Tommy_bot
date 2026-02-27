import time
import math
import random
from gpiozero import AngularServo

# ==========================================
#           CONFIGURATION & PINS
# ==========================================
PIN_L_HIP  = 4   # Pin 7
PIN_L_FOOT = 24  # Pin 18
PIN_R_HIP  = 6   # Pin 31
PIN_R_FOOT = 13  # Pin 33
PIN_L_HAND = 26  # Pin 37
PIN_R_HAND = 12  # Pin 32

# --- DRIFT CORRECTION (Fixes Rotating while Walking) ---
# If robot curves LEFT -> Set this to -2 or -3
# If robot curves RIGHT -> Set this to +2 or +3
# 0 means perfect balance.
WALK_TRIM = 0 

# --- SERVO SETUP ---
def make_servo(pin):
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
        self.home = 90
        self.home_l_hand = 0    # Locked Down
        self.home_r_hand = 180  # Locked Down
        
        # Mechanical Calibration (Use this if legs are crooked)
        self.offset = {'lh':0, 'lf':0, 'rh':0, 'rf':0, 'lhand':0, 'rhand':0}
        self.soft_start()

    def set_angle(self, servo, name, angle):
        target = angle + self.offset.get(name, 0)
        target = max(0, min(180, target))
        servo.angle = target

    def soft_start(self):
        """Standard Reset"""
        print(">> Stabilizing...")
        self.set_angle(s_lh, 'lh', 90)
        self.set_angle(s_rh, 'rh', 90)
        self.set_angle(s_lf, 'lf', 90)
        self.set_angle(s_rf, 'rf', 90)
        self.set_angle(s_lhand, 'lhand', self.home_l_hand) 
        self.set_angle(s_rhand, 'rhand', self.home_r_hand)
        time.sleep(0.5)

    def _oscillate(self, A, O, T, phase_diff):
        steps = 100 
        for i in range(steps):
            # Legs & Feet
            ang_lh = O[0] + A[0] * math.sin(2 * math.pi * (i/steps) + phase_diff[0])
            ang_rh = O[1] + A[1] * math.sin(2 * math.pi * (i/steps) + phase_diff[1])
            ang_lf = O[2] + A[2] * math.sin(2 * math.pi * (i/steps) + phase_diff[2])
            ang_rf = O[3] + A[3] * math.sin(2 * math.pi * (i/steps) + phase_diff[3])
            
            # Hands
            raw_sin_l = math.sin(2 * math.pi * (i/steps) + phase_diff[4])
            raw_sin_r = math.sin(2 * math.pi * (i/steps) + phase_diff[5])
            ang_lhand = O[4] + abs(A[4] * raw_sin_l) 
            ang_rhand = O[5] - abs(A[5] * raw_sin_r)

            self.set_angle(s_lh, 'lh', ang_lh)
            self.set_angle(s_rh, 'rh', ang_rh)
            self.set_angle(s_lf, 'lf', ang_lf)
            self.set_angle(s_rf, 'rf', ang_rf)
            self.set_angle(s_lhand, 'lhand', ang_lhand)
            self.set_angle(s_rhand, 'rhand', ang_rhand)
            time.sleep(T / steps)

    # ==========================
    #   WALKING (With Trim)
    # ==========================
    def walk(self, steps=1, dir=1):
        print(f"Walking {'Forward' if dir==1 else 'Backward'} (Trim: {WALK_TRIM})")
        
        # We adjust the Leg Amplitude using WALK_TRIM
        # If Trim is positive, Left Leg moves more.
        # If Trim is negative, Right Leg moves more.
        
        amp_left = 25 + WALK_TRIM
        amp_right = 25 - WALK_TRIM
        
        # HANDS LOCKED (0)
        A = [amp_left, amp_right, 20, 20, 0, 0] 
        O = [90, 90, 90, 90, 0, 180]
        
        if dir == 1: phase = [0, 0, math.pi/2, math.pi/2, 0, 0]
        else:        phase = [0, 0, -math.pi/2, -math.pi/2, 0, 0]
        
        for _ in range(steps): self._oscillate(A, O, 1.0, phase)

    def rotate(self, steps=1, dir=1):
        # Rotation doesn't need trim usually
        A = [20, 20, 20, 20, 0, 0]
        O = [90, 90, 90, 90, 0, 180]
        if dir == 1: # Left
            phase = [0, 0, -math.pi/2, -math.pi/2, 0, 0]
            A[0] = 10; A[1] = 25
        else: # Right
            phase = [0, 0, -math.pi/2, -math.pi/2, 0, 0]
            A[0] = 25; A[1] = 10
        for _ in range(steps): self._oscillate(A, O, 1.0, phase)

    # ==========================
    #   NEW: FREESTYLE DANCE
    # ==========================
    def dance_freestyle(self):
        print("\n>>> FREESTYLE DANCE (Random Twists) <<<")
        
        # List of "Cool Angles" you asked for
        # We mix standard 90 with sharp angles 12, 13, 0, 180
        cool_angles = [0, 12, 13, 45, 90, 135, 180]
        
        # Do 10 random moves
        for _ in range(10):
            # Pick random poses for Hands
            target_l = random.choice(cool_angles)
            target_r = random.choice(cool_angles)
            
            # Pick random tilt for feet (Small amounts to keep balance)
            tilt_l = random.choice([80, 90, 100])
            tilt_r = random.choice([80, 90, 100])
            
            print(f"Pose: L={target_l}, R={target_r}")
            
            # Move Fast!
            self.set_angle(s_lhand, 'lhand', target_l)
            self.set_angle(s_rhand, 'rhand', target_r)
            self.set_angle(s_lf, 'lf', tilt_l)
            self.set_angle(s_rf, 'rf', tilt_r)
            
            # Shake Hips slightly
            self.set_angle(s_lh, 'lh', 80)
            self.set_angle(s_rh, 'rh', 80)
            time.sleep(0.2)
            self.set_angle(s_lh, 'lh', 100)
            self.set_angle(s_rh, 'rh', 100)
            time.sleep(0.2)
            
        self.soft_start()

    def perform_routine(self):
        # Join standard dance with freestyle
        print("1. Smooth Sway...")
        A = [30, 30, 20, 20, 40, 40]
        O = [90, 90, 90, 90, 0, 180]
        phase = [0, 0, math.pi/2, math.pi/2, 0, math.pi]
        for _ in range(3): self._oscillate(A, O, 1.2, phase)
        
        print("2. THE TWIST (Freestyle)...")
        self.dance_freestyle()
        
        print("Done.")

# --- MAIN ---
if __name__ == "__main__":
    bot = EmoRobot()
    print("\n--- EMO TWIST EDITION ---")
    print("w/s: Walk Fwd/Back")
    print("a/d: Rotate")
    print("f: FREESTYLE DANCE (Random Twists!)")
    print("p: Full Routine")
    print("q: Quit")
    
    try:
        while True:
            cmd = input("Cmd: ").lower()
            if cmd == 'w': bot.walk(steps=4, dir=1)
            elif cmd == 's': bot.walk(steps=4, dir=-1)
            elif cmd == 'a': bot.rotate(steps=3, dir=1)
            elif cmd == 'd': bot.rotate(steps=3, dir=-1)
            elif cmd == 'f': bot.dance_freestyle()
            elif cmd == 'p': bot.perform_routine()
            elif cmd == 'q': 
                bot.soft_start()
                break
    except KeyboardInterrupt:
        bot.soft_start()
