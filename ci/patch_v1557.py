from pathlib import Path
import re,sys,shutil

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
index=assets/'index.html'
app=assets/'app.js'
v15=assets/'v15-features.js'
v14=assets/'v14-features.js'

h=index.read_text(encoding='utf-8')
s=app.read_text(encoding='utf-8')
v=v15.read_text(encoding='utf-8')
f=v14.read_text(encoding='utf-8')

# ---- v15.5.7 assets ----
if 'v1557-fixes.css' not in h:
    if '</head>' not in h: raise SystemExit('head close missing')
    h=h.replace('</head>','<link rel="stylesheet" href="v1557-fixes.css">\n</head>',1)
if 'v1557-fixes.js' not in h:
    if '</body>' not in h: raise SystemExit('body close missing')
    h=h.replace('</body>','<script src="v1557-fixes.js"></script>\n</body>',1)

# ---- Work & Time: explicit save only ----
work_anchor='<div class="preview" id="stdPreview">Standard day: 9h 00m • OT after +30m</div>'
if 'id="saveWorkSettings"' not in h:
    if work_anchor not in h: raise SystemExit('Work preview anchor missing')
    h=h.replace(work_anchor,work_anchor+'\n        <button class="btn primary fullBtn" id="saveWorkSettings" type="button">Save Work &amp; Time Settings</button><small id="workSaveStatus" aria-live="polite"></small>',1)

# ---- Leave Setup save feedback ----
leave_anchor='<div class="actions"><button class="btn ghost" id="addLeaveCategory" type="button">+ Add Category</button><button class="btn primary" id="saveLeaves" type="button">Save Leave Setup</button></div>'
if 'id="leaveSaveStatus"' not in h:
    if leave_anchor not in h: raise SystemExit('Leave actions anchor missing')
    h=h.replace(leave_anchor,leave_anchor+'<small id="leaveSaveStatus" aria-live="polite"></small>',1)

# ---- Appearance Theme: roll back to older non-animated selector ----
theme_pat=re.compile(r'<div class="label">Theme</div><div class="themeVisualToggle v1551ThemeToggleShell">.*?</div>\s*<div class="themePreview">',re.S)
theme_old='''<div class="label">Theme</div><div class="themeVisualToggle">
          <button id="themeLight" type="button"><span aria-hidden="true">☀</span><small>Light</small></button>
          <button id="themeDark" type="button"><span aria-hidden="true">☾</span><small>Dark</small></button>
        </div>
        <div class="themePreview">'''
h,n=theme_pat.subn(theme_old,h,count=1)
if n!=1: raise SystemExit('Animated Theme block missing')

# ---- Salary description matches accrued/recorded attendance calculation ----
old_help='Estimate starts from your monthly salary, deducts recorded short hours/absence, adds normal OT after the configured delay, and adds one extra hourly rate for Sunday/holiday work so those worked hours are paid at double rate overall.'
new_help='Earned amount is calculated from recorded paid days so far, including paid leave / recorded holidays or week offs, minus recorded short time or absence, plus eligible OT. Sunday / holiday work receives one additional hourly-rate payment so worked hours are paid at double rate overall.'
if old_help in h:
    h=h.replace(old_help,new_help,1)

index.write_text(h,encoding='utf-8')

# ---- Work & Time functions: edit draft first, save explicitly ----
load_pat=re.compile(r"function loadSettings\(\)\{.*?\n\}",re.S)
m=load_pat.search(s)
if not m: raise SystemExit('loadSettings block missing')
load_new=r"""var workDraftFmt='12h';
function previewWorkDraft(){
 var h=parseInt(E('stdHours').value,10)||0,m=parseInt(E('stdMinutes').value,10)||0,d=parseInt(E('otDelay').value,10)||0,st=E('workSaveStatus');
 E('fmt12').classList.toggle('on',workDraftFmt==='12h');E('fmt24').classList.toggle('on',workDraftFmt==='24h');
 E('stdPreview').textContent='Standard day: '+h+'h '+P(m)+'m • OT after +'+d+'m';
 if(st){st.textContent='';st.className=''}
}
function loadSettings(){
 var x=setGet();workDraftFmt=x.fmt||'12h';E('stdHours').value=x.h;E('stdMinutes').value=x.m;E('otDelay').value=x.otDelay;E('fmt12').classList.toggle('on',workDraftFmt==='12h');E('fmt24').classList.toggle('on',workDraftFmt==='24h');E('stdPreview').textContent='Standard day: '+x.h+'h '+P(x.m)+'m • OT after +'+x.otDelay+'m'
}"""
s=s[:m.start()]+load_new+s[m.end():]

