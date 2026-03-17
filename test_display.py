import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_gc9a01a import GC9A01A

# --- CRITICAL FIX: Import FourWire directly ---
try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire

# Release any displays held by the system
displayio.release_displays()

print("Initializing SPI...")
# Pin 23 (SCK), Pin 19 (MOSI)
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)

print("Initializing Display Bus...")
try:
    # Pin 22 (DC), Pin 24 (CS), Pin 13 (RST)
    display_bus = FourWire(
        spi, 
        command=board.D25, 
        chip_select=board.D8, 
        reset=board.D27,
        baudrate=24000000
    )
    
    print("Initializing Driver...")
    display = GC9A01A(display_bus, width=240, height=240)
    print("Display Setup Complete.")
except Exception as e:
    print(f"Error setting up hardware: {e}")
    exit()

# --- TEST GRAPHICS ---
main_group = displayio.Group()
display.root_group = main_group

# 1. Red Circle
bitmap = displayio.Bitmap(240, 240, 1)
palette = displayio.Palette(1)
palette[0] = 0xFF0000 # Red
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
main_group.append(tile_grid)

# 2. Text
text = "TOMMY V3\nONLINE"
text_area = label.Label(
    terminalio.FONT, 
    text=text, 
    color=0xFFFFFF, 
    scale=3,
    anchor_point=(0.5, 0.5),
    anchored_position=(120, 120)
)
main_group.append(text_area)

print("Display should be RED with White Text.")

import time
while True:
    time.sleep(1)
