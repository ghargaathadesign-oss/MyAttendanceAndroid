from pathlib import Path
import sys, re

assets = Path(sys.argv[1] if len(sys.argv) > 1 else "app/src/main/assets")
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

      <div class="settingsCard profileInlineFields" id="profileFields">
        <div class="label">Display Name</div><div class="field"><input id="profileName" placeholder="Your name"></div>
        <div class="label">Job Title</div><div class="field"><input id="profileJob" placeholder="e.g. Graphic Designer"></div>
        <div class="label">Company / Department</div><div class="field"><input id="profileCompany" placeholder="e.g. Design Department"></div>
        <div class="label">App Title</div><div class="field"><input id="profileAppTitle" placeholder="My Attendance"></div>
        <button class="btn primary fullBtn" id="saveProfile" type="button">Save Profile</button>
      </div>
    </section>'''

pat = r'<section class="screen settingScreen" id="screen-setting-profile">.*?</section>\s*(?=<section class="screen settingScreen" id="screen-setting-work">)'
html2, n = re.subn(pat, new_profile + "\n\n    ", html, count=1, flags=re.S)
if n != 1:
    raise SystemExit("v9.5 profile section replacement failed")
index.write_text(html2, encoding="utf-8")

profile_ui = r'''(function(){
  'use strict';
  var KEY='attendance_profile_v81';
  function E(id){return document.getElementById(id)}
  function getProfile(){var p={name:'My Profile',jobTitle:'',company:'',appTitle:'My Attendance',photo:''},o,k;try{o=JSON.parse(localStorage.getItem(KEY)||'{}')||{};for(k in p)if(typeof o[k]!=='undefined')p[k]=o[k]}catch(e){}return p}
  function sync(){var p=getProfile(),src=p.photo||'profile-placeholder.svg';if(E('profilePreview'))E('profilePreview').src=src;if(E('profileCardName'))E('profileCardName').textContent=p.name||'My Profile';if(E('profileCardJob'))E('profileCardJob').textContent=p.jobTitle||'Job title not set';if(E('profileCardCompany'))E('profileCardCompany').textContent=p.company||'Company not set'}
  function focusFields(){var box=E('profileFields'),inp=E('profileName');if(box&&box.scrollIntoView)box.scrollIntoView({behavior:'smooth',block:'start'});setTimeout(function(){try{if(inp)inp.focus()}catch(e){}},250)}
  function init(){var edit=E('openProfileEditor'),save=E('saveProfile'),del=E('removePhoto'),photoSave=E('photoSave');if(edit)edit.addEventListener('click',focusFields);if(save)save.addEventListener('click',function(){setTimeout(sync,40)});if(del)del.addEventListener('click',function(){setTimeout(sync,40)});if(photoSave)photoSave.addEventListener('click',function(){setTimeout(sync,180)});sync()}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();'''
(assets / "profile-ui.js").write_text(profile_ui, encoding="utf-8")

css = assets / "app.css"
with css.open("a", encoding="utf-8") as f:
    f.write(r'''

/* v9.5 profile theme: match app blue, keep old inline text-box editor */
.profileReferenceCard:before{
  background:radial-gradient(circle,rgba(77,143,233,.24),rgba(77,143,233,0) 70%) !important;
}
.profileCameraButton{
  background:linear-gradient(135deg,#4d8fe9,#5578dc) !important;
  color:#fff !important;
}
.profileReferenceEdit{
  background:linear-gradient(135deg,#4d8fe9,#5578dc) !important;
  color:#fff !important;
  box-shadow:0 9px 22px rgba(77,127,218,.24) !important;
}
.profileInlineFields{
  margin-top:14px;
  text-align:left;
}
.profileInlineFields .fullBtn{
  display:flex;
  align-items:center;
  justify-content:center;
  text-align:center;
}
body.dark-mode .profileReferenceCard:before{
  background:radial-gradient(circle,rgba(77,143,233,.20),rgba(77,143,233,0) 70%) !important;
}
''')

if 'profileInlineFields' not in index.read_text(encoding='utf-8'):
    raise SystemExit('v9.5 inline profile fields missing')
print('v9.5 profile patch applied')
