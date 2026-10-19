(function(){
'use strict';
function E(id){return document.getElementById(id)}
function t(s){return window.AttendanceI18n?AttendanceI18n.t(s):s}
function duration(n){return window.AttendanceAppApi.signedDuration(Math.max(0,n||0)).replace(/^\+/,'')}
function refresh(c){var api=window.AttendanceAppApi;if(!api||!E('salaryNetOT22'))return;c=c||api.salaryCalc(window.salarySelectedMonth||api.monthNow());E('salaryNetOT22').textContent=api.signedDuration(c.net);E('salaryNetOT22').className=c.net<0?'deficit21':'surplus21';E('salaryShortfall22').textContent=duration(c.remainingShortfall);E('salaryOtEarned').textContent=duration(c.ot);E('salaryOtUsed').textContent=duration(c.otUsedForLeave);E('salaryOtRemaining').textContent=duration(c.otPaidMinutes);var info=E('salaryPaidDays').parentNode.querySelector('.salaryCardInfo');if(info&&!info.textContent.includes(t('Under 6 hours: Half Day. 6 hours or more: Present. Pay for full attendance days follows actual worked hours.')))info.textContent+=' '+t('Under 6 hours: Half Day. 6 hours or more: Present. Pay for full attendance days follows actual worked hours.')}
var old=window.renderSalaryMonthDetails;window.renderSalaryMonthDetails=function(c){if(old)old(c);refresh(c)};
function init(){refresh();document.addEventListener('attendance-language-changed',function(){refresh()})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
