from pathlib import Path
import re, sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
index=assets/'index.html'
html=index.read_text(encoding='utf-8')
html=html.replace('\n<script src="v111-fixes.js"></script>','')
old='''      <div class="settingsCard">
        <div class="label">Theme</div><div class="themeVisualToggle"><button id="themeLight" type="button" aria-label="Light mode"><span>☀</span><small>Light</small></button><button id="themeDark" type="button" aria-label="Dark mode"><span>☾</span><small>Dark</small></button></div>
        <div class="themePreview"><span class="themeMoon">◐</span><b id="themeLabel">Light Mode</b><small>Switch the entire app appearance.</small></div>
      </div>'''
new=old+'''
      <div class="settingsCard typographySettingsCard">
        <div class="typographyHead"><span><b>Typography</b><small>Choose the app font and adjust text by size group.</small></span></div>
        <div class="label">Font</div><div class="field"><select id="fontFamilySelect"><option value="default">Default</option><option value="system">Roboto / System</option><option value="arial">Arial</option><option value="verdana">Verdana</option><option value="georgia">Georgia</option><option value="mono">Monospace</option></select></div>
        <div class="typographyGrid">
          <div><div class="label">Small Text</div><div class="field"><select id="fontSmallScale"><option value="0.9">90%</option><option value="1">100%</option><option value="1.1">110%</option><option value="1.2">120%</option></select></div></div>
          <div><div class="label">Body Text</div><div class="field"><select id="fontBodyScale"><option value="0.9">90%</option><option value="1">100%</option><option value="1.1">110%</option><option value="1.2">120%</option></select></div></div>
          <div><div class="label">Headings</div><div class="field"><select id="fontHeadingScale"><option value="0.9">90%</option><option value="1">100%</option><option value="1.1">110%</option><option value="1.2">120%</option></select></div></div>
          <div><div class="label">Large Display</div><div class="field"><select id="fontDisplayScale"><option value="0.9">90%</option><option value="1">100%</option><option value="1.1">110%</option><option value="1.2">120%</option></select></div></div>
        </div>
        <div class="typographyPreview"><small>Preview</small><b>My Attendance</b><span>Readable text for every area</span></div>
        <button class="btn ghost fullBtn" id="resetTypographyBtn" type="button">Reset Typography</button>
      </div>'''
if old not in html:
    raise SystemExit('Appearance card anchor not found')
html=html.replace(old,new,1)
anchor='''        <button class="settingsMenuRow" data-setting="backup"><span class="menuLottie lottieIcon" data-lottie="lottie/backup.json"></span><span><b>Backup</b><small>Import or export attendance CSV</small></span><i>›</i></button>'''
repl='''        <button class="settingsMenuRow" data-setting="backup"><span class="menuLottie lottieIcon" data-lottie="lottie/backup.json"></span><span><b>Backup</b><small>Cloud backup, CSV and Excel export</small></span><i>›</i></button>
        <button class="settingsLogoutRow" id="settingsLogoutBtn" type="button"><span class="logoutGlyph" aria-hidden="true">↪</span><span><b>Log Out</b><small>Sign out of My Attendance</small></span><i>›</i></button>'''
if anchor not in html:
    raise SystemExit('Settings backup row anchor not found')
html=html.replace(anchor,repl,1)
html=html.replace('<button class="settingsMenuRow" data-setting="appearance"><span class="menuLottie lottieIcon" data-lottie="lottie/settings.json"></span><span><b>Appearance</b><small>Light or dark mode</small></span><i>›</i></button>', '<button class="settingsMenuRow" data-setting="appearance"><span class="menuLottie lottieIcon" data-lottie="lottie/settings.json"></span><span><b>Appearance</b><small>Theme, font and text sizes</small></span><i>›</i></button>',1)
html=html.replace('<link rel="stylesheet" href="v11-ui.css">','<link rel="stylesheet" href="v11-ui.css">\n<link rel="stylesheet" href="v112-ui.css">',1)
html=html.replace('<script src="exceljs.min.js"></script>','<script src="exceljs.min.js"></script>\n<script src="v112-fixes.js"></script>',1)
index.write_text(html,encoding='utf-8')
v11=assets/'v11-ui.js'
s=v11.read_text(encoding='utf-8')
s2,n=re.subn(r"function decorateDates\(root\)\{var a=\(root\|\|document\)\.querySelectorAll\('input\[type=\\\"date\\\"\]'\),i;for\(i=0;i<a\.length;i\+\+\)decorateDate\(a\[i\]\)\}","function decorateDates(root){}",s,count=1)
if n!=1:
    s2,n=re.subn(r"function decorateDates\(root\)\{.*?\}","function decorateDates(root){}",s,count=1)
if n!=1:
    raise SystemExit('Could not disable old date decorator')
v11.write_text(s2,encoding='utf-8')
