import re

with open('script.js', 'r', encoding='utf-8') as f:
    content = f.read()

localization_logic = """
// Localization Logic
const supportedLangs = ['tr', 'en', 'de', 'ru', 'da', 'uk', 'fr', 'ro', 'pt'];
let currentLang = 'en'; // default fallback

// Get browser language (e.g., 'tr-TR', 'en-US', 'de', 'pt-BR')
const browserLang = navigator.language || navigator.userLanguage;
const baseLang = browserLang.split('-')[0].toLowerCase();

if (supportedLangs.includes(baseLang)) {
    currentLang = baseLang;
}

// Function to translate keys
function t(key) {
    if (translations[currentLang] && translations[currentLang][key]) {
        return translations[currentLang][key];
    }
    return translations['en'][key] || key;
}

// Apply translations to DOM
function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[currentLang] && translations[currentLang][key]) {
            el.innerText = translations[currentLang][key];
        } else if (translations['en'][key]) {
            el.innerText = translations['en'][key];
        }
    });
}

// Run translation on load
document.addEventListener('DOMContentLoaded', applyTranslations);

"""

# Prepend localization logic to script.js
if "// Localization Logic" not in content:
    content = localization_logic + content

# Update JS strings to use t('...')
content = content.replace("? 'Galibiyet'", "? t('win')")
content = content.replace(": 'Mağlubiyet'", ": t('loss')")
content = content.replace("Skor: ${match.score}", "${t('score')}: ${match.score}")

with open('script.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("script.js updated successfully.")