savework_pat=re.compile(r"function saveWork\(\)\{[^\n]*\}")
m=savework_pat.search(s)
if not m: raise SystemExit('saveWork missing')
savework_new=r"""function saveWork(){
 var x=setGet(),st=E('workSaveStatus');x.h=parseInt(E('stdHours').value,10)||0;x.m=parseInt(E('stdMinutes').value,10)||0;x.otDelay=parseInt(E('otDelay').value,10)||0;x.fmt=(workDraftFmt==='24h'?'24h':'12h');
 if(!setPut(x)){if(st){st.textContent='Could not save Work & Time settings';st.className='err'}return false}
 if(window.AttendanceV15&&AttendanceV15.onDataChanged)AttendanceV15.onDataChanged();
 if(window.AttendanceV14&&AttendanceV14.onDataChanged)AttendanceV14.onDataChanged();
 renderAll();
 if(st){st.textContent='Work & Time settings saved';st.className='ok'}
 toast('Work & Time settings saved');return true
}"""
s=s[:m.start()]+savework_new+s[m.end():]

setfmt_pat=re.compile(r"function setFormat\(fmt\)\{[^\n]*\}")
m=setfmt_pat.search(s)
if not m: raise SystemExit('setFormat missing')
setfmt_new=r"""function setFormat(fmt){workDraftFmt=fmt==='24h'?'24h':'12h';previewWorkDraft()}"""
s=s[:m.start()]+setfmt_new+s[m.end():]

old_bind="E('fmt12').onclick=function(){setFormat('12h')};E('fmt24').onclick=function(){setFormat('24h')};E('stdHours').onchange=saveWork;E('stdMinutes').onchange=saveWork;E('otDelay').onchange=saveWork;"
new_bind="E('fmt12').onclick=function(){setFormat('12h')};E('fmt24').onclick=function(){setFormat('24h')};E('stdHours').onchange=previewWorkDraft;E('stdMinutes').onchange=previewWorkDraft;E('otDelay').onchange=previewWorkDraft;if(E('saveWorkSettings'))E('saveWorkSettings').onclick=saveWork;"
if old_bind not in s: raise SystemExit('Work binding anchor missing')
s=s.replace(old_bind,new_bind,1)

# ---- Leave Setup: validated save/read-back and reliable refresh ----
leave_pat=re.compile(r"function saveLeaves\(\)\{[^\n]*\}")
m=leave_pat.search(s)
if not m: raise SystemExit('saveLeaves block missing')
leave_new=r"""function saveLeaves(){
 var rows=E('leaveSetupRows').getElementsByClassName('leaveSetupRow'),cfg={total:parseInt(E('totalLeaves').value,10)||0,categories:[]},seen={},i,n,a,id,st=E('leaveSaveStatus');
 for(i=0;i<rows.length;i++){
  n=rows[i].querySelector('.catName').value.trim();a=parseInt(rows[i].querySelector('.catAllowed').value,10)||0;id=rows[i].getAttribute('data-id')||idNew();
  if(!n)continue;
  if(seen[n.toLowerCase()]){if(st){st.textContent='Leave category names must be unique';st.className='err'}toast('Leave category names must be unique');return false}
  seen[n.toLowerCase()]=true;cfg.categories.push({id:id,name:n,allowed:a})
 }
 if(!leavePut(cfg)){if(st){st.textContent='Could not save Leave Setup';st.className='err'}return false}
 var check=leaveGet();
 if(!check||+check.total!==+cfg.total||!Array.isArray(check.categories)||check.categories.length!==cfg.categories.length){if(st){st.textContent='Leave Setup could not be verified';st.className='err'}toast('Leave Setup could not be verified');return false}
 buildLeaveSetup();syncLeaveCategory();renderLeaves();renderSalary();renderHome();
 if(window.AttendanceV15&&AttendanceV15.onDataChanged)AttendanceV15.onDataChanged();
 if(window.AttendanceV14&&AttendanceV14.onDataChanged)AttendanceV14.onDataChanged();
 if(st){st.textContent='Leave Setup saved';st.className='ok'}
 toast('Leave Setup saved');return true
}"""
s=s[:m.start()]+leave_new+s[m.end():]

