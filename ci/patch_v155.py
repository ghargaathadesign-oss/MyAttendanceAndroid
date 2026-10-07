from pathlib import Path
import re, sys, shutil

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
index=assets/'index.html'
app=assets/'app.js'
v15=assets/'v15-features.js'
v112=assets/'v112-fixes.js'

h=index.read_text(encoding='utf-8')
s=app.read_text(encoding='utf-8')
v=v15.read_text(encoding='utf-8')
d=v112.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global h
    if old not in h:
        raise SystemExit(label+' anchor missing')
    h=h.replace(old,new,1)

# v15.5 stylesheet
if 'v155-icons.css' not in h:
    if '</head>' not in h: raise SystemExit('head close missing')
    h=h.replace('</head>','<link rel="stylesheet" href="v155-icons.css">\n</head>',1)

# Settings menu icon map
menu_map={
    'appearance':'lottie/appearance-v155.json',
    'reports':'lottie/reports-v155.json',
    'reminders':'lottie/reminder-v155.json',
    'privacy':'lottie/privacy-v155.json',
    'diagnostics':'lottie/diagnose-v155.json'
}
for setting,path in menu_map.items():
    pat=re.compile(r'(<button class="settingsMenuRow" data-setting="'+re.escape(setting)+r'">\s*<span class="menuLottie lottieIcon" data-lottie=")[^"]+(")')
    h,n=pat.subn(r'\1'+path+r'\2',h,count=1)
    if n!=1: raise SystemExit('settings icon missing: '+setting)

# Matching page-header icons
screen_map={
    'appearance':'lottie/appearance-v155.json',
    'reports':'lottie/reports-v155.json',
    'reminders':'lottie/reminder-v155.json',
    'privacy':'lottie/privacy-v155.json',
    'diagnostics':'lottie/diagnose-v155.json'
}
for screen,path in screen_map.items():
    pat=re.compile(r'(<section class="screen settingScreen" id="screen-setting-'+re.escape(screen)+r'">.*?<div class="sectionHeader">.*?<span class="pageLottie lottieIcon" data-lottie=")[^"]+(")',re.S)
    h,n=pat.subn(r'\1'+path+r'\2',h,count=1)
    if n!=1: raise SystemExit('page header icon missing: '+screen)

# Logout icon
old='<span class="logoutGlyph" aria-hidden="true">↪</span>'
new='<span class="v155LogoutLottie lottieIcon" data-lottie="lottie/logout-v155.json" aria-hidden="true"></span>'
replace_once(old,new,'logout glyph')

# Main notification bell + Notification page header
old='<span class="topBellGlyph" aria-hidden="true">🔔</span>'
new='<span class="v155TopBell lottieIcon" data-lottie="lottie/notification-v155.json" aria-hidden="true"></span>'
replace_once(old,new,'main notification glyph')
h,n=re.subn(r'<span class="navIcon">🔔</span>', '<span class="navIcon lottieIcon" data-lottie="lottie/notification-v155.json" aria-hidden="true"></span>', h, count=1)
if n!=1: raise SystemExit('notification page header icon missing')

# Home Monthly Overview Present
pat=re.compile(r'(<div class="miniCard"><span class="miniLottie lottieIcon" data-lottie=")[^"]+("></span><b id="qPresent">)')
h,n=pat.subn(r'\1lottie/present-v155.json\2',h,count=1)
if n!=1: raise SystemExit('home Present icon missing')

# Theme light/dark switch: keep existing ids/bindings, use supplied animation as the visual toggle.
pat=re.compile(r'<div class="themeVisualToggle">.*?</div>',re.S)
theme='''<div class="themeVisualToggle v155ThemeToggle"><button id="themeLight" type="button" aria-label="Light mode"><small>Light</small></button><span class="v155ThemeLottie lottieIcon" data-lottie="lottie/theme-v155.json" aria-hidden="true"></span><button id="themeDark" type="button" aria-label="Dark mode"><small>Dark</small></button></div>'''
h,n=pat.subn(theme,h,count=1)
if n!=1: raise SystemExit('theme toggle missing')

# Smart Reminders: supplied clock in header/menu and one clock on the right of each time box.
h=h.replace('class="reminderTimeGrid"','class="reminderTimeGrid v155ReminderRow"',3)
for rid in ['remClockInTime','remClockOutTime','remMissedTime']:
    pat=re.compile(r'<div class="field"><input id="'+rid+r'" type="time" value="([^"]+)"></div>')
    repl=r'<div class="field v155ReminderTime"><input id="'+rid+r'" type="time" value="\1"><span class="v155ReminderClock lottieIcon" data-lottie="lottie/reminder-v155.json" aria-hidden="true"></span></div>'
    h,n=pat.subn(repl,h,count=1)
    if n!=1: raise SystemExit('reminder time field missing: '+rid)

