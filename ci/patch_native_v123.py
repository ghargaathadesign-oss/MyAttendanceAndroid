from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/java/com/personal/attendance/MainActivity.java')
s=p.read_text(encoding='utf-8')

imports='''import android.content.SharedPreferences;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
'''
anchor='import android.content.Intent;\n'
if imports.strip() not in s:
    if anchor not in s: raise SystemExit('android import anchor missing')
    s=s.replace(anchor,anchor+imports,1)

crypto_imports='''import java.security.KeyStore;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
'''
anchor2='import java.nio.charset.StandardCharsets;\n'
if crypto_imports.strip() not in s:
    if anchor2 not in s: raise SystemExit('java import anchor missing')
    s=s.replace(anchor2,anchor2+crypto_imports,1)

if 'import org.json.JSONArray;' not in s:
    s=s.replace('import org.json.JSONObject;\n','import org.json.JSONArray;\nimport org.json.JSONObject;\n',1)

field_anchor='  private String firebaseInitError="";\n'
fields='''  private static final String SECURE_PREFS="my_attendance_secure_store_v1";
  private static final String SECURE_KEY_ALIAS="my_attendance_local_aes_v1";
'''
if fields.strip() not in s:
    if field_anchor not in s: raise SystemExit('field anchor missing')
    s=s.replace(field_anchor,field_anchor+fields,1)

method_anchor='  private void initFirebase(){\n'
methods='''  private SecretKey secureSecretKey() throws Exception{
    KeyStore keyStore=KeyStore.getInstance("AndroidKeyStore");
    keyStore.load(null);
    if(!keyStore.containsAlias(SECURE_KEY_ALIAS)){
      KeyGenerator generator=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
      generator.init(new KeyGenParameterSpec.Builder(
        SECURE_KEY_ALIAS,
        KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT
      ).setBlockModes(KeyProperties.BLOCK_MODE_GCM)
       .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
       .setKeySize(256)
       .build());
      return generator.generateKey();
    }
    KeyStore.SecretKeyEntry entry=(KeyStore.SecretKeyEntry)keyStore.getEntry(SECURE_KEY_ALIAS,null);
    return entry.getSecretKey();
  }

  private String secureEncrypt(String storageKey,String value) throws Exception{
    Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(Cipher.ENCRYPT_MODE,secureSecretKey());
    cipher.updateAAD(storageKey.getBytes(StandardCharsets.UTF_8));
    byte[] iv=cipher.getIV();
    byte[] enc=cipher.doFinal((value==null?"":value).getBytes(StandardCharsets.UTF_8));
    return Base64.encodeToString(iv,Base64.NO_WRAP)+"."+Base64.encodeToString(enc,Base64.NO_WRAP);
  }

  private String secureDecrypt(String storageKey,String packed) throws Exception{
    int dot=packed==null?-1:packed.indexOf('.');
    if(dot<=0)throw new IllegalArgumentException("Invalid encrypted value");
    byte[] iv=Base64.decode(packed.substring(0,dot),Base64.NO_WRAP);
    byte[] enc=Base64.decode(packed.substring(dot+1),Base64.NO_WRAP);
    Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(Cipher.DECRYPT_MODE,secureSecretKey(),new GCMParameterSpec(128,iv));
    cipher.updateAAD(storageKey.getBytes(StandardCharsets.UTF_8));
    return new String(cipher.doFinal(enc),StandardCharsets.UTF_8);
  }

  private synchronized String secureStoreGet(String key){
    try{
      String packed=getSharedPreferences(SECURE_PREFS,MODE_PRIVATE).getString(key,null);
      if(packed==null)return null;
      return secureDecrypt(key,packed);
    }catch(Exception e){
      return null;
    }
  }

  private synchronized boolean secureStoreSet(String key,String value){
    try{
      String packed=secureEncrypt(key,value);
      return getSharedPreferences(SECURE_PREFS,MODE_PRIVATE).edit().putString(key,packed).commit();
    }catch(Exception e){
      return false;
    }
  }

  private synchronized void secureStoreRemove(String key){
    getSharedPreferences(SECURE_PREFS,MODE_PRIVATE).edit().remove(key).apply();
  }

  private synchronized String secureStoreKeys(String prefix){
    JSONArray out=new JSONArray();
    try{
      for(String k:getSharedPreferences(SECURE_PREFS,MODE_PRIVATE).getAll().keySet()){
        if(prefix==null||prefix.isEmpty()||k.startsWith(prefix))out.put(k);
      }
    }catch(Exception ignored){}
    return out.toString();
  }

  private synchronized void secureStoreClearPrefix(String prefix){
    SharedPreferences prefs=getSharedPreferences(SECURE_PREFS,MODE_PRIVATE);
    SharedPreferences.Editor editor=prefs.edit();
    for(String k:prefs.getAll().keySet())if(prefix==null||prefix.isEmpty()||k.startsWith(prefix))editor.remove(k);
    editor.commit();
  }

  private boolean secureStoreAvailable(){
    try{
      secureSecretKey();
      return true;
    }catch(Exception e){
      return false;
    }
  }

'''
if methods.strip() not in s:
    if method_anchor not in s: raise SystemExit('method anchor missing')
    s=s.replace(method_anchor,methods+method_anchor,1)

bridge_anchor='    @JavascriptInterface public String currentUserUid(){FirebaseUser u=auth==null?null:auth.getCurrentUser();return u==null?"":u.getUid();}\n'
bridge_methods='''    @JavascriptInterface public boolean secureStorageAvailable(){return MainActivity.this.secureStoreAvailable();}
    @JavascriptInterface public String secureGet(String key){return MainActivity.this.secureStoreGet(key);}
    @JavascriptInterface public boolean secureSet(String key,String value){return MainActivity.this.secureStoreSet(key,value);}
    @JavascriptInterface public void secureRemove(String key){MainActivity.this.secureStoreRemove(key);}
    @JavascriptInterface public String secureKeys(String prefix){return MainActivity.this.secureStoreKeys(prefix);}
    @JavascriptInterface public void secureClearPrefix(String prefix){MainActivity.this.secureStoreClearPrefix(prefix);}
'''
if bridge_methods.strip() not in s:
    if bridge_anchor not in s: raise SystemExit('secure bridge anchor missing')
    s=s.replace(bridge_anchor,bridge_anchor+bridge_methods,1)

p.write_text(s,encoding='utf-8')
print('v12.3 Android Keystore secure storage patch applied')
