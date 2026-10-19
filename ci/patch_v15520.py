from pathlib import Path
import sys,shutil
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
h=(p/'index.html').read_text()
h=h.replace('6-MONTH WORKING HOURS TREND','Working hours trend').replace('MONTHLY IN / OUT TIMES','Daily rhythm')
h=h.replace('Required vs worked hours for recorded days. Future records are excluded.','Required vs worked hours · Last six months · Recorded days only')
h=h.replace('Swipe to view all dates. Missing punches are gaps. Overnight out times show +1 day.','Your in and out times at a glance. Recorded punch days only; +1 day means the following day.')
h=h.replace('</head>','<link rel="stylesheet" href="v15520-ui.css"></head>',1).replace('</body>','<script src="v15520-ui.js"></script></body>',1)
(p/'index.html').write_text(h)
for name in ['v15520-ui.js','v15520-ui.css']:shutil.copy(Path('ci')/name,p/name)
print('v15.5.20 compact Salary info, polished Reports and branded invite sharing prepared')
