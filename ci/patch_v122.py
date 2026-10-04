from pathlib import Path
import re, sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
cloud=assets/'cloud-ui.js'
s=cloud.read_text(encoding='utf-8')

old="function backup(manual){if(!user||!user.signedIn||!user.emailVerified||!window.Android||!Android.cloudBackup)return;var s=snap(),x=sig(JSON.stringify((function(){try{return JSON.parse(s).storage||{}}catch(e){return{}}})()));if(!manual&&x===lastSig)return;text('cloudStatus',manual?'Backing up…':'Syncing…');lastSig=x;Android.cloudBackup(s)}"
new="function backup(manual){if(!manual)return;if(!user||!user.signedIn||!user.emailVerified||!window.Android||!Android.cloudBackup)return;var s=snap(),x=sig(JSON.stringify((function(){try{return JSON.parse(s).storage||{}}catch(e){return{}}})()));text('cloudStatus','Backing up…');lastSig=x;Android.cloudBackup(s)}"
if old not in s: raise SystemExit('backup anchor missing')
s=s.replace(old,new,1)

old="function startAuto(){if(autoStarted)return;autoStarted=true;timer=setInterval(function(){backup(false)},45000);setTimeout(function(){backup(false)},5000)}"
new="function startAuto(){if(autoStarted)return;autoStarted=true;text('cloudStatus','Manual cloud backup ready. Backup Now creates the restore point.');}"
if old not in s: raise SystemExit('startAuto anchor missing')
s=s.replace(old,new,1)

old="function restore(){if(!user||!user.signedIn||!user.emailVerified)return;if(confirm('Restore your latest cloud backup? Current local app data will be replaced.')){text('cloudStatus','Restoring…');Android.cloudRestore()}}"
new="function restore(){if(!user||!user.signedIn||!user.emailVerified)return;var go=function(){text('cloudStatus','Restoring last manual backup…');Android.cloudRestore()};if(window.appDialog){window.appDialog('Restore backup?','This will restore the last Backup Now snapshot and replace newer local attendance/settings data on this device.',[{label:'Restore',kind:'primary'},{label:'Cancel',kind:'outline'}],function(i){if(i===0)go()})}else if(confirm('Restore your last manual cloud backup? Newer local app data will be replaced.'))go()}"
if old not in s: raise SystemExit('restore anchor missing')
s=s.replace(old,new,1)

old="window.onCloudBackupResult=function(ok,msg,ts){text('cloudStatus',ok?'Cloud backup saved':(msg||'Backup failed'));if(ok&&ts)localStorage.setItem('attendance_cloud_last_v10',String(ts))};"
new="window.onCloudBackupResult=function(ok,msg,ts){text('cloudStatus',ok?'Manual cloud backup saved':(msg||'Backup failed'));if(ok&&ts){localStorage.setItem('attendance_cloud_last_v10',String(ts));localStorage.setItem('attendance_cloud_last_manual_v122',String(ts))}};"
if old not in s: raise SystemExit('backup result anchor missing')
s=s.replace(old,new,1)

cloud.write_text(s,encoding='utf-8')

index=assets/'index.html'
html=index.read_text(encoding='utf-8')
html=html.replace('Automatic cloud backup is on while signed in.','Manual backup only. Tap Backup Now to create a safe restore point.')
index.write_text(html,encoding='utf-8')
print('v12.2 safe manual backup patch applied')
