from pathlib import Path
import sys,shutil
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
h=(p/'index.html').read_text();a='<p class="homeNote21" id="homeLeaveNote21"></p>';assert a in h
h=h.replace(a,'''<div class="homeBalances21 homeLeaveBalances23">
        <div><small>Paid Leave Used</small><b id="qPaidLeaveUsed23">0</b></div>
        <div><small>Unpaid Leave</small><b id="qUnpaidLeave23">0</b></div>
        <div><small>Absent Days</small><b id="qAbsentDays23">0</b></div>
      </div>''',1)
h=h.replace('</head>','<link rel="stylesheet" href="v15523-home.css"></head>',1);(p/'index.html').write_text(h)
shutil.copy('ci/v15523-home.css',p/'v15523-home.css')
print('v15.5.23 separate leave/absent counters and aligned Home salary/chart layout prepared')
