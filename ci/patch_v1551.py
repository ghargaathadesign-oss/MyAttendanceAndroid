from pathlib import Path
import re, sys, shutil

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
index=assets/'index.html'
app=assets/'app.js'
runtime=assets/'lottie-runtime.js'

h=index.read_text(encoding='utf-8')
s=app.read_text(encoding='utf-8')
lr=runtime.read_text(encoding='utf-8')

# v15.5.1 assets
if 'v1551-fixes.css' not in h:
    if '</head>' not in h: raise SystemExit('head close missing')
    h=h.replace('</head>','<link rel="stylesheet" href="v1551-fixes.css">\n</head>',1)
if 'v1551-fixes.js' not in h:
    if '</body>' not in h: raise SystemExit('body close missing')
    h=h.replace('</body>','<script src="v1551-fixes.js"></script>\n</body>',1)

# Theme: supplied JSON becomes the actual interactive toggle.
theme_pat=re.compile(r'<div class="themeVisualToggle v155ThemeToggle">.*?</div>',re.S)
theme_new='''<div class="themeVisualToggle v1551ThemeToggleShell">
  <button id="themeLight" class="v1551ThemeProxy" type="button" aria-hidden="true" tabindex="-1"></button>
  <button id="v1551ThemeToggle" type="button" role="switch" aria-checked="false">
    <span class="v1551ThemeSide light">Light</span>
    <span class="v155ThemeLottie lottieIcon" data-lottie="lottie/theme-v155.json" aria-hidden="true"></span>
    <span class="v1551ThemeSide dark">Dark</span>
  </button>
  <button id="themeDark" class="v1551ThemeProxy" type="button" aria-hidden="true" tabindex="-1"></button>
</div>'''
h,n=theme_pat.subn(theme_new,h,count=1)
if n!=1: raise SystemExit('v15.5 theme toggle anchor missing')

# Keep Delete visibly inside the edit popup as requested earlier.
if 'id="editPopupDelete"' not in h:
    anchor='<div class="actions"><button class="btn primary" id="editSave" type="button">Save Changes</button><button class="btn ghost" id="editCancel" type="button">Cancel</button></div>'
    if anchor not in h: raise SystemExit('edit action anchor missing')
    h=h.replace(anchor,anchor+'\n    <button class="btn dangerOutline" id="editPopupDelete" type="button">Delete Attendance</button>',1)

index.write_text(h,encoding='utf-8')

# Export edit save/close so the final safety binding can call the existing tested logic.
api_pat=re.compile(r'window\.AttendanceAppApi=\{([^}]*)\};')
m=api_pat.search(s)
if not m: raise SystemExit('AttendanceAppApi missing')
body=m.group(1)
for item in ['closeEdit:closeEdit','saveEdit:saveEdit']:
    if item not in body:
        body += ','+item
s=s[:m.start()]+'window.AttendanceAppApi={'+body+'};'+s[m.end():]
app.write_text(s,encoding='utf-8')

# Theme Lottie must stay at the selected endpoint instead of replaying every few seconds.
if 'function isThemeToggle(rec)' not in lr:
    anchor="function clearTimer(rec){if(rec.timer){clearTimeout(rec.timer);rec.timer=null;}}"
    if anchor not in lr: raise SystemExit('lottie clearTimer anchor missing')
    lr=lr.replace(anchor,anchor+"\n  function isThemeToggle(rec){return !!(rec&&rec.container&&rec.container.classList&&rec.container.classList.contains('v155ThemeLottie'));}",1)

old="cfg.container=rec.container;cfg.path=resolvedPath(rec.originalPath,rec.forceWhite);cfg.loop=false;cfg.autoplay=false;"
new="cfg.container=rec.container;cfg.path=isThemeToggle(rec)?rec.originalPath:resolvedPath(rec.originalPath,rec.forceWhite);cfg.loop=false;cfg.autoplay=false;"
if old not in lr: raise SystemExit('lottie build path anchor missing')
lr=lr.replace(old,new,1)

old="rec.anim=originalLoad(cfg);attachLifecycle(rec,initialDelay);"
new="rec.anim=originalLoad(cfg);if(rec.container)rec.container._attendanceLottie=rec.anim;attachLifecycle(rec,initialDelay);"
if old not in lr: raise SystemExit('lottie assign anchor missing')
lr=lr.replace(old,new,1)

old="rec.anim.addEventListener('DOMLoaded',function(){clearTimer(rec);rec.timer=setTimeout(function(){playOnce(rec)},Math.max(0,initialDelay||0));});"
new="rec.anim.addEventListener('DOMLoaded',function(){clearTimer(rec);if(isThemeToggle(rec)){try{var tf=Math.max(1,Math.floor(rec.anim.totalFrames||96));rec.anim.goToAndStop(isDark()?tf-1:0,true)}catch(e){}return;}rec.timer=setTimeout(function(){playOnce(rec)},Math.max(0,initialDelay||0));});"
if old not in lr: raise SystemExit('lottie DOMLoaded anchor missing')
lr=lr.replace(old,new,1)

old="rec.anim.addEventListener('complete',function(){if(rec.forceWhite)return;scheduleNormalReplay(rec);});"
new="rec.anim.addEventListener('complete',function(){if(rec.forceWhite||isThemeToggle(rec))return;scheduleNormalReplay(rec);});"
if old not in lr: raise SystemExit('lottie complete anchor missing')
lr=lr.replace(old,new,1)

old="function reloadForTheme(rec){if(!rec||rec.forceWhite||!rec.container||!document.documentElement.contains(rec.container))return;clearTimer(rec);try{if(rec.anim)rec.anim.destroy()}catch(e){}buildAnim(rec,rec.delay);}"
new="function reloadForTheme(rec){if(!rec||rec.forceWhite||!rec.container||!document.documentElement.contains(rec.container))return;clearTimer(rec);if(isThemeToggle(rec)){try{var tf=Math.max(1,Math.floor(rec.anim.totalFrames||96));rec.anim.goToAndStop(isDark()?tf-1:0,true)}catch(e){}return;}try{if(rec.anim)rec.anim.destroy()}catch(e){}buildAnim(rec,rec.delay);}"
if old not in lr: raise SystemExit('lottie reload anchor missing')
lr=lr.replace(old,new,1)
runtime.write_text(lr,encoding='utf-8')

shutil.copy('ci/v1551-fixes.css',assets/'v1551-fixes.css')
shutil.copy('ci/v1551-fixes.js',assets/'v1551-fixes.js')

print('v15.5.1 UI correction patch applied')
