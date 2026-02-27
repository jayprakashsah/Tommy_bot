import time
from smbus2 import SMBus

# --- CONFIGURATION ---
bus_number = 3       # We are using your custom Bus 3
device_addr = 0x40   # The address we found in i2cdetect
servo_channel = 0    # Plug a servo into slot 0

# --- REGISTERS ---
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06
LED0_ON_H = 0x07
LED0_OFF_L = 0x08
LED0_OFF_H = 0x09

def set_pwm_freq(bus, freq):
    # Set frequency to 50Hz (Standard for Servos)
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    prescale = int(prescaleval + 0.5)
    
    # Go to sleep to set prescale
    oldmode = bus.read_byte_data(device_addr, MODE1)
    newmode = (oldmode & 0x7F) | 0x10
    bus.write_byte_data(device_addr, MODE1, newmode)
    bus.write_byte_data(device_addr, PRESCALE, prescale)
    bus.write_byte_data(device_addr, MODE1, oldmode)
    time.sleep(0.005)
    bus.write_byte_data(device_addr, MODE1, oldmode | 0x80)

def set_servo_pulse(bus, channel, pulse_ms):
    # Convert milliseconds to 12-bit steps (0-4096)
    # 20ms period (50Hz)
    pulse_length = 1000000 / 50 / 4096 
    duty = int((pulse_ms * 1000) / pulse_length)
    
    # Register offsets for the specific channel
    on_l = LED0_ON_L + 4 * channel
    on_h = LED0_ON_H + 4 * channel
    off_l = LED0_OFF_L + 4 * channel
    off_h = LED0_OFF_H + 4 * channel
    
    bus.write_byte_data(device_addr, on_l, 0)
    bus.write_byte_data(device_addr, on_h, 0)
    bus.write_byte_data(device_addr, off_l, duty & 0xFF)
    bus.write_byte_data(device_addr, off_h, duty >> 8)

# --- MAIN LOOP ---
try:
    bus = SMBus(bus_number)
    print("Resetting Chip...")
    set_pwm_freq(bus, 50)
    
    print("Wiggling Servo on Channel 0...")
    while True:
        print("Left...")
        set_servo_pulse(bus, servo_channel, 1.0) # 1.0ms (0 degrees)
        time.sleep(1)
        
        print("Right...")
        set_servo_pulse(bus, servo_channel, 2.0) # 2.0ms (180 degrees)
        time.sleep(1)

except Exception as e:
    print(f"Error: {e}")
