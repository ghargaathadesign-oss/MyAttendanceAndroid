from pathlib import Path
import re, sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/java/com/personal/attendance/MainActivity.java')
s=p.read_text(encoding='utf-8')

if 'import android.app.KeyguardManager;' not in s:
    s=s.replace('import android.app.Activity;\n','import android.app.Activity;\nimport android.app.KeyguardManager;\n',1)
if 'import androidx.biometric.BiometricManager;' not in s:
    s=s.replace('import androidx.core.content.ContextCompat;\n','import androidx.biometric.BiometricManager;\nimport androidx.biometric.BiometricPrompt;\nimport androidx.core.content.ContextCompat;\n',1)
if 'import androidx.fragment.app.FragmentActivity;' not in s:
    s=s.replace('import androidx.credentials.exceptions.GetCredentialException;\n','import androidx.credentials.exceptions.GetCredentialException;\nimport androidx.fragment.app.FragmentActivity;\n',1)
if 'import java.util.function.Consumer;' not in s:
    s=s.replace('import java.util.Map;\n','import java.util.Map;\nimport java.util.function.Consumer;\n',1)

s=s.replace('public class MainActivity extends Activity {','public class MainActivity extends FragmentActivity {',1)

field='  private static final String SECURE_KEY_ALIAS="my_attendance_local_aes_v1";\n'
if 'BACKUP_KEY_ALIAS_PREFIX' not in s:
    if field not in s: raise SystemExit('secure key field anchor missing')
    s=s.replace(field,field+'  private static final String BACKUP_KEY_ALIAS_PREFIX="my_attendance_cloud_backup_aes_v2_";\n',1)

old='''      FirebaseAppCheck.getInstance().installAppCheckProviderFactory(
        PlayIntegrityAppCheckProviderFactory.getInstance()
      );'''
new='''      if(BuildConfig.FIREBASE_APP_CHECK_ENABLED){
        FirebaseAppCheck.getInstance().installAppCheckProviderFactory(
          PlayIntegrityAppCheckProviderFactory.getInstance()
        );
      }'''
if old not in s: raise SystemExit('App Check init anchor missing')
s=s.replace(old,new,1)

