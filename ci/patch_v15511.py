from pathlib import Path
import re,sys,shutil
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
h=(p/'index.html').read_text();s=(p/'app.js').read_text();t=(p/'v112-fixes.js').read_text()
def replace(src,old,new):
 if old not in src: raise SystemExit('Missing anchor: '+old[:90])
 return src.replace(old,new,1)
h=replace(h,'</head>','<link rel="stylesheet" href="v15511-ui.css">\n</head>')
h=replace(h,'</body>','<script src="v15511-updates.js"></script>\n</body>')
h=replace(h,'<div class="settingsMenu">','<div class="field"><input id="settingsSearch" type="search" placeholder="Search settings" aria-label="Search settings"></div><p id="settingsSearchEmpty" class="helpText" hidden>No matching settings.</p>\n      <div class="settingsMenu">')
h=replace(h,'<div class="label">Annual Paid Leave Cap</div>','<div class="label">Annual Paid Leave Allowance</div>')
h=replace(h,'Set the total paid leaves available for this year. My Leaves uses this saved total and subtracts paid leave already used.','Annual allowance ÷ 12 = monthly allowance. Leave accrues each month; additional granted leave is available separately.')
h=replace(h,'<div id="leaveSetupRows">','<div class="label">Additional Leaves Granted</div><div class="field"><input id="additionalLeaves" type="number" min="0" max="365" step="0.5" aria-label="Additional leaves granted"></div><p class="helpText">Extra paid leave granted for this year, in addition to monthly accrual.</p><div id="leaveSetupRows">') if '<div id="leaveSetupRows">' in h else replace(h,'id="leaveSetupRows"','id="leaveSetupRows"')
# Insert before category rows regardless of existing classes.
if 'id="additionalLeaves"' not in h:
 h=re.sub(r'(<div[^>]*id="leaveSetupRows"[^>]*>)','<div class="label">Additional Leaves Granted</div><div class="field"><input id="additionalLeaves" type="number" min="0" max="365" step="0.5" aria-label="Additional leaves granted"></div><p class="helpText">Extra paid leave granted for this year, in addition to monthly accrual.</p>\\1',h,count=1)
h=replace(h,'<small>Total Leaves</small>','<small>Accrued + Granted</small>')
h=replace(h,'<div class="leaveStats">','<p id="leaveAllowanceInfo" class="helpText"></p><div class="leaveStats">')
s=replace(s,"tot.value=cfg.total;","tot.value=cfg.total;E('additionalLeaves').value=Number(cfg.additional)||0;")
s=replace(s,"opt(tot,i,i+' days')","opt(tot,i,i+' / year · '+Number((i/12).toFixed(2))+' / month')")
s=replace(s,"cfg={total:parseInt(E('totalLeaves').value,10)||0,categories:[]}","cfg={total:parseInt(E('totalLeaves').value,10)||0,additional:Number(E('additionalLeaves').value)||0,categories:[]}")
s=replace(s," for(i=0;i<rows.length;i++){\n  n=rows[i]", " if(!isFinite(cfg.additional)||cfg.additional<0||cfg.additional>365){st.textContent='Enter additional leave between 0 and 365 days';st.className='err';return false}\n for(i=0;i<rows.length;i++){\n  n=rows[i]")
s=replace(s,"total=Math.max(0,Number(cfg.total)||0);","total=Math.max(0,Number(cfg.total)||0)/12*(new Date().getMonth()+1)+Math.max(0,Number(cfg.additional)||0);")
s=replace(s,"if(x.date.indexOf(yr)===0){if(x.status==='Paid Leave')paid++;", "if(x.date.indexOf(yr)===0&&x.date<=nowDate()){if(x.status==='Paid Leave')paid++;")
s=replace(s,"E('leaveBalance').textContent=balance;E('leaveAccrued').textContent=total;", "E('leaveBalance').textContent=Number(balance.toFixed(2));E('leaveAccrued').textContent=Number(total.toFixed(2));E('leaveAllowanceInfo').textContent=cfg.total+' days / year ÷ 12 = '+Number((cfg.total/12).toFixed(2))+' days / month · '+Number((total-(Number(cfg.additional)||0)).toFixed(2))+' accrued + '+(Number(cfg.additional)||0)+' granted';")
s=replace(s,"+' days • Overall total: '+E('totalLeaves').value+' days'", "+' days • Annual: '+E('totalLeaves').value+' ÷ 12 = '+Number((Number(E('totalLeaves').value)/12).toFixed(2))+' days/month • Additional: '+(Number(E('additionalLeaves').value)||0)+' days'")
s=replace(s,"function renderPunchButton(){", "function renderPunchButton(){")
s=replace(s,"status.textContent='Checked in at '+timeText(x.checkIn)","if(window.AttendanceV15511)window.AttendanceV15511.renderPunchTimes();else status.textContent='' ")
old=re.search(r'function updateWorkRing\(\)\{.*?\n',t).group(0)
new="""function updateWorkRing(){var btn=E('punchBtn'),wrap=btn&&btn.parentNode,ring=E('workProgressValue'),txt=E('workProgressText'),x=currentRecord(),s=getSettings(),std=s.h*60+s.m;if(!btn||!ring||!txt)return;var C=351.86,active=!!(x&&x.checkIn&&!x.checkOut);btn.classList.toggle('workProgressActive',active);if(wrap)wrap.classList.toggle('working',active);txt.textContent='';ring.style.strokeDasharray=C;ring.style.strokeDashoffset=C;if(active){var now=new Date(),elapsed=now.getHours()*60+now.getMinutes()-minFrom(x.checkIn);if(elapsed<0)elapsed+=1440;ring.style.strokeDashoffset=String(C*(1-(specialV113(x)?1:Math.max(0,Math.min(1,elapsed/Math.max(1,std))))))}if(window.AttendanceV15511)window.AttendanceV15511.renderPunchTimes()}
"""
t=t.replace(old,new,1)
for name,content in [('index.html',h),('app.js',s),('v112-fixes.js',t)]: (p/name).write_text(content)
for name in ['v15511-ui.css','v15511-updates.js']:shutil.copy(Path('ci')/name,p/name)
print('v15.5.11 five requested updates applied')
