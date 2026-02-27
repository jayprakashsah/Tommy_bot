import time
import board
import busio
import displayio
import os
from fourwire import FourWire
from adafruit_gc9a01a import GC9A01A
from picamera2 import Picamera2
from PIL import Image

# --- 1. SETUP DISPLAY ---
displayio.release_displays()
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
display_bus = FourWire(spi, command=board.D25, chip_select=board.D8, reset=board.D27, baudrate=24000000)
display = GC9A01A(display_bus, width=240, height=240)

# --- 2. SETUP CAMERA ---
print("Initializing Camera...")
try:
    picam = Picamera2()
    # Configure 240x240 capture
    config = picam.create_preview_configuration(main={"size": (240, 240), "format": "RGB888"})
    picam.configure(config)
    picam.start()
    print("Camera Started.")
except Exception as e:
    print(f"Camera Error: {e}")
    exit()

# --- 3. DISPLAY LOOP ---
main_group = displayio.Group()
display.root_group = main_group

print("Displaying Camera Feed... (Press Ctrl+C to Stop)")

try:
    while True:
        # 1. Capture to JPG (Fastest capture method)
        picam.capture_file("temp_cam.jpg")
        
        # 2. Convert JPG to BMP using Pillow
        try:
            img = Image.open("temp_cam.jpg")
            img.save("temp_cam.bmp")
            
            # 3. Display the BMP
            # We must create a new group to force a refresh
            odb = displayio.OnDiskBitmap("temp_cam.bmp")
            tile_grid = displayio.TileGrid(odb, pixel_shader=odb.pixel_shader)
            
            new_group = displayio.Group()
            new_group.append(tile_grid)
            display.root_group = new_group
            
        except Exception as e:
            print(f"Frame Error: {e}")

        # Small delay to prevent CPU overheating during test
        time.sleep(0.05)

except KeyboardInterrupt:
    picam.stop()
    print("\nStopped.")
