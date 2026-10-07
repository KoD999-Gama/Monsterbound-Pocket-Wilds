from pathlib import Path
import re, subprocess

p=Path("app/src/main/assets/index.html")
s=p.read_text(encoding="utf-8")
scripts=re.findall(r"<script[^>]*>(.*?)</script>",s,re.I|re.S)
assert len(scripts)==1, f"expected exactly 1 script block, got {len(scripts)}"
assert re.search(r'<meta[^>]+name=["\']viewport["\']',s,re.I), "viewport meta missing"
assert "function autoSave(" in scripts[0], "autosave function missing"
assert "</html>" in s.lower() and s.rstrip().lower().endswith("</html>"), "document ending invalid"
Path("/tmp/monsterbound.js").write_text(scripts[0],encoding="utf-8")
subprocess.run(["node","--check","/tmp/monsterbound.js"],check=True)
print("HTML/JS validation passed:",len(s.encode("utf-8")),"bytes")
