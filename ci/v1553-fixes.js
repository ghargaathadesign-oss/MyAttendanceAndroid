(function(){
'use strict';
function E(id){return document.getElementById(id)}
function toggleFromJson(){
  var dark=document.body.classList.contains('dark-mode');
  var target=E(dark?'themeLight':'themeDark');
  if(target&&typeof target.click==='function'){
    target.click();
  }else{
    try{localStorage.setItem('attendance_theme_v8',dark?'light':'dark')}catch(e){}
    document.body.classList.toggle('dark-mode',!dark);
  }
  setTimeout(function(){
    if(window.v1551SyncThemeToggle)try{window.v1551SyncThemeToggle()}catch(e){}
    if(window.v1552SyncThemeCard)try{window.v1552SyncThemeCard()}catch(e){}
  },35);
}
function init(){
  var icon=document.querySelector('#v1551ThemeToggle .v155ThemeLottie');
  if(icon&&!icon.getAttribute('data-v1553-bound')){
    icon.setAttribute('data-v1553-bound','1');
    icon.addEventListener('click',function(e){
      e.preventDefault();
      e.stopPropagation();
      toggleFromJson();
    });
  }
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();