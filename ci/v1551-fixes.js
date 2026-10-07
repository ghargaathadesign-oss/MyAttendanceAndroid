(function(){
'use strict';
function E(id){return document.getElementById(id)}
function api(){return window.AttendanceAppApi||{}}

function syncThemeToggle(){
  var el=E('v1551ThemeToggle'),anim=document.querySelector('.v155ThemeLottie');
  if(!el)return;
  var dark=document.body.classList.contains('dark-mode');
  el.setAttribute('aria-checked',dark?'true':'false');
  el.setAttribute('aria-label',dark?'Dark mode on. Tap for light mode.':'Light mode on. Tap for dark mode.');
  if(anim&&anim._attendanceLottie){
    try{
      var total=Math.max(1,Math.floor(anim._attendanceLottie.totalFrames||96));
      anim._attendanceLottie.goToAndStop(dark?total-1:0,true);
    }catch(e){}
  }
}
window.v1551SyncThemeToggle=syncThemeToggle;

function toggleTheme(){
  var dark=document.body.classList.contains('dark-mode');
  var target=E(dark?'themeLight':'themeDark');
  if(target&&typeof target.click==='function')target.click();
  else{
    try{localStorage.setItem('attendance_theme_v8',dark?'light':'dark')}catch(e){}
    document.body.classList.toggle('dark-mode',!dark);
  }
  setTimeout(syncThemeToggle,30);
}

function bindTheme(){
  var t=E('v1551ThemeToggle');
  if(t&&!t.getAttribute('data-v1551-bound')){
    t.setAttribute('data-v1551-bound','1');
    t.addEventListener('click',function(e){e.preventDefault();toggleTheme()});
    t.addEventListener('keydown',function(e){
      if(e.key==='Enter'||e.key===' '){e.preventDefault();toggleTheme()}
    });
  }
  syncThemeToggle();
  if(document.body&&!document.body.getAttribute('data-v1551-theme-watch')){
    document.body.setAttribute('data-v1551-theme-watch','1');
    new MutationObserver(syncThemeToggle).observe(document.body,{attributes:true,attributeFilter:['class']});
  }
}

function handleEditControls(e){
  var b=e.target&&e.target.closest?e.target.closest('#editClose,#editCancel,#editSave,#editPopupDelete'):null;
  if(!b)return;
  var A=api();
  if(b.id==='editClose'||b.id==='editCancel'){
    if(typeof A.closeEdit==='function'){
      e.preventDefault();e.stopImmediatePropagation();A.closeEdit();
    }
    return;
  }
  if(b.id==='editSave'){
    if(typeof A.saveEdit==='function'){
      e.preventDefault();e.stopImmediatePropagation();A.saveEdit();
    }
    return;
  }
  if(b.id==='editPopupDelete'){
    var id=E('editPopupId')?E('editPopupId').value:'';
    if(id&&typeof A.deleteRecord==='function'){
      e.preventDefault();e.stopImmediatePropagation();A.deleteRecord(id);
    }
  }
}

function init(){
  bindTheme();
  document.addEventListener('click',handleEditControls,true);
  setTimeout(syncThemeToggle,80);
  setTimeout(syncThemeToggle,450);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();