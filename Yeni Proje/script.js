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
                statusIndicator.innerHTML = `<span class="pulse" style="background-color: #ffaa00; box-shadow: 0 0 10px #ffaa00;"></span> Geçici Veriler (API Bekleniyor)`;
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
            matchDiv.className = `match-item ${isWin ? 'win' : 'loss'}`;
            
            matchDiv.innerHTML = `
                <div>
                    <div class="match-map">${match.map}</div>
                    <div class="match-score">${match.score}</div>
                </div>
                <div class="match-kd">
                    ${match.kills}/${match.deaths} <span style="font-size:0.7em; color:#aaa; font-weight:400;">K/D</span>
                </div>
            `;
            matchesList.appendChild(matchDiv);
        });
    }
}
