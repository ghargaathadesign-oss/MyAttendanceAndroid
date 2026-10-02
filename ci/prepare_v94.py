from pathlib import Path
import sys, re, json, copy

assets = Path(sys.argv[1] if len(sys.argv) > 1 else "app/src/main/assets")
src = assets / "lottie"
dark = assets / "lottie-dark"
white = assets / "lottie-white"
dark.mkdir(parents=True, exist_ok=True)
white.mkdir(parents=True, exist_ok=True)

aliases = {"setting.json": "settings.json", "worktime.json": "work.json"}
for original, alias in aliases.items():
    p = src / original
    if p.exists():
        (src / alias).write_bytes(p.read_bytes())

for name in ["punch.json","home.json","attendance.json","leaves.json","documents.json",
             "salary.json","backup.json","profile.json","settings.json","work.json"]:
    p = src / name
    if p.exists():
        (assets / name).write_bytes(p.read_bytes())

BLACK_LIMIT = 0.18

def nums(v):
    return isinstance(v, list) and all(isinstance(x, (int, float)) for x in v)

def should_white(rgb, mode):
    return mode == "white" or (mode == "dark" and max(float(x) for x in rgb) <= BLACK_LIMIT)

def recolor_color_value(v, mode):
    if isinstance(v, list):
        if len(v) >= 3 and nums(v[:3]) and all(0 <= float(x) <= 1.0001 for x in v[:3]):
            out = list(v)
            if should_white(out[:3], mode):
                out[0] = out[1] = out[2] = 1
            return out
        return [recolor_color_value(x, mode) for x in v]
    if isinstance(v, dict):
        return {k: recolor_color_value(val, mode) for k, val in v.items()}
    return v

def recolor_gradient_payload(v, points, mode):
    if isinstance(v, list):
        if points and nums(v) and len(v) >= points * 4:
            out = list(v)
            for i in range(points):
                b = i * 4
                rgb = out[b+1:b+4]
                if len(rgb) == 3 and all(0 <= float(x) <= 1.0001 for x in rgb) and should_white(rgb, mode):
                    out[b+1] = out[b+2] = out[b+3] = 1
            return out
        return [recolor_gradient_payload(x, points, mode) for x in v]
    if isinstance(v, dict):
        return {k: recolor_gradient_payload(val, points, mode) for k, val in v.items()}
    return v

def recolor_hex(v, mode):
    if not isinstance(v, str) or not v.startswith("#"):
        return v
    h = v[1:]
    if len(h) in (3, 4):
        h = "".join(ch * 2 for ch in h[:3])
    elif len(h) >= 6:
        h = h[:6]
    else:
        return v
    try:
        rgb = [int(h[i:i+2], 16) for i in (0, 2, 4)]
    except Exception:
        return v
    if mode == "white" or (mode == "dark" and max(rgb) <= 46):
        return "#FFFFFF"
    return v

def transform(obj, mode):
    if isinstance(obj, list):
        return [transform(x, mode) for x in obj]
    if not isinstance(obj, dict):
        return obj
    if obj.get("ty") == 2 and isinstance(obj.get("v"), dict) and "k" in obj["v"]:
        obj = copy.deepcopy(obj)
        obj["v"]["k"] = recolor_color_value(obj["v"]["k"], mode)

    out = {}
    for k, v in obj.items():
        if k == "c" and isinstance(v, dict) and "k" in v:
            vv = copy.deepcopy(v)
            vv["k"] = recolor_color_value(vv["k"], mode)
            out[k] = transform(vv, mode)
        elif k == "g" and isinstance(v, dict):
            gg = copy.deepcopy(v)
            points = int(gg.get("p") or 0)
            kval = gg.get("k")
            if isinstance(kval, dict) and "k" in kval:
                kval["k"] = recolor_gradient_payload(kval["k"], points, mode)
            else:
                gg["k"] = recolor_gradient_payload(kval, points, mode)
            out[k] = transform(gg, mode)
        elif k in ("fc", "sc"):
            out[k] = recolor_hex(v, mode) if isinstance(v, str) else recolor_color_value(v, mode)
        else:
            out[k] = transform(v, mode)
    return out

