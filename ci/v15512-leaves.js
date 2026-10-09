(function(){
'use strict';
function E(id){return document.getElementById(id)}
function A(){return window.AttendanceAppApi}
function num(v){return Number(Number(v||0).toFixed(2))}
function config(){try{return JSON.parse(localStorage.getItem('attendance_leave_setup_v81')||'{}')||{}}catch(e){return{}}}
function summary(month){var api=A(),cfg=config(),today=api.nowDate(),now=api.monthNow(),annual=Math.max(0,cfg.total==null?18:+cfg.total||0),rate=annual/12,grant=Math.max(0,+cfg.additional||0),year=month.slice(0,4),m=+month.slice(5,7),before=0,used=0,yearUsed=0,cutoff=month<now?month+'-31':today;
 api.dataGet().forEach(function(r){if(r.status!=='Paid Leave'||r.date.slice(0,4)!==year||r.date>cutoff)return;yearUsed++;if(r.date.slice(0,7)<month)before++;else if(r.date.slice(0,7)===month)used++});
 var future=month>now,priorMonths=future?(year===now.slice(0,4)?+now.slice(5,7):0):m-1,priorAllowance=rate*priorMonths,carry=Math.max(0,priorAllowance-before),extra=Math.max(0,grant-Math.max(0,before-priorAllowance)),monthly=future?0:rate;
 return{month:month,annual:annual,monthly:monthly,rate:rate,carry:carry,extra:extra,used:used,available:Math.max(0,carry+extra+monthly-used),yearUsed:yearUsed,total:rate*(future?priorMonths:m)+grant,future:future};
}
window.leavesSelectedMonth=null;
window.renderFriendlyLeaves=function(){var api=A();if(!api||!E('leaveMonthly'))return;var month=window.leavesSelectedMonth||api.monthNow();window.leavesSelectedMonth=month;var s=summary(month),parts=month.split('-'),label=new Date(+parts[0],+parts[1]-1,1).toLocaleDateString('en-US',{month:'long',year:'numeric'});
 E('leavesMonthLabel').textContent=label;E('leaveBalance').textContent=num(s.available);E('leaveMonthly').textContent=num(s.monthly)+' days';E('leaveCarry').textContent=num(s.carry)+(num(s.carry)===1?' day':' days');E('leaveGranted').textContent=num(s.extra)+' days';E('leaveMonthlyUsed').textContent=num(s.used)+(s.used===1?' day':' days');
 E('leaveBalanceCaption').textContent=s.future?'Future allowance is not available yet':'Ready to use this month';
 E('leavePolicyNote').textContent='You get '+num(s.rate)+' days each month.';E('leaveAnnual').textContent=s.annual+' days';E('leaveYear').textContent=label;
 E('leaveAccrued').textContent=num(s.total);E('leaveUsed').textContent=s.yearUsed;E('leaveAllowanceInfo').textContent=s.annual+' days / year ÷ 12 = '+num(s.rate)+' days / month';
 var rows=api.dataGet().filter(function(r){return r.date.slice(0,7)===month&&(r.status==='Paid Leave'||r.status==='Unpaid Leave')}).sort(function(a,b){return b.date.localeCompare(a.date)}),html='';
 rows.forEach(function(r){var d=r.date.split('-'),short=new Date(+d[0],+d[1]-1,+d[2]).toLocaleDateString('en-US',{month:'short'});html+='<article class="friendlyLeaveRecord"><div class="friendlyLeaveDate"><b>'+d[2]+'</b><small>'+short+'</small></div><div class="friendlyLeaveRecordText"><b>'+api.esc(r.status)+'</b><small>'+api.esc(r.reason||'Leave')+(r.date>todayDate()?' · Scheduled':'')+'</small></div><b class="friendlyLeaveDay">1 day</b></article>'});
 var box=E('leaveRecords'),content=html||'<div class="empty">No leave taken in this month.</div>';if(box.innerHTML!==content)box.innerHTML=content;
};
function todayDate(){return A().nowDate()}
function move(delta){var p=window.leavesSelectedMonth.split('-'),d=new Date(+p[0],+p[1]-1+delta,1);window.leavesSelectedMonth=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0');window.renderFriendlyLeaves()}
function init(){window.leavesSelectedMonth=A().monthNow();E('leavesPrevMonth').onclick=function(){move(-1)};E('leavesNextMonth').onclick=function(){move(1)};E('friendlyLeaveSettings').onclick=function(){A().showScreen('setting-leaves')};window.renderFriendlyLeaves()}
window.AttendanceV15512={leaveSummary:summary};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
