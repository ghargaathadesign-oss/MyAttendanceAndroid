(function(){
'use strict';
function E(id){return document.getElementById(id)}
window.renderPayrollSetup=function(s){E('salaryPfEnabled').checked=s.pfEnabled===true;E('salaryEsicEnabled').checked=s.esicEnabled===true;E('salaryBasicDa').value=s.basicDa||'';E('salaryPfFullWages').checked=s.pfFullWages===true;visibility()};
function visibility(){E('salaryPfFields').hidden=!E('salaryPfEnabled').checked;E('salaryEsicHint').hidden=!E('salaryEsicEnabled').checked}
var previous=window.renderSalaryMonthDetails;
window.renderSalaryMonthDetails=function(c){
 if(previous)previous(c);
 var A=window.AttendanceAppApi,box=E('salaryPayrollBreakdown'),s=A.salaryGet();box.textContent='';
 function row(label,amount,total){var r=document.createElement('div'),l=document.createElement('span'),v=document.createElement('b');r.className='payrollRow'+(total?' total':'');l.textContent=label;v.textContent=A.money(amount);r.appendChild(l);r.appendChild(v);box.appendChild(r)}
 if(s.pfEnabled||s.esicEnabled){row('Gross earned salary',c.earned);if(s.pfEnabled)row('PF · 12%',c.pfDeduction);if(s.esicEnabled)row(c.esicExempt?'ESIC · daily-wage exemption':'ESIC · 0.75%',c.esicDeduction);row('Total deductions',c.payrollDeduction,true);row('Take-home before adjustment',c.netEarned,true)}
 var amount=Number(E('salaryAdjustmentAmount').value)||0;E('salaryFinalAmount').textContent=A.money(c.netEarned+(E('salaryAdjustmentType').value==='subtract'?-amount:amount));
};
function init(){E('salaryPfEnabled').addEventListener('change',visibility);E('salaryEsicEnabled').addEventListener('change',visibility);if(window.AttendanceAppApi)renderPayrollSetup(AttendanceAppApi.salaryGet())}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
