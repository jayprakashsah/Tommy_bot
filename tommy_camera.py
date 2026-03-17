import time
import displayio
from picamera2 import Picamera2
from PIL import Image

class TommyCamera:
    def __init__(self, display, main_group, lock):
        self.display = display
        self.main_group = main_group
        self.lock = lock
        self.picam = None
        self.running = False

    def start(self):
        if self.running: return
        print("[CAM] Starting...")
        self.picam = Picamera2()
        config = self.picam.create_preview_configuration(main={"size": (240, 240), "format": "RGB888"})
        self.picam.configure(config)
        self.picam.start()
        self.running = True

    def stop(self):
        if not self.running: return
        print("[CAM] Stopping...")
        if self.picam:
            self.picam.stop()
            self.picam.close()
            self.picam = None
        self.running = False

    def capture_photo(self, filename="photo.jpg"):
        if not self.running: return False
        try:
            self.picam.capture_file(filename)
            return True
        except:
            return False
            
    def update_feed(self):
        """Captures one frame and updates display (Called in loop)."""
        if not self.running: return
        
        try:
            # Capture fast
            self.picam.capture_file("temp_live.jpg")
            
            # Convert to BMP
            img = Image.open("temp_live.jpg")
            img.save("temp_live.bmp")
            
            # Update Display
            with self.lock:
                odb = displayio.OnDiskBitmap("temp_live.bmp")
                tg = displayio.TileGrid(odb, pixel_shader=odb.pixel_shader)
                
                # Clear old group
                while len(self.main_group) > 0:
                    self.main_group.pop()
                    
                self.main_group.append(tg)
                self.display.refresh()
                
        except Exception as e:
            pass
