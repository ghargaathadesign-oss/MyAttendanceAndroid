(function(){
'use strict';
var user=null,lastSig='',timer=null,autoStarted=false;
function E(id){return document.getElementById(id)}
function text(id,v){var e=E(id);if(e)e.textContent=v||''}
function showGate(on){var g=E('authGate');if(g)g.classList.toggle('show',!!on)}
function profileFromGoogle(u){if(!u||!u.signedIn)return;var k='attendance_profile_v81',p={},changed=false;try{p=JSON.parse(localStorage.getItem(k)||'{}')||{}}catch(e){}if((!p.name||p.name==='My Profile')&&u.name){p.name=u.name;changed=true}if(!p.photo&&u.photo){p.photo=u.photo;changed=true}if(changed){localStorage.setItem(k,JSON.stringify(p));var n=E('profileName');if(n)n.value=p.name||'';var a=E('profilePreview');if(a&&p.photo)a.src=p.photo;var ta=E('topAvatar');if(ta&&p.photo)ta.src=p.photo;var tn=E('topName');if(tn)tn.textContent=p.name||'My Profile'}}
function account(u){var signed=u&&u.signedIn;showGate(!signed);if(!signed){text('authMsg',u&&u.setupError?u.setupError:'Sign in to continue');return}var av=E('cloudAvatar');if(av)av.src=u.photo||'profile-placeholder.svg';text('cloudName',u.name||'Google Account');text('cloudEmail',u.email||'');text('authMsg','');profileFromGoogle(u);startAuto()}
function snap(){var o={version:1,savedAt:new Date().toISOString(),storage:{}},i,k;for(i=0;i<localStorage.length;i++){k=localStorage.key(i);if(k&&k.indexOf('attendance_')===0&&k.indexOf('attendance_cloud_')!==0)o.storage[k]=localStorage.getItem(k)}return JSON.stringify(o)}
function sig(s){var h=0,i;for(i=0;i<s.length;i++)h=((h<<5)-h+s.charCodeAt(i))|0;return s.length+':'+h}
function backup(manual){if(!user||!user.signedIn||!window.Android||!Android.cloudBackup)return;var s=snap(),x=sig(s);if(!manual&&x===lastSig)return;text('cloudStatus',manual?'Backing up…':'Syncing…');lastSig=x;Android.cloudBackup(s)}
function startAuto(){if(autoStarted)return;autoStarted=true;timer=setInterval(function(){backup(false)},45000);setTimeout(function(){backup(false)},5000)}
function restore(){if(!user||!user.signedIn)return;if(confirm('Restore your latest Google cloud backup? Current local app data will be replaced.')){text('cloudStatus','Restoring…');Android.cloudRestore()}}
window.onNativeAuthChanged=function(u){user=u||{};account(user)};
window.onNativeAuthError=function(m){showGate(true);text('authMsg',m||'Google sign-in failed')};
window.onCloudBackupResult=function(ok,msg,ts){text('cloudStatus',ok?'Cloud backup saved':(msg||'Backup failed'));if(ok&&ts)localStorage.setItem('attendance_cloud_last_v10',String(ts))};
window.onCloudRestore=function(payload){try{var o=JSON.parse(payload||'{}'),s=o.storage||{},k;for(k in s)if(s.hasOwnProperty(k))localStorage.setItem(k,s[k]);localStorage.setItem('attendance_cloud_last_v10',String(Date.now()));location.reload()}catch(e){text('cloudStatus','Restore file is invalid')}};
window.onCloudRestoreError=function(m){text('cloudStatus',m||'No cloud backup found')};
function init(){var gi=E('googleLoginBtn'),gb=E('googleSignupBtn'),bk=E('cloudBackupBtn'),rs=E('cloudRestoreBtn'),so=E('cloudSignOutBtn'),tabs=document.querySelectorAll('.authTab'),i;if(gi)gi.onclick=function(){text('authMsg','Opening Google…');Android.googleSignIn()};if(gb)gb.onclick=gi.onclick;if(bk)bk.onclick=function(){backup(true)};if(rs)rs.onclick=restore;if(so)so.onclick=function(){if(confirm('Sign out of this Google account?'))Android.googleSignOut()};for(i=0;i<tabs.length;i++)tabs[i].onclick=function(){var mode=this.getAttribute('data-auth-mode'),j;for(j=0;j<tabs.length;j++)tabs[j].classList.toggle('active',tabs[j]===this);E('googleLoginBtn').style.display=mode==='login'?'flex':'none';E('googleSignupBtn').style.display=mode==='signup'?'flex':'none';text('authTitle',mode==='signup'?'Create your account':'Welcome back');text('authSub',mode==='signup'?'Sign up securely with Google':'Sign in to sync and restore your attendance')};if(window.Android&&Android.authState)Android.authState()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
