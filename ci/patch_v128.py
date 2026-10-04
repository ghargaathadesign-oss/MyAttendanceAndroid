from pathlib import Path
import sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')

p=assets/'cloud-ui.js'
s=p.read_text(encoding='utf-8')

old="function applyRestore(plain){var o=JSON.parse(plain||'{}'),s=o.storage||{},current=String(window.attendanceRuntimeUid||'');if(o.userUid&&current&&String(o.userUid)!==current)throw new Error('This backup belongs to a different account.');if(window.AttendancePolicy&&AttendancePolicy.validateStorage){var check=AttendancePolicy.validateStorage(s);if(!check.ok)throw new Error(check.error||'Backup validation failed')}var ok=window.attendanceRestoreCurrentUser?window.attendanceRestoreCurrentUser(s):false;if(!ok)throw new Error('Restore failed safely. Your existing data was kept.');localStorage.setItem('attendance_cloud_last_v10',String(Date.now()));text('cloudStatus','Restore verified. Reloading…');setTimeout(function(){location.reload()},120)}"
new="function applyRestore(plain){var o=JSON.parse(plain||'{}'),s=o.storage||{},current=String(window.attendanceRuntimeUid||'');if(o.userUid&&current&&String(o.userUid)!==current)throw new Error('This backup belongs to a different account.');if(window.AttendancePolicy&&AttendancePolicy.normalizeStorage){var norm=AttendancePolicy.normalizeStorage(s);if(!norm.ok)throw new Error(norm.error||'Backup validation failed');s=norm.storage}else if(window.AttendancePolicy&&AttendancePolicy.validateStorage){var check=AttendancePolicy.validateStorage(s);if(!check.ok)throw new Error(check.error||'Backup validation failed')}var ok=window.attendanceRestoreCurrentUser?window.attendanceRestoreCurrentUser(s):false;if(!ok)throw new Error('Restore failed safely. Your existing data was kept.');localStorage.setItem('attendance_cloud_last_v10',String(Date.now()));text('cloudStatus','Restore verified. Reloading…');setTimeout(function(){location.reload()},120)}"
if old not in s: raise SystemExit('applyRestore anchor missing')
s=s.replace(old,new,1)

anchor="function startAuto(){if(autoStarted)return;autoStarted=true;text('cloudStatus','Ready. Backup and Restore are protected by your phone security.')}"
transfer="""function validTransferPin(pin){return window.AttendanceTransferCrypto&&AttendanceTransferCrypto.validPin(String(pin||''))}
function askTransferPin(title,message,done){if(window.appDialog){window.appDialog(title,message,[{label:'Continue',kind:'primary'},{label:'Cancel',kind:'outline'}],function(i,val){if(i!==0)return;val=String(val||'').trim();if(!validTransferPin(val)){text('cloudStatus','Transfer PIN must be 6 to 12 digits.');return}done(val)},{placeholder:'6–12 digit Transfer PIN',type:'tel'});return}var v=prompt(message);if(v!=null){v=String(v).trim();if(!validTransferPin(v)){text('cloudStatus','Transfer PIN must be 6 to 12 digits.');return}done(v)}}
function transferBackup(){if(!user||!user.signedIn||!user.emailVerified)return;if(!window.Android||!Android.cloudTransferBackup||!window.AttendanceTransferCrypto){text('cloudStatus','Switch-device backup is unavailable in this build.');return}askTransferPin('Create Transfer PIN','Choose a 6 to 12 digit PIN. You will need this PIN on the new phone.',function(pin){askTransferPin('Confirm Transfer PIN','Enter the same Transfer PIN again.',function(confirmPin){if(pin!==confirmPin){text('cloudStatus','Transfer PINs do not match. Please try again.');return}text('cloudStatus','Encrypting switch-device backup…');AttendanceTransferCrypto.encrypt(snap(),pin,String(user.uid||window.attendanceRuntimeUid||'')).then(function(enc){text('cloudStatus','Uploading switch-device backup…');Android.cloudTransferBackup(enc)}).catch(function(e){text('cloudStatus',(e&&e.message)||'Could not create switch-device backup')})})})}
function transferRestore(){if(!user||!user.signedIn||!user.emailVerified)return;if(!window.Android||!Android.cloudTransferRestore||!window.AttendanceTransferCrypto){text('cloudStatus','Switch-device restore is unavailable in this build.');return}askTransferPin('Restore on New Device','Enter the Transfer PIN used when the switch-device backup was created.',function(pin){window._attendanceTransferPin=pin;text('cloudStatus','Downloading switch-device backup…');Android.cloudTransferRestore()})}
"""
if anchor not in s: raise SystemExit('startAuto anchor missing')
s=s.replace(anchor,transfer+anchor,1)

