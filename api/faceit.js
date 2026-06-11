export default async function handler(req, res) {
    // Tarayici uzerinden erisime izin ver (CORS)
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    
    // Faceit kullanici adiniz
    const NICKNAME = 'Manikk';
    
    // Vercel Environment Variables uzerinden API Key alinir
    // (Vercel paneline FACEIT_API_KEY eklenmelidir)
    const API_KEY = process.env.FACEIT_API_KEY;
    
    if (!API_KEY) {
        return res.status(500).json({ error: 'FACEIT_API_KEY bulunamadi. Lutfen Vercel ortam degiskenlerine ekleyin.' });
    }

    const headers = {
        'Authorization': `Bearer ${API_KEY}`,
        'Accept': 'application/json'
    };

    try {
        // 1. Oyuncu bilgilerini al
        const playerRes = await fetch(`https://open.faceit.com/data/v4/players?nickname=${NICKNAME}`, { headers });
        if (!playerRes.ok) throw new Error('Oyuncu bulunamadi');
        const playerData = await playerRes.json();
        
        const playerId = playerData.player_id;
        const cs2Data = playerData.games.cs2 || {}; // Eger hic CS2 oynamamissa hata vermemesi icin

        // 2. Oyuncu Genel CS2 Istatistiklerini (K/D, Win Rate) al
        const statsRes = await fetch(`https://open.faceit.com/data/v4/players/${playerId}/stats/cs2`, { headers });
        let average_kd = "-";
        let win_rate = "-";
        
        if (statsRes.ok) {
            const statsData = await statsRes.json();
            average_kd = statsData.lifetime["Average K/D Ratio"] || "-";
            win_rate = statsData.lifetime["Win Rate %"] || "-";
        }

        // 3. Son 5 macin gecmisini al
        const historyRes = await fetch(`https://open.faceit.com/data/v4/players/${playerId}/history?game=cs2&offset=0&limit=5`, { headers });
        const recent_matches = [];
        
        if (historyRes.ok) {
            const historyData = await historyRes.json();
            
            // Her mac icin detaylari cekip Kill/Death bulalim
            const matchPromises = historyData.items.map(async (item) => {
                const matchId = item.match_id;
                const finishedAt = item.finished_at; // Unix timestamp
                
                try {
                    const matchStatsRes = await fetch(`https://open.faceit.com/data/v4/matches/${matchId}/stats`, { headers });
                    if (!matchStatsRes.ok) return null;
                    const matchStatsData = await matchStatsRes.json();
                    
                    let pKills = 0;
                    let pDeaths = 0;
                    let pADR = "?";
                    let isWin = false;
                    let map = "Unknown";
                    let score = "";
                    
                    if (matchStatsData.rounds && matchStatsData.rounds.length > 0) {
                        const round = matchStatsData.rounds[0];
                        map = round.round_stats.Map;
                        score = round.round_stats.Score;
                        
                        // Hangi takimda oldugunu bul ve skorlari kendi lehine dondur
                        let playerTeamScore = "";
                        let enemyTeamScore = "";
                        
                        for (const team of round.teams) {
                            const playerFound = team.players.find(p => p.player_id === playerId);
                            if (playerFound) {
                                pKills = playerFound.player_stats.Kills;
                                pDeaths = playerFound.player_stats.Deaths;
                                pADR = playerFound.player_stats.ADR || "?";
                                isWin = team.team_stats["Team Win"] === "1";
                                playerTeamScore = team.team_stats["Final Score"];
                            } else {
                                enemyTeamScore = team.team_stats["Final Score"];
                            }
                        }
                        
                        if (playerTeamScore !== undefined && enemyTeamScore !== undefined) {
                            score = `${playerTeamScore} / ${enemyTeamScore}`;
                        }
                    }
                    
                    return {
                        match_id: matchId,
                        is_win: isWin,
                        map: map,
                        score: score,
                        kills: pKills,
                        deaths: pDeaths,
                        adr: pADR,
                        finished_at: finishedAt
                    };
                } catch (e) {
                    return null;
                }
            });
            
            const resolvedMatches = await Promise.all(matchPromises);
            recent_matches.push(...resolvedMatches.filter(m => m !== null));
        }

        // Sonuclari geri dondur
        res.status(200).json({
            skill_level: cs2Data.skill_level || 1,
            faceit_elo: cs2Data.faceit_elo || '-',
            average_kd,
            win_rate,
            recent_matches
        });

    } catch (error) {
        console.error(error);
        res.status(500).json({ error: error.message });
    }
}
