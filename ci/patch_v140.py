from pathlib import Path
import re,sys,shutil
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
html=assets/'index.html'; app=assets/'app.js'
h=html.read_text(encoding='utf-8'); s=app.read_text(encoding='utf-8')

if 'v14-features.css' not in h:
    h=h.replace('<link rel="stylesheet" href="diagnostics-ui.css">','<link rel="stylesheet" href="diagnostics-ui.css">\n<link rel="stylesheet" href="v14-features.css">',1)

pat=re.compile(r'<section class="screen" id="screen-attendance">.*?</section>\s*\n\s*<section class="screen" id="screen-add">',re.S)
m=pat.search(h)
if not m: raise SystemExit('attendance section missing')
attendance='''<section class="screen" id="screen-attendance">
      <div class="sectionHeader"><span class="pageLottie lottieIcon" data-lottie="lottie/attendance.json"></span><h1>Attendance</h1></div>
      <div class="attendanceMonthBar"><button class="monthArrow" id="attendancePrevMonth" type="button">‹</button><div class="field"><input type="month" id="monthFilter"></div><button class="monthArrow" id="attendanceNextMonth" type="button">›</button></div>
      <div class="attendanceStats" id="attendanceStats"></div>
      <div class="attendanceViewToggle"><button id="attendanceListTab" class="on" type="button">List</button><button id="attendanceCalendarTab" type="button">Calendar</button></div>
      <div class="attendanceSearchRow"><div class="field"><input id="attendanceSearch" type="search" placeholder="Search status, note, reason or date"></div><button class="btn ghost" id="attendanceClearFilters" type="button">Clear</button></div>
      <div class="filterRow" style="margin-top:8px"><div class="field"><select id="statusFilter"><option value="">All Status</option><option>Present</option><option>Absent</option><option>Paid Leave</option><option>Unpaid Leave</option><option>Half Day</option><option>Short Day</option><option>Holiday</option><option>Week Off</option></select></div></div>
      <div class="attendanceAdvancedFilters"><div class="field"><input type="date" id="attendanceFrom" aria-label="From date"></div><div class="field"><input type="date" id="attendanceTo" aria-label="To date"></div></div>
      <div class="attendanceFilterMeta"><span id="attendanceResultCount">0 records</span><span>Tap a calendar day to add or edit</span></div>
      <div id="attendanceCalendar" style="display:none"></div>
      <div class="records" id="records"></div>
    </section>

    <section class="screen" id="screen-add">'''
h=h[:m.start()]+attendance+h[m.end():]

anchor='<button class="settingsMenuRow" data-setting="backup"><span class="menuLottie lottieIcon" data-lottie="lottie/backup.json"></span><span><b>Backup</b><small>Cloud backup, CSV and Excel export</small></span><i>›</i></button>'
rows='''<button class="settingsMenuRow" data-setting="reports"><span class="menuLottie lottieIcon" data-lottie="lottie/salary.json"></span><span><b>Reports &amp; Analytics</b><small>Hours, attendance, OT, leave and salary trends</small></span><i>›</i></button>
        <button class="settingsMenuRow" data-setting="reminders"><span class="menuLottie lottieIcon" data-lottie="lottie/work.json"></span><span><b>Smart Reminders</b><small>Clock-in, clock-out and missed-punch notifications</small></span><i>›</i></button>
        <button class="settingsMenuRow" data-setting="privacy"><span class="menuLottie lottieIcon" data-lottie="lottie/profile.json"></span><span><b>Privacy &amp; App Lock</b><small>Require phone security when opening the app</small></span><i>›</i></button>
        '''+anchor
if 'data-setting="reports"' not in h:
    if anchor not in h: raise SystemExit('backup settings row missing')
    h=h.replace(anchor,rows,1)

