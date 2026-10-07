(function(){
'use strict';
function E(id){return document.getElementById(id)}
function status(msg,ok){
  var el=E('salarySaveStatus');
  if(!el)return;
  el.textContent=msg||'';
  el.classList.toggle('ok',!!ok);
  el.classList.toggle('err',ok===false);
}
function triggerSave(ev){
  var b=ev.target&&ev.target.closest?ev.target.closest('#saveSalary'):null;
  if(!b)return;
  ev.preventDefault();
  ev.stopImmediatePropagation();
  var A=window.AttendanceAppApi||{};
  if(typeof A.saveSalary==='function'){
    status('Saving…');
    A.saveSalary();
    setTimeout(function(){
      var amt=E('salaryAmount');
      var n=amt?parseFloat(String(amt.value||'').replace(/[^0-9.\-]/g,'')):0;
      var daily=E('salaryDaily'),est=E('salaryEstimated');
      if(n>0 && daily && est && daily.textContent!=='₹0' && est.textContent!=='₹0') status('Salary settings saved',true);
      else if(n===0) status('Salary settings saved',true);
      else status('Saved. Salary summary refreshed.',true);
    },80);
  }else{
    status('Could not save salary settings',false);
  }
}
function init(){
  document.addEventListener('click',triggerSave,true);
  var amt=E('salaryAmount');
  if(amt)amt.addEventListener('keydown',function(e){
    if(e.key==='Enter'){e.preventDefault();var b=E('saveSalary');if(b)b.click();}
  });
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();