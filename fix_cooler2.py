import urllib.request
import os
from rembg import remove, new_session

# Use official asus image url
url = "https://dlcdnwebimgs.asus.com/gain/16900f60-93bc-41de-84d7-75908b8b54da/w800/fwebp"
try:
    print("Downloading official image from Asus...")
    req_img = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req_img) as response:
        input_data = response.read()
        
    print("Removing background with alpha matting...")
    session = new_session("u2net")
    output_data = remove(input_data, session=session, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
    
    with open("ekipmanlar/sogutucu.png", "wb") as o:
        o.write(output_data)
        
    print("Done! Replaced sogutucu.png with official Asus image.")
except Exception as e:
    print(f"Error: {e}")
