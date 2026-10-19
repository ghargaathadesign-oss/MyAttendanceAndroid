from pathlib import Path
import sys,re,shutil
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
def rep(s,a,b):
 if a not in s:raise SystemExit('Missing v15524 anchor '+a[:100])
 return s.replace(a,b,1)
s=(p/'app.js').read_text()
# A verified write invalidates every dependent view before a caller can render.
s=rep(s," if(!ok){toast('Could not save '+(label||'data'));return false}\n return true", " if(!ok){toast('Could not save '+(label||'data'));return false}\n dataChanged(key);return true")
# Read-through snapshots last only for one synchronous render; writes clear them.
for name,nextname in [('dataGet','dataPut'),('setGet','setPut'),('profileGet','profilePut'),('leaveGet','leavePut'),('salaryGet','salaryPut')]:
 start=s.index('function '+name+'(');end=s.index('function '+nextname+'(',start);part=s[start:end].replace('localStorage.getItem(','viewRead(')
 if name=='dataGet':
  part=rep(part,"function dataGet(){var keys=", "function dataGet(){if(viewFrame&&viewFrame.data)return viewFrame.data.map(function(r){return Object.assign({},r)});var keys=")
  part=rep(part,"a=JSON.parse(r);", "viewStats.dataParses++;a=JSON.parse(r);")
  part=rep(part,'}return a}', '}if(viewFrame)viewFrame.data=a.map(function(r){return Object.assign({},r)});return a}')
 s=s[:start]+part+s[end:]
