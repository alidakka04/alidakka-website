import urllib.parse
import urllib.request
import json
import base64
import os

CLIENT_ID = "b313c9f316534360902f018b2b14217c"
CLIENT_SECRET = "74d52de819d34335a6960c9d80b3fcc6"
REDIRECT_URI = "https://manikk.vercel.app/callback"
CODE = "AQCLStvTURm_LjFu4RozUq87_yc2XAj3rdxn-KzAIiz_J3kMqiyT9Oe2TAuVh4ZSuIE-bb8pHgZ3wETPkqKFD_AJymn3UD1_R08TdHADf5FZpfcLPKNarfh-8GwqY3NQK3AVFyFHxOyAb7Qs8aIe7NmkXMluTRU2lNP18Rdu88c6SuJalKDKdZlIAgJrMdv1B7gvMWr9gtCCnfFjBPUQq10WIGYh6NMO-IYBtk6PDlwJwMzwLrT0GhxiWe-p"

auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
b64_auth_str = base64.b64encode(auth_str.encode()).decode()

data = urllib.parse.urlencode({
    "grant_type": "authorization_code",
    "code": CODE,
    "redirect_uri": REDIRECT_URI
}).encode("utf-8")

req = urllib.request.Request("https://accounts.spotify.com/api/token", data=data)
req.add_header("Authorization", f"Basic {b64_auth_str}")
req.add_header("Content-Type", "application/x-www-form-urlencoded")

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        
    refresh_token = result.get('refresh_token')
    print(f"SUCCESS! Refresh token: {refresh_token}")
    
    with open(".env", "w") as f:
        f.write(f"SPOTIFY_CLIENT_ID={CLIENT_ID}\n")
        f.write(f"SPOTIFY_CLIENT_SECRET={CLIENT_SECRET}\n")
        f.write(f"SPOTIFY_REFRESH_TOKEN={refresh_token}\n")
        
    print(".env file updated.")
except urllib.error.HTTPError as e:
    print(f"Error: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
