from pathlib import Path
import re,sys

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
index=assets/'index.html'
app=assets/'app.js'
h=index.read_text(encoding='utf-8')
s=app.read_text(encoding='utf-8')

# Leave Setup is now the authoritative annual balance; do not replace it with monthly accrual.
old_help='Paid leave accrues automatically at 1.5 days per month, up to this annual cap.'
new_help='Set the total paid leaves available for this year. My Leaves uses this saved total and subtracts paid leave already used.'
if old_help not in h:
    raise SystemExit('Leave Setup help anchor missing')
h=h.replace(old_help,new_help,1)
index.write_text(h,encoding='utf-8')

# Every Sunday is canonical Week Off throughout the app, including older stored records.
old_data="function dataGet(){var keys=[DATA_KEY,'attendance_v9','attendance_v6','attendance_v5'],i,r,a;for(i=0;i<keys.length;i++){try{r=localStorage.getItem(keys[i]);if(r){a=JSON.parse(r);if(a&&typeof a.length==='number'){if(keys[i]!==DATA_KEY)localStorage.setItem(DATA_KEY,JSON.stringify(a));return a}}}catch(e){}}return[]}"
new_data="""function canonicalSundayRecord(x){if(x&&isSundayDate(x.date)){x.status='Week Off';x.specialOT=true}return x}
function dataGet(){var keys=[DATA_KEY,'attendance_v9','attendance_v6','attendance_v5'],i,r,a,j;for(i=0;i<keys.length;i++){try{r=localStorage.getItem(keys[i]);if(r){a=JSON.parse(r);if(a&&typeof a.length==='number'){if(keys[i]!==DATA_KEY)localStorage.setItem(DATA_KEY,JSON.stringify(a));for(j=0;j<a.length;j++)canonicalSundayRecord(a[j]);return a}}}catch(e){}}return[]}"""
if old_data not in s:
    raise SystemExit('dataGet anchor missing')
s=s.replace(old_data,new_data,1)

# Reset all Add Attendance controls and also refresh the custom date/select wrappers.
old_reset="function resetForm(){E('editId').value='';E('dateInput').value=nowDate();E('statusInput').value='Present';buildTime('checkIn','');buildTime('checkOut','');E('reasonInput').value='';E('notesInput').value='';E('formTitle').textContent='Add Attendance';syncLeaveCategory()}"
new_reset="""function triggerControlChange(id){var z=E(id);if(!z)return;try{z.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}
function applySundayFormRule(){var d=E('dateInput'),st=E('statusInput');if(!d||!st)return;if(isSundayDate(d.value)&&st.value!=='Week Off'){st.value='Week Off';triggerControlChange('statusInput')}}
function applySundayEditRule(){var d=E('editPopupDate'),st=E('editPopupStatus');if(!d||!st)return;if(isSundayDate(d.value)&&st.value!=='Week Off'){st.value='Week Off';triggerControlChange('editPopupStatus')}}
function resetForm(){var d=nowDate(),ids=['dateInput','statusInput','checkInH','checkInM','checkInP','checkOutH','checkOutM','checkOutP'];E('editId').value='';E('dateInput').value=d;E('statusInput').value=isSundayDate(d)?'Week Off':'Present';buildTime('checkIn','');buildTime('checkOut','');E('reasonInput').value='';E('notesInput').value='';E('formTitle').textContent='Add Attendance';for(var i=0;i<ids.length;i++)triggerControlChange(ids[i]);syncLeaveCategory();triggerControlChange('leaveCategoryInput')}"""
if old_reset not in s:
    raise SystemExit('resetForm anchor missing')
s=s.replace(old_reset,new_reset,1)

# Week Off on Sunday may contain times: every minute worked is OT.
old_status="function statusChanged(){var s=E('statusInput').value;if(s==='Absent'||s==='Paid Leave'||s==='Unpaid Leave'||s==='Holiday'||s==='Week Off'){buildTime('checkIn','');buildTime('checkOut','')}syncLeaveCategory()}"
new_status="function statusChanged(){var st=E('statusInput'),s=st.value,sun=isSundayDate(E('dateInput').value);if(sun&&s!=='Week Off'){st.value='Week Off';triggerControlChange('statusInput');return}if(s==='Absent'||s==='Paid Leave'||s==='Unpaid Leave'||s==='Holiday'||(s==='Week Off'&&!sun)){buildTime('checkIn','');buildTime('checkOut','');triggerControlChange('checkInH');triggerControlChange('checkInM');triggerControlChange('checkOutH');triggerControlChange('checkOutM')}syncLeaveCategory()}"
if old_status not in s:
    raise SystemExit('statusChanged anchor missing')
s=s.replace(old_status,new_status,1)

