import displayio
print("DisplayIO dir:", dir(displayio))
try:
    from fourwire import FourWire
    print("SUCCESS: Found 'FourWire' in 'fourwire' module.")
except ImportError:
    print("FAIL: Could not import 'fourwire'.")

try:
    print("Checking displayio.FourWire...")
    print(displayio.FourWire)
    print("SUCCESS: Found 'displayio.FourWire'")
except AttributeError:
    print("FAIL: 'displayio' has no 'FourWire'")