backup_screen='<section class="screen settingScreen" id="screen-setting-backup">'
new_screens='''<section class="screen settingScreen" id="screen-setting-reports">
      <div class="sectionHeader"><button class="back settingBack" type="button">‹</button><span class="pageLottie lottieIcon" data-lottie="lottie/salary.json"></span><h1>Reports &amp; Analytics</h1></div>
      <div class="settingsCard"><div class="label">Report Month</div><div class="field"><input type="month" id="reportMonth"></div><small id="reportTracked" class="helpText"></small></div>
      <div class="reportGrid"><div class="reportCard"><b id="reportAttendanceRate">0%</b><small>Attendance Rate</small></div><div class="reportCard"><b id="reportWorked">0h</b><small>Working Hours</small></div><div class="reportCard"><b id="reportNet">0m</b><small>Net OT / Short</small></div><div class="reportCard"><b id="reportLeave">0</b><small>Leaves Used</small></div><div class="reportCard full"><b id="reportSalary">₹0</b><small>Estimated Salary Earned</small></div></div>
      <div class="settingsCard"><div class="label">6-MONTH WORKING HOURS TREND</div><div id="reportTrend" class="trendChart"></div></div>
    </section>

    <section class="screen settingScreen" id="screen-setting-reminders">
      <div class="sectionHeader"><button class="back settingBack" type="button">‹</button><span class="pageLottie lottieIcon" data-lottie="lottie/work.json"></span><h1>Smart Reminders</h1></div>
      <div class="settingsCard">
        <div class="reminderTimeGrid"><label class="switchLine"><span><b>Clock-in reminder</b><small>Skipped automatically after you clock in.</small></span><input id="remClockInEnabled" type="checkbox"></label><div class="field"><input id="remClockInTime" type="time" value="09:30"></div></div>
        <div class="reminderTimeGrid"><label class="switchLine"><span><b>Clock-out reminder</b><small>Only shown when you are still clocked in.</small></span><input id="remClockOutEnabled" type="checkbox"></label><div class="field"><input id="remClockOutTime" type="time" value="18:30"></div></div>
        <div class="reminderTimeGrid"><label class="switchLine"><span><b>Missed-punch warning</b><small>Warn if today's attendance is incomplete.</small></span><input id="remMissedEnabled" type="checkbox"></label><div class="field"><input id="remMissedTime" type="time" value="21:00"></div></div>
        <p class="reminderInfo" id="reminderPermission">Notification permission: checking…</p><div class="actions"><button class="btn primary" id="saveRemindersBtn" type="button">Save Reminders</button><button class="btn ghost" id="testReminderBtn" type="button">Send Test</button></div><small class="cloudStatus" id="reminderStatus"></small>
      </div>
    </section>

    <section class="screen settingScreen" id="screen-setting-privacy">
      <div class="sectionHeader"><button class="back settingBack" type="button">‹</button><span class="pageLottie lottieIcon" data-lottie="lottie/profile.json"></span><h1>Privacy &amp; App Lock</h1></div>
      <div class="settingsCard"><label class="switchLine"><span><b>Require phone security</b><small>Fingerprint, face, PIN, pattern or device password.</small></span><input id="appLockToggle" type="checkbox"></label><div class="label" style="margin-top:14px">Lock after leaving app</div><div class="field"><select id="appLockTimeout"><option value="0">Immediately</option><option value="30">30 seconds</option><option value="60">1 minute</option><option value="300">5 minutes</option></select></div><p class="privacyInfo" id="appLockDevice"></p><button class="btn primary fullBtn" id="saveAppLockBtn" type="button">Save App Lock</button><small class="cloudStatus" id="appLockStatus"></small></div>
    </section>

    '''+backup_screen
if 'screen-setting-reports' not in h:
    if backup_screen not in h: raise SystemExit('backup screen anchor missing')
    h=h.replace(backup_screen,new_screens,1)

hist_anchor='''      <div class="settingsCard"><div class="backupGrid"><button class="btn ghost" id="exportBtn" type="button">Export CSV</button>'''
hist='''      <div class="settingsCard"><div class="typographyHead"><span><b>Encrypted Restore Points</b><small>Backup Now keeps up to 5 previous cloud snapshots.</small></span><button class="btn ghost" id="refreshBackupHistoryBtn" type="button">Refresh</button></div><small class="cloudStatus" id="backupHistoryStatus">Open Backup to load restore points.</small><div id="backupHistoryList"></div></div>
      <div class="settingsCard"><div class="backupGrid"><button class="btn ghost" id="exportBtn" type="button">Export CSV</button>'''
if 'backupHistoryList' not in h:
    if hist_anchor not in h: raise SystemExit('backup export anchor missing')
    h=h.replace(hist_anchor,hist,1)

if 'v14-features.js' not in h:
    h=h.replace('<script src="v113-fixes.js"></script>','<script src="v113-fixes.js"></script>\n<script src="v14-features.js"></script>',1)
html.write_text(h,encoding='utf-8')

