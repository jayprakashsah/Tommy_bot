import os
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def analyze_emotion(image_path):
    """
    Sends the image to Gemini Flash to detect emotion.
    """
    if not api_key:
        print("Error: API Key missing in emotion core.")
        return "neutral"

    try:
        # Check if file exists
        if not os.path.exists(image_path):
            return "neutral"

        # Setup Gemini
        genai.configure(api_key=api_key)
        # Use Flash because it is fast and cheap
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Load Image
        img = Image.open(image_path)
        
        # Ask AI
        prompt = "Look at the face in this image. What is the dominant emotion? Return ONE word only (Example: Happy, Sad, Angry, Fear, Neutral)."
        response = model.generate_content([prompt, img])
        
        # Clean result
        emotion = response.text.strip().lower()
        print(f"[EMOTION AI] Detected: {emotion}")
        
        # Normalize simple keywords for the robot to understand
        if "happy" in emotion or "joy" in emotion or "smile" in emotion: return "happy"
        if "sad" in emotion or "cry" in emotion or "upset" in emotion: return "sad"
        if "angry" in emotion or "mad" in emotion: return "angry"
        if "fear" in emotion or "scared" in emotion: return "fear"
        
        return "neutral"

    except Exception as e:
        print(f"Emotion Error: {e}")
        return "neutral"
