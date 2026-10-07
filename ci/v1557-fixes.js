(function(){
'use strict';
function E(id){return document.getElementById(id)}
function A(){return window.AttendanceAppApi||{}}

function openMonthlyRecordEdit(ev){
  var b=ev.target&&ev.target.closest?ev.target.closest('#records .v154RecordEdit[data-id],#records .v15RecordOpen[data-id]'):null;
  if(!b)return;
  var api=A(),id=b.getAttribute('data-id');
  if(id&&typeof api.openEdit==='function'){
    ev.preventDefault();
    ev.stopPropagation();
    api.openEdit(id);
  }
}

function ensureCanonicalAttendance(){
  var screen=E('screen-attendance');
  if(!screen||!screen.classList.contains('active'))return;
  try{
    if(window.AttendanceV15&&typeof AttendanceV15.renderScreen==='function')AttendanceV15.renderScreen('attendance');
  }catch(e){}
}

function init(){
  document.addEventListener('click',openMonthlyRecordEdit,true);
  document.addEventListener('click',function(ev){
    var b=ev.target&&ev.target.closest?ev.target.closest('.navBtn[data-screen="attendance"],.settingBack'):null;
    if(b)setTimeout(ensureCanonicalAttendance,30);
  },true);
  document.addEventListener('visibilitychange',function(){if(!document.hidden)setTimeout(ensureCanonicalAttendance,30)});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();