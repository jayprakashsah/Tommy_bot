import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

L_HIP  = 0
L_FOOT = 1
R_HIP  = 2
R_FOOT = 3

CENTER = 90

def set_angle(channel, angle):
    if angle < 0: angle = 0
    if angle > 180: angle = 180
    kit.servo[channel].angle = angle

def stand():
    set_angle(L_HIP, CENTER)
    set_angle(L_FOOT, CENTER)
    set_angle(R_HIP, CENTER)
    set_angle(R_FOOT, CENTER)

def sweep_servo(channel, start, end, step, delay):
    if start < end:
        angle = start
        while angle <= end:
            set_angle(channel, angle)
            angle += step
            time.sleep(delay)
    else:
        angle = start
        while angle >= end:
            set_angle(channel, angle)
            angle -= step
            time.sleep(delay)

def full_direction_test(duration=60):
    print("Starting 1-Minute Full Servo Direction Test...")
    start_time = time.time()

    while time.time() - start_time < duration:

        # 1️⃣ Sweep All Forward
        for angle in range(0, 181, 5):
            set_angle(L_HIP, angle)
            set_angle(R_HIP, angle)
            set_angle(L_FOOT, angle)
            set_angle(R_FOOT, angle)
            time.sleep(0.02)

        # 2️⃣ Sweep All Backward
        for angle in range(180, -1, -5):
            set_angle(L_HIP, angle)
            set_angle(R_HIP, angle)
            set_angle(L_FOOT, angle)
            set_angle(R_FOOT, angle)
            time.sleep(0.02)

        # 3️⃣ Opposite Direction Test
        for angle in range(0, 181, 5):
            set_angle(L_HIP, angle)
            set_angle(R_HIP, 180 - angle)
            set_angle(L_FOOT, angle)
            set_angle(R_FOOT, 180 - angle)
            time.sleep(0.02)

        # 4️⃣ Circular Pattern Simulation
        for angle in range(0, 181, 5):
            set_angle(L_HIP, angle)
            set_angle(R_FOOT, angle)
            set_angle(R_HIP, 180 - angle)
            set_angle(L_FOOT, 180 - angle)
            time.sleep(0.02)

    print("Test Complete.")
    stand()

if __name__ == "__main__":
    try:
        stand()
        time.sleep(1)
        full_direction_test(60)
    except KeyboardInterrupt:
        stand()