from pathlib import Path
import sys,shutil

assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
index=assets/'index.html'
h=index.read_text(encoding='utf-8')

if 'v152-delivery.css' not in h:
    h=h.replace('<link rel="stylesheet" href="v152-ui.css">','<link rel="stylesheet" href="v152-ui.css">\n<link rel="stylesheet" href="v152-delivery.css">',1)

old='<div class="notificationSummaryActions"><button class="btn primary" id="enablePushBtn" type="button">Enable Notifications</button><button class="btn ghost" id="notificationMarkAll" type="button">Mark All Read</button><button class="btn ghost" id="notificationClear" type="button">Clear</button></div>'
new='<div class="notificationSummaryActions"><button class="btn primary" id="notificationCheckUpdates" type="button">Check for Updates</button><button class="btn primary" id="enablePushBtn" type="button">Enable Notifications</button><button class="btn ghost" id="notificationPushRefresh" type="button">Refresh Push</button><button class="btn ghost" id="notificationMarkAll" type="button">Mark All Read</button><button class="btn ghost" id="notificationClear" type="button">Clear</button></div><div class="notificationPushDiag" id="notificationPushDiag">Checking push registration…</div>'
if old not in h: raise SystemExit('notification summary actions anchor missing')
h=h.replace(old,new,1)

if 'v152-delivery.js' not in h:
    h=h.replace('<script src="v152-fixes.js"></script>','<script src="v152-fixes.js"></script>\n<script src="v152-delivery.js"></script>',1)

index.write_text(h,encoding='utf-8')
shutil.copy('ci/v152-delivery.js',assets/'v152-delivery.js')
shutil.copy('ci/v152-delivery.css',assets/'v152-delivery.css')
print('v15.2 delivery diagnostics UI patch applied')
