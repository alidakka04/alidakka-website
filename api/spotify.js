export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    
    const client_id = process.env.SPOTIFY_CLIENT_ID;
    const client_secret = process.env.SPOTIFY_CLIENT_SECRET;
    const refresh_token = process.env.SPOTIFY_REFRESH_TOKEN;
    
    if (!client_id || !client_secret || !refresh_token) {
        return res.status(500).json({ error: 'Missing Spotify credentials' });
    }

    const basic = Buffer.from(`${client_id}:${client_secret}`).toString('base64');
    const TOKEN_ENDPOINT = `https://accounts.spotify.com/api/token`;
    const NOW_PLAYING_ENDPOINT = `https://api.spotify.com/v1/me/player/currently-playing`;

    try {
        // 1. Get access token
        const tokenResponse = await fetch(TOKEN_ENDPOINT, {
            method: 'POST',
            headers: {
                Authorization: `Basic ${basic}`,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                grant_type: 'refresh_token',
                refresh_token,
            }),
        });
        
        const tokenData = await tokenResponse.json();
        const access_token = tokenData.access_token;
        
        if (!access_token) {
             return res.status(500).json({ error: 'Failed to get access token' });
        }

        // 2. Fetch currently playing song
        const response = await fetch(NOW_PLAYING_ENDPOINT, {
            headers: {
                Authorization: `Bearer ${access_token}`,
            },
        });

        if (response.status === 204 || response.status > 400) {
            return res.status(200).json({ is_playing: false });
        }

        const song = await response.json();

        if (song.item === null) {
            return res.status(200).json({ is_playing: false });
        }

        const is_playing = song.is_playing;
        const title = song.item.name;
        const artist = song.item.artists.map((_artist) => _artist.name).join(', ');
        const album = song.item.album.name;
        const albumImageUrl = song.item.album.images[0].url;
        const songUrl = song.item.external_urls.spotify;
        const progress_ms = song.progress_ms;
        const duration_ms = song.item.duration_ms;

        return res.status(200).json({
            is_playing,
            title,
            artist,
            album,
            albumImageUrl,
            songUrl,
            progress_ms,
            duration_ms
        });
        
    } catch (error) {
        console.error(error);
        return res.status(500).json({ error: error.message });
    }
}
