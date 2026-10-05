from pathlib import Path
import re, sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
p=assets/'app.js'
s=p.read_text(encoding='utf-8')

old_show="""function showScreen(name,push){
 var screens=document.getElementsByClassName('screen'),navs=document.getElementsByClassName('navBtn'),i,el=E('screen-'+name);
 if(!el)return;
 for(i=0;i<screens.length;i++)screens[i].classList.remove('active');
 for(i=0;i<navs.length;i++)navs[i].classList.remove('active');
 el.classList.add('active');
 for(i=0;i<navs.length;i++)if(navs[i].getAttribute('data-screen')===name)navs[i].classList.add('active');
 if(push!==false){if(screenHistory[screenHistory.length-1]!==name)screenHistory.push(name)}
 window.scrollTo(0,0);renderAll()
}
"""
new_show="""function renderScreen(name){
 if(name==='home'){tick();renderHome();return}
 if(name==='attendance'){renderAttendance();return}
 if(name==='leaves'){renderLeaves();return}
 if(name==='setting-profile'){renderProfile();return}
 if(name==='setting-work'){loadSettings();return}
 if(name==='setting-salary'){renderSalary();return}
 if(name==='setting-leaves'){buildLeaveSetup();return}
 if(name==='setting-documents'){renderDocuments();return}
 if(name==='setting-appearance'){renderTheme();return}
 if(name==='settings'){renderProfile();return}
}
function showScreen(name,push){
 var screens=document.getElementsByClassName('screen'),navs=document.getElementsByClassName('navBtn'),i,el=E('screen-'+name);
 if(!el)return;
 for(i=0;i<screens.length;i++)screens[i].classList.remove('active');
 for(i=0;i<navs.length;i++)navs[i].classList.remove('active');
 el.classList.add('active');
 for(i=0;i<navs.length;i++)if(navs[i].getAttribute('data-screen')===name)navs[i].classList.add('active');
 if(push!==false){if(screenHistory[screenHistory.length-1]!==name)screenHistory.push(name)}
 window.scrollTo(0,0);
 var paint=function(){if(activeScreen()===name)renderScreen(name)};
 if(window.requestAnimationFrame)window.requestAnimationFrame(paint);else paint()
}
"""
if old_show not in s: raise SystemExit('showScreen performance anchor missing')
s=s.replace(old_show,new_show,1)

old_tick="function tick(){var d=new Date(),s=setGet(),h=d.getHours(),m=d.getMinutes(),disp,p;"
new_tick="function tick(){if(!E('screen-home').classList.contains('active'))return;var d=new Date(),s=setGet(),h=d.getHours(),m=d.getMinutes(),disp,p;"
if old_tick not in s: raise SystemExit('tick anchor missing')
s=s.replace(old_tick,new_tick,1)

profile_pat=re.compile(r"function renderProfile\(\)\{.*?\}\nfunction renderTheme",re.S)
m=profile_pat.search(s)
if not m: raise SystemExit('renderProfile block missing')
profile_new="""function renderProfile(){
 var p=profileGet(),src=p.photo||'profile-placeholder.svg',a=E('topAvatar'),b=E('profilePreview');
 if(a.getAttribute('src')!==src)a.setAttribute('src',src);
 if(b.getAttribute('src')!==src)b.setAttribute('src',src);
 E('topName').textContent=p.name||'My Profile';
 E('topProfileMeta').textContent=(p.jobTitle?(p.jobTitle+(p.company?' • '+p.company:'')):p.company);
 E('appTitleDisplay').textContent=String(p.appTitle||'My Attendance').toUpperCase();
 document.title=p.appTitle||'My Attendance';
 E('profileName').value=p.name||'';
 E('profileJob').value=p.jobTitle||'';
 E('profileCompany').value=p.company||'';
 E('profileAppTitle').value=p.appTitle||'My Attendance'
}
function renderTheme"""
s=s[:m.start()]+profile_new+s[m.end():]

old_filters="E('monthFilter').onchange=renderAll;E('statusFilter').onchange=renderAll;"
new_filters="E('monthFilter').onchange=renderAttendance;E('statusFilter').onchange=renderAttendance;"
if old_filters not in s: raise SystemExit('filter render anchor missing')
s=s.replace(old_filters,new_filters,1)

old_interval="renderDocuments();renderAll();initLottie(document);setInterval(tick,250)"
new_interval="renderDocuments();renderAll();initLottie(document);setInterval(tick,1000)"
if old_interval not in s: raise SystemExit('tick interval anchor missing')
s=s.replace(old_interval,new_interval,1)

p.write_text(s,encoding='utf-8')
print('v13.5 navigation performance patch applied')
