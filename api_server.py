import os
import json
import base64
import requests
import time
from urllib.parse import urlencode
from flask import Flask, jsonify, request, render_template_string, redirect, Response
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
CACHE_DURATION = 1800  # 30 dakika

STEAM_CACHE = {}
STEAM_CACHE_DURATION = 10800  # 3 saat (10800 saniye)

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# --- BASIC AUTH ---
def check_auth(username, password):
    return username == 'alidakka04' and password == '213133'

def authenticate():
    return Response(
        'Erişim Engellendi. Lütfen yetkili bilgilerinizi giriniz.\n', 401,
        {'WWW-Authenticate': 'Basic realm="Admin Paneli"'}
    )

def requires_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


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
        .container { max-width: 1000px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #eee; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input { width: 100%; padding: 8px; box-sizing: border-box; margin-bottom: 5px; }
        button { padding: 10px 15px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;}
        button:hover { background: #0056b3; }
        .delete-btn { background: #dc3545; padding: 5px 10px; }
        .delete-btn:hover { background: #c82333; }
        .copy-btn { background: #1DB954; padding: 5px 10px; margin-right: 5px;}
        .copy-btn:hover { background: #1ed760; }
        .status-ok { color: #1DB954; font-weight: bold; }
        .status-wait { color: #f39c12; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Manikk API - Admin Paneli</h1>
        
        <h3>Yeni Kullanıcı Ekle</h3>
        <form id="userForm">
            <div class="form-group">
                <label>User ID (örn: user2):</label>
                <input type="text" id="user_id" placeholder="Kullanıcı kimliği (Boşluksuz İngilizce karakter)" required>
            </div>
            <div class="form-group">
                <label>Faceit Nickname:</label>
                <input type="text" id="faceit_nickname" placeholder="Faceit Kullanıcı Adı" required>
            </div>
            <div class="form-group">
                <label>Steam ID64 (İsteğe bağlı - Envanter için):</label>
                <input type="text" id="steam_id" placeholder="Örn: 76561198858013891">
            </div>
            <button type="submit" style="width: 100%; margin-top: 10px;">Kullanıcıyı Kaydet (Sonra Davet Linkini Arkadaşa At)</button>
        </form>

        <h3 style="margin-top: 40px;">Kayıtlı Kullanıcılar</h3>
        <table>
            <thead>
                <tr>
                    <th>User ID</th>
                    <th>Faceit Nickname</th>
                    <th>Steam ID</th>
                    <th>Spotify Durumu</th>
                    <th>Davet İşlemleri</th>
                    <th>Sil</th>
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
            if (response.status === 401) {
                window.location.reload();
                return;
            }
            const users = await response.json();
            const tbody = document.getElementById('usersTable');
            tbody.innerHTML = '';
            for (const [userId, data] of Object.entries(users)) {
                const inviteLink = 'https://api.manikk.info/invite/' + userId;
                const hasToken = data.spotify_refresh_token && data.spotify_refresh_token.length > 0;
                const statusHtml = hasToken ? '<span class="status-ok">Bağlı ✔️</span>' : '<span class="status-wait">Bekleniyor ⏳</span>';
                
                tbody.innerHTML += `
                    <tr>
                        <td><strong>${userId}</strong></td>
                        <td>${data.faceit_nickname}</td>
                        <td>${data.steam_id || '-'}</td>
                        <td>${statusHtml}</td>
                        <td>
                            <button class="copy-btn" onclick="copyLink('${inviteLink}')">Link Kopyala</button>
                        </td>
                        <td><button class="delete-btn" onclick="deleteUser('${userId}')">Sil</button></td>
                    </tr>
                `;
            }
        }

        function copyLink(link) {
            navigator.clipboard.writeText(link).then(() => {
                alert("Davet Linki Kopyalandı! Bunu arkadaşına at:\\n\\n" + link);
            }).catch(err => {
                alert("Kopyalanamadı: " + err);
            });
        }

        document.getElementById('userForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const user_id = document.getElementById('user_id').value;
            const data = {
                faceit_nickname: document.getElementById('faceit_nickname').value,
                steam_id: document.getElementById('steam_id').value,
                spotify_refresh_token: "" // Yeni eklenen kullanıcıda token boştur
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
@requires_auth
def admin_panel():
    return render_template_string(ADMIN_HTML)

@app.route('/admin/users', methods=['GET'])
@requires_auth
def get_all_users():
    return jsonify(load_users())

@app.route('/admin/users/<user_id>', methods=['POST'])
@requires_auth
def save_user(user_id):
    data = request.json
    users = load_users()
    
    # Mevcut verileri koruyarak güncelleme yapalım
    existing = users.get(user_id, {})
    
    users[user_id] = {
        "faceit_nickname": data.get("faceit_nickname", existing.get("faceit_nickname", "")),
        "steam_id": data.get("steam_id", existing.get("steam_id", "")),
        "spotify_refresh_token": data.get("spotify_refresh_token", existing.get("spotify_refresh_token", ""))
    }
    save_users(users)
    return jsonify({"status": "success"})

@app.route('/admin/users/<user_id>', methods=['DELETE'])
@requires_auth
def delete_user(user_id):
    users = load_users()
    if user_id in users:
        del users[user_id]
        save_users(users)
    return jsonify({"status": "success"})


# --- SPOTIFY OAUTH FLOW (INVITE SYSTEM) ---
@app.route('/invite/<user_id>')
def spotify_invite(user_id):
    users = load_users()
    if user_id not in users:
        return "Boyle bir kullanici bulunamadi.", 404
        
    if not SPOTIFY_CLIENT_ID:
        return "SPOTIFY_CLIENT_ID eksik.", 500
        
    scope = "user-read-currently-playing"
    redirect_uri = "https://api.manikk.info/admin/spotify_callback"
    
    auth_query = {
        "response_type": "code",
        "client_id": SPOTIFY_CLIENT_ID,
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": user_id  # user_id'yi callback'e aktariyoruz
    }
    url = "https://accounts.spotify.com/authorize?" + urlencode(auth_query)
    return redirect(url)

@app.route('/admin/spotify_callback')
def spotify_callback():
    code = request.args.get('code')
    user_id = request.args.get('state')  # Hangi kullanici oldugunu anliyoruz
    
    if not code or not user_id:
        return "Gecersiz istek (Code veya State eksik).", 400
        
    users = load_users()
    if user_id not in users:
        return "Gecersiz kullanici ID.", 404
        
    redirect_uri = "https://api.manikk.info/admin/spotify_callback"
    basic_auth = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    
    try:
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {basic_auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri
            }
        )
        token_res.raise_for_status()
        token_data = token_res.json()
        
        refresh_token = token_data.get("refresh_token")
        
        # Token'i kullaniciya otomatik kaydet
        users[user_id]["spotify_refresh_token"] = refresh_token
        save_users(users)
        
        return f'''
        <html><body style="font-family: Arial; padding: 40px; background: #111; color: white; text-align: center;">
            <h1 style="color: #1DB954;">&#x2705; Basariyla Baglandi!</h1>
            <p style="font-size: 18px;">Spotify hesabiniz basariyla sisteme eklendi.</p>
            <p style="color: #aaa;">Artik dinlediginiz sarkilar sitede gorunecektir. Bu sekmeyi kapatabilirsiniz.</p>
        </body></html>
        '''
        
    except Exception as e:
        return f"Token alinamadi: {e}", 500


# --- STEAM INVENTORY API ---
@app.route('/steam/inventory/<user_id>', methods=['GET'])
def steam_inventory(user_id):
    global STEAM_CACHE
    users = load_users()
    
    if user_id not in users:
        return jsonify({"error": "Kullanici bulunamadi"}), 404
        
    steam_id = users[user_id].get("steam_id")
    if not steam_id:
        return jsonify({"error": "Kullanicinin Steam ID bilgisi yok"}), 400

    current_time = time.time()
    if user_id in STEAM_CACHE:
        cache_data = STEAM_CACHE[user_id]
        if (current_time - cache_data["time"]) < STEAM_CACHE_DURATION:
            return jsonify(cache_data["data"])

    try:
        url = f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=turkish&count=2000"
        res = requests.get(url, timeout=15)
        if res.status_code != 200:
            return jsonify({"error": f"Steam envanteri alinamadi (Kod: {res.status_code}). Gizli olabilir veya Steam engelledi."}), res.status_code
        
        data = res.json()
        if not data or not data.get("assets") or not data.get("descriptions"):
            return jsonify([])
            
        assets = data["assets"]
        descriptions = data["descriptions"]
        
        desc_map = {}
        for d in descriptions:
            key = f"{d.get('classid')}_{d.get('instanceid')}"
            desc_map[key] = d
            
        inventory_items = []
        # Ayni esyadan birden fazla varsa sadece 1 tanesini gostermek daha temiz olabilir ama kullanici belki 2 bicak seviyordur. Ayni asseti eklememek icin isim kontrolu de yapabiliriz, ya da asset map kullanabiliriz.
        seen_instance_ids = set()
        
        for asset in assets:
            classid = asset.get('classid')
            instanceid = asset.get('instanceid')
            
            # Aynı instanceid olan kopyaları atla (stackli eşyalar)
            if f"{classid}_{instanceid}" in seen_instance_ids:
                continue
            seen_instance_ids.add(f"{classid}_{instanceid}")
            
            key = f"{classid}_{instanceid}"
            desc = desc_map.get(key)
            if not desc: continue
            
            tags = desc.get("tags", [])
            item_type = next((t["internal_name"] for t in tags if t.get("category") == "Type"), "")
            rarity = next((t["internal_name"] for t in tags if t.get("category") == "Rarity"), "")
            rarity_color = next((t.get("color", "") for t in tags if t.get("category") == "Rarity"), "")
            
            # Sadece Silah, Bıçak, Eldiven, Ajan kalsın
            valid_types = ["CSGO_Type_Knife", "CSGO_Type_Weapon", "Type_Hands", "Type_CustomPlayer"]
            if not any(item_type.startswith(vt) for vt in valid_types):
                continue
                
            # Ucuz silahları gizle (Consumer/Industrial)
            if item_type.startswith("CSGO_Type_Weapon"):
                if rarity in ["rarity_common", "rarity_uncommon"]:
                    continue
                    
            item = {
                "name": desc.get("name", "Bilinmeyen Eşya"),
                "icon_url": f"https://community.cloudflare.steamstatic.com/economy/image/{desc.get('icon_url')}",
                "rarity": rarity,
                "rarity_color": f"#{rarity_color}" if rarity_color else "#ffffff",
                "type": item_type
            }
            inventory_items.append(item)
            
        def get_sort_score(item):
            t = item["type"]
            r = item["rarity"]
            score = 0
            if "Knife" in t: score += 1000
            elif "Hands" in t: score += 900
            elif "CustomPlayer" in t: score += 800
            
            if "covert" in r: score += 70
            elif "classified" in r: score += 60
            elif "restricted" in r: score += 50
            elif "milspec" in r: score += 40
            return score
            
        inventory_items.sort(key=get_sort_score, reverse=True)
        
        STEAM_CACHE[user_id] = {"data": inventory_items, "time": current_time}
        return jsonify(inventory_items)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
    
    if user_id in FACEIT_CACHE:
        cache_data = FACEIT_CACHE[user_id]
        if (current_time - cache_data["time"]) < CACHE_DURATION:
            return jsonify(cache_data["data"])
            
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
        FACEIT_CACHE[user_id] = {"data": data_to_cache, "time": current_time}
        return jsonify(data_to_cache)

    except Exception as e:
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
        if not item: return jsonify({"is_playing": False})

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
        return jsonify({"error": str(e)}), 500

# Endpoint to fetch user public profile links (Steam)
@app.route('/user_links/<user_id>', methods=['GET'])
def get_user_links(user_id):
    users = load_users()
    if user_id not in users:
        return jsonify({"error": "Kullanici bulunamadi"}), 404
        
    steam_id = users[user_id].get("steam_id")
    return jsonify({
        "steam_id": steam_id,
        "faceit_nickname": users[user_id].get("faceit_nickname")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
