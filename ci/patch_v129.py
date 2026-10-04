from pathlib import Path
import re,sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
p=assets/'v11-ui.js'
s=p.read_text(encoding='utf-8')

pat=re.compile(r"function clearLocalEverything\(\)\{.*?\}\nfunction deleteProfileFlow",re.S)
m=pat.search(s)
if not m: raise SystemExit('clearLocalEverything anchor missing')
replacement="""function clearLocalEverything(){
 try{if(window.attendanceClearCurrentUser){window.attendanceClearCurrentUser();return}}catch(e){}
 var prefix=String(window.attendanceUserPrefix||''),keys=[],i,k;
 for(i=0;i<localStorage.length;i++)keys.push(localStorage.key(i));
 for(i=0;i<keys.length;i++){k=keys[i];if(k&&prefix&&k.indexOf(prefix)===0)try{localStorage.removeItem(k)}catch(e){}}
 try{if(prefix)indexedDB.deleteDatabase(prefix+'attendance_docs_v81')}catch(e){}
}
function deleteProfileFlow"""
s=s[:m.start()]+replacement+s[m.end():]

pat=re.compile(r"function deleteProfileFlow\(\)\{.*?\nwindow\.onProfileDeleteResult",re.S)
m=pat.search(s)
if not m: raise SystemExit('deleteProfileFlow anchor missing')
flow="""function deleteProfileFlow(){dialog('Delete profile?','This permanently removes this account, its cloud backup (including switch-device backup), encrypted local attendance/settings and local job documents. This cannot be undone.',[{label:'Continue',kind:'danger'},{label:'Cancel',kind:'outline'}],function(i){if(i!==0)return;var email=E('cloudEmail')?E('cloudEmail').textContent:'';dialog('Verify account','Type your registered email address to continue.',[{label:'Verify',kind:'danger'},{label:'Cancel',kind:'outline'}],function(j,val){if(j!==0)return;if(String(val||'').trim().toLowerCase()!==String(email||'').trim().toLowerCase()){dialog('Verification failed','The email address did not match the signed-in account.',[{label:'OK',kind:'primary'}]);return}dialog('Final confirmation','Type DELETE to permanently erase this profile and all of its current app data.',[{label:'Delete permanently',kind:'danger'},{label:'Cancel',kind:'outline'}],function(k,word){if(k!==0)return;if(String(word||'').trim()!=='DELETE'){dialog('Not deleted','You must type DELETE exactly.',[{label:'OK',kind:'primary'}]);return}var provider='';try{if(window.Android&&Android.authProvider)provider=String(Android.authProvider()||'')}catch(e){}if(provider==='password'){dialog('Confirm your identity','Enter your current account password. Firebase will re-authenticate you before deletion begins.',[{label:'Verify & Delete',kind:'danger'},{label:'Cancel',kind:'outline'}],function(q,pw){if(q!==0)return;if(!String(pw||'')){dialog('Password required','Enter your current password to continue.',[{label:'OK',kind:'primary'}]);return}window.onProfileDeleteProgress('Verifying your account…');Android.deleteAccountDataWithPassword(String(pw))},{placeholder:'Current password',type:'password'});return}if(provider==='google.com'&&window.Android&&Android.deleteAccountData){dialog('Confirm with Google','Google account verification will open. Nothing is erased unless re-authentication succeeds.',[{label:'Continue',kind:'danger'},{label:'Cancel',kind:'outline'}],function(q){if(q===0){window.onProfileDeleteProgress('Waiting for Google verification…');Android.deleteAccountData()}});return}dialog('Deletion unavailable','This account provider cannot be securely re-authenticated in the current build. No data was deleted.',[{label:'OK',kind:'primary'}])},{placeholder:'DELETE'})},{placeholder:'Email address',type:'email'})})}
window.onProfileDeleteProgress=function(msg){var old=E('profileDeleteProgress');if(!old){old=document.createElement('div');old.id='profileDeleteProgress';old.className='helpText';old.style.marginTop='10px';var btn=E('deleteProfileBtn');if(btn&&btn.parentNode)btn.parentNode.appendChild(old)}if(old)old.textContent=msg||''};
window.onProfileDeleteResult"""
s=s[:m.start()]+flow+s[m.end():]

old="window.onProfileDeleteResult=function(ok,msg){if(ok){clearLocalEverything();dialog('Profile deleted','Your local profile data and account were deleted.',[{label:'OK',kind:'primary'}],function(){location.reload()})}else dialog('Could not delete profile',msg||'Please sign out, sign in again and retry.',[{label:'OK',kind:'primary'}])};"
new="window.onProfileDeleteResult=function(ok,msg){window.onProfileDeleteProgress('');if(ok){clearLocalEverything();dialog('Profile deleted','Your Firebase account, cloud backup, encrypted local attendance/settings and local job documents were deleted.',[{label:'OK',kind:'primary'}],function(){location.reload()})}else dialog('Could not delete profile',msg||'No local data was erased. Please retry after checking your connection and account sign-in.',[{label:'OK',kind:'primary'}])};"
if old not in s: raise SystemExit('delete result anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('v12.9 secure delete UI patch applied')
