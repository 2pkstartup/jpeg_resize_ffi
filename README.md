Příklad použití v GIMP pythonu

import os
import sys
import ctypes
from glob import glob

# === ZPRACOVÁNÍ ARGUMENTŮ ===
input_dir = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
resize_percent = int(sys.argv[2]) if len(sys.argv) > 2 else 50

# === NAJÍT SLOŽKU, KDE LEŽÍ TENTO SKRIPT ===
script_dir = os.path.dirname(os.path.abspath(__file__))

# === PŘÍPRAVA KNIHOVNY ===
dll_path = os.path.join(script_dir, "jpeg_resize_ffi.dll")
lib = ctypes.CDLL(dll_path)

lib.get_jpeg_dimensions_ffi.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
lib.get_jpeg_dimensions_ffi.restype = ctypes.c_int

lib.resize_jpeg_percent_ffi.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
lib.resize_jpeg_percent_ffi.restype = ctypes.c_int

# === SLOŽKY ===
output_dir = os.path.join(input_dir, "resized")
os.makedirs(output_dir, exist_ok=True)

# === NAJDI OBRÁZKY ===
image_paths = glob(os.path.join(input_dir, "*.jpg")) + glob(os.path.join(input_dir, "*.jpeg"))

if not image_paths:
    print(f"Ve složce {input_dir} nebyly nalezeny žádné JPEG soubory.")
    exit(0)

# === ZPRACOVÁNÍ ===
for image_path in image_paths:
    filename = os.path.basename(image_path)
    print(f"\nZpracovávám: {filename}")

    width = ctypes.c_int()
    height = ctypes.c_int()

    result = lib.get_jpeg_dimensions_ffi(image_path.encode('utf-8'), ctypes.byref(width), ctypes.byref(height))
    if result != 0:
        print("❌ Nelze zjistit rozměry.")
        continue

    print(f"✅ Velikost: {width.value} × {height.value}")

    output_path = os.path.join(output_dir, filename)

    result = lib.resize_jpeg_percent_ffi(image_path.encode('utf-8'), output_path.encode('utf-8'), resize_percent)
    if result != 0:
        print("❌ Chyba při změně velikosti.")
    else:
        print(f"💾 Uloženo do: {output_path}")
