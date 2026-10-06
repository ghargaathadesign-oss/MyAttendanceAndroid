from pathlib import Path
import re,sys,shutil
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
index=assets/'index.html'; app=assets/'app.js'
h=index.read_text(encoding='utf-8'); s=app.read_text(encoding='utf-8')

if 'v152-ui.css' not in h:
    if '<link rel="stylesheet" href="v151-ui.css">' not in h: raise SystemExit('v15.1 CSS anchor missing')
    h=h.replace('<link rel="stylesheet" href="v151-ui.css">','<link rel="stylesheet" href="v151-ui.css">\n<link rel="stylesheet" href="v152-ui.css">',1)

if 'v152-fixes.js' not in h:
    if '<script src="v151-ui.js"></script>' not in h: raise SystemExit('v15.1 JS anchor missing')
    h=h.replace('<script src="v151-ui.js"></script>','<script src="v151-ui.js"></script>\n<script src="v152-fixes.js"></script>',1)

salary_old="""function renderSalary(){
 var s=salaryGet(),c=salaryCalc(monthNow());E('salaryAmount').value=s.monthly||'';E('salaryOtMultiplier').value=String(s.otMultiplier);E('salaryDaily').textContent=money(c.dayRate);E('salaryPaidDays').textContent=c.paid;E('salaryOTPay').textContent=money(c.otPay);E('salaryEstimated').textContent=money(c.earned)
}"""
salary_new="""function renderSalary(){
 var s=salaryGet(),c=salaryCalc(monthNow()),paid=Number(c.paid)||0,paidText=Math.abs(paid-Math.round(paid))<0.005?String(Math.round(paid)):paid.toFixed(2).replace(/0+$/,'').replace(/\\.$/,'');
 E('salaryAmount').value=s.monthly||'';E('salaryOtMultiplier').value=String(s.otMultiplier);E('salaryDaily').textContent=money(c.dayRate);E('salaryPaidDays').textContent=paidText;E('salaryOTPay').textContent=money(c.otPay);E('salaryEstimated').textContent=money(c.earned)
}"""
if salary_old not in s: raise SystemExit('renderSalary anchor missing')
s=s.replace(salary_old,salary_new,1)

start_old="""function startUserScopedApp(){var go=function(){init()},ready=window.attendanceDocumentsReady||window.attendanceStorageReady;if(ready&&typeof ready.then==='function')ready.then(go).catch(go);else go()}"""
start_new="""function startUserScopedApp(){
 var started=false,go=function(){if(started)return;started=true;init();try{document.documentElement.classList.remove('v152BootSync')}catch(e){}},ready=window.attendanceDocumentsReady||window.attendanceStorageReady,authReady=window.attendanceAuthReadyPromise;
 if(window.Android&&Android.authState){try{Android.authState()}catch(e){}}
 if(window.Promise){
   Promise.all([ready&&typeof ready.then==='function'?ready:Promise.resolve(),authReady&&typeof authReady.then==='function'?authReady:Promise.resolve()]).then(go).catch(go);
   setTimeout(go,1800)
 }else go()
}"""
if start_old not in s: raise SystemExit('startUserScopedApp anchor missing')
s=s.replace(start_old,start_new,1)
app.write_text(s,encoding='utf-8')

old='''        <small class="cloudStatus" id="cloudStatus">Ready. Your backup is protected by this device.</small>
        <div class="label" style="margin-top:22px">SWITCHING TO A NEW PHONE?</div>
        <p class="helpText">Create a portable encrypted backup with a Transfer PIN. On the new phone, sign in to the same account and enter that PIN.</p>
        <div class="cloudActions"><button class="btn ghost" id="cloudTransferBackupBtn" type="button">Backup for New Device</button><button class="btn ghost" id="cloudTransferRestoreBtn" type="button">Restore on New Device</button></div>
      </div>
      <div class="settingsCard"><div class="typographyHead"><span><b>Encrypted Restore Points</b>'''
new='''        <small class="cloudStatus" id="cloudStatus">Ready. Your backup is protected by this device.</small>
      </div>
      <div class="settingsCard switchDeviceCard">
        <div class="label">SWITCHING TO A NEW PHONE?</div>
        <p class="helpText">Create a portable encrypted backup with a Transfer PIN. On the new phone, sign in to the same account and enter that PIN.</p>
        <div class="cloudActions"><button class="btn ghost" id="cloudTransferBackupBtn" type="button">Backup for New Device</button><button class="btn ghost" id="cloudTransferRestoreBtn" type="button">Restore on New Device</button></div>
      </div>
      <div class="settingsCard"><div class="typographyHead"><span><b>Encrypted Restore Points</b>'''
if old not in h: raise SystemExit('switch-device backup section anchor missing')
h=h.replace(old,new,1)
index.write_text(h,encoding='utf-8')

shutil.copy('ci/v152-ui.css',assets/'v152-ui.css')
shutil.copy('ci/v152-fixes.js',assets/'v152-fixes.js')
print('v15.2 startup, salary, calendar spacing and backup-section patch applied')
