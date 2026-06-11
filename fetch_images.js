const fs = require('fs');
const https = require('https');

const queries = [
    { name: 'islemci.png', q: 'AMD RYZEN 5 7600X' },
    { name: 'ekran-karti.png', q: 'ASUS PRIME RTX 5070 WHITE' },
    { name: 'anakart.png', q: 'MSI B850M GAMING PLUS WHITE' },
    { name: 'ram.png', q: 'LEXAR ARES 16 GB 6400 MHz WHITE RAM' },
    { name: 'sogutucu.png', q: 'ASUS MAX Gaming LC 360mm ARGB LCD White' },
    { name: 'kasa.png', q: 'BITFENIX MH100 WHITE pc case' },
    { name: 'ssd.png', q: 'TEAM T-FORCE 1TB SSD' },
    { name: 'fan.png', q: 'LIAN LI UNI FAN CL Wireless White' },
    { name: 'monitor1.png', q: 'AOC 310 Hz 0.3 MS FAST IPS monitor' },
    { name: 'monitor2.png', q: 'Casper Excalibur 200 Hz 1ms FAST IPS' },
    { name: 'mouse.png', q: 'LOGITECH G PRO X SUPERLIGHT 2 WHITE' },
    { name: 'klavye.png', q: 'LOGITECH G515 TKL WHITE' },
    { name: 'kulaklik.png', q: 'LOGITECH G733 WHITE' },
    { name: 'mousepad.png', q: 'Wraith Spirit of Aim Pro Hybrid' },
    { name: 'skatez.png', q: 'Hoverpad V3' },
    { name: 'koltuk.png', q: 'Hawk Fab c5 White Fabric gaming chair' }
];

if (!fs.existsSync('ekipmanlar')) fs.mkdirSync('ekipmanlar');

async function download() {
    for (const item of queries) {
        console.log(`Searching: ${item.q}`);
        const url = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(item.q + " product image")}`;
        
        await new Promise(resolve => {
            https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    const match = data.match(/src="\/\/external-content\.duckduckgo\.com\/iu\/\?u=([^&"]+)/);
                    if (match && match[1]) {
                        const imgUrl = decodeURIComponent(match[1]);
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
        
        // Wait 2 sec
        await new Promise(r => setTimeout(r, 2000));
    }
}

download();
