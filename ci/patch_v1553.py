from pathlib import Path
import sys, shutil

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
index=assets/'index.html'
h=index.read_text(encoding='utf-8')

if 'v1553-fixes.css' not in h:
    if '</head>' not in h: raise SystemExit('missing head close')
    h=h.replace('</head>','<link rel="stylesheet" href="v1553-fixes.css">\n</head>',1)
if 'v1553-fixes.js' not in h:
    if '</body>' not in h: raise SystemExit('missing body close')
    h=h.replace('</body>','<script src="v1553-fixes.js"></script>\n</body>',1)

for anchor in ('id="settingsLogoutBtn"','v155LogoutLottie','id="v1551ThemeToggle"','class="v154BootLottie'):
    if anchor not in h: raise SystemExit('expected UI element missing: '+anchor)

index.write_text(h,encoding='utf-8')
shutil.copy('ci/v1553-fixes.css',assets/'v1553-fixes.css')
shutil.copy('ci/v1553-fixes.js',assets/'v1553-fixes.js')

print('v15.5.3 red Logout, direct Theme JSON touch and responsive loading art applied')
