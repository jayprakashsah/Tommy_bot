import sys
import os
import time
import threading
import random
import subprocess
import board
import busio
import digitalio
import displayio
import terminalio
import gc
import re
import datetime
import sqlite3
import math
import requests
from adafruit_display_text import label
from ctypes import *
from contextlib import contextmanager

# --- SILENCE ERRORS ---
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt): pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def no_alsa_noise():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield

with no_alsa_noise():
    import speech_recognition as sr
    import face_recognition
    from fourwire import FourWire
    from adafruit_gc9a01a import GC9A01A

# --- CUSTOM MODULES ---
import tommy_emotions
import tommy_camera
import tommy_brain
import tommy_db
import tommy_emotion_core  # NEW: Feelings
import EmoRobot            # NEW: Motors

# --- CONFIGURATION ---
TIMEZONE_OFFSET = 5.5

# --- INITIALIZE MOTORS ---
try:
    bot_legs = EmoRobot.EmoRobot()
    print("[SYSTEM] Motors Connected.")
except Exception as e:
    print(f"[SYSTEM] Motor Error (Running without legs): {e}")
    bot_legs = None

# --- DATABASE ---
def init_reminder_db():
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reminders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  purpose TEXT, 
                  trigger_time REAL, 
                  readable_time TEXT)''')
    conn.commit()
    conn.close()
init_reminder_db()

# --- HARDWARE ---
displayio.release_displays()
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
display_bus = FourWire(spi, command=board.D25, chip_select=board.D8, reset=board.D27, baudrate=24000000)
display = GC9A01A(display_bus, width=240, height=240)

touch_main = digitalio.DigitalInOut(board.D23)
touch_main.direction = digitalio.Direction.INPUT
touch_main.pull = digitalio.Pull.DOWN

touch_learn = digitalio.DigitalInOut(board.D22)
touch_learn.direction = digitalio.Direction.INPUT
touch_learn.pull = digitalio.Pull.DOWN

light_pin = digitalio.DigitalInOut(board.D5)
light_pin.direction = digitalio.Direction.OUTPUT
light_pin.value = False

# --- DISPLAY GROUPS ---
main_group = displayio.Group()
weather_group = displayio.Group()
clock_group = displayio.Group()
timer_group = displayio.Group()
# Global Display Lock to prevent threading crashes
display_lock = threading.Lock()

display.root_group = main_group

# Shared Palette
bitmap = displayio.Bitmap(240, 240, 9)
palette = displayio.Palette(9)
palette[0]=0x000000; palette[1]=0x00FFFF; palette[2]=0xFF0000; palette[3]=0xFFFF00; 
palette[4]=0x00FF00; palette[5]=0xFFFFFF; palette[6]=0x333333; palette[7]=0x0000FF; palette[8]=0xFFA500
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
main_group.append(tile_grid)

# Dedicated Weather Bitmap
weather_bmp = displayio.Bitmap(240, 240, 9)
weather_tg = displayio.TileGrid(weather_bmp, pixel_shader=palette)
weather_group.append(weather_tg)

robot_state = "idle"
camera_obj = tommy_camera.TommyCamera(display, main_group, display_lock)
current_name = tommy_brain.load_robot_name()
is_camera_live = False

# --- GLOBALS ---
timer_running = False
timer_end_timestamp = 0
timer_start_timestamp = 0
timer_ui_visible = False

# --- UI FUNCTIONS ---
def draw_weather_icon(icon_type):
    for y in range(240):
        for x in range(240): weather_bmp[x, y] = 0
    cx, cy = 120, 120
    if "sun" in icon_type or "clear" in icon_type:
        for r in range(40):
            for deg in range(0, 360):
                rad = math.radians(deg); x = int(cx + r * math.cos(rad)); y = int(cy + r * math.sin(rad))
                if 0 <= x < 240 and 0 <= y < 240: weather_bmp[x, y] = 3
        for deg in range(0, 360, 45):
            for r in range(50, 70):
                rad = math.radians(deg); x = int(cx + r * math.cos(rad)); y = int(cy + r * math.sin(rad))
                if 0 <= x < 240 and 0 <= y < 240: weather_bmp[x, y] = 8
    elif "cloud" in icon_type or "rain" in icon_type:
        offsets = [(-20, 0), (20, 0), (0, -15)]
        for ox, oy in offsets:
            for r in range(25):
                for deg in range(0, 360):
                    rad = math.radians(deg); x = int(cx + ox + r * math.cos(rad)); y = int(cy + oy + r * math.sin(rad))
                    if 0 <= x < 240 and 0 <= y < 240: weather_bmp[x, y] = 6
        if "rain" in icon_type:
            for i in range(-20, 30, 10):
                for j in range(20, 40):
                    x = cx + i; y = cy + j
                    if 0 <= x < 240 and 0 <= y < 240: weather_bmp[x, y] = 7

def setup_clock_ui():
    while len(clock_group) > 0: clock_group.pop()
    bg_bmp = displayio.Bitmap(240, 240, 1); bg_pal = displayio.Palette(1); bg_pal[0]=0x000000
    clock_group.append(displayio.TileGrid(bg_bmp, pixel_shader=bg_pal))
    utc_now = datetime.datetime.utcnow(); now = utc_now + datetime.timedelta(hours=TIMEZONE_OFFSET)
    t_str = now.strftime("%I:%M"); ampm = now.strftime("%p"); date_str = now.strftime("%A, %b %d")
    lbl_time = label.Label(terminalio.FONT, text=t_str, color=0x00FFFF, scale=6)
    lbl_time.anchor_point = (0.5, 0.5); lbl_time.anchored_position = (120, 100)
    lbl_ampm = label.Label(terminalio.FONT, text=ampm, color=0xFFFF00, scale=3)
    lbl_ampm.anchor_point = (0.5, 0.5); lbl_ampm.anchored_position = (120, 160)
    lbl_date = label.Label(terminalio.FONT, text=date_str, color=0xFFFFFF, scale=2)
    lbl_date.anchor_point = (0.5, 0.5); lbl_date.anchored_position = (120, 40)
    clock_group.append(lbl_time); clock_group.append(lbl_ampm); clock_group.append(lbl_date)
    return f"The time is {t_str} {ampm}"

def draw_timer_ring(bmp, percentage):
    cx, cy = 120, 120; radius_outer = 118; radius_inner = 108
    color = 4 
    if percentage < 0.5: color = 3 
    if percentage < 0.2: color = 2 
    for r in range(radius_inner, radius_outer):
        for deg in range(0, 360, 3): 
            rad = math.radians(deg - 90); x = int(cx + r * math.cos(rad)); y = int(cy + r * math.sin(rad))
            if 0 <= x < 240 and 0 <= y < 240:
                if (deg / 360.0) < percentage: bmp[x, y] = color
                else: bmp[x, y] = 6 

def get_weather(location=""):
    try:
        url = "https://wttr.in/" + location + "?format=j1"
        response = requests.get(url, timeout=3)
        data = response.json()
        current = data['current_condition'][0]
        temp = current['temp_C']
        desc = current['weatherDesc'][0]['value'].lower()
        return f"{desc}, {temp} degrees", desc
    except: return "I cannot check the weather.", "unknown"

# --- GAME ---
def play_tic_tac_toe(r, mic):
    global robot_state
    robot_state = "game"
    tommy_brain.speak("Tic Tac Toe. Say 1 to 9.")
    board_state = [" "] * 9 
    
    game_group = displayio.Group()
    bg_bmp = displayio.Bitmap(240, 240, 2); bg_pal = displayio.Palette(2); bg_pal[0]=0x000000; bg_pal[1]=0xFFFFFF
    bg_grid = displayio.TileGrid(bg_bmp, pixel_shader=bg_pal)
    for y in range(40, 200):
        for x in [100, 140]: bg_bmp[x, y] = 1
    for x in range(60, 180):
        for y in [93, 146]: bg_bmp[x, y] = 1
    game_group.append(bg_grid)
    
    positions = [(70,60),(120,60),(170,60),(70,120),(120,120),(170,120),(70,180),(120,180),(170,180)]
    text_labels = []
    for i in range(9):
        lbl = label.Label(terminalio.FONT, text=str(i+1), color=0x00FFFF, scale=2)
        lbl.anchor_point = (0.5,0.5); lbl.anchored_position = positions[i]
        game_group.append(lbl); text_labels.append(lbl)
    
    with display_lock: display.root_group = game_group

    game_active = True
    while game_active:
        valid_move = False
        while not valid_move:
            if touch_main.value: game_active = False; break
            try:
                with mic as source: audio = r.listen(source, timeout=3, phrase_time_limit=2)
                cmd = r.recognize_google(audio).lower()
                move = -1
                if "one" in cmd or "1" in cmd: move=0
                elif "two" in cmd or "to" in cmd: move=1
                elif "three" in cmd or "3" in cmd: move=2
                elif "four" in cmd or "4" in cmd: move=3
                elif "five" in cmd or "5" in cmd: move=4
                elif "six" in cmd or "6" in cmd: move=5
                elif "seven" in cmd or "7" in cmd: move=6
                elif "eight" in cmd or "8" in cmd: move=7
                elif "nine" in cmd or "9" in cmd: move=8
                if move != -1:
                    if board_state[move] == " ":
                        text_labels[move].text = "X"; text_labels[move].color = 0x00FF00
                        board_state[move] = "X"; valid_move = True
                    else: tommy_brain.speak("Taken.")
            except: pass
        if not game_active: break
        if check_win(board_state, "X"): tommy_brain.speak("You won!"); time.sleep(3); break
        if " " not in board_state: tommy_brain.speak("Draw."); time.sleep(3); break
        tommy_brain.speak("My turn.")
        available = [i for i, x in enumerate(board_state) if x == " "]
        if available:
            bot_move = random.choice(available)
            board_state[bot_move] = "O"; text_labels[bot_move].text = "O"; text_labels[bot_move].color = 0xFF0000
            if check_win(board_state, "O"): tommy_brain.speak("I won!"); time.sleep(3); break

    with display_lock: 
        display.root_group = main_group
        tommy_emotions.draw_face(bitmap, "idle")
    robot_state = "idle"; gc.collect() 

def check_win(b, p):
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for x,y,z in wins:
        if b[x]==p and b[y]==p and b[z]==p: return True
    return False

def camera_feed_thread():
    global is_camera_live
    while is_camera_live: camera_obj.update_feed(); time.sleep(0.04)

def enter_live_camera_mode(r, mic):
    global robot_state, is_camera_live
    tommy_brain.speak("Camera On."); robot_state = "camera"; camera_obj.start(); is_camera_live = True
    t_feed = threading.Thread(target=camera_feed_thread, daemon=True); t_feed.start()
    while True:
        if touch_main.value:
            is_camera_live = False
            time.sleep(0.2)
            camera_obj.stop()
            with display_lock:
                display.root_group = main_group 
                tommy_emotions.draw_face(bitmap, "idle")
                display.refresh() 
            robot_state = "idle"
            tommy_brain.speak("Closed.")
            while touch_main.value: time.sleep(0.1)
            break 

        try:
            with mic as source: audio = r.listen(source, timeout=0.5, phrase_time_limit=2)
            cmd = r.recognize_google(audio).lower()
            if "click" in cmd or "photo" in cmd:
                tommy_brain.speak("3"); time.sleep(0.5); tommy_brain.speak("2"); time.sleep(0.5); tommy_brain.speak("1")
                is_camera_live = False; time.sleep(0.2); camera_obj.capture_photo("user_click.jpg")
                tommy_brain.speak("Click")
                
                photo_group = displayio.Group()
                odb = displayio.OnDiskBitmap("user_click.jpg"); tg = displayio.TileGrid(odb, pixel_shader=odb.pixel_shader)
                photo_group.append(tg)
                
                with display_lock: display.root_group = photo_group
                start = time.time()
                while time.time() - start < 30:
                    if touch_main.value: break
                    time.sleep(0.1)
                
                with display_lock: display.root_group = main_group
                is_camera_live = True; t_feed = threading.Thread(target=camera_feed_thread, daemon=True); t_feed.start()
        except: pass
    gc.collect()

def perform_face_recognition(quiet_mode=False):
    global robot_state
    if not quiet_mode: tommy_brain.speak("Scanning...")
    camera_obj.start(); time.sleep(1.0); camera_obj.capture_photo("temp_face.jpg"); camera_obj.stop()
    found_someone = False
    try:
        known_names, _, known_encodings = tommy_db.get_all_faces()
        unknown_image = face_recognition.load_image_file("temp_face.jpg")
        unknown_encodings = face_recognition.face_encodings(unknown_image)
        if len(unknown_encodings) > 0:
            found_someone = True
            matches = face_recognition.compare_faces(known_encodings, unknown_encodings[0], tolerance=0.5)
            if True in matches:
                name = known_names[matches.index(True)]; tommy_brain.speak(f"Hello {name}!")
            else: tommy_brain.speak("Hello friend! Nice to meet you.")
    except: pass
    if quiet_mode and not found_someone: tommy_brain.speak("Hello! I can't see you clearly, but hi friend!")
    robot_state = "idle"; gc.collect() 

def perform_object_id():
    global robot_state
    tommy_brain.speak("Checking."); camera_obj.start(); time.sleep(2); camera_obj.capture_photo("temp_obj.jpg"); camera_obj.stop()
    with display_lock:
        tommy_emotions.draw_face(bitmap, "thinking")
    tommy_brain.speak(tommy_brain.identify_image("temp_obj.jpg"))
    robot_state = "idle"; gc.collect() 

def parse_date_time_from_speech(text):
    now = datetime.datetime.now(); target_dt = now
    if "tomorrow" in text: target_dt += datetime.timedelta(days=1)
    match_date = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)', text)
    if match_date:
        try:
            day = int(match_date.group(1)); month_str = match_date.group(2)
            month_map = {"january":1, "february":2, "march":3, "april":4, "may":5, "june":6, "july":7, "august":8, "september":9, "october":10, "november":11, "december":12}
            target_dt = target_dt.replace(month=month_map[month_str], day=day)
        except: pass
    match_time = re.search(r'(\d{1,2})(:(\d{2}))?\s*(am|pm)?', text)
    if match_time and ("at" in text or "for" in text):
        try:
            hr = int(match_time.group(1)); mn = int(match_time.group(3)) if match_time.group(3) else 0
            ampm = match_time.group(4)
            if ampm == "pm" and hr != 12: hr += 12
            if ampm == "am" and hr == 12: hr = 0
            target_dt = target_dt.replace(hour=hr, minute=mn, second=0)
        except: pass
    return target_dt

def add_reminder(text):
    purpose = "Something"
    if "remind me to" in text: purpose = text.split("remind me to")[1]
    elif "remind me" in text: purpose = text.split("remind me")[1]
    dt = parse_date_time_from_speech(text); ts = dt.timestamp(); readable = dt.strftime("%b %d, %H:%M")
    conn = sqlite3.connect('reminders.db'); c = conn.cursor()
    c.execute("INSERT INTO reminders (purpose, trigger_time, readable_time) VALUES (?, ?, ?)", (purpose.strip(), ts, readable))
    conn.commit(); conn.close()
    return readable

def delete_reminder_by_speech(text):
    conn = sqlite3.connect('reminders.db'); c = conn.cursor()
    c.execute("SELECT id, readable_time, purpose FROM reminders ORDER BY trigger_time ASC"); rows = c.fetchall()
    target_index = -1
    digit_match = re.search(r'(\d+)', text)
    if digit_match: target_index = int(digit_match.group(1)) - 1
    if target_index == -1:
        if "one" in text: target_index = 0
        elif "two" in text: target_index = 1
        elif "three" in text: target_index = 2
        elif "four" in text: target_index = 3
        elif "five" in text: target_index = 4
    deleted_count = 0
    if "all" in text: c.execute("DELETE FROM reminders"); deleted_count = len(rows)
    elif target_index != -1:
        if 0 <= target_index < len(rows):
            rem_id = rows[target_index][0]; c.execute("DELETE FROM reminders WHERE id=?", (rem_id,)); deleted_count = 1
    else:
        for rid, rtime, rpurp in rows:
            if rpurp in text: c.execute("DELETE FROM reminders WHERE id=?", (rid,)); deleted_count += 1
    conn.commit(); conn.close(); return deleted_count

def check_reminders_loop():
    global robot_state
    while True:
        try:
            now_ts = time.time(); conn = sqlite3.connect('reminders.db'); c = conn.cursor()
            c.execute("SELECT id, purpose FROM reminders WHERE trigger_time <= ?", (now_ts,)); due = c.fetchall()
            for rid, purpose in due:
                if robot_state == "idle":
                    tommy_brain.speak(f"Reminder: {purpose}"); c.execute("DELETE FROM reminders WHERE id=?", (rid,)); conn.commit()
            conn.close()
        except: pass
        time.sleep(10)

def show_all_reminders_on_display():
    global robot_state
    tommy_brain.speak("Checking reminders.")
    conn = sqlite3.connect('reminders.db'); c = conn.cursor()
    c.execute("SELECT readable_time, purpose FROM reminders ORDER BY trigger_time ASC"); rows = c.fetchall(); conn.close()
    
    if not rows: tommy_brain.speak("No upcoming reminders."); return
    
    tommy_brain.speak(f"You have {len(rows)} reminders.")
    
    remind_group = displayio.Group()
    bg = displayio.Bitmap(240, 240, 1); bg_pal = displayio.Palette(1); bg_pal[0]=0x000000
    remind_group.append(displayio.TileGrid(bg, pixel_shader=bg_pal))
    
    lbl_count = label.Label(terminalio.FONT, text="", color=0x00FFFF, scale=2); lbl_count.anchored_position = (120, 20)
    lbl_time = label.Label(terminalio.FONT, text="", color=0xFFFFFF, scale=2); lbl_time.anchored_position = (120, 80)
    lbl_purpose = label.Label(terminalio.FONT, text="", color=0x00FF00, scale=2); lbl_purpose.anchored_position = (120, 120)
    
    for lbl in [lbl_count, lbl_time, lbl_purpose]: lbl.anchor_point = (0.5, 0.5); remind_group.append(lbl)
    
    # SWITCH DISPLAY
    with display_lock: display.root_group = remind_group
    
    for i, (r_time, r_purpose) in enumerate(rows):
        if touch_main.value: break
        lbl_count.text = f"Reminder {i+1}/{len(rows)}"; lbl_time.text = r_time; lbl_purpose.text = r_purpose
        display.refresh(); tommy_brain.speak(f"{r_time}. {r_purpose}"); time.sleep(3)
    
    # RESTORE
    with display_lock: 
        display.root_group = main_group
        tommy_emotions.draw_face(bitmap, "idle")
    robot_state = "idle"

def timer_loop_func():
    global timer_running, timer_ui_visible, robot_state, timer_start_timestamp, timer_end_timestamp
    last_spoken_min = -1
    
    while len(timer_group) > 0: timer_group.pop()
    timer_bmp = displayio.Bitmap(240, 240, 9); timer_tg = displayio.TileGrid(timer_bmp, pixel_shader=palette)
    timer_group.append(timer_tg)
    lbl_day = label.Label(terminalio.FONT, text="--/--", color=0x00FFFF, scale=2); lbl_day.anchored_position = (120, 30)
    lbl_clock = label.Label(terminalio.FONT, text="--:--", color=0xFFFFFF, scale=3); lbl_clock.anchored_position = (120, 60)
    lbl_count = label.Label(terminalio.FONT, text="00:00", color=0x00FF00, scale=4); lbl_count.anchored_position = (120, 120)
    for lbl in [lbl_day, lbl_clock, lbl_count]: lbl.anchor_point = (0.5, 0.0); timer_group.append(lbl)
    total_duration = timer_end_timestamp - timer_start_timestamp

    while timer_running:
        remaining = int(timer_end_timestamp - time.time())
        utc_now = datetime.datetime.utcnow(); now = utc_now + datetime.timedelta(hours=TIMEZONE_OFFSET)
        if timer_ui_visible:
            lbl_day.text = now.strftime("%b %d"); lbl_clock.text = now.strftime("%I:%M %p") 
            mins = remaining // 60; secs = remaining % 60; lbl_count.text = f"{mins:02}:{secs:02}"
            if remaining < 10: lbl_count.color = 0xFF0000
            else: lbl_count.color = 0x00FF00
            pct = max(0, remaining / total_duration); draw_timer_ring(timer_bmp, pct)
            with display_lock:
                if display.root_group != timer_group: display.root_group = timer_group
        if remaining <= 10 and remaining > 0: tommy_brain.speak(str(remaining)); time.sleep(0.8) 
        elif remaining > 10:
            if remaining % 60 == 0 and (remaining // 60) != last_spoken_min:
                m = remaining // 60; tommy_brain.speak(f"{m} minutes left."); last_spoken_min = m
            time.sleep(0.5)
        if remaining <= 0:
            timer_running = False; timer_ui_visible = False
            tommy_brain.speak("Time up!"); tommy_brain.speak("Ring Ring Ring"); time.sleep(1)
            with display_lock:
                display.root_group = main_group
                tommy_emotions.draw_face(bitmap, "idle")
            break

def hourly_chime_loop():
    last_hour = -1
    while True:
        utc_now = datetime.datetime.utcnow(); local_now = utc_now + datetime.timedelta(hours=TIMEZONE_OFFSET)
        if local_now.minute == 0 and local_now.hour != last_hour:
            last_hour = local_now.hour
            h_speak = local_now.hour % 12; 
            if h_speak == 0: h_speak = 12
            ampm = "AM" if local_now.hour < 12 else "PM"
            if robot_state == "idle": tommy_brain.speak(f"It is {h_speak} {ampm}")
        time.sleep(20)

# --- NEW: EMOTION CHECK ---
def check_user_emotion():
    global robot_state
    tommy_brain.speak("Looking at you.")
    camera_obj.start(); time.sleep(1.0); camera_obj.capture_photo("temp_mood.jpg"); camera_obj.stop()
    
    # Use the new core file
    mood = tommy_emotion_core.analyze_emotion("temp_mood.jpg")
    tommy_brain.speak(f"You look {mood}.")
    
    # React to mood
    if mood == "happy":
        with display_lock: tommy_emotions.draw_face(bitmap, "happy")
        if bot_legs: bot_legs.turn_left(2); bot_legs.turn_right(2) # Happy wiggle
    elif mood == "sad" or mood == "fear":
        with display_lock: tommy_emotions.draw_face(bitmap, "sad")
        tommy_brain.speak("Do not worry. I am here.")
    else:
        with display_lock: tommy_emotions.draw_face(bitmap, "idle")
    
    time.sleep(2)
    with display_lock: tommy_emotions.draw_face(bitmap, "idle")

# --- MAIN ANIMATION ---
def animation_loop():
    while True:
        if display.root_group != main_group: time.sleep(0.5); continue 
        if robot_state == "idle":
            with display_lock: tommy_emotions.draw_face(bitmap, "idle")
            time.sleep(random.uniform(3, 5))
            with display_lock: tommy_emotions.draw_face(bitmap, "blink")
            time.sleep(0.15)
        elif robot_state == "speaking":
            with display_lock: tommy_emotions.draw_face(bitmap, "happy"); time.sleep(0.2)
            with display_lock: tommy_emotions.draw_face(bitmap, "idle"); time.sleep(0.2)
        elif robot_state == "music":
            with display_lock: tommy_emotions.draw_face(bitmap, "happy"); time.sleep(0.5)
            with display_lock: tommy_emotions.draw_face(bitmap, "idle"); time.sleep(0.5)
        time.sleep(0.1)

# --- CHAT GESTURE HELPER ---
def do_chat_gesture():
    """Performs the requested right-right-right-right forward gesture"""
    if bot_legs:
        bot_legs.turn_right(4)
        bot_legs.walk(1, dir=1)
        bot_legs.turn_right(4)

# --- LISTENING LOGIC ---
def listen_loop():
    global robot_state, current_name
    global timer_running, timer_end_timestamp, timer_start_timestamp, timer_ui_visible

    r = sr.Recognizer()
    try:
        with no_alsa_noise(): mic = sr.Microphone(device_index=0) 
    except: print("MIC ERROR"); return

    r.energy_threshold = 200; r.dynamic_energy_threshold = True; r.pause_threshold = 0.8
    print("\n--- SYSTEM ONLINE ---")
    tommy_brain.speak(f"{current_name} Ready.")
    
    with mic as source: r.adjust_for_ambient_noise(source, duration=1)

    while True:
        # 1. Hardware Interrupt (Touch)
        if touch_main.value:
            os.system("pkill mpv"); robot_state = "idle"; tommy_brain.speak("Stopped.")
            while touch_main.value: time.sleep(0.1)
            continue

        if touch_learn.value:
            os.system("pkill mpv"); robot_state = "idle"; tommy_brain.speak("Learning Mode."); camera_obj.start()
            time.sleep(1.5); camera_obj.capture_photo("new_face.jpg"); camera_obj.stop()
            with display_lock: display.root_group = main_group
            tommy_brain.speak("Say Name.")
            try:
                with mic as source: audio = r.listen(source, timeout=5)
                raw = r.recognize_google(audio).strip(); clean = tommy_brain.extract_name_from_text(raw)
                img = face_recognition.load_image_file("new_face.jpg"); encs = face_recognition.face_encodings(img)
                if encs: tommy_db.save_face(clean, encs[0]); tommy_brain.speak(f"Saved {clean}.")
                else: tommy_brain.speak("No face.")
            except: tommy_brain.speak("No name.")
            time.sleep(1); gc.collect(); continue
            
        # 2. Wake Word Listening
        try:
            print("[Waiting for Wake Word...]")
            with mic as source: audio = r.listen(source, timeout=0.5, phrase_time_limit=4)
            raw = r.recognize_google(audio, language=tommy_brain.current_lang).lower()
            
            if current_name.lower() in raw or "robot" in raw:
                # --- WAKE UP & ENTER CONTINUOUS LOOP ---
                os.system("pkill mpv")
                if "hello" in raw or "hi " in raw: perform_face_recognition(quiet_mode=True)

                robot_state = "listening"
                tommy_brain.speak("Ji?")
                
                # CONTINUOUS CONVERSATION LOOP
                active_conversation = True
                while active_conversation:
                    # Check Touch to Exit Loop
                    if touch_main.value:
                        tommy_brain.speak("Bye."); active_conversation = False
                        while touch_main.value: time.sleep(0.1)
                        robot_state = "idle"; break

                    try:
                        print("  [In Loop: Listening for command...]")
                        with mic as source: 
                            # Longer timeout for command
                            audio_cmd = r.listen(source, timeout=5, phrase_time_limit=10)
                        
                        cmd = r.recognize_google(audio_cmd, language=tommy_brain.current_lang).lower()
                        print(f"  Command: {cmd}")

                        # --- EXIT COMMANDS ---
                        if "stop" in cmd or "exit" in cmd or "bye" in cmd:
                            tommy_brain.speak("Ok, stopping.")
                            active_conversation = False
                            robot_state = "idle"
                            break

                        # --- HARDCODED COMMANDS (Timer/Weather/etc from original) ---
                        if "timer" in cmd and "set" in cmd:
                            seconds = 0; m_match = re.search(r'(\d+)\s*(?:min|minute)', cmd); s_match = re.search(r'(\d+)\s*(?:sec|second)', cmd)
                            if m_match: seconds += int(m_match.group(1)) * 60
                            if s_match: seconds += int(s_match.group(1))
                            if seconds > 0:
                                tommy_brain.speak(f"Timer set for {seconds} seconds.")
                                timer_start_timestamp = time.time(); timer_end_timestamp = timer_start_timestamp + seconds
                                timer_running = True; timer_ui_visible = True
                                threading.Thread(target=timer_loop_func, daemon=True).start()
                            else: tommy_brain.speak("Please say a time.")
                            continue

                        if "weather" in cmd:
                             city = "Mumbai"
                             if "in" in cmd: city = cmd.split("in")[-1].strip()
                             with display_lock: 
                                 display.root_group = weather_group
                                 draw_weather_icon("thinking")
                             tommy_brain.speak("Checking weather.")
                             text, desc = get_weather(city)
                             with display_lock: draw_weather_icon(desc)
                             tommy_brain.speak(text); time.sleep(3)
                             with display_lock: 
                                 display.root_group = main_group
                                 tommy_emotions.draw_face(bitmap, "idle")
                             continue
                        
                        if "time" in cmd or "date" in cmd:
                             spoken_time = setup_clock_ui()
                             with display_lock: display.root_group = clock_group
                             tommy_brain.speak(spoken_time)
                             time.sleep(10) 
                             with display_lock: 
                                 display.root_group = main_group
                                 tommy_emotions.draw_face(bitmap, "idle")
                             continue

                        if "light" in cmd:
                             if "on" in cmd: light_pin.value = True; tommy_brain.speak("Light on.")
                             elif "off" in cmd: light_pin.value = False; tommy_brain.speak("Light off.")
                             continue
                             
                        if "reminder" in cmd:
                            if "delete" in cmd or "remove" in cmd:
                                count = delete_reminder_by_speech(cmd)
                                if count > 0: tommy_brain.speak(f"Deleted {count} reminders.")
                                else: tommy_brain.speak("No matching reminders.")
                            elif "show" in cmd or "list" in cmd: show_all_reminders_on_display()
                            elif "set" in cmd or "add" in cmd: 
                                readable = add_reminder(cmd); tommy_brain.speak(f"Reminder set for {readable}")
                            continue

                        # --- INTENT ANALYSIS ---
                        intent, content = tommy_brain.analyze_intent(cmd)
                        print(f"  Intent: {intent} | Content: {content}")

                        # --- ACTION HANDLER ---
                        if intent == "CMD_MOVE":
                            if bot_legs:
                                robot_state = "music" # Show happy face while moving
                                if "dance" in content:
                                    tommy_brain.speak("Dancing.")
                                    bot_legs.dance_music()
                                elif "walk_forward" in content:
                                    bot_legs.walk(steps=4, dir=1)
                                elif "walk_backward" in content:
                                    bot_legs.walk(steps=4, dir=-1)
                                elif "turn_left" in content:
                                    bot_legs.turn_left(3)
                                elif "turn_right" in content:
                                    bot_legs.turn_right(3)
                                robot_state = "idle"
                                tommy_brain.speak("Done.")
                            else:
                                tommy_brain.speak("My motors are not connected.")

                        elif intent == "CMD_EMOTION":
                            check_user_emotion()

                        elif intent == "CMD_MUSIC":
                            tommy_brain.speak(f"Playing {content}")
                            cmd_str = f"yt-dlp -f bestaudio -g 'ytsearch:{content}'"
                            try:
                                url = subprocess.check_output(cmd_str, shell=True).decode().strip()
                                os.system(f"mpv --no-video '{url}' &")
                                robot_state = "idle" 
                            except: pass

                        elif intent == "CMD_GAME": play_tic_tac_toe(r, mic)
                        elif intent == "CMD_OPEN_CAMERA": enter_live_camera_mode(r, mic)
                        elif intent == "CMD_IDENTIFY": perform_object_id()
                        elif intent == "CMD_FACE": perform_face_recognition(quiet_mode=False)

                        elif intent == "CHAT":
                            robot_state = "speaking"
                            # --- SPECIAL REQUEST: GESTURE WHILE TALKING ---
                            # "rotate right-right-right-right then forward"
                            if bot_legs:
                                t_move = threading.Thread(target=do_chat_gesture)
                                t_move.start()
                            
                            tommy_brain.speak(content)
                            robot_state = "idle"

                    except sr.WaitTimeoutError:
                        print("  [Timeout - Exiting Loop]")
                        active_conversation = False
                        robot_state = "idle"
                    except sr.UnknownValueError:
                        pass # Listen again
                    except Exception as e:
                        print(f"Loop Error: {e}")
                        active_conversation = False
        
        except: pass 

if __name__ == "__main__":
    t = threading.Thread(target=animation_loop, daemon=True); t.start()
    t_chime = threading.Thread(target=hourly_chime_loop, daemon=True); t_chime.start()
    t_remind = threading.Thread(target=check_reminders_loop, daemon=True); t_remind.start()
    try: listen_loop()
    except KeyboardInterrupt: 
        if bot_legs: bot_legs.soft_start()
        camera_obj.stop()
        os.system("pkill mpv")
