from pathlib import Path
import re, sys
assets=Path(sys.argv[1])
app=assets/'app.js'
s=app.read_text(encoding='utf-8')
old="function requiredMinutesForStatus(st){var s=setGet(),std=s.h*60+s.m;if(st==='Paid Leave'||st==='Holiday'||st==='Week Off')return 0;if(st==='Half Day')return Math.round(std/2);return std}\nfunction dailyBalanceMinutes(x){var s=setGet(),req=requiredMinutesForStatus(x.status),worked=workMinutes(x.checkIn,x.checkOut),diff;if(x.status==='Paid Leave'||x.status==='Holiday'||x.status==='Week Off')return 0;if(x.status==='Absent'||x.status==='Unpaid Leave')return-req;diff=worked-req;return diff>0?Math.max(0,diff-s.otDelay):diff}"
new="""function isSundayDate(date){var d=new Date(date+'T00:00:00');return !isNaN(d.getTime())&&d.getDay()===0}\nfunction specialDayFlag(date){try{return localStorage.getItem('attendance_special_ot_'+date)==='holiday'}catch(e){return false}}\nfunction isSpecialOTRecord(x){return !!(x&&(x.specialOT===true||x.status==='Holiday'||x.status==='Week Off'||isSundayDate(x.date)))}\nfunction requiredMinutesForStatus(st){var s=setGet(),std=s.h*60+s.m;if(st==='Paid Leave'||st==='Holiday'||st==='Week Off')return 0;if(st==='Half Day')return Math.round(std/2);return std}\nfunction dailyBalanceMinutes(x){var s=setGet(),req=requiredMinutesForStatus(x.status),worked=workMinutes(x.checkIn,x.checkOut),diff;if(isSpecialOTRecord(x))return worked;if(x.status==='Paid Leave')return 0;if(x.status==='Absent'||x.status==='Unpaid Leave')return-req;diff=worked-req;return diff>0?Math.max(0,diff-s.otDelay):diff}"""
if old not in s: raise SystemExit('daily balance anchor not found')
s=s.replace(old,new,1)
pat=r"function punch\(\)\{.*?\n\}\nfunction renderPunchButton"
newp="""function punch(){\n var a=dataGet(),x=null,i,t=nowTime24(),date=nowDate(),flagged=specialDayFlag(date),sunday=isSundayDate(date),def=flagged?'Holiday':(sunday?'Week Off':'Present');\n for(i=0;i<a.length;i++)if(a[i].date===date){x=a[i];break}\n if(!x){x={id:idNew(),date:date,status:def,checkIn:t,checkOut:'',reason:flagged?'Holiday':'',notes:'',specialOT:flagged||sunday};a.push(x);dataPut(a);toast('Clocked in at '+timeText(t))}\n else if(!x.checkIn){x.checkIn=t;if(flagged){x.status='Holiday';x.specialOT=true;if(!x.reason)x.reason='Holiday'}else if(sunday){if(x.status!=='Holiday')x.status='Week Off';x.specialOT=true}else if(x.status!=='Holiday'&&x.status!=='Week Off'){x.status='Present';x.specialOT=false}dataPut(a);toast('Clocked in at '+timeText(t))}\n else if(!x.checkOut){var finish=function(){x.checkOut=t;if(flagged||sunday||x.status==='Holiday'||x.status==='Week Off')x.specialOT=true;dataPut(a);toast('Clocked out at '+timeText(t));renderAll()};if(window.confirmClockOut){window.confirmClockOut(x,t,finish);return}finish();return}\n else{if(!confirm('Today is already completed. Start again and replace current times?'))return;x.checkIn=t;x.checkOut='';x.status=def;x.specialOT=flagged||sunday;if(flagged&&!x.reason)x.reason='Holiday';dataPut(a);toast('Clock in restarted')}\n renderAll()\n}\nfunction renderPunchButton"""
s2,n=re.subn(pat,newp,s,count=1,flags=re.S)
if n!=1: raise SystemExit('punch anchor not found')
s=s2
oldmeta="<div class=\"recordMeta\">OT: '+durationText(overtimeMinutes(x.checkIn,x.checkOut))"
newmeta="<div class=\"recordMeta\">'+(dailyBalanceMinutes(x)>=0?'OT: '+durationText(dailyBalanceMinutes(x)):'Short: '+durationText(-dailyBalanceMinutes(x)))"
if oldmeta not in s: raise SystemExit('record OT anchor not found')
s=s.replace(oldmeta,newmeta,1)
pat=r"function openEdit\(id\)\{.*?\nfunction closeEdit"
newe="""function refreshEditControl(id){var z=E(id);if(!z)return;try{z.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}\nfunction openEdit(id){var a=dataGet(),x=null,i,ids;for(i=0;i<a.length;i++)if(a[i].id===id){x=a[i];break}if(!x)return;E('editPopupId').value=x.id;E('editPopupDate').value=x.date;E('editPopupStatus').value=x.status;buildTime('editIn',x.checkIn);buildTime('editOut',x.checkOut);E('editPopupReason').value=x.reason||'';E('editPopupNotes').value=x.notes||'';ids=['editPopupDate','editPopupStatus','editInH','editInM','editInP','editOutH','editOutM','editOutP'];for(i=0;i<ids.length;i++)refreshEditControl(ids[i]);if(E('editPopupDate')._v112CalBtn)E('editPopupDate')._v112CalBtn.textContent=x.date;E('editModal').classList.add('show')}\nfunction closeEdit"""
s2,n=re.subn(pat,newe,s,count=1,flags=re.S)
if n!=1: raise SystemExit('openEdit anchor not found')
s=s2
app.write_text(s,encoding='utf-8')

