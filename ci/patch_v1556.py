from pathlib import Path
import re,sys,shutil

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
app=assets/'app.js'
v112=assets/'v112-fixes.js'
v1553=assets/'v1553-fixes.js'
s=app.read_text(encoding='utf-8')
t=v112.read_text(encoding='utf-8')
u=v1553.read_text(encoding='utf-8')

# One verified persistence path for every user-owned setting/data write.
anchor="function E(id){return document.getElementById(id)}"
helper="""function E(id){return document.getElementById(id)}
function verifiedStorageSet(key,value,label){
 var raw=typeof value==='string'?value:JSON.stringify(value),ok=false,physical='';
 try{localStorage.setItem(key,raw);ok=localStorage.getItem(key)===raw}catch(e){}
 if(!ok){
  try{
   if(window.Android&&Android.secureSet&&window.attendanceUserKey){
    physical=String(window.attendanceUserKey(key)||'');
    if(physical)ok=!!Android.secureSet(physical,raw)
   }
  }catch(e){}
 }
 if(!ok){toast('Could not save '+(label||'data'));return false}
 return true
}
window.attendanceVerifiedSet=verifiedStorageSet"""
if anchor not in s: raise SystemExit('E helper anchor missing')
s=s.replace(anchor,helper,1)

patterns=[
 (r"function dataPut\(a\)\{.*?\}",
  "function dataPut(a){if(!verifiedStorageSet(DATA_KEY,a,'attendance'))return false;if(window.AttendanceV15&&AttendanceV15.onDataChanged)AttendanceV15.onDataChanged();if(window.AttendanceV14&&AttendanceV14.onDataChanged)AttendanceV14.onDataChanged();return true}"),
 (r"function setPut\(s\)\{.*?\}",
  "function setPut(s){return verifiedStorageSet(SET_KEY,s,'work settings')}"),
 (r"function profilePut\(p\)\{.*?\}",
  "function profilePut(p){return verifiedStorageSet(PROFILE_KEY,p,'profile')}"),
 (r"function leavePut\(o\)\{.*?\}",
  "function leavePut(o){return verifiedStorageSet(LEAVE_KEY,o,'leave setup')}")
]
for pat,repl in patterns:
    s,n=re.subn(pat,repl,s,count=1)
    if n!=1: raise SystemExit('persistence function anchor missing: '+pat)

# v15.5.5 salaryPut was already hardened; route it through the shared verifier.
pat=re.compile(r"function salaryPut\(s\)\{.*?\n\}",re.S)
m=pat.search(s)
if not m: raise SystemExit('salaryPut block missing')
s=s[:m.start()]+"function salaryPut(s){return verifiedStorageSet(SALARY_KEY,s,'salary settings')}"+s[m.end():]

# Never let the removed legacy Attendance summary renderer run against v15 markup.
old="function renderAttendance(){"
new="function renderAttendance(){if(window.AttendanceV15&&AttendanceV15.renderScreen)return AttendanceV15.renderScreen('attendance');"
if old not in s: raise SystemExit('renderAttendance anchor missing')
s=s.replace(old,new,1)

# Extra fallback protection for the old summary code if v15 is ever unavailable.
summary_pat=re.compile(r"function attendanceApplySummary\(x\)\{.*?\n\}",re.S)
m=summary_pat.search(s)
if m:
    summary="""function attendanceApplySummary(x){
 x=x||{};
 var e=E('attendanceMonthTitle');if(e)e.textContent=x.monthTitle||attendanceMonthLabel(E('monthFilter')&&E('monthFilter').value);
 e=E('attendanceMonthCount');if(e)e.textContent=(x.shown||0)+' shown • '+(x.records||0)+' records';
 e=E('attendanceSummaryPresent');if(e)e.textContent=x.present||0;
 e=E('attendanceSummaryWorked');if(e)e.textContent=attendanceTotalText(x.worked||0);
 e=E('attendanceSummaryBalance');if(e)e.textContent=signedDuration(x.balance||0);
 e=E('attendanceSummaryLeaves');if(e)e.textContent=x.leaves||0
}"""
    s=s[:m.start()]+summary+s[m.end():]

# Theme persistence should use the same verified storage path.
old="function setTheme(theme){localStorage.setItem(THEME_KEY,theme);renderTheme()}"
new="function setTheme(theme){if(verifiedStorageSet(THEME_KEY,String(theme),'theme'))renderTheme()}"
if old not in s: raise SystemExit('setTheme anchor missing')
s=s.replace(old,new,1)

# Export the verifier for newer feature scripts and audit coverage.
api_pat=re.compile(r'window\.AttendanceAppApi=\{([^}]*)\};')
m=api_pat.search(s)
if not m: raise SystemExit('AttendanceAppApi missing')
body=m.group(1)
if 'verifiedStorageSet:verifiedStorageSet' not in body:
    body+=',verifiedStorageSet:verifiedStorageSet'
s=s[:m.start()]+'window.AttendanceAppApi={'+body+'};'+s[m.end():]

# Typography is also a user-owned setting: verify its write.
old="function saveTypography(){var t=readTypographyUI();localStorage.setItem(TYPE_KEY,JSON.stringify(t));applyTypography(t)}"
new="function saveTypography(){var t=readTypographyUI(),raw=JSON.stringify(t),ok=false;try{ok=window.attendanceVerifiedSet?window.attendanceVerifiedSet(TYPE_KEY,raw,'typography'):(localStorage.setItem(TYPE_KEY,raw),true)}catch(e){}if(ok)applyTypography(t)}"
if old not in t: raise SystemExit('saveTypography anchor missing')
t=t.replace(old,new,1)

# Correct the emergency Theme fallback key to the current v9 key.
u=u.replace("attendance_theme_v8","attendance_theme_v9")

app.write_text(s,encoding='utf-8')
v112.write_text(t,encoding='utf-8')
v1553.write_text(u,encoding='utf-8')
print('v15.5.6 persistence and Attendance compatibility patch applied')
