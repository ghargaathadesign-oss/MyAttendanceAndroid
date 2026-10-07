from pathlib import Path
import re, sys, shutil

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
index=assets/'index.html'
app=assets/'app.js'
v15=assets/'v15-features.js'
profile_ui=assets/'profile-ui.js'
lottie=assets/'lottie-runtime.js'

h=index.read_text(encoding='utf-8')
s=app.read_text(encoding='utf-8')
v=v15.read_text(encoding='utf-8')
pui=profile_ui.read_text(encoding='utf-8')
lr=lottie.read_text(encoding='utf-8')

# ---- v15.4 assets and boot cover ----
if 'v154-ui.css' not in h:
    h=h.replace('</head>','<link rel="stylesheet" href="v154-ui.css">\n</head>',1)
if 'v154-ui.js' not in h:
    h=h.replace('</body>','<script src="v154-ui.js"></script>\n</body>',1)
if 'id="v154BootScreen"' not in h:
    boot='''<div id="v154BootScreen" class="v154BootScreen" aria-live="polite">
  <div class="v154BootMark" aria-hidden="true">◷</div>
  <b>My Attendance</b>
  <small>Preparing your attendance…</small>
  <span class="v154BootDots" aria-hidden="true"><i></i><i></i><i></i></span>
</div>'''
    if '<body>' not in h: raise SystemExit('body anchor missing')
    h=h.replace('<body>','<body>\n'+boot,1)

# ---- Add Attendance: remove header back button ----
h,n=re.subn(r'(<section class="screen" id="screen-add">\s*<div class="sectionHeader">)\s*<button class="back" type="button" data-back="home">‹</button>',r'\1',h,count=1)
if n!=1: raise SystemExit('Add Attendance back button anchor missing')

# ---- Profile: add requested employee fields ----
company_anchor='<div class="label">Company / Department</div><div class="field"><input id="profileCompany" placeholder="e.g. Design Department"></div>'
profile_extra='''<div class="label">Company</div><div class="field"><input id="profileCompany" placeholder="e.g. Ghar Gaatha"></div>
        <div class="profileExtraGrid">
          <div><div class="label">Department</div><div class="field"><input id="profileDepartment" placeholder="e.g. Design"></div></div>
          <div><div class="label">Employee ID</div><div class="field"><input id="profileEmployeeId" placeholder="e.g. GG-001"></div></div>
          <div><div class="label">Date of Birth</div><div class="field"><input type="date" id="profileDob"></div></div>
          <div><div class="label">Date of Joining</div><div class="field"><input type="date" id="profileJoining"></div></div>
        </div>'''
if 'id="profileDepartment"' not in h:
    if company_anchor not in h: raise SystemExit('profile company anchor missing')
    h=h.replace(company_anchor,profile_extra,1)
card_anchor='<span class="profileReferenceCompany" id="profileCardCompany"></span>'
if 'id="profileCardExtra"' not in h:
    if card_anchor not in h: raise SystemExit('profile card company anchor missing')
    h=h.replace(card_anchor,card_anchor+'\n        <span class="profileReferenceExtra" id="profileCardExtra"></span>',1)

index.write_text(h,encoding='utf-8')

# ---- Profile model/render/save ----
old_profile="var p={name:'My Profile',jobTitle:'',company:'',appTitle:'My Attendance',photo:''},o"
new_profile="var p={name:'My Profile',jobTitle:'',company:'',department:'',employeeId:'',dob:'',dateOfJoining:'',appTitle:'My Attendance',photo:''},o"
if old_profile not in s: raise SystemExit('profileGet defaults anchor missing')
s=s.replace(old_profile,new_profile,1)

