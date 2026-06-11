import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    '<title>Manikk | Portfolyo</title>': '<title data-i18n="title">Manikk | Portfolyo</title>',
    'Faceit Profili\n                </a>': '<span data-i18n="faceit_profile">Faceit Profili</span>\n                </a>',
    'Steam Profili\n                </a>': '<span data-i18n="steam_profile">Steam Profili</span>\n                </a>',
    '<h2 class="text-3xl font-bold text-white mb-2 tracking-tight">İstatistikler</h2>': '<h2 class="text-3xl font-bold text-white mb-2 tracking-tight" data-i18n="stats_title">İstatistikler</h2>',
    '<p class="text-zinc-400 text-sm">Faceit API ile canlı senkronizasyon</p>': '<p class="text-zinc-400 text-sm" data-i18n="stats_desc">Faceit API ile canlı senkronizasyon</p>',
    '</span> Canlı\n                </div>': '</span> <span data-i18n="live">Canlı</span>\n                </div>',
    '<p class="text-zinc-500 font-medium">Oyuncu verileri alınıyor...</p>': '<p class="text-zinc-500 font-medium" data-i18n="loading_data">Oyuncu verileri alınıyor...</p>',
    'group-hover:text-zinc-300 transition-colors">Seviye</span>': 'group-hover:text-zinc-300 transition-colors" data-i18n="level">Seviye</span>',
    'group-hover:text-zinc-300 transition-colors">Elo Puanı</span>': 'group-hover:text-zinc-300 transition-colors" data-i18n="elo">Elo Puanı</span>',
    'group-hover:text-zinc-300 transition-colors">K/D Oranı</span>': 'group-hover:text-zinc-300 transition-colors" data-i18n="kd_ratio">K/D Oranı</span>',
    'group-hover:text-zinc-300 transition-colors">Kazanma Oranı</span>': 'group-hover:text-zinc-300 transition-colors" data-i18n="win_rate">Kazanma Oranı</span>',
    '<i class="fa-solid fa-clock-rotate-left"></i> Son Maçlar\n                </h3>': '<i class="fa-solid fa-clock-rotate-left"></i> <span data-i18n="recent_matches">Son Maçlar</span>\n                </h3>',
    '<h2 class="text-3xl font-bold text-white mb-2 tracking-tight">Ekipmanlar</h2>': '<h2 class="text-3xl font-bold text-white mb-2 tracking-tight" data-i18n="equipment_title">Ekipmanlar</h2>',
    '<p class="text-zinc-400 text-sm">Bilgisayar ve donanım yapılandırması</p>': '<p class="text-zinc-400 text-sm" data-i18n="equipment_desc">Bilgisayar ve donanım yapılandırması</p>',
    '<i class="fa-solid fa-microchip"></i> Sistem Bileşenleri\n                    </h3>': '<i class="fa-solid fa-microchip"></i> <span data-i18n="pc_build">Sistem Bileşenleri</span>\n                    </h3>',
    'font-bold mb-1.5">İşlemci</span>': 'font-bold mb-1.5" data-i18n="cpu">İşlemci</span>',
    'font-bold mb-1.5">Ekran Kartı</span>': 'font-bold mb-1.5" data-i18n="gpu">Ekran Kartı</span>',
    'font-bold mb-1.5">Anakart</span>': 'font-bold mb-1.5" data-i18n="motherboard">Anakart</span>',
    'font-bold mb-1.5">Bellek</span>': 'font-bold mb-1.5" data-i18n="ram">Bellek</span>',
    'font-bold mb-1.5">Soğutma</span>': 'font-bold mb-1.5" data-i18n="cooler">Soğutma</span>',
    'font-bold mb-1.5">Kasa</span>': 'font-bold mb-1.5" data-i18n="case">Kasa</span>',
    'font-bold mb-1.5">Depolama</span>': 'font-bold mb-1.5" data-i18n="storage">Depolama</span>',
    'font-bold mb-1.5">Fanlar</span>': 'font-bold mb-1.5" data-i18n="fans">Fanlar</span>',
    'font-bold mb-1.5">Ana Monitör</span>': 'font-bold mb-1.5" data-i18n="monitor1">Ana Monitör</span>',
    'font-bold mb-1.5">İkinci Monitör</span>': 'font-bold mb-1.5" data-i18n="monitor2">İkinci Monitör</span>',
    '<i class="fa-solid fa-headphones"></i> Çevre Birimleri\n                    </h3>': '<i class="fa-solid fa-headphones"></i> <span data-i18n="peripherals">Çevre Birimleri</span>\n                    </h3>',
    'font-bold mb-1.5">Mouse</span>': 'font-bold mb-1.5" data-i18n="mouse">Mouse</span>',
    'font-bold mb-1.5">Keyboard</span>': 'font-bold mb-1.5" data-i18n="keyboard">Keyboard</span>',
    'font-bold mb-1.5">Headset</span>': 'font-bold mb-1.5" data-i18n="headset">Headset</span>',
    'font-bold mb-1.5">Mousepad</span>': 'font-bold mb-1.5" data-i18n="mousepad">Mousepad</span>',
    'font-bold mb-1.5">Skatez</span>': 'font-bold mb-1.5" data-i18n="skates">Skatez</span>',
    'font-bold mb-1.5">Koltuk</span>': 'font-bold mb-1.5" data-i18n="chair">Koltuk</span>',
    '<i class="fab fa-spotify animate-pulse"></i> Şu An Çalıyor\n            </div>': '<i class="fab fa-spotify animate-pulse"></i> <span data-i18n="now_playing">Şu An Çalıyor</span>\n            </div>',
    'id="spotify-title" class="text-[0.95rem] font-bold text-white whitespace-nowrap overflow-hidden text-ellipsis leading-tight mb-0.5">Başlık</div>': 'id="spotify-title" class="text-[0.95rem] font-bold text-white whitespace-nowrap overflow-hidden text-ellipsis leading-tight mb-0.5" data-i18n="title_placeholder">Başlık</div>',
    'id="spotify-artist" class="text-[0.8rem] text-zinc-400 whitespace-nowrap overflow-hidden text-ellipsis mb-2">Sanatçı</div>': 'id="spotify-artist" class="text-[0.8rem] text-zinc-400 whitespace-nowrap overflow-hidden text-ellipsis mb-2" data-i18n="artist_placeholder">Sanatçı</div>',
    '<script src="script.js"></script>': '<script src="translations.js"></script>\n    <script src="script.js"></script>'
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("index.html updated successfully.")
