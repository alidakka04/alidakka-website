const fs = require('fs');
const https = require('https');

const item = { name: 'kulaklik.png', q: 'Logitech G733 White headset transparent png' };

async function download() {
    console.log(`Searching: ${item.q}`);
    const url = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(item.q)}`;
    
    await new Promise(resolve => {
        https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' } }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                // Try to find the second or third image in case the first is bad
                const matches = [...data.matchAll(/src="\/\/external-content\.duckduckgo\.com\/iu\/\?u=([^&"]+)/g)];
                if (matches && matches.length > 0) {
                    const imgUrl = decodeURIComponent(matches[0][1]);
                    console.log(`Found: ${imgUrl}`);
                    https.get(imgUrl, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (imgRes) => {
                        if (imgRes.statusCode === 200) {
                            const file = fs.createWriteStream(`ekipmanlar/${item.name}`);
                            imgRes.pipe(file);
                            file.on('finish', () => {
                                console.log(`Saved ${item.name}`);
                                file.close();
                                resolve();
                            });
                        } else {
                            console.log(`Failed to download image ${imgRes.statusCode}`);
                            resolve();
                        }
                    }).on('error', resolve);
                } else {
                    console.log('No image found');
                    resolve();
                }
            });
        }).on('error', resolve);
    });
}

download();
