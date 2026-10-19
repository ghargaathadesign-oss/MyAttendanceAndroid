(function(){
'use strict';
function E(id){return document.getElementById(id)}
function t(s){return window.AttendanceI18n?AttendanceI18n.t(s):s}
var old=window.renderSalaryMonthDetails;
window.renderSalaryMonthDetails=function(c){if(old)old(c);var month=window.salarySelectedMonth||AttendanceAppApi.monthNow(),s=AttendanceV15512.leaveSummary(month),cards=E('salaryBreakdown').querySelectorAll('.salaryInfoCard');
 cards[1].querySelector('b').textContent=Number(s.used.toFixed(2))+' '+t('days');cards[1].querySelector('.salaryCardInfo').textContent=Number(s.rate.toFixed(2))+' days allowed per month. '+t('Paid leave charged after OT cover.')+' '+Number(c.otPaidLeaveRefund.toFixed(2))+' '+t('days restored by OT.');
 E('salaryOtCoverOutcome').textContent=c.otUsedForLeave>0?Number(c.otPaidLeaveRefund.toFixed(2))+' '+t('paid leave days restored')+' · '+Number(c.otCoveredUnpaidDays.toFixed(2))+' '+t('unpaid days covered'):E('salaryOtCoverEnabled').checked?t('No OT or eligible leave to cover in this month.'):t('Turn on to apply OT immediately.');
};
})();
