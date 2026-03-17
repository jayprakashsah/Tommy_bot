import face_recognition
import pickle
import os

DB_FILE = "tommy_faces.dat"

def save_face(name, encoding):
    """Saves a new face to memory."""
    data = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "rb") as f:
                data = pickle.load(f)
        except:
            data = {}
            
    data[name] = encoding
    
    with open(DB_FILE, "wb") as f:
        pickle.dump(data, f)
    print(f"[DB] Saved {name}")

def get_all_faces():
    """Returns lists of names and encodings."""
    if not os.path.exists(DB_FILE):
        return [], [], []
        
    try:
        with open(DB_FILE, "rb") as f:
            data = pickle.load(f)
            
        names = list(data.keys())
        encodings = list(data.values())
        # We don't have intros yet, just return empty list for compatibility
        return names, [], encodings
    except:
        return [], [], []
