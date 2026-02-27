import displayio
import random

# PALETTE DEFINITIONS (Matches your main.py later)
# 0: Black (Background)
# 1: Cyan (Eyes)
# 2: Red (Angry)
# 3: Yellow (Happy)
# 4: Green (Success)
# 5: White (Text)

SCREEN_WIDTH = 240
SCREEN_HEIGHT = 240

def fill_rect(bitmap, x, y, w, h, color):
    """Helper to draw a rectangle on the bitmap"""
    for i in range(x, x + w):
        for j in range(y, y + h):
            if 0 <= i < SCREEN_WIDTH and 0 <= j < SCREEN_HEIGHT:
                bitmap[i, j] = color

def draw_face(bitmap, emotion):
    """Draws specific eye shapes based on the emotion name."""
    # 1. Clear screen (Fill with Black - Color 0)
    bitmap.fill(0)
    
    # Eye Dimensions
    eye_w = 40
    eye_h = 60
    left_x = 60
    right_x = 140
    y_pos = 90
    
    if emotion == "idle":
        # Normal Cyan Eyes
        fill_rect(bitmap, left_x, y_pos, eye_w, eye_h, 1)
        fill_rect(bitmap, right_x, y_pos, eye_w, eye_h, 1)

    elif emotion == "blink":
        # Flat thin lines (Closed eyes)
        fill_rect(bitmap, left_x, y_pos + 25, eye_w, 10, 1)
        fill_rect(bitmap, right_x, y_pos + 25, eye_w, 10, 1)

    elif emotion == "happy":
        # Yellow Eyes, shorter to look "squinty/happy"
        fill_rect(bitmap, left_x, y_pos + 10, eye_w, 40, 3)
        fill_rect(bitmap, right_x, y_pos + 10, eye_w, 40, 3)
        
    elif emotion == "angry" or emotion == "furious":
        # Red Eyes, taller
        fill_rect(bitmap, left_x, y_pos - 10, eye_w, eye_h + 20, 2)
        fill_rect(bitmap, right_x, y_pos - 10, eye_w, eye_h + 20, 2)
        
    elif emotion == "look_right":
        # Eyes shifted right
        fill_rect(bitmap, left_x + 20, y_pos, eye_w, eye_h, 1)
        fill_rect(bitmap, right_x + 20, y_pos, eye_w, eye_h, 1)
        
    elif emotion == "look_left":
        # Eyes shifted left
        fill_rect(bitmap, left_x - 20, y_pos, eye_w, eye_h, 1)
        fill_rect(bitmap, right_x - 20, y_pos, eye_w, eye_h, 1)
        
    elif emotion == "dizzy":
        # Mismatched eyes
        fill_rect(bitmap, left_x, y_pos - 20, eye_w, eye_h, 4) # One Green high
        fill_rect(bitmap, right_x, y_pos + 20, eye_w, eye_h, 4) # One Green low
