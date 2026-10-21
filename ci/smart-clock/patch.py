from pathlib import Path
import sys,shutil,json
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
def rep(s,a,b):
 if a not in s:raise SystemExit('Missing Smart Clock anchor '+a[:120])
 return s.replace(a,b,1)
h=(p/'index.html').read_text().replace('Smart Reminders','Smart Clock')
a=h.index('id="remClockInEnabled"');a=h.rfind('      <div class="settingsCard">',0,a)
h=h[:a]+h[a:].replace('      <div class="settingsCard">','      <div class="settingsCard"><label class="switchLine"><span><b>Clock Reminders</b><small>Enable or pause your saved clock-in, clock-out and missed-punch reminders.</small></span><input id="clockReminderMaster" type="checkbox" checked></label><div id="clockReminderControls">',1)
b=h.index('<p class="reminderInfo" id="reminderPermission">');h=h[:b]+'</div>'+h[b:]
b=h.index('    </section>',b);h=h[:b]+Path('ci/smart-clock/ui.html').read_text()+h[b:]
h=h.replace('</head>','<link rel="stylesheet" href="smart-clock.css"></head>',1).replace('</body>','<script src="smart-clock.js"></script></body>',1)
h=h.replace('Clock-in, clock-out and missed-punch notifications','Reminders and location-assisted attendance times')
h=h.replace('Documents are encrypted with Android Keystore and stored only on this device','Office coordinates and detected visits for Smart Clock stay encrypted on this device and are not included in backups or uploaded. Documents are encrypted with Android Keystore and stored only on this device')
(p/'index.html').write_text(h)
f=p/'app.js';s=f.read_text();s=rep(s,'function punch(){','function punch(smartTime,smartDate){');s=rep(s," if(x&&x.status==='Half Day Holiday'&&!sunday)flagged=false;", " if(typeof smartTime==='string'){if(smartDate!==date||!/^([01]\\d|2[0-3]):[0-5]\\d$/.test(smartTime)){toast('Please try again with today’s time');return}t=smartTime;}else if((!x||!x.checkIn||!x.checkOut)&&window.AttendanceSmartClock){var kind=x&&x.checkIn?'out':'in';if(AttendanceSmartClock.choose(kind,x,function(value,day){punch(value,day)}))return;}\n if(x&&x.status==='Half Day Holiday'&&!sunday)flagged=false;")
# Capture the chosen record state: abort if another save/account change happened while a dialog was open.
s=rep(s,'punch(value,day)}))return;',"var latest=currentRecord();if(JSON.stringify(latest||null)!==JSON.stringify(x||null)){toast('Attendance changed. Please tap again.');return}punch(value,day)}))return;")
s=rep(s,"function punch(smartTime,smartDate){","function punch(smartTime,smartDate){var punchAccount=window.AttendanceSmartClock?AttendanceSmartClock.accountKey():'';")
s=rep(s,"var finish=function(){x.checkOut=t;","var finish=function(){if(window.AttendanceSmartClock&&AttendanceSmartClock.accountKey()!==punchAccount||date!==nowDate()||JSON.stringify(currentRecord()||null)!==JSON.stringify(x||null)){toast('Attendance changed. Please tap again.');return}x.checkOut=t;")
(p/'app.js').write_text(s)
f=p/'v14-features.js';s=f.read_text();s=rep(s,"E('remClockInEnabled').checked=!!o.clockInEnabled;", "E('clockReminderMaster').checked=o.masterEnabled!==false;E('clockReminderControls').hidden=o.masterEnabled===false;E('remClockInEnabled').checked=!!o.clockInEnabled;");s=rep(s,"if((o.clockInEnabled||o.clockOutEnabled||o.missedEnabled)&&Android.requestNotificationPermission)","if(o.masterEnabled&&(o.clockInEnabled||o.clockOutEnabled||o.missedEnabled)&&Android.requestNotificationPermission)");s=rep(s,"function saveReminders(){var o={", "function saveReminders(){var o={masterEnabled:E('clockReminderMaster').checked,");f.write_text(s)
for a,b in [('ui.css','smart-clock.css'),('ui.js','smart-clock.js')]:shutil.copy(Path('ci/smart-clock')/a,p/b)
# Keep ordinary Clock Out confirmation accurate for shortened holidays as well.
f=p/'v113-fixes.js';s=f.read_text();s=rep(s,'std=s.h*60+s.m,special=isSpecial(record)',"std=window.AttendancePolicy&&AttendancePolicy.attendanceStatus(record)==='Half Day Holiday'?AttendancePolicy.requiredMinutes(record,s):s.h*60+s.m,special=isSpecial(record)");f.write_text(s)
print('Smart Clock settings, reminder master and confirmation-only detected times prepared')

f=p/'v15515-i18n.js';s=f.read_text();dictionary={'Smart Clock':'स्मार्ट क्लॉक','Clock Reminders':'क्लॉक रिमाइंडर','Location-Assisted Times':'स्थान आधारित समय','Use detected time':'पहचाना गया समय चुनें','Use current time':'वर्तमान समय चुनें','Edit time':'समय बदलें','Confirm time':'समय की पुष्टि करें','Confirm Clock In time':'क्लॉक इन समय की पुष्टि करें','Confirm Clock Out time':'क्लॉक आउट समय की पुष्टि करें','Detected arrival':'पहुँचने का पहचाना समय','Detected departure':'जाने का पहचाना समय','Office radius (metres)':'कार्यालय की सीमा (मीटर)','Use current location':'वर्तमान स्थान चुनें','Location permissions':'स्थान अनुमतियाँ','Save Location Settings':'स्थान सेटिंग्स सहेजें','Clear times':'पहचाने समय हटाएँ','Office latitude':'कार्यालय अक्षांश','Office longitude':'कार्यालय देशांतर','Today’s detected visits':'आज की पहचानी गई यात्राएँ'}
s=rep(s,'Object.keys(dictionary)', 'Object.assign(dictionary,'+json.dumps(dictionary,ensure_ascii=False)+');\nObject.keys(dictionary)');f.write_text(s)
# Keep the supplied logout animation's colours when the generated runtime is rebuilt.
f=p/'lottie-runtime.js';s=f.read_text()
if 'function isRedLogout(rec)' not in s:
 s=rep(s,'  function playOnce(rec)',"  function isRedLogout(rec){return !!(rec&&rec.container&&rec.container.classList&&rec.container.classList.contains('v1554LogoutLottie'));}\n  function playOnce(rec)")
 s=rep(s,'cfg.path=isThemeToggle(rec)?rec.originalPath:', 'cfg.path=(isThemeToggle(rec)||isRedLogout(rec))?rec.originalPath:')
 s=rep(s,'return;}try{if(rec.anim)rec.anim.destroy()}catch(e){}buildAnim(rec,rec.delay);}', 'return;}if(isRedLogout(rec))return;try{if(rec.anim)rec.anim.destroy()}catch(e){}buildAnim(rec,rec.delay);}')
 f.write_text(s)