anchor='''  private void initFirebase(){
'''
methods=r'''  private String backupKeyAlias(String uid){
    return BACKUP_KEY_ALIAS_PREFIX+String.valueOf(uid==null?"":uid).replaceAll("[^A-Za-z0-9_-]","_");
  }

  private SecretKey backupSecretKey(String uid,boolean create) throws Exception{
    String alias=backupKeyAlias(uid);
    KeyStore keyStore=KeyStore.getInstance("AndroidKeyStore");
    keyStore.load(null);
    if(!keyStore.containsAlias(alias)){
      if(!create)throw new IllegalStateException("This device does not have the key for this backup.");
      KeyGenerator generator=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
      KeyGenParameterSpec.Builder b=new KeyGenParameterSpec.Builder(
        alias,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT
      ).setBlockModes(KeyProperties.BLOCK_MODE_GCM)
       .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
       .setKeySize(256)
       .setUserAuthenticationRequired(true);
      if(Build.VERSION.SDK_INT>=30){
        b.setUserAuthenticationParameters(60,KeyProperties.AUTH_BIOMETRIC_STRONG|KeyProperties.AUTH_DEVICE_CREDENTIAL);
      }else{
        b.setUserAuthenticationValidityDurationSeconds(60);
      }
      generator.init(b.build());
      return generator.generateKey();
    }
    KeyStore.SecretKeyEntry entry=(KeyStore.SecretKeyEntry)keyStore.getEntry(alias,null);
    return entry.getSecretKey();
  }

  private boolean deviceSecurityReady(){
    KeyguardManager km=(KeyguardManager)getSystemService(KEYGUARD_SERVICE);
    return km!=null&&km.isDeviceSecure();
  }

  private void deviceAuthenticate(String title,String subtitle,Runnable success,Consumer<String> failure){
    runOnUiThread(()->{
      if(!deviceSecurityReady()){
        failure.accept("Set a PIN, pattern or device password in Android Settings first.");
        return;
      }
      BiometricPrompt prompt=new BiometricPrompt(
        MainActivity.this,
        ContextCompat.getMainExecutor(MainActivity.this),
        new BiometricPrompt.AuthenticationCallback(){
          @Override public void onAuthenticationSucceeded(BiometricPrompt.AuthenticationResult result){
            super.onAuthenticationSucceeded(result);
            new Thread(success).start();
          }
          @Override public void onAuthenticationError(int errorCode,CharSequence errString){
            super.onAuthenticationError(errorCode,errString);
            String m=errString==null?"Device verification was cancelled":errString.toString();
            failure.accept(m);
          }
          @Override public void onAuthenticationFailed(){
            super.onAuthenticationFailed();
          }
        }
      );
      BiometricPrompt.PromptInfo.Builder info=new BiometricPrompt.PromptInfo.Builder()
        .setTitle(title)
        .setSubtitle(subtitle)
        .setConfirmationRequired(false);
      if(Build.VERSION.SDK_INT>=30){
        info.setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG|BiometricManager.Authenticators.DEVICE_CREDENTIAL);
      }else{
        info.setDeviceCredentialAllowed(true);
      }
      prompt.authenticate(info.build());
    });
  }

  private byte[] backupAad(String uid){
    return ("MyAttendance|cloud-backup|v5|"+String.valueOf(uid==null?"":uid)).getBytes(StandardCharsets.UTF_8);
  }

  private String encryptDeviceBackup(String uid,String plain) throws Exception{
    Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(Cipher.ENCRYPT_MODE,backupSecretKey(uid,true));
    cipher.updateAAD(backupAad(uid));
    byte[] enc=cipher.doFinal((plain==null?"{}":plain).getBytes(StandardCharsets.UTF_8));
    JSONObject o=new JSONObject();
    o.put("version",5);
    o.put("encrypted",true);
    o.put("cipher","AES-256-GCM");
    o.put("keyProtection","AndroidKeystoreUserAuth");
    o.put("userUid",uid);
    o.put("savedAt",System.currentTimeMillis());
    o.put("iv",Base64.encodeToString(cipher.getIV(),Base64.NO_WRAP));
    o.put("ciphertext",Base64.encodeToString(enc,Base64.NO_WRAP));
    return o.toString();
  }

  private String decryptDeviceBackup(String uid,String payload) throws Exception{
    JSONObject o=new JSONObject(payload);
    if(o.optInt("version")!=5||!o.optBoolean("encrypted")||!"AES-256-GCM".equals(o.optString("cipher")))throw new IllegalArgumentException("Unsupported device backup format");
    String owner=o.optString("userUid","");
    if(!owner.isEmpty()&&!owner.equals(uid))throw new IllegalArgumentException("This backup belongs to a different account.");
    byte[] iv=Base64.decode(o.getString("iv"),Base64.NO_WRAP);
    byte[] enc=Base64.decode(o.getString("ciphertext"),Base64.NO_WRAP);
    Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(Cipher.DECRYPT_MODE,backupSecretKey(uid,false),new GCMParameterSpec(128,iv));
    cipher.updateAAD(backupAad(uid));
    return new String(cipher.doFinal(enc),StandardCharsets.UTF_8);
  }

  private void secureCloudBackup(String json){
    FirebaseUser u=auth==null?null:auth.getCurrentUser();
    if(u==null||!u.isEmailVerified()||cloudStorage==null){
      js("window.onCloudBackupResult&&window.onCloudBackupResult(false,'Please sign in with a verified account first',0);");
      return;
    }
    if(!deviceSecurityReady()){
      js("window.onCloudBackupResult&&window.onCloudBackupResult(false,'Set a phone screen lock first',0);");
      return;
    }
    try{backupSecretKey(u.getUid(),true);}catch(Exception e){
      js("window.onCloudBackupResult&&window.onCloudBackupResult(false,"+JSONObject.quote(e.getMessage()==null?"Could not create device backup key":e.getMessage())+",0);");
      return;
    }
    deviceAuthenticate(
      "Confirm backup",
      "Use fingerprint, face or your phone screen lock",
      ()->{
        try{
          String encrypted=encryptDeviceBackup(u.getUid(),json);
          cloudBackup(encrypted);
        }catch(Exception e){
          js("window.onCloudBackupResult&&window.onCloudBackupResult(false,"+JSONObject.quote(e.getMessage()==null?"Could not encrypt backup":e.getMessage())+",0);");
        }
      },
      msg->js("window.onCloudBackupResult&&window.onCloudBackupResult(false,"+JSONObject.quote(msg)+",0);")
    );
  }

  private void secureCloudRestore(){
    FirebaseUser u=auth==null?null:auth.getCurrentUser();
    if(u==null||!u.isEmailVerified()||cloudStorage==null){
      js("window.onCloudRestoreError&&window.onCloudRestoreError('Please sign in with a verified account first');");
      return;
    }
    deviceAuthenticate(
      "Confirm restore",
      "Use fingerprint, face or your phone screen lock",
      ()->cloudRestoreAfterDeviceAuth(u.getUid()),
      msg->js("window.onCloudRestoreError&&window.onCloudRestoreError("+JSONObject.quote(msg)+");")
    );
  }

  private void cloudRestoreAfterDeviceAuth(String uid){
    StorageReference ref=backupRef();
    if(ref==null){js("window.onCloudRestoreError&&window.onCloudRestoreError('Please sign in with a verified account first');");return;}
    ref.getBytes(25L*1024L*1024L).addOnSuccessListener(bytes->{
      String payload=new String(bytes,StandardCharsets.UTF_8);
      try{
        JSONObject o=new JSONObject(payload);
        if(o.optBoolean("encrypted")&&o.optInt("version")==5){
          String plain=decryptDeviceBackup(uid,payload);
          js("window.onDeviceCloudRestore&&window.onDeviceCloudRestore("+JSONObject.quote(plain)+");");
        }else{
          js("window.onCloudRestore&&window.onCloudRestore("+JSONObject.quote(payload)+");");
        }
      }catch(Exception e){
        js("window.onCloudRestoreError&&window.onCloudRestoreError("+JSONObject.quote(e.getMessage()==null?"Could not unlock backup on this device":e.getMessage())+");");
      }
    }).addOnFailureListener(e->js("window.onCloudRestoreError&&window.onCloudRestoreError("+JSONObject.quote(e.getMessage()==null?"No backup found":e.getMessage())+");"));
  }

'''
if 'private void secureCloudBackup(' not in s:
    if anchor not in s: raise SystemExit('initFirebase anchor missing')
    s=s.replace(anchor,methods+anchor,1)

