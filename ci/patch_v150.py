from pathlib import Path
import re,sys,shutil
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
html=assets/'index.html'; app=assets/'app.js'
h=html.read_text(encoding='utf-8'); s=app.read_text(encoding='utf-8')

if 'v15-features.css' not in h:
    if '<link rel="stylesheet" href="v14-features.css">' in h:
        h=h.replace('<link rel="stylesheet" href="v14-features.css">','<link rel="stylesheet" href="v14-features.css">\n<link rel="stylesheet" href="v15-features.css">',1)
    else:
        h=h.replace('</head>','<link rel="stylesheet" href="v15-features.css">\n</head>',1)

top_pat=re.compile(r'(<button[^>]*id="topSettings"[^>]*>).*?(</button>)',re.S)
m=top_pat.search(h)
if not m: raise SystemExit('topSettings button missing')
h=h[:m.start()]+m.group(1)+'<span class="topBellGlyph" aria-hidden="true">🔔</span><span class="notificationBadge" id="notificationBadge" hidden>0</span>'+m.group(2)+h[m.end():]
h=re.sub(r'(<button[^>]*id="topSettings"[^>]*)(>)',lambda x:(x.group(1)+' aria-label="Notifications"'+x.group(2)) if 'aria-label=' not in x.group(1) else x.group(0),h,count=1)

attendance='''<section class="screen" id="screen-attendance">
      <div class="sectionHeader"><span class="pageLottie lottieIcon" data-lottie="lottie/attendance.json"></span><h1>Attendance</h1></div>
      <div class="attendanceHeroV15">
        <div class="attendanceMonthNavV15">
          <button class="monthArrow" id="attendancePrevMonth" type="button" aria-label="Previous month">‹</button>
          <div class="attendanceMonthTitleWrap"><small>ATTENDANCE MONTH</small><b id="attendanceMonthTitle">Month</b><div class="attendanceMonthPicker"><input type="month" id="monthFilter" aria-label="Choose month"></div></div>
          <button class="monthArrow" id="attendanceNextMonth" type="button" aria-label="Next month">›</button>
        </div>
        <div class="attendanceStatsV15" id="attendanceStats"></div>
      </div>
      <div class="attendanceCalendarCard" id="attendanceSwipeSurface">
        <div id="attendanceCalendar"></div>
        <div class="attendanceLegendV15"><span><i class="present"></i>Present</span><span><i class="absent"></i>Absent</span><span><i class="leave"></i>Leave</span><span><i class="special"></i>Holiday / Week Off</span></div>
        <div class="attendanceSwipeHint">Swipe left or right to change month • Tap any date to add or edit</div>
      </div>
      <div class="attendanceLegacyToggle"><button id="attendanceListTab" type="button">List</button><button id="attendanceCalendarTab" type="button">Calendar</button></div>
      <div class="attendanceRecordsHead"><div><b>Monthly Records</b><small id="attendanceResultCount">0 records</small></div><button class="btn ghost attendanceFilterBtn" id="attendanceFilterToggle" type="button">Filters</button></div>
      <div class="attendanceFiltersPanel" id="attendanceFiltersPanel" hidden>
        <div class="attendanceFiltersGrid">
          <div class="field full"><input id="attendanceSearch" type="search" placeholder="Search note, reason, status or date"></div>
          <div class="field"><select id="statusFilter"><option value="">All Status</option><option>Present</option><option>Absent</option><option>Paid Leave</option><option>Unpaid Leave</option><option>Half Day</option><option>Short Day</option><option>Holiday</option><option>Week Off</option></select></div>
          <div class="field"><button class="btn ghost" id="attendanceClearFilters" type="button">Clear Filters</button></div>
          <div class="field"><input type="date" id="attendanceFrom" aria-label="From date"></div>
          <div class="field"><input type="date" id="attendanceTo" aria-label="To date"></div>
        </div>
      </div>
      <div class="records" id="records"></div>
    </section>'''
