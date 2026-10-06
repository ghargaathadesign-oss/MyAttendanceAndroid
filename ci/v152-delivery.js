(function(){
'use strict';
function E(id){return document.getElementById(id)}
function renderPushDiag(state){
  var el=E('notificationPushDiag');if(!el)return;
  state=state||{};
  var token=!!state.pushTokenAvailable,updates=!!state.topicUpdates,all=!!state.topicAll,err=String(state.topicError||'').trim();
  var parts=[];
  parts.push(token?'FCM connected':'FCM token not ready');
  parts.push(updates?'Update channel subscribed':'Update channel not subscribed');
  parts.push(all?'General channel subscribed':'General channel not subscribed');
  el.textContent=parts.join(' • ')+(err?' • '+err:'');
  el.className='notificationPushDiag '+(token&&(updates||all)?'ok':'warn');
}
var previous=window.onNativeNotificationState;
window.onNativeNotificationState=function(payload){
  if(typeof previous==='function')previous(payload);
  var state=payload;
  if(typeof payload==='string'){try{state=JSON.parse(payload)}catch(e){state={}}}
  renderPushDiag(state||{});
};
window.onUpdateCheckResult=function(state,msg){
  var el=E('updateInstallStatus');
  if(el)el.textContent=msg||'';
  var progress=E('updateProgress');
  if(progress)progress.hidden=false;
  if(state==='up_to_date')setTimeout(function(){if(progress)progress.hidden=true},2600);
};
function refreshState(){
  try{
    if(window.Android&&Android.notificationState){
      window.onNativeNotificationState(Android.notificationState());
    }
  }catch(e){}
}
function bind(){
  var check=E('notificationCheckUpdates');
  if(check)check.onclick=function(){
    var st=E('updateInstallStatus'),p=E('updateProgress');
    if(p)p.hidden=false;if(st)st.textContent='Checking for updates…';
    try{if(window.Android&&Android.checkForUpdates)Android.checkForUpdates()}catch(e){if(st)st.textContent='Could not start update check.'}
  };
  var refresh=E('notificationPushRefresh');
  if(refresh)refresh.onclick=function(){
    var d=E('notificationPushDiag');if(d)d.textContent='Refreshing push registration…';
    try{if(window.Android&&Android.refreshPushRegistration)Android.refreshPushRegistration()}catch(e){}
    setTimeout(refreshState,1200);
    setTimeout(refreshState,3000);
  };
  refreshState();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind);else bind();
})();