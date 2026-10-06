(function(){
'use strict';
var resolved=false,resolveAuth;
window.attendanceAuthReadyPromise=new Promise(function(resolve){
  resolveAuth=resolve;
  setTimeout(function(){if(!resolved){resolved=true;resolve()}},1500);
});
var previousAuth=window.onNativeAuthChanged;
window.onNativeAuthChanged=function(user){
  if(typeof previousAuth==='function')previousAuth(user);
  if(!resolved){resolved=true;resolveAuth()}
  setTimeout(function(){try{if(window.AttendanceAppApi&&AttendanceAppApi.renderAll)AttendanceAppApi.renderAll()}catch(e){}},0);
  setTimeout(function(){try{if(window.AttendanceAppApi&&AttendanceAppApi.renderAll)AttendanceAppApi.renderAll()}catch(e){}},250);
};
function refreshHome(){
  try{if(window.AttendanceAppApi&&AttendanceAppApi.renderAll)AttendanceAppApi.renderAll()}catch(e){}
}
if(document.readyState==='loading'){
  document.addEventListener('DOMContentLoaded',function(){
    try{if(window.Android&&Android.authState)Android.authState()}catch(e){}
    setTimeout(refreshHome,350);
    setTimeout(refreshHome,900);
  });
}else{
  try{if(window.Android&&Android.authState)Android.authState()}catch(e){}
  setTimeout(refreshHome,350);
  setTimeout(refreshHome,900);
}
document.addEventListener('visibilitychange',function(){if(!document.hidden)setTimeout(refreshHome,60)});
window.addEventListener('pageshow',function(){setTimeout(refreshHome,60)});
})();