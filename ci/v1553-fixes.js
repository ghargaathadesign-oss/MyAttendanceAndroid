(function(){
'use strict';
function E(id){return document.getElementById(id)}
function updateThemeUi(){
  if(window.v1551SyncThemeToggle)try{window.v1551SyncThemeToggle()}catch(e){}
  if(window.v1552SyncThemeCard)try{window.v1552SyncThemeCard()}catch(e){}
}
function bindDirectThemeTouch(){
  var art=document.querySelector('#v1551ThemeToggle .v155ThemeLottie');
  if(!art||art.dataset.v1553Bound==='1')return;
  art.dataset.v1553Bound='1';
  art.setAttribute('title','Tap to switch between light and dark mode');
  art.addEventListener('click',function(e){
    /* Do not bubble into the existing whole-card toggle and switch twice. */
    e.preventDefault();
    e.stopPropagation();
    var dark=document.body.classList.contains('dark-mode');
    var proxy=E(dark?'themeLight':'themeDark');
    if(proxy)proxy.click();
    updateThemeUi();
    if(window.requestAnimationFrame)requestAnimationFrame(updateThemeUi);
  },false);
}
function fitBootSvg(){
  var wrap=E('v154BootScreen');
  if(!wrap)return;
  var canvas=wrap.querySelector('.v154BootLottie'),svg=canvas&&canvas.querySelector('svg');
  if(!svg)return;
  /* Original 1920x1080 artwork reaches outside its source canvas.
     Fit its actual drawing bounds instead of zooming by an arbitrary factor. */
  svg.setAttribute('viewBox','-460 290 2840 580');
  svg.setAttribute('preserveAspectRatio','xMidYMid meet');
}
function init(){
  bindDirectThemeTouch();
  fitBootSvg();
  if(window.MutationObserver){
    var wrap=E('v154BootScreen');
    if(wrap){
      var observer=new MutationObserver(function(){fitBootSvg()});
      observer.observe(wrap,{childList:true,subtree:true});
      setTimeout(function(){observer.disconnect()},6000);
    }
  }
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();