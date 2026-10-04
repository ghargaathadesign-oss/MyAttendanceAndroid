from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/java/com/personal/attendance/MainActivity.java')
s=p.read_text(encoding='utf-8')

bridge_anchor='    @JavascriptInterface public void secureClearPrefix(String prefix){MainActivity.this.secureStoreClearPrefix(prefix);}\n'
bridge='''    @JavascriptInterface public String secureEncryptValue(String context,String value){
      try{return MainActivity.this.secureEncrypt("value:"+String.valueOf(context),value);}
      catch(Exception e){return null;}
    }
    @JavascriptInterface public String secureDecryptValue(String context,String packed){
      try{return MainActivity.this.secureDecrypt("value:"+String.valueOf(context),packed);}
      catch(Exception e){return null;}
    }
'''
if bridge.strip() not in s:
    if bridge_anchor not in s: raise SystemExit('secure bridge anchor missing')
    s=s.replace(bridge_anchor,bridge_anchor+bridge,1)

p.write_text(s,encoding='utf-8')
print('v12.4 secure value crypto bridge applied')