old="function dataPut(a){try{localStorage.setItem(DATA_KEY,JSON.stringify(a));return true}catch(e){toast('Could not save attendance');return false}}"
new="function dataPut(a){try{localStorage.setItem(DATA_KEY,JSON.stringify(a));if(window.AttendanceV14&&AttendanceV14.onDataChanged)AttendanceV14.onDataChanged();return true}catch(e){toast('Could not save attendance');return false}}"
if old not in s: raise SystemExit('dataPut anchor missing')
s=s.replace(old,new,1)
old_render="function renderScreen(name){\n if(name==='home'){tick();renderHome();return}"
new_render="function renderScreen(name){\n if(window.AttendanceV14&&AttendanceV14.renderScreen&&AttendanceV14.renderScreen(name)===true)return;\n if(name==='home'){tick();renderHome();return}"
if old_render not in s: raise SystemExit('renderScreen anchor missing')
s=s.replace(old_render,new_render,1)
api='''window.AttendanceAppApi={dataGet:dataGet,setGet:setGet,salaryCalc:salaryCalc,workMinutes:workMinutes,durationText:durationText,signedDuration:signedDuration,money:money,showScreen:showScreen,openEdit:openEdit,dayShort:dayShort,statusClass:statusClass,esc:esc,monthNow:monthNow,nowDate:nowDate,renderAll:renderAll,renderHome:renderHome};\n'''
if 'window.AttendanceAppApi=' not in s:
    init_anchor='function init(){\n'
    if init_anchor not in s: raise SystemExit('init anchor missing')
    s=s.replace(init_anchor,api+init_anchor,1)

old_bind="E('monthFilter').onchange=renderAttendance;E('statusFilter').onchange=renderAttendance;"
new_bind="E('monthFilter').onchange=function(){if(window.AttendanceV14&&AttendanceV14.renderScreen)AttendanceV14.renderScreen('attendance');else renderAttendance()};E('statusFilter').onchange=function(){if(window.AttendanceV14&&AttendanceV14.renderScreen)AttendanceV14.renderScreen('attendance');else renderAttendance()};"
if old_bind not in s: raise SystemExit('v14 attendance bind anchor missing')
s=s.replace(old_bind,new_bind,1)
old_prewarm="setTimeout(function(){if(activeScreen()!=='attendance')renderAttendance()},350)"
new_prewarm="setTimeout(function(){if(activeScreen()!=='attendance'){if(window.AttendanceV14&&AttendanceV14.renderScreen)AttendanceV14.renderScreen('attendance');else renderAttendance()}},350)"
if old_prewarm not in s: raise SystemExit('v14 prewarm anchor missing')
s=s.replace(old_prewarm,new_prewarm,1)
app.write_text(s,encoding='utf-8')

dp=assets/'diagnostics-ui.js'; ds=dp.read_text(encoding='utf-8')
old_sec="+row('App Check client',n.appCheckEnabled===true?'Enabled':(n.appCheckEnabled===false?'Disabled':'Checking'),n.appCheckEnabled===true?'ok':(n.appCheckEnabled===false?'warn':''))+row('Firebase account'"
new_sec="+row('App Check client',n.appCheckEnabled===true?'Enabled':(n.appCheckEnabled===false?'Disabled':'Checking'),n.appCheckEnabled===true?'ok':(n.appCheckEnabled===false?'warn':''))+row('App lock',n.appLockEnabled===true?'Enabled':'Off',n.appLockEnabled===true?'ok':'')+row('Reminder notifications',n.reminderPermission||'Unknown',n.reminderPermission==='granted'||n.reminderPermission==='not_required'?'ok':'warn')+row('Firebase account'"
if old_sec in ds: ds=ds.replace(old_sec,new_sec,1)
old_cloud="+row('Switch-device copy',c.hasTransfer===true?'Available':(c.exists?'No':'—'),c.hasTransfer===true?'ok':'')+row('Encrypted size'"
new_cloud="+row('Switch-device copy',c.hasTransfer===true?'Available':(c.exists?'No':'—'),c.hasTransfer===true?'ok':'')+row('Previous restore points',c.exists?String(c.historyCount||0):'—',c.historyCount>0?'ok':'')+row('Encrypted size'"
if old_cloud in ds: ds=ds.replace(old_cloud,new_cloud,1)
dp.write_text(ds,encoding='utf-8')

shutil.copy('ci/v14-features.js',assets/'v14-features.js')
shutil.copy('ci/v14-features.css',assets/'v14-features.css')
print('v14 Steps 13-18 UI patch applied')
