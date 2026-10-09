from pathlib import Path
import sys,shutil
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
def replace(s,a,b):
 if a not in s:raise SystemExit('Missing anchor: '+a[:70])
 return s.replace(a,b,1)
h=(p/'index.html').read_text()
h=replace(h,'<span class="v154BootLottie lottieIcon" data-lottie="lottie/loading-v155.json" aria-hidden="true"></span>','<span class="v154BootDots" aria-hidden="true"><i></i><i></i><i></i></span>')
h=replace(h,'<div class="preview" id="leaveSetupPreview">','<p id="startingLeaveNote" class="helpText"></p><div class="preview" id="leaveSetupPreview">')
h=replace(h,'<script src="app.js"','<script src="v15514-leave-start.js"></script>\n<script src="app.js"')
(p/'index.html').write_text(h)
s=(p/'app.js').read_text()
s=replace(s," box.innerHTML=html;previewLeaveSetup()"," box.innerHTML=html;previewLeaveSetup();if(window.refreshStartingLeaveNote)window.refreshStartingLeaveNote(cfg)")
s=replace(s," if(!leavePut(cfg)){", " var previous=leaveGet();\n function commitLeaveSetup(){\n if(!leavePut(cfg)){")
s=replace(s," toast('Leave Setup saved');return true\n}",""" toast('Leave Setup saved');return true
 }
 if(!previous.startingLeave||+previous.total!==+cfg.total)return window.promptStartingLeave(cfg,previous,commitLeaveSetup);
 cfg.startingLeave=previous.startingLeave;
 return commitLeaveSetup();
}""")
(p/'app.js').write_text(s)
s=(p/'v15512-leaves.js').read_text()
a=" return{month:month,annual:annual,monthly:monthly,rate:rate,carry:carry,extra:extra,used:used,available:Math.max(0,carry+extra+monthly-used),yearUsed:yearUsed,total:rate*(future?priorMonths:m)+grant,future:future};"
b=""" var total=rate*(future?priorMonths:m)+grant,opening=cfg.startingLeave;
 if(opening&&/^\\d{4}-\\d{2}$/.test(opening.month)&&isFinite(opening.balance)&&+opening.balance>=0&&opening.month.slice(0,4)===year&&month>=opening.month){
  var startMonth=+opening.month.slice(5,7),elapsed=Math.max(0,priorMonths-startMonth+1),trackedBefore=0,trackedUsed=0;
  api.dataGet().forEach(function(r){if(r.status!=='Paid Leave'||r.date.slice(0,4)!==year||r.date.slice(0,7)<opening.month||r.date>cutoff)return;trackedUsed++;if(r.date.slice(0,7)<month)trackedBefore++});
  priorAllowance=+opening.balance+rate*elapsed;
  carry=Math.max(0,priorAllowance-trackedBefore);extra=Math.max(0,grant-Math.max(0,trackedBefore-priorAllowance));
  yearUsed=trackedUsed;total=+opening.balance+rate*(elapsed+(future?0:1))+grant;
 }
 return{month:month,annual:annual,monthly:monthly,rate:rate,carry:carry,extra:extra,used:used,available:Math.max(0,carry+extra+monthly-used),yearUsed:yearUsed,total:total,future:future};"""
s=replace(s,a,b);(p/'v15512-leaves.js').write_text(s)
s=(p/'v15511-updates.js').read_text();a=" set(2,n(Math.max(0,accrued+allow.additional-yearUsed))+' days',n(accrued)+' accrued + '+allow.additional+' granted − '+yearUsed+' used. Annual allowance ÷ 12; unused accrued leave carries forward.');";b=a+"\n if(window.AttendanceV15512){var balance=AttendanceV15512.leaveSummary(month);set(2,n(balance.available)+' days',n(balance.carry)+' carried forward + '+n(balance.monthly)+' this month + '+n(balance.extra)+' granted − '+n(balance.used)+' used this month.');}";s=replace(s,a,b);(p/'v15511-updates.js').write_text(s)
shutil.copy('ci/v15514-leave-start.js',p/'v15514-leave-start.js')
print('v15.5.14 stable UI, starting balance and three-dot startup prepared')