for p in src.glob("*.json"):
    data = json.loads(p.read_text(encoding="utf-8"))
    (dark / p.name).write_text(json.dumps(transform(data, "dark"), separators=(",", ":")), encoding="utf-8")
    (white / p.name).write_text(json.dumps(transform(data, "white"), separators=(",", ":")), encoding="utf-8")

app_js = assets / "app.js"
s = app_js.read_text(encoding="utf-8")
s = s.replace("var repunch={type:'',until:0},screenHistory=['home'];", "var screenHistory=['home'];")
pat = r"function startRepunch\(type\)\{.*?\nfunction salaryCalc\(month\)\{"
replacement = r'''function punch(){
 var a=dataGet(),x=null,i,t=nowTime24();
 for(i=0;i<a.length;i++)if(a[i].date===nowDate()){x=a[i];break}
 if(!x){x={id:idNew(),date:nowDate(),status:'Present',checkIn:t,checkOut:'',reason:'',notes:''};a.push(x);dataPut(a);toast('Clocked in at '+timeText(t))}
 else if(!x.checkIn){x.checkIn=t;x.status='Present';dataPut(a);toast('Clocked in at '+timeText(t))}
 else if(!x.checkOut){x.checkOut=t;dataPut(a);toast('Clocked out at '+timeText(t))}
 else{if(!confirm('Today is already completed. Start again and replace current times?'))return;x.checkIn=t;x.checkOut='';x.status='Present';dataPut(a);toast('Clock in restarted')}
 renderAll()
}
function renderPunchButton(){
 var x=currentRecord(),btn=E('punchBtn'),label=E('punchLabel'),status=E('todayStatus');
 btn.classList.remove('out','repunch');
 if(x&&x.checkIn&&!x.checkOut){btn.classList.add('out');label.textContent='CLOCK OUT';status.textContent='Checked in at '+timeText(x.checkIn)}
 else{label.textContent='CLOCK IN';status.textContent=x&&x.checkOut?'Completed today • '+durationText(workMinutes(x.checkIn,x.checkOut)):'Tap the button to mark your time'}
}
function salaryCalc(month){'''
s2, n = re.subn(pat, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit("Could not remove repunch block")
if "RE-PUNCH" in s2 or "startRepunch" in s2:
    raise SystemExit("Repunch code still present")
app_js.write_text(s2, encoding="utf-8")

index = assets / "index.html"
html = index.read_text(encoding="utf-8")
new_profile = r'''<section class="screen settingScreen" id="screen-setting-profile">
      <div class="sectionHeader"><button class="back settingBack" type="button">‹</button><span class="pageLottie lottieIcon" data-lottie="profile.json"></span><h1>Profile</h1></div>
      <div class="profileReferenceCard">
        <button class="profileCardDelete" id="removePhoto" type="button" aria-label="Delete profile photo" title="Delete profile photo">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 3h6l1 2h4v2H4V5h4l1-2Zm-2 6h10l-.7 11H7.7L7 9Zm3 2v7h2v-7h-2Zm4 0v7h2v-7h-2Z"/></svg>
        </button>
        <div class="profileReferenceAvatar">
          <div class="profilePreview"><img id="profilePreview" src="profile-placeholder.svg" alt="Profile"></div>
          <label class="profileCameraButton" aria-label="Change profile photo" title="Change profile photo">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 4.5 10.4 3h3.2L15 4.5h3A2.5 2.5 0 0 1 20.5 7v10A2.5 2.5 0 0 1 18 19.5H6A2.5 2.5 0 0 1 3.5 17V7A2.5 2.5 0 0 1 6 4.5h3Zm3 3A4.5 4.5 0 1 0 12 16.5 4.5 4.5 0 0 0 12 7.5Zm0 2A2.5 2.5 0 1 1 12 14.5 2.5 2.5 0 0 1 12 9.5Z"/></svg>
            <input type="file" id="profileFile" accept="image/*" hidden>
          </label>
        </div>
        <b class="profileReferenceName" id="profileCardName">My Profile</b>
        <span class="profileReferenceJob" id="profileCardJob"></span>
        <span class="profileReferenceCompany" id="profileCardCompany"></span>
        <button class="profileReferenceEdit" id="openProfileEditor" type="button"><span>✎</span> Edit Profile</button>
      </div>
      <div class="profileOptionList">
        <button class="profileOptionRow" type="button" data-profile-edit><span class="profileOptionIcon">◎</span><span><b>Personal Details</b><small id="profileOptionName">My Profile</small></span><i>›</i></button>
        <button class="profileOptionRow" type="button" data-profile-edit><span class="profileOptionIcon">▣</span><span><b>Job Details</b><small id="profileOptionJob">Not set</small></span><i>›</i></button>
        <button class="profileOptionRow" type="button" data-profile-edit><span class="profileOptionIcon">◇</span><span><b>App Name</b><small id="profileOptionApp">My Attendance</small></span><i>›</i></button>
      </div>
      <div class="modal" id="profileEditorModal">
        <div class="sheet profileEditorSheet">
          <div class="sheetHead"><b>Edit Profile</b><button id="profileEditorClose" type="button">×</button></div>
          <div class="label">Display Name</div><div class="field"><input id="profileName" placeholder="Your name"></div>
          <div class="label">Job Title</div><div class="field"><input id="profileJob" placeholder="e.g. Graphic Designer"></div>
          <div class="label">Company / Department</div><div class="field"><input id="profileCompany" placeholder="e.g. Design Department"></div>
          <div class="label">App Title</div><div class="field"><input id="profileAppTitle" placeholder="My Attendance"></div>
          <div class="actions"><button class="btn primary" id="saveProfile" type="button">Save Profile</button><button class="btn ghost" id="profileEditorCancel" type="button">Cancel</button></div>
        </div>
      </div>
    </section>'''
profile_pat = r'<section class="screen settingScreen" id="screen-setting-profile">.*?</section>\s*(?=<section class="screen settingScreen" id="screen-setting-work">)'
html2, n = re.subn(profile_pat, new_profile + "\n\n    ", html, count=1, flags=re.S)
if n != 1:
    raise SystemExit("Profile section replacement failed")
needle = '<script src="app.js"></script>'
if needle not in html2:
    raise SystemExit("app.js script tag not found")
html2 = html2.replace(needle, '<script src="lottie-runtime.js"></script>\n<script src="app.js"></script>\n<script src="profile-ui.js"></script>')
index.write_text(html2, encoding="utf-8")

profile_ui = r'''(function(){
  'use strict';
  var KEY='attendance_profile_v81';
  function E(id){return document.getElementById(id)}
  function getProfile(){var p={name:'My Profile',jobTitle:'',company:'',appTitle:'My Attendance',photo:''},o,k;try{o=JSON.parse(localStorage.getItem(KEY)||'{}')||{};for(k in p)if(typeof o[k]!=='undefined')p[k]=o[k]}catch(e){}return p}
  function sync(){var p=getProfile(),src=p.photo||'profile-placeholder.svg',job=p.jobTitle||'Job title not set',company=p.company||'Company not set';if(E('profilePreview'))E('profilePreview').src=src;if(E('profileCardName'))E('profileCardName').textContent=p.name||'My Profile';if(E('profileCardJob'))E('profileCardJob').textContent=job;if(E('profileCardCompany'))E('profileCardCompany').textContent=company;if(E('profileOptionName'))E('profileOptionName').textContent=p.name||'My Profile';if(E('profileOptionJob'))E('profileOptionJob').textContent=(p.jobTitle||'Job title not set')+(p.company?' • '+p.company:'');if(E('profileOptionApp'))E('profileOptionApp').textContent=p.appTitle||'My Attendance'}
  function openEditor(){var m=E('profileEditorModal');if(m)m.classList.add('show')}
  function closeEditor(){var m=E('profileEditorModal');if(m)m.classList.remove('show')}
  function init(){var b=E('openProfileEditor'),c=E('profileEditorClose'),x=E('profileEditorCancel'),save=E('saveProfile'),del=E('removePhoto'),photoSave=E('photoSave'),rows=document.querySelectorAll('[data-profile-edit]'),i;if(b)b.addEventListener('click',openEditor);if(c)c.addEventListener('click',closeEditor);if(x)x.addEventListener('click',closeEditor);for(i=0;i<rows.length;i++)rows[i].addEventListener('click',openEditor);if(save)save.addEventListener('click',function(){setTimeout(function(){sync();closeEditor()},30)});if(del)del.addEventListener('click',function(){setTimeout(sync,30)});if(photoSave)photoSave.addEventListener('click',function(){setTimeout(sync,180)});var m=E('profileEditorModal');if(m)m.addEventListener('click',function(e){if(e.target===m)closeEditor()});sync()}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();'''
(assets / "profile-ui.js").write_text(profile_ui, encoding="utf-8")

css_append = r'''
.profileReferenceCard{position:relative;overflow:hidden;background:var(--surface);border:1px solid var(--line);border-radius:24px;padding:24px 18px 20px;text-align:center;box-shadow:var(--shadow)}
.profileReferenceCard:before{content:"";position:absolute;width:220px;height:120px;border-radius:50%;top:-82px;right:-52px;background:radial-gradient(circle,rgba(255,171,106,.28),rgba(255,171,106,0) 70%);pointer-events:none}
.profileReferenceAvatar{position:relative;width:124px;height:124px;margin:0 auto 13px}
.profileReferenceAvatar .profilePreview{width:124px;height:124px;border-radius:50%;overflow:hidden;border:4px solid var(--surface);box-shadow:0 10px 28px rgba(40,64,100,.16);background:#eaf1f8}
.profileReferenceAvatar .profilePreview img{width:100%;height:100%;display:block;object-fit:cover;border-radius:50%}
.profileCameraButton{position:absolute;right:1px;bottom:5px;width:38px;height:38px;border-radius:50%;background:#ff8a25;border:3px solid var(--surface);display:flex;align-items:center;justify-content:center;box-shadow:0 7px 18px rgba(255,138,37,.3);cursor:pointer}
.profileCameraButton svg{width:19px;height:19px;fill:#fff}
.profileCardDelete{position:absolute;right:14px;top:14px;width:38px;height:38px;border-radius:50%;border:1px solid #ffd8da;background:#fff4f4;color:#d95764;display:flex;align-items:center;justify-content:center;padding:0;z-index:2}
.profileCardDelete svg{width:18px;height:18px;fill:currentColor}
.profileReferenceName{display:block;font-size:17px;line-height:1.25;margin-top:2px}
.profileReferenceJob,.profileReferenceCompany{display:block;color:var(--muted);font-size:10px;line-height:1.5;margin-top:3px}
.profileReferenceEdit{margin:16px auto 0;border:0;border-radius:999px;min-height:42px;padding:0 20px;background:linear-gradient(135deg,#ff922f,#ff7d1a);color:#fff;font-weight:800;display:inline-flex;align-items:center;justify-content:center;gap:7px;box-shadow:0 9px 21px rgba(255,132,30,.24)}
.profileReferenceEdit span{font-size:17px}
.profileOptionList{margin-top:13px;background:var(--surface);border:1px solid var(--line);border-radius:18px;overflow:hidden;box-shadow:0 9px 25px rgba(48,67,101,.06)}
.profileOptionRow{width:100%;min-height:61px;border:0;border-bottom:1px solid var(--line);background:transparent;color:inherit;display:grid;grid-template-columns:38px 1fr 18px;align-items:center;gap:9px;text-align:left;padding:9px 13px}
.profileOptionRow:last-child{border-bottom:0}
.profileOptionIcon{width:34px;height:34px;border-radius:50%;border:1px solid var(--line);display:grid;place-items:center;color:#596473;background:var(--surface2);font-size:14px}
.profileOptionRow>span:nth-child(2) b{display:block;font-size:12px}
.profileOptionRow>span:nth-child(2) small{display:block;color:var(--muted);font-size:9px;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.profileOptionRow i{font-style:normal;color:var(--muted);font-size:23px}
.profileEditorSheet{padding-bottom:20px}
body.dark-mode .profileReferenceCard:before{background:radial-gradient(circle,rgba(255,145,55,.15),rgba(255,145,55,0) 70%)}
body.dark-mode .profileCardDelete{background:#351a20;border-color:#5b2833;color:#ff8c9a}
body.dark-mode .profileOptionIcon{color:#eef4fb}
'''
with (assets / "app.css").open("a", encoding="utf-8") as f:
    f.write(css_append)

print("v9.4 transformations complete")
