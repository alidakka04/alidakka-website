import os
from duckduckgo_search import DDGS
from PIL import Image
import urllib.request
import time

equipment = [
    ("islemci.png", "AMD RYZEN 5 7600X processor box"),
    ("ekran-karti.png", "ASUS PRIME RTX 5070 WHITE graphics card"),
    ("anakart.png", "MSI B850M GAMING PLUS WHITE motherboard"),
    ("ram.png", "LEXAR ARES 16 GB 6400 MHz WHITE RAM"),
    ("sogutucu.png", "ASUS MAX Gaming LC 360mm ARGB LCD White cooler"),
    ("kasa.png", "BITFENIX MH100 WHITE case pc"),
    ("ssd.png", "TEAM T-FORCE ssd nvme"),
    ("fan.png", "LIAN LI UNI FAN CL Wireless White"),
    ("monitor1.png", "AOC monitor gaming"),
    ("monitor2.png", "Casper Excalibur 200 Hz monitor"),
    ("mouse.png", "LOGITECH G PRO X SUPERLIGHT 2 WHITE mouse"),
    ("klavye.png", "LOGITECH G515 TKL WHITE keyboard"),
    ("kulaklik.png", "LOGITECH G733 WHITE headset"),
    ("mousepad.png", "Wraith Spirit of Aim Pro Hybrid mousepad"),
    ("skatez.png", "Hoverpad V3 mouse skatez"),
    ("koltuk.png", "Hawk Fab c5 White Fabric gaming chair")
]

os.makedirs("ekipmanlar", exist_ok=True)

with DDGS() as ddgs:
    for filename, query in equipment:
        print(f"Searching for {query}...")
        results = list(ddgs.images(query, max_results=1))
        if results:
            img_url = results[0]['image']
            filepath = os.path.join("ekipmanlar", filename)
            try:
                urllib.request.urlretrieve(img_url, filepath)
                # Resize to make it square-ish and smaller
                try:
                    img = Image.open(filepath).convert("RGBA")
                    img.thumbnail((300, 300))
                    img.save(filepath, "PNG")
                    print(f"Saved {filename}")
                except Exception as e:
                    print(f"Image processing failed for {filename}: {e}")
            except Exception as e:
                print(f"Download failed for {filename}: {e}")
        time.sleep(1)

print("Fixing logo.png...")
try:
    img = Image.open("logo.png").convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        # threshold for black
        if item[0] < 20 and item[1] < 20 and item[2] < 20:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    img.save("logo.png", "PNG")
    print("Fixed logo.png")
except Exception as e:
    print(f"Error fixing logo: {e}")
