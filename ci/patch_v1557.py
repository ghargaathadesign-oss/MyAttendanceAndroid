from pathlib import Path
import re,sys,shutil

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
index=assets/'index.html'
app=assets/'app.js'

h=index.read_text(encoding='utf-8')
s=app.read_text(encoding='utf-8')

# Add final v15.5.7 assets.
if 'v1557-fixes.css' not in h:
    h=h.replace('</head>','<link rel="stylesheet" href="v1557-fixes.css">\n</head>',1)
if 'v1557-fixes.js' not in h:
    h=h.replace('</body>','<script src="v1557-fixes.js"></script>\n</body>',1)

# Work & Time now uses an explicit Save button.
work_anchor='<div class="preview" id="stdPreview">Standard day: 9h 00m • OT after +30m</div>'
if 'id="saveWorkSettings"' not in h:
    if work_anchor not in h: raise SystemExit('Work preview anchor missing')
    h=h.replace(work_anchor,work_anchor+'\n        <button class="btn primary fullBtn" id="saveWorkSettings" type="button">Save Work &amp; Time Settings</button><small id="workSaveStatus" aria-live="polite"></small>',1)

# Leave save feedback.
leave_anchor='<div class="preview" id="leaveSetupPreview"></div>'
if 'id="leaveSaveStatus"' not in h:
    if leave_anchor not in h: raise SystemExit('Leave preview anchor missing')
    h=h.replace(leave_anchor,leave_anchor+'<small id="leaveSaveStatus" aria-live="polite"></small>',1)

# Revert Appearance Theme to the older non-animated selector.
theme_pat=re.compile(r'<div class="themeVisualToggle v1551ThemeToggleShell">.*?</div>',re.S)
theme_old='''<div class="themeVisualToggle"><button id="themeLight" type="button" aria-label="Light mode"><span>☀</span><small>Light</small></button><button id="themeDark" type="button" aria-label="Dark mode"><span>☾</span><small>Dark</small></button></div>'''
h,n=theme_pat.subn(theme_old,h,count=1)
if n!=1: raise SystemExit('Animated theme control anchor missing')

# Salary wording now reflects earned-to-date from recorded paid days.
h=h.replace(
 'Estimate starts from your monthly salary, deducts recorded short hours/absence, adds normal OT after the configured delay, and adds one extra hourly rate for Sunday/holiday work so those worked hours are paid at double rate overall.',
 'Earned amount is calculated from recorded paid days only. Short hours reduce the recorded day value, normal OT is added after the configured delay, and Sunday/holiday worked hours receive the configured extra pay.'
)

# Force fresh local JS/CSS on app updates so an older UI bundle cannot be reused by WebView.
def bust_attr(m):
    pre,url,post=m.group(1),m.group(2),m.group(3)
    if url.startswith(('http://','https://','data:')): return m.group(0)
    url=re.sub(r"\?v=[^\"]+$",'',url)
    return pre+url+'?v=1557'+post
h=re.sub(r'((?:src|href)=")([^"]+\.(?:js|css))(")',bust_attr,h)

index.write_text(h,encoding='utf-8')

# Work & Time: edit draft values, persist only when Save is tapped.
old_load="function loadSettings(){\n var s=setGet();E('stdHours').value=s.h;E('stdMinutes').value=s.m;E('otDelay').value=s.otDelay;E('fmt12').classList.toggle('on',s.fmt==='12h');E('fmt24').classList.toggle('on',s.fmt==='24h');E('stdPreview').textContent='Standard day: '+s.h+'h '+P(s.m)+'m • OT after +'+s.otDelay+'m'\n}"
new_load="""function loadSettings(){
 var s=setGet();E('stdHours').value=s.h;E('stdMinutes').value=s.m;E('otDelay').value=s.otDelay;E('fmt12').classList.toggle('on',s.fmt==='12h');E('fmt24').classList.toggle('on',s.fmt==='24h');previewWorkDraft();var st=E('workSaveStatus');if(st){st.textContent='';st.className=''}
}"""
if old_load not in s: raise SystemExit('loadSettings anchor missing')
s=s.replace(old_load,new_load,1)

old_work="function saveWork(){var s=setGet();s.h=parseInt(E('stdHours').value,10)||0;s.m=parseInt(E('stdMinutes').value,10)||0;s.otDelay=parseInt(E('otDelay').value,10)||0;setPut(s);renderAll()}\nfunction setFormat(fmt){var s=setGet(),ci=readTime('checkIn'),co=readTime('checkOut');s.fmt=fmt;setPut(s);buildTime('checkIn',ci);buildTime('checkOut',co);renderAll()}"
new_work="""function previewWorkDraft(){
 var h=parseInt(E('stdHours').value,10)||0,m=parseInt(E('stdMinutes').value,10)||0,d=parseInt(E('otDelay').value,10)||0;
 E('stdPreview').textContent='Standard day: '+h+'h '+P(m)+'m • OT after +'+d+'m'
}
function markWorkDirty(){var st=E('workSaveStatus');if(st){st.textContent='Unsaved changes';st.className=''}previewWorkDraft()}
function saveWork(){
 var old=setGet(),fmt=E('fmt24').classList.contains('on')?'24h':'12h',ci=readTime('checkIn'),co=readTime('checkOut'),st=E('workSaveStatus');
 var next={h:parseInt(E('stdHours').value,10)||0,m:parseInt(E('stdMinutes').value,10)||0,fmt:fmt,otDelay:parseInt(E('otDelay').value,10)||0};
 if(!setPut(next)){if(st){st.textContent='Could not save Work & Time settings';st.className='err'}return false}
 buildTime('checkIn',ci);buildTime('checkOut',co);buildTime('editIn','');buildTime('editOut','');
 if(window.AttendanceV15&&AttendanceV15.onDataChanged)AttendanceV15.onDataChanged();
 if(window.AttendanceV14&&AttendanceV14.onDataChanged)AttendanceV14.onDataChanged();
 renderHome();renderSalary();if(activeScreen()==='attendance'&&window.AttendanceV15)AttendanceV15.renderScreen('attendance');
 if(st){st.textContent='Work & Time settings saved';st.className='ok'}toast('Work & Time settings saved');return true
}
function setFormat(fmt){
 E('fmt12').classList.toggle('on',fmt==='12h');E('fmt24').classList.toggle('on',fmt==='24h');markWorkDirty()
}"""
if old_work not in s: raise SystemExit('saveWork/setFormat anchor missing')
s=s.replace(old_work,new_work,1)

