from pathlib import Path
import sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
p=assets/'index.html'
s=p.read_text(encoding='utf-8')

logout='''        <button class="settingsLogoutRow" id="settingsLogoutBtn" type="button"><span class="logoutGlyph" aria-hidden="true">↪</span><span><b>Log Out</b><small>Sign out of My Attendance</small></span><i>›</i></button>'''
diagrow='''        <button class="settingsMenuRow" data-setting="diagnostics"><span class="menuLottie lottieIcon" data-lottie="lottie/settings.json"></span><span><b>Diagnostics & Recovery</b><small>Health checks, safe repair and support report</small></span><i>›</i></button>
'''+logout
if logout not in s: raise SystemExit('settings logout anchor missing')
s=s.replace(logout,diagrow,1)

end='''    </section>
  </main>
</div>

<div class="toast" id="toast"></div>'''
section='''    </section>

    <section class="screen settingScreen" id="screen-setting-diagnostics">
      <div class="sectionHeader"><button class="back settingBack" type="button">‹</button><span class="pageLottie lottieIcon" data-lottie="lottie/settings.json"></span><h1>Diagnostics & Recovery</h1></div>
      <div id="diagnosticsSummary" class="diagSummary diagWarn"><div class="diagShield">•</div><div><b>Ready to check</b><small>Run a health check for security, storage and backups.</small></div></div>

      <div class="diagSectionTitle">APP & RELEASE</div>
      <div class="diagCard" id="diagAppCard"></div>

      <div class="diagSectionTitle">SECURITY</div>
      <div class="diagCard" id="diagSecurityCard"></div>

      <div class="diagSectionTitle">LOCAL DATA</div>
      <div class="diagCard" id="diagDataCard"></div>

      <div class="diagSectionTitle">CLOUD BACKUP</div>
      <div class="diagCard" id="diagCloudCard"></div>

      <div id="diagNotes"></div>

      <div class="settingsCard">
        <div class="diagActions">
          <button class="btn primary" id="diagRunBtn" type="button">Run Health Check</button>
          <button class="btn ghost" id="diagRepairBtn" type="button">Repair Compatible Data</button>
          <button class="btn ghost" id="diagBackupBtn" type="button">Backup & Restore</button>
          <button class="btn ghost" id="diagClearCacheBtn" type="button">Clear Temporary Cache</button>
          <button class="btn ghost full" id="diagReportBtn" type="button">Export Support Report</button>
        </div>
        <p class="diagPrivacy">The support report contains technical status only. It excludes your email, Firebase UID, salary amount, attendance notes, document contents, passwords, phone PIN/biometrics, Firebase API keys and Transfer PIN.</p>
      </div>
    </section>
  </main>
</div>

<div class="toast" id="toast"></div>'''
if end not in s: raise SystemExit('main closing anchor missing')
s=s.replace(end,section,1)

if '<link rel="stylesheet" href="diagnostics-ui.css">' not in s:
    s=s.replace('</head>','<link rel="stylesheet" href="diagnostics-ui.css">\n</head>',1)
if '<script src="diagnostics-core.js"></script>' not in s:
    s=s.replace('<script src="cloud-ui.js"></script>','<script src="cloud-ui.js"></script>\n<script src="diagnostics-core.js"></script>\n<script src="diagnostics-ui.js"></script>',1)

p.write_text(s,encoding='utf-8')
print('v13.1 diagnostics screen patch applied')
