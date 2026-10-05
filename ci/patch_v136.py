from pathlib import Path
import re, sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
p=assets/'app.js'
s=p.read_text(encoding='utf-8')

pat=re.compile(r"function renderAttendance\(\)\{.*?\n\}\nfunction renderLeaves",re.S)
m=pat.search(s)
if not m: raise SystemExit('renderAttendance block missing')

replacement=r'''var attendanceRenderKey='',attendanceRenderHtml='';
function attendanceTimeTextFast(t,fmt){
 if(!t)return'--:--';
 var a=t.split(':'),h=+a[0],m=+a[1],p;
 if(fmt==='24h')return P(h)+':'+P(m);
 p=h>=12?'PM':'AM';
 return P(h%12||12)+':'+P(m)+' '+p
}
function renderAttendance(){
 var records=E('records'),mo=E('monthFilter').value,st=E('statusFilter').value,raw='',settingsRaw='',key,a,s,v=[],i,x,d,out='',worked,bal,html;
 try{raw=localStorage.getItem(DATA_KEY)||'';settingsRaw=localStorage.getItem(SET_KEY)||''}catch(e){}
 key=mo+'\u001f'+st+'\u001f'+settingsRaw+'\u001f'+raw;
 if(key===attendanceRenderKey){
  if(records.innerHTML!==attendanceRenderHtml)records.innerHTML=attendanceRenderHtml;
  return
 }
 a=dataGet();s=setGet();
 for(i=0;i<a.length;i++)if((!mo||a[i].date.indexOf(mo)===0)&&(!st||a[i].status===st))v.push(a[i]);
 v.sort(function(q,w){return w.date.localeCompare(q.date)});
 for(i=0;i<v.length;i++){
  x=v[i];d=x.date.split('-');worked=workMinutes(x.checkIn,x.checkOut);
  bal=window.AttendancePolicy?AttendancePolicy.balanceMinutes(x,s):dailyBalanceMinutes(x);
  out+='<div class="record"><div class="recordTop"><div class="dateBlock"><b>'+d[2]+'</b><small>'+dayShort(x.date)+'</small></div><div class="recordMain"><div class="recordTimes"><div class="timeCol"><small>Clock In</small><b>'+attendanceTimeTextFast(x.checkIn,s.fmt)+'</b></div><div class="timeCol"><small>Clock Out</small><b>'+attendanceTimeTextFast(x.checkOut,s.fmt)+'</b></div><div class="timeCol"><small>Working</small><b>'+durationText(worked)+'</b></div></div></div><span class="statusBadge '+statusClass(x.status)+'">'+esc(x.status)+'</span></div><div class="recordMeta">'+(bal>=0?'OT: '+durationText(bal):'Short: '+durationText(-bal))+(x.reason?' • '+esc(x.reason):'')+(x.notes?' • '+esc(x.notes):'')+'</div><div class="recordActions"><button class="btn ghost editRecord" data-id="'+x.id+'">Edit</button><button class="btn deleteRecord" data-id="'+x.id+'">Delete</button></div></div>'
 }
 html=out||'<div class="empty">No attendance records for this filter.</div>';
 attendanceRenderKey=key;attendanceRenderHtml=html;
 if(records.innerHTML!==html)records.innerHTML=html
}
function renderLeaves'''
s=s[:m.start()]+replacement+s[m.end():]

old_all="function renderAll(){tick();loadSettings();renderProfile();renderHome();renderAttendance();renderLeaves();renderSalary();renderTheme()}"
new_all="function renderAll(){tick();loadSettings();renderProfile();renderHome();if(activeScreen()==='attendance')renderAttendance();renderLeaves();renderSalary();renderTheme()}"
if old_all not in s: raise SystemExit('renderAll attendance anchor missing')
s=s.replace(old_all,new_all,1)

old_init="renderDocuments();renderAll();initLottie(document);setInterval(tick,1000)"
new_init="renderDocuments();renderAll();initLottie(document);setTimeout(function(){if(activeScreen()!=='attendance')renderAttendance()},350);setInterval(tick,1000)"
if old_init not in s: raise SystemExit('init prewarm anchor missing')
s=s.replace(old_init,new_init,1)

p.write_text(s,encoding='utf-8')
print('v13.6 attendance performance patch applied')
