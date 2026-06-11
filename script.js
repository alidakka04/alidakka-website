document.addEventListener('DOMContentLoaded', () => {
    fetchFaceitStats();
});

async function fetchFaceitStats() {
    try {
        const response = await fetch('/api/faceit');
        
        if (!response.ok) {
            throw new Error('API Bulunamadi veya calismiyor.');
        }
        
        const data = await response.json();
        renderFaceitData(data);
        
    } catch (error) {
        console.warn('Vercel API baglantisi basarisiz. Demo verileri gosteriliyor...', error);
        
        // Demo (Mock) Veriler - Vercel'e yuklenene kadar sitenin guzel gorunmesi ve test edilebilmesi icin
        const demoData = {
            skill_level: 10,
            faceit_elo: "?",
            average_kd: "?",
            win_rate: "?",
            recent_matches: []
        };

        // Yükleniyormuş hissi vermek için bekle
        setTimeout(() => {
            renderFaceitData(demoData);
            
            // Local'de oldugumuzu belli eden sari uyari
            const statusIndicator = document.querySelector('.status-indicator');
            if(statusIndicator) {
                statusIndicator.innerHTML = `<span class="w-2 h-2 bg-yellow-500 rounded-full shadow-[0_0_10px_#eab308] animate-pulse-fast"></span> Geçici Veriler (API Bekleniyor)`;
                statusIndicator.title = "Canlı verileriniz Vercel'e yüklenip API girildiğinde görünecektir.";
            }
        }, 800);
    }
}

function renderFaceitData(data) {
    document.getElementById('faceit-loading').classList.add('hidden');
    document.getElementById('faceit-data').classList.remove('hidden');
    
    document.getElementById('faceit-level-icon').src = `https://cdn-frontend.faceit.com/web/960/src/app/assets/images-compress/skill-icons/skill_level_${data.skill_level}_svg.svg`;
    document.getElementById('faceit-elo').textContent = data.faceit_elo;
    document.getElementById('faceit-kd').textContent = data.average_kd;
    document.getElementById('faceit-winrate').textContent = data.win_rate + '%';
    
    const matchesContainer = document.getElementById('recent-matches-container');
    const matchesList = document.getElementById('recent-matches-list');
    
    if (data.recent_matches && data.recent_matches.length > 0) {
        matchesContainer.classList.remove('hidden');
        matchesList.innerHTML = ''; // Oncekileri temizle
        
        data.recent_matches.forEach(match => {
            const isWin = match.is_win;
            const matchDiv = document.createElement('div');
            matchDiv.className = `flex justify-between items-center p-3 bg-black/40 rounded-lg border-l-4 transition-colors hover:bg-white/5 ${isWin ? 'border-green-500' : 'border-red-500'}`;
            
            let dateStr = "";
            if (match.finished_at) {
                const matchDate = new Date(match.finished_at * 1000);
                const options = { day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' };
                dateStr = matchDate.toLocaleDateString('tr-TR', options);
            }
            
            const matchKd = match.deaths > 0 ? (match.kills / match.deaths).toFixed(2) : match.kills.toFixed(2);
            
            let kdClass = "text-red-500";
            const kdValue = parseFloat(matchKd);
            if (kdValue >= 1.50) {
                kdClass = "text-yellow-400 drop-shadow-[0_0_10px_#ffcc00] font-black";
            } else if (kdValue >= 1.0) {
                kdClass = "text-green-400";
            }
            
            matchDiv.innerHTML = `
                <div>
                    <div class="font-bold text-white">${match.map}</div>
                    <div class="font-semibold text-zinc-300 inline-block">${match.score}</div>
                    ${dateStr ? `<span class="text-xs text-zinc-500 ml-2">🕒 ${dateStr}</span>` : ''}
                </div>
                <div class="text-right flex flex-col items-end justify-center">
                    <div class="text-lg font-extrabold text-white">${match.kills}/${match.deaths} <span class="text-xs ml-1 ${kdClass}">${matchKd} K/D</span></div>
                    ${match.adr !== "?" ? `<div class="text-sm text-zinc-400 mt-0.5">${match.adr} <span class="text-[0.7em] text-zinc-500">ADR</span></div>` : ''}
                </div>
            `;
            matchesList.appendChild(matchDiv);
        });
    }
}

// --- Spotify Widget Logic ---
const spotifyWidget = document.getElementById('spotify-widget');
const spotifyCover = document.getElementById('spotify-cover');
const spotifyTitle = document.getElementById('spotify-title');
const spotifyArtist = document.getElementById('spotify-artist');
const spotifyLink = document.getElementById('spotify-link');
const spotifyProgressBar = document.getElementById('spotify-progress-bar');
const spotifyTimeCurrent = document.getElementById('spotify-time-current');
const spotifyTimeTotal = document.getElementById('spotify-time-total');

function formatTime(ms) {
    if (!ms) return "0:00";
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

async function updateSpotify() {
    try {
        const response = await fetch('/api/spotify');
        if (!response.ok) return;
        const data = await response.json();

        if (data && data.is_playing) {
            spotifyWidget.classList.remove('hidden');
            // Small delay to allow display block to apply before opacity transition
            setTimeout(() => spotifyWidget.setAttribute('data-active', 'true'), 10);
            
            spotifyCover.src = data.albumImageUrl;
            spotifyTitle.textContent = data.title;
            spotifyArtist.textContent = data.artist;
            spotifyLink.href = data.songUrl;
            
            spotifyTimeCurrent.textContent = formatTime(data.progress_ms);
            spotifyTimeTotal.textContent = formatTime(data.duration_ms);
            
            const progressPercent = (data.progress_ms / data.duration_ms) * 100;
            spotifyProgressBar.style.width = `${progressPercent}%`;
        } else {
            spotifyWidget.removeAttribute('data-active');
            setTimeout(() => spotifyWidget.classList.add('hidden'), 500);
        }
    } catch (error) {
        console.error('Error fetching Spotify data:', error);
    }
}

// Check Spotify API every 2.5 seconds
setInterval(updateSpotify, 2500);
updateSpotify();

// --- 3D Parallax Effect for Hardware ---
const specItems = document.querySelectorAll('.spec-item');

specItems.forEach(item => {
    item.addEventListener('mousemove', (e) => {
        const rect = item.getBoundingClientRect();
        const x = e.clientX - rect.left; // x position within the element.
        const y = e.clientY - rect.top;  // y position within the element.
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        // Calculate rotation degrees (max 10 degrees)
        const rotateX = ((y - centerY) / centerY) * -10;
        const rotateY = ((x - centerX) / centerX) * 10;
        
        // Apply 3D transform
        item.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05)`;
        
        // Make the image inside pop out
        const imgContainer = item.querySelector('.spec-img-container');
        if (imgContainer) {
            imgContainer.style.transform = 'translateZ(40px)';
        }
    });
    
    item.addEventListener('mouseleave', () => {
        // Reset transform on mouse leave
        item.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
        
        const imgContainer = item.querySelector('.spec-img-container');
        if (imgContainer) {
            imgContainer.style.transform = 'translateZ(0px)';
        }
    });
});
