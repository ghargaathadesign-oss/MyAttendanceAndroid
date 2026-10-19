from pathlib import Path
import sys,shutil
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
def rep(s,a,b):
 if a not in s:raise SystemExit('Missing v15522 anchor '+a[:100])
 return s.replace(a,b,1)
h=(p/'index.html').read_text()
h=rep(h,'<span class="homeCountIcon21">◐</span>','<span class="homeCountIcon21 lottieIcon" data-lottie="lottie/half-day-v15522.json" aria-hidden="true"></span>');h=rep(h,'<span class="homeCountIcon21">☀</span>','<span class="homeCountIcon21 lottieIcon" data-lottie="lottie/week-off-v15522.json" aria-hidden="true"></span>')
h=h.replace('Half / Incomplete Days','Half Day')
h=rep(h,'<div class="otCoverStats"><div><small>OT earned</small>','<div class="otNet22"><small>Net OT / Deficit</small><b id="salaryNetOT22">0h 00m</b><p>Same net balance as Home for this month. Earned OT minus OT used for leave and uncovered shortfall.</p></div><div class="otCoverStats"><div><small>Gross OT earned</small>')
h=rep(h,'<div><small>Days covered</small><b id="salaryOtCovered">0</b></div></div>','<div><small>Days covered</small><b id="salaryOtCovered">0</b></div><div><small>Shortfall after OT cover</small><b id="salaryShortfall22">0h 00m</b></div></div>')
h=rep(h,'</head>','<link rel="stylesheet" href="v15522-ui.css"></head>');h=rep(h,'</body>','<script src="v15522-ui.js"></script></body>');(p/'index.html').write_text(h)
f=p/'app.js';s=f.read_text()
s=rep(s,'for(j=0;j<a.length;j++)canonicalSundayRecord(a[j]);return a','for(j=0;j<a.length;j++){canonicalSundayRecord(a[j]);if(window.AttendancePolicy)a[j].status=AttendancePolicy.attendanceStatus(a[j])}return a')
s=rep(s,"function dataPut(a){if(!verifiedStorageSet", "function dataPut(a){if(window.AttendancePolicy)a.forEach(function(r){r.status=AttendancePolicy.attendanceStatus(r)});if(!verifiedStorageSet")
f.write_text(s)
for name in ['v15522-ui.js','v15522-ui.css']:shutil.copy(Path('ci')/name,p/name)
print('v15.5.22 6-hour attendance threshold, supplied Home icons and matching net OT prepared')
