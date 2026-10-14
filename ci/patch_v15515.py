from pathlib import Path
import re,sys,json,shutil,base64
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
def rep(s,a,b):
 if a not in s:raise SystemExit('Missing v15515 anchor: '+a[:90])
 return s.replace(a,b,1)
h=(p/'index.html').read_text()
h,n=re.subn(r'<div id="v154BootScreen".*?</div>\s*<div id="authGate"', '<div id="authGate"',h,count=1,flags=re.S)
if n!=1:raise SystemExit('Startup overlay missing')
# New settings use static icons and no startup animation.
rows=''
for key,title,sub,icon in [('language','Language','English or Hindi','文'),('policy','Privacy Policy','How your information is used','⌁'),('help','Help &amp; Support','FAQs and chat with support','?')]:
 rows+='<button class="settingsMenuRow" data-setting="'+key+'"><span class="menuLottie" aria-hidden="true">'+icon+'</span><span><b>'+title+'</b><small>'+sub+'</small></span><i>›</i></button>'
h=rep(h,'<div class="settingsMenu">','<div class="settingsMenu">'+rows)
h=rep(h,'  </main>',Path('ci/v15515-pages.html').read_text()+'\n  </main>')
h=rep(h,'</head>','<link rel="stylesheet" href="v15515-ui.css">\n</head>')
h=rep(h,'<script src="user-storage.js"></script>','<script src="user-storage.js"></script>\n<script src="v15515-i18n.js"></script>')
h=rep(h,'<script src="xlsx.full.min.js"></script>','')
h=rep(h,'<script src="exceljs.min.js"></script>','<script src="v15515-lazy-vendors.js" data-excel-vendor="exceljs.min.js"></script>')
h=rep(h,'</body>','<script src="v15515-support.js"></script>\n</body>')
h=rep(h,'<div class="authDivider">','<button type="button" class="authLink" id="loginPrivacyPolicy">Privacy Policy</button><div class="authDivider">')
(p/'index.html').write_text(h)
s=(p/'app.js').read_text()
# Auth is already hydrated synchronously before scoped storage is created.
start=re.search(r'function startUserScopedApp\(\)\{.*?\n\}\nif\(document.readyState',s,re.S)
if not start:raise SystemExit('Scoped startup missing')
s=s[:start.start()]+'''function startUserScopedApp(){
 init();
 if(window.Android&&Android.authState){try{Android.authState()}catch(e){}}
}
if(document.readyState'''+s[start.end():]
s=rep(s,'buildLeaveSetup();bind();resetForm();renderDocuments();renderAll();','bind();resetForm();renderAll();')
prewarm=re.search(r'var prewarm=function\(\)\{.*?setInterval\(tick,1000\)',s,re.S)
if not prewarm:raise SystemExit('Prewarm anchor missing')
s=s[:prewarm.start()]+'setInterval(tick,1000)'+s[prewarm.end():]
s=rep(s,"renderLeaves();renderSalary();renderTheme()}","if(activeScreen()==='leaves')renderLeaves();if(activeScreen()==='setting-salary')renderSalary();renderTheme()}")
# Document migrations remain protected, but do not block Home.
s=rep(s,'function renderDocuments(){dbOpen(','''var documentsStarted=false;
function renderDocuments(){
 if(!documentsStarted&&window.attendanceDocumentsReady){documentsStarted=true;E('documentList').textContent='Preparing documents…';window.attendanceDocumentsReady.then(renderDocuments);return}
 dbOpen(''')
# Existing native toast uses translated UI copy, not translated stored record values.
s=s.replace('Android.toast(m)','Android.toast(window.AttendanceI18n?AttendanceI18n.t(m):m)')
(p/'app.js').write_text(s)
d=(p/'document-crypto.js').read_text()
d=rep(d,'Promise.resolve(window.attendanceStorageReady).then(migrateAll)','Promise.resolve(window.attendanceStorageReady).then(function(){return new Promise(function(resolve){setTimeout(resolve,250)})}).then(migrateAll)')
(p/'document-crypto.js').write_text(d)
v=(p/'v154-startup.js') if (p/'v154-startup.js').exists() else p/'v152-fixes.js'
s=v.read_text();s=s.replace('2200','250');v.write_text(s)
# No hidden Leaves work on startup.
v=p/'v15512-leaves.js';s=v.read_text();s=rep(s,"A().showScreen('setting-leaves')};window.renderFriendlyLeaves()","A().showScreen('setting-leaves')};if(E('screen-leaves').classList.contains('active'))window.renderFriendlyLeaves()");v.write_text(s)
v=p/'v15-features.js';s=v.read_text();s=rep(s,"monthNow();attendanceRenderKey='';renderAttendance()}","monthNow();attendanceRenderKey='';if(E('screen-attendance').classList.contains('active'))renderAttendance()}");v.write_text(s)
v=p/'v112-fixes.js';s=v.read_text();s=rep(s,"if(!window.ExcelJS){notice('Excel export','Excel styling engine is not available.');return}","if(!window.ExcelJS){notice('Excel export','Loading Excel tools…');window.loadAttendanceExcel().then(function(){exportExcelSelection(selection)}).catch(function(){notice('Excel export','Excel engine could not load. Please try again.')});return}");v.write_text(s)
for name in ['v15515-ui.css','v15515-support.js','v15515-lazy-vendors.js']:shutil.copy(Path('ci')/name,p/name)
i18n=Path('ci/v15515-i18n.js').read_text().replace('__HINDI_DICTIONARY__',json.dumps(json.loads(Path('ci/v15515-hi.json').read_text()),ensure_ascii=False))
(p/'v15515-i18n.js').write_text(i18n)
(p/'v15515-hindi.woff2').write_bytes(base64.b64decode(Path('ci/v15515-hindi-font.woff2.b64').read_text()))
print('v15.5.15 faster startup, English/Hindi and policy/help pages prepared')
