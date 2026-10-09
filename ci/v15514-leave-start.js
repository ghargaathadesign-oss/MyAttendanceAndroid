(function(){
'use strict';
function E(id){return document.getElementById(id)}
function num(n){return Number(Number(n||0).toFixed(2))}
window.promptStartingLeave=function(cfg,old,save){
 var month=AttendanceAppApi.monthNow();
 function ask(value,error){
  var dialog=appDialog('Starting leave balance','How many unused paid leave days do you have from earlier months?',[{label:'Save',kind:'primary'},{label:'Cancel',kind:'outline'}],function(i,text){
   if(i!==0)return;
   var balance=Number(text);
   if(!text.trim()||!isFinite(balance)||balance<0||balance>365||Math.abs(balance*2-Math.round(balance*2))>0.00001){ask(text,'Enter 0–365 days, including half-days.');return}
   cfg.startingLeave={month:month,balance:balance};save();
  },{type:'number',placeholder:'Unused leave days, e.g. 0 or 2.5'});
  var help=document.createElement('p');help.className='helpText';help.style.cssText='font-size:12px;line-height:1.5;margin:12px 0;font-style:italic';help.textContent='Exclude this month’s allowance. Enter 0 if you’ve used all earlier leave.';dialog.querySelector('.appDialogText').appendChild(help);
  if(error){var warning=document.createElement('p');warning.className='err';warning.textContent=error;dialog.querySelector('.appDialogText').appendChild(warning)}
  var input=E('appDialogInput');input.min='0';input.max='365';input.step='0.5';input.inputMode='decimal';input.value=value;input.setAttribute('aria-label','Unused leave from earlier months');input.focus();
 }
 ask(old.startingLeave?String(old.startingLeave.balance):'',false);
 return false;
};
window.refreshStartingLeaveNote=function(cfg){var el=E('startingLeaveNote');if(!el)return;var s=cfg.startingLeave;el.textContent=s?'Starting balance: '+num(s.balance)+' days from earlier months · Set for '+s.month+'. Unused leave carries forward automatically.':'On saving, enter the unused leave you have from earlier months.'};
})();
