from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text();anchor='  public class AndroidBridge{'
if anchor not in s:raise SystemExit('Android bridge anchor missing')
s=s.replace(anchor,Path('ci/v15515-native-support.java').read_text()+'\n'+anchor,1)
s=s.replace(anchor,anchor+'''
    @JavascriptInterface public void supportLoad(String thread){supportLoadNative(thread);}
    @JavascriptInterface public void supportSend(String thread,String text){supportSendNative(thread,text);}
    @JavascriptInterface public void supportClear(String thread){supportClearNative(thread);}
    @JavascriptInterface public String currentUserEmail(){FirebaseUser u=auth==null?null:auth.getCurrentUser();return u==null?"":u.getEmail();}
''',1)
s=s.replace('    AppMessagingService.ensureSubscribed(this);','    new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(()->AppMessagingService.ensureSubscribed(this),1500);')
s=s.replace('    checkForUpdatesNative(false);','    new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(()->checkForUpdatesNative(false),2500);')
p.write_text(s)
print('v15.5.15 support bridge and deferred startup network work applied')
