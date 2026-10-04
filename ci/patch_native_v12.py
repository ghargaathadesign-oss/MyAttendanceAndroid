from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/java/com/personal/attendance/MainActivity.java')
s=p.read_text(encoding='utf-8')
anchor='    @JavascriptInterface public void googleSignIn(){runOnUiThread(() -> beginGoogleSignIn());}\n'
insert='    @JavascriptInterface public String currentUserUid(){FirebaseUser u=auth==null?null:auth.getCurrentUser();return u==null?"":u.getUid();}\n'
if anchor not in s: raise SystemExit('Android bridge anchor missing')
s=s.replace(anchor,insert+anchor,1)
p.write_text(s,encoding='utf-8')
print('v12 native user identity bridge applied')