old="window.onCloudRestoreError=function(m){text('cloudStatus',m||'No cloud backup found')};"
new="""window.onCloudTransferBackupResult=function(ok,msg,ts){text('cloudStatus',ok?'Switch-device backup saved. Keep your Transfer PIN safe.':(msg||'Switch-device backup failed'));};
window.onCloudTransferRestore=function(payload){var pin=String(window._attendanceTransferPin||'');window._attendanceTransferPin='';if(!pin){text('cloudStatus','Transfer PIN is required.');return}AttendanceTransferCrypto.decrypt(payload,pin,String((user&&user.uid)||window.attendanceRuntimeUid||'')).then(function(plain){applyRestore(plain)}).catch(function(e){text('cloudStatus',(e&&e.message)||'Could not restore switch-device backup')})};
window.onCloudRestoreError=function(m){window._attendanceTransferPin='';text('cloudStatus',m||'No cloud backup found')};"""
if old not in s: raise SystemExit('restore callback anchor missing')
s=s.replace(old,new,1)

old="function init(){var gi=E('googleLoginBtn'),gs=E('googleSignupBtn'),el=E('emailLoginBtn'),es=E('emailSignupBtn'),fp=E('forgotPasswordBtn'),bk=E('cloudBackupBtn'),rs=E('cloudRestoreBtn'),so=E('cloudSignOutBtn'),cv=E('checkVerifiedBtn'),rv=E('resendVerificationBtn'),vs=E('verifySignOutBtn'),sw=document.querySelectorAll('[data-switch-auth]'),eyes=document.querySelectorAll('[data-password-target]'),i;"
new="function init(){var gi=E('googleLoginBtn'),gs=E('googleSignupBtn'),el=E('emailLoginBtn'),es=E('emailSignupBtn'),fp=E('forgotPasswordBtn'),bk=E('cloudBackupBtn'),rs=E('cloudRestoreBtn'),tb=E('cloudTransferBackupBtn'),tr=E('cloudTransferRestoreBtn'),so=E('cloudSignOutBtn'),cv=E('checkVerifiedBtn'),rv=E('resendVerificationBtn'),vs=E('verifySignOutBtn'),sw=document.querySelectorAll('[data-switch-auth]'),eyes=document.querySelectorAll('[data-password-target]'),i;"
if old not in s: raise SystemExit('init vars anchor missing')
s=s.replace(old,new,1)
old="if(bk)bk.onclick=backup;if(rs)rs.onclick=restore;if(so)so.onclick=function(){if(confirm('Sign out of this account?'))Android.googleSignOut()};"
new="if(bk)bk.onclick=backup;if(rs)rs.onclick=restore;if(tb)tb.onclick=transferBackup;if(tr)tr.onclick=transferRestore;if(so)so.onclick=function(){if(confirm('Sign out of this account?'))Android.googleSignOut()};"
if old not in s: raise SystemExit('init bind anchor missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

p=assets/'index.html'
html=p.read_text(encoding='utf-8')
old='''        <div class="cloudActions"><button class="btn primary" id="cloudBackupBtn" type="button">Backup Now</button><button class="btn ghost" id="cloudRestoreBtn" type="button">Restore</button><button class="btn ghost cloudSignOut" id="cloudSignOutBtn" type="button">Sign Out</button></div>
        <small class="cloudStatus" id="cloudStatus">Ready. Your backup is protected by this device.</small>'''
new='''        <div class="cloudActions"><button class="btn primary" id="cloudBackupBtn" type="button">Backup Now</button><button class="btn ghost" id="cloudRestoreBtn" type="button">Restore</button><button class="btn ghost cloudSignOut" id="cloudSignOutBtn" type="button">Sign Out</button></div>
        <small class="cloudStatus" id="cloudStatus">Ready. Your backup is protected by this device.</small>
        <div class="label" style="margin-top:22px">SWITCHING TO A NEW PHONE?</div>
        <p class="helpText">Create a portable encrypted backup with a Transfer PIN. On the new phone, sign in to the same account and enter that PIN.</p>
        <div class="cloudActions"><button class="btn ghost" id="cloudTransferBackupBtn" type="button">Backup for New Device</button><button class="btn ghost" id="cloudTransferRestoreBtn" type="button">Restore on New Device</button></div>'''
if old not in html: raise SystemExit('switch-device UI anchor missing')
html=html.replace(old,new,1)
html=html.replace('<script src="backup-crypto.js"></script>','<script src="backup-crypto.js"></script>\n<script src="transfer-crypto.js"></script>',1)
p.write_text(html,encoding='utf-8')
print('v12.8 legacy restore + switch-device UI patch applied')
