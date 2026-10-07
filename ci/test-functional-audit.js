'use strict';
// v15.5.6 deep audit

const fs=require('fs');
const path=require('path');
const assert=require('assert');
const {JSDOM}=require('jsdom');
const {indexedDB,IDBKeyRange}=require('fake-indexeddb');
const {webcrypto}=require('crypto');

const assets=path.resolve(process.argv[2]||'app/src/main/assets');
const htmlPath=path.join(assets,'index.html');
const html=fs.readFileSync(htmlPath,'utf8');
const appSource=fs.readFileSync(path.join(assets,'app.js'),'utf8');
function sourceSnippet(token){const i=appSource.indexOf(token);return i>=0?appSource.slice(Math.max(0,i-500),Math.min(appSource.length,i+2400)):'MISSING '+token}
const results=[];
function ok(name,detail){results.push({name,ok:true,detail:detail||''});}
function fail(name,e){results.push({name,ok:false,detail:String(e&&e.stack||e)});}
async function test(name,fn){try{await fn();ok(name)}catch(e){fail(name,e)}}
function wait(ms){return new Promise(r=>setTimeout(r,ms))}
function fire(w,el,type){el.dispatchEvent(new w.Event(type,{bubbles:true,cancelable:true}))}
function setValue(w,id,value,type='change'){
  const el=w.document.getElementById(id);assert(el,'Missing '+id);el.value=String(value);fire(w,el,type);return el;
}
function click(w,id){
  const el=typeof id==='string'?w.document.getElementById(id):id;assert(el,'Missing '+id);el.click();return el;
}
function parseJSON(v){return JSON.parse(String(v||'{}'))}

const dom=new JSDOM(html,{
  url:'https://appassets.androidplatform.net/assets/index.html',
  runScripts:'outside-only',
  pretendToBeVisual:true
});
const w=dom.window;
const nativeState={
  secure:new Map(), calls:[], reminders:null, appLock:null, signedOut:false,
  savedFiles:[], sharedFiles:[], csvFiles:[], updateChecks:0, pushRefresh:0, tests:0, markAll:0, clears:0, installs:[], diagRuns:0, cacheClears:0, historyChecks:0
};
w.indexedDB=indexedDB;w.IDBKeyRange=IDBKeyRange;
w.TextEncoder=global.TextEncoder;w.TextDecoder=global.TextDecoder;
Object.defineProperty(w,'crypto',{value:webcrypto,configurable:true});
Object.defineProperty(w,'confirm',{value:()=>true,writable:true,configurable:true});
Object.defineProperty(w,'alert',{value:()=>{},writable:true,configurable:true});
w.scrollTo=()=>{};
w.matchMedia=()=>({matches:false,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}});
w.requestAnimationFrame=cb=>setTimeout(()=>cb(Date.now()),0);
w.cancelAnimationFrame=id=>clearTimeout(id);
w.requestIdleCallback=cb=>setTimeout(()=>cb({didTimeout:false,timeRemaining:()=>50}),0);
w.cancelIdleCallback=id=>clearTimeout(id);
w.HTMLElement.prototype.scrollIntoView=function(){};
if(w.HTMLCanvasElement)w.HTMLCanvasElement.prototype.getContext=function(){return{
  clearRect(){},save(){},restore(){},fillRect(){},translate(){},rotate(){},scale(){},drawImage(){},
  set fillStyle(v){},get fillStyle(){return'#000'}
}};
if(w.HTMLCanvasElement)w.HTMLCanvasElement.prototype.toDataURL=function(){return'data:image/jpeg;base64,AA=='};
if(!w.URL.createObjectURL)w.URL.createObjectURL=()=> 'blob:audit';
if(!w.URL.revokeObjectURL)w.URL.revokeObjectURL=()=>{};

