from pathlib import Path
import sys

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
cloud=assets/'cloud-ui.js'
s=cloud.read_text(encoding='utf-8')

old="function backup(manual){if(!manual)return;if(!user||!user.signedIn||!user.emailVerified||!window.Android||!Android.cloudBackup)return;var s=snap(),x=sig(JSON.stringify((function(){try{return JSON.parse(s).storage||{}}catch(e){return{}}})()));text('cloudStatus','Backing up…');lastSig=x;Android.cloudBackup(s)}"
new="""function b64u(bytes){var s='',i;for(i=0;i<bytes.length;i++)s+=String.fromCharCode(bytes[i]);return btoa(s)}
function unb64u(v){var s=atob(String(v||'')),a=new Uint8Array(s.length),i;for(i=0;i<s.length;i++)a[i]=s.charCodeAt(i);return a}
function backupKeyMaterial(){var uid=String((user&&user.uid)||window.attendanceRuntimeUid||''),email=String((user&&user.email)||'').trim().toLowerCase();return 'MyAttendance|cloud-backup|aes256gcm|v1|'+uid+'|'+email+'|mab-2026-10-client-envelope'}
function backupCryptoKey(){if(!window.crypto||!crypto.subtle)return Promise.reject(new Error('Secure backup encryption is unavailable'));var raw=new TextEncoder().encode(backupKeyMaterial());return crypto.subtle.digest('SHA-256',raw).then(function(h){return crypto.subtle.importKey('raw',h,{name:'AES-GCM'},false,['encrypt','decrypt'])})}
function encryptBackup(plain){var iv=new Uint8Array(12);crypto.getRandomValues(iv);return backupCryptoKey().then(function(k){return crypto.subtle.encrypt({name:'AES-GCM',iv:iv},k,new TextEncoder().encode(plain))}).then(function(buf){return JSON.stringify({version:3,encrypted:true,cipher:'AES-256-GCM',keyDerivation:'account-v1',userUid:String((user&&user.uid)||window.attendanceRuntimeUid||''),savedAt:new Date().toISOString(),iv:b64u(iv),ciphertext:b64u(new Uint8Array(buf))})})}
function decryptBackup(payload){var o;try{o=JSON.parse(payload||'{}')}catch(e){return Promise.reject(new Error('Restore file is invalid'))}if(!o||!o.encrypted)return Promise.resolve(payload);if(o.version!==3||o.cipher!=='AES-256-GCM'||!o.iv||!o.ciphertext)return Promise.reject(new Error('Encrypted backup format is unsupported'));var current=String((user&&user.uid)||window.attendanceRuntimeUid||'');if(o.userUid&&current&&String(o.userUid)!==current)return Promise.reject(new Error('This backup belongs to a different account.'));return backupCryptoKey().then(function(k){return crypto.subtle.decrypt({name:'AES-GCM',iv:unb64u(o.iv)},k,unb64u(o.ciphertext))}).then(function(buf){return new TextDecoder().decode(buf)})}
function backup(manual){if(!manual)return;if(!user||!user.signedIn||!user.emailVerified||!window.Android||!Android.cloudBackup)return;var s=snap(),x=sig(JSON.stringify((function(){try{return JSON.parse(s).storage||{}}catch(e){return{}}})()));text('cloudStatus','Encrypting backup…');lastSig=x;encryptBackup(s).then(function(enc){text('cloudStatus','Uploading encrypted backup…');Android.cloudBackup(enc)}).catch(function(e){text('cloudStatus',(e&&e.message)||'Backup encryption failed')})}"""
if old not in s: raise SystemExit('v12.5 backup anchor missing')
s=s.replace(old,new,1)

pairs=[
("function startAuto(){if(autoStarted)return;autoStarted=true;text('cloudStatus','Manual cloud backup ready. Backup Now creates the restore point.');}",
 "function startAuto(){if(autoStarted)return;autoStarted=true;text('cloudStatus','Encrypted cloud backup ready. Backup Now creates a protected restore point.');}"),
("function restore(){if(!user||!user.signedIn||!user.emailVerified)return;var go=function(){text('cloudStatus','Restoring last manual backup…');Android.cloudRestore()};if(window.appDialog){window.appDialog('Restore backup?','This will restore the last Backup Now snapshot and replace newer local attendance/settings data on this device.',[{label:'Restore',kind:'primary'},{label:'Cancel',kind:'outline'}],function(i){if(i===0)go()})}else if(confirm('Restore your last manual cloud backup? Newer local app data will be replaced.'))go()}",
 "function restore(){if(!user||!user.signedIn||!user.emailVerified)return;var go=function(){text('cloudStatus','Restoring encrypted backup…');Android.cloudRestore()};if(window.appDialog){window.appDialog('Restore backup?','This will restore the last Backup Now snapshot and replace newer local attendance/settings data on this device.',[{label:'Restore',kind:'primary'},{label:'Cancel',kind:'outline'}],function(i){if(i===0)go()})}else if(confirm('Restore your last manual cloud backup? Newer local app data will be replaced.'))go()}"),
("window.onCloudBackupResult=function(ok,msg,ts){text('cloudStatus',ok?'Manual cloud backup saved':(msg||'Backup failed'));if(ok&&ts){localStorage.setItem('attendance_cloud_last_v10',String(ts));localStorage.setItem('attendance_cloud_last_manual_v122',String(ts))}};",
 "window.onCloudBackupResult=function(ok,msg,ts){text('cloudStatus',ok?'Encrypted cloud backup saved':(msg||'Backup failed'));if(ok&&ts){localStorage.setItem('attendance_cloud_last_v10',String(ts));localStorage.setItem('attendance_cloud_last_manual_v122',String(ts))}};"),
("window.onCloudRestore=function(payload){try{var o=JSON.parse(payload||'{}'),s=o.storage||{},current=String(window.attendanceRuntimeUid||'');if(o.userUid&&current&&String(o.userUid)!==current){text('cloudStatus','This backup belongs to a different account.');return}if(window.attendanceRestoreCurrentUser)window.attendanceRestoreCurrentUser(s);else{var k;for(k in s)if(s.hasOwnProperty(k))localStorage.setItem(k,s[k])}localStorage.setItem('attendance_cloud_last_v10',String(Date.now()));location.reload()}catch(e){text('cloudStatus','Restore file is invalid')}};",
 "window.onCloudRestore=function(payload){decryptBackup(payload).then(function(plain){var o=JSON.parse(plain||'{}'),s=o.storage||{},current=String(window.attendanceRuntimeUid||'');if(o.userUid&&current&&String(o.userUid)!==current){text('cloudStatus','This backup belongs to a different account.');return}if(window.attendanceRestoreCurrentUser)window.attendanceRestoreCurrentUser(s);else{var k;for(k in s)if(s.hasOwnProperty(k))localStorage.setItem(k,s[k])}localStorage.setItem('attendance_cloud_last_v10',String(Date.now()));location.reload()}).catch(function(e){text('cloudStatus',(e&&e.message)||'Restore file is invalid')})};")
]
for old,new in pairs:
    if old not in s: raise SystemExit('v12.5 cloud anchor missing')
    s=s.replace(old,new,1)
cloud.write_text(s,encoding='utf-8')

index=assets/'index.html'
html=index.read_text(encoding='utf-8')
old='Manual backup only. Tap Backup Now to create a safe restore point.'
new='Encrypted backup. Tap Backup Now to create a protected restore point.'
if old not in html: raise SystemExit('v12.5 index anchor missing')
index.write_text(html.replace(old,new,1),encoding='utf-8')
print('v12.5 encrypted cloud backup patch applied')