old_leave_bind="E('addLeaveCategory').onclick=addLeaveCategory;E('saveLeaves').onclick=saveLeaves;E('totalLeaves').onchange=previewLeaveSetup;E('leaveSetupRows').addEventListener('click',function(e){if(e.target.classList.contains('leaveSetupDelete')){e.target.parentNode.remove();previewLeaveSetup()}});E('leaveSetupRows').addEventListener('change',previewLeaveSetup);"
new_leave_bind="E('addLeaveCategory').onclick=function(){addLeaveCategory();var st=E('leaveSaveStatus');if(st){st.textContent='';st.className=''}};E('saveLeaves').onclick=saveLeaves;E('totalLeaves').onchange=function(){previewLeaveSetup();var st=E('leaveSaveStatus');if(st){st.textContent='';st.className=''}};E('leaveSetupRows').addEventListener('click',function(e){if(e.target.classList.contains('leaveSetupDelete')){e.target.parentNode.remove();previewLeaveSetup();var st=E('leaveSaveStatus');if(st){st.textContent='';st.className=''}}});E('leaveSetupRows').addEventListener('change',function(){previewLeaveSetup();var st=E('leaveSaveStatus');if(st){st.textContent='';st.className=''}});"
if old_leave_bind not in s: raise SystemExit('Leave binding anchor missing')
s=s.replace(old_leave_bind,new_leave_bind,1)

# ---- Attendance edit: safe duplicate-date handling and forced canonical refresh ----
edit_pat=re.compile(r"function saveEdit\(\)\{[^\n]*\}")
m=edit_pat.search(s)
if not m: raise SystemExit('saveEdit block missing')
edit_new=r"""function saveEdit(){
 var a=dataGet(),id=E('editPopupId').value,i,current=null,dup=false,out=[],updated;
 for(i=0;i<a.length;i++)if(a[i].id===id){current=a[i];break}
 if(!current){toast('Attendance record was not found');return false}
 updated={id:current.id,date:E('editPopupDate').value,status:E('editPopupStatus').value,checkIn:readTime('editIn'),checkOut:readTime('editOut'),reason:E('editPopupReason').value.trim(),notes:E('editPopupNotes').value.trim()};
 if(!updated.date){toast('Please select a date');return false}
 for(i=0;i<a.length;i++)if(a[i].id!==id&&a[i].date===updated.date){dup=true;break}
 if(dup&&!confirm('Another attendance record exists for this date. Replace it?'))return false;
 for(i=0;i<a.length;i++)if(a[i].id!==id&&(!dup||a[i].date!==updated.date))out.push(a[i]);
 out.push(updated);
 if(dataPut(out)){closeEdit();toast('Attendance updated');if(window.AttendanceV15&&AttendanceV15.onDataChanged)AttendanceV15.onDataChanged();if(window.AttendanceV15&&AttendanceV15.renderScreen)AttendanceV15.renderScreen('attendance');renderHome();renderSalary();return true}
 return false
}"""
s=s[:m.start()]+edit_new+s[m.end():]

# Core legacy Attendance renderer must never be allowed to redraw the retired UI.
legacy_start="function renderAttendance(){if(window.AttendanceV15&&AttendanceV15.renderScreen)return AttendanceV15.renderScreen('attendance');"
if legacy_start not in s: raise SystemExit('core renderAttendance v15 guard missing')
s=s.replace(legacy_start,legacy_start+"return false;",1)

