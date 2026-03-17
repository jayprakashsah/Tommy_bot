import os
import google.generativeai as genai
from gtts import gTTS
from dotenv import load_dotenv
import requests
from io import BytesIO
from PIL import Image
import datetime
import re

# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

current_lang = "en-IN" 
robot_name = "Tommy"
model = None

# --- 1. SMART AI CONNECTION ---
if not api_key:
    print("\n[CRITICAL] API Key MISSING in .env")
else:
    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_model = next((m for m in available_models if "flash" in m), None)
        if not chosen_model:
            chosen_model = next((m for m in available_models if "gemini-pro" in m), available_models[0] if available_models else None)
        
        if chosen_model:
            print(f"[SYSTEM] CONNECTED TO: {chosen_model}")
            model = genai.GenerativeModel(chosen_model)
    except Exception as e:
        print(f"[CONNECTION ERROR] {e}")

# --- 2. FILE HELPERS ---
def load_robot_name():
    global robot_name
    try:
        if os.path.exists("robot_name.txt"):
            with open("robot_name.txt", "r") as f:
                robot_name = f.read().strip()
    except: pass
    return robot_name

def extract_name_from_text(text):
    text = text.lower().replace(".", "")
    remove_phrases = ["my name is", "i am", "call me", "this is", "name is"]
    for phrase in remove_phrases:
        if phrase in text:
            text = text.replace(phrase, "").strip()
    return text.capitalize()

# --- 3. SPEECH & INTENT ---
def speak(text):
    if not text: return
    print(f"🤖 Says: {text}")
    try:
        if "CMD_" in text or "|" in text: return 
        lang_settings = {'en-IN': 'en', 'hi-IN': 'hi', 'ta-IN': 'ta', 'te-IN': 'te'}
        code = lang_settings.get(current_lang, 'en')
        tts = gTTS(text=text, lang=code, tld='co.in')
        tts.save("response.mp3")
        os.system("mpg123 -q response.mp3")
    except Exception as e:
        print(f"Speech Error: {e}")

def analyze_intent(text):
    if not model: return "CHAT", "I have no brain connection."
    
    # --- UPDATED PROMPT WITH SEARCH IMAGE ---
    prompt = f"""
    You are {robot_name}. User said: "{text}"
    Classify the intent into ONE of these categories.
    Output ONLY: TYPE|CONTENT

    Categories:
    1. CMD_MOVE -> Physical movement (Content: dance, walk_forward, walk_backward, turn_left, turn_right, stop).
    2. CMD_SEARCH_IMG -> If user wants to see an image. (Content: search term).
    3. CMD_EMOTION -> If user asks "How do I look?" or "Read my mood".
    4. CMD_GAME -> If user wants to play Tic Tac Toe.
    5. CMD_OPEN_CAMERA -> If user wants to see camera feed.
    6. CMD_IDENTIFY -> If user asks "what is this".
    7. CMD_FACE -> If user asks "who am I" or "scan face".
    8. CMD_MUSIC -> If user wants to play a song (Content = song name).
    9. CHAT -> General conversation.

    Examples:
    "Show me a cat" -> CMD_SEARCH_IMG|cat
    "Show image of car" -> CMD_SEARCH_IMG|car
    "Dance for me" -> CMD_MOVE|dance
    "Walk forward" -> CMD_MOVE|walk_forward
    "How am I looking?" -> CMD_EMOTION|check
    "Who is in front of you?" -> CMD_FACE|scan
    "Play Believer" -> CMD_MUSIC|Believer
    "Hello" -> CHAT|Hi there!
    """
    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        if "|" in result:
            return result.split("|", 1)
        return "CHAT", result
    except:
        return "CHAT", "I am confusing."

# --- 4. VISION & SEARCH ---
def identify_image(image_path):
    if not model: return "I cannot see right now."
    try:
        img = Image.open(image_path)
        response = model.generate_content(["Describe this object in one short sentence.", img])
        return response.text.strip()
    except: return "Unknown object."

def fetch_image(query):
    """
    Downloads an image for the given query from loremflickr (free placeholder service).
    """
    try:
        print(f"[SEARCH] Downloading image for: {query}")
        # 240x240 is the size of your round display
        url = f"https://loremflickr.com/240/240/{query.replace(' ', '%20')}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img.save("temp_search.jpg")
            return True
    except Exception as e:
        print(f"Search Error: {e}")
    return False
