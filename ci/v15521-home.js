(function(){
'use strict';
function E(id){return document.getElementById(id)}
function t(s){return window.AttendanceI18n?AttendanceI18n.t(s):s}
var chartKey='';
function number(v){return Number(Number(v||0).toFixed(2))}
function render(){
 var A=window.AttendanceAppApi;if(!A||!E('qPartial'))return;
 var month=A.monthNow(),today=A.nowDate(),records=A.dataGet(),settings=A.setGet(),c=A.salaryCalc(month),present=0,partial=0,off={},paid=0,unpaid=0,absent=0,pending=false;
 var parts=month.split('-');for(var day=1;day<=+today.slice(8,10);day++){var date=month+'-'+String(day).padStart(2,'0');if(AttendancePolicy.isSunday(date))off[date]=true}
 records.forEach(function(r){if(r.date.slice(0,7)!==month||r.date>today)return;var st=AttendancePolicy.attendanceStatus(r),d=AttendancePolicy.daily(r,settings,today);
  if(st==='Paid Leave')paid++;if(st==='Unpaid Leave')unpaid++;if(st==='Absent')absent++;
  if(d.pending)pending=true;
  if(st==='Week Off'||AttendancePolicy.isSunday(r.date)){off[r.date]=true;return}
  if(st==='Half Day')partial++;
  else if(st==='Present')present++;
 });
 var leave=window.AttendanceV15512.leaveSummary(month),adj={};try{adj=JSON.parse(localStorage.getItem('attendance_salary_adjustments_v1559')||'{}')[month]||{}}catch(e){}
 var amount=Math.max(0,Number(adj.amount)||0),deduction=adj.type==='subtract'?amount:0,bonus=adj.type==='add'?amount:0;
 E('qPresent').textContent=present;E('qPartial').textContent=partial;E('qWeekOff').textContent=Object.keys(off).length;
 E('qOT').textContent=A.signedDuration(c.net);E('qOT').className=c.net<0?'deficit21':'surplus21';
 E('qLeave').textContent=number(paid+unpaid);E('qLeaveRemaining').textContent=number(leave.available);
 E('qPaidLeaveUsed23').textContent=number(leave.used);E('qUnpaidLeave23').textContent=number(unpaid);E('qAbsentDays23').textContent=number(absent);
 E('qGrossSalary').textContent=A.money(c.earned);E('qPF').textContent=A.money(c.pfDeduction);E('qESIC').textContent=A.money(c.esicDeduction);E('qOtherDeductions').textContent=A.money(deduction);E('qBonus').textContent=A.money(bonus);E('homeBonusRow21').hidden=bonus===0;
 E('qSalary').textContent=A.money(c.netEarned+bonus-deduction);
 E('homeSalaryNote21').textContent=t(pending?'Today’s shift is in progress. Its OT and salary are finalized after Clock Out.':'Based on completed attendance this month.');
 var key=JSON.stringify([month,today,records,settings,document.documentElement.lang]);if(key!==chartKey){var data=window.AttendanceReports19.series(month,records,settings,today);window.AttendanceReports19.chart(E('homePunchChart21'),data.daily,['inTime','outTime'],true,true);chartKey=key;}
 E('homePunchMonth21').textContent=new Date(+parts[0],+parts[1]-1,1).toLocaleDateString(document.documentElement.lang==='hi'?'hi-IN':'en-IN',{month:'long',year:'numeric'});
}
window.AttendanceHome21={render:render};
var old=window.renderSalaryMonthDetails;window.renderSalaryMonthDetails=function(c){if(old)old(c);render()};
function init(){render();document.addEventListener('attendance-language-changed',render)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
