from pathlib import Path
import sys,shutil,re
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
def rep(s,a,b):
 if a not in s:raise SystemExit('Missing v15518 anchor '+a[:90])
 return s.replace(a,b,1)
h=(p/'index.html').read_text()
h=rep(h,'<div class="settingsCard">\n        <div class="label">Monthly Salary','<div class="settingsCard"><div class="typographyHead"><span><b>Salary setup</b></span></div>\n        <div class="label">Monthly Salary')
h=rep(h,'<div class="salaryAdjustment">','''<section id="salaryOtCover"><label class="payrollToggle" for="salaryOtCoverEnabled"><span><b>Use OT for days off</b><small>Paid leave stays unchanged</small></span><input id="salaryOtCoverEnabled" type="checkbox" role="switch"></label><div class="otCoverStats"><div><small>OT earned</small><b id="salaryOtEarned">0h</b></div><div><small>OT used for leave</small><b id="salaryOtUsed">0h</b></div><div><small>OT left for pay</small><b id="salaryOtRemaining">0h</b></div><div><small>Days covered</small><b id="salaryOtCovered">0</b></div></div><button type="button" class="btn primary fullBtn" id="saveSalaryOtCover">Save OT Cover</button><small id="salaryOtCoverStatus" class="otCoverStatus" aria-live="polite"></small></section><div class="salaryAdjustment">''')
h=rep(h,'<button class="settingsLogoutRow"','''<button type="button" class="settingsMenuRow" id="inviteEmployeeBtn"><span class="inviteIcon" aria-hidden="true">✉</span><span><b>Invite via email</b><small>Share the app with an employee</small></span><i>›</i></button><button class="settingsLogoutRow"''')
h=re.sub(r'(data-setting="help">.*?data-lottie="lottie/)privacy-v155.json',r'\1help-v15518.json',h,count=1,flags=re.S)
start=h.index('id="screen-setting-help"');h=h[:start]+h[start:].replace('lottie/privacy-v155.json','lottie/help-v15518.json',1)
h=rep(h,'</head>','<link rel="stylesheet" href="v15518-ui.css"></head>');h=rep(h,'</body>','<script src="v15518-ui.js"></script></body>');(p/'index.html').write_text(h)
s=(p/'app.js').read_text();s=rep(s,'return AttendancePolicy.salaryMonth(dataGet(),month,setGet(),salaryGet());',"{var sal=salaryGet();try{sal.otCoverEnabled=JSON.parse(localStorage.getItem('attendance_ot_cover_v15518')||'{}')[month]===true}catch(e){sal.otCoverEnabled=false}return AttendancePolicy.salaryMonth(dataGet(),month,setGet(),sal);}")
(p/'app.js').write_text(s)
for name in ['v15518-ui.js','v15518-ui.css']:shutil.copy(Path('ci')/name,p/name)
print('v15.5.18 OT leave cover, Salary info popups, Help and invites prepared')
