from pathlib import Path
import re,sys,shutil

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
index=assets/'index.html'
app=assets/'app.js'
h=index.read_text(encoding='utf-8')
s=app.read_text(encoding='utf-8')

if 'v1555-salary.css' not in h:
    h=h.replace('</head>','<link rel="stylesheet" href="v1555-salary.css">\n</head>',1)
if 'v1555-salary.js' not in h:
    h=h.replace('</body>','<script src="v1555-salary.js"></script>\n</body>',1)

if 'id="salarySaveStatus"' not in h:
    old='<button class="btn primary fullBtn" id="saveSalary" type="button">Save Salary Settings</button>'
    new=old+'<small id="salarySaveStatus" aria-live="polite"></small>'
    if old not in h: raise SystemExit('salary save button anchor missing')
    h=h.replace(old,new,1)

old_put="function salaryPut(s){localStorage.setItem(SALARY_KEY,JSON.stringify(s))}"
new_put="""function salaryPut(s){
 var raw=JSON.stringify(s),ok=false,key='';
 try{localStorage.setItem(SALARY_KEY,raw);ok=localStorage.getItem(SALARY_KEY)===raw}catch(e){}
 if(!ok){
  try{
   if(window.Android&&Android.secureSet&&window.attendanceUserKey){
    key=window.attendanceUserKey(SALARY_KEY);
    ok=!!Android.secureSet(String(key),raw);
   }
  }catch(e){}
 }
 if(!ok){toast('Could not save salary settings');return false}
 return true
}"""
if old_put not in s: raise SystemExit('salaryPut anchor missing')
s=s.replace(old_put,new_put,1)

old_save="function saveSalary(){salaryPut({monthly:parseFloat(E('salaryAmount').value)||0,otMultiplier:parseFloat(E('salaryOtMultiplier').value)||1});toast('Salary settings saved');renderAll()}"
new_save="""function saveSalary(){
 var raw=String(E('salaryAmount').value||'').replace(/[^0-9.\-]/g,''),monthly=parseFloat(raw),mult=parseFloat(E('salaryOtMultiplier').value),status=E('salarySaveStatus');
 if(!isFinite(monthly)||monthly<0){if(status){status.textContent='Enter a valid monthly salary';status.className='err'}toast('Enter a valid monthly salary');return false}
 if(!isFinite(mult)||mult<=0)mult=1;
 if(!salaryPut({monthly:monthly,otMultiplier:mult})){if(status){status.textContent='Could not save salary settings';status.className='err'}return false}
 if(window.AttendanceV14&&AttendanceV14.onDataChanged)AttendanceV14.onDataChanged();
 renderSalary();renderHome();
 if(activeScreen()==='setting-reports'&&window.AttendanceV14&&AttendanceV14.renderScreen)AttendanceV14.renderScreen('setting-reports');
 if(status){status.textContent='Salary settings saved';status.className='ok'}
 toast('Salary settings saved');
 return true
}"""
if old_save not in s: raise SystemExit('saveSalary anchor missing')
s=s.replace(old_save,new_save,1)

api_pat=re.compile(r'window\.AttendanceAppApi=\{([^}]*)\};')
m=api_pat.search(s)
if not m: raise SystemExit('AttendanceAppApi missing')
body=m.group(1)
if 'saveSalary:saveSalary' not in body:
    body += ',saveSalary:saveSalary'
s=s[:m.start()]+'window.AttendanceAppApi={'+body+'};'+s[m.end():]

index.write_text(h,encoding='utf-8')
app.write_text(s,encoding='utf-8')
shutil.copy('ci/v1555-salary.js',assets/'v1555-salary.js')
shutil.copy('ci/v1555-salary.css',assets/'v1555-salary.css')
print('v15.5.5 salary save reliability patch applied')
