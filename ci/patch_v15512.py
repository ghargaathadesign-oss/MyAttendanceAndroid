from pathlib import Path
import re,sys,json,copy,shutil
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
h=(p/'index.html').read_text();s=(p/'app.js').read_text();v=(p/'v15511-updates.js').read_text()
def rep(src,old,new):
 if old not in src:raise SystemExit('Missing v15.5.12 anchor: '+old[:100])
 return src.replace(old,new,1)
def icon(paths):return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+paths+'</svg>'
icons=[icon('<rect x="4" y="5" width="16" height="16" rx="3"/><path d="M8 3v4m8-4v4M4 11h16M10 15h4m-2-2v4"/>'),icon('<circle cx="12" cy="12" r="9"/><path d="M8 12h8m-4-4 4 4-4 4"/>'),icon('<path d="M6 3h8l4 4v14H6zM14 3v5h4m-8 6h6m-3-3v6"/>'),icon('<rect x="4" y="5" width="16" height="16" rx="3"/><path d="M8 3v4m8-4v4M4 11h16m-8 5 2 2 4-4"/>')]
start=h.index('      <div class="leaveCard">',h.index('id="screen-leaves"'));end=h.index('    </section>',start)
body='''      <div class="friendlyLeaveMonth"><button id="leavesPrevMonth" type="button" aria-label="Previous leave month">‹</button><b id="leavesMonthLabel">October 2026</b><button id="leavesNextMonth" type="button" aria-label="Next leave month">›</button></div>
      <section class="friendlyLeaveHero" aria-label="Available leave"><span class="friendlyLeaveLabel">Available Leave</span><b id="leaveBalance">0</b><span class="friendlyLeaveUnit">days</span><small id="leaveBalanceCaption">Ready to use this month</small><svg class="friendlyHeroLeaf" viewBox="0 0 90 100" fill="none" aria-hidden="true"><path d="M15 83C7 35 34 22 77 12c8 39-1 61-35 69" fill="currentColor" opacity=".12"/><path d="M23 87c-9-39 9-52 47-64 7 31-2 54-36 59M24 93c9-26 20-40 36-52" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg></section>
      <div class="friendlyLeaveGrid">'''
for label,id,hint,i in [('This Month','leaveMonthly','Monthly allowance',0),('Carried Forward','leaveCarry','Unused from last month',1),('Additional Granted','leaveGranted','Extra approved leave remaining',2),('Used This Month','leaveMonthlyUsed','Paid leave taken',3)]:
 body+='<section class="friendlyLeaveCard"><span class="friendlyLeaveIcon">'+icons[i]+'</span><small class="friendlyLeaveCardLabel">'+label+'</small><b id="'+id+'">0 days</b><small class="friendlyLeaveCardHint">'+hint+'</small></section>'
body+='''</div><div class="friendlyLeaveNote"><span aria-hidden="true">ⓘ</span><p><span id="leavePolicyNote">You get 1.5 days each month.</span><br>Unused leave carries forward.</p></div>
      <div class="friendlyLeaveAnnual"><span>Annual allowance: <b id="leaveAnnual">18 days</b></span><button id="friendlyLeaveSettings" type="button">⚙ Leave Settings</button></div>
      <section class="friendlyLeaveHistory"><div class="overviewHead"><b>Recent Leave</b><span id="leaveYear"></span></div><div id="leaveRecords"></div></section>
      <div hidden aria-hidden="true"><div id="leaveRing"></div><b id="leaveAccrued"></b><b id="leaveUsed"></b><div id="leaveTypes"></div><p id="leaveAllowanceInfo"></p></div>
'''
h=h[:start]+body+h[end:]
old='<div class="field"><input id="settingsSearch" type="search" placeholder="Search settings" aria-label="Search settings"></div><p id="settingsSearchEmpty" class="helpText" hidden>No matching settings.</p>'
new='<div class="settingsSearchPanel"><div class="settingsSearchField"><span class="settingsSearchLottie lottieIcon" data-lottie="lottie/search-v15512.json" aria-hidden="true"></span><input id="settingsSearch" type="search" placeholder="Search settings" aria-label="Search settings"></div><p id="settingsSearchEmpty" class="helpText" hidden>No matching settings.</p></div>'
h=rep(h,old,new);h=rep(h,'</head>','<link rel="stylesheet" href="v15512-ui.css">\n</head>');h=rep(h,'</body>','<script src="v15512-leaves.js"></script>\n</body>')
s=rep(s,'function renderLeaves(){','function renderLeaves(){\n if(window.renderFriendlyLeaves){window.renderFriendlyLeaves();return}')
old=" var html='<section><small>Remaining Time</small><b>'+hm(left)+'</b></section><section><small>Passed Time</small><b>'+hm(elapsed)+'</b></section>';if(el.innerHTML!==html)el.innerHTML=html;"
new=""" if(!E('homeTimeRemaining')){el.innerHTML='<section><span class="v15512Hourglass lottieIcon" data-lottie="lottie/hourglass-v15512.json" aria-hidden="true"></span><span class="punchTimeCopy"><b id="homeTimeRemaining"></b><small>Remaining Time</small></span></section><section><span class="v15512Hourglass lottieIcon" data-lottie="lottie/hourglass-v15512.json" aria-hidden="true"></span><span class="punchTimeCopy"><b id="homeTimePassed"></b><small>Passed Time</small></span></section>';if(window.initLottie)window.initLottie(el)}
 E('homeTimeRemaining').textContent=hm(left);E('homeTimePassed').textContent=hm(elapsed);"""
v=rep(v,old,new)
for name,text in [('index.html',h),('app.js',s),('v15511-updates.js',v)]: (p/name).write_text(text)
for name in ['v15512-ui.css','v15512-leaves.js']:shutil.copy(Path('ci')/name,p/name)
# Keep supplied light-theme animation artwork exact. Theme variants preserve animation geometry.
def recolor(obj,rgb):
 if isinstance(obj,dict):
  if obj.get('ty') in ('fl','st') and isinstance(obj.get('c'),dict):
   c=obj['c']
   if c.get('a')==0:c['k']=rgb+[1]
   elif isinstance(c.get('k'),list):
    for f in c['k']:
     for k in ('s','e'):
      if k in f:f[k]=rgb+[1]
  for child in obj.values():recolor(child,rgb)
 elif isinstance(obj,list):
  for child in obj:recolor(child,rgb)
for source in (Path('ci')/'v15512-lottie').glob('*.json'):
 obj=json.loads(source.read_text())
 for folder,rgb in [('lottie',None),('lottie-dark',[.85,.94,.97]),('lottie-white',[1,1,1])]:
  (p/folder).mkdir(exist_ok=True);variant=copy.deepcopy(obj)
  if rgb:recolor(variant,rgb)
  (p/folder/source.name).write_text(json.dumps(variant,separators=(',',':')))
print('v15.5.12 approved Leaves, compact time cards and Settings search applied')
