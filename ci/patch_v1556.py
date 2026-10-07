from pathlib import Path
import re,sys,shutil

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
app=assets/'app.js'
v112=assets/'v112-fixes.js'
v1553=assets/'v1553-fixes.js'
diag=assets/'diagnostics-ui.js'
s=app.read_text(encoding='utf-8')
t=v112.read_text(encoding='utf-8')
u=v1553.read_text(encoding='utf-8')
d=diag.read_text(encoding='utf-8')

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

replacements=[
 ("function dataPut(a){try{localStorage.setItem(DATA_KEY,JSON.stringify(a));if(window.AttendanceV15&&AttendanceV15.onDataChanged)AttendanceV15.onDataChanged();if(window.AttendanceV14&&AttendanceV14.onDataChanged)AttendanceV14.onDataChanged();return true}catch(e){toast('Could not save attendance');return false}}",
  "function dataPut(a){if(!verifiedStorageSet(DATA_KEY,a,'attendance'))return false;if(window.AttendanceV15&&AttendanceV15.onDataChanged)AttendanceV15.onDataChanged();if(window.AttendanceV14&&AttendanceV14.onDataChanged)AttendanceV14.onDataChanged();return true}"),
 ("function setPut(s){try{localStorage.setItem(SET_KEY,JSON.stringify(s));return true}catch(e){toast('Could not save settings');return false}}",
  "function setPut(s){return verifiedStorageSet(SET_KEY,s,'work settings')}"),
 ("function profilePut(p){try{localStorage.setItem(PROFILE_KEY,JSON.stringify(p));return true}catch(e){toast('Profile image may be too large');return false}}",
  "function profilePut(p){return verifiedStorageSet(PROFILE_KEY,p,'profile')}"),
 ("function leavePut(o){try{localStorage.setItem(LEAVE_KEY,JSON.stringify(o));return true}catch(e){return false}}",
  "function leavePut(o){return verifiedStorageSet(LEAVE_KEY,o,'leave setup')}")
]
for old,repl in replacements:
    if old not in s: raise SystemExit('persistence function anchor missing: '+old[:50])
    s=s.replace(old,repl,1)

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

# The v15 Attendance redesign removed two legacy controls. Guard those lookups so
# the core bind() function continues and Settings/Profile/Leave/Documents/Edit handlers bind.
old="E('attendanceResetFilters').onclick=attendanceResetFilters;"
new="if(E('attendanceResetFilters'))E('attendanceResetFilters').onclick=attendanceResetFilters;"
if old not in s: raise SystemExit('legacy attendanceResetFilters binding anchor missing')
s=s.replace(old,new,1)
old="E('attendanceClearSearch').onclick=function(){if(E('attendanceSearch').value){E('attendanceSearch').value='';renderAttendance()}else E('attendanceSearch').focus()};"
new="if(E('attendanceClearSearch'))E('attendanceClearSearch').onclick=function(){if(E('attendanceSearch').value){E('attendanceSearch').value='';renderAttendance()}else E('attendanceSearch').focus()};"
if old not in s: raise SystemExit('legacy attendanceClearSearch binding anchor missing')
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

# Diagnostics Backup & Restore button must use the public app API. The old
# window.showScreen reference is not exported by the core app.
old="if(backup)backup.onclick=function(){if(typeof window.showScreen==='function')window.showScreen('setting-backup')};"
new="if(backup)backup.onclick=function(){var A=window.AttendanceAppApi;if(A&&typeof A.showScreen==='function')A.showScreen('setting-backup');else if(typeof window.showScreen==='function')window.showScreen('setting-backup')};"
if old not in d: raise SystemExit('diagnostics backup navigation anchor missing')
d=d.replace(old,new,1)

# Correct the emergency Theme fallback key to the current v9 key.
u=u.replace("attendance_theme_v8","attendance_theme_v9")

app.write_text(s,encoding='utf-8')
v112.write_text(t,encoding='utf-8')
v1553.write_text(u,encoding='utf-8')
diag.write_text(d,encoding='utf-8')
print('v15.5.6 persistence, Attendance and diagnostics compatibility patch applied')
