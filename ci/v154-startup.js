(function(){
'use strict';
var resolved=false,resolveAuth,refreshQueued=false;
window.attendanceAuthReadyPromise=new Promise(function(resolve){
  resolveAuth=resolve;
  setTimeout(function(){if(!resolved){resolved=true;resolve()}},2200);
});
var previousAuth=window.onNativeAuthChanged;
function renderOnce(){
  refreshQueued=false;
  try{if(window.AttendanceAppApi&&AttendanceAppApi.renderAll)AttendanceAppApi.renderAll()}catch(e){}
}
function queueRender(){
  if(refreshQueued)return;refreshQueued=true;
  if(window.requestAnimationFrame)requestAnimationFrame(renderOnce);else setTimeout(renderOnce,0);
}
window.onNativeAuthChanged=function(user){
  if(typeof previousAuth==='function')previousAuth(user);
  if(!resolved){resolved=true;resolveAuth()}
  if(window.AttendanceAppApi)queueRender();
};
function requestAuth(){try{if(window.Android&&Android.authState)Android.authState()}catch(e){}}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',requestAuth);else requestAuth();
document.addEventListener('visibilitychange',function(){if(!document.hidden&&window.AttendanceAppApi)queueRender()});
window.addEventListener('pageshow',function(){if(window.AttendanceAppApi)queueRender()});
})();