# Startup prewarm must use the canonical v15 renderer, never v14.
old_prewarm="var prewarm=function(){if(activeScreen()!=='attendance'){if(window.AttendanceV14&&AttendanceV14.renderScreen)AttendanceV14.renderScreen('attendance');else renderAttendance()}};"
new_prewarm="var prewarm=function(){if(activeScreen()!=='attendance'){if(window.AttendanceV15&&AttendanceV15.renderScreen)AttendanceV15.renderScreen('attendance')}};"
if old_prewarm not in s: raise SystemExit('startup prewarm anchor missing')
s=s.replace(old_prewarm,new_prewarm,1)

# Export explicit-save functions for the audit/fallback handlers.
api_pat=re.compile(r'window\.AttendanceAppApi=\{([^}]*)\};')
m=api_pat.search(s)
if not m: raise SystemExit('AttendanceAppApi missing')
body=m.group(1)
for item in ['saveWork:saveWork','saveLeaves:saveLeaves','buildLeaveSetup:buildLeaveSetup']:
    if item not in body: body+=','+item
s=s[:m.start()]+'window.AttendanceAppApi={'+body+'};'+s[m.end():]
app.write_text(s,encoding='utf-8')

# ---- v15 Attendance is the only Attendance renderer ----
# Force a repaint if legacy calendar markup somehow appears.
old_v15_start="function renderAttendance(){var month=E('monthFilter')&&E('monthFilter').value||monthNow(),raw='',key;"
new_v15_start="function renderAttendance(){var legacyCal=E('attendanceCalendar'),legacyRecords=E('records');if((legacyCal&&legacyCal.querySelector('.calendarCell'))||(legacyRecords&&legacyRecords.querySelector('.attendanceRow,.attendanceCard')))attendanceRenderKey='';var month=E('monthFilter')&&E('monthFilter').value||monthNow(),raw='',key;"
if old_v15_start not in v: raise SystemExit('v15 renderAttendance anchor missing')
v=v.replace(old_v15_start,new_v15_start,1)

# Whole Monthly Record card + edit icon both open the current record.
old_records="if(E('records'))E('records').onclick=function(ev){var b=ev.target.closest('.v154RecordEdit[data-id]');if(b&&A&&A.openEdit)A.openEdit(b.getAttribute('data-id'))};"
new_records="if(E('records'))E('records').onclick=function(ev){var b=ev.target.closest('.v154RecordEdit[data-id],.v154Record[data-id]'),api=window.AttendanceAppApi||A;if(b&&api&&api.openEdit){var card=b.classList.contains('v154Record')?b:b.closest('.v154Record[data-id]');api.openEdit(b.getAttribute('data-id')||(card&&card.getAttribute('data-id'))||'')}};"
if old_records not in v: raise SystemExit('v15 Monthly Record binding missing')
v=v.replace(old_records,new_records,1)

# Existing-date calendar edits also resolve API dynamically.
v=v.replace("if(x&&A&&A.openEdit){A.openEdit(x.id);return}","var api=window.AttendanceAppApi||A;if(x&&api&&api.openEdit){api.openEdit(x.id);return}",1)
v15.write_text(v,encoding='utf-8')

# v14 may still be loaded for reports/reminders, but it must not paint Attendance.
old_v14="function renderAttendance(){"
new_v14="function renderAttendance(){if(window.AttendanceV15&&AttendanceV15.renderScreen)return AttendanceV15.renderScreen('attendance');return false;"
if old_v14 not in f: raise SystemExit('v14 renderAttendance anchor missing')
f=f.replace(old_v14,new_v14,1)
v14.write_text(f,encoding='utf-8')

shutil.copy('ci/v1557-fixes.css',assets/'v1557-fixes.css')
shutil.copy('ci/v1557-fixes.js',assets/'v1557-fixes.js')
print('v15.5.7 consolidated bug-fix patch applied')
