import urllib.parse
import urllib.request
import json
import webbrowser
import base64
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

CLIENT_ID = "b313c9f316534360902f018b2b14217c"
CLIENT_SECRET = "74d52de819d34335a6960c9d80b3fcc6"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "user-read-currently-playing user-read-playback-state"

def get_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    }
    return "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)

def get_tokens(code):
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }).encode("utf-8")
    
    req = urllib.request.Request("https://accounts.spotify.com/api/token", data=data)
    req.add_header("Authorization", f"Basic {b64_auth_str}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Suppress HTTP logs
        
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        if self.path.startswith("/callback"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            if "code" in params:
                code = params["code"][0]
                tokens = get_tokens(code)
                print(f"SPOTIFY_REFRESH_TOKEN={tokens['refresh_token']}")
                
                # Update the .env file with the tokens directly!
                with open(".env", "w") as f:
                    f.write(f"SPOTIFY_CLIENT_ID={CLIENT_ID}\n")
                    f.write(f"SPOTIFY_CLIENT_SECRET={CLIENT_SECRET}\n")
                    f.write(f"SPOTIFY_REFRESH_TOKEN={tokens['refresh_token']}\n")
                
                html = """
                <html><body style='font-family:sans-serif;text-align:center;padding-top:100px;background:#1db954;color:white;'>
                <h1>Bağlantı Başarılı! 🎉</h1>
                <h3>Bu pencereyi kapatıp bana dönebilirsin. Kodlamaya başlıyorum!</h3>
                <script>setTimeout(()=>window.close(), 5000);</script>
                </body></html>
                """
                self.wfile.write(html.encode('utf-8'))
                os._exit(0)
            else:
                self.wfile.write(b"<h1>Hata olustu! Kodu alamadim.</h1>")
                os._exit(1)

def run():
    server_address = ('', 8888)
    httpd = HTTPServer(server_address, RequestHandler)
    url = get_auth_url()
    print("Opening browser for Spotify authentication...")
    webbrowser.open(url)
    httpd.serve_forever()

if __name__ == '__main__':
    run()
