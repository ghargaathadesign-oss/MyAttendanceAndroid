from pathlib import Path
import sys,shutil
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
def rep(s,a,b):
 if a not in s:raise SystemExit('Missing payroll anchor: '+a[:100])
 return s.replace(a,b,1)
h=(p/'index.html').read_text();h=rep(h,'<button class="btn primary fullBtn" id="saveSalary"',Path('ci/v15517-payroll.html').read_text()+'<button class="btn primary fullBtn" id="saveSalary"')
h=rep(h,'<div class="salaryFinal">','<div id="salaryPayrollBreakdown" aria-live="polite"></div><div class="salaryFinal">');h=h.replace('Final earned salary','Take-home salary');h=rep(h,'</head>','<link rel="stylesheet" href="v15517-payroll.css"></head>');h=rep(h,'</body>','<script src="v15517-payroll.js"></script></body>');(p/'index.html').write_text(h)
s=(p/'app.js').read_text();s=rep(s,'s.monthly=parseFloat(o.monthly)||0;',"s.pfEnabled=o.pfEnabled===true;s.esicEnabled=o.esicEnabled===true;s.basicDa=Math.max(0,Number(o.basicDa)||0);s.pfFullWages=o.pfFullWages===true;s.monthly=parseFloat(o.monthly)||0;")
s=rep(s,"if(!salaryPut({monthly:monthly,otMultiplier:mult}))",'''var pfEnabled=E('salaryPfEnabled').checked,esicEnabled=E('salaryEsicEnabled').checked,basicDa=Number(E('salaryBasicDa').value),pfFullWages=E('salaryPfFullWages').checked;
 if(pfEnabled&&(!isFinite(basicDa)||basicDa<=0||basicDa>monthly)){if(status){status.textContent='Enter Basic + DA greater than 0 and no higher than monthly salary';status.className='err'}return false}
 if(!isFinite(basicDa)||basicDa<0)basicDa=0;
 if(!salaryPut({monthly:monthly,otMultiplier:mult,pfEnabled:pfEnabled,esicEnabled:esicEnabled,basicDa:basicDa,pfFullWages:pfFullWages}))''')
s=rep(s,"E('salaryAmount').value=s.monthly||'';","if(window.renderPayrollSetup)window.renderPayrollSetup(s);E('salaryAmount').value=s.monthly||'';")
s=rep(s,'salaryCalc:salaryCalc,','salaryGet:salaryGet,salaryCalc:salaryCalc,')
s=rep(s,"E('qSalary').textContent=money(sc.earned)","E('qSalary').textContent=money(sc.netEarned)");(p/'app.js').write_text(s)
v=(p/'v14-features.js').read_text();v=rep(v,'salary:sc.earned||0','salary:(sc.netEarned===undefined?sc.earned:sc.netEarned)||0');(p/'v14-features.js').write_text(v)
for name in ['v15517-payroll.js','v15517-payroll.css']:shutil.copy(Path('ci')/name,p/name)
print('v15.5.17 PF/ESIC deductions and take-home salary prepared')
