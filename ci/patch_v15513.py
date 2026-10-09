from pathlib import Path
import shutil,sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
p=assets/'lottie-runtime.js'
s=p.read_text()
anchor='    var container=cfg.container;'
replacement='''    var container=cfg.container;
    if(container&&container.classList&&container.classList.contains('v154BootLottie')){
      var bootCfg=Object.assign({},cfg,{loop:true,autoplay:true,rendererSettings:{preserveAspectRatio:'xMidYMid meet'}});
      var bootAnim=originalLoad(bootCfg);
      container._attendanceBootAnimation=bootAnim;
      bootAnim.addEventListener('DOMLoaded',function(){
        container.classList.add('bootAnimationReady');
        try{bootAnim.goToAndPlay(12,true)}catch(e){}
      });
      bootAnim.addEventListener('data_failed',function(){container.classList.remove('bootAnimationReady')});
      return bootAnim;
    }'''
if anchor not in s:raise SystemExit('Lottie container anchor missing')
p.write_text(s.replace(anchor,replacement,1))
p=assets/'v154-ui.js';s=p.read_text()
anchor="  b.classList.add('hide');setTimeout(function(){if(b&&b.parentNode)b.parentNode.removeChild(b)},240);"
replacement="""  b.classList.add('hide');setTimeout(function(){
    var loader=b.querySelector('.v154BootLottie');
    try{if(loader&&loader._attendanceBootAnimation)loader._attendanceBootAnimation.destroy()}catch(e){}
    if(b&&b.parentNode)b.parentNode.removeChild(b);
  },240);"""
if anchor not in s:raise SystemExit('Boot cleanup anchor missing')
p.write_text(s.replace(anchor,replacement,1))
p=assets/'index.html';s=p.read_text().replace('</head>','<link rel="stylesheet" href="v15513-startup.css">\n</head>',1);p.write_text(s)
shutil.copy('ci/v15513-startup.css',assets/'v15513-startup.css')
print('v15.5.13 immediate full-width startup animation prepared')