# Remove the explicit App Check preflight that caused the visible 403 error.
s=re.sub(r'  private void withAppCheck\(Runnable action,java\.util\.function\.Consumer<String> fail\)\{.*?\n  \}\n\n', '', s, count=1, flags=re.S)

pat=re.compile(r'''  private void cloudBackup\(String json\)\{.*?\n  \}\n\n  private void cloudRestore\(\)\{.*?\n  \}\n''',re.S)
m=pat.search(s)
if not m: raise SystemExit('cloud backup/restore block missing')
direct='''  private void cloudBackup(String json){
    StorageReference ref=backupRef();
    if(ref==null){js("window.onCloudBackupResult&&window.onCloudBackupResult(false,'Please sign in with a verified account first',0);");return;}
    byte[] bytes=(json==null?"{}":json).getBytes(StandardCharsets.UTF_8);
    StorageMetadata meta=new StorageMetadata.Builder().setContentType("application/json").setCustomMetadata("source","My Attendance Android").build();
    ref.putBytes(bytes,meta).addOnSuccessListener(x->{
      long now=System.currentTimeMillis();
      js("window.onCloudBackupResult&&window.onCloudBackupResult(true,'Backup saved',"+now+");");
    }).addOnFailureListener(e->js("window.onCloudBackupResult&&window.onCloudBackupResult(false,"+JSONObject.quote(e.getMessage()==null?"Backup failed":e.getMessage())+",0);"));
  }

  private void cloudRestore(){
    StorageReference ref=backupRef();
    if(ref==null){js("window.onCloudRestoreError&&window.onCloudRestoreError('Please sign in with a verified account first');");return;}
    ref.getBytes(25L*1024L*1024L).addOnSuccessListener(bytes->{
      String payload=new String(bytes,StandardCharsets.UTF_8);
      js("window.onCloudRestore&&window.onCloudRestore("+JSONObject.quote(payload)+");");
    }).addOnFailureListener(e->js("window.onCloudRestoreError&&window.onCloudRestoreError("+JSONObject.quote(e.getMessage()==null?"No backup found":e.getMessage())+");"));
  }
'''
s=s[:m.start()]+direct+s[m.end():]

bridge='    @JavascriptInterface public void cloudRestore(){MainActivity.this.cloudRestore();}\n'
add='''    @JavascriptInterface public void secureCloudBackup(String json){MainActivity.this.secureCloudBackup(json);}
    @JavascriptInterface public void secureCloudRestore(){MainActivity.this.secureCloudRestore();}
'''
if add.strip() not in s:
    if bridge not in s: raise SystemExit('cloud bridge anchor missing')
    s=s.replace(bridge,bridge+add,1)

p.write_text(s,encoding='utf-8')
print('v12.7 device-auth cloud backup patch applied')