# Manual Add Attendance can never save a Sunday under another status.
old_entry="e={id:id||idNew(),date:date,status:E('statusInput').value,checkIn:readTime('checkIn'),checkOut:readTime('checkOut'),reason:E('reasonInput').value.trim(),notes:E('notesInput').value.trim()};"
new_entry="e={id:id||idNew(),date:date,status:isSundayDate(date)?'Week Off':E('statusInput').value,checkIn:readTime('checkIn'),checkOut:readTime('checkOut'),reason:E('reasonInput').value.trim(),notes:E('notesInput').value.trim()};if(isSundayDate(date))e.specialOT=true;"
if old_entry not in s:
    raise SystemExit('saveForm entry anchor missing')
s=s.replace(old_entry,new_entry,1)

# Editing/moving an entry to Sunday also makes it Week Off + special OT.
old_edit=" updated={id:current.id,date:E('editPopupDate').value,status:E('editPopupStatus').value,checkIn:readTime('editIn'),checkOut:readTime('editOut'),reason:E('editPopupReason').value.trim(),notes:E('editPopupNotes').value.trim()};"
new_edit=old_edit+"\n if(isSundayDate(updated.date)){updated.status='Week Off';updated.specialOT=true}"
if old_edit not in s:
    raise SystemExit('saveEdit updated anchor missing')
s=s.replace(old_edit,new_edit,1)

# Saved Leave Setup total is exactly what My Leaves displays and balances against.
leave_pat=re.compile(r"function renderLeaves\(\)\{.*?\n\}",re.S)
m=leave_pat.search(s)
if not m:
    raise SystemExit('renderLeaves block missing')
new_leaves="""function renderLeaves(){
 var cfg=leaveGet(),a=dataGet(),yr=String(new Date().getFullYear()),paid=0,unpaid=0,hol=0,out='',i,j,x,d,u,balance,pct,types='',total=Math.max(0,Number(cfg.total)||0);
 for(i=0;i<a.length;i++){x=a[i];if(x.date.indexOf(yr)===0){if(x.status==='Paid Leave')paid++;if(x.status==='Unpaid Leave')unpaid++;if(x.status==='Holiday')hol++}if(x.status==='Paid Leave'||x.status==='Unpaid Leave'){d=x.date.split('-');out+='<div class="record"><div class="recordTop"><div class="dateBlock"><b>'+d[2]+'</b><small>'+dayShort(x.date)+'</small></div><div class="recordMain"><b style="font-size:12px">'+esc(x.reason||x.status)+'</b><div style="font-size:10px;color:var(--muted);margin-top:4px">'+x.date+'</div></div><span class="statusBadge '+statusClass(x.status)+'">'+esc(x.status)+'</span></div></div>'}}
 balance=Math.max(0,total-paid);pct=total?Math.round(balance/total*100):0;E('leaveBalance').textContent=balance;E('leaveAccrued').textContent=total;E('leaveUsed').textContent=paid;E('leaveRing').style.background='conic-gradient(#2d8bdd 0 '+pct+'%,#e9eef3 '+pct+'% 100%)';
 for(i=0;i<cfg.categories.length;i++){u=0;for(j=0;j<a.length;j++)if(a[j].date.indexOf(yr)===0&&a[j].status==='Paid Leave'&&a[j].reason===cfg.categories[i].name)u++;types+='<div class="leaveType"><b>'+Math.max(0,cfg.categories[i].allowed-u)+'/'+cfg.categories[i].allowed+'</b><small>'+esc(cfg.categories[i].name)+'</small></div>'}
 E('leaveTypes').innerHTML=types||'<div class="empty">No categories.</div>';E('leaveYear').textContent=yr;E('leaveRecords').innerHTML=out||'<div class="empty">No leave records yet.</div>'
}"""
s=s[:m.start()]+new_leaves+s[m.end():]

# Date edits immediately enforce Sunday Week Off in both Add and Edit screens.
old_bind="E('punchBtn').onclick=punch;E('saveBtn').onclick=saveForm;E('resetBtn').onclick=resetForm;E('statusInput').onchange=statusChanged;E('leaveCategoryInput').onchange=function(){if(this.value)E('reasonInput').value=this.value};"
new_bind=old_bind+"if(E('dateInput'))E('dateInput').addEventListener('change',applySundayFormRule);if(E('editPopupDate'))E('editPopupDate').addEventListener('change',applySundayEditRule);"
if old_bind not in s:
    raise SystemExit('core Add Attendance binding anchor missing')
s=s.replace(old_bind,new_bind,1)

# Export the Sunday/reset helpers for audit/debugging without changing existing API behavior.
api_pat=re.compile(r'window\.AttendanceAppApi=\{([^}]*)\};')
m=api_pat.search(s)
if not m:
    raise SystemExit('AttendanceAppApi missing')
body=m.group(1)
for item in ['canonicalSundayRecord:canonicalSundayRecord','applySundayFormRule:applySundayFormRule']:
    if item not in body: body+=','+item
s=s[:m.start()]+'window.AttendanceAppApi={'+body+'};'+s[m.end():]

app.write_text(s,encoding='utf-8')
print('v15.5.8 Sunday, Reset and Leave Balance fixes applied')
