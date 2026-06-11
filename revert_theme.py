import os

def replace_in_file(filepath, replacements):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

index_replacements = [
    ('<html lang="tr">', '<html lang="tr" class="dark">'),
    ("background: '#f8fafc'", "background: '#09090b'"),
    ("surface: '#ffffff'", "surface: '#18181b'"),
    ("@apply bg-white/70 backdrop-blur-2xl border border-slate-200/60 rounded-[2rem] shadow-xl;", "@apply bg-surface/30 backdrop-blur-2xl border border-white/5 rounded-[2rem] shadow-2xl;"),
    ("@apply bg-slate-50/50 border border-slate-200/50 rounded-2xl hover:bg-white hover:border-sky-200 hover:shadow-lg;", "@apply bg-white/[0.02] border border-white/5 rounded-2xl hover:bg-white/[0.04] hover:border-white/10 hover:shadow-xl;"),
    ("@apply bg-clip-text text-transparent bg-gradient-to-r from-slate-900 via-slate-600 to-slate-400;", "@apply bg-clip-text text-transparent bg-gradient-to-r from-white via-zinc-200 to-zinc-500;"),
    ("color: #0f172a;", "color: #fff;"),
    ("background-color: #f8fafc;", "background-color: #09090b;"),
    ("background: #f1f5f9;", "background: #09090b;"),
    ("background: #cbd5e1;", "background: #27272a;"),
    ("background: #94a3b8;", "background: #3f3f46;"),
    ("selection:bg-faceit/20 selection:text-slate-900", "selection:bg-faceit/30 selection:text-white"),
    ("bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 hover:text-slate-900 shadow-sm", "bg-white/5 text-white border border-white/10 hover:bg-white hover:text-black"),
    ("text-slate-900", "text-white"),
    ("text-slate-500", "text-zinc-400"),
    ("text-slate-400", "text-zinc-500"),
    ("text-slate-700", "text-zinc-200"),
    ("text-slate-600", "text-zinc-300"),
    ("border-black/5", "border-white/5"),
    ("border-black/10", "border-white/10"),
    ("border-slate-300", "border-zinc-600"),
    ("bg-white/90", "bg-surface/80"),
]

script_replacements = [
    ("border-emerald-500/50 hover:border-emerald-600 bg-white shadow-sm", "border-emerald-500/50 hover:border-emerald-500"),
    ("border-red-500/50 hover:border-red-600 bg-white shadow-sm", "border-red-500/50 hover:border-red-500"),
    ("text-red-500", "text-red-400"),
    ("text-amber-500", "text-yellow-400"),
    ("text-emerald-500", "text-emerald-400"),
    ("text-slate-900", "text-white"),
    ("bg-slate-100", "bg-white/5"),
    ("text-slate-600", "text-zinc-300"),
    ("border-slate-200", "border-white/5"),
    ("text-slate-500", "text-zinc-400"),
]

replace_in_file('index.html', index_replacements)
replace_in_file('script.js', script_replacements)

# Manual fix for body color
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()
    content = content.replace("body {\n        background-color: #09090b;\n        color: #fff;\n", "body {\n        background-color: #09090b;\n        color: #f4f4f5;\n")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done reverting theme')
