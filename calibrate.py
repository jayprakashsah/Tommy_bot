import time
from adafruit_servokit import ServoKit
from adafruit_extended_bus import ExtendedI2C as I2C

# --- CONFIGURATION ---
# We are using the "Software I2C" bus we created on Bus 3
try:
    i2c_bus = I2C(3)
except Exception as e:
    print(f"Error: Could not access Bus 3. {e}")
    exit()

# Initialize the Servo Kit using the custom bus
# Address 0x40 is the default for PCA9685, which matches your scan result
kit = ServoKit(channels=16, i2c=i2c_bus, address=0x40)

print("SUCCESS: Connected to Servo Driver at 0x40 on Bus 3.")
print("Moving servos 0-5 to 90 degrees...")

# --- CALIBRATION ---
# You have 6 servos (0 to 5)
for i in range(6):
    print(f" - Setting Servo {i} to 90 degrees")
    kit.servo[i].angle = 90
    time.sleep(0.2) # Small delay to prevent power spikes

print("\nDONE! All servos are at 90 degrees.")
print("You can now attach the legs and arms.")
