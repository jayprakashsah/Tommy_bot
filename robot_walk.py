import time
from adafruit_servokit import ServoKit

# --- Configuration ---
# Initialize the PCA9685 driver (16 channels)
kit = ServoKit(channels=16)

# Servo Mapping (Based on your request)
# HIP moves leg forward/back | FOOT tilts the robot left/right
L_HIP  = 0
L_FOOT = 1
R_HIP  = 2
R_FOOT = 3

# --- Calibration / Center Positions ---
# Adjust these offsets if your robot's legs aren't perfectly straight at 90 degrees
TRIM_L_HIP  = 0 
TRIM_L_FOOT = 0
TRIM_R_HIP  = 0
TRIM_R_FOOT = 0

# Base Angle (Stand position)
CENTER = 90

def set_angle(channel, angle):
    """Safely writes the angle to the servo."""
    # Constrain angle between 0 and 180 to prevent damage
    if angle < 0: angle = 0
    if angle > 180: angle = 180
    kit.servo[channel].angle = angle

def stand():
    """Moves all servos to the center (standing) position."""
    print("Standing...")
    set_angle(L_HIP,  CENTER + TRIM_L_HIP)
    set_angle(L_FOOT, CENTER + TRIM_L_FOOT)
    set_angle(R_HIP,  CENTER + TRIM_R_HIP)
    set_angle(R_FOOT, CENTER + TRIM_R_FOOT)
    time.sleep(0.5)

# --- Movement Primitives ---

def walk_forward(steps=4, speed=0.3):
    """
    Otto Walk Logic:
    1. Tilt Right (Lift Left Leg)
    2. Swing Left Hip Forward
    3. Tilt Left (Lift Right Leg)
    4. Swing Right Hip Forward
    """
    print(f"Walking Forward: {steps} steps")
    
    # Amplitude: How far hips swing (20) and feet tilt (20)
    h_amp = 20 
    f_amp = 20 
    
    for _ in range(steps):
        # Phase 1: Tilt Body to the Right (Lift Left foot)
        set_angle(L_FOOT, CENTER - f_amp) # Tilt
        set_angle(R_FOOT, CENTER - f_amp) # Tilt matching
        time.sleep(speed)

        # Phase 2: Swing Left Leg Forward (Right Leg back relative to body)
        set_angle(L_HIP, CENTER + h_amp)
        set_angle(R_HIP, CENTER + h_amp)
        time.sleep(speed)

        # Phase 3: Tilt Body to the Left (Lift Right foot)
        set_angle(L_FOOT, CENTER + f_amp)
        set_angle(R_FOOT, CENTER + f_amp)
        time.sleep(speed)

        # Phase 4: Swing Right Leg Forward
        set_angle(L_HIP, CENTER - h_amp)
        set_angle(R_HIP, CENTER - h_amp)
        time.sleep(speed)
    
    stand()

def walk_backward(steps=4, speed=0.3):
    print(f"Walking Backward: {steps} steps")
    h_amp = 20
    f_amp = 20
    
    for _ in range(steps):
        # Reverse the Hip logic of forward
        # Tilt Right
        set_angle(L_FOOT, CENTER - f_amp)
        set_angle(R_FOOT, CENTER - f_amp)
        time.sleep(speed)

        # Swing Left Leg BACK
        set_angle(L_HIP, CENTER - h_amp)
        set_angle(R_HIP, CENTER - h_amp)
        time.sleep(speed)

        # Tilt Left
        set_angle(L_FOOT, CENTER + f_amp)
        set_angle(R_FOOT, CENTER + f_amp)
        time.sleep(speed)

        # Swing Right Leg BACK
        set_angle(L_HIP, CENTER + h_amp)
        set_angle(R_HIP, CENTER + h_amp)
        time.sleep(speed)
        
    stand()

def turn_left(steps=4, speed=0.3):
    print("Turning Left...")
    f_amp = 20
    h_amp = 30 
    
    for _ in range(steps):
        # Tilt Right (Weight on Right leg)
        set_angle(L_FOOT, CENTER - f_amp)
        set_angle(R_FOOT, CENTER - f_amp)
        time.sleep(speed)

        # Move Left Hip (Swing leg out)
        set_angle(L_HIP, CENTER + h_amp)
        set_angle(R_HIP, CENTER) # Right hip stays
        time.sleep(speed)

        # Tilt Left (Weight on Left leg)
        set_angle(L_FOOT, CENTER + f_amp)
        set_angle(R_FOOT, CENTER + f_amp)
        time.sleep(speed)

        # Return Hips to center
        set_angle(L_HIP, CENTER)
        set_angle(R_HIP, CENTER)
        time.sleep(speed)
    
    stand()

def turn_right(steps=4, speed=0.3):
    print("Turning Right...")
    f_amp = 20
    h_amp = 30 
    
    for _ in range(steps):
        # Tilt Left (Weight on Left leg)
        set_angle(L_FOOT, CENTER + f_amp)
        set_angle(R_FOOT, CENTER + f_amp)
        time.sleep(speed)

        # Move Right Hip (Swing leg out)
        set_angle(L_HIP, CENTER) 
        set_angle(R_HIP, CENTER - h_amp)
        time.sleep(speed)

        # Tilt Right (Weight on Right leg)
        set_angle(L_FOOT, CENTER - f_amp)
        set_angle(R_FOOT, CENTER - f_amp)
        time.sleep(speed)

        # Return Hips
        set_angle(L_HIP, CENTER)
        set_angle(R_HIP, CENTER)
        time.sleep(speed)
    
    stand()

def dance():
    print("Dancing: Tiptoe!")
    # A simple "tiptoe" dance move
    for _ in range(3):
        set_angle(L_FOOT, 50)
        set_angle(R_FOOT, 130)
        time.sleep(0.2)
        stand()
        time.sleep(0.2)
        
        # Shake hips
        set_angle(L_HIP, 60)
        set_angle(R_HIP, 60)
        time.sleep(0.2)
        set_angle(L_HIP, 120)
        set_angle(R_HIP, 120)
        time.sleep(0.2)
    stand()

# --- Main Execution ---
if __name__ == "__main__":
    try:
        stand()
        time.sleep(1)
        
        walk_forward(4)
        time.sleep(1)
        
        walk_backward(4)
        time.sleep(1)
        
        turn_left(4)
        turn_right(4)
        
        dance()
        
    except KeyboardInterrupt:
        # If you press Ctrl+C, robot goes to stand position
        stand()
