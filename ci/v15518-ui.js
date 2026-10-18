(function(){
'use strict';
var OTKEY='attendance_ot_cover_v15518';
function E(id){return document.getElementById(id)}
function A(){return window.AttendanceAppApi}
function t(s){return window.AttendanceI18n?AttendanceI18n.t(s):s}
function config(){try{var c=JSON.parse(localStorage.getItem(OTKEY)||'{}');return c&&typeof c==='object'&&!Array.isArray(c)?c:{}}catch(e){return {}}}
function info(el,title,details){if(!el||el.querySelector(':scope > .salaryInfoButton'))return;el.classList.add('salaryInfoSection');var b=document.createElement('button');b.type='button';b.className='salaryInfoButton';b.textContent='i';b.setAttribute('aria-label',title+' information');b.onclick=function(e){e.preventDefault();e.stopPropagation();var dialog=appDialog(t(title),t(typeof details==='function'?details():details),[{label:t('Close'),kind:'primary'}]);dialog.classList.add('salaryInfoDialog')};el.appendChild(b)}
function decorate(){
 var page=E('screen-setting-salary'),cards=page.querySelectorAll(':scope > .settingsCard');
 info(cards[0],'Salary setup','Enter your monthly gross salary and overtime rate. Daily rate = monthly salary ÷ calendar days. Salary accrues from recorded paid days. Save to apply changes.');
 info(page.querySelector('.monthlySalaryCard'),'Monthly salary details','Choose a month. Attendance, OT cover, employee deductions and saved manual adjustments determine your take-home salary. OT cover and adjustments are saved separately for each month.');
 info(page.querySelector('.payrollSetup'),'Salary deductions',function(){return Array.from(page.querySelectorAll('.payrollHint')).map(function(n){return n.textContent}).join('\n\n')});
 page.querySelectorAll('.salarySummary > div,.salaryInfoCard').forEach(function(card){info(card,card.querySelector('small').textContent,function(){var d=card.querySelector('.salaryCardInfo');return d?d.textContent:''})});
 info(page.querySelector('.salaryAdjustment'),'Manual adjustment','Add a bonus or subtract another deduction for the selected month. This changes final take-home after PF and ESIC; it does not alter their contribution wages.');
 if(E('salaryPayrollBreakdown').textContent)info(E('salaryPayrollBreakdown'),'Employee deductions','PF uses prorated Basic + DA, excluding overtime. ESIC uses eligible earned wages including payable overtime. Only employee shares are deducted. OT exchanged for leave is removed from OT pay before these calculations.');
 info(page.querySelector('.salaryFinal'),'Take-home salary','Gross earned salary minus employee PF and ESIC, plus or minus your saved monthly adjustment. Compare the estimate with your payslip.');
 info(E('salaryOtCover'),'Use OT for days off','Uses overtime earned in the selected month to cover recorded Absent or Unpaid Leave days, earliest date first. Your standard workday sets the conversion: 9 hours = 1 day when your standard day is 9 hours. Partial cover is allowed. Normal OT is used before Sunday/holiday OT. Used hours are not paid again. Paid leave and attendance records stay unchanged. Unused OT is paid in the same month; it is not carried forward.');
}
var old=window.renderSalaryMonthDetails;
window.renderSalaryMonthDetails=function(c){if(old)old(c);var month=window.salarySelectedMonth||A().monthNow();E('salaryOtCoverEnabled').checked=config()[month]===true;E('salaryOtCoverStatus').textContent='';
 E('salaryOtEarned').textContent=A().durationText(c.ot);E('salaryOtUsed').textContent=A().durationText(c.otUsedForLeave);E('salaryOtRemaining').textContent=A().durationText(c.otPaidMinutes);E('salaryOtCovered').textContent=Number(c.otCoveredDays.toFixed(2))+' '+t('days');
 var detail=E('salaryOTPay').parentNode.querySelector('.salaryCardInfo');if(detail)detail.textContent=A().durationText(c.otPaidMinutes)+' payable overtime; '+A().durationText(c.otUsedForLeave)+' used for days off. Normal OT '+A().money(c.normalOtPay)+'; Sunday/holiday OT '+A().money(c.specialPay)+'.';
 var paid=E('salaryPaidDays').parentNode.querySelector('.salaryCardInfo');if(paid)paid.textContent=Number(c.paid.toFixed(2))+' paid day equivalents, including '+Number(c.otCoveredDays.toFixed(2))+' days covered by OT. Paid leave balance is unchanged.';
 decorate()};
function init(){
 E('saveSalaryOtCover').onclick=function(){var month=window.salarySelectedMonth||A().monthNow(),all=config(),status=E('salaryOtCoverStatus');all[month]=E('salaryOtCoverEnabled').checked;if(!A().verifiedStorageSet(OTKEY,all,'OT leave cover')){status.textContent=t('Could not save OT cover');return}A().renderAll();status.textContent=t('OT cover saved for')+' '+month};
 E('inviteEmployeeBtn').onclick=function(){var dialog=appDialog(t('Invite via email'),t('Enter the employee’s email address. Your email app will open with the invitation and app download link.'),[{label:t('Open email app'),kind:'primary'},{label:t('Cancel'),kind:'outline'}],function(i){if(i!==0)return;var email=input.value.trim();if(!email||!input.checkValidity())return;if(window.Android&&typeof Android.inviteEmployee==='function')Android.inviteEmployee(email);else window.location.href='mailto:'+encodeURIComponent(email)+'?subject='+encodeURIComponent('You’re invited to My Attendance')+'&body='+encodeURIComponent('Download My Attendance:\nhttps://github.com/ghargaathadesign-oss/MyAttendanceAndroid/releases/latest')});
 var input=document.createElement('input');input.type='email';input.required=true;input.autocomplete='email';input.placeholder=t('Employee email address');input.setAttribute('aria-label',t('Employee email address'));input.className='inviteEmailInput';dialog.querySelector('.appDialogText').appendChild(input);
 var primary=dialog.querySelector('.appDialogActions button');if(primary){primary.disabled=true;input.oninput=function(){primary.disabled=!input.checkValidity()}}input.onkeydown=function(e){if(e.key==='Enter'&&input.checkValidity()){e.preventDefault();primary.click()}};input.focus();
 };
 decorate();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