start=s.index('function salaryCalc(');end=s.index('function money(',start);part=s[start:end]
part=rep(part,'function salaryCalc(month){','function salaryCalc(month){if(viewFrame&&viewFrame.salary[month])return Object.assign({},viewFrame.salary[month]);')
part=part.replace('localStorage.getItem(','viewRead(')
part=rep(part,'return AttendancePolicy.salaryMonth(dataGet(),month,setGet(),sal);','viewStats.salaryCalculations++;var result=AttendancePolicy.salaryMonth(dataGet(),month,setGet(),sal);if(viewFrame)viewFrame.salary[month]=result;return Object.assign({},result);')
s=s[:start]+part+s[end:]
# Home has one data owner; remove the legacy summary pass overwritten by Home21.
a=s.index('function renderHome(){');b=s.index('\nfunction ',a+1)
s=s[:a]+'''function renderHome(){
 var x=currentRecord();E('homeIn').textContent=x?timeText(x.checkIn):'--:--';E('homeOut').textContent=x?timeText(x.checkOut):'--:--';E('homeWorked').textContent=x?durationText(workMinutes(x.checkIn,x.checkOut)):'--';renderPunchButton();if(window.AttendanceHome21)AttendanceHome21.render();
}
'''+s[b:]
s=rep(s,"if(activeScreen()==='setting-salary')renderSalary();renderTheme()}","if(activeScreen()==='setting-salary')renderSalary();if(activeScreen()==='setting-reports')renderScreen('setting-reports');renderTheme()}")
s=rep(s,'window.AttendanceAppApi={',Path('ci/v15524-cache.js').read_text()+'\nwindow.AttendanceAppApi={readView:viewRead,withView:withView,viewStats:viewStats,dataRevision:function(){return dataRevision},invalidateData:function(){dataChanged(\'attendance_v8\')},')
(p/'app.js').write_text(s)
# Avoid redundant startup auth bridge requests; the verified snapshot and cloud UI remain authoritative.
f=p/'v152-fixes.js';v=f.read_text();v=rep(v,'var previousAuth=window.onNativeAuthChanged;',"var previousAuth=window.onNativeAuthChanged,lastAuthKey='';")
v=rep(v,'if(window.AttendanceAppApi)queueRender();',"var key=JSON.stringify([user&&user.uid,user&&user.signedIn,user&&user.emailVerified,user&&user.name,user&&user.email,user&&user.photo]);if(key!==lastAuthKey&&window.AttendanceAppApi){lastAuthKey=key;queueRender()}")
v=rep(v,'function requestAuth(){try{','function requestAuth(){if(window.attendanceInitialAuth)return;try{');f.write_text(v)
f=p/'app.js';v=f.read_text();v=v.replace(" init();\n if(window.Android&&Android.authState){try{Android.authState()}catch(e){}}", " init();");f.write_text(v)
# Build custom control menus when their page/modal opens, not for every hidden form at startup.
f=p/'v11-ui.js';v=f.read_text();v=rep(v,'function decorateAllSelects(root){',"function controlVisible(el){var screen=el.closest('.screen'),modal=el.closest('#editModal');return (!screen||screen.classList.contains('active'))&&(!modal||modal.classList.contains('show'))&&!el.closest('[hidden]')}\nfunction decorateAllSelects(root){")
v=rep(v,'for(i=0;i<a.length;i++)decorateSelect(a[i])','for(i=0;i<a.length;i++)if(controlVisible(a[i]))decorateSelect(a[i])')
v=rep(v,'function init(){decorateAllSelects(document);','window.attendanceDecorateSelects=decorateAllSelects;function init(){decorateAllSelects(document);');f.write_text(v)
f=p/'v112-fixes.js';v=f.read_text();v=rep(v,'for(i=0;i<a.length;i++)decorateDateV112(a[i])',"for(i=0;i<a.length;i++){var screen=a[i].closest('.screen'),modal=a[i].closest('#editModal');if((!screen||screen.classList.contains('active'))&&(!modal||modal.classList.contains('show')))decorateDateV112(a[i])}")
v=rep(v,'function init(){decorateDatesV112(document);','window.attendanceDecorateDates=decorateDatesV112;function init(){decorateDatesV112(document);');f.write_text(v)
# Remove duplicate startup renders and chart work for hidden Home.
f=p/'v15511-updates.js';s=f.read_text().replace('if(A())A().renderAll();renderPunchTimes()','renderPunchTimes()');f.write_text(s)
f=p/'v15521-home.js';s=f.read_text();s=s.replace("if(key!==chartKey){", "if(E('screen-home').classList.contains('active')&&key!==chartKey){")
s=s.replace("function init(){render();document.addEventListener('attendance-language-changed',render)}", "function init(){document.addEventListener('attendance-language-changed',function(){if(E('screen-home').classList.contains('active'))A().renderHome()})}")
# A() is not a local helper in Home21.
s=s.replace("A().renderHome()", "window.AttendanceAppApi.renderHome()")
f.write_text(s)
# Leave usage shares the monthly OT allocation rather than recalculating history.
f=p/'v15512-leaves.js';s=f.read_text();s=rep(s,"AttendancePolicy.salaryMonth(api.dataGet().filter(function(x){return x.date<=cutoff}),month,api.setGet(),sal).otLeaveAllocations", "api.salaryCalc(month).otLeaveAllocations");f.write_text(s)
# Totals on Reports are elapsed-date totals and net salary includes saved adjustment.
f=p/'v14-features.js';s=f.read_text();s=rep(s,'function monthMetrics(month){var a=monthRecords(month),','function monthMetrics(month){var a=monthRecords(month).filter(function(r){return r.date<=today()}),')
s=rep(s,"var sc=A&&A.salaryCalc?A.salaryCalc(month):{earned:0};return", "var sc=A&&A.salaryCalc?A.salaryCalc(month):{earned:0},adj={};try{adj=JSON.parse(localStorage.getItem('attendance_salary_adjustments_v1559')||'{}')[month]||{}}catch(e){}var adjustment=(Number(adj.amount)||0)*(adj.type==='subtract'?-1:1);return")
s=rep(s,'salary:(sc.netEarned===undefined?sc.earned:sc.netEarned)||0','salary:((sc.netEarned===undefined?sc.earned:sc.netEarned)||0)+adjustment')
s=rep(s,"E('reportNet').textContent=duration(x.net)","E('reportNet').textContent=A&&A.signedDuration?A.signedDuration(x.net):duration(x.net)")
s=rep(s,"renderTrend(month);if(window.AttendanceReports19)AttendanceReports19.render(month)","if(window.AttendanceReports19)AttendanceReports19.render(month);else renderTrend(month)")
f.write_text(s)
# Attendance month summary agrees with elapsed Home/Reports totals; future calendar records remain visible.
f=p/'v15-features.js';s=f.read_text();s=rep(s,'var a=monthRecords(month),s=settings(),days=0','var a=monthRecords(month).filter(function(r){return r.date<=today()}),s=settings(),days=0');f.write_text(s)
# Exports use canonical attendance and the same post-cover monthly net balance.
f=p/'v112-fixes.js';s=f.read_text();s=rep(s,'function getRecords(){try{','function getRecords(){if(window.AttendanceAppApi)return AttendanceAppApi.dataGet();try{')
s=rep(s,'tw+=w;tr+=req;if(bal>0)to+=bal;else ts+=-bal;net+=bal;','if(date<=today()){tw+=w;tr+=req;if(bal>0)to+=bal;else ts+=-bal;net+=bal;}')
s=rep(s,'}var t=row+1;',"}if(window.AttendanceAppApi){var calculation=AttendanceAppApi.salaryCalc(year+'-'+P(month+1));net=calculation.net;ts=calculation.remainingShortfall;}var t=row+1;")
f.write_text(s)
# A minute-resolution display must not reread full history every second.
f=p/'v112-fixes.js';s=f.read_text();s=rep(s,'function updateWorkRing(){var btn=',"var ringMinuteKey='';function updateWorkRing(){if(document.hidden||!E('screen-home').classList.contains('active'))return;var nextKey=Math.floor(Date.now()/60000)+'|'+(window.AttendanceAppApi?AttendanceAppApi.dataRevision():0);if(nextKey===ringMinuteKey)return;ringMinuteKey=nextKey;var btn=");f.write_text(s)
# Skip translation/decoration scans for SVG mutation traffic. Animations play on entry, not continuously.
f=p/'lottie-runtime.js';s=f.read_text();s=rep(s,"function playOnce(rec){if(!rec||!rec.anim)return;", "function playOnce(rec){if(!rec||!rec.anim||document.hidden||!lottieVisible(rec.container))return;")
a=s.index('  function scheduleNormalReplay(');b=s.index('\n  function attachLifecycle',a);s=s[:a]+"  function scheduleNormalReplay(rec){clearTimer(rec);}\n"+s[b:]
s=s.replace('delay:(sequence++%10)*380','delay:0')
s=s.replace("if(rec.container&&document.documentElement.contains(rec.container)){alive.push(rec);reloadForTheme(rec)}","if(rec.container&&document.documentElement.contains(rec.container)&&lottieVisible(rec.container)){alive.push(rec);reloadForTheme(rec)}").replace("else{clearTimer(rec);try{if(rec.anim)rec.anim.destroy()}catch(e){}}}records=alive;","else{clearTimer(rec);try{if(rec.anim)rec.anim.destroy();if(rec.container)rec.container.removeAttribute('data-lottie-ready')}catch(e){}}}records=alive;")
s=rep(s,"function lottieVisible(el){var screen=", "function lottieVisible(el){if(document.hidden||!el||el.closest('[hidden]'))return false;var screen=")
s=rep(s,"var path=el.getAttribute('data-lottie');if(!path)return;", "var path=el.getAttribute('data-lottie');if(!path||!lottieVisible(el))return;if(viewportObserver&&!el._lottieInView){viewportObserver.observe(el);return;}")
a=s.index('  function start(){');b=s.index("  if(document.readyState",a)
s=s[:a]+'''  var viewportObserver=typeof IntersectionObserver==='function'?new IntersectionObserver(function(entries){entries.forEach(function(entry){var el=entry.target;el._lottieInView=entry.isIntersecting;if(entry.isIntersecting&&lottieVisible(el)){if(el.getAttribute('data-lottie-ready')!=='1')initOne(el);else try{el._attendanceLottie.goToAndPlay(0,true)}catch(e){}}else try{el._attendanceLottie.pause()}catch(e){}})},{rootMargin:'100px'}):null;
  function pauseHidden(){records.forEach(function(rec){if(!lottieVisible(rec.container))try{rec.anim.pause()}catch(e){}})}
  function cleanup(){records=records.filter(function(rec){if(document.documentElement.contains(rec.container))return true;clearTimer(rec);try{rec.anim.destroy();if(viewportObserver)viewportObserver.unobserve(rec.container)}catch(e){}return false})}
  function start(){observeTheme();window.initLottie(document);document.addEventListener('visibilitychange',function(){pauseHidden();if(!document.hidden)window.initLottie(document)});new MutationObserver(function(ms){var clean=false;ms.forEach(function(m){var target=m.target;if(target&&target.closest&&target.closest('svg,[data-lottie]'))return;if(m.type==='attributes'){if(target.classList&&target.classList.contains('screen')){pauseHidden();if(target.classList.contains('active'))window.initLottie(target)}return}m.addedNodes.forEach(function(n){if(n.nodeType===1&&n.namespaceURI!=='http://www.w3.org/2000/svg')window.initLottie(n)});m.removedNodes.forEach(function(n){if(n.nodeType===1&&(n.hasAttribute('data-lottie')||n.querySelector('[data-lottie]')))clean=true})});if(clean)cleanup()}).observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class']});}
'''+s[b:];f.write_text(s)
h=(p/'index.html').read_text().replace('Estimated Salary Earned','Net Salary Earned').replace('<small>Leaves Used</small>','<small>Leaves Taken</small>').replace('</head>','<link rel="stylesheet" href="v15524-ui.css"></head>',1).replace('</body>','<script src="v15524-ui.js"></script></body>',1);(p/'index.html').write_text(h)
for name in ['v15524-ui.js','v15524-ui.css']:shutil.copy(Path('ci')/name,p/name)
print('v15.5.24 scoped render snapshots, synchronized totals, quiet observers and responsive layout prepared')
