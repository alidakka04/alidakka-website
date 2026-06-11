import urllib.request
import urllib.parse
import re
import os
from rembg import remove, new_session

query = "ASUS ROG Strix LC 360 RGB White Edition png"
url = "https://www.bing.com/images/search?q=" + urllib.parse.quote(query)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

try:
    print("Searching Bing for cooler image...")
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        
    # Find murl (media url) in Bing's JSON data attributes
    match = re.search(r'murl&quot;:&quot;(http[^&]+)&quot;', html)
    if match:
        img_url = match.group(1)
        print(f"Found image: {img_url}")
        
        print("Downloading image...")
        req_img = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_img) as response:
            input_data = response.read()
            
        print("Removing background with alpha matting...")
        session = new_session("u2net")
        output_data = remove(input_data, session=session, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
        
        with open("ekipmanlar/sogutucu.png", "wb") as o:
            o.write(output_data)
            
        print("Done! Replaced sogutucu.png")
    else:
        print("No image found on Bing.")
        
except Exception as e:
    print(f"Error: {e}")