# Leave Setup: verify saved values and refresh all dependent views.
save_leave_pat=re.compile(r"function saveLeaves\(\)\{.*?\n\}",re.S)
m=save_leave_pat.search(s)
if not m: raise SystemExit('saveLeaves block missing')
new_leave="""function saveLeaves(){
 var rows=E('leaveSetupRows').getElementsByClassName('leaveSetupRow'),cfg={total:parseInt(E('totalLeaves').value,10)||0,categories:[]},i,n,a,seen={},status=E('leaveSaveStatus');
 for(i=0;i<rows.length;i++){
  n=rows[i].querySelector('.catName').value.trim();a=parseInt(rows[i].querySelector('.catAllowed').value,10)||0;
  if(!n)continue;
  if(seen[n.toLowerCase()]){if(status){status.textContent='Leave category names must be unique';status.className='err'}toast('Leave category names must be unique');return false}
  seen[n.toLowerCase()]=1;cfg.categories.push({id:rows[i].getAttribute('data-id')||idNew(),name:n,allowed:a})
 }
 if(!leavePut(cfg)){if(status){status.textContent='Could not save Leave Setup';status.className='err'}return false}
 var verify=leaveGet();
 if(+verify.total!==+cfg.total||verify.categories.length!==cfg.categories.length){if(status){status.textContent='Leave Setup was not saved correctly';status.className='err'}toast('Could not verify Leave Setup');return false}
 buildLeaveSetup();syncLeaveCategory();renderLeaves();renderSalary();renderHome();
 if(status){status.textContent='Leave Setup saved';status.className='ok'}toast('Leave setup saved');return true
}"""
s=s[:m.start()]+new_leave+s[m.end():]

# Canonical Attendance only: never render the legacy Attendance list again.
attendance_pat=re.compile(r"function renderAttendance\(\)\{.*?\n\}\nfunction renderLeaves",re.S)
m=attendance_pat.search(s)
if not m: raise SystemExit('legacy renderAttendance block missing')
canonical="""function renderAttendance(){
 if(window.AttendanceV15&&AttendanceV15.renderScreen)return AttendanceV15.renderScreen('attendance');
 return false
}
function renderLeaves"""
s=s[:m.start()]+canonical+s[m.end():]

# Remove legacy Attendance event handlers that could overwrite v15 handlers.
legacy_bind=re.compile(r"E\('monthFilter'\)\.onchange=.*?(?=E\('fmt12'\)\.onclick=)",re.S)
s,n=legacy_bind.subn("",s,count=1)
if n!=1: raise SystemExit('legacy Attendance bind block missing')

# Replace Work & Time auto-save bindings with draft + explicit Save.
old_bind="E('fmt12').onclick=function(){setFormat('12h')};E('fmt24').onclick=function(){setFormat('24h')};E('stdHours').onchange=saveWork;E('stdMinutes').onchange=saveWork;E('otDelay').onchange=saveWork;"
new_bind="E('fmt12').onclick=function(){setFormat('12h')};E('fmt24').onclick=function(){setFormat('24h')};E('stdHours').onchange=markWorkDirty;E('stdMinutes').onchange=markWorkDirty;E('otDelay').onchange=markWorkDirty;if(E('saveWorkSettings'))E('saveWorkSettings').onclick=saveWork;"
if old_bind not in s: raise SystemExit('Work bind anchor missing')
s=s.replace(old_bind,new_bind,1)

# The legacy records handler expects removed .editRecord buttons and can overwrite v15.
old_records="E('records').onclick=function(e){var b=e.target.closest('button');if(!b)return;var id=b.getAttribute('data-id');if(b.classList.contains('editRecord'))openEdit(id);else if(b.classList.contains('deleteRecord'))deleteRecord(id)};"
if old_records in s:s=s.replace(old_records,"",1)

# Export new save APIs for audit and resilient UI handlers.
api_pat=re.compile(r'window\.AttendanceAppApi=\{([^}]*)\};')
m=api_pat.search(s)
if not m: raise SystemExit('AttendanceAppApi missing')
body=m.group(1)
for item in ['saveWork:saveWork','saveLeaves:saveLeaves','leaveGet:leaveGet']:
    if item not in body: body+=','+item
s=s[:m.start()]+'window.AttendanceAppApi={'+body+'};'+s[m.end():]

app.write_text(s,encoding='utf-8')
shutil.copy('ci/v1557-fixes.css',assets/'v1557-fixes.css')
shutil.copy('ci/v1557-fixes.js',assets/'v1557-fixes.js')
print('v15.5.7 consolidated bug batch applied')
