from pathlib import Path
import sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
p=assets/'index.html'
s=p.read_text(encoding='utf-8')
head='<link rel="stylesheet" href="app.css">'
if 'cloud-ui.css' not in s:
    s=s.replace(head,head+'\n<link rel="stylesheet" href="cloud-ui.css">')
auth='''<div id="authGate" class="show">
  <div class="authShell">
    <div class="authGlow authGlowOne"></div><div class="authGlow authGlowTwo"></div>
    <div class="authTop"><button class="authBack" id="authBackBtn" type="button" aria-label="Back">‹</button></div>
    <div class="authContent">
      <div class="authMode authModeLogin active" id="authLoginMode">
        <h1>Hello there <span>👋</span></h1>
        <p>Please enter your email &amp; password to access your account.</p>
        <label class="authLabel" for="loginEmail">Email Address</label>
        <div class="authField"><input id="loginEmail" type="email" inputmode="email" autocomplete="email" placeholder="Email"><span class="authFieldIcon">✉</span></div>
        <label class="authLabel" for="loginPassword">Password</label>
        <div class="authField"><input id="loginPassword" type="password" autocomplete="current-password" placeholder="••••••••"><button class="passwordEye" type="button" data-password-target="loginPassword" aria-label="Show password">◉</button></div>
        <div class="authMeta"><label class="rememberRow"><input id="rememberMe" type="checkbox" checked><span></span>Remember Me</label><button id="forgotPasswordBtn" class="authLink" type="button">Forgot Password?</button></div>
        <button class="authPrimary" id="emailLoginBtn" type="button">Continue</button>
        <div class="authDivider"><span>or</span></div>
        <button class="googleAuthBtn" id="googleLoginBtn" type="button"><span class="googleG">G</span>Continue With Google</button>
        <div class="authMsg" id="authMsg"></div>
        <div class="authBottom">New here? Create an account. <button class="authLink" type="button" data-switch-auth="signup">Sign up</button></div>
      </div>
      <div class="authMode authModeSignup" id="authSignupMode">
        <h1>Create account</h1>
        <p>Enter your details to create your My Attendance account.</p>
        <label class="authLabel" for="signupEmail">Email Address</label>
        <div class="authField"><input id="signupEmail" type="email" inputmode="email" autocomplete="email" placeholder="Email"><span class="authFieldIcon">✉</span></div>
        <label class="authLabel" for="signupPassword">Password</label>
        <div class="authField"><input id="signupPassword" type="password" autocomplete="new-password" placeholder="••••••••"><button class="passwordEye" type="button" data-password-target="signupPassword" aria-label="Show password">◉</button></div>
        <label class="authLabel" for="signupConfirm">Confirm Password</label>
        <div class="authField"><input id="signupConfirm" type="password" autocomplete="new-password" placeholder="••••••••"><button class="passwordEye" type="button" data-password-target="signupConfirm" aria-label="Show password">◉</button></div>
        <label class="termsRow"><input id="termsAgree" type="checkbox"><span></span><em>I agree to the Terms &amp; Privacy Policy.</em></label>
        <button class="authPrimary" id="emailSignupBtn" type="button">Continue</button>
        <div class="authDivider"><span>or</span></div>
        <button class="googleAuthBtn" id="googleSignupBtn" type="button"><span class="googleG">G</span>Continue With Google</button>
        <div class="authMsg authSignupMsg" id="signupMsg"></div>
        <div class="authBottom">Already have an account? <button class="authLink" type="button" data-switch-auth="login">Login</button></div>
      </div>
    </div>
  </div>
</div>
<div class="verifyOverlay" id="verifyOverlay">
  <div class="verifyCard">
    <div class="verifyIcon">✓</div>
    <h2>Verify your email</h2>
    <p>We sent a secure verification link to</p>
    <b id="verifyEmail"></b>
    <p class="verifyHint">Open the email, tap the verification link, then return here.</p>
    <button class="authPrimary" id="checkVerifiedBtn" type="button">I've Verified My Email</button>
    <button class="verifySecondary" id="resendVerificationBtn" type="button">Resend Verification Email</button>
    <button class="verifyTextBtn" id="verifySignOutBtn" type="button">Use another account</button>
    <div class="authMsg" id="verifyMsg"></div>
  </div>
</div>'''
if 'id="authGate"' not in s:
    s=s.replace('<body>','<body>\n'+auth,1)
else:
    start=s.index('<div id="authGate"')
    end=s.index('</div>', start)
    # Existing v10 auth gate contains nested divs. Replace through the first app shell marker instead.
    shell_marker='<div class="app">'
    shell=s.find(shell_marker,start)
    if shell==-1: raise SystemExit('App shell marker not found after auth gate')
    s=s[:start]+auth+'\n'+s[shell:]
marker='<section class="screen settingScreen" id="screen-setting-backup">\n      <div class="sectionHeader"><button class="back settingBack" type="button">‹</button><span class="pageLottie lottieIcon" data-lottie="lottie/backup.json"></span><h1>Backup</h1></div>'
card='''<div class="settingsCard cloudAccountCard">
        <div class="cloudUser"><img id="cloudAvatar" src="profile-placeholder.svg" alt="Account profile"><span><b id="cloudName">Account</b><small id="cloudEmail"></small></span></div>
        <div class="cloudActions"><button class="btn primary" id="cloudBackupBtn" type="button">Backup Now</button><button class="btn ghost" id="cloudRestoreBtn" type="button">Restore</button><button class="btn ghost cloudSignOut" id="cloudSignOutBtn" type="button">Sign Out</button></div>
        <small class="cloudStatus" id="cloudStatus">Automatic cloud backup is on while signed in.</small>
      </div>'''
if 'id="cloudBackupBtn"' not in s:
    if marker not in s: raise SystemExit('Backup section marker not found')
    s=s.replace(marker,marker+'\n      '+card,1)
if 'cloud-ui.js' not in s:
    s=s.replace('</body>','<script src="cloud-ui.js"></script>\n</body>',1)
p.write_text(s,encoding='utf-8')
for f in ('cloud-ui.js','cloud-ui.css'):
    if not (assets/f).exists(): raise SystemExit(f+' missing')
print('v10 auth/cloud UI patch applied')
