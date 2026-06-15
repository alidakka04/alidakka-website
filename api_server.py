import os
import json
import base64
import requests
import time
from flask import Flask, jsonify, request, render_template_string
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

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

# Cache variables: Dictionary { "user_id": {"data": {...}, "time": float} }
FACEIT_CACHE = {}
CACHE_DURATION = 1800  # 30 dakika (saniye cinsinden)

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# --- ADMIN PANEL ---
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Paneli</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #eee; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input { width: 100%; padding: 8px; box-sizing: border-box; }
        button { padding: 10px 15px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;}
        button:hover { background: #0056b3; }
        .delete-btn { background: #dc3545; padding: 5px 10px; }
        .delete-btn:hover { background: #c82333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Manikk API - Admin Paneli</h1>
        
        <h3>Yeni Kullanıcı Ekle / Güncelle</h3>
        <form id="userForm">
            <div class="form-group">
                <label>User ID (örn: user1):</label>
                <input type="text" id="user_id" placeholder="user2" required>
            </div>
            <div class="form-group">
                <label>Faceit Nickname:</label>
                <input type="text" id="faceit_nickname" placeholder="Oyuncu_NICK" required>
            </div>
            <div class="form-group">
                <label>Spotify Refresh Token:</label>
                <input type="text" id="spotify_refresh_token" placeholder="AQB..." required>
            </div>
            <button type="submit">Kaydet</button>
        </form>

        <h3 style="margin-top: 40px;">Kayıtlı Kullanıcılar</h3>
        <table>
            <thead>
                <tr>
                    <th>User ID</th>
                    <th>Faceit Nickname</th>
                    <th>İşlem</th>
                </tr>
            </thead>
            <tbody id="usersTable">
                <!-- Users will be populated here -->
            </tbody>
        </table>
    </div>

    <script>
        async function fetchUsers() {
            const response = await fetch('/admin/users');
            const users = await response.json();
            const tbody = document.getElementById('usersTable');
            tbody.innerHTML = '';
            for (const [userId, data] of Object.entries(users)) {
                tbody.innerHTML += `
                    <tr>
                        <td><strong>${userId}</strong></td>
                        <td>${data.faceit_nickname}</td>
                        <td><button class="delete-btn" onclick="deleteUser('${userId}')">Sil</button></td>
                    </tr>
                `;
            }
        }

        document.getElementById('userForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const user_id = document.getElementById('user_id').value;
            const data = {
                faceit_nickname: document.getElementById('faceit_nickname').value,
                spotify_refresh_token: document.getElementById('spotify_refresh_token').value
            };
            await fetch('/admin/users/' + user_id, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            document.getElementById('userForm').reset();
            fetchUsers();
        });

        async function deleteUser(user_id) {
            if(confirm(user_id + " adlı kullanıcıyı silmek istediğinize emin misiniz?")) {
                await fetch('/admin/users/' + user_id, { method: 'DELETE' });
                fetchUsers();
            }
        }

        fetchUsers();
    </script>
</body>
</html>
"""

@app.route('/admin', methods=['GET'])
def admin_panel():
    return render_template_string(ADMIN_HTML)

@app.route('/admin/users', methods=['GET'])
def get_all_users():
    return jsonify(load_users())

@app.route('/admin/users/<user_id>', methods=['POST'])
def save_user(user_id):
    data = request.json
    users = load_users()
    users[user_id] = {
        "faceit_nickname": data.get("faceit_nickname", ""),
        "spotify_refresh_token": data.get("spotify_refresh_token", "")
    }
    save_users(users)
    return jsonify({"status": "success"})

@app.route('/admin/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    users = load_users()
    if user_id in users:
        del users[user_id]
        save_users(users)
    return jsonify({"status": "success"})

# --- FACEIT API ---
@app.route('/faceit/<user_id>', methods=['GET'])
def faceit(user_id):
    global FACEIT_CACHE
    users = load_users()
    
    if user_id not in users:
        return jsonify({"error": "Kullanici bulunamadi"}), 404
        
    faceit_nickname = users[user_id].get("faceit_nickname")
    if not faceit_nickname:
        return jsonify({"error": "Kullanicinin Faceit bilgisi yok"}), 400

    current_time = time.time()
    
    # Cache kontrolü
    if user_id in FACEIT_CACHE:
        cache_data = FACEIT_CACHE[user_id]
        if (current_time - cache_data["time"]) < CACHE_DURATION:
            print(f"[{user_id}] Faceit verisi CACHE'den gonderiliyor...")
            return jsonify(cache_data["data"])
            
    print(f"[{user_id}] Faceit verisi API'den guncelleniyor...")

    if not FACEIT_API_KEY:
        return jsonify({"error": "FACEIT_API_KEY bulunamadi."}), 500

    headers = {
        "Authorization": f"Bearer {FACEIT_API_KEY}",
        "Accept": "application/json"
    }

    try:
        player_res = requests.get(f"https://open.faceit.com/data/v4/players?nickname={faceit_nickname}", headers=headers)
        if player_res.status_code != 200:
            return jsonify({"error": "Faceit profil bulunamadi"}), 404
        
        player_data = player_res.json()
        player_id = player_data.get("player_id")
        cs2_data = player_data.get("games", {}).get("cs2", {})

        stats_res = requests.get(f"https://open.faceit.com/data/v4/players/{player_id}/stats/cs2", headers=headers)
        average_kd = "-"
        win_rate = "-"
        
        if stats_res.status_code == 200:
            stats_data = stats_res.json()
            lifetime = stats_data.get("lifetime", {})
            average_kd = lifetime.get("Average K/D Ratio", "-")
            win_rate = lifetime.get("Win Rate %", "-")

        history_res = requests.get(f"https://open.faceit.com/data/v4/players/{player_id}/history?game=cs2&offset=0&limit=5", headers=headers)
        recent_matches = []
        
        if history_res.status_code == 200:
            history_data = history_res.json()
            for item in history_data.get("items", []):
                match_id = item.get("match_id")
                finished_at = item.get("finished_at")
                
                match_stats_res = requests.get(f"https://open.faceit.com/data/v4/matches/{match_id}/stats", headers=headers)
                if match_stats_res.status_code != 200: continue
                
                match_stats_data = match_stats_res.json()
                rounds = match_stats_data.get("rounds", [])
                if not rounds: continue
                
                round_info = rounds[0]
                map_name = round_info.get("round_stats", {}).get("Map", "Unknown")
                score = round_info.get("round_stats", {}).get("Score", "")
                
                p_kills = 0
                p_deaths = 0
                p_adr = "?"
                is_win = False
                player_team_score = ""
                enemy_team_score = ""
                
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

        data_to_cache = {
            "skill_level": cs2_data.get("skill_level", 1),
            "faceit_elo": cs2_data.get("faceit_elo", "-"),
            "average_kd": average_kd,
            "win_rate": win_rate,
            "recent_matches": recent_matches
        }
        
        FACEIT_CACHE[user_id] = {
            "data": data_to_cache,
            "time": current_time
        }

        return jsonify(data_to_cache)

    except Exception as e:
        print(f"[{user_id}] Faceit Error: {e}")
        return jsonify({"error": str(e)}), 500


# --- SPOTIFY API ---
@app.route('/spotify/<user_id>', methods=['GET'])
def spotify(user_id):
    users = load_users()
    if user_id not in users:
        return jsonify({"error": "Kullanici bulunamadi"}), 404
        
    refresh_token = users[user_id].get("spotify_refresh_token")
    if not refresh_token:
        return jsonify({"error": "Kullanicinin Spotify Refresh Token bilgisi yok"}), 400

    if not all([SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET]):
        return jsonify({"error": "Missing Spotify Client ID/Secret"}), 500

    basic_auth = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    
    try:
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {basic_auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
        )
        token_res.raise_for_status()
        access_token = token_res.json().get("access_token")

        playing_res = requests.get(
            "https://api.spotify.com/v1/me/player/currently-playing",
            headers={"Authorization": f"Bearer {access_token}"}
        )

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
        print(f"[{user_id}] Spotify Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("Multi-Tenant API Sunucusu Baslatiliyor...")
    print("Erisim adresleri:")
    print(" - Admin Paneli: http://localhost:5000/admin")
    print(" - API (Faceit):   http://localhost:5000/faceit/<user_id>")
    print(" - API (Spotify):  http://localhost:5000/spotify/<user_id>")
    app.run(host='0.0.0.0', port=5000, debug=True)
