import time
from smbus2 import SMBus

# We use Bus 3 because that is where your driver is detected
bus = SMBus(3)
addr = 0x40

# --- REGISTERS ---
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06
LED0_ON_H = 0x07
LED0_OFF_L = 0x08
LED0_OFF_H = 0x09

print("1. Sending SOFTWARE RESET...")
# This special address 0x00 with data 0x06 resets all PCA9685 chips
try:
    bus.write_byte(0x00, 0x06) 
    time.sleep(0.1)
except:
    pass # Ignore error if it doesn't ack, just trying to wake it up

print("2. Waking up chip...")
# Write to MODE1 to wake up (Clear Sleep bit) and enable Auto-Increment
bus.write_byte_data(addr, MODE1, 0x20) 
time.sleep(0.1)

print("3. Setting Frequency to 50Hz...")
# We have to sleep to set prescale
old_mode = bus.read_byte_data(addr, MODE1)
new_mode = (old_mode & 0x7F) | 0x10 # Sleep
bus.write_byte_data(addr, MODE1, new_mode)
bus.write_byte_data(addr, PRESCALE, 121) # 121 = approx 50Hz
bus.write_byte_data(addr, MODE1, old_mode)
time.sleep(0.01)
bus.write_byte_data(addr, MODE1, old_mode | 0x80) # Restart

print("4. ATTEMPTING MOVEMENT on Channel 0...")
# Move to Center (1.5ms pulse)
# ON time = 0
# OFF time = 307 (approx 1.5ms out of 20ms)
bus.write_byte_data(addr, LED0_ON_L, 0x00)
bus.write_byte_data(addr, LED0_ON_H, 0x00)
bus.write_byte_data(addr, LED0_OFF_L, 0x33) # Low byte of 307
bus.write_byte_data(addr, LED0_OFF_H, 0x01) # High byte of 307 (0x133 = 307)

print("Check Servo 0 now. Did it twitch?")
