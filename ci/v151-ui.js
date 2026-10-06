(function(){
'use strict';
var A=null;
function E(id){return document.getElementById(id)}
function openNotificationPage(ev){
  if(ev){ev.preventDefault();ev.stopPropagation();if(ev.stopImmediatePropagation)ev.stopImmediatePropagation()}
  if(A&&A.showScreen)A.showScreen('notifications');
  try{if(window.Android&&Android.markAllNotificationsRead)setTimeout(function(){Android.markAllNotificationsRead()},300)}catch(e){}
  return false;
}
function goHome(ev){
  if(ev){ev.preventDefault();ev.stopPropagation();if(ev.stopImmediatePropagation)ev.stopImmediatePropagation()}
  if(A&&A.showScreen)A.showScreen('home');
  return false;
}
function bind(){
  A=window.AttendanceAppApi||null;if(!A)return;
  var bell=E('topSettings');
  if(bell){
    bell.setAttribute('aria-label','Notifications');
    bell.setAttribute('title','Notifications');
    bell.onclick=openNotificationPage;
    bell.addEventListener('click',openNotificationPage,true);
  }
  var back=E('notificationBack');
  if(back){back.onclick=goHome;back.addEventListener('click',goHome,true)}
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind);else bind();
})();