(function(){
'use strict';
var OTKEY='attendance_ot_cover_v15518';
function E(id){return document.getElementById(id)}
function A(){return window.AttendanceAppApi}
function t(s){return window.AttendanceI18n?AttendanceI18n.t(s):s}
function inviteNotice(msg){var el=E('toast');if(el){el.textContent=msg;el.style.display='block';setTimeout(function(){el.style.display='none'},2200)}}
function config(){try{var c=JSON.parse(localStorage.getItem(OTKEY)||'{}');return c&&typeof c==='object'&&!Array.isArray(c)?c:{}}catch(e){return {}}}
function info(el,title,details){if(!el||Array.prototype.some.call(el.querySelectorAll('.salaryInfoButton'),function(b){return b._salaryInfoOwner===el}))return;el.classList.add('salaryInfoSection');var b=document.createElement('button');b._salaryInfoOwner=el;b.type='button';b.className='salaryInfoButton';b.textContent='i';b.setAttribute('aria-label',title+' information');b.onclick=function(e){e.preventDefault();e.stopPropagation();var dialog=appDialog(t(title),t(typeof details==='function'?details():details),[{label:t('Close'),kind:'primary'}]);dialog.classList.add('salaryInfoDialog')};el.appendChild(b)}
function decorate(){
 var page=E('screen-setting-salary'),cards=page.querySelectorAll(':scope > .settingsCard');
 info(cards[0],'Salary setup','Enter your monthly gross salary and overtime rate. Daily rate = monthly salary ÷ calendar days. Salary accrues from recorded paid days. Save to apply changes.');
 info(page.querySelector('.monthlySalaryCard'),'Monthly salary details','Choose a month. Attendance, OT cover, employee deductions and saved manual adjustments determine your take-home salary. OT cover and adjustments are saved separately for each month.');
 info(page.querySelector('.payrollSetup'),'Salary deductions',function(){return Array.from(page.querySelectorAll('.payrollHint')).map(function(n){return n.textContent}).join('\n\n')});
 page.querySelectorAll('.salarySummary > div,.salaryInfoCard').forEach(function(card){info(card,card.querySelector('small').textContent,function(){var d=card.querySelector('.salaryCardInfo');return d?d.textContent:''})});
 info(page.querySelector('.salaryAdjustment'),'Manual adjustment','Add a bonus or subtract another deduction for the selected month. This changes final take-home after PF and ESIC; it does not alter their contribution wages.');
 if(E('salaryPayrollBreakdown').textContent)info(E('salaryPayrollBreakdown'),'Employee deductions','PF uses prorated Basic + DA, excluding overtime. ESIC uses eligible earned wages including payable overtime. Only employee shares are deducted. OT exchanged for leave is removed from OT pay before these calculations.');
 info(page.querySelector('.salaryFinal'),'Take-home salary','Gross earned salary minus employee PF and ESIC, plus or minus your saved monthly adjustment. Compare the estimate with your payslip.');
 info(E('salaryOtCover'),'Use OT for days off','Uses overtime earned in the selected month to cover recorded leave days, earliest date first within each type. Your standard workday sets the conversion: 9 hours = 1 day when your standard day is 9 hours. Partial cover is allowed. Normal OT is used before Sunday/holiday OT. Used hours are not paid again. OT covers Paid Leave first and returns that allowance to your balance, then covers Absent or Unpaid Leave. Attendance records stay unchanged. Unused OT is paid in the same month; it is not carried forward.');
}
var old=window.renderSalaryMonthDetails;
window.renderSalaryMonthDetails=function(c){if(old)old(c);var month=window.salarySelectedMonth||A().monthNow();E('salaryOtCoverEnabled').checked=config()[month]===true;E('salaryOtCoverStatus').textContent='';
 E('salaryOtEarned').textContent=A().durationText(c.ot);E('salaryOtUsed').textContent=A().durationText(c.otUsedForLeave);E('salaryOtRemaining').textContent=A().durationText(c.otPaidMinutes);E('salaryOtCovered').textContent=Number(c.otCoveredDays.toFixed(2))+' '+t('days');
 var detail=E('salaryOTPay').parentNode.querySelector('.salaryCardInfo');if(detail)detail.textContent=A().durationText(c.otPaidMinutes)+' payable overtime; '+A().durationText(c.otUsedForLeave)+' used for days off. Normal OT '+A().money(c.normalOtPay)+'; Sunday/holiday OT '+A().money(c.specialPay)+'.';
 var paid=E('salaryPaidDays').parentNode.querySelector('.salaryCardInfo');if(paid)paid.textContent=Number(c.paid.toFixed(2))+' paid day equivalents, including '+Number(c.otCoveredDays.toFixed(2))+' days covered by OT. OT-covered Paid Leave is returned to your balance.';
 decorate()};
function init(){
 E('saveSalaryOtCover').onclick=function(){var month=window.salarySelectedMonth||A().monthNow(),all=config(),status=E('salaryOtCoverStatus');all[month]=E('salaryOtCoverEnabled').checked;if(!A().verifiedStorageSet(OTKEY,all,'OT leave cover')){status.textContent=t('Could not save OT cover');return}if(window.AttendanceV14)AttendanceV14.onDataChanged();if(window.AttendanceV15&&AttendanceV15.onDataChanged)AttendanceV15.onDataChanged();A().renderAll();status.textContent=t('OT cover saved for')+' '+month};
 E('salaryOtCoverEnabled').onchange=function(){E('saveSalaryOtCover').click()};
 E('inviteEmployeeBtn').onclick=function(){var dialog=appDialog(t('Invite via email'),t('Enter the employee’s email address. Your email app will open with the invitation and app download link.'),[{label:t('Open email app'),kind:'primary'},{label:t('Cancel'),kind:'outline'}],function(i){if(i!==0)return;var email=input.value.trim();if(!email||!input.checkValidity())return;if(window.Android&&typeof Android.inviteEmployee==='function')Android.inviteEmployee(email);else window.location.href='mailto:'+encodeURIComponent(email)+'?subject='+encodeURIComponent('You’re invited to My Attendance')+'&body='+encodeURIComponent('Download My Attendance:\nhttps://my-attendance-download.lively-cloud-6542.chatgpt.site')});
 var card=dialog.querySelector('.appDialogCard'),heading=dialog.querySelector('.appDialogTitle');card.classList.add('inviteDialog20');
 var share=document.createElement('button');share.id='inviteShareBtn';share.type='button';share.className='inviteShareButton';share.setAttribute('aria-label',t('Share app link'));share.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 10.5 6.8-4M8.6 13.5l6.8 4"/></svg>';
 share.onclick=function(){var url='https://my-attendance-download.lively-cloud-6542.chatgpt.site',body='You’re invited to My Attendance. Track your attendance, leave and salary. Download the Android app: '+url;
  if(window.Android&&typeof Android.shareAppInvite==='function'){Android.shareAppInvite();return}
  if(navigator.share){navigator.share({title:'My Attendance',text:body,url:url}).catch(function(e){if(e.name!=='AbortError')inviteNotice(t('Could not open sharing. Try again.'))});return}
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(body).then(function(){inviteNotice(t('Invite link copied'))},function(){inviteNotice(url)});return}inviteNotice(url);
 };heading.appendChild(share);
 var input=document.createElement('input');input.type='email';input.required=true;input.autocomplete='email';input.placeholder=t('Employee email address');input.setAttribute('aria-label',t('Employee email address'));input.className='inviteEmailInput';dialog.querySelector('.appDialogText').appendChild(input);
 var primary=dialog.querySelector('.appDialogActions button');if(primary){primary.disabled=true;input.oninput=function(){primary.disabled=!input.checkValidity()}}input.onkeydown=function(e){if(e.key==='Enter'&&input.checkValidity()){e.preventDefault();primary.click()}};input.focus();
 };
 decorate();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
