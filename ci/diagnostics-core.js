(function(root,factory){
  var api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.AttendanceDiagnostics=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
function num(v,d){v=Number(v);return isFinite(v)?v:d}
function safeJson(v,d){try{var x=JSON.parse(String(v||''));return x==null?d:x}catch(e){return d}}
function inspectStorage(storage,policy,todayValue){
  storage=storage&&typeof storage==='object'&&!Array.isArray(storage)?storage:{};
  var norm=policy&&policy.normalizeStorage?policy.normalizeStorage(storage):{ok:true,storage:storage};
  var out={ok:!!norm.ok,error:norm.ok?'':String(norm.error||'Storage validation failed'),keyCount:Object.keys(storage).length,approxChars:0,recordCount:0,duplicateDates:0,incompletePunches:0,openShiftToday:0,legacyNormalized:false,settingsPresent:false,profilePresent:false,salaryPresent:false,leaveSetupPresent:false};
  Object.keys(storage).forEach(function(k){out.approxChars+=String(storage[k]||'').length});
  if(!norm.ok)return out;
  var s=norm.storage||storage,a=safeJson(s.attendance_v8,[]),seen={},i,r,d,today=String(todayValue||new Date().toISOString().slice(0,10));
  if(Array.isArray(a)){
    out.recordCount=a.length;
    for(i=0;i<a.length;i++){r=a[i]||{};d=String(r.date||'');if(d){if(seen[d])out.duplicateDates++;seen[d]=1}if(r.checkIn&&!r.checkOut&&d===today)out.openShiftToday++;else if((r.checkIn&&!r.checkOut)||(!r.checkIn&&r.checkOut))out.incompletePunches++}
  }
  out.settingsPresent=typeof s.attendance_settings_v8==='string';
  out.profilePresent=typeof s.attendance_profile_v81==='string';
  out.salaryPresent=typeof s.attendance_salary_v9==='string';
  out.leaveSetupPresent=typeof s.attendance_leave_setup_v81==='string';
  out.legacyNormalized=!!(norm.storage&&(norm.storage.attendance_v8!==storage.attendance_v8||norm.storage.attendance_settings_v8!==storage.attendance_settings_v8));
  return out;
}
function health(local,nativeInfo,docs,cloud){
  var issues=[],warnings=[];
  if(!local||!local.ok)issues.push('Local attendance data failed validation');
  if(local&&local.duplicateDates>0)warnings.push('Duplicate attendance dates found');
  if(local&&local.incompletePunches>0)warnings.push('Some attendance records have only one punch time');
  if(nativeInfo&&nativeInfo.secureStorage===false)issues.push('Android Keystore secure storage is unavailable');
  if(nativeInfo&&nativeInfo.webViewFileAccess===true)issues.push('WebView file access is enabled');
  if(nativeInfo&&typeof nativeInfo.webViewFileAccess==='undefined')warnings.push('WebView hardening status could not be read');
  if(nativeInfo&&nativeInfo.safeBrowsing===false)warnings.push('WebView Safe Browsing is disabled');
  if(nativeInfo&&nativeInfo.appCheckEnabled===false)warnings.push('Firebase App Check client is disabled');
  if(nativeInfo&&typeof nativeInfo.safeBrowsing==='undefined')warnings.push('Safe Browsing status could not be read');
  if(nativeInfo&&nativeInfo.signedIn===false)warnings.push('Not signed in to Firebase');
  if(nativeInfo&&nativeInfo.signedIn===true&&nativeInfo.emailVerified===false)warnings.push('Firebase email is not verified');
  if(docs&&docs.ok===false)warnings.push('Local document database could not be checked');
  if(cloud&&cloud.ok===false)warnings.push('Cloud backup could not be checked');
  if(cloud&&cloud.ok===true&&cloud.exists===false)warnings.push('No cloud backup found');
  return{level:issues.length?'error':(warnings.length?'warning':'good'),issues:issues,warnings:warnings};
}
function yn(v){return v===true?'Yes':v===false?'No':'Unknown'}
function cleanText(v,max){v=String(v==null?'':v).replace(/[\r\n\t]+/g,' ').replace(/\s{2,}/g,' ').trim();return v.slice(0,max||120)}
function buildSupportReport(state){
  state=state||{};var n=state.native||{},l=state.local||{},d=state.documents||{},c=state.cloud||{},h=state.health||health(l,n,d,c);
  var lines=[
    'MY ATTENDANCE SUPPORT REPORT',
    'Generated: '+new Date().toISOString(),
    'Privacy: Technical summary only. No email, UID, salary amount, attendance notes, document contents, passwords, device PINs, biometric data, Firebase API keys or Transfer PINs are included.',
    '',
    '[App]',
    'Version: '+cleanText(n.versionName||state.versionName||'Unknown',40),
    'Version code: '+cleanText(n.versionCode||state.versionCode||'Unknown',20),
    'Android SDK: '+cleanText(n.sdk||'Unknown',20),
    'Android release: '+cleanText(n.androidRelease||'Unknown',30),
    'R8 release: '+yn(state.r8Enabled!==false),
    '',
    '[Security]',
    'Firebase signed in: '+yn(n.signedIn),
    'Email verified: '+yn(n.emailVerified),
    'Auth provider: '+cleanText(n.authProvider||'Unknown',40),
    'Android Keystore storage: '+yn(n.secureStorage),
    'Device screen lock: '+yn(n.deviceSecure),
    'Device backup key present: '+yn(n.backupKeyPresent),
    'WebView file access disabled: '+yn(n.webViewFileAccess===false),
    'WebView Safe Browsing: '+yn(n.safeBrowsing),
    'App Check client enabled: '+yn(n.appCheckEnabled),
    '',
    '[Local data]',
    'Storage validation: '+(l.ok?'PASS':'FAIL'),
    'Attendance records: '+num(l.recordCount,0),
    'Duplicate dates: '+num(l.duplicateDates,0),
    'Historical incomplete punch pairs: '+num(l.incompletePunches,0),
    'Open shift today: '+num(l.openShiftToday,0),
    'Legacy normalization available: '+yn(l.legacyNormalized),
    'Encrypted storage keys: '+num(n.secureKeyCount,0),
    'Job documents: '+(d.ok===false?'Check unavailable':num(d.count,0)),
    '',
    '[Cloud backup]',
    'Cloud check: '+(c.ok===false?'Unavailable':'Available'),
    'Backup exists: '+yn(c.exists),
    'Envelope version: '+cleanText(c.version||'None',20),
    'Same-device backup present: '+yn(c.hasDevice),
    'Switch-device backup present: '+yn(c.hasTransfer),
    'Legacy backup present: '+yn(c.hasLegacy),
    'Encrypted backup bytes: '+num(c.bytes,0),
    '',
    '[Health]',
    'Overall: '+String(h.level||'unknown').toUpperCase(),
    'Issues: '+(h.issues&&h.issues.length?h.issues.map(function(x){return cleanText(x,120)}).join(' | '):'None'),
    'Warnings: '+(h.warnings&&h.warnings.length?h.warnings.map(function(x){return cleanText(x,120)}).join(' | '):'None')
  ];
  return lines.join('\n');
}
return{inspectStorage:inspectStorage,health:health,buildSupportReport:buildSupportReport};
});