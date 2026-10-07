from pathlib import Path
import re, sys, shutil

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
index=assets/'index.html'

h=index.read_text(encoding='utf-8')

if 'v1552-fixes.css' not in h:
    if '</head>' not in h: raise SystemExit('head close missing')
    h=h.replace('</head>','<link rel="stylesheet" href="v1552-fixes.css">\n</head>',1)
if 'v1552-fixes.js' not in h:
    if '</body>' not in h: raise SystemExit('body close missing')
    h=h.replace('</body>','<script src="v1552-fixes.js"></script>\n</body>',1)

# Appearance: match the supplied reference — current mode text on the left,
# supplied day/night JSON on the right, and the whole card remains one-tap toggle.
theme_button=re.compile(
    r'<button id="v1551ThemeToggle" type="button" role="switch" aria-checked="[^"]*">.*?</button>',
    re.S
)
theme_new='''<button id="v1551ThemeToggle" class="v1552ThemeCard" type="button" role="switch" aria-checked="false">
    <span class="v1552ThemeCopy">
      <b id="v1552ThemeTitle">Light Mode</b>
      <small id="v1552ThemeHint">Tap to switch to dark mode</small>
    </span>
    <span class="v155ThemeLottie lottieIcon" data-lottie="lottie/theme-v155.json" aria-hidden="true"></span>
  </button>'''
h,n=theme_button.subn(theme_new,h,count=1)
if n!=1: raise SystemExit('v15.5.1 theme button anchor missing')

index.write_text(h,encoding='utf-8')

shutil.copy('ci/v1552-fixes.css',assets/'v1552-fixes.css')
shutil.copy('ci/v1552-fixes.js',assets/'v1552-fixes.js')

print('v15.5.2 startup, Appearance and Smart Reminder polish applied')