function enc(ctx,v){return Buffer.from(JSON.stringify({ctx:String(ctx),v:String(v)}),'utf8').toString('base64')}
function dec(ctx,v){try{const o=JSON.parse(Buffer.from(String(v),'base64').toString('utf8'));return o.ctx===String(ctx)?o.v:null}catch(e){return null}}
w.Android={
  currentUserUid:()=> 'audit-user',
  secureStorageAvailable:()=>true,
  secureGet:k=>nativeState.secure.has(String(k))?nativeState.secure.get(String(k)):null,
  secureSet:(k,v)=>{nativeState.secure.set(String(k),String(v));return true},
  secureRemove:k=>{nativeState.secure.delete(String(k));return true},
  secureKeys:prefix=>JSON.stringify([...nativeState.secure.keys()].filter(k=>k.startsWith(String(prefix||'')))),
  secureClearPrefix:prefix=>{for(const k of [...nativeState.secure.keys()])if(k.startsWith(String(prefix)))nativeState.secure.delete(k);return true},
  secureReplacePrefix:(prefix,payload)=>{const p=String(prefix);for(const k of [...nativeState.secure.keys()])if(k.startsWith(p))nativeState.secure.delete(k);const o=parseJSON(payload);for(const k of Object.keys(o))nativeState.secure.set(k,String(o[k]));return true},
  secureEncryptValue:(ctx,v)=>enc(ctx,v),
  secureDecryptValue:(ctx,v)=>dec(ctx,v),
  authState:()=>setTimeout(()=>{if(typeof w.onNativeAuthChanged==='function')w.onNativeAuthChanged({signedIn:true,emailVerified:true,uid:'audit-user',email:'audit@example.com',name:'Audit User',photo:''})},0),
  emailSignIn:(e,p)=>nativeState.calls.push(['emailSignIn',e,p]),
  emailSignUp:(e,p)=>nativeState.calls.push(['emailSignUp',e,p]),
  googleSignIn:()=>nativeState.calls.push(['googleSignIn']),
  authProvider:()=> 'google.com',
  googleSignOut:()=>{nativeState.signedOut=true;nativeState.calls.push(['googleSignOut'])},
  resetPassword:e=>nativeState.calls.push(['resetPassword',e]),
  checkEmailVerified:()=>nativeState.calls.push(['checkEmailVerified']),
  resendVerification:()=>nativeState.calls.push(['resendVerification']),
  reminderSettings:()=>JSON.stringify(nativeState.reminders||{clockInEnabled:false,clockInTime:'09:30',clockOutEnabled:false,clockOutTime:'18:30',missedEnabled:false,missedTime:'21:00',permission:'granted'}),
  saveReminderSettings:j=>{nativeState.reminders=parseJSON(j);nativeState.calls.push(['saveReminderSettings',nativeState.reminders]);setTimeout(()=>w.onReminderSettingsSaved&&w.onReminderSettingsSaved(true,'Saved'),0)},
  requestNotificationPermission:()=>nativeState.calls.push(['requestNotificationPermission']),
  sendTestReminder:()=>{nativeState.tests++;nativeState.calls.push(['sendTestReminder'])},
  appLockState:()=>JSON.stringify(nativeState.appLock||{enabled:false,timeoutSeconds:30,deviceSecure:true}),
  setAppLockConfig:(e,t)=>{nativeState.appLock={enabled:!!e,timeoutSeconds:+t};nativeState.calls.push(['setAppLockConfig',!!e,+t]);setTimeout(()=>w.onAppLockConfigResult&&w.onAppLockConfigResult(true,'Saved'),0)},
  secureCloudBackup:p=>{nativeState.calls.push(['secureCloudBackup',p]);setTimeout(()=>w.onCloudBackupResult&&w.onCloudBackupResult(true,'Saved',Date.now()),0)},
  secureCloudRestore:()=>nativeState.calls.push(['secureCloudRestore']),
  cloudTransferBackup:()=>nativeState.calls.push(['cloudTransferBackup']),
  cloudTransferRestore:()=>nativeState.calls.push(['cloudTransferRestore']),
  cloudBackupHistoryList:()=>{nativeState.historyChecks++;nativeState.calls.push(['cloudBackupHistoryList']);setTimeout(()=>w.onCloudBackupHistory&&w.onCloudBackupHistory('[]'),0)},
  secureCloudRestoreHistory:id=>nativeState.calls.push(['secureCloudRestoreHistory',id]),
  saveBase64File:(n,m,d)=>{nativeState.savedFiles.push([n,m,String(d).length]);return true},
  saveCsv:(n,d)=>{nativeState.csvFiles.push([n,String(d)]);return true},
  shareBase64File:(n,m,d)=>{nativeState.sharedFiles.push([n,m,String(d).length]);return true},
  saveTextFile:(n,m,d)=>{nativeState.savedFiles.push([n,m,String(d).length]);return true},
  shareTextFile:(n,m,d)=>{nativeState.sharedFiles.push([n,m,String(d).length]);return true},
  toast:m=>nativeState.calls.push(['toast',String(m)]),
  checkForUpdates:()=>{nativeState.updateChecks++;nativeState.calls.push(['checkForUpdates'])},
  refreshPushRegistration:()=>{nativeState.pushRefresh++;nativeState.calls.push(['refreshPushRegistration'])},
  notificationState:()=>JSON.stringify({items:[],unread:0,pushTokenAvailable:true,topicUpdates:true,topicAll:true,topicError:'',versionName:'15.5.6',versionCode:40,permission:'granted'}),
  markAllNotificationsRead:()=>{nativeState.markAll++;nativeState.calls.push(['markAllNotificationsRead'])},
  clearNotifications:()=>{nativeState.clears++;nativeState.calls.push(['clearNotifications'])},
  installUpdate:(url,sha,ver)=>{nativeState.installs.push([url,sha,ver]);nativeState.calls.push(['installUpdate',url,sha,ver])},
  diagnosticsSummary:()=>{nativeState.diagRuns++;return JSON.stringify({versionName:'15.5.6',versionCode:40,sdk:35,androidRelease:'15',secureStorage:true,deviceSecure:true,backupKeyPresent:true,webViewFileAccess:false,safeBrowsing:true,appCheckEnabled:true,signedIn:true,emailVerified:true})},
  diagnosticsCloudBackup:()=>{setTimeout(()=>w.onDiagnosticsCloudStatus&&w.onDiagnosticsCloudStatus({ok:true,exists:false,bytes:0}),0)},
  clearDiagnosticsCache:()=>{nativeState.cacheClears++;nativeState.calls.push(['clearDiagnosticsCache']);setTimeout(()=>w.onDiagnosticsCacheCleared&&w.onDiagnosticsCacheCleared(true),0);return true},
  deleteAccountData:()=>nativeState.calls.push(['deleteAccountData']),
  deleteAccountDataWithPassword:p=>nativeState.calls.push(['deleteAccountDataWithPassword',p]),
  syncTodayPunchState:()=>{},
  openAppNotificationSettings:()=>nativeState.calls.push(['openAppNotificationSettings'])
};

