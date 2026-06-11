document.addEventListener('DOMContentLoaded', () => {
    fetchFaceitStats();
});

async function fetchFaceitStats() {
    try {
        const response = await fetch('http://192.168.1.5:5000/faceit');
        
        if (!response.ok) {
            throw new Error('API Bulunamadı veya çalışmıyor.');
        }
        
        const data = await response.json();
        renderFaceitData(data);
        
    } catch (error) {
        console.warn('Faceit API bağlantısı başarısız. Faceit bölümü tamamen gizleniyor...', error);
        const faceitSection = document.getElementById('faceit-section');
        if (faceitSection) {
            faceitSection.classList.add('hidden');
        }
    }
}

function renderFaceitData(data) {
    document.getElementById('faceit-loading').classList.add('hidden');
    document.getElementById('faceit-data').classList.remove('hidden');
    
    document.getElementById('faceit-level-icon').src = `https://cdn-frontend.faceit.com/web/960/src/app/assets/images-compress/skill-icons/skill_level_${data.skill_level}_svg.svg`;
    document.getElementById('faceit-elo').textContent = data.faceit_elo;
    
    const kdEl = document.getElementById('faceit-kd');
    if (kdEl) kdEl.textContent = data.average_kd;
    
    const winrateEl = document.getElementById('faceit-winrate');
    if (winrateEl) winrateEl.textContent = data.win_rate + '%';
    
    const matchesContainer = document.getElementById('recent-matches-container');
    const matchesList = document.getElementById('recent-matches-list');
    
    if (matchesContainer && data.recent_matches && data.recent_matches.length > 0) {
        matchesContainer.classList.remove('hidden');
        matchesList.innerHTML = ''; // Öncekileri temizle
        
        data.recent_matches.forEach(match => {
            const isWin = match.is_win;
            const matchDiv = document.createElement('div');
            matchDiv.className = `glass-card p-4 flex justify-between items-center border-l-4 ${isWin ? 'border-emerald-500/50 hover:border-emerald-600 bg-white shadow-sm' : 'border-red-500/50 hover:border-red-600 bg-white shadow-sm'}`;
            
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
                kdClass = "text-amber-500 drop-shadow-[0_0_5px_rgba(245,158,11,0.5)] font-black";
            } else if (kdValue >= 1.0) {
                kdClass = "text-emerald-500";
            }
            
            matchDiv.innerHTML = `
                <div class="flex flex-col">
                    <div class="flex items-center gap-3">
                        <span class="font-bold text-slate-900 text-lg">${match.map}</span>
                        <span class="font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-sm border border-slate-200">${match.score}</span>
                    </div>
                    ${dateStr ? `<span class="text-[11px] text-slate-500 mt-1 font-medium tracking-wide">🕒 ${dateStr}</span>` : ''}
                </div>
                <div class="text-right flex flex-col items-end justify-center">
                    <div class="text-xl font-black text-slate-900 tracking-tight">${match.kills}<span class="text-slate-500 font-medium text-sm mx-0.5">/</span>${match.deaths} <span class="text-xs ml-2 ${kdClass}">${matchKd} K/D</span></div>
                    ${match.adr !== "?" ? `<div class="text-xs text-slate-500 mt-1 font-medium">${match.adr} <span class="text-[9px] text-slate-500 uppercase tracking-widest">ADR</span></div>` : ''}
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
        const response = await fetch('http://192.168.1.5:5000/spotify');
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
const specItems = document.querySelectorAll('.glass-card');

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
        const imgContainer = item.querySelector('img');
        if (imgContainer) {
            imgContainer.style.transform = 'translateZ(40px)';
        }
    });
    
    item.addEventListener('mouseleave', () => {
        // Reset transform on mouse leave
        item.style.transform = '';
        
        const imgContainer = item.querySelector('img');
        if (imgContainer) {
            imgContainer.style.transform = '';
        }
    });
});