pat=re.compile(r"function renderProfile\(\)\{.*?\n\}\nfunction renderTheme",re.S)
m=pat.search(s)
if not m: raise SystemExit('renderProfile block missing')
render_profile=r"""function renderProfile(){
 var p=profileGet(),src=p.photo||'profile-placeholder.svg',a=E('topAvatar'),b=E('profilePreview');
 if(a&&a.getAttribute('src')!==src)a.setAttribute('src',src);
 if(b&&b.getAttribute('src')!==src)b.setAttribute('src',src);
 E('topName').textContent=p.name||'My Profile';
 E('topProfileMeta').textContent=(p.jobTitle?(p.jobTitle+(p.department?' • '+p.department:(p.company?' • '+p.company:''))):(p.department||p.company||''));
 E('appTitleDisplay').textContent=String(p.appTitle||'My Attendance').toUpperCase();
 document.title=p.appTitle||'My Attendance';
 E('profileName').value=p.name||'';
 E('profileJob').value=p.jobTitle||'';
 E('profileCompany').value=p.company||'';
 if(E('profileDepartment'))E('profileDepartment').value=p.department||'';
 if(E('profileEmployeeId'))E('profileEmployeeId').value=p.employeeId||'';
 if(E('profileDob'))E('profileDob').value=p.dob||'';
 if(E('profileJoining'))E('profileJoining').value=p.dateOfJoining||'';
 E('profileAppTitle').value=p.appTitle||'My Attendance'
}
function renderTheme"""
s=s[:m.start()]+render_profile+s[m.end():]

old_save="function saveProfile(){var p=profileGet();p.name=E('profileName').value.trim()||'My Profile';p.jobTitle=E('profileJob').value.trim();p.company=E('profileCompany').value.trim();p.appTitle=E('profileAppTitle').value.trim()||'My Attendance';if(profilePut(p)){toast('Profile saved');renderProfile()}}"
new_save="function saveProfile(){var p=profileGet();p.name=E('profileName').value.trim()||'My Profile';p.jobTitle=E('profileJob').value.trim();p.company=E('profileCompany').value.trim();p.department=E('profileDepartment')?E('profileDepartment').value.trim():'';p.employeeId=E('profileEmployeeId')?E('profileEmployeeId').value.trim():'';p.dob=E('profileDob')?E('profileDob').value:'';p.dateOfJoining=E('profileJoining')?E('profileJoining').value:'';p.appTitle=E('profileAppTitle').value.trim()||'My Attendance';if(profilePut(p)){toast('Profile saved');renderProfile()}}"
if old_save not in s: raise SystemExit('saveProfile anchor missing')
s=s.replace(old_save,new_save,1)

# ---- Edit/delete flow ----
old_delete="function deleteRecord(id){var a=dataGet(),b=[],i;if(!confirm('Delete this attendance record?'))return;for(i=0;i<a.length;i++)if(a[i].id!==id)b.push(a[i]);if(dataPut(b)){toast('Attendance deleted');renderAll()}}"
new_delete="function deleteRecord(id){var a=dataGet(),b=[],i;if(!confirm('Delete this attendance record?'))return;for(i=0;i<a.length;i++)if(a[i].id!==id)b.push(a[i]);if(dataPut(b)){try{closeEdit()}catch(e){}toast('Attendance deleted');renderAll();if(window.AttendanceV15&&AttendanceV15.onDataChanged)AttendanceV15.onDataChanged();if(window.AttendanceV15&&AttendanceV15.renderScreen)AttendanceV15.renderScreen('attendance')}}"
if old_delete not in s: raise SystemExit('deleteRecord anchor missing')
s=s.replace(old_delete,new_delete,1)

old_back="document.querySelector('#screen-add .back').onclick=function(){showScreen('home',false)};"
if old_back not in s: raise SystemExit('Add Attendance back binding anchor missing')
s=s.replace(old_back,"var addBack=document.querySelector('#screen-add .back');if(addBack)addBack.onclick=function(){showScreen('home',false)};",1)

