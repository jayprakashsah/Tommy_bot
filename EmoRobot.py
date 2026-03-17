import time
import math
import random
from gpiozero import AngularServo

# --- PINS (Direct to Pi) ---
PIN_L_HIP  = 4   # Pin 7
PIN_L_FOOT = 24  # Pin 18
PIN_R_HIP  = 6   # Pin 31
PIN_R_FOOT = 13  # Pin 33
PIN_L_HAND = 26  # Pin 37
# PIN_R_HAND = 12  # DISABLED

# --- SETUP ---
def make_servo(pin):
    return AngularServo(pin, min_angle=0, max_angle=180, 
                        min_pulse_width=0.0005, max_pulse_width=0.0025)

# Initialize Servos
s_lh = make_servo(PIN_L_HIP)
s_lf = make_servo(PIN_L_FOOT)
s_rh = make_servo(PIN_R_HIP)
s_rf = make_servo(PIN_R_FOOT)
s_lhand = make_servo(PIN_L_HAND)
# s_rhand = make_servo(PIN_R_HAND) <-- DISABLED

class EmoRobot:
    def __init__(self):
        self.home = 90
        self.home_l_hand = 0    
        self.offset = {'lh':0, 'lf':0, 'rh':0, 'rf':0, 'lhand':0} 
        self.soft_start()

    def set_angle(self, servo, name, angle):
        target = angle + self.offset.get(name, 0)
        target = max(0, min(180, target))
        servo.angle = target

    def soft_start(self):
        """Reset to stable standing pose"""
        print("Emo: Stabilizing...")
        self.set_angle(s_lh, 'lh', 90)
        self.set_angle(s_rh, 'rh', 90)
        self.set_angle(s_lf, 'lf', 90)
        self.set_angle(s_rf, 'rf', 90)
        self.set_angle(s_lhand, 'lhand', self.home_l_hand) 
        time.sleep(1.0)

    def _oscillate(self, A, O, T, phase_diff, cycles=1):
        steps = 40 
        total_steps = int(steps * cycles)
        for i in range(total_steps):
            current_cycle_progress = i / steps
            # Sine Wave Math
            ang_lh = O[0] + A[0] * math.sin(2 * math.pi * current_cycle_progress + phase_diff[0])
            ang_rh = O[1] + A[1] * math.sin(2 * math.pi * current_cycle_progress + phase_diff[1])
            ang_lf = O[2] + A[2] * math.sin(2 * math.pi * current_cycle_progress + phase_diff[2])
            ang_rf = O[3] + A[3] * math.sin(2 * math.pi * current_cycle_progress + phase_diff[3])
            
            # Hand Math
            raw_sin_l = math.sin(2 * math.pi * current_cycle_progress + phase_diff[4])
            ang_lhand = O[4] + abs(A[4] * raw_sin_l) 
            
            self.set_angle(s_lh, 'lh', ang_lh)
            self.set_angle(s_rh, 'rh', ang_rh)
            self.set_angle(s_lf, 'lf', ang_lf)
            self.set_angle(s_rf, 'rf', ang_rf)
            self.set_angle(s_lhand, 'lhand', ang_lhand)
            time.sleep(T / steps)

    # ==========================
    #    ROTATION (TURNING)
    # ==========================
    def turn_left(self, steps=3):
        print(f"Turning Left ({steps} steps)")
        # Left Hip (-20) moves backward, Right Hip (20) moves forward -> Rotate Left
        A = [-20, 20, 25, 25, 0, 0] 
        O = [90, 90, 90, 90, 0, 180]
        phase = [0, 0, math.pi/2, math.pi/2, 0, 0]
        self._oscillate(A, O, T=1.0, phase_diff=phase, cycles=steps)

    def turn_right(self, steps=3):
        print(f"Turning Right ({steps} steps)")
        # Left Hip (20) moves forward, Right Hip (-20) moves backward -> Rotate Right
        A = [20, -20, 25, 25, 0, 0]
        O = [90, 90, 90, 90, 0, 180]
        phase = [0, 0, math.pi/2, math.pi/2, 0, 0]
        self._oscillate(A, O, T=1.0, phase_diff=phase, cycles=steps)

    # ==========================
    #      DANCE ROUTINES
    # ==========================
    def dance_music(self):
        print("\n>> ♫ STARTING EMO DANCE ROUTINE ♫")
        
        # 1. Warm Up (Sway)
        print(">> 1. Warm Up")
        A = [20, 20, 10, 10, 10, 0] 
        O = [90, 90, 90, 90, 10, 0]
        P = [0, 0, math.pi/2, math.pi/2, 0, 0] 
        self._oscillate(A, O, T=1.5, phase_diff=P, cycles=4)

        # 2. Beat Drop (Fast Taps)
        print(">> 2. The Beat Drop")
        A = [5, 5, 35, 35, 50, 0] 
        O = [90, 90, 90, 90, 10, 0]
        P = [0, 0, 0, math.pi, 0, 0] 
        self._oscillate(A, O, T=0.4, phase_diff=P, cycles=10)

        # 3. Tippy Toes
        print(">> 3. Tippy Toes")
        for _ in range(4):
            self.set_angle(s_lf, 'lf', 60) 
            self.set_angle(s_lhand, 'lhand', 60)
            time.sleep(0.3)
            self.set_angle(s_lf, 'lf', 90)
            self.set_angle(s_lhand, 'lhand', 0)
            self.set_angle(s_rf, 'rf', 120) 
            time.sleep(0.3)
            self.set_angle(s_rf, 'rf', 90)
        
        # 4. The Slide (STABILIZED)
        print(">> 4. The Slide")
        self.set_angle(s_lh, 'lh', 80)
        self.set_angle(s_rh, 'rh', 80)
        self.set_angle(s_lf, 'lf', 85)
        self.set_angle(s_lhand, 'lhand', 30)
        time.sleep(0.8) 
        
        self.set_angle(s_lh, 'lh', 100)
        self.set_angle(s_rh, 'rh', 100)
        self.set_angle(s_rf, 'rf', 95)
        self.set_angle(s_lhand, 'lhand', 10)
        time.sleep(0.8)

        # 5. Finale - LONG FREESTYLE
        print(">> 5. Freestyle (Extended Mix)!")
        
        # Increased range to 100 loops (approx 20 seconds of dancing)
        # You can change 100 to 200 if you want it even longer.
        for i in range(100):
            # Print progress every 10 steps so you know it's working
            if i % 10 == 0: print(f"   >> Vibe check {i}%")
            
            l_foot = random.randint(70, 110)
            r_foot = random.randint(70, 110)
            l_hand = random.randint(0, 80)
            
            self.set_angle(s_lf, 'lf', l_foot)
            self.set_angle(s_rf, 'rf', r_foot)
            self.set_angle(s_lhand, 'lhand', l_hand)
            
            if random.random() > 0.5:
                self.set_angle(s_lh, 'lh', 80)
                self.set_angle(s_rh, 'rh', 80)
            else:
                self.set_angle(s_lh, 'lh', 100)
                self.set_angle(s_rh, 'rh', 100)
                
            time.sleep(0.2) 

        print(">> Dance Complete.")
        self.soft_start()

    def walk(self, steps=1, T=1.0, dir=1):
        print(f"Walking {'Forward' if dir==1 else 'Backward'}")
        A = [25, 25, 20, 20, 0, 0] 
        O = [90, 90, 90, 90, 0, 180]
        if dir == 1: phase = [0, 0, math.pi/2, math.pi/2, 0, 0]
        else: phase = [0, 0, -math.pi/2, -math.pi/2, 0, 0]
        self._oscillate(A, O, T, phase, cycles=steps)

# --- MAIN CONTROLLER ---
if __name__ == "__main__":
    bot = EmoRobot()
    print("\n--- EMO PARTY CONTROLLER ---")
    print("m: ♫ Long Dance Routine ♫")
    print("w: Walk Forward")
    print("s: Walk Backward")
    print("a: Turn Left (Rotate)")
    print("d: Turn Right (Rotate)")
    print("q: Quit")
    
    try:
        while True:
            cmd = input("Cmd: ").lower()
            if cmd == 'm': bot.dance_music()
            elif cmd == 'w': bot.walk(4, dir=1)
            elif cmd == 's': bot.walk(4, dir=-1)
            elif cmd == 'a': bot.turn_left(4)
            elif cmd == 'd': bot.turn_right(4)
            elif cmd == 'q': 
                bot.soft_start()
                break
    except KeyboardInterrupt:
        bot.soft_start()
