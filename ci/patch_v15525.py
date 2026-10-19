from pathlib import Path
import sys,shutil
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
h=(p/'index.html').read_text()
a=h.index('      <div class="overviewHead"'); b=h.index('      <section class="homeSalary21">',a)
h=h[:a]+'<section class="homeOverview25">'+h[a:b]+'</section>\n'+h[b:]
h=h.replace('</head>','<link rel="stylesheet" href="v15525-home.css"></head>',1)
(p/'index.html').write_text(h)
f=p/'v15519-reports.js';s=f.read_text();anchor='details.append(picker,output);box.appendChild(details);';assert anchor in s
s=s.replace(anchor,"if(area){var calendar=document.createElement('span');calendar.className='homeCalendar25 lottieIcon';calendar.setAttribute('data-lottie','lottie/calendar-v155.json');calendar.setAttribute('aria-hidden','true');details.appendChild(calendar)}"+anchor,1);f.write_text(s)
shutil.copy('ci/v15525-home.css',p/'v15525-home.css')
print('v15.5.25 soft Home cards and punch dropdown spacing prepared')