pat=re.compile(r'<section class="screen" id="screen-attendance">.*?</section>',re.S)
m=pat.search(h)
if not m: raise SystemExit('attendance screen missing after v14 patch')
h=h[:m.start()]+attendance+h[m.end():]

notifications='''<section class="screen" id="screen-notifications">
      <div class="sectionHeader"><button class="back" type="button" data-screen="home">‹</button><span class="navIcon">🔔</span><h1>Notifications</h1><div class="notificationHeaderActions"><button class="notificationMiniBtn" id="notificationSettingsBtn" type="button" aria-label="Settings">⚙</button></div></div>
      <div class="notificationSummary">
        <div class="notificationSummaryTop"><div class="notificationCountBubble"><div><b id="notificationUnread">0</b><small>UNREAD</small></div></div><div class="notificationSummaryText"><b>Updates &amp; alerts in one place</b><small id="pushPermissionState">Checking notification permission…</small></div></div>
        <div class="notificationSummaryActions"><button class="btn primary" id="enablePushBtn" type="button">Enable Notifications</button><button class="btn ghost" id="notificationMarkAll" type="button">Mark All Read</button><button class="btn ghost" id="notificationClear" type="button">Clear</button></div>
        <div class="updateProgress" id="updateProgress" hidden><div class="updateProgressTrack"><div class="updateProgressBar" id="updateProgressBar"></div></div><small class="updateInstallStatus" id="updateInstallStatus"></small></div>
      </div>
      <div class="notificationVersionLine"><span>Notification history</span><span id="notificationVersion">Installed version</span></div>
      <div id="notificationList"></div>
    </section>

    '''
if 'id="screen-notifications"' not in h:
    sm=re.search(r'<section class="screen" id="screen-settings">',h)
    if not sm:
        sm=re.search(r'<section[^>]*id="screen-settings"[^>]*>',h)
    if not sm: raise SystemExit('settings screen anchor missing')
    h=h[:sm.start()]+notifications+h[sm.start():]

if 'v15-features.js' not in h:
    if '<script src="v14-features.js"></script>' in h:
        h=h.replace('<script src="v14-features.js"></script>','<script src="v14-features.js"></script>\n<script src="v15-features.js"></script>',1)
    else:
        h=h.replace('</body>','<script src="v15-features.js"></script>\n</body>',1)
html.write_text(h,encoding='utf-8')

old="function renderScreen(name){\n if(window.AttendanceV14&&AttendanceV14.renderScreen&&AttendanceV14.renderScreen(name)===true)return;"
new="function renderScreen(name){\n if(window.AttendanceV15&&AttendanceV15.renderScreen&&AttendanceV15.renderScreen(name)===true)return;\n if(window.AttendanceV14&&AttendanceV14.renderScreen&&AttendanceV14.renderScreen(name)===true)return;"
if old not in s: raise SystemExit('v15 render hook anchor missing')
s=s.replace(old,new,1)

old="if(window.AttendanceV14&&AttendanceV14.onDataChanged)AttendanceV14.onDataChanged();"
new="if(window.AttendanceV15&&AttendanceV15.onDataChanged)AttendanceV15.onDataChanged();if(window.AttendanceV14&&AttendanceV14.onDataChanged)AttendanceV14.onDataChanged();"
if old not in s: raise SystemExit('v15 data change hook anchor missing')
s=s.replace(old,new,1)

api_pat=re.compile(r'window\.AttendanceAppApi=\{([^}]*)\};')
m=api_pat.search(s)
if not m: raise SystemExit('AttendanceAppApi missing')
body=m.group(1)
for item in ['resetForm:resetForm','deleteRecord:deleteRecord']:
    if item not in body:
        body += ','+item
s=s[:m.start()]+'window.AttendanceAppApi={'+body+'};'+s[m.end():]
app.write_text(s,encoding='utf-8')

shutil.copy('ci/v15-features.js',assets/'v15-features.js')
shutil.copy('ci/v15-features.css',assets/'v15-features.css')
print('v15 notification center and attendance UI patch applied')
