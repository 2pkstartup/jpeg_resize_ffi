import os
import sys
import ctypes
from glob import glob

# === ZPRACOVÁNÍ ARGUMENTŮ ===
input_dir = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
resize_percent = int(sys.argv[2]) if len(sys.argv) > 2 else 50
resize_percent = max(1, min(resize_percent, 1000))  # bezpečný rozsah

# === NAJÍT SLOŽKU, KDE LEŽÍ TENTO SKRIPT ===
script_dir = os.path.dirname(os.path.abspath(__file__))

# === PŘÍPRAVA KNIHOVNY ===
dll_path = os.path.join(script_dir, "jpeg_resize_ffi.dll")
lib = ctypes.CDLL(dll_path)

lib.get_jpeg_dimensions_ffi.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)]
lib.get_jpeg_dimensions_ffi.restype = ctypes.c_int

lib.resize_jpeg_ffi.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint]
lib.resize_jpeg_ffi.restype = ctypes.c_int

# === SLOŽKY ===
output_dir = os.path.join(input_dir, f"resized_{resize_percent}pct")
os.makedirs(output_dir, exist_ok=True)

# === NAJDI OBRÁZKY ===
image_paths = glob(os.path.join(input_dir, "*.jpg")) + glob(os.path.join(input_dir, "*.jpeg"))

if not image_paths:
    print(f"🟡 Ve složce {input_dir} nebyly nalezeny žádné JPEG soubory.")
    exit(0)

# === ZPRACOVÁNÍ ===
for image_path in image_paths:
    filename = os.path.basename(image_path)
    print(f"\n🖼 Zpracovávám: {filename}")

    width = ctypes.c_uint()
    height = ctypes.c_uint()

    result = lib.get_jpeg_dimensions_ffi(
        image_path.encode('utf-8'),
        ctypes.byref(width),
        ctypes.byref(height)
    )

    if result != 0:
        print("❌ Nelze zjistit rozměry.")
        continue

    orig_w = width.value
    orig_h = height.value

    print(f"✅ Původní velikost: {orig_w} × {orig_h}")

    # Výpočet nové velikosti podle procenta
    new_w = max(1, orig_w * resize_percent // 100)
    new_h = max(1, orig_h * resize_percent // 100)

    print(f"📐 Nová velikost: {new_w} × {new_h} ({resize_percent} %)")

    output_path = os.path.join(output_dir, filename)

    result = lib.resize_jpeg_ffi(
        image_path.encode('utf-8'),
        output_path.encode('utf-8'),
        new_w,
        new_h
    )

    if result != 0:
        print("❌ Chyba při změně velikosti.")
    else:
        print(f"💾 Uloženo do: {output_path}")
