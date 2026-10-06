from pathlib import Path
import re,sys,shutil
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
html=assets/'index.html'; app=assets/'app.js'
h=html.read_text(encoding='utf-8'); s=app.read_text(encoding='utf-8')

if 'v151-ui.css' not in h:
    if '<link rel="stylesheet" href="v15-features.css">' not in h: raise SystemExit('v15 CSS anchor missing')
    h=h.replace('<link rel="stylesheet" href="v15-features.css">','<link rel="stylesheet" href="v15-features.css">\n<link rel="stylesheet" href="v151-ui.css">',1)

attendance='''<section class="screen" id="screen-attendance">
      <div class="sectionHeader"><span class="pageLottie lottieIcon" data-lottie="lottie/attendance.json"></span><h1>Attendance</h1></div>
      <div class="attendanceHeroV15"><div class="attendanceStatsV15" id="attendanceStats"></div></div>
      <div class="attendanceCalendarCard" id="attendanceSwipeSurface">
        <div class="attendanceCalendarTitleRow">
          <button class="monthArrow" id="attendancePrevMonth" type="button" aria-label="Previous month">‹</button>
          <div class="attendanceCalendarTitle"><small>CALENDAR</small><b id="attendanceMonthTitle">Month</b></div>
          <button class="monthArrow" id="attendanceNextMonth" type="button" aria-label="Next month">›</button>
        </div>
        <input class="attendanceMonthInputV151" type="month" id="monthFilter" aria-label="Choose attendance month">
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
if not m: raise SystemExit('attendance screen missing')
h=h[:m.start()]+attendance+h[m.end():]

old_header='<div class="sectionHeader"><button class="back" type="button" data-screen="home">‹</button><span class="navIcon">🔔</span><h1>Notifications</h1><div class="notificationHeaderActions"><button class="notificationMiniBtn" id="notificationSettingsBtn" type="button" aria-label="Settings">⚙</button></div></div>'
new_header='<div class="sectionHeader"><button class="notificationBack" id="notificationBack" type="button" aria-label="Back to home">‹</button><span class="navIcon">🔔</span><h1>Notifications</h1></div>'
if old_header not in h: raise SystemExit('notification header anchor missing')
h=h.replace(old_header,new_header,1)

if 'v151-ui.js' not in h:
    if '<script src="v15-features.js"></script>' not in h: raise SystemExit('v15 JS anchor missing')
    h=h.replace('<script src="v15-features.js"></script>','<script src="v15-features.js"></script>\n<script src="v151-ui.js"></script>',1)
html.write_text(h,encoding='utf-8')

old="E('topSettings').onclick=function(){showScreen('settings')};"
new="E('topSettings').onclick=function(){showScreen('notifications')};"
if old not in s: raise SystemExit('legacy top settings handler missing')
s=s.replace(old,new,1)
app.write_text(s,encoding='utf-8')

shutil.copy('ci/v151-ui.css',assets/'v151-ui.css')
shutil.copy('ci/v151-ui.js',assets/'v151-ui.js')
print('v15.1 unified page UI and notification navigation patch applied')
