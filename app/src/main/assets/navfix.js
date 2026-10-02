(function(){
  function findParentWithAttr(node,attr,value){
    while(node&&node!==document.body){
      if(node.getAttribute&&node.getAttribute(attr)===value)return node;
      node=node.parentNode;
    }
    return null;
  }
  function returnSettingsToHub(){
    setTimeout(function(){
      var hub=document.getElementById('settingsHub');
      if(hub&&hub.style.display==='none'&&window.appBack){window.appBack();}
    },25);
  }
  document.addEventListener('click',function(e){
    if(findParentWithAttr(e.target,'data-screen','settings'))returnSettingsToHub();
  },false);
  var top=document.getElementById('topSettings');
  if(top)top.addEventListener('click',returnSettingsToHub,false);
})();
