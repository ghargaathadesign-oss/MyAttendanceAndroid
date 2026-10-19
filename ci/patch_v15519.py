from pathlib import Path
import sys,shutil
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
def rep(s,a,b):
 if a not in s:raise SystemExit('Missing v15519 anchor '+a[:100])
 return s.replace(a,b,1)
h=(p/'index.html').read_text();h=rep(h,'<span class="inviteIcon" aria-hidden="true">✉</span>','<span class="menuLottie lottieIcon" data-lottie="lottie/invite-v15519.json" aria-hidden="true"></span>');h=h.replace('Paid leave stays unchanged','Apply OT and restore paid leave');h=rep(h,'<small id="salaryOtCoverStatus"','<p id="salaryOtCoverOutcome" class="otCoverOutcome" aria-live="polite"></p><small id="salaryOtCoverStatus"')
h=rep(h,'<div id="reportTrend" class="trendChart"></div></div>','<p class="reportChartNote">Required vs worked hours for recorded days. Future records are excluded.</p><div id="reportTrend" class="trendChart"></div></div><div class="settingsCard"><div class="label">MONTHLY IN / OUT TIMES</div><b id="reportPunchMonth" class="chartMonthLabel"></b><p class="reportChartNote">Swipe to view all dates. Missing punches are gaps. Overnight out times show +1 day.</p><div id="reportPunchChart"></div></div>')
h=rep(h,'</head>','<link rel="stylesheet" href="v15519-ui.css"></head>');h=rep(h,'</body>','<script src="v15519-leaves.js"></script><script src="v15519-reports.js"></script></body>');(p/'index.html').write_text(h)
f=p/'app.js';app=f.read_text();app=rep(app,'return AttendancePolicy.salaryMonth(dataGet(),month,setGet(),sal);','sal.asOfDate=nowDate();return AttendancePolicy.salaryMonth(dataGet(),month,setGet(),sal);');f.write_text(app)
# Net summaries use remaining overtime and the remaining uncovered shortfall.
v=(p/'v14-features.js').read_text();v=rep(v,'net:net,leave:leave,rate:', 'net:sc.net==null?net:sc.net,leave:leave,rate:');v=rep(v,'renderTrend(month);return true','renderTrend(month);if(window.AttendanceReports19)AttendanceReports19.render(month);return true');(p/'v14-features.js').write_text(v)
v=(p/'v15-features.js').read_text();v=rep(v,"var box=E('attendanceStats');","if(A&&A.salaryCalc)net=A.salaryCalc(month).net;var box=E('attendanceStats');");(p/'v15-features.js').write_text(v)
# Leave charges are calculated per date; OT-funded Paid Leave consumes no allowance.
f=p/'v15512-leaves.js';s=f.read_text()
helper='''function otPaidUsage(r,cutoff,cache){
 var month=r.date.slice(0,7),api=A();
 if(!cache[month]){var flags={};try{flags=JSON.parse(localStorage.getItem('attendance_ot_cover_v15518')||'{}')}catch(e){}var sal=api.salaryGet();sal.otCoverEnabled=flags[month]===true;cache[month]=AttendancePolicy.salaryMonth(api.dataGet().filter(function(x){return x.date<=cutoff}),month,api.setGet(),sal).otLeaveAllocations;}
 return Math.max(0,1-(cache[month][r.date]||0));
}
'''
s=rep(s,'function summary(month){',helper+'function summary(month){');s=rep(s,"cutoff=month<now?month+'-31':today;","cutoff=month<now?month+'-31':today,otCache={};")
s=rep(s,"yearUsed++;if(r.date.slice(0,7)<month)before++;else if(r.date.slice(0,7)===month)used++","var unit=otPaidUsage(r,cutoff,otCache);yearUsed+=unit;if(r.date.slice(0,7)<month)before+=unit;else if(r.date.slice(0,7)===month)used+=unit")
s=rep(s,"trackedUsed++;if(r.date.slice(0,7)<month)trackedBefore++","var unit=otPaidUsage(r,cutoff,otCache);trackedUsed+=unit;if(r.date.slice(0,7)<month)trackedBefore+=unit")
s=rep(s,"rows.forEach(function(r){var d=", "var historyCache={};rows.forEach(function(r){var charge=otPaidUsage(r,todayDate(),historyCache);var d=")
s=rep(s,"<b class=\"friendlyLeaveDay\">1 day</b>","<b class=\"friendlyLeaveDay\">'+(charge<1?num(1-charge)+' OT / '+num(charge)+' '+(r.status==='Paid Leave'?'PL':'unpaid'):'1 day')+'</b>")
f.write_text(s)
for name in ['v15519-ui.css','v15519-leaves.js','v15519-reports.js']:shutil.copy(Path('ci')/name,p/name)
print('v15.5.19 immediate OT cover, paid-leave refunds, Reports charts and Invite icon prepared')
