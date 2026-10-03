from pathlib import Path
import sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
p=assets/'index.html'
s=p.read_text(encoding='utf-8')
head='<link rel="stylesheet" href="app.css">'
if 'cloud-ui.css' not in s:
    s=s.replace(head,head+'\n<link rel="stylesheet" href="cloud-ui.css">')
auth='''<div id="authGate" class="show">\n  <div class="authCard">\n    <div class="authLogo">MA</div>\n    <h1 id="authTitle">Welcome back</h1>\n    <p id="authSub">Sign in to sync and restore your attendance</p>\n    <div class="authTabs"><button class="authTab active" data-auth-mode="login" type="button">Login</button><button class="authTab" data-auth-mode="signup" type="button">Sign Up</button></div>\n    <button class="googleAuthBtn" id="googleLoginBtn" type="button"><span class="googleG">G</span>Continue with Google</button>\n    <button class="googleAuthBtn" id="googleSignupBtn" type="button" style="display:none"><span class="googleG">G</span>Sign up with Google</button>\n    <div class="authMsg" id="authMsg">Checking account…</div>\n  </div>\n</div>'''
if 'id="authGate"' not in s:
    s=s.replace('<body>','<body>\n'+auth,1)
marker='<section class="screen settingScreen" id="screen-setting-backup">\n      <div class="sectionHeader"><button class="back settingBack" type="button">‹</button><span class="pageLottie lottieIcon" data-lottie="lottie/backup.json"></span><h1>Backup</h1></div>'
card='''<div class="settingsCard cloudAccountCard">\n        <div class="cloudUser"><img id="cloudAvatar" src="profile-placeholder.svg" alt="Google profile"><span><b id="cloudName">Google Account</b><small id="cloudEmail"></small></span></div>\n        <div class="cloudActions"><button class="btn primary" id="cloudBackupBtn" type="button">Backup Now</button><button class="btn ghost" id="cloudRestoreBtn" type="button">Restore</button><button class="btn ghost cloudSignOut" id="cloudSignOutBtn" type="button">Sign Out</button></div>\n        <small class="cloudStatus" id="cloudStatus">Automatic cloud backup is on while signed in.</small>\n      </div>'''
if 'id="cloudBackupBtn"' not in s:
    if marker not in s: raise SystemExit('Backup section marker not found')
    s=s.replace(marker,marker+'\n      '+card,1)
if 'cloud-ui.js' not in s:
    s=s.replace('</body>','<script src="cloud-ui.js"></script>\n</body>',1)
p.write_text(s,encoding='utf-8')
for f in ('cloud-ui.js','cloud-ui.css'):
    if not (assets/f).exists(): raise SystemExit(f+' missing')
print('v10 auth/cloud UI patch applied')
