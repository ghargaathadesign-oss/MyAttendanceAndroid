from pathlib import Path
import re, sys

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')

# ---- Attendance HTML ----
p=assets/'index.html'
html=p.read_text(encoding='utf-8')
old='''    <section class="screen" id="screen-attendance">
      <div class="sectionHeader"><span class="pageLottie lottieIcon" data-lottie="lottie/attendance.json"></span><h1>Attendance History</h1></div>
      <div class="filterRow">
        <div class="field"><input type="month" id="monthFilter"></div>
        <div class="field"><select id="statusFilter"><option value="">All Status</option><option>Present</option><option>Absent</option><option>Paid Leave</option><option>Unpaid Leave</option><option>Half Day</option><option>Holiday</option><option>Week Off</option></select></div>
      </div>
      <div class="records" id="records"></div>
    </section>
'''
new='''    <section class="screen" id="screen-attendance">
      <div class="sectionHeader"><span class="pageLottie lottieIcon" data-lottie="lottie/attendance.json"></span><h1>Attendance History</h1></div>

      <div class="attMonthToolbar">
        <button class="attMonthBtn" id="attendancePrevMonth" type="button" aria-label="Previous month">‹</button>
        <div class="attMonthHeading"><b id="attendanceMonthTitle">This month</b><small id="attendanceMonthCount">0 records</small></div>
        <button class="attMonthBtn" id="attendanceNextMonth" type="button" aria-label="Next month">›</button>
      </div>

      <div class="attSummaryGrid">
        <div class="attSummaryCard"><small>Present</small><b id="attendanceSummaryPresent">0</b></div>
        <div class="attSummaryCard"><small>Worked</small><b id="attendanceSummaryWorked">0h</b></div>
        <div class="attSummaryCard"><small>Net OT / Short</small><b id="attendanceSummaryBalance">0h</b></div>
        <div class="attSummaryCard"><small>Leaves</small><b id="attendanceSummaryLeaves">0</b></div>
      </div>

      <div class="attSearchBar">
        <span aria-hidden="true">⌕</span>
        <input id="attendanceSearch" type="search" autocomplete="off" placeholder="Search date, status, reason or notes">
        <button id="attendanceClearSearch" type="button" aria-label="Clear search">×</button>
      </div>

      <div class="filterRow attFilters">
        <div class="field"><input type="month" id="monthFilter"></div>
        <div class="field"><select id="statusFilter"><option value="">All Status</option><option>Present</option><option>Absent</option><option>Paid Leave</option><option>Unpaid Leave</option><option>Half Day</option><option>Short Day</option><option>Holiday</option><option>Week Off</option></select></div>
      </div>
      <button class="attResetFilters" id="attendanceResetFilters" type="button">Reset filters</button>

      <div class="records" id="records"></div>
    </section>
'''
if old not in html:
    raise SystemExit('attendance HTML anchor missing')
html=html.replace(old,new,1)
p.write_text(html,encoding='utf-8')

# ---- Attendance CSS ----
p=assets/'app.css'
css=p.read_text(encoding='utf-8')
extra=r'''
/* v13.7 Attendance upgrade */
.attMonthToolbar{display:grid;grid-template-columns:42px 1fr 42px;gap:10px;align-items:center;margin:2px 0 12px}
.attMonthBtn{width:42px;height:42px;border:1px solid var(--line);border-radius:14px;background:var(--surface);font-size:26px;line-height:1;box-shadow:0 7px 22px rgba(48,67,101,.05)}
.attMonthHeading{text-align:center;min-width:0}
.attMonthHeading b{display:block;font-size:16px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.attMonthHeading small{display:block;color:var(--muted);font-size:10px;margin-top:3px}
.attSummaryGrid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-bottom:10px}
.attSummaryCard{background:var(--surface);border:1px solid var(--line);border-radius:15px;padding:10px 7px;text-align:center;box-shadow:0 7px 20px rgba(48,67,101,.04);min-width:0}
.attSummaryCard small{display:block;color:var(--muted);font-size:8px;line-height:1.25;min-height:20px}
.attSummaryCard b{display:block;font-size:13px;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.attSearchBar{display:grid;grid-template-columns:24px 1fr 32px;align-items:center;background:var(--surface2);border:1px solid var(--line);border-radius:15px;padding:5px 7px 5px 10px;margin-bottom:8px}
.attSearchBar>span{font-size:19px;color:var(--muted)}
.attSearchBar input{border:0;outline:0;background:transparent;min-height:38px;width:100%;font-size:13px}
.attSearchBar button{border:0;background:transparent;color:var(--muted);font-size:22px;min-height:34px}
.attFilters{margin-bottom:6px}
.attResetFilters{display:block;margin:0 0 10px auto;border:0;background:transparent;color:var(--muted);font-size:10px;font-weight:700;padding:3px 2px}
.shortday{background:#eef0f4;color:#59616d}
.recordSearchHit{font-weight:800}
@media(max-width:375px){.attSummaryGrid{grid-template-columns:1fr 1fr}.attSummaryCard small{min-height:auto}}
'''
if '/* v13.7 Attendance upgrade */' not in css:
    css += extra
