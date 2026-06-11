import os
import base64
import requests
import time
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# .env dosyasındaki ortam değişkenlerini yükle
load_dotenv()

app = Flask(__name__)
# Statik siteniz bu sunucuya farklı bir port/domain'den erişebilsin diye CORS ekliyoruz
CORS(app)

FACEIT_API_KEY = os.getenv("FACEIT_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

NICKNAME = "Manikk"

# Cache variables
FACEIT_CACHE = None
FACEIT_CACHE_TIME = 0
CACHE_DURATION = 1800  # 30 dakika (saniye cinsinden)

@app.route('/faceit', methods=['GET'])
def faceit():
    global FACEIT_CACHE, FACEIT_CACHE_TIME
    current_time = time.time()
    
    # Eğer önbellekte veri varsa ve henüz 30 dakika (1800 sn) geçmediyse onu döndür
    if FACEIT_CACHE is not None and (current_time - FACEIT_CACHE_TIME) < CACHE_DURATION:
        print("Faceit verisi CACHE'den gönderiliyor...")
        return jsonify(FACEIT_CACHE)
        
    print("Faceit verisi API'den güncelleniyor...")

    if not FACEIT_API_KEY:
        return jsonify({"error": "FACEIT_API_KEY bulunamadi. .env dosyanizi kontrol edin."}), 500

    headers = {
        "Authorization": f"Bearer {FACEIT_API_KEY}",
        "Accept": "application/json"
    }

    try:
        # 1. Oyuncu bilgilerini al
        player_res = requests.get(f"https://open.faceit.com/data/v4/players?nickname={NICKNAME}", headers=headers)
        if player_res.status_code != 200:
            return jsonify({"error": "Oyuncu bulunamadi"}), 404
        
        player_data = player_res.json()
        player_id = player_data.get("player_id")
        cs2_data = player_data.get("games", {}).get("cs2", {})

        # 2. Genel Istatistikler (K/D, Win Rate)
        stats_res = requests.get(f"https://open.faceit.com/data/v4/players/{player_id}/stats/cs2", headers=headers)
        average_kd = "-"
        win_rate = "-"
        
        if stats_res.status_code == 200:
            stats_data = stats_res.json()
            lifetime = stats_data.get("lifetime", {})
            average_kd = lifetime.get("Average K/D Ratio", "-")
            win_rate = lifetime.get("Win Rate %", "-")

        # 3. Son 5 Mac Gecmisi
        history_res = requests.get(f"https://open.faceit.com/data/v4/players/{player_id}/history?game=cs2&offset=0&limit=5", headers=headers)
        recent_matches = []
        
        if history_res.status_code == 200:
            history_data = history_res.json()
            for item in history_data.get("items", []):
                match_id = item.get("match_id")
                finished_at = item.get("finished_at")
                
                # Her macin detayina girip kill/death verilerini al
                match_stats_res = requests.get(f"https://open.faceit.com/data/v4/matches/{match_id}/stats", headers=headers)
                if match_stats_res.status_code != 200:
                    continue
                
                match_stats_data = match_stats_res.json()
                rounds = match_stats_data.get("rounds", [])
                if not rounds:
                    continue
                
                round_info = rounds[0]
                map_name = round_info.get("round_stats", {}).get("Map", "Unknown")
                score = round_info.get("round_stats", {}).get("Score", "")
                
                p_kills = 0
                p_deaths = 0
                p_adr = "?"
                is_win = False
                
                player_team_score = ""
                enemy_team_score = ""
                
                # Bizim oyuncunun hangi takimda oldugunu bul
                for team in round_info.get("teams", []):
                    player_found = next((p for p in team.get("players", []) if p.get("player_id") == player_id), None)
                    if player_found:
                        stats = player_found.get("player_stats", {})
                        p_kills = int(stats.get("Kills", 0))
                        p_deaths = int(stats.get("Deaths", 0))
                        p_adr = stats.get("ADR", "?")
                        is_win = team.get("team_stats", {}).get("Team Win") == "1"
                        player_team_score = team.get("team_stats", {}).get("Final Score", "")
                    else:
                        enemy_team_score = team.get("team_stats", {}).get("Final Score", "")
                
                if player_team_score and enemy_team_score:
                    score = f"{player_team_score} / {enemy_team_score}"
                    
                recent_matches.append({
                    "match_id": match_id,
                    "is_win": is_win,
                    "map": map_name,
                    "score": score,
                    "kills": p_kills,
                    "deaths": p_deaths,
                    "adr": p_adr,
                    "finished_at": finished_at
                })

        # Veriyi önbelleğe (cache) kaydet
        FACEIT_CACHE = {
            "skill_level": cs2_data.get("skill_level", 1),
            "faceit_elo": cs2_data.get("faceit_elo", "-"),
            "average_kd": average_kd,
            "win_rate": win_rate,
            "recent_matches": recent_matches
        }
        FACEIT_CACHE_TIME = current_time

        return jsonify(FACEIT_CACHE)

    except Exception as e:
        print(f"Faceit Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/spotify', methods=['GET'])
def spotify():
    if not all([SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REFRESH_TOKEN]):
        return jsonify({"error": "Missing Spotify credentials in .env file"}), 500

    basic_auth = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    
    try:
        # 1. Spotify'dan yeni bir access_token (gecici erisim anahtari) al
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {basic_auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": SPOTIFY_REFRESH_TOKEN
            }
        )
        token_res.raise_for_status()
        access_token = token_res.json().get("access_token")

        # 2. Su an calan sarkiyi sorgula
        playing_res = requests.get(
            "https://api.spotify.com/v1/me/player/currently-playing",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # Eger sarki calmiyorsa (204 No Content doner)
        if playing_res.status_code == 204 or playing_res.status_code > 400:
            return jsonify({"is_playing": False})

        song_data = playing_res.json()
        item = song_data.get("item")
        
        if not item:
            return jsonify({"is_playing": False})

        return jsonify({
            "is_playing": song_data.get("is_playing", False),
            "title": item.get("name"),
            "artist": ", ".join([artist.get("name") for artist in item.get("artists", [])]),
            "album": item.get("album", {}).get("name"),
            "albumImageUrl": item.get("album", {}).get("images", [{}])[0].get("url"),
            "songUrl": item.get("external_urls", {}).get("spotify"),
            "progress_ms": song_data.get("progress_ms"),
            "duration_ms": item.get("duration_ms")
        })

    except Exception as e:
        print(f"Spotify Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("API Sunucusu Baslatiliyor...")
    print("Erisim adresleri:")
    print(" - Local: http://localhost:5000")
    print(" - Network: http://192.168.1.5:5000")
    print(" - http://192.168.1.5:5000/faceit")
    print(" - http://192.168.1.5:5000/spotify")
    # 0.0.0.0 ile çalıştırarak ağdaki diğer cihazların da bu API'ye erişebilmesini sağlıyoruz
    app.run(host='0.0.0.0', port=5000, debug=True)
