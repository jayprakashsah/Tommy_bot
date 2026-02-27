import speech_recognition as sr

print("Searching for microphones...")
mics = sr.Microphone.list_microphone_names()

print(f"\nFound {len(mics)} microphones:")
for i, name in enumerate(mics):
    print(f"Index {i}: {name}")

print("\n-------------------------")
print("Look for the index that says 'snd_rpi_googlevoicehat' or 'googlevoicehat'.")
print("We will use that NUMBER in main.py")
