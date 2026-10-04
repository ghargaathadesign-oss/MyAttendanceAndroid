from pathlib import Path
import re, sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')

p=assets/'app.js'; s=p.read_text(encoding='utf-8')
s=s.replace("function setGet(){var s={h:8,m:0,fmt:'12h',otDelay:30}","function setGet(){var s={h:9,m:0,fmt:'12h',otDelay:30}",1)
s=s.replace("function leaveGet(){var d={total:20,","function leaveGet(){var d={total:18,",1)
old="function requiredMinutesForStatus(st){var s=setGet(),std=s.h*60+s.m;if(st==='Paid Leave'||st==='Holiday'||st==='Week Off')return 0;if(st==='Half Day')return Math.round(std/2);return std}"
new="function requiredMinutesForStatus(st){return window.AttendancePolicy?AttendancePolicy.requiredMinutes({status:st},setGet()):(setGet().h*60+setGet().m)}"
if old not in s: raise SystemExit('app requiredMinutes anchor missing')
s=s.replace(old,new,1)
old="function dailyBalanceMinutes(x){var s=setGet(),req=requiredMinutesForStatus(x.status),worked=workMinutes(x.checkIn,x.checkOut),diff;if(isSpecialOTRecord(x))return worked;if(x.status==='Paid Leave')return 0;if(x.status==='Absent'||x.status==='Unpaid Leave')return-req;diff=worked-req;return diff>0?Math.max(0,diff-s.otDelay):diff}"
new="function dailyBalanceMinutes(x){return window.AttendancePolicy?AttendancePolicy.balanceMinutes(x,setGet()):0}"
if old not in s: raise SystemExit('app dailyBalance anchor missing')
s=s.replace(old,new,1)
salary_pat=re.compile(r"function salaryCalc\(month\)\{.*?\n\}\nfunction money",re.S)
m=salary_pat.search(s)
if not m: raise SystemExit('salaryCalc block missing')
salary_new="function salaryCalc(month){if(window.AttendancePolicy)return AttendancePolicy.salaryMonth(dataGet(),month,setGet(),salaryGet());return{days:0,paid:0,ot:0,net:0,shortfall:0,dayRate:0,hourRate:0,otPay:0,earned:0}}\nfunction money"
s=s[:m.start()]+salary_new+s[m.end():]
old="balance=Math.max(0,cfg.total-paid);pct=cfg.total?Math.round(balance/cfg.total*100):0;E('leaveBalance').textContent=balance;E('leaveAccrued').textContent=cfg.total;E('leaveUsed').textContent=paid;"
new="var accrued=window.AttendancePolicy?AttendancePolicy.leaveAccrued(new Date(),cfg.total,1.5):cfg.total;balance=Math.max(0,accrued-paid);pct=accrued?Math.round(balance/accrued*100):0;E('leaveBalance').textContent=balance;E('leaveAccrued').textContent=accrued;E('leaveUsed').textContent=paid;"
if old not in s: raise SystemExit('leave accrual anchor missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

p=assets/'v112-fixes.js'; s=p.read_text(encoding='utf-8')
old="function getSettings(){var s={h:9,m:0,otDelay:30,fmt:'12h'};try{var o=JSON.parse(localStorage.getItem('attendance_settings_v8')||'{}')||{};if(typeof o.h!=='undefined')s.h=+o.h||0;if(typeof o.m!=='undefined')s.m=+o.m||0;if(typeof o.otDelay!=='undefined')s.otDelay=+o.otDelay||0;if(o.fmt==='24h')s.fmt='24h'}catch(e){}return s}"
new="function getSettings(){var s={h:9,m:0,otDelay:30,fmt:'12h'};try{var o=JSON.parse(localStorage.getItem('attendance_settings_v8')||'{}')||{};for(var k in o)s[k]=o[k]}catch(e){}return window.AttendancePolicy?AttendancePolicy.normalizeSettings(s):s}"
if old not in s: raise SystemExit('v112 settings anchor missing')
s=s.replace(old,new,1)
old="function workMinutes(x){if(!x||!x.checkIn||!x.checkOut)return 0;var a=minFrom(x.checkIn),b=minFrom(x.checkOut);if(b<a)b+=1440;return b-a}"
new="function workMinutes(x){return window.AttendancePolicy?AttendancePolicy.workedMinutes(x):0}"
if old not in s: raise SystemExit('v112 workMinutes anchor missing')
s=s.replace(old,new,1)
old="function requiredMinutes(x,std){if(!x)return 0;if(x.status==='Paid Leave'||x.status==='Holiday'||x.status==='Week Off')return 0;if(x.status==='Half Day')return Math.round(std/2);return std}"
new="function requiredMinutes(x,std){var h=Math.floor((+std||0)/60),m=(+std||0)%60;return window.AttendancePolicy?AttendancePolicy.requiredMinutes(x,{h:h,m:m,otDelay:getSettings().otDelay}):0}"
if old not in s: raise SystemExit('v112 required anchor missing')
s=s.replace(old,new,1)
old="function balanceMinutes(x,s){var std=s.h*60+s.m,r=requiredMinutes(x,std),w=workMinutes(x),d;if(!x)return 0;if(x.status==='Paid Leave'||x.status==='Holiday'||x.status==='Week Off')return 0;if(x.status==='Absent'||x.status==='Unpaid Leave')return-r;d=w-r;return d>0?Math.max(0,d-s.otDelay):d}"
new="function balanceMinutes(x,s){return window.AttendancePolicy?AttendancePolicy.balanceMinutes(x,s):0}"
if old not in s: raise SystemExit('v112 balance anchor missing')
s=s.replace(old,new,1)
old="function isSundayV113(date){var d=new Date(date+'T00:00:00');return !isNaN(d.getTime())&&d.getDay()===0}"
new="function isSundayV113(date){return window.AttendancePolicy?AttendancePolicy.isSunday(date):false}"
if old not in s: raise SystemExit('v112 sunday anchor missing')
s=s.replace(old,new,1)
old="function specialV113(x){return !!(x&&(x.specialOT===true||x.status==='Holiday'||x.status==='Week Off'||isSundayV113(x.date)))}"
new="function specialV113(x){return window.AttendancePolicy?AttendancePolicy.isSpecial(x):false}"
if old not in s: raise SystemExit('v112 special anchor missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

p=assets/'v113-fixes.js'; s=p.read_text(encoding='utf-8')
old="function settings(){var s={h:9,m:0,otDelay:30};try{var o=JSON.parse(localStorage.getItem('attendance_settings_v8')||'{}')||{};if(typeof o.h!=='undefined')s.h=+o.h||0;if(typeof o.m!=='undefined')s.m=+o.m||0;if(typeof o.otDelay!=='undefined')s.otDelay=+o.otDelay||0}catch(e){}return s}"
new="function settings(){var s={h:9,m:0,otDelay:30};try{var o=JSON.parse(localStorage.getItem('attendance_settings_v8')||'{}')||{};for(var k in o)s[k]=o[k]}catch(e){}return window.AttendancePolicy?AttendancePolicy.normalizeSettings(s):s}"
if old not in s: raise SystemExit('v113 settings anchor missing')
s=s.replace(old,new,1)
old="function workBetween(a,b){if(!a||!b)return 0;var x=minFrom(a),y=minFrom(b);if(y<x)y+=1440;return Math.max(0,y-x)}"
new="function workBetween(a,b){return window.AttendancePolicy?AttendancePolicy.minutesBetween(a,b):0}"
if old not in s: raise SystemExit('v113 work anchor missing')
s=s.replace(old,new,1)
old="function isSunday(date){var d=new Date(date+'T00:00:00');return !isNaN(d.getTime())&&d.getDay()===0}"
new="function isSunday(date){return window.AttendancePolicy?AttendancePolicy.isSunday(date):false}"
if old not in s: raise SystemExit('v113 sunday anchor missing')
s=s.replace(old,new,1)
old="function isSpecial(x){return !!(x&&(x.specialOT===true||x.status==='Holiday'||x.status==='Week Off'||isSunday(x.date)))}"
new="function isSpecial(x){return window.AttendancePolicy?AttendancePolicy.isSpecial(x):false}"
if old not in s: raise SystemExit('v113 special anchor missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

p=assets/'v11-ui.js'; s=p.read_text(encoding='utf-8')
pat=re.compile(r"function deleteProfileFlow\(\)\{.*?\nwindow\.onProfileDeleteResult",re.S)
m=pat.search(s)
if not m: raise SystemExit('deleteProfileFlow block missing')
fn="""function deleteProfileFlow(){dialog('Delete profile?','This permanently removes attendance, salary, settings, local documents, cloud backup and your Firebase account. This cannot be undone.',[{label:'Continue',kind:'danger'},{label:'Cancel',kind:'outline'}],function(i){if(i!==0)return;var email=E('cloudEmail')?E('cloudEmail').textContent:'';dialog('Verify account','Type your registered email address to continue.',[{label:'Verify',kind:'danger'},{label:'Cancel',kind:'outline'}],function(j,val){if(j!==0)return;if(String(val||'').trim().toLowerCase()!==String(email||'').trim().toLowerCase()){dialog('Verification failed','The email address did not match the signed-in account.',[{label:'OK',kind:'primary'}]);return}dialog('Final confirmation','Type DELETE to permanently erase this profile.',[{label:'Delete permanently',kind:'danger'},{label:'Cancel',kind:'outline'}],function(k,word){if(k!==0)return;if(String(word||'').trim()!=='DELETE'){dialog('Not deleted','You must type DELETE exactly.',[{label:'OK',kind:'primary'}]);return}var provider='';try{if(window.Android&&Android.authProvider)provider=String(Android.authProvider()||'')}catch(e){}if(provider==='password'){dialog('Re-authenticate','Enter your current account password. Firebase requires a recent login before permanent deletion.',[{label:'Verify & Delete',kind:'danger'},{label:'Cancel',kind:'outline'}],function(q,pw){if(q!==0)return;if(!String(pw||'')){dialog('Password required','Enter your current password to continue.',[{label:'OK',kind:'primary'}]);return}Android.deleteAccountDataWithPassword(String(pw))},{placeholder:'Current password',type:'password'});return}if(window.Android&&Android.deleteAccountData){dialog('Re-authenticate with Google','Google account verification will open before anything is deleted.',[{label:'Continue',kind:'danger'},{label:'Cancel',kind:'outline'}],function(q){if(q===0)Android.deleteAccountData()});return}dialog('Deletion unavailable','Secure account deletion is unavailable in this build.',[{label:'OK',kind:'primary'}])},{placeholder:'DELETE'})},{placeholder:'Email address',type:'email'})})}
window.onProfileDeleteResult"""
s=s[:m.start()]+fn+s[m.end():]
p.write_text(s,encoding='utf-8')

p=assets/'index.html'; html=p.read_text(encoding='utf-8')
html=html.replace('<button class="settingsMenuRow" data-setting="documents"><span class="menuLottie lottieIcon" data-lottie="lottie/documents.json"></span><span><b>Job Documents</b><small>Upload, share, export and manage documents</small></span><i>›</i></button>','<button class="settingsMenuRow" data-setting="documents"><span class="menuLottie lottieIcon" data-lottie="lottie/documents.json"></span><span><b>Job Documents</b><small>Encrypted on this device • upload, share and export</small></span><i>›</i></button>')
html=html.replace('<p class="helpText">Monthly salary is divided by the number of calendar days in the month. Present, Paid Leave, Holiday and Week Off count as paid days; Half Day counts as 0.5. Overtime is added using the calculated hourly rate.</p>','<p class="helpText">Estimate starts from your monthly salary, deducts recorded short hours/absence, adds normal OT after the configured delay, and adds one extra hourly rate for Sunday/holiday work so those worked hours are paid at double rate overall.</p>')
html=html.replace('<div class="label">Total Leaves</div><div class="field"><select id="totalLeaves"></select></div>','<div class="label">Annual Paid Leave Cap</div><div class="field"><select id="totalLeaves"></select></div><p class="helpText">Paid leave accrues automatically at 1.5 days per month, up to this annual cap.</p>',1)
html=html.replace('<button class="btn primary fullBtn" id="saveDocument" type="button">Save Document</button>','<button class="btn primary fullBtn" id="saveDocument" type="button">Save Document</button><p class="helpText">Documents are encrypted with Android Keystore and stored only on this device. Cloud Backup currently protects attendance, profile and settings data, not document files.</p>')
old='''        <div class="cloudUser"><img id="cloudAvatar" src="profile-placeholder.svg" alt="Account profile"><span><b id="cloudName">Account</b><small id="cloudEmail"></small></span></div>
        <div class="cloudActions"><button class="btn primary" id="cloudBackupBtn" type="button">Backup Now</button><button class="btn ghost" id="cloudRestoreBtn" type="button">Restore</button><button class="btn ghost cloudSignOut" id="cloudSignOutBtn" type="button">Sign Out</button></div>
        <small class="cloudStatus" id="cloudStatus">Encrypted backup. Tap Backup Now to create a protected restore point.</small>'''
new='''        <div class="cloudUser"><img id="cloudAvatar" src="profile-placeholder.svg" alt="Account profile"><span><b id="cloudName">Account</b><small id="cloudEmail"></small></span></div>
        <div class="label">Backup Recovery Password</div><div class="field"><input id="backupRecoveryPassword" type="password" minlength="8" autocomplete="new-password" placeholder="Enter 8+ character recovery password"></div>
        <button class="btn ghost fullBtn" id="saveBackupRecoveryBtn" type="button">Save Recovery Password</button>
        <small class="cloudStatus" id="backupRecoveryState">Set a recovery password before creating a new encrypted backup.</small>
        <div class="cloudActions"><button class="btn primary" id="cloudBackupBtn" type="button">Backup Now</button><button class="btn ghost" id="cloudRestoreBtn" type="button">Restore</button><button class="btn ghost cloudSignOut" id="cloudSignOutBtn" type="button">Sign Out</button></div>
        <small class="cloudStatus" id="cloudStatus">End-to-end encrypted backup. Your recovery password is not uploaded to Firebase.</small>'''
if old not in html: raise SystemExit('backup UI anchor missing')
html=html.replace(old,new,1)
html=html.replace('<script src="user-storage.js"></script>','<script src="policy-engine.js"></script>\n<script src="user-storage.js"></script>',1)
html=html.replace('<script src="cloud-ui.js"></script>','<script src="backup-crypto.js"></script>\n<script src="cloud-ui.js"></script>',1)
p.write_text(html,encoding='utf-8')
print('v12.6 correctness/reliability UI patch applied')
