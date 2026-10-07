(function(){
'use strict';
function E(id){return document.getElementById(id)}
function addDeleteButton(){
  if(E('editPopupDelete'))return;
  var modal=E('editModal');if(!modal)return;
  var actions=modal.querySelector('.actions');if(!actions)return;
  var b=document.createElement('button');
  b.type='button';b.id='editPopupDelete';b.className='btn dangerOutline';b.textContent='Delete Attendance';
  actions.parentNode.insertBefore(b,actions.nextSibling);
  b.onclick=function(){
    var id=E('editPopupId')?E('editPopupId').value:'';
    var A=window.AttendanceAppApi;
    if(id&&A&&A.deleteRecord)A.deleteRecord(id);
  };
}
function syncProfileExtra(){
  var p={};try{p=JSON.parse(localStorage.getItem('attendance_profile_v81')||'{}')||{}}catch(e){}
  var extra=E('profileCardExtra'),parts=[];
  if(p.department)parts.push(p.department);
  if(p.employeeId)parts.push('ID '+p.employeeId);
  if(extra)extra.textContent=parts.join(' • ');
}
function hideBoot(){
  var b=E('v154BootScreen');if(!b)return;
  b.classList.add('hide');setTimeout(function(){if(b&&b.parentNode)b.parentNode.removeChild(b)},240);
}
window.v154AppReady=hideBoot;
function init(){
  addDeleteButton();
  syncProfileExtra();
  var save=E('saveProfile');if(save)save.addEventListener('click',function(){setTimeout(syncProfileExtra,60)});
  setTimeout(function(){var b=E('v154BootScreen');if(b)hideBoot()},5000);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();