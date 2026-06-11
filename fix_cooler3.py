from duckduckgo_search import DDGS
import urllib.request
import os
from rembg import remove, new_session
from PIL import Image
import io

query = "ASUS ROG Strix LC 360 RGB White Edition transparent background"
print(f"Searching for: {query}")

try:
    with DDGS() as ddgs:
        results = list(ddgs.images(query, max_results=3))
        
    if results:
        img_url = results[0]['image']
        print(f"Found image: {img_url}")
        
        req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            input_data = response.read()
            
        print("Processing with alpha matting...")
        session = new_session("u2net")
        output_data = remove(input_data, session=session, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
        
        with open("ekipmanlar/sogutucu.png", "wb") as o:
            o.write(output_data)
            
        print("Done! Replaced sogutucu.png")
    else:
        print("No image found")
except Exception as e:
    print(f"Error: {e}")
