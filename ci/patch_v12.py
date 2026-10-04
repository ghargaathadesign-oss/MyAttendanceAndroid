from pathlib import Path
import re, sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')

app=assets/'app.js'
s=app.read_text(encoding='utf-8')
old="var DATA_KEY='attendance_v8',SET_KEY='attendance_settings_v8',PROFILE_KEY='attendance_profile_v81',LEAVE_KEY='attendance_leave_setup_v81',SALARY_KEY='attendance_salary_v9',THEME_KEY='attendance_theme_v9',DOC_DB='attendance_docs_v81',DOC_STORE='documents';"
new="var DATA_KEY='attendance_v8',SET_KEY='attendance_settings_v8',PROFILE_KEY='attendance_profile_v81',LEAVE_KEY='attendance_leave_setup_v81',SALARY_KEY='attendance_salary_v9',THEME_KEY='attendance_theme_v9',DOC_DB=(window.attendanceUserDb?window.attendanceUserDb('attendance_docs_v81'):'attendance_docs_v81'),DOC_STORE='documents';"
if old not in s: raise SystemExit('app storage constants anchor not found')
s=s.replace(old,new,1)
old_boot="if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init()"
new_boot="function startUserScopedApp(){var go=function(){init()};if(window.attendanceStorageReady&&typeof window.attendanceStorageReady.then==='function')window.attendanceStorageReady.then(go).catch(go);else go()}\nif(document.readyState==='loading')document.addEventListener('DOMContentLoaded',startUserScopedApp);else startUserScopedApp()"
if old_boot not in s: raise SystemExit('app boot anchor not found')
s=s.replace(old_boot,new_boot,1)
app.write_text(s,encoding='utf-8')

cloud=assets/'cloud-ui.js'
c=cloud.read_text(encoding='utf-8')
account_pat=r"function account\(u\)\{.*?\}\nfunction snap\(\)"
account_new="""function account(u){user=u||{};var signed=!!user.signedIn,verified=!!user.emailVerified,expected=signed?String(user.uid||''):'';if(typeof window.attendanceRuntimeUid==='string'&&window.attendanceRuntimeUid!==expected){location.reload();return}if(signed&&!verified){showGate(true);showVerify(true,user.email||'');return}showVerify(false);showGate(!signed);if(!signed){if(user.setupError)text('authMsg',user.setupError);return}var av=E('cloudAvatar');if(av)av.src=user.photo||'profile-placeholder.svg';text('cloudName',user.name||'My Account');text('cloudEmail',user.email||'');clearMsgs();profileFromAccount(user);startAuto()}\nfunction snap()"""
c2,n=re.subn(account_pat,account_new,c,count=1,flags=re.S)
if n!=1: raise SystemExit('cloud account function anchor not found')
c=c2
snap_pat=r"function snap\(\)\{.*?\}\nfunction sig\(s\)"
snap_new="""function snap(){var storage=window.attendanceSnapshotCurrentUser?window.attendanceSnapshotCurrentUser():{},o={version:2,userUid:String(window.attendanceRuntimeUid||''),savedAt:new Date().toISOString(),storage:storage};return JSON.stringify(o)}\nfunction sig(s)"""
c2,n=re.subn(snap_pat,snap_new,c,count=1,flags=re.S)
if n!=1: raise SystemExit('cloud snap anchor not found')
c=c2
backup_old="function backup(manual){if(!user||!user.signedIn||!user.emailVerified||!window.Android||!Android.cloudBackup)return;var s=snap(),x=sig(s);if(!manual&&x===lastSig)return;text('cloudStatus',manual?'Backing up…':'Syncing…');lastSig=x;Android.cloudBackup(s)}"
backup_new="function backup(manual){if(!user||!user.signedIn||!user.emailVerified||!window.Android||!Android.cloudBackup)return;var s=snap(),x=sig(JSON.stringify((function(){try{return JSON.parse(s).storage||{}}catch(e){return{}}})()));if(!manual&&x===lastSig)return;text('cloudStatus',manual?'Backing up…':'Syncing…');lastSig=x;Android.cloudBackup(s)}"
if backup_old not in c: raise SystemExit('cloud backup anchor not found')
c=c.replace(backup_old,backup_new,1)
restore_pat=r"window\.onCloudRestore=function\(payload\)\{.*?\};\nwindow\.onCloudRestoreError"
restore_new="""window.onCloudRestore=function(payload){try{var o=JSON.parse(payload||'{}'),s=o.storage||{},current=String(window.attendanceRuntimeUid||'');if(o.userUid&&current&&String(o.userUid)!==current){text('cloudStatus','This backup belongs to a different account.');return}if(window.attendanceRestoreCurrentUser)window.attendanceRestoreCurrentUser(s);else{var k;for(k in s)if(s.hasOwnProperty(k))localStorage.setItem(k,s[k])}localStorage.setItem('attendance_cloud_last_v10',String(Date.now()));location.reload()}catch(e){text('cloudStatus','Restore file is invalid')}};\nwindow.onCloudRestoreError"""
c2,n=re.subn(restore_pat,restore_new,c,count=1,flags=re.S)
if n!=1: raise SystemExit('cloud restore anchor not found')
cloud.write_text(c2,encoding='utf-8')

v11=assets/'v11-ui.js'
v=v11.read_text(encoding='utf-8')
clear_pat=r"function clearLocalEverything\(\)\{.*?\}\nfunction deleteProfileFlow"
clear_new="""function clearLocalEverything(){if(window.attendanceClearCurrentUser){window.attendanceClearCurrentUser();return}var keys=[],i;for(i=0;i<localStorage.length;i++)keys.push(localStorage.key(i));for(i=0;i<keys.length;i++)if(keys[i]&&keys[i].indexOf('attendance_')===0)localStorage.removeItem(keys[i]);try{indexedDB.deleteDatabase('attendance_docs_v81')}catch(e){}}\nfunction deleteProfileFlow"""
v2,n=re.subn(clear_pat,clear_new,v,count=1,flags=re.S)
if n!=1: raise SystemExit('v11 clearLocalEverything anchor not found')
v11.write_text(v2,encoding='utf-8')

index=assets/'index.html'
html=index.read_text(encoding='utf-8')
needle='<script src="app.js"></script>'
if needle not in html: raise SystemExit('app.js tag missing')
html=html.replace(needle,'<script src="user-storage.js"></script>\n'+needle,1)
index.write_text(html,encoding='utf-8')
print('v12 per-user data isolation patch applied')
