import sys
print("Python yolun:", sys.executable)
print("Modül arama yolları:")
for p in sys.path:
    print("-", p)
