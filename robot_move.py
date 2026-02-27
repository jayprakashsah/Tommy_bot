from gpiozero import AngularServo
from time import sleep
import math

# --- CONFIGURATION ---
# Adjust these offsets if your robot is not standing perfectly straight at '90'
OFFSET_LH = 0
OFFSET_LF = 0
OFFSET_RH = 0
OFFSET_RF = 0

# Pin Mapping (GPIO Numbers)
PIN_LH = 4   # Left Hip
PIN_LF = 24  # Left Foot
PIN_RH = 6   # Right Hip
PIN_RF = 13  # Right Foot (Pin 33)

# Movement Settings
SPEED = 0.05       # Time between small moves (Lower = Faster)
STEP_SIZE = 25     # How big the steps are (Degrees)
LEAN_ANGLE = 20    # How much it leans side-to-side (Degrees)

# Initialize Servos
# pulse_width is tuned for standard MG90S / SG90 servos
# min/max angles set to 0-180
lh = AngularServo(PIN_LH, min_angle=0, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0025)
lf = AngularServo(PIN_LF, min_angle=0, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0025)
rh = AngularServo(PIN_RH, min_angle=0, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0025)
rf = AngularServo(PIN_RF, min_angle=0, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0025)

def move_servos(angle_lh, angle_lf, angle_rh, angle_rf):
    """Moves all 4 servos to the target angles immediately."""
    lh.angle = 90 + OFFSET_LH + angle_lh
    lf.angle = 90 + OFFSET_LF + angle_lf
    rh.angle = 90 + OFFSET_RH + angle_rh
    rf.angle = 90 + OFFSET_RF + angle_rf

def smooth_move(target_lh, target_lf, target_rh, target_rf, duration=0.3):
    """Interpolates movement so the robot doesn't jerk and fall."""
    steps = 10
    
    # Calculate difference
    diff_lh = (target_lh - (lh.angle - 90 - OFFSET_LH)) / steps
    diff_lf = (target_lf - (lf.angle - 90 - OFFSET_LF)) / steps
    diff_rh = (target_rh - (rh.angle - 90 - OFFSET_RH)) / steps
    diff_rf = (target_rf - (rf.angle - 90 - OFFSET_RF)) / steps
    
    for i in range(steps):
        move_servos(
            (lh.angle - 90 - OFFSET_LH) + diff_lh,
            (lf.angle - 90 - OFFSET_LF) + diff_lf,
            (rh.angle - 90 - OFFSET_RH) + diff_rh,
            (rf.angle - 90 - OFFSET_RF) + diff_rf
        )
        sleep(duration / steps)

def home():
    """Stand Straight"""
    print("Standing...")
    smooth_move(0, 0, 0, 0)
    sleep(0.5)

def walk_forward(steps=4):
    """Otto Walking Gait"""
    print("Walking Forward...")
    for _ in range(steps):
        # 1. Lean Left, Right Leg Up
        smooth_move(0, LEAN_ANGLE, 0, LEAN_ANGLE)
        
        # 2. Swing Right Leg Forward, Left Leg Back
        smooth_move(-STEP_SIZE, LEAN_ANGLE, -STEP_SIZE, LEAN_ANGLE)
        
        # 3. Lean Right, Left Leg Up
        smooth_move(-STEP_SIZE, -LEAN_ANGLE, -STEP_SIZE, -LEAN_ANGLE)
        
        # 4. Swing Left Leg Forward, Right Leg Back
        smooth_move(STEP_SIZE, -LEAN_ANGLE, STEP_SIZE, -LEAN_ANGLE)

    home()

def walk_backward(steps=4):
    print("Walking Backward...")
    for _ in range(steps):
        # 1. Lean Left
        smooth_move(0, LEAN_ANGLE, 0, LEAN_ANGLE)
        # 2. Swing Legs (Reverse of forward)
        smooth_move(STEP_SIZE, LEAN_ANGLE, STEP_SIZE, LEAN_ANGLE)
        # 3. Lean Right
        smooth_move(STEP_SIZE, -LEAN_ANGLE, STEP_SIZE, -LEAN_ANGLE)
        # 4. Swing Legs
        smooth_move(-STEP_SIZE, -LEAN_ANGLE, -STEP_SIZE, -LEAN_ANGLE)
    home()

def turn_left(steps=4):
    print("Turning Left...")
    for _ in range(steps):
        # Lean Left
        smooth_move(0, LEAN_ANGLE, 0, LEAN_ANGLE)
        # Turn Hips
        smooth_move(STEP_SIZE, LEAN_ANGLE, -STEP_SIZE, LEAN_ANGLE)
        # Lean Right
        smooth_move(STEP_SIZE, -LEAN_ANGLE, -STEP_SIZE, -LEAN_ANGLE)
        # Center Hips
        smooth_move(0, -LEAN_ANGLE, 0, -LEAN_ANGLE)
    home()

def turn_right(steps=4):
    print("Turning Right...")
    for _ in range(steps):
        # Lean Right
        smooth_move(0, -LEAN_ANGLE, 0, -LEAN_ANGLE)
        # Turn Hips
        smooth_move(-STEP_SIZE, -LEAN_ANGLE, STEP_SIZE, -LEAN_ANGLE)
        # Lean Left
        smooth_move(-STEP_SIZE, LEAN_ANGLE, STEP_SIZE, LEAN_ANGLE)
        # Center Hips
        smooth_move(0, LEAN_ANGLE, 0, LEAN_ANGLE)
    home()

def dance():
    print("Dancing!")
    # Tiptoe / Flap
    for _ in range(3):
        smooth_move(0, 30, 0, -30, 0.2)
        smooth_move(0, -30, 0, 30, 0.2)
    
    # Moonwalk-ish
    for _ in range(2):
        smooth_move(-20, 0, 20, 0, 0.3)
        smooth_move(20, 0, -20, 0, 0.3)
    
    home()

# --- MAIN MENU ---
try:
    print("Robot Initialized.")
    home()
    while True:
        cmd = input("Enter command (w=fwd, s=back, a=left, d=right, q=dance, e=exit): ")
        
        if cmd == 'w':
            walk_forward()
        elif cmd == 's':
            walk_backward()
        elif cmd == 'a':
            turn_left()
        elif cmd == 'd':
            turn_right()
        elif cmd == 'q':
            dance()
        elif cmd == 'e':
            break
        
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    home()
    lh.detach()
    lf.detach()
    rh.detach()
    rf.detach()