# ---- Startup: wait for scoped data, then reveal a fully rendered Home ----
old_init="renderDocuments();renderAll();initLottie(document);setTimeout(function(){if(activeScreen()!=='attendance'){if(window.AttendanceV14&&AttendanceV14.renderScreen)AttendanceV14.renderScreen('attendance');else renderAttendance()}},350);setInterval(tick,1000)"
new_init="""renderDocuments();renderAll();if(window.initLottie)window.initLottie(document);setTimeout(function(){try{if(window.v154AppReady)window.v154AppReady();else{var boot=E('v154BootScreen');if(boot)boot.classList.add('hide')}}catch(e){}},100);var prewarm=function(){if(activeScreen()!=='attendance'){if(window.AttendanceV14&&AttendanceV14.renderScreen)AttendanceV14.renderScreen('attendance');else renderAttendance()}};if(window.requestIdleCallback)requestIdleCallback(prewarm,{timeout:1600});else setTimeout(prewarm,1200);setInterval(tick,1000)"""
if old_init not in s: raise SystemExit('init startup anchor missing')
s=s.replace(old_init,new_init,1)

start_pat=re.compile(r"function startUserScopedApp\(\)\{.*?\n\}\nif\(document\.readyState",re.S)
m=start_pat.search(s)
if not m: raise SystemExit('startUserScopedApp block missing')
new_start=r"""function startUserScopedApp(){
 var started=false,go=function(){if(started)return;started=true;init()},ready=window.attendanceDocumentsReady||window.attendanceStorageReady,authReady=window.attendanceAuthReadyPromise;
 if(window.Android&&Android.authState){try{Android.authState()}catch(e){}}
 if(window.Promise){
   var storageReady=ready&&typeof ready.then==='function'?ready:Promise.resolve();
   var userReady=authReady&&typeof authReady.then==='function'?authReady:Promise.resolve();
   Promise.all([storageReady,userReady]).then(go).catch(go);
   setTimeout(function(){if(!started)go()},4500)
 }else go()
}
if(document.readyState"""
s=s[:m.start()]+new_start+s[m.end():]
app.write_text(s,encoding='utf-8')

# ---- Monthly Records: only a top-right edit icon; status sits lower ----
records_pat=re.compile(r"function renderRecords\(month\)\{.*?\nfunction renderAttendance",re.S)
m=records_pat.search(v)
if not m: raise SystemExit('v15 renderRecords block missing')
records=r"""function renderRecords(month){
 var a=filteredMonthRecords(month),s=settings(),box=E('records'),count=E('attendanceResultCount'),out='',i,x,w,b,parts;
 if(count)count.textContent=a.length+' record'+(a.length===1?'':'s');
 if(!box)return;
 if(!a.length){box.innerHTML='<div class="v15Empty"><span>◎</span><b>No matching records</b><small>Tap any day in the calendar to add attendance.</small></div>';return}
 for(i=0;i<a.length;i++){
  x=a[i];w=worked(x);b=balance(x,s);parts=String(x.date||'').split('-');
  out+='<article class="v15Record v154Record" data-id="'+esc(x.id)+'"><button type="button" class="v154RecordEdit" data-id="'+esc(x.id)+'" aria-label="Edit attendance for '+esc(x.date)+'" title="Edit attendance"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 16.5V20h3.5L18.1 9.4l-3.5-3.5L4 16.5Zm16.7-9.7a1 1 0 0 0 0-1.4l-2.1-2.1a1 1 0 0 0-1.4 0l-1.6 1.6 3.5 3.5 1.6-1.6Z"/></svg></button><div class="v154RecordInner"><span class="v15RecordDate"><b>'+esc(parts[2]||'')+'</b><small>'+(A&&A.dayShort?esc(A.dayShort(x.date)):'')+'</small></span><span class="v154RecordBody"><span class="v154RecordTimes">'+formatTime(x.checkIn,s.fmt)+' → '+formatTime(x.checkOut,s.fmt)+' <i>•</i> '+esc(duration(w).replace(/^\+/,''))+'</span><span class="v154RecordStatus"><em class="v15StatusDot '+statusClass(x.status)+'"></em><b>'+esc(x.status)+'</b></span><span class="v154RecordMeta">'+(b>=0?'OT '+esc(duration(b)):'Short '+esc(duration(-b).replace(/^\+/,'')))+(x.reason?' • '+esc(x.reason):'')+(x.notes?' • '+esc(x.notes):'')+'</span></span></div></article>'
 }
 box.innerHTML=out
}
function renderAttendance"""
v=v[:m.start()]+records+v[m.end():]

