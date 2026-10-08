from pathlib import Path
import sys,re,shutil
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets');h=(p/'index.html').read_text();s=(p/'app.js').read_text()
h=h.replace('</head>','<link rel="stylesheet" href="v1559-ui.css">\n</head>')
h=h.replace('</body>','<script src="v1559-salary.js"></script>\n</body>')
start=h.index('      <div class="salarySummary">',h.index('id="screen-setting-salary"'));end=h.index('    </section>',start)
h=h[:start]+'''      <div class="settingsCard monthlySalaryCard">
        <div class="typographyHead"><span><b>Monthly salary details</b><small>Select a month to view its breakdown.</small></span></div>
        <div class="salaryMonthBar"><button type="button" id="salaryPrevMonth" aria-label="Previous salary month">‹</button><input type="month" id="salaryMonth" aria-label="Salary month"><button type="button" id="salaryNextMonth" aria-label="Next salary month">›</button></div>
        <div class="salarySummary">
          <div><small>Daily Rate</small><b id="salaryDaily">₹0</b></div><div><small>Paid Days</small><b id="salaryPaidDays">0</b></div>
          <div><small>OT Pay</small><b id="salaryOTPay">₹0</b></div><div><small>Earned salary</small><b id="salaryEstimated">₹0</b></div>
        </div><div id="salaryBreakdown" aria-live="polite"></div>
        <div class="salaryAdjustment"><div class="label">Manual adjustment</div><div class="field"><select id="salaryAdjustmentType" aria-label="Adjustment type"><option value="add">Add (+) · Bonus</option><option value="subtract">Subtract (−) · Deduction</option></select></div>
        <div class="field moneyField"><span>₹</span><input id="salaryAdjustmentAmount" type="number" min="0" step="0.01" inputmode="decimal" placeholder="Amount" aria-label="Adjustment amount"></div>
        <div class="field"><input id="salaryAdjustmentReason" maxlength="200" placeholder="Reason" aria-label="Adjustment reason"></div><button type="button" class="btn primary fullBtn" id="saveSalaryAdjustment">Save Adjustment</button><small id="salaryAdjustmentStatus" aria-live="polite"></small></div>
        <div class="salaryFinal"><small>Final earned salary</small><b id="salaryFinalAmount">₹0</b></div>
      </div>
''' +h[end:]
s=s.replace('c=salaryCalc(monthNow())','c=salaryCalc(window.salarySelectedMonth||monthNow())')
s=s.replace("E('salaryEstimated').textContent=money(c.earned)","E('salaryEstimated').textContent=money(c.earned);if(window.renderSalaryMonthDetails)window.renderSalaryMonthDetails(c)")
(p/'index.html').write_text(h);(p/'app.js').write_text(s)
for name in ['v1559-ui.css','v1559-salary.js']:shutil.copy(Path('ci')/name,p/name)
print('v15.5.9 monthly salary and settings UI applied')
