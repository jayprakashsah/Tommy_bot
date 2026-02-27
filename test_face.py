import board
import busio
import displayio
import time
import random
from fourwire import FourWire  # Use the fix we found earlier
from adafruit_gc9a01a import GC9A01A

# --- IMPORT OUR NEW LIBRARY ---
import tommy_emotions

displayio.release_displays()

# --- HARDWARE SETUP ---
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
display_bus = FourWire(spi, command=board.D25, chip_select=board.D8, reset=board.D27, baudrate=24000000)
display = GC9A01A(display_bus, width=240, height=240)

# --- GRAPHICS SETUP ---
main_group = displayio.Group()
display.root_group = main_group

# Define Palette (Colors)
palette = displayio.Palette(6)
palette[0] = 0x000000 # Black
palette[1] = 0x00FFFF # Cyan
palette[2] = 0xFF0000 # Red
palette[3] = 0xFFFF00 # Yellow
palette[4] = 0x00FF00 # Green
palette[5] = 0xFFFFFF # White

# Create Bitmap (The Face Layer)
bitmap = displayio.Bitmap(240, 240, 6)
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
main_group.append(tile_grid)

print("Starting Animation Loop...")
print("Press Ctrl+C to stop.")

try:
    while True:
        # 1. Normal State
        tommy_emotions.draw_face(bitmap, "idle")
        time.sleep(random.uniform(2.0, 4.0)) # Wait 2-4 seconds
        
        # 2. Blink
        tommy_emotions.draw_face(bitmap, "blink")
        time.sleep(0.15)
        
        # 3. Random Action (Look around or feel emotion)
        action = random.choice(["look_right", "look_left", "happy", "angry", "dizzy", "idle"])
        if action != "idle":
            tommy_emotions.draw_face(bitmap, action)
            time.sleep(1.0)
            
except KeyboardInterrupt:
    print("\nStopping...")