old_open="function openDay(date){var a=data(),i,x=null;for(i=0;i<a.length;i++)if(a[i].date===date){x=a[i];break}if(x&&A&&A.openEdit){A.openEdit(x.id);return}if(A&&A.resetForm)A.resetForm();var d=E('dateInput');if(d)d.value=date;if(E('formTitle'))E('formTitle').textContent='Add Attendance';if(A&&A.showScreen)A.showScreen('add')}"
new_open="function openDay(date){var a=data(),i,x=null;for(i=0;i<a.length;i++)if(a[i].date===date){x=a[i];break}if(x&&A&&A.openEdit){A.openEdit(x.id);return}if(A&&A.resetForm)A.resetForm();var d=E('dateInput');if(d){d.value=date;try{d.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}if(d._calBtn)d._calBtn.textContent=date;if(d._v112CalBtn)d._v112CalBtn.textContent=date}if(E('formTitle'))E('formTitle').textContent='Add Attendance';if(A&&A.showScreen)A.showScreen('add')}"
if old_open not in v: raise SystemExit('v15 openDay anchor missing')
v=v.replace(old_open,new_open,1)

old_records_bind="if(E('records'))E('records').onclick=function(ev){var b=ev.target.closest('.v15RecordOpen[data-id]');if(b&&A&&A.openEdit)A.openEdit(b.getAttribute('data-id'))};"
new_records_bind="if(E('records'))E('records').onclick=function(ev){var b=ev.target.closest('.v154RecordEdit[data-id]');if(b&&A&&A.openEdit)A.openEdit(b.getAttribute('data-id'))};"
if old_records_bind not in v: raise SystemExit('v15 records binding anchor missing')
v=v.replace(old_records_bind,new_records_bind,1)
v15.write_text(v,encoding='utf-8')

# ---- Profile card helper understands new fields ----
old_pget="function getProfile(){var p={name:'My Profile',jobTitle:'',company:'',appTitle:'My Attendance',photo:''},o,k;try{o=JSON.parse(localStorage.getItem(KEY)||'{}')||{};for(k in p)if(typeof o[k]!=='undefined')p[k]=o[k]}catch(e){}return p}"
new_pget="function getProfile(){var p={name:'My Profile',jobTitle:'',company:'',department:'',employeeId:'',dob:'',dateOfJoining:'',appTitle:'My Attendance',photo:''},o,k;try{o=JSON.parse(localStorage.getItem(KEY)||'{}')||{};for(k in p)if(typeof o[k]!=='undefined')p[k]=o[k]}catch(e){}return p}"
if old_pget not in pui: raise SystemExit('profile-ui getProfile anchor missing')
pui=pui.replace(old_pget,new_pget,1)
old_sync="function sync(){var p=getProfile(),src=p.photo||'profile-placeholder.svg',job=p.jobTitle||'Job title not set',company=p.company||'Company not set';if(E('profilePreview'))E('profilePreview').src=src;if(E('profileCardName'))E('profileCardName').textContent=p.name||'My Profile';if(E('profileCardJob'))E('profileCardJob').textContent=job;if(E('profileCardCompany'))E('profileCardCompany').textContent=company;if(E('profileOptionName'))E('profileOptionName').textContent=p.name||'My Profile';if(E('profileOptionJob'))E('profileOptionJob').textContent=(p.jobTitle||'Job title not set')+(p.company?' • '+p.company:'');if(E('profileOptionApp'))E('profileOptionApp').textContent=p.appTitle||'My Attendance'}"
new_sync="function sync(){var p=getProfile(),src=p.photo||'profile-placeholder.svg',job=p.jobTitle||'Job title not set',company=p.company||'Company not set',work=[p.department,p.employeeId?('ID '+p.employeeId):''].filter(Boolean).join(' • ');if(E('profilePreview'))E('profilePreview').src=src;if(E('profileCardName'))E('profileCardName').textContent=p.name||'My Profile';if(E('profileCardJob'))E('profileCardJob').textContent=job;if(E('profileCardCompany'))E('profileCardCompany').textContent=company;if(E('profileCardExtra'))E('profileCardExtra').textContent=work;if(E('profileOptionName'))E('profileOptionName').textContent=p.name||'My Profile';if(E('profileOptionJob'))E('profileOptionJob').textContent=(p.jobTitle||'Job title not set')+(p.department?' • '+p.department:(p.company?' • '+p.company:''));if(E('profileOptionApp'))E('profileOptionApp').textContent=p.appTitle||'My Attendance'}"
if old_sync in pui:
    pui=pui.replace(old_sync,new_sync,1)
