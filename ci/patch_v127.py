from pathlib import Path
import sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
p=assets/'index.html'
s=p.read_text(encoding='utf-8')
old='''        <div class="label">Backup Recovery Password</div><div class="field"><input id="backupRecoveryPassword" type="password" minlength="8" autocomplete="new-password" placeholder="Enter 8+ character recovery password"></div>
        <button class="btn ghost fullBtn" id="saveBackupRecoveryBtn" type="button">Save Recovery Password</button>
        <small class="cloudStatus" id="backupRecoveryState">Set a recovery password before creating a new encrypted backup.</small>
        <div class="cloudActions"><button class="btn primary" id="cloudBackupBtn" type="button">Backup Now</button><button class="btn ghost" id="cloudRestoreBtn" type="button">Restore</button><button class="btn ghost cloudSignOut" id="cloudSignOutBtn" type="button">Sign Out</button></div>
        <small class="cloudStatus" id="cloudStatus">End-to-end encrypted backup. Your recovery password is not uploaded to Firebase.</small>'''
new='''        <p class="helpText">Protected by your phone security. Backup and Restore will ask for your fingerprint, face, PIN, pattern or device password.</p>
        <div class="cloudActions"><button class="btn primary" id="cloudBackupBtn" type="button">Backup Now</button><button class="btn ghost" id="cloudRestoreBtn" type="button">Restore</button><button class="btn ghost cloudSignOut" id="cloudSignOutBtn" type="button">Sign Out</button></div>
        <small class="cloudStatus" id="cloudStatus">Ready. Your backup is protected by this device.</small>'''
if old not in s: raise SystemExit('v12.7 backup UI anchor missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('v12.7 device-security backup UI patch applied')
