import fitz
import sys

print("--- Python Executable ---")
print(sys.executable)
print("\n--- Python's Search Path (sys.path) ---")
for path in sys.path:
    print(path)
print("\n--- Location of the loaded 'fitz' module ---")
# This will print the full path to the file that was actually imported.
print(fitz.__file__)