profile_ui.write_text(pui,encoding='utf-8')

# ---- Lazy Lottie: initialize only visible screen animations at startup ----
old_init_lottie="""  window.initLottie=function(root){
    root=root||document;
    var list=[],i;
    if(root.nodeType===1&&root.getAttribute&&root.getAttribute('data-lottie'))list.push(root);
    if(root.querySelectorAll){var q=root.querySelectorAll('[data-lottie]');for(i=0;i<q.length;i++)list.push(q[i]);}
    for(i=0;i<list.length;i++)initOne(list[i]);
  };"""
new_init_lottie="""  function lottieVisible(el){var screen=el&&el.closest?el.closest('.screen'):null;return !screen||screen.classList.contains('active');}
  window.initLottie=function(root){
    root=root||document;
    var list=[],i;
    if(root.nodeType===1&&root.getAttribute&&root.getAttribute('data-lottie'))list.push(root);
    if(root.querySelectorAll){var q=root.querySelectorAll('[data-lottie]');for(i=0;i<q.length;i++)list.push(q[i]);}
    for(i=0;i<list.length;i++)if(lottieVisible(list[i]))initOne(list[i]);
  };"""
if old_init_lottie not in lr: raise SystemExit('lottie init block missing')
lr=lr.replace(old_init_lottie,new_init_lottie,1)
old_lottie_start="  function start(){observeTheme();window.initLottie(document);new MutationObserver(function(ms){var i,j,n;for(i=0;i<ms.length;i++)for(j=0;j<ms[i].addedNodes.length;j++){n=ms[i].addedNodes[j];if(n&&n.nodeType===1)window.initLottie(n);}}).observe(document.body,{childList:true,subtree:true});}"
new_lottie_start="  function start(){observeTheme();window.initLottie(document);new MutationObserver(function(ms){var i,j,n,t;for(i=0;i<ms.length;i++){if(ms[i].type==='attributes'){t=ms[i].target;if(t&&t.classList&&t.classList.contains('screen')&&t.classList.contains('active'))window.initLottie(t);continue}for(j=0;j<ms[i].addedNodes.length;j++){n=ms[i].addedNodes[j];if(n&&n.nodeType===1)window.initLottie(n)}}}).observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class']});}"
if old_lottie_start not in lr: raise SystemExit('lottie start block missing')
lr=lr.replace(old_lottie_start,new_lottie_start,1)
lottie.write_text(lr,encoding='utf-8')

# Replace v15.2 startup retry storm with the synchronized v15.4 version.
shutil.copy('ci/v154-startup.js',assets/'v152-fixes.js')
shutil.copy('ci/v154-ui.css',assets/'v154-ui.css')
shutil.copy('ci/v154-ui.js',assets/'v154-ui.js')

print('v15.4 attendance, profile and startup batch patch applied')
