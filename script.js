document.addEventListener('DOMContentLoaded', () => {
    fetchFaceitStats();
});

async function fetchFaceitStats() {
    try {
        const response = await fetch('https://api.faceit.com/users/v1/nicknames/Manikk');
        
        if (!response.ok) {
            throw new Error('API Bulunamadi veya calismiyor.');
        }
        
        const data = await response.json();
        const cs2Data = data.payload.games.cs2;
        
        renderFaceitData({
            skill_level: cs2Data.skill_level,
            faceit_elo: cs2Data.faceit_elo
        });
        
    } catch (error) {
        console.warn('Faceit API baglantisi basarisiz. Demo verileri gosteriliyor...', error);
        
        // Demo (Mock) Veriler
        const demoData = {
            skill_level: 10,
            faceit_elo: "?"
        };

        // Yükleniyormuş hissi vermek için bekle
        setTimeout(() => {
            renderFaceitData(demoData);
            
            // Local'de oldugumuzu belli eden sari uyari
            const statusIndicator = document.querySelector('.status-indicator');
            if(statusIndicator) {
                statusIndicator.innerHTML = `<span class="w-2 h-2 bg-yellow-500 rounded-full shadow-[0_0_10px_#eab308] animate-pulse-fast"></span> Bağlantı Hatası`;
                statusIndicator.title = "Faceit verileri çekilemedi.";
            }
        }, 800);
    }
}

function renderFaceitData(data) {
    document.getElementById('faceit-loading').classList.add('hidden');
    document.getElementById('faceit-data').classList.remove('hidden');
    
    document.getElementById('faceit-level-icon').src = `https://cdn-frontend.faceit.com/web/960/src/app/assets/images-compress/skill-icons/skill_level_${data.skill_level}_svg.svg`;
    document.getElementById('faceit-elo').textContent = data.faceit_elo;
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
