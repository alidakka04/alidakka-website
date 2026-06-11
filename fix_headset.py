import urllib.request
import os
from rembg import remove, new_session

# Download raw image
url = "https://resource.logitechg.com/w_692,c_limit,q_auto,f_auto,dpr_1.0/d_transparent.gif/content/dam/gaming/en/products/g733/gallery/g733-white-gallery-1.png?v=1"
try:
    print("Downloading image from Logitech...")
    urllib.request.urlretrieve(url, "ekipmanlar/kulaklik_raw.png")
    
    print("Removing background with alpha matting...")
    with open("ekipmanlar/kulaklik_raw.png", "rb") as i:
        input_data = i.read()
    
    session = new_session("u2net")
    output_data = remove(input_data, session=session, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
    
    with open("ekipmanlar/kulaklik.png", "wb") as o:
        o.write(output_data)
        
    os.remove("ekipmanlar/kulaklik_raw.png")
    print("Done! Replaced kulaklik.png")
except Exception as e:
    print(f"Error: {e}")
