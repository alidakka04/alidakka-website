import os
import re
import urllib.request
import urllib.parse
import time
from PIL import Image

equipment = [
    ("islemci.png", "AMD RYZEN 5 7600X box"),
    ("ekran-karti.png", "ASUS PRIME RTX 5070 WHITE"),
    ("anakart.png", "MSI B850M GAMING PLUS WHITE"),
    ("ram.png", "LEXAR ARES 16 GB 6400 MHz WHITE RAM"),
    ("sogutucu.png", "ASUS MAX Gaming LC 360mm ARGB LCD White"),
    ("kasa.png", "BITFENIX MH100 WHITE"),
    ("ssd.png", "TEAM T-FORCE 1TB SSD"),
    ("fan.png", "LIAN LI UNI FAN CL Wireless White"),
    ("monitor1.png", "AOC 310 Hz 0.3 MS FAST IPS monitor"),
    ("monitor2.png", "Casper Excalibur 200 Hz 1ms FAST IPS"),
    ("mouse.png", "LOGITECH G PRO X SUPERLIGHT 2 WHITE"),
    ("klavye.png", "LOGITECH G515 TKL WHITE"),
    ("kulaklik.png", "LOGITECH G733 WHITE"),
    ("mousepad.png", "Wraith Spirit of Aim Pro Hybrid"),
    ("skatez.png", "Hoverpad V3"),
    ("koltuk.png", "Hawk Fab c5 White Fabric")
]

os.makedirs("ekipmanlar", exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for filename, query in equipment:
    filepath = os.path.join("ekipmanlar", filename)
    if os.path.exists(filepath):
        print(f"{filename} already exists.")
        continue

    print(f"Searching for {query}...")
    url = "https://www.bing.com/images/search?q=" + urllib.parse.quote(query)
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
        
        # Parse Bing image search JSON data
        matches = re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', html)
        if not matches:
             matches = re.findall(r'murl":"([^"]+)"', html)

        if matches:
            img_url = matches[0]
            print(f"Found image: {img_url}")
            
            req_img = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req_img, timeout=10) as res, open(filepath, 'wb') as f:
                f.write(res.read())
            
            # Resize image
            try:
                img = Image.open(filepath).convert("RGBA")
                img.thumbnail((400, 400))
                img.save(filepath, "PNG")
                print(f"Saved {filename}")
            except Exception as e:
                print(f"Failed to resize {filename}: {e}")
        else:
            print("No matches found.")
    except Exception as e:
        print(f"Error fetching {query}: {e}")
    time.sleep(1)

print("Done!")
