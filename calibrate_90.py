import time
from adafruit_servokit import ServoKit
from adafruit_extended_bus import ExtendedI2C as I2C

print("Initializing Servo Driver on Bus 3...")

# 1. Define the Custom Bus (Bus 3 created in config.txt)
try:
    # This looks for /dev/i2c-3
    i2c_bus = I2C(3)
except Exception as e:
    print(f"CRITICAL ERROR: Could not find I2C Bus 3. {e}")
    exit()

# 2. Connect to the Driver
try:
    # We pass the custom 'i2c_bus' to the kit
    kit = ServoKit(channels=16, i2c=i2c_bus, address=0x40)
except ValueError:
    print("ERROR: Bus 3 exists, but the Driver Board is not answering.")
    exit()

# 3. Set Servos to 90 Degrees
print("SUCCESS: Connected! Moving servos to 90 degrees...")

# Adjust this range if you have more or fewer servos attached
number_of_servos = 6 

for i in range(number_of_servos):
    print(f" - Setting Servo {i} to 90")
    kit.servo[i].angle = 90
    time.sleep(0.1)

print("\nDONE. All servos are locked at 90 degrees.")
print("You can now screw on the servo horns (arms/legs) at the 90-degree position.")