const fakeListeners={};
w.lottie={
  loadAnimation(cfg){
    const listeners={};
    const a={
      totalFrames:96,currentFrame:0,
      addEventListener(n,cb){listeners[n]=cb;if(n==='DOMLoaded')setTimeout(cb,0)},
      playSegments(seg){this.currentFrame=Array.isArray(seg)?seg[1]||0:0;setTimeout(()=>listeners.complete&&listeners.complete(),0)},
      goToAndStop(f){this.currentFrame=+f||0},
      stop(){},destroy(){},setSpeed(){},setDirection(){}
    };
    return a;
  }
};
w.XLSX={utils:{book_new:()=>({}),aoa_to_sheet:()=>({}),book_append_sheet:()=>{}},write:()=>''};
w.ExcelJS=require('exceljs');

const errors=[];
w.addEventListener('error',e=>errors.push(String(e.error&&e.error.stack||e.message||e.error||'error')));
w.addEventListener('unhandledrejection',e=>errors.push(String(e.reason&&e.reason.stack||e.reason||'rejection')));

const skip=new Set(['lottie.min.js','xlsx.full.min.js','exceljs.min.js']);
for(const s of [...w.document.querySelectorAll('script')]){
  const src=s.getAttribute('src');
  try{
    if(src){
      const base=src.split('?')[0].split('/').pop();
      if(skip.has(base)||/^https?:/i.test(src))continue;
      const p=path.join(assets,src.replace(/^\.\//,''));
      if(!fs.existsSync(p))throw new Error('Missing script '+src);
      w.eval(fs.readFileSync(p,'utf8')+'\n//# sourceURL='+src);
    }else if(String(s.textContent||'').trim()){
      w.eval(s.textContent);
    }
  }catch(e){errors.push('load '+(src||'inline')+': '+e.stack)}
}

(async()=>{
  await wait(2300);

  await test('Core app initialized without JavaScript errors',async()=>{
    assert(w.AttendanceAppApi,'AttendanceAppApi missing');
    assert.strictEqual(errors.length,0,errors.join('\n'));
  });

  await test('HTML contains no duplicate IDs',async()=>{
    const seen=new Set(),dups=[];
    for(const el of w.document.querySelectorAll('[id]')){if(seen.has(el.id))dups.push(el.id);seen.add(el.id)}
    assert.deepStrictEqual(dups,[]);
  });

  await test('Bottom navigation buttons open their screens',async()=>{
    for(const b of w.document.querySelectorAll('.bottomNav [data-screen], nav [data-screen]')){
      const name=b.getAttribute('data-screen');if(!name)continue;b.click();await wait(5);
      const screen=w.document.getElementById('screen-'+name);assert(screen,'Missing screen '+name);
      assert(screen.classList.contains('active'),'Screen did not activate: '+name);
    }
  });

  await test('Every Settings menu row opens its matching page and Back works',async()=>{
    const rows=[...w.document.querySelectorAll('.settingsMenuRow[data-setting]')];assert(rows.length>=8,'Too few settings rows');
    for(const row of rows){
      const name=row.getAttribute('data-setting');row.click();await wait(3);
      const screen=w.document.getElementById('screen-setting-'+name);assert(screen,'Missing setting screen '+name);
      assert(screen.classList.contains('active'),'Setting did not open: '+name);
      const back=screen.querySelector('.settingBack');assert(back,'Missing back: '+name);back.click();await wait(3);
      assert(w.document.getElementById('screen-settings').classList.contains('active'),'Back failed: '+name);
    }
  });

  await test('Work & Time inputs persist',async()=>{
    setValue(w,'stdHours',8);setValue(w,'stdMinutes',30);setValue(w,'otDelay',15);
    const s=parseJSON(w.localStorage.getItem('attendance_settings_v8'));
    assert.strictEqual(+s.h,8);assert.strictEqual(+s.m,30);assert.strictEqual(+s.otDelay,15);
  });

  await test('12/24 hour format controls persist',async()=>{
    click(w,'fmt24');await wait(10);
    let s=parseJSON(w.localStorage.getItem('attendance_settings_v8'));assert.strictEqual(s.fmt,'24h');
    click(w,'fmt12');await wait(10);
    s=parseJSON(w.localStorage.getItem('attendance_settings_v8'));assert.strictEqual(s.fmt,'12h');
  });

  await test('Profile fields persist including DOB, joining, department and employee ID',async()=>{
    setValue(w,'profileName','Audit Person','input');setValue(w,'profileJob','Designer','input');
    setValue(w,'profileCompany','Audit Co','input');setValue(w,'profileDepartment','Design','input');
    setValue(w,'profileEmployeeId','EMP-42','input');setValue(w,'profileDob','1999-01-02');
    setValue(w,'profileJoining','2025-04-05');setValue(w,'profileAppTitle','My Attendance','input');
    click(w,'saveProfile');await wait(20);
    const p=parseJSON(w.localStorage.getItem('attendance_profile_v81'));
    assert.strictEqual(p.name,'Audit Person');assert.strictEqual(p.department,'Design');assert.strictEqual(p.employeeId,'EMP-42');
    assert.strictEqual(p.dob,'1999-01-02');assert.strictEqual(p.dateOfJoining,'2025-04-05');
  });

  await test('Typography selections persist',async()=>{
    setValue(w,'fontFamilySelect','arial');setValue(w,'fontSmallScale','1.1');setValue(w,'fontBodyScale','1.1');
    const t=parseJSON(w.localStorage.getItem('attendance_typography_v112'));
    assert.strictEqual(t.family,'arial');assert(Math.abs(+t.small-1.1)<0.001);assert(Math.abs(+t.body-1.1)<0.001);
  });

  await test('Typography reset restores defaults',async()=>{
    click(w,'resetTypographyBtn');await wait(15);
    assert.strictEqual(w.document.getElementById('fontFamilySelect').value,'default');
    assert.strictEqual(+w.document.getElementById('fontSmallScale').value,1);
  });

  await test('Salary Save persists and immediately recalculates summary',async()=>{
    setValue(w,'salaryAmount','40000','input');setValue(w,'salaryOtMultiplier','1.5');
    click(w,'saveSalary');await wait(30);
    const s=parseJSON(w.localStorage.getItem('attendance_salary_v9'));
    assert.strictEqual(+s.monthly,40000);assert.strictEqual(+s.otMultiplier,1.5);
    assert.notStrictEqual(w.document.getElementById('salaryDaily').textContent,'₹0');
    assert.notStrictEqual(w.document.getElementById('salaryEstimated').textContent,'₹0');
    assert(/saved/i.test(w.document.getElementById('salarySaveStatus').textContent));
  });

  await test('Reports & Analytics reflects saved salary',async()=>{
    w.AttendanceAppApi.showScreen('setting-reports');await wait(25);
    const rs=w.document.getElementById('reportSalary');assert(rs,'reportSalary missing');
    assert.notStrictEqual(rs.textContent,'₹0');
    assert(/40,000|40000/.test(rs.textContent),'Reports salary did not reflect ₹40,000: '+rs.textContent);
  });

  await test('Leave setup add/save/delete paths persist',async()=>{
    setValue(w,'totalLeaves','20');
    click(w,'addLeaveCategory');await wait(5);
    const rows=[...w.document.querySelectorAll('#leaveSetupRows .leaveSetupRow')];assert(rows.length>=1);
    const last=rows[rows.length-1];last.querySelector('.catName').value='Audit Leave';last.querySelector('.catAllowed').value='3';
    click(w,'saveLeaves');await wait(10);
    let l=parseJSON(w.localStorage.getItem('attendance_leave_setup_v81'));
    assert(l.categories.some(x=>x.name==='Audit Leave'&&+x.allowed===3));
    const target=[...w.document.querySelectorAll('#leaveSetupRows .leaveSetupRow')].find(r=>r.querySelector('.catName').value==='Audit Leave');
    assert(target);target.querySelector('.leaveSetupDelete').click();click(w,'saveLeaves');await wait(10);
    l=parseJSON(w.localStorage.getItem('attendance_leave_setup_v81'));
    assert(!l.categories.some(x=>x.name==='Audit Leave'));
  });

  await test('Add Attendance Reset clears user-entered fields',async()=>{
    w.AttendanceAppApi.showScreen('add');await wait(5);
    setValue(w,'notesInput','Temporary note','input');setValue(w,'reasonInput','Temporary reason','input');setValue(w,'statusInput','Absent');
    click(w,'resetBtn');await wait(10);
    assert.strictEqual(w.document.getElementById('notesInput').value,'');
    assert.strictEqual(w.document.getElementById('reasonInput').value,'');
    assert.strictEqual(w.document.getElementById('statusInput').value,'Present');
    assert(/^\d{4}-\d{2}-\d{2}$/.test(w.document.getElementById('dateInput').value));
  });

  await test('Add Attendance saves all core inputs',async()=>{
    w.AttendanceAppApi.showScreen('add');
    setValue(w,'dateInput','2026-10-19');setValue(w,'statusInput','Present');
    setValue(w,'checkInH','9');setValue(w,'checkInM','0');setValue(w,'checkInP','AM');
    setValue(w,'checkOutH','6');setValue(w,'checkOutM','30');setValue(w,'checkOutP','PM');
    setValue(w,'reasonInput','Audit reason','input');setValue(w,'notesInput','Audit note','input');
    click(w,'saveBtn');await wait(20);
    const a=parseJSON(w.localStorage.getItem('attendance_v8'));
    const x=a.find(r=>r.date==='2026-10-19');assert(x,'Attendance not saved');
    assert.strictEqual(x.status,'Present');assert.strictEqual(x.checkIn,'09:00');assert.strictEqual(x.checkOut,'18:30');
    assert.strictEqual(x.notes,'Audit note');
  });

  await test('Edit Attendance Save, Cancel, Close and Delete all work',async()=>{
    let a=parseJSON(w.localStorage.getItem('attendance_v8'));let x=a.find(r=>r.date==='2026-10-19');assert(x);
    w.AttendanceAppApi.openEdit(x.id);await wait(5);
    assert(w.document.getElementById('editModal').classList.contains('show'));
    setValue(w,'editPopupNotes','Edited audit note','input');click(w,'editSave');await wait(15);
    a=parseJSON(w.localStorage.getItem('attendance_v8'));x=a.find(r=>r.id===x.id);assert.strictEqual(x.notes,'Edited audit note');
    w.AttendanceAppApi.openEdit(x.id);click(w,'editCancel');await wait(5);assert(!w.document.getElementById('editModal').classList.contains('show'));
    w.AttendanceAppApi.openEdit(x.id);click(w,'editClose');await wait(5);assert(!w.document.getElementById('editModal').classList.contains('show'));
    w.AttendanceAppApi.openEdit(x.id);
    var deleteCalls=0,deleteArgs=[],deleteSnapshots=[],originalDelete=w.AttendanceAppApi.deleteRecord;
    w.AttendanceAppApi.deleteRecord=function(id){
      deleteCalls++;deleteArgs.push(String(id));
      deleteSnapshots.push({before:w.localStorage.getItem('attendance_v8'),hidden:w.document.getElementById('editPopupId').value});
      var out=originalDelete(id);
      deleteSnapshots[deleteSnapshots.length-1].after=w.localStorage.getItem('attendance_v8');
      return out
    };
    click(w,'editPopupDelete');await wait(20);
    a=parseJSON(w.localStorage.getItem('attendance_v8'));
    if(a.some(r=>r.id===x.id)){
      const confirmBtn=[...w.document.querySelectorAll('#appDialogOverlay .appDialogBtn')].find(b=>/^Confirm$/i.test(String(b.textContent||'').trim()));
      assert(confirmBtn,'Attendance delete confirmation dialog did not appear');
      confirmBtn.click();await wait(40);
    }
    assert(deleteCalls>0,'Delete Attendance button did not invoke deleteRecord');
    assert(deleteArgs.includes(String(x.id)),'Delete button passed wrong record id: '+JSON.stringify(deleteArgs)+' hidden='+w.document.getElementById('editPopupId').value);
    a=parseJSON(w.localStorage.getItem('attendance_v8'));
    if(a.some(r=>r.id===x.id))console.log('ATTENDANCE DELETE DEBUG',JSON.stringify(deleteSnapshots),'SOURCE',sourceSnippet('function deleteRecord'));
    assert(!a.some(r=>r.id===x.id),'Attendance record remained after confirming deletion');
  });

  await test('Empty Attendance calendar date opens Add with date prefilled',async()=>{
    w.AttendanceAppApi.showScreen('attendance');await wait(30);
    const cells=[...w.document.querySelectorAll('#attendanceCalendar .v15Day[data-date]')];
    assert(cells.length>0,'No calendar day cells rendered');
    const cell=cells.find(el=>!el.querySelector('.present,.absent,.leave,.special'))||cells[0];
    const date=cell.getAttribute('data-date');cell.click();await wait(20);
    assert(w.document.getElementById('screen-add').classList.contains('active'),'Add screen did not open');
    assert.strictEqual(w.document.getElementById('dateInput').value,date);
  });

  await test('Theme Light/Dark buttons and JSON toggle persist correctly',async()=>{
    click(w,'themeDark');await wait(15);assert.strictEqual(w.localStorage.getItem('attendance_theme_v9'),'dark');assert(w.document.body.classList.contains('dark-mode'));
    click(w,'themeLight');await wait(15);assert.strictEqual(w.localStorage.getItem('attendance_theme_v9'),'light');assert(!w.document.body.classList.contains('dark-mode'));
    const json=w.document.querySelector('#v1551ThemeToggle .v155ThemeLottie');assert(json);json.click();await wait(30);
    assert.strictEqual(w.localStorage.getItem('attendance_theme_v9'),'dark');assert(w.document.body.classList.contains('dark-mode'));
  });

  await test('Smart Reminder inputs save to native layer and test button works',async()=>{
    const ci=w.document.getElementById('remClockInEnabled'),co=w.document.getElementById('remClockOutEnabled'),mi=w.document.getElementById('remMissedEnabled');
    ci.checked=true;co.checked=true;mi.checked=true;
    setValue(w,'remClockInTime','09:15');setValue(w,'remClockOutTime','18:45');setValue(w,'remMissedTime','21:30');
    click(w,'saveRemindersBtn');await wait(20);assert(nativeState.reminders);assert.strictEqual(nativeState.reminders.clockInTime,'09:15');assert(nativeState.reminders.missedEnabled);
    click(w,'testReminderBtn');assert(nativeState.tests>0);
  });

  await test('Privacy & App Lock saves configuration',async()=>{
    const t=w.document.getElementById('appLockToggle');t.checked=true;setValue(w,'appLockTimeout','60');
    click(w,'saveAppLockBtn');await wait(20);assert(nativeState.appLock);assert.strictEqual(nativeState.appLock.enabled,true);assert.strictEqual(nativeState.appLock.timeoutSeconds,60);
  });

  await test('Cloud Backup button invokes native backup with a snapshot',async()=>{
    click(w,'cloudBackupBtn');await wait(10);
    const call=nativeState.calls.find(x=>x[0]==='secureCloudBackup');assert(call,'Cloud backup not invoked');
    const snap=parseJSON(call[1]);assert.strictEqual(snap.userUid,'audit-user');assert(snap.storage&&typeof snap.storage==='object');
  });

  await test('Cloud Restore and backup history controls invoke native layer',async()=>{
    click(w,'cloudRestoreBtn');await wait(10);
    let cont=[...w.document.querySelectorAll('#appDialogOverlay .appDialogBtn')].find(b=>/^Continue$/i.test(String(b.textContent||'').trim()));
    assert(cont,'Cloud Restore confirmation missing');cont.click();await wait(10);
    assert(nativeState.calls.some(x=>x[0]==='secureCloudRestore'),'secureCloudRestore not invoked');
    const refresh=w.document.getElementById('refreshBackupHistoryBtn');if(refresh){refresh.click();await wait(15);assert(nativeState.historyChecks>0,'Backup history not requested')}
  });

  await test('Switch-device Restore accepts Transfer PIN and invokes native layer',async()=>{
    click(w,'cloudTransferRestoreBtn');await wait(10);
    const input=w.document.getElementById('appDialogInput');assert(input,'Transfer PIN input missing');input.value='123456';
    const cont=[...w.document.querySelectorAll('#appDialogOverlay .appDialogBtn')].find(b=>/^Continue$/i.test(String(b.textContent||'').trim()));
    assert(cont,'Transfer restore Continue missing');cont.click();await wait(15);
    assert(nativeState.calls.some(x=>x[0]==='cloudTransferRestore'),'cloudTransferRestore not invoked');
  });

  await test('Switch-device Backup validates PIN twice and uploads encrypted backup',async()=>{
    click(w,'cloudTransferBackupBtn');await wait(10);
    let input=w.document.getElementById('appDialogInput');assert(input,'Create Transfer PIN input missing');input.value='654321';
    let cont=[...w.document.querySelectorAll('#appDialogOverlay .appDialogBtn')].find(b=>/^Continue$/i.test(String(b.textContent||'').trim()));assert(cont);cont.click();await wait(10);
    input=w.document.getElementById('appDialogInput');assert(input,'Confirm Transfer PIN input missing');input.value='654321';
    cont=[...w.document.querySelectorAll('#appDialogOverlay .appDialogBtn')].find(b=>/^Continue$/i.test(String(b.textContent||'').trim()));assert(cont);cont.click();
    for(let i=0;i<30&&!nativeState.calls.some(x=>x[0]==='cloudTransferBackup');i++)await wait(100);
    assert(nativeState.calls.some(x=>x[0]==='cloudTransferBackup'),'Encrypted switch-device backup was not uploaded');
  });

  await test('Document save and delete persist in encrypted IndexedDB',async()=>{
    setValue(w,'docType','Other');setValue(w,'docName','Audit Document','input');setValue(w,'docIssue','2026-01-02');setValue(w,'docExpiry','2027-01-02');setValue(w,'docNotes','Audit doc note','input');
    const inp=w.document.getElementById('docFile');const file=new w.File(['hello audit'],'audit.txt',{type:'text/plain'});
    Object.defineProperty(inp,'files',{configurable:true,value:[file]});fire(w,inp,'change');click(w,'saveDocument');await wait(500);
    assert.strictEqual(await w.attendanceDocumentCount(),1);
    const exportBtn=w.document.querySelector('#documentList .docExport'),shareBtn=w.document.querySelector('#documentList .docShare');
    assert(exportBtn&&shareBtn,'Document Export/Share buttons missing');
    exportBtn.click();await wait(120);shareBtn.click();await wait(120);
    assert(nativeState.savedFiles.some(x=>x[0]==='audit.txt'),'Document export did not reach native save');
    assert(nativeState.sharedFiles.some(x=>x[0]==='audit.txt'),'Document share did not reach native share');
    const del=w.document.querySelector('#documentList .docDelete');assert(del,'Document delete button missing');
    assert(typeof w.document.getElementById('documentList').onclick==='function','Document list delegated click handler missing');
    del.click();await wait(30);
    if((await w.attendanceDocumentCount())!==0){
      const confirmBtn=[...w.document.querySelectorAll('#appDialogOverlay .appDialogBtn')].find(b=>/^Confirm$/i.test(String(b.textContent||'').trim()));
      assert(confirmBtn,'Document delete confirmation dialog did not appear');
      confirmBtn.click();await wait(350);
    }
    assert.strictEqual(await w.attendanceDocumentCount(),0,'Document remained after confirming deletion');
  });

  await test('Home Clock In and Clock Out buttons save punch state',async()=>{
    const today=new Date().toISOString().slice(0,10);
    let records=parseJSON(w.localStorage.getItem('attendance_v8')||'[]');
    records=records.filter(r=>r.date!==today);
    assert(w.AttendanceAppApi.verifiedStorageSet('attendance_v8',records,'attendance'));
    w.AttendanceAppApi.showScreen('home');w.AttendanceAppApi.renderAll();await wait(10);
    click(w,'punchBtn');await wait(25);
    records=parseJSON(w.localStorage.getItem('attendance_v8'));let cur=records.find(r=>r.date===today);
    assert(cur&&cur.checkIn&&!cur.checkOut,'Clock In did not create an open shift');
    click(w,'punchBtn');await wait(15);
    const yes=w.document.getElementById('clockOutYes');assert(yes,'Clock Out confirmation did not open');yes.click();await wait(30);
    records=parseJSON(w.localStorage.getItem('attendance_v8'));cur=records.find(r=>r.date===today);
    assert(cur&&cur.checkOut,'Clock Out did not save checkout time');
    records=records.filter(r=>r.date!==today);
    assert(w.AttendanceAppApi.verifiedStorageSet('attendance_v8',records,'attendance'));
  });

  await test('CSV export button produces a native CSV file',async()=>{
    // Seed one exportable record through the same verified storage layer.
    const rec=[{id:'export-audit',date:'2026-10-20',status:'Present',checkIn:'09:00',checkOut:'18:00',reason:'',notes:''}];
    assert(w.AttendanceAppApi.verifiedStorageSet('attendance_v8',rec,'attendance'));
    click(w,'exportBtn');await wait(20);
    assert(nativeState.csvFiles.length>0,'CSV export did not invoke native saveCsv');
    assert(/Date,Status,Check In/.test(nativeState.csvFiles[nativeState.csvFiles.length-1][1]));
  });

  await test('Excel export picker, Cancel and actual export work',async()=>{
    click(w,'exportExcelBtn');await wait(15);
    assert(w.document.getElementById('excelExportOverlay'),'Excel export picker did not open');
    click(w,'excelExportCancel');await wait(10);
    assert(!w.document.getElementById('excelExportOverlay'),'Excel export picker did not close');
    const before=nativeState.savedFiles.length;
    click(w,'exportExcelBtn');await wait(15);assert(w.document.getElementById('excelExportOverlay'));
    click(w,'excelExportGo');await wait(500);
    assert(nativeState.savedFiles.length>before,'Excel export did not save a file');
    assert(nativeState.savedFiles.some(x=>/\.xlsx$/i.test(x[0])),'No XLSX file was produced');
  });

  await test('Attendance search/filter/month navigation controls respond',async()=>{
    w.AttendanceAppApi.showScreen('attendance');await wait(15);
    const before=w.document.getElementById('monthFilter').value;click(w,'attendancePrevMonth');await wait(5);assert.notStrictEqual(w.document.getElementById('monthFilter').value,before);
    click(w,'attendanceNextMonth');await wait(5);assert.strictEqual(w.document.getElementById('monthFilter').value,before);
    setValue(w,'attendanceSearch','audit','input');await wait(120);click(w,'attendanceClearFilters');await wait(5);assert.strictEqual(w.document.getElementById('attendanceSearch').value,'');
  });

  await test('Notification Center update, push, mark-read, clear and install actions work',async()=>{
    const check=w.document.getElementById('notificationCheckUpdates');assert(check,'Check for Updates missing');check.click();await wait(5);assert(nativeState.updateChecks>0);
    const refresh=w.document.getElementById('notificationPushRefresh');assert(refresh,'Refresh Push missing');refresh.click();await wait(5);assert(nativeState.pushRefresh>0);
    click(w,'notificationMarkAll');await wait(5);assert(nativeState.markAll>0,'Mark All Read did not invoke native layer');
    click(w,'notificationClear');await wait(5);
    let clearBtn=[...w.document.querySelectorAll('#appDialogOverlay .appDialogBtn')].find(b=>/^Clear$/i.test(String(b.textContent||'').trim()));
    assert(clearBtn,'Clear Notifications confirmation missing');clearBtn.click();await wait(10);assert(nativeState.clears>0,'Clear Notifications did not invoke native layer');
    const state={items:[{type:'update',title:'Audit update',body:'Test',version:'99.0',versionCode:999,apkUrl:'https://example.com/a.apk',sha256:'abc',receivedAt:Date.now(),read:false}],unread:1,permission:'granted',versionName:'15.5.6',versionCode:40,pushTokenAvailable:true,topicUpdates:true,topicAll:true,topicError:''};
    w.onNativeNotificationState(state);await wait(10);
    const install=w.document.querySelector('.installUpdateBtn');assert(install&&!install.disabled,'Install Update button missing/disabled');install.click();await wait(5);
    assert(nativeState.installs.length>0,'Install Update did not invoke native installer');
  });

  await test('Diagnostics health check, cache clear, support report and Backup navigation work',async()=>{
    w.AttendanceAppApi.showScreen('setting-diagnostics');await wait(20);
    click(w,'diagRunBtn');await wait(30);assert(nativeState.diagRuns>0,'Diagnostics native summary not requested');
    assert(w.document.getElementById('diagnosticsSummary').textContent.trim().length>0);
    const beforeFiles=nativeState.savedFiles.length;click(w,'diagReportBtn');await wait(20);assert(nativeState.savedFiles.length>beforeFiles,'Support report was not saved');
    click(w,'diagClearCacheBtn');await wait(15);assert(nativeState.cacheClears>0,'Clear cache not invoked');
    // Close any informational dialog before testing navigation.
    const okBtn=[...w.document.querySelectorAll('#appDialogOverlay .appDialogBtn')].find(b=>/^OK$/i.test(String(b.textContent||'').trim()));if(okBtn)okBtn.click();
    click(w,'diagBackupBtn');await wait(10);assert(w.document.getElementById('screen-setting-backup').classList.contains('active'),'Backup & Restore navigation failed');
  });

  await test('Delete Profile multi-step verification reaches native delete only after confirmations',async()=>{
    nativeState.calls=nativeState.calls.filter(x=>x[0]!=='deleteAccountData');
    click(w,'deleteProfileBtn');await wait(10);
    let btn=[...w.document.querySelectorAll('#appDialogOverlay .appDialogBtn')].find(b=>/^Continue$/i.test(String(b.textContent||'').trim()));assert(btn,'Delete Profile Continue missing');btn.click();await wait(10);
    let input=w.document.getElementById('appDialogInput');assert(input,'Delete Profile email verification input missing');input.value='audit@example.com';
    btn=[...w.document.querySelectorAll('#appDialogOverlay .appDialogBtn')].find(b=>/^Verify$/i.test(String(b.textContent||'').trim()));assert(btn,'Verify button missing');btn.click();await wait(10);
    input=w.document.getElementById('appDialogInput');assert(input,'DELETE confirmation input missing');input.value='DELETE';
    btn=[...w.document.querySelectorAll('#appDialogOverlay .appDialogBtn')].find(b=>/Delete permanently/i.test(String(b.textContent||'').trim()));assert(btn,'Delete permanently button missing');btn.click();await wait(10);
    btn=[...w.document.querySelectorAll('#appDialogOverlay .appDialogBtn')].find(b=>/^Continue$/i.test(String(b.textContent||'').trim()));assert(btn,'Google re-auth Continue missing');btn.click();await wait(15);
    assert(nativeState.calls.some(x=>x[0]==='deleteAccountData'),'Native account deletion was not invoked after full verification');
  });

  await test('Logout button opens confirmation and invokes sign-out',async()=>{
    click(w,'settingsLogoutBtn');await wait(5);
    const dlg=w.document.querySelector('.appDialogOverlay.show,.dialogOverlay.show,[data-app-dialog]');
    const confirmBtn=[...w.document.querySelectorAll('button')].find(b=>/Log Out/i.test(b.textContent||'')&&b.id!=='settingsLogoutBtn');
    if(confirmBtn)confirmBtn.click();await wait(10);
    assert(nativeState.signedOut,'Native sign-out was not invoked');
  });

  await test('Important action buttons exist after all UI patches',async()=>{
    const ids=['saveBtn','resetBtn','saveSalary','saveProfile','saveLeaves','saveDocument','saveRemindersBtn','testReminderBtn','saveAppLockBtn','settingsLogoutBtn','editClose','editCancel','editSave','editPopupDelete'];
    for(const id of ids)assert(w.document.getElementById(id),'Missing '+id);
    assert(w.AttendanceAppApi&&typeof w.AttendanceAppApi.saveSalary==='function','Salary save API missing');
    assert(w.AttendanceAppApi&&typeof w.AttendanceAppApi.saveEdit==='function','Edit save API missing');
    assert(w.AttendanceAppApi&&typeof w.AttendanceAppApi.deleteRecord==='function','Delete API missing');
  });

  await wait(50);
  if(errors.length)fail('No late JavaScript errors',new Error(errors.join('\n')));else ok('No late JavaScript errors');

  const passed=results.filter(x=>x.ok).length,failed=results.length-passed;
  console.log('\nFUNCTIONAL AUDIT RESULTS');
  for(const r of results)console.log((r.ok?'PASS ':'FAIL ')+r.name+(r.detail?'\n  '+r.detail.replace(/\n/g,'\n  '):''));
  console.log(`\nSummary: ${passed} passed, ${failed} failed`);
  if(failed)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
