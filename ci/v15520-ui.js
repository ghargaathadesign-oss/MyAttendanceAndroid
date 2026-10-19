(function(){
'use strict';
function E(id){return document.getElementById(id)}
function tidy(){var page=E('screen-setting-salary');page.querySelectorAll('.salaryInfoSection').forEach(function(section){
 var button=section.querySelector(':scope > .salaryInfoButton');if(!button)return;
 var heading=section.querySelector(':scope > .salaryInfoHeading');if(!heading){var title=section.querySelector(':scope > .typographyHead')||section.querySelector(':scope > small:first-child')||section.querySelector(':scope > .label');
  if(section.id==='salaryOtCover')title=section.querySelector('.payrollToggle b');
  heading=document.createElement('div');heading.className='salaryInfoHeading';
  if(title){title.parentNode.insertBefore(heading,title);heading.appendChild(title)}else{var label=document.createElement('span');label.textContent=window.AttendanceI18n?AttendanceI18n.t('Employee deductions'):'Employee deductions';heading.appendChild(label);section.insertBefore(heading,section.firstChild)}
 }
 heading.appendChild(button);
});}
var old=window.renderSalaryMonthDetails;window.renderSalaryMonthDetails=function(c){if(old)old(c);tidy()};
function init(){tidy()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
