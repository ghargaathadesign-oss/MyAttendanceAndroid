from pathlib import Path
import re,sys,shutil,json,copy
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
def rep(s,a,b):
 if a not in s:raise SystemExit('Missing v15516 anchor: '+a[:85])
 return s.replace(a,b,1)
h=(p/'index.html').read_text()
rows={}
for key in ['policy','help']:
 pattern=r'<button class="settingsMenuRow" data-setting="'+key+r'">.*?</button>'
 match=re.search(pattern,h,re.S)
 if not match:raise SystemExit('Settings row missing '+key)
 rows[key]=match.group();h=h[:match.start()]+h[match.end():]
h=rep(h,'<button class="settingsLogoutRow"',rows['policy']+rows['help']+'<button class="settingsLogoutRow"')
h=h.replace('Privacy &amp; App Lock','Security')
for key,file in [('language','language-v15516.json'),('policy','policy-v15516.json'),('help','privacy-v155.json')]:
 pattern=r'(<button class="settingsMenuRow" data-setting="'+key+r'">)<span[^>]*>.*?</span>'
 h,n=re.subn(pattern,r'\1<span class="menuLottie lottieIcon" data-lottie="lottie/'+file+'" aria-hidden="true"></span>',h,count=1,flags=re.S)
 if n!=1:raise SystemExit('Icon anchor missing '+key)
# The renamed Security row and page use the supplied new Security icon.
h=h.replace('data-lottie="lottie/privacy-v155.json"></span><span><b>Security','data-lottie="lottie/security-v15516.json"></span><span><b>Security')
h=h.replace('data-lottie="lottie/privacy-v155.json"></span><h1>Security','data-lottie="lottie/security-v15516.json"></span><h1>Security')
for key,file in [('language','language-v15516.json'),('policy','policy-v15516.json')]:
 anchor='<section class="screen settingScreen" id="screen-setting-'+key+'">'
 start=h.index(anchor);end=h.index('</section>',start)
 fragment=h[start:end];fragment=rep(fragment,'</button><h1>','</button><span class="pageLottie lottieIcon" data-lottie="lottie/'+file+'" aria-hidden="true"></span><h1>');h=h[:start]+fragment+h[end:]
start=h.index('<section class="screen settingScreen" id="screen-setting-help">');end=h.index('</section>',start)+len('</section>')
h=h[:start]+Path('ci/v15516-help.html').read_text()+h[end:]
bootstrap='''<script>
(function(){
 var state=null;
 try{if(window.Android&&Android.authSnapshot)state=JSON.parse(String(Android.authSnapshot()))}catch(e){}
 window.attendanceInitialAuth=state;
 document.documentElement.classList.toggle('sessionVerified',!!(state&&state.signedIn&&state.emailVerified));
})();
</script>
'''
h=rep(h,'</head>','<link rel="stylesheet" href="v15516-ui.css">\n'+bootstrap+'</head>')
(p/'index.html').write_text(h)
c=p/'cloud-ui.js';s=c.read_text()
s=rep(s,"var signed=!!user.signedIn,verified=!!user.emailVerified,expected=", "var signed=!!user.signedIn,verified=!!user.emailVerified,expected=") if "var signed=!!user.signedIn" in s else s
s=rep(s,"function account(u){user=u||{};","function account(u){user=u||{};document.documentElement.classList.toggle('sessionVerified',!!(user.signedIn&&user.emailVerified));")
s=rep(s,"setMode('login');if(window.Android&&Android.authState)Android.authState()","setMode('login');if(window.attendanceInitialAuth)account(window.attendanceInitialAuth);if(window.Android&&Android.authState)Android.authState()")
c.write_text(s)
shutil.copy('ci/v15516-support.js',p/'v15515-support.js');shutil.copy('ci/v15516-ui.css',p/'v15516-ui.css')
# Preserve the supplied geometry; create matching dark and white color variants.
def recolor(node,color):
 if isinstance(node,dict):
  if node.get('ty') in ['fl','st'] and isinstance(node.get('c'),dict) and node['c'].get('a')==0:node['c']['k']=color
  if node.get('ty')==2 and isinstance(node.get('v'),dict) and isinstance(node['v'].get('k'),list) and len(node['v']['k'])==4:node['v']['k']=color
  for v in node.values():recolor(v,color)
 elif isinstance(node,list):
  for v in node:recolor(v,color)
for source in Path('ci/v15516-lottie').glob('*.json'):
 data=json.loads(source.read_text())
 for folder,color in [('lottie',None),('lottie-dark',[.82,.88,.94,1]),('lottie-white',[1,1,1,1])]:
  variant=copy.deepcopy(data)
  if color:recolor(variant,color)
  (p/folder/source.name).write_text(json.dumps(variant,separators=(',',':')))
print('v15.5.16 settings order, supplied icons, flash-free session and Help tabs prepared')
