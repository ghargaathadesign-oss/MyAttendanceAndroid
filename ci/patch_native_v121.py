from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/java/com/personal/attendance/MainActivity.java')
s=p.read_text(encoding='utf-8')

imports='''import com.google.firebase.appcheck.FirebaseAppCheck;
import com.google.firebase.appcheck.playintegrity.PlayIntegrityAppCheckProviderFactory;
'''
anchor='import com.google.firebase.auth.AuthCredential;\n'
if imports.strip() not in s:
    if anchor not in s: raise SystemExit('Firebase auth import anchor missing')
    s=s.replace(anchor,imports+anchor,1)

old='''      auth=FirebaseAuth.getInstance();
      cloudStorage=FirebaseStorage.getInstance();
      firebaseInitError="";'''
new='''      FirebaseAppCheck.getInstance().installAppCheckProviderFactory(
        PlayIntegrityAppCheckProviderFactory.getInstance()
      );
      auth=FirebaseAuth.getInstance();
      cloudStorage=FirebaseStorage.getInstance();
      firebaseInitError="";'''
if old not in s: raise SystemExit('Firebase initialization anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('v12.1 Firebase App Check Play Integrity patch applied')
