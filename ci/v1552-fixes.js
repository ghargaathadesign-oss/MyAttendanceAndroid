(function(){
'use strict';
function E(id){return document.getElementById(id)}

function syncThemeCard(){
  var card=E('v1551ThemeToggle');
  if(!card)return;
  var dark=document.body.classList.contains('dark-mode');
  var title=E('v1552ThemeTitle'),hint=E('v1552ThemeHint');
  if(title)title.textContent=dark?'Dark Mode':'Light Mode';
  if(hint)hint.textContent=dark?'Tap to switch to light mode':'Tap to switch to dark mode';
  card.setAttribute('aria-label',dark?'Dark mode on. Tap to switch to light mode.':'Light mode on. Tap to switch to dark mode.');
  card.setAttribute('aria-checked',dark?'true':'false');
  if(window.v1551SyncThemeToggle)try{window.v1551SyncThemeToggle()}catch(e){}
}
window.v1552SyncThemeCard=syncThemeCard;

function init(){
  syncThemeCard();
  if(document.body&&!document.body.getAttribute('data-v1552-theme-watch')){
    document.body.setAttribute('data-v1552-theme-watch','1');
    new MutationObserver(syncThemeCard).observe(document.body,{attributes:true,attributeFilter:['class']});
  }
  var card=E('v1551ThemeToggle');
  if(card)card.addEventListener('click',function(){setTimeout(syncThemeCard,45)});
  setTimeout(syncThemeCard,120);
  setTimeout(syncThemeCard,500);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();