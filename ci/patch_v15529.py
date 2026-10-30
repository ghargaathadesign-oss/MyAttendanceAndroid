from pathlib import Path
import sys,shutil
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
def rep(s,a,b):
 if a not in s:raise SystemExit('Missing v15529 anchor: '+a[:100])
 return s.replace(a,b,1)
f=p/'app.js';s=f.read_text();s=rep(s,'sal.asOfDate=nowDate();','sal.autoWeekOffs=true;sal.employmentStartDate=profileGet().dateOfJoining;sal.asOfDate=nowDate();');f.write_text(s)
f=p/'v15-features.js';s=f.read_text();a=s.index('function renderStats(month){');b=s.index('\nfunction calendarMap',a)
s=s[:a]+'''function renderStats(month){
 var a=monthRecords(month),s=settings(),days=0,leave=0,hours=0,partial=0,i,x,st,d,c=A.salaryCalc(month);
 for(i=0;i<a.length;i++){x=a[i];if(x.date>A.nowDate())continue;st=AttendancePolicy.attendanceStatus(x);d=AttendancePolicy.daily(x,s,A.nowDate());hours+=worked(x);if(st==='Present'||st==='Half Day'||st==='Short Day'||st==='Half Day Holiday')days++;if(st==='Paid Leave'||st==='Unpaid Leave')leave++;if(st==='Half Day'||st==='Half Day Holiday'&&!d.pending&&AttendancePolicy.workedMinutes(x)<AttendancePolicy.requiredMinutes(x,s))partial++}
 var box=E('attendanceStats');if(!box)return;
 function card(value,label,icon){return '<div class="v15Stat"><span class="v15StatIcon v155StatLottie lottieIcon" data-lottie="lottie/'+icon+'" aria-hidden="true"></span><b>'+esc(value)+'</b><small>'+esc(label)+'</small></div>'}
 box.innerHTML=card(days,'Worked','worked-v155.json')+card(leave,'Leaves','leaves.json')+card(c.weekOffDays,'Week Off','week-off-v15522.json')+card(partial,'Half Day','half-day-v15522.json')+card(Math.round(hours/6)/10+'h','Hours','hours-v155.json')+card(duration(c.net),'Net OT / Short','work.json');
 if(window.initLottie)window.initLottie(box)
}'''+s[b:];f.write_text(s)
f=p/'v15521-home.js';s=f.read_text();s=rep(s,"E('qWeekOff').textContent=Object.keys(off).length;","E('qWeekOff').textContent=c.weekOffDays;");f.write_text(s)
f=p/'v1559-salary.js';s=f.read_text();s=rep(s,"detail('salaryPaidDays',num(c.paid)+' recorded paid day equivalents. Includes paid leave and recorded holidays/weekoffs; short time reduces paid days.');", "detail('salaryPaidDays',num(c.paid)+' paid day equivalents. Includes elapsed eligible Sundays, paid leave and recorded holidays/weekoffs; short time reduces paid days.');")
s=rep(s,"card('Holidays / Weekoffs',num(hol)+' / '+off,'Recorded holidays and all Sundays, plus recorded non-Sunday weekoffs. Only recorded paid days contribute to earned salary.');", "card('Holidays / Weekoffs',num(hol)+' / '+c.weekOffDays,'Recorded holidays and eligible elapsed paid weekoffs. Missing Sundays receive salary credit without creating attendance entries. Future dates are excluded.');")
f.write_text(s)
h=(p/'index.html').read_text();h=rep(h,'</head>','<link rel="stylesheet" href="v15529-fixes.css"></head>');(p/'index.html').write_text(h)
shutil.copy('ci/v15529-fixes.css',p/'v15529-fixes.css')
print('v15.5.29 paid Sundays, attendance cards, chart selection and aligned dropdown prepared')
