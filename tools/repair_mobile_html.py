from pathlib import Path
import re

p = Path("app/src/main/assets/index.html")
s = p.read_text(encoding="utf-8")

# Guarantee a real mobile viewport.
vp = '<meta name="viewport"'
if vp in s:
    s = re.sub(r'<meta\s+name=["\']viewport["\'][^>]*>', '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">', s, count=1, flags=re.I)
else:
    s = re.sub(r'(<head[^>]*>)', r'\1<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">', s, count=1, flags=re.I)

# Replace the first style block with a predictable responsive phone shell.
css = r'''<style>
:root{color-scheme:dark}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;width:100%;min-height:100%;background:#07111d;color:#fff;font-family:monospace;overflow:hidden;overscroll-behavior:none}
body{display:flex;justify-content:center;align-items:flex-start;touch-action:manipulation;padding:max(6px,env(safe-area-inset-top)) max(6px,env(safe-area-inset-right)) max(6px,env(safe-area-inset-bottom)) max(6px,env(safe-area-inset-left))}
.wrap{width:min(100%,760px);display:flex;flex-direction:column;align-items:center;gap:6px;padding:4px 0}
h1{text-align:center;font-size:clamp(13px,3.6vw,18px);line-height:1;margin:2px 0;color:#fff;flex:0 0 auto}
.screen{width:min(96vw,680px);max-width:680px;background:#101827;border:4px solid #7c4dff;padding:5px;border-radius:10px;flex:0 0 auto}
canvas{display:block;width:100%;height:auto;aspect-ratio:160/144;margin:auto;image-rendering:pixelated;image-rendering:crisp-edges;background:#63d8ff;touch-action:none}
.controls{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));width:min(94vw,420px);margin:0 auto;gap:5px;flex:0 0 auto}
button{font:700 13px monospace;padding:8px 6px;border:2px solid #00e5ff;background:#ffd54a;color:#17112e;min-height:42px;border-radius:8px;touch-action:manipulation;user-select:none;-webkit-user-select:none}
button:active{transform:translateY(2px)}
.panel{display:none;width:min(94vw,680px);max-height:34dvh;overflow:auto;background:#fff4c7;color:#17112e;border:3px solid #ff3d81;padding:8px;margin:0;border-radius:8px}
.panel button{margin:3px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:6px}
.small{font-size:11px}.status{text-align:center;font-size:10px;line-height:1.1;margin:0;color:#7fffd4}
@media (max-height:620px){h1{display:none}.wrap{gap:3px}.screen{width:min(92vw,calc((100dvh - 150px)*1.1111));padding:3px}.controls{gap:3px}button{min-height:36px;padding:5px}.status{display:none}.panel{max-height:25dvh}}
</style>'''
styles = list(re.finditer(r'<style[^>]*>.*?</style>', s, re.I|re.S))
if styles:
    m=styles[0]
    s=s[:m.start()]+css+s[m.end():]
else:
    s=s.replace("</head>",css+"</head>",1)

# Remove any JavaScript accidentally left after the HTML document.
s = re.sub(r'(</html>)\s*setInterval\(\(\)=>.*$', r'\1', s, flags=re.S)

# Keep autosave inside the script block only.
scripts=list(re.finditer(r'<script[^>]*>(.*?)</script>',s,re.I|re.S))
if len(scripts)!=1:
    raise SystemExit(f"Expected one script block before repair, found {len(scripts)}")
body=scripts[0].group(1)
body=re.sub(r'function\s+autoSave\s*\([^)]*\)\s*\{.*?\}\s*setInterval\(.*?\);', '', body, flags=re.S)
if "function autoSave(" not in body:
    body += "\nfunction autoSave(){try{localStorage.setItem('monsterbound_full_save_v2',JSON.stringify(S));}catch(e){}}\nsetInterval(()=>{if(S&&S.mode!=='title')autoSave()},15000);\n"
s=s[:scripts[0].start(1)]+body+s[scripts[0].end(1):]
if not s.rstrip().lower().endswith("</html>"):
    raise SystemExit("HTML document does not end with </html>")
p.write_text(s,encoding="utf-8")
