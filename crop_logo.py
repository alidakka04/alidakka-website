import os
from rembg import remove
from PIL import Image

try:
    with open("logo.png", 'rb') as i:
        input_data = i.read()
        
    output_data = remove(input_data)
    
    with open("logo.png", 'wb') as o:
        o.write(output_data)
        
    # Now crop it
    img = Image.open("logo.png").convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    img.save("logo.png", "PNG")
    print("Logo perfectly cleaned with rembg and cropped tightly!")
except Exception as e:
    print(f"Error: {e}")
