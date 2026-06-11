import urllib.request
import urllib.parse
import re
from rembg import remove, new_session

query = "ASUS ROG Strix LC 360 RGB White Edition"
url = "https://images.search.yahoo.com/search/images?p=" + urllib.parse.quote(query)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    print("Searching Yahoo...")
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        
    matches = re.findall(r'imgurl=(http[^&]+)', html)
    if matches:
        # Get first high-res looking image
        img_url = urllib.parse.unquote(matches[0])
        print(f"Found image: {img_url}")
        
        print("Downloading...")
        req_img = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_img) as response:
            input_data = response.read()
            
        print("Removing background with alpha matting...")
        session = new_session("u2net")
        output_data = remove(input_data, session=session, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
        
        with open("ekipmanlar/sogutucu.png", "wb") as o:
            o.write(output_data)
            
        print("Done!")
    else:
        print("No image found on Yahoo.")
except Exception as e:
    print(f"Error: {e}")
