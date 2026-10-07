from pathlib import Path
import re, sys, shutil

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
index=assets/'index.html'
runtime=assets/'lottie-runtime.js'

h=index.read_text(encoding='utf-8')
lr=runtime.read_text(encoding='utf-8')

if 'v1554-fixes.css' not in h:
    if '</head>' not in h: raise SystemExit('head close missing')
    h=h.replace('</head>','<link rel="stylesheet" href="v1554-fixes.css">\n</head>',1)

# Revert the Appearance Theme control back to the older compact Light/JSON/Dark layout.
theme_pat=re.compile(
    r'<button id="v1551ThemeToggle" class="v1552ThemeCard" type="button" role="switch" aria-checked="[^"]*">.*?</button>',
    re.S
)
theme_old='''<button id="v1551ThemeToggle" type="button" role="switch" aria-checked="false">
    <span class="v1551ThemeSide light">Light</span>
    <span class="v155ThemeLottie lottieIcon" data-lottie="lottie/theme-v155.json" aria-hidden="true"></span>
    <span class="v1551ThemeSide dark">Dark</span>
  </button>'''
h,n=theme_pat.subn(theme_old,h,count=1)
if n!=1: raise SystemExit('v15.5.2 theme card anchor missing')

# Use the newly supplied red logout animation.
h,n=re.subn(
    r'<span class="v155LogoutLottie lottieIcon" data-lottie="lottie/logout-v155.json"',
    '<span class="v155LogoutLottie v1554LogoutLottie lottieIcon" data-lottie="lottie/logout-red-v1554.json"',
    h,
    count=1
)
if n!=1: raise SystemExit('logout lottie anchor missing')

index.write_text(h,encoding='utf-8')

# Preserve the supplied red logout colors in dark mode too.
if 'function isRedLogout(rec)' not in lr:
    anchor="function isThemeToggle(rec){return !!(rec&&rec.container&&rec.container.classList&&rec.container.classList.contains('v155ThemeLottie'));}"
    if anchor not in lr: raise SystemExit('theme runtime anchor missing')
    lr=lr.replace(
        anchor,
        anchor+"\n  function isRedLogout(rec){return !!(rec&&rec.container&&rec.container.classList&&rec.container.classList.contains('v1554LogoutLottie'));}",
        1
    )

old="cfg.container=rec.container;cfg.path=isThemeToggle(rec)?rec.originalPath:resolvedPath(rec.originalPath,rec.forceWhite);cfg.loop=false;cfg.autoplay=false;"
new="cfg.container=rec.container;cfg.path=(isThemeToggle(rec)||isRedLogout(rec))?rec.originalPath:resolvedPath(rec.originalPath,rec.forceWhite);cfg.loop=false;cfg.autoplay=false;"
if old not in lr: raise SystemExit('runtime build path anchor missing')
lr=lr.replace(old,new,1)

old="function reloadForTheme(rec){if(!rec||rec.forceWhite||!rec.container||!document.documentElement.contains(rec.container))return;clearTimer(rec);if(isThemeToggle(rec)){try{var tf=Math.max(1,Math.floor(rec.anim.totalFrames||96));rec.anim.goToAndStop(isDark()?tf-1:0,true)}catch(e){}return;}try{if(rec.anim)rec.anim.destroy()}catch(e){}buildAnim(rec,rec.delay);}"
new="function reloadForTheme(rec){if(!rec||rec.forceWhite||!rec.container||!document.documentElement.contains(rec.container))return;clearTimer(rec);if(isThemeToggle(rec)){try{var tf=Math.max(1,Math.floor(rec.anim.totalFrames||96));rec.anim.goToAndStop(isDark()?tf-1:0,true)}catch(e){}return;}if(isRedLogout(rec))return;try{if(rec.anim)rec.anim.destroy()}catch(e){}buildAnim(rec,rec.delay);}"
if old not in lr: raise SystemExit('runtime reload anchor missing')
lr=lr.replace(old,new,1)

runtime.write_text(lr,encoding='utf-8')
shutil.copy('ci/v1554-fixes.css',assets/'v1554-fixes.css')
print('v15.5.4 Theme revert, smaller loader and supplied red logout applied')
