(function(){
  'use strict';
  var lib=window.lottie||window.bodymovin;
  if(!lib||!lib.loadAnimation)return;

  var originalLoad=lib.loadAnimation.bind(lib);
  var instances=[];
  var sequence=0;

  function isBlack(v){
    if(!v)return false;
    v=String(v).toLowerCase().replace(/\s+/g,'');
    if(v==='black'||v==='#000'||v==='#000000'||v==='rgb(0,0,0)'||v==='rgba(0,0,0,1)')return true;
    var m=v.match(/^rgb\((\d+),(\d+),(\d+)\)$/);
    if(m)return (+m[1]<=18&&+m[2]<=18&&+m[3]<=18);
    m=v.match(/^rgba\((\d+),(\d+),(\d+),([\d.]+)\)$/);
    if(m)return (+m[1]<=18&&+m[2]<=18&&+m[3]<=18&&+m[4]>0);
    return false;
  }

  function rememberAndSet(el,prop,value){
    var attr=el.getAttribute(prop),styleVal=el.style&&el.style[prop] ? el.style[prop] : '';
    if(!el.hasAttribute('data-lottie-orig-'+prop)){
      el.setAttribute('data-lottie-orig-'+prop, attr===null ? '__NULL__' : attr);
      el.setAttribute('data-lottie-orig-style-'+prop, styleVal||'__EMPTY__');
    }
    el.setAttribute(prop,value);
    if(el.style)el.style[prop]=value;
  }

  function restore(el,prop){
    var a='data-lottie-orig-'+prop,sa='data-lottie-orig-style-'+prop;
    if(!el.hasAttribute(a))return;
    var old=el.getAttribute(a),oldStyle=el.getAttribute(sa);
    if(old==='__NULL__')el.removeAttribute(prop);else el.setAttribute(prop,old);
    if(el.style)el.style[prop]=(oldStyle==='__EMPTY__'?'':oldStyle);
    el.removeAttribute(a);el.removeAttribute(sa);
  }

  function paint(container,forceWhite){
    if(!container)return;
    var dark=document.body.classList.contains('dark-mode');
    var nodes=container.querySelectorAll('path,rect,circle,ellipse,polygon,polyline,line,g');
    for(var i=0;i<nodes.length;i++){
      var el=nodes[i],fill=el.getAttribute('fill')||(el.style?el.style.fill:''),stroke=el.getAttribute('stroke')||(el.style?el.style.stroke:'');
      if(forceWhite){
        if(fill&&fill!=='none'&&fill!=='transparent')rememberAndSet(el,'fill','#ffffff');
        if(stroke&&stroke!=='none'&&stroke!=='transparent')rememberAndSet(el,'stroke','#ffffff');
      }else if(dark){
        if(isBlack(fill))rememberAndSet(el,'fill','#ffffff');else if(el.hasAttribute('data-lottie-orig-fill'))restore(el,'fill');
        if(isBlack(stroke))rememberAndSet(el,'stroke','#ffffff');else if(el.hasAttribute('data-lottie-orig-stroke'))restore(el,'stroke');
      }else{
        restore(el,'fill');restore(el,'stroke');
      }
    }
  }

  function repaintAll(){
    for(var i=0;i<instances.length;i++)paint(instances[i].container,instances[i].forceWhite);
  }

  function schedule(anim,delay){
    var stopped=false,timer=null;
    function play(){
      if(stopped)return;
      try{anim.goToAndPlay(0,true)}catch(e){}
    }
    function queue(){
      if(stopped)return;
      clearTimeout(timer);
      timer=setTimeout(play,5000);
    }
    anim.addEventListener('complete',queue);
    timer=setTimeout(play,delay);
    anim.__stopStagger=function(){stopped=true;clearTimeout(timer)};
  }

  lib.loadAnimation=function(cfg){
    cfg=cfg||{};
    var container=cfg.container;
    var forceWhite=!!(container&&container.classList&&container.classList.contains('punchLottie'));
    cfg.loop=false;
    cfg.autoplay=false;
    var anim=originalLoad(cfg);
    var idx=sequence++;
    var delay=(idx%10)*500;
    instances.push({anim:anim,container:container,forceWhite:forceWhite});
    anim.addEventListener('DOMLoaded',function(){paint(container,forceWhite);schedule(anim,delay)});
    anim.addEventListener('enterFrame',function(){paint(container,forceWhite)});
    return anim;
  };
  if(window.bodymovin&&window.bodymovin!==lib)window.bodymovin.loadAnimation=lib.loadAnimation;

  function observeTheme(){
    if(!document.body)return;
    new MutationObserver(function(){repaintAll()}).observe(document.body,{attributes:true,attributeFilter:['class']});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',observeTheme);else observeTheme();
})();