# Startup: replace old 3-dot loader with supplied Lottie.
old='<span class="v154BootDots" aria-hidden="true"><i></i><i></i><i></i></span>'
new='<span class="v154BootLottie lottieIcon" data-lottie="lottie/loading-v155.json" aria-hidden="true"></span>'
replace_once(old,new,'startup dot loader')

index.write_text(h,encoding='utf-8')

# Attendance stats: supplied Worked + Hours, default Leaves, same work icon as Home Net OT/Deficit.
pat=re.compile(r'function renderStats\(month\)\{.*?\nfunction calendarMap',re.S)
m=pat.search(v)
if not m: raise SystemExit('v15 renderStats missing')
stats=r"""function renderStats(month){
 var a=monthRecords(month),s=settings(),days=0,leave=0,hours=0,net=0,i,x;
 for(i=0;i<a.length;i++){x=a[i];hours+=worked(x);net+=balance(x,s);if(x.status==='Present'||x.status==='Half Day'||x.status==='Short Day')days++;if(x.status==='Paid Leave'||x.status==='Unpaid Leave')leave++}
 var box=E('attendanceStats');if(!box)return;
 box.innerHTML='<div class="v15Stat"><span class="v15StatIcon v155StatLottie lottieIcon" data-lottie="lottie/worked-v155.json"></span><b>'+days+'</b><small>Worked</small></div><div class="v15Stat"><span class="v15StatIcon v155StatLottie lottieIcon" data-lottie="lottie/leaves.json"></span><b>'+leave+'</b><small>Leaves</small></div><div class="v15Stat"><span class="v15StatIcon v155StatLottie lottieIcon" data-lottie="lottie/hours-v155.json"></span><b>'+Math.round(hours/6)/10+'h</b><small>Hours</small></div><div class="v15Stat"><span class="v15StatIcon v155StatLottie lottieIcon" data-lottie="lottie/work.json"></span><b>'+esc(duration(net))+'</b><small>Net OT / Short</small></div>';
 if(window.initLottie)window.initLottie(box)
}
function calendarMap"""
v=v[:m.start()]+stats+v[m.end():]

# When a calendar day opens Add Attendance, keep the new Calendar icon intact.
v=v.replace("if(d._v112CalBtn)d._v112CalBtn.textContent=date","if(window.v155SetDateButton)window.v155SetDateButton(d,date)",1)
v15.write_text(v,encoding='utf-8')

# Date selector decoration for every input[type=date].
old_func=re.compile(r"function decorateDateV112\(inp\)\{.*?\}\nfunction decorateDatesV112",re.S)
m=old_func.search(d)
if not m: raise SystemExit('decorateDateV112 missing')
new_func=r"""function v155DateButtonSet(inp,value){
 var b=inp&&inp._v112CalBtn,label=b&&b.querySelector?b.querySelector('.v155DateLabel'):null;
 if(!b)return;
 if(label)label.textContent=value||'Select date';else b.textContent=value||'Select date'
}
window.v155SetDateButton=v155DateButtonSet;
function decorateDateV112(inp){
 if(!inp||inp.getAttribute('data-v112-date')==='1')return;
 inp.setAttribute('data-v112-date','1');inp.classList.add('customNativeDateV112');
 var b=document.createElement('button');b.type='button';b.className='customDateButton v155DateButton';
 b.innerHTML='<span class="v155CalendarLottie lottieIcon" data-lottie="lottie/calendar-v155.json" aria-hidden="true"></span><span class="v155DateLabel"></span>';
 inp.parentNode.insertBefore(b,inp.nextSibling);inp._v112CalBtn=b;v155DateButtonSet(inp,inp.value);
 if(window.initLottie)window.initLottie(b);
 b.onclick=function(){calInput=inp;var p=inp.value?inp.value.split('-'):null;calDate=p?new Date(+p[0],+p[1]-1,+p[2]):new Date();renderCalendarV112();ensureCalendarV112().classList.add('show')};
 inp.addEventListener('change',function(){v155DateButtonSet(inp,inp.value)})
}
function decorateDatesV112"""
d=d[:m.start()]+new_func+d[m.end():]
d=d.replace("if(calInput._v112CalBtn)calInput._v112CalBtn.textContent=calInput.value","if(window.v155SetDateButton)window.v155SetDateButton(calInput,calInput.value)",1)
v112.write_text(d,encoding='utf-8')

# Existing edit-popup date assignment must not replace the custom date button contents.
s=s.replace("if(E('editPopupDate')._v112CalBtn)E('editPopupDate')._v112CalBtn.textContent=x.date","if(window.v155SetDateButton)window.v155SetDateButton(E('editPopupDate'),x.date)",1)
app.write_text(s,encoding='utf-8')

shutil.copy('ci/v155-icons.css',assets/'v155-icons.css')
print('v15.5 icon refresh patch applied')
