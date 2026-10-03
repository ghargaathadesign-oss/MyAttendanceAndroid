(function(){
  'use strict';
  var lib=window.lottie||window.bodymovin;
  if(!lib||!lib.loadAnimation)return;

  var originalLoad=lib.loadAnimation.bind(lib);
  var records=[];
  var sequence=0;
  var REPLAY_DELAY=4000;

  function isDark(){return !!(document.body&&document.body.classList.contains('dark-mode'));}
  function baseName(path){path=String(path||'');var q=path.indexOf('?');if(q>=0)path=path.slice(0,q);var p=path.split('/');return p[p.length-1]||path;}
  function resolvedPath(original,forceWhite){var name=baseName(original);if(forceWhite)return 'lottie-white/'+name;if(isDark())return 'lottie-dark/'+name;return original;}
  function clearTimer(rec){if(rec.timer){clearTimeout(rec.timer);rec.timer=null;}}
  function playOnce(rec){if(!rec||!rec.anim)return;try{rec.anim.goToAndPlay(0,true)}catch(e){}}
  function scheduleNormalReplay(rec){clearTimer(rec);rec.timer=setTimeout(function(){if(!rec.container||!document.documentElement.contains(rec.container))return;playOnce(rec);},REPLAY_DELAY);}
  function attachLifecycle(rec,initialDelay){
    if(!rec.anim)return;
    rec.anim.addEventListener('DOMLoaded',function(){clearTimer(rec);rec.timer=setTimeout(function(){playOnce(rec)},Math.max(0,initialDelay||0));});
    rec.anim.addEventListener('complete',function(){if(rec.forceWhite)return;scheduleNormalReplay(rec);});
  }
  function buildAnim(rec,initialDelay){
    var cfg={},k;for(k in rec.originalCfg)cfg[k]=rec.originalCfg[k];
    cfg.container=rec.container;cfg.path=resolvedPath(rec.originalPath,rec.forceWhite);cfg.loop=false;cfg.autoplay=false;
    rec.anim=originalLoad(cfg);attachLifecycle(rec,initialDelay);
  }
  function reloadForTheme(rec){if(!rec||rec.forceWhite||!rec.container||!document.documentElement.contains(rec.container))return;clearTimer(rec);try{if(rec.anim)rec.anim.destroy()}catch(e){}buildAnim(rec,rec.delay);}
  function reloadAllForTheme(){var alive=[],i,rec;for(i=0;i<records.length;i++){rec=records[i];if(rec.container&&document.documentElement.contains(rec.container)){alive.push(rec);reloadForTheme(rec)}else{clearTimer(rec);try{if(rec.anim)rec.anim.destroy()}catch(e){}}}records=alive;}

  lib.loadAnimation=function(cfg){
    cfg=cfg||{};
    var container=cfg.container;
    var forceWhite=!!(container&&container.classList&&container.classList.contains('punchLottie'));
    var rec={container:container,forceWhite:forceWhite,originalPath:cfg.path||'',originalCfg:cfg,anim:null,timer:null,delay:(sequence++%10)*380};
    records.push(rec);buildAnim(rec,rec.delay);
    if(forceWhite&&container){
      var button=container.closest?container.closest('#punchBtn,.punchBtn'):null;
      if(button&&!button.hasAttribute('data-punch-lottie-bound')){
        button.setAttribute('data-punch-lottie-bound','1');
        button.addEventListener('click',function(){setTimeout(function(){playOnce(rec)},0);});
      }
    }
    return rec.anim;
  };
  if(window.bodymovin&&window.bodymovin!==lib)window.bodymovin.loadAnimation=lib.loadAnimation;

  function initOne(el){
    if(!el||!el.getAttribute||el.getAttribute('data-lottie-ready')==='1')return;
    var path=el.getAttribute('data-lottie');if(!path)return;
    el.setAttribute('data-lottie-ready','1');
    try{lib.loadAnimation({container:el,renderer:'svg',loop:false,autoplay:false,path:path});}
    catch(e){el.removeAttribute('data-lottie-ready');}
  }
  window.initLottie=function(root){
    root=root||document;
    var list=[],i;
    if(root.nodeType===1&&root.getAttribute&&root.getAttribute('data-lottie'))list.push(root);
    if(root.querySelectorAll){var q=root.querySelectorAll('[data-lottie]');for(i=0;i<q.length;i++)list.push(q[i]);}
    for(i=0;i<list.length;i++)initOne(list[i]);
  };

  function observeTheme(){
    if(!document.body)return;
    var lastDark=isDark(),themeTimer=null;
    new MutationObserver(function(){var nowDark=isDark();if(nowDark===lastDark)return;lastDark=nowDark;clearTimeout(themeTimer);themeTimer=setTimeout(reloadAllForTheme,30);}).observe(document.body,{attributes:true,attributeFilter:['class']});
  }
  function start(){observeTheme();window.initLottie(document);new MutationObserver(function(ms){var i,j,n;for(i=0;i<ms.length;i++)for(j=0;j<ms[i].addedNodes.length;j++){n=ms[i].addedNodes[j];if(n&&n.nodeType===1)window.initLottie(n);}}).observe(document.body,{childList:true,subtree:true});}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();
