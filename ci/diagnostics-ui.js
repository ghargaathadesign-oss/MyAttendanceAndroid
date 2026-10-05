(function(){
'use strict';
function E(id){return document.getElementById(id)}
var state={native:{},local:{},documents:{ok:null,count:0},cloud:{ok:null,exists:null},health:{level:'warning',issues:[],warnings:[]},r8Enabled:true};
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function parse(v,d){try{return JSON.parse(String(v||''))}catch(e){return d}}
function boolText(v){return v===true?'Good':v===false?'Attention':'Checking'}
function fmtBytes(n){n=Number(n)||0;if(n<1024)return n+' B';if(n<1024*1024)return(n/1024).toFixed(1)+' KB';return(n/(1024*1024)).toFixed(1)+' MB'}
function row(label,value,kind){return'<div class="diagRow"><span>'+esc(label)+'</span><b class="'+esc(kind||'')+'">'+esc(value)+'</b></div>'}
function currentStorage(){try{return window.attendanceSnapshotCurrentUser?window.attendanceSnapshotCurrentUser():{}}catch(e){return{}}}
function todayLocal(){var d=new Date(),m=d.getMonth()+1,x=d.getDate();return d.getFullYear()+'-'+(m<10?'0':'')+m+'-'+(x<10?'0':'')+x}
function render(){
  if(!E('diagnosticsSummary'))return;
  state.health=window.AttendanceDiagnostics?AttendanceDiagnostics.health(state.local,state.native,state.documents,state.cloud):state.health;
  var h=state.health,klass=h.level==='good'?'diagGood':(h.level==='error'?'diagError':'diagWarn'),title=h.level==='good'?'All core checks passed':(h.level==='error'?'Action needed':'Mostly healthy');
  E('diagnosticsSummary').className='diagSummary '+klass;
  E('diagnosticsSummary').innerHTML='<div class="diagShield">'+(h.level==='good'?'✓':(h.level==='error'?'!':'•'))+'</div><div><b>'+esc(title)+'</b><small>'+esc((h.issues.length?h.issues[0]:(h.warnings.length?h.warnings[0]:'Security, storage and backup checks look healthy.')))+'</small></div>';
  var n=state.native||{},l=state.local||{},d=state.documents||{},c=state.cloud||{};
  E('diagAppCard').innerHTML=row('App version',(n.versionName||'—')+' ('+(n.versionCode||'—')+')')+row('Android','SDK '+(n.sdk||'—')+' • '+(n.androidRelease||'—'))+row('R8 protection','Enabled','ok');
  E('diagSecurityCard').innerHTML=row('Encrypted local storage',boolText(n.secureStorage),n.secureStorage?'ok':'bad')+row('Phone screen lock',boolText(n.deviceSecure),n.deviceSecure?'ok':'bad')+row('Device backup key',n.backupKeyPresent===true?'Ready':(n.backupKeyPresent===false?'Not created yet':'Checking'),n.backupKeyPresent===false?'warn':'ok')+row('WebView file access',n.webViewFileAccess===false?'Blocked':'Attention',n.webViewFileAccess===false?'ok':'bad')+row('Safe Browsing',boolText(n.safeBrowsing),n.safeBrowsing?'ok':'warn')+row('App Check client',n.appCheckEnabled===true?'Enabled':(n.appCheckEnabled===false?'Disabled':'Checking'),n.appCheckEnabled===true?'ok':(n.appCheckEnabled===false?'warn':''))+row('Firebase account',n.signedIn?(n.emailVerified?'Verified':'Needs verification'):'Not signed in',n.signedIn&&n.emailVerified?'ok':'warn');
  E('diagDataCard').innerHTML=row('Attendance data',l.ok?'Valid':'Needs attention',l.ok?'ok':'bad')+row('Attendance records',l.recordCount||0)+row('Duplicate dates',l.duplicateDates||0,l.duplicateDates?'warn':'ok')+row('Historical incomplete punches',l.incompletePunches||0,l.incompletePunches?'warn':'ok')+row('Open shift today',l.openShiftToday||0,l.openShiftToday?'ok':'')+row('Legacy data repair',l.legacyNormalized?'Available':'Not needed',l.legacyNormalized?'warn':'ok')+row('Job documents',d.ok===false?'Check unavailable':(d.ok===null?'Checking…':d.count),d.ok===false?'warn':'');
  var cloudStatus=c.ok===null?'Checking…':(c.ok===false?'Check unavailable':(c.exists?'Backup found':'No backup found'));
  E('diagCloudCard').innerHTML=row('Cloud status',cloudStatus,c.ok===false?'warn':(c.exists?'ok':'warn'))+row('Backup format',c.exists?'v'+(c.version||'?'):'—')+row('Same-device copy',c.hasDevice===true?'Available':(c.exists?'No':'—'),c.hasDevice===true?'ok':'')+row('Switch-device copy',c.hasTransfer===true?'Available':(c.exists?'No':'—'),c.hasTransfer===true?'ok':'')+row('Encrypted size',c.exists?fmtBytes(c.bytes):'—');
  var notes=(h.issues||[]).concat(h.warnings||[]);
  E('diagNotes').innerHTML=notes.length?notes.map(function(x){return'<div class="diagNote">'+esc(x)+'</div>'}).join(''):'<div class="diagNote good">No diagnostic warnings.</div>';
}
function docsCheck(){
  state.documents={ok:null,count:0};render();
  try{
    if(typeof window.attendanceDocumentCount!=='function'){state.documents={ok:false,count:0};render();return}
    var ready=window.attendanceDocumentsReady&&typeof window.attendanceDocumentsReady.then==='function'?window.attendanceDocumentsReady:Promise.resolve();
    var done=false,t=setTimeout(function(){if(!done){done=true;state.documents={ok:false,count:0};render()}},3500);
    ready.then(function(){return window.attendanceDocumentCount()}).then(function(count){
      if(done)return;done=true;clearTimeout(t);state.documents={ok:true,count:Number(count)||0};render();
    }).catch(function(){if(done)return;done=true;clearTimeout(t);state.documents={ok:false,count:0};render()});
  }catch(e){state.documents={ok:false,count:0};render()}
}
function run(){
  state.cloud={ok:null,exists:null};
  var storage=currentStorage();
  state.local=window.AttendanceDiagnostics?AttendanceDiagnostics.inspectStorage(storage,window.AttendancePolicy,todayLocal()):{ok:false,error:'Diagnostics engine unavailable'};
  try{state.native=window.Android&&Android.diagnosticsSummary?parse(Android.diagnosticsSummary(),{}):{}}catch(e){state.native={}}
  render();docsCheck();
  try{if(window.Android&&Android.diagnosticsCloudBackup)Android.diagnosticsCloudBackup();else{state.cloud={ok:false,exists:null};render()}}catch(e){state.cloud={ok:false,exists:null};render()}
}
window.onDiagnosticsCloudStatus=function(o){state.cloud=o&&typeof o==='object'?o:{ok:false,exists:null};render()};
window.onDiagnosticsCacheCleared=function(ok){if(window.appDialog)window.appDialog(ok?'Cache cleared':'Could not clear cache',ok?'Temporary cache was cleared. Your attendance, settings, documents and backups were not changed.':'Temporary cache could not be cleared.',[{label:'OK',kind:'primary'}]);run()};
function repair(){
  var raw=currentStorage(),norm=window.AttendancePolicy&&AttendancePolicy.normalizeStorage?AttendancePolicy.normalizeStorage(raw):{ok:false,error:'Policy engine unavailable'};
  if(!norm.ok){if(window.appDialog)window.appDialog('Repair unavailable',String(norm.error||'Local data failed validation.'),[{label:'OK',kind:'primary'}]);return}
  var changes=[];
  ['attendance_v8','attendance_settings_v8'].forEach(function(k){if(typeof norm.storage[k]==='string'&&norm.storage[k]!==raw[k])changes.push(k)});
  if(!changes.length){if(window.appDialog)window.appDialog('No repair needed','Attendance dates, times, statuses and work settings already use the current format.',[{label:'OK',kind:'primary'}]);return}
  var go=function(){try{changes.forEach(function(k){localStorage.setItem(k,norm.storage[k])});if(window.appDialog)window.appDialog('Repair complete','Compatible legacy attendance formats were normalized. No attendance record was deleted.',[{label:'OK',kind:'primary'}]);run()}catch(e){if(window.appDialog)window.appDialog('Repair failed','Your existing data was kept. '+String(e&&e.message||''),[{label:'OK',kind:'primary'}])}};
  if(window.appDialog)window.appDialog('Repair compatible data?','This only normalizes legacy date, time, status and work-setting formats. It does not delete attendance records.',[{label:'Repair',kind:'primary'},{label:'Cancel',kind:'outline'}],function(i){if(i===0)go()});else go();
}
function supportReport(){
  var report=window.AttendanceDiagnostics?AttendanceDiagnostics.buildSupportReport(state):'Diagnostics report unavailable';
  var bytes=new TextEncoder().encode(report),bin='',i,step=32768;for(i=0;i<bytes.length;i+=step)bin+=String.fromCharCode.apply(null,bytes.subarray(i,Math.min(bytes.length,i+step)));
  var b64=btoa(bin),name='My_Attendance_Support_Report_'+new Date().toISOString().slice(0,10)+'.txt';
  try{if(window.Android&&Android.saveBase64File){Android.saveBase64File(name,'text/plain',b64);if(window.appDialog)window.appDialog('Support report exported','A privacy-safe technical report was saved. It does not contain your email, UID, salary amount, attendance notes, document contents, passwords, device PIN or Transfer PIN.',[{label:'OK',kind:'primary'}]);return}}catch(e){}
  if(window.appDialog)window.appDialog('Export unavailable','Support report export is available in the Android app.',[{label:'OK',kind:'primary'}]);
}
function init(){
  var r=E('diagRunBtn'),repairBtn=E('diagRepairBtn'),backup=E('diagBackupBtn'),cache=E('diagClearCacheBtn'),report=E('diagReportBtn');
  if(r)r.onclick=run;if(repairBtn)repairBtn.onclick=repair;if(backup)backup.onclick=function(){if(typeof window.showScreen==='function')window.showScreen('setting-backup')};if(cache)cache.onclick=function(){try{if(window.Android&&Android.clearDiagnosticsCache){Android.clearDiagnosticsCache();return}}catch(e){}window.onDiagnosticsCacheCleared(false)};if(report)report.onclick=supportReport;
  document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-setting="diagnostics"]');if(b)setTimeout(run,80)},true);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();