(function(){
'use strict';
function E(id){return document.getElementById(id)}
var guarding=false;
function canonicalAttendance(){
  if(guarding)return;
  var screen=E('screen-attendance');
  if(!screen||!screen.classList.contains('active'))return;
  var cal=E('attendanceCalendar'),legacy=!!(cal&&cal.querySelector('.calendarCell'));
  if(!legacy)return;
  guarding=true;
  try{
    if(window.AttendanceV15&&AttendanceV15.onDataChanged)AttendanceV15.onDataChanged();
    if(window.AttendanceV15&&AttendanceV15.renderScreen)AttendanceV15.renderScreen('attendance');
  }catch(e){}
  guarding=false;
}
function openRecordFromClick(e){
  var target=e.target&&e.target.closest?e.target.closest('#records .v154RecordEdit[data-id],#records .v154Record[data-id]'):null;
  if(!target)return;
  var card=target.classList.contains('v154Record')?target:target.closest('.v154Record[data-id]');
  var id=(target.getAttribute('data-id')||(card&&card.getAttribute('data-id'))||'');
  var A=window.AttendanceAppApi||{};
  if(id&&typeof A.openEdit==='function'){
    e.preventDefault();
    e.stopImmediatePropagation();
    A.openEdit(id);
  }
}
function init(){
  document.addEventListener('click',openRecordFromClick,true);
  var screen=E('screen-attendance');
  if(screen)new MutationObserver(function(){setTimeout(canonicalAttendance,0)}).observe(screen,{childList:true,subtree:true});
  document.addEventListener('visibilitychange',function(){if(!document.hidden)setTimeout(canonicalAttendance,0)});
  window.addEventListener('pageshow',function(){setTimeout(canonicalAttendance,0)});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();