from pathlib import Path
import sys,shutil
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
h=(p/'index.html').read_text()
a=h.index('      <div class="overviewGrid overview4">');b=h.index('    </section>',a)
h=h[:a]+'''      <div class="homeAttendance21">
        <div><span class="homeCountIcon21 lottieIcon" data-lottie="lottie/present-v155.json"></span><b id="qPresent">0</b><small>Present</small></div>
        <div><span class="homeCountIcon21">◐</span><b id="qPartial">0</b><small>Half / Incomplete Days</small></div>
        <div><span class="homeCountIcon21">☀</span><b id="qWeekOff">0</b><small>Week Off</small></div>
      </div>
      <div class="homeBalances21">
        <div><small>Net OT / Deficit</small><b id="qOT">0h</b></div>
        <div><small>Leaves Taken</small><b id="qLeave">0</b></div>
        <div><small>Remaining Paid Leaves</small><b id="qLeaveRemaining">0</b></div>
      </div>
      <p class="homeNote21" id="homeLeaveNote21"></p>
      <section class="homeSalary21">
        <div class="homeSalaryTitle21"><b>Salary Earned</b><button type="button" id="salaryShortcut">View details <span aria-hidden="true">›</span></button></div>
        <div class="homeGross21"><small>Gross Salary Earned</small><b id="qGrossSalary">₹0</b><span>Before PF, ESIC and other deductions</span></div>
        <div class="homeDeduction21"><span>PF Deduction</span><b id="qPF">₹0</b></div>
        <div class="homeDeduction21"><span>ESIC Deduction</span><b id="qESIC">₹0</b></div>
        <div class="homeDeduction21"><span>Other Deductions</span><b id="qOtherDeductions">₹0</b></div>
        <div class="homeDeduction21" id="homeBonusRow21" hidden><span>Bonus / Addition</span><b id="qBonus">₹0</b></div>
        <div class="homeNet21"><span>Net Salary Earned</span><b id="qSalary">₹0</b></div>
        <p class="homeNote21" id="homeSalaryNote21">Based on completed attendance this month.</p>
      </section>
      <section class="settingsCard homePunch21"><div class="label">Daily In &amp; Out</div><b id="homePunchMonth21" class="chartMonthLabel"></b><p class="reportChartNote">Your in and out times at a glance. Recorded punch days only; +1 day means the following day.</p><div id="homePunchChart21"></div></section>
'''+h[b:]
h=h.replace('Daily rhythm','Daily In &amp; Out').replace('</head>','<link rel="stylesheet" href="v15521-home.css"></head>',1).replace('</body>','<script src="v15521-home.js"></script></body>',1)
(p/'index.html').write_text(h)
f=p/'app.js';s=f.read_text();anchor="E('qSalary').textContent=money(sc.netEarned);renderPunchButton()";assert anchor in s;s=s.replace(anchor,anchor+";if(window.AttendanceHome21)AttendanceHome21.render()",1);f.write_text(s)
for name in ['v15521-home.js','v15521-home.css']:shutil.copy(Path('ci')/name,p/name)
print('v15.5.21 Home attendance, leave/salary balances and daily area chart prepared')
