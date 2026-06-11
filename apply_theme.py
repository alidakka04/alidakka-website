import os

def replace_in_file(filepath, replacements):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

index_replacements = [
    ('<html lang="tr" class="dark">', '<html lang="tr">'),
    ("faceit: '#ff5500'", "faceit: '#0ea5e9'"),
    ("faceithover: '#ff7733'", "faceithover: '#0284c7'"),
    ("background: '#09090b'", "background: '#f8fafc'"),
    ("surface: '#18181b'", "surface: '#ffffff'"),
    ("@apply bg-surface/30 backdrop-blur-2xl border border-white/5 rounded-[2rem] shadow-2xl;", "@apply bg-white/70 backdrop-blur-2xl border border-slate-200/60 rounded-[2rem] shadow-xl;"),
    ("@apply bg-white/[0.02] border border-white/5 rounded-2xl hover:bg-white/[0.04] hover:border-white/10 hover:shadow-xl;", "@apply bg-slate-50/50 border border-slate-200/50 rounded-2xl hover:bg-white hover:border-sky-200 hover:shadow-lg;"),
    ("@apply bg-clip-text text-transparent bg-gradient-to-r from-white via-zinc-200 to-zinc-500;", "@apply bg-clip-text text-transparent bg-gradient-to-r from-slate-900 via-slate-600 to-slate-400;"),
    ("color: #fff;", "color: #0f172a;"),
    ("text-shadow: 0 0 30px rgba(255, 255, 255, 0.6);", "text-shadow: 0 0 30px rgba(14, 165, 233, 0.4);"),
    ("background-color: #09090b;", "background-color: #f8fafc;"),
    ("color: #f4f4f5;", "color: #0f172a;"),
    ("background: #09090b;", "background: #f1f5f9;"),
    ("background: #27272a;", "background: #cbd5e1;"),
    ("background: #3f3f46;", "background: #94a3b8;"),
    ("selection:bg-faceit/30 selection:text-white", "selection:bg-faceit/20 selection:text-slate-900"),
    ("bg-zinc-600/10", "bg-sky-300/20"),
    ("bg-white/5 text-white border border-white/10 hover:bg-white hover:text-black", "bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 hover:text-slate-900 shadow-sm"),
    ("text-white", "text-slate-900"),
    ("text-zinc-400", "text-slate-500"),
    ("text-zinc-500", "text-slate-400"),
    ("text-zinc-200", "text-slate-700"),
    ("text-zinc-300", "text-slate-600"),
    ("border-white/5", "border-black/5"),
    ("border-white/10", "border-black/10"),
    ("border-zinc-600", "border-slate-300"),
    ("shadow-[0_0_20px_rgba(255,85,0,0.4)]", "shadow-[0_0_20px_rgba(14,165,233,0.4)]"),
    ("shadow-[0_0_30px_rgba(255,85,0,0.7)]", "shadow-[0_0_30px_rgba(14,165,233,0.7)]"),
    ("bg-surface/80", "bg-white/90"),
]

script_replacements = [
    ("border-emerald-500/50 hover:border-emerald-500", "border-emerald-500/50 hover:border-emerald-600 bg-white shadow-sm"),
    ("border-red-500/50 hover:border-red-500", "border-red-500/50 hover:border-red-600 bg-white shadow-sm"),
    ("text-red-400", "text-red-500"),
    ("text-yellow-400", "text-amber-500"),
    ("text-emerald-400", "text-emerald-500"),
    ("text-white", "text-slate-900"),
    ("bg-white/5", "bg-slate-100"),
    ("text-zinc-300", "text-slate-600"),
    ("border-white/5", "border-slate-200"),
    ("text-zinc-500", "text-slate-500"),
    ("text-zinc-400", "text-slate-500"),
    ("drop-shadow-[0_0_10px_#ffcc00]", "drop-shadow-[0_0_5px_rgba(245,158,11,0.5)]"),
]

replace_in_file('index.html', index_replacements)
replace_in_file('script.js', script_replacements)
print('Done')