v11=assets/'v11-ui.js'; v=v11.read_text(encoding='utf-8')
v2,n=re.subn(r"function updateRing\(\)\{.*?setInterval\(updateRing,1000\);setTimeout\(updateRing,200\);","function updateRing(){}",v,count=1,flags=re.S)
if n!=1: raise SystemExit('old ring updater anchor not found')
v11.write_text(v2,encoding='utf-8')

v112=assets/'v112-fixes.js'; q=v112.read_text(encoding='utf-8')
q2,n=re.subn(r"window\.addEventListener\('scroll',function\(\)\{var a=document\.querySelectorAll\('\.customSelect\.open'\),i;for\(i=0;i<a\.length;i\+\+\)a\[i\]\.classList\.remove\('open'\)\},true\);\n?","",q,count=1)
if n!=1: raise SystemExit('dropdown scroll closer anchor not found')
oldfun=re.search(r"function updateWorkRing\(\)\{.*?\}\n",q2,re.S)
if not oldfun: raise SystemExit('v112 ring function missing')
newfun="""function isSundayV113(date){var d=new Date(date+'T00:00:00');return !isNaN(d.getTime())&&d.getDay()===0}\nfunction specialV113(x){return !!(x&&(x.specialOT===true||x.status==='Holiday'||x.status==='Week Off'||isSundayV113(x.date)))}\nfunction updateWorkRing(){var btn=E('punchBtn'),wrap=btn&&btn.parentNode,ring=E('workProgressValue'),txt=E('workProgressText'),x=currentRecord(),s=getSettings(),std=s.h*60+s.m;if(!btn||!ring||!txt)return;var C=351.86;ring.style.strokeDasharray=C;ring.style.strokeDashoffset=C;var active=!!(x&&x.checkIn&&!x.checkOut);btn.classList.toggle('workProgressActive',active);if(wrap&&wrap.classList)wrap.classList.toggle('working',active);if(!active){txt.innerHTML='';return}var now=new Date(),start=minFrom(x.checkIn),cur=now.getHours()*60+now.getMinutes(),elapsed=cur-start;if(elapsed<0)elapsed+=1440;if(specialV113(x)){ring.style.strokeDashoffset='0';txt.innerHTML='<b>'+P(Math.floor(elapsed/60))+':'+P(elapsed%60)+'</b><small>overtime today</small>';return}if(!std){txt.innerHTML='';return}var pct=Math.max(0,Math.min(1,elapsed/std)),left=Math.max(0,std-elapsed);ring.style.strokeDashoffset=String(C*(1-pct));txt.innerHTML=left>0?('<b>'+P(Math.floor(left/60))+':'+P(left%60)+'</b><small>to work time</small>'):'<b>00:00</b><small>work time done</small>'}\n"""
q2=q2[:oldfun.start()]+newfun+q2[oldfun.end():]
v112.write_text(q2,encoding='utf-8')

index=assets/'index.html'; html=index.read_text(encoding='utf-8')
old='<button class="btn primary fullBtn" id="saveProfile" type="button">Save Profile</button><button class="btn dangerOutline fullBtn" id="deleteProfileBtn" type="button">Delete Profile</button>'
new='<button class="btn primary fullBtn" id="saveProfile" type="button">Save Profile</button>'
if old not in html: raise SystemExit('delete button inline anchor missing')
html=html.replace(old,new,1)
anchor='''      </div>\n    </section>\n\n    <section class="screen settingScreen" id="screen-setting-work">'''
danger='''      </div>\n      <div class="settingsCard profileDangerZone">\n        <div class="dangerZoneIcon">!</div>\n        <div class="dangerZoneTitle">Delete Profile</div>\n        <p>This is a permanent action. Before deletion, the app will ask you to verify and confirm several times.</p>\n        <ul><li>Attendance and salary records will be deleted.</li><li>Profile details, settings and local documents will be cleared.</li><li>Cloud backup and account data will be removed where available.</li><li>This action cannot be undone after final confirmation.</li></ul>\n        <div class="dangerZoneWarning">Make sure you have exported any data you want to keep.</div>\n        <button class="btn dangerOutline fullBtn" id="deleteProfileBtn" type="button">Delete Profile Permanently</button>\n      </div>\n    </section>\n\n    <section class="screen settingScreen" id="screen-setting-work">'''
if anchor not in html: raise SystemExit('profile section end anchor missing')
html=html.replace(anchor,danger,1)
html=html.replace('<link rel="stylesheet" href="v112-ui.css">','<link rel="stylesheet" href="v112-ui.css">\n<link rel="stylesheet" href="v113-ui.css">',1)
html=html.replace('<script src="v112-fixes.js"></script>','<script src="v112-fixes.js"></script>\n<script src="v113-fixes.js"></script>',1)
index.write_text(html,encoding='utf-8')