p.write_text(css,encoding='utf-8')

# ---- Attendance JS ----
p=assets/'app.js'
s=p.read_text(encoding='utf-8')

old_status="function statusClass(s){return{'Present':'present','Absent':'absent','Paid Leave':'paid','Unpaid Leave':'unpaid','Half Day':'half','Holiday':'holiday','Week Off':'week'}[s]||''}"
new_status="function statusClass(s){return{'Present':'present','Absent':'absent','Paid Leave':'paid','Unpaid Leave':'unpaid','Half Day':'half','Short Day':'shortday','Holiday':'holiday','Week Off':'week'}[s]||''}"
if old_status not in s:
    raise SystemExit('statusClass anchor missing')
s=s.replace(old_status,new_status,1)

pat=re.compile(r"var attendanceRenderKey='',attendanceRenderHtml='';.*?\nfunction renderLeaves",re.S)
m=pat.search(s)
if not m:
    raise SystemExit('attendance renderer block missing')

new_block=r'''var attendanceRenderCache={},attendanceRenderOrder=[],attendanceSearchTimer=0;
function attendanceTimeTextFast(t,fmt){
 if(!t)return'--:--';
 var a=t.split(':'),h=+a[0],m=+a[1],p;
 if(fmt==='24h')return P(h)+':'+P(m);
 p=h>=12?'PM':'AM';
 return P(h%12||12)+':'+P(m)+' '+p
}
function attendanceTotalText(min){
 min=Math.max(0,Math.round(min||0));
 return Math.floor(min/60)+'h '+P(min%60)+'m'
}
function attendanceMonthLabel(mo){
 if(!/^\d{4}-\d{2}$/.test(String(mo||'')))return'This month';
 var d=new Date(mo+'-01T00:00:00');
 return isNaN(d.getTime())?mo:d.toLocaleDateString(undefined,{month:'long',year:'numeric'})
}
function attendanceMoveMonth(delta){
 var input=E('monthFilter'),mo=input.value||monthNow(),p=mo.split('-'),d=new Date(+p[0],(+p[1])-1+(delta||0),1);
 input.value=d.getFullYear()+'-'+P(d.getMonth()+1);
 renderAttendance()
}
function attendanceResetFilters(){
 E('monthFilter').value=monthNow();
 E('statusFilter').value='';
 E('attendanceSearch').value='';
 renderAttendance()
}
function attendanceApplySummary(x){
 x=x||{};
 E('attendanceMonthTitle').textContent=x.monthTitle||attendanceMonthLabel(E('monthFilter').value);
 E('attendanceMonthCount').textContent=(x.shown||0)+' shown • '+(x.records||0)+' records';
 E('attendanceSummaryPresent').textContent=x.present||0;
 E('attendanceSummaryWorked').textContent=attendanceTotalText(x.worked||0);
 E('attendanceSummaryBalance').textContent=signedDuration(x.balance||0);
 E('attendanceSummaryLeaves').textContent=x.leaves||0
}
function attendanceCachePut(key,value){
 attendanceRenderCache[key]=value;
 attendanceRenderOrder.push(key);
 while(attendanceRenderOrder.length>10){
  var old=attendanceRenderOrder.shift();
  if(old!==key)delete attendanceRenderCache[old]
 }
}
function renderAttendance(){
 var records=E('records'),mo=E('monthFilter').value||monthNow(),st=E('statusFilter').value||'',q=String(E('attendanceSearch').value||'').trim().toLowerCase(),raw='',settingsRaw='',key,cached,a,s,v=[],i,x,d,out='',worked,bal,monthRecords=0,present=0,leaves=0,totalWorked=0,totalBalance=0,hay;
 try{raw=localStorage.getItem(DATA_KEY)||'';settingsRaw=localStorage.getItem(SET_KEY)||''}catch(e){}
 key=mo+'\u001f'+st+'\u001f'+q+'\u001f'+settingsRaw+'\u001f'+raw;
 cached=attendanceRenderCache[key];
 if(cached){
  if(records.innerHTML!==cached.html)records.innerHTML=cached.html;
  attendanceApplySummary(cached.summary);
  return
 }
 a=dataGet();s=setGet();
 for(i=0;i<a.length;i++){
  x=a[i];
  if(x.date.indexOf(mo)!==0)continue;
  monthRecords++;
  worked=workMinutes(x.checkIn,x.checkOut);
  bal=window.AttendancePolicy?AttendancePolicy.balanceMinutes(x,s):dailyBalanceMinutes(x);
  totalWorked+=worked;totalBalance+=bal;
  if(x.status==='Present')present++;
  if(x.status==='Paid Leave'||x.status==='Unpaid Leave')leaves++;
  if(st&&x.status!==st)continue;
  if(q){
   hay=(String(x.date||'')+' '+String(x.status||'')+' '+String(x.reason||'')+' '+String(x.notes||'')+' '+String(x.checkIn||'')+' '+String(x.checkOut||'')).toLowerCase();
   if(hay.indexOf(q)<0)continue
  }
  v.push({record:x,worked:worked,balance:bal})
 }
 v.sort(function(q,w){return w.record.date.localeCompare(q.record.date)});
 for(i=0;i<v.length;i++){
  x=v[i].record;worked=v[i].worked;bal=v[i].balance;d=x.date.split('-');
  out+='<div class="record"><div class="recordTop"><div class="dateBlock"><b>'+d[2]+'</b><small>'+dayShort(x.date)+'</small></div><div class="recordMain"><div class="recordTimes"><div class="timeCol"><small>Clock In</small><b>'+attendanceTimeTextFast(x.checkIn,s.fmt)+'</b></div><div class="timeCol"><small>Clock Out</small><b>'+attendanceTimeTextFast(x.checkOut,s.fmt)+'</b></div><div class="timeCol"><small>Working</small><b>'+durationText(worked)+'</b></div></div></div><span class="statusBadge '+statusClass(x.status)+'">'+esc(x.status)+'</span></div><div class="recordMeta">'+(bal>=0?'OT: '+durationText(bal):'Short: '+durationText(-bal))+(x.reason?' • '+esc(x.reason):'')+(x.notes?' • '+esc(x.notes):'')+'</div><div class="recordActions"><button class="btn ghost editRecord" data-id="'+x.id+'">Edit</button><button class="btn deleteRecord" data-id="'+x.id+'">Delete</button></div></div>'
 }
 out=out||'<div class="empty">No attendance records match these filters.</div>';
 cached={html:out,summary:{monthTitle:attendanceMonthLabel(mo),shown:v.length,records:monthRecords,present:present,worked:totalWorked,balance:totalBalance,leaves:leaves}};
 attendanceCachePut(key,cached);
 if(records.innerHTML!==out)records.innerHTML=out;
 attendanceApplySummary(cached.summary)
}
function renderLeaves'''
s=s[:m.start()]+new_block+s[m.end():]

old_bind=" E('monthFilter').onchange=renderAttendance;E('statusFilter').onchange=renderAttendance;"
new_bind=""" E('monthFilter').onchange=renderAttendance;E('statusFilter').onchange=renderAttendance;
 E('attendancePrevMonth').onclick=function(){attendanceMoveMonth(-1)};
 E('attendanceNextMonth').onclick=function(){attendanceMoveMonth(1)};
 E('attendanceResetFilters').onclick=attendanceResetFilters;
 E('attendanceClearSearch').onclick=function(){if(E('attendanceSearch').value){E('attendanceSearch').value='';renderAttendance()}else E('attendanceSearch').focus()};
 E('attendanceSearch').oninput=function(){clearTimeout(attendanceSearchTimer);attendanceSearchTimer=setTimeout(renderAttendance,90)};"""
if old_bind not in s:
    raise SystemExit('attendance bind anchor missing')
s=s.replace(old_bind,new_bind,1)

p.write_text(s,encoding='utf-8')
print('v13.7 Attendance upgrade applied')
