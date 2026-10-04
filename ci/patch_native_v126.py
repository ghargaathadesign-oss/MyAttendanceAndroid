from pathlib import Path
import re, sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/java/com/personal/attendance/MainActivity.java')
s=p.read_text(encoding='utf-8')

imports='''import android.webkit.WebResourceRequest;\nimport android.webkit.WebResourceResponse;\n'''
if 'import android.webkit.WebResourceRequest;' not in s:
    s=s.replace('import android.webkit.ValueCallback;\n','import android.webkit.ValueCallback;\n'+imports,1)
if 'import androidx.webkit.WebViewAssetLoader;' not in s:
    s=s.replace('import androidx.core.content.FileProvider;\n','import androidx.core.content.FileProvider;\nimport androidx.webkit.WebViewAssetLoader;\n',1)
if 'import com.google.firebase.auth.EmailAuthProvider;' not in s:
    s=s.replace('import com.google.firebase.auth.AuthCredential;\n','import com.google.firebase.auth.AuthCredential;\nimport com.google.firebase.auth.EmailAuthProvider;\nimport com.google.firebase.auth.UserInfo;\n',1)
if 'import com.google.firebase.storage.StorageException;' not in s:
    s=s.replace('import com.google.firebase.storage.StorageMetadata;\n','import com.google.firebase.storage.StorageMetadata;\nimport com.google.firebase.storage.StorageException;\n',1)
if 'import java.util.HashMap;' not in s:
    s=s.replace('import java.util.ArrayList;\n','import java.util.ArrayList;\nimport java.util.HashMap;\nimport java.util.Iterator;\nimport java.util.Map;\n',1)

field='  private String firebaseInitError="";\n'
if 'private boolean pendingDeleteGoogle=false;' not in s:
    s=s.replace(field,field+'  private boolean pendingDeleteGoogle=false;\n',1)

old='''    s.setAllowFileAccess(true);
    s.setAllowContentAccess(true);
    s.setAllowFileAccessFromFileURLs(true);
    s.setTextZoom(100);
    webView.setWebViewClient(new WebViewClient(){
      @Override public void onPageFinished(WebView view,String url){super.onPageFinished(view,url);pushAuthState();}
    });'''
new='''    final WebViewAssetLoader assetLoader=new WebViewAssetLoader.Builder()
      .addPathHandler("/assets/",new WebViewAssetLoader.AssetsPathHandler(this))
      .build();
    s.setAllowFileAccess(false);
    s.setAllowContentAccess(true);
    s.setAllowFileAccessFromFileURLs(false);
    s.setAllowUniversalAccessFromFileURLs(false);
    s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
    s.setSafeBrowsingEnabled(true);
    s.setTextZoom(100);
    webView.setWebViewClient(new WebViewClient(){
      @Override public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest request){
        return assetLoader.shouldInterceptRequest(request.getUrl());
      }
      @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){
        Uri u=request.getUrl();
        if(u!=null&&"https".equalsIgnoreCase(u.getScheme())&&"appassets.androidplatform.net".equalsIgnoreCase(u.getHost()))return false;
        try{if(u!=null)startActivity(new Intent(Intent.ACTION_VIEW,u));}catch(Exception ignored){}
        return true;
      }
      @Override public void onPageFinished(WebView view,String url){super.onPageFinished(view,url);pushAuthState();}
    });'''
if old not in s: raise SystemExit('WebView settings anchor missing')
s=s.replace(old,new,1)
s=s.replace('webView.loadUrl("file:///android_asset/index.html");','webView.loadUrl("https://appassets.androidplatform.net/assets/index.html");',1)

anchor='''  private boolean secureStoreAvailable(){
'''
method='''  private synchronized boolean secureStoreReplacePrefix(String prefix,String json){
    try{
      JSONObject input=new JSONObject(json==null?"{}":json);
      Map<String,String> encrypted=new HashMap<>();
      Iterator<String> it=input.keys();
      while(it.hasNext()){
        String k=it.next();
        if(prefix==null||prefix.isEmpty()||!k.startsWith(prefix))return false;
        encrypted.put(k,secureEncrypt(k,input.optString(k,"")));
      }
      SharedPreferences prefs=getSharedPreferences(SECURE_PREFS,MODE_PRIVATE);
      SharedPreferences.Editor editor=prefs.edit();
      for(String k:prefs.getAll().keySet())if(k.startsWith(prefix))editor.remove(k);
      for(Map.Entry<String,String> e:encrypted.entrySet())editor.putString(e.getKey(),e.getValue());
      return editor.commit();
    }catch(Exception e){return false;}
  }

'''
if 'secureStoreReplacePrefix' not in s:
    if anchor not in s: raise SystemExit('secure replace anchor missing')
    s=s.replace(anchor,method+anchor,1)

pat=re.compile(r"  private void deleteAccountData\(\)\{.*?\n  \}\n\n  private void cloudRestore",re.S)
m=pat.search(s)
if not m: raise SystemExit('deleteAccountData method anchor missing')
replacement='''  private String authProviderNative(){
    FirebaseUser u=auth==null?null:auth.getCurrentUser();
    if(u==null)return "";
    String found="";
    for(UserInfo info:u.getProviderData()){
      String provider=info.getProviderId();
      if("password".equals(provider))return "password";
      if(GoogleAuthProvider.PROVIDER_ID.equals(provider))found="google.com";
    }
    return found;
  }

  private void finishDeleteAccount(FirebaseUser u){
    if(u==null){js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,'Please sign in again.');");return;}
    StorageReference ref=cloudStorage==null?null:cloudStorage.getReference().child("users").child(u.getUid()).child("backups").child("latest.json");
    Runnable deleteUser=()->u.delete().addOnCompleteListener(this,t->{
      if(t.isSuccessful())js("window.onProfileDeleteResult&&window.onProfileDeleteResult(true,'Profile deleted');");
      else{String msg=t.getException()==null?"Could not delete account":t.getException().getMessage();js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,"+JSONObject.quote(msg)+");");}
    });
    if(ref==null){deleteUser.run();return;}
    ref.delete().addOnSuccessListener(x->deleteUser.run()).addOnFailureListener(e->{
      if(e instanceof StorageException&&((StorageException)e).getErrorCode()==StorageException.ERROR_OBJECT_NOT_FOUND)deleteUser.run();
      else js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,"+JSONObject.quote(e.getMessage()==null?"Could not remove cloud backup":e.getMessage())+");");
    });
  }

  private void deleteAccountWithPassword(String password){
    FirebaseUser u=auth==null?null:auth.getCurrentUser();
    if(u==null||u.getEmail()==null){js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,'Please sign in again.');");return;}
    AuthCredential credential=EmailAuthProvider.getCredential(u.getEmail(),password==null?"":password);
    u.reauthenticate(credential).addOnCompleteListener(this,t->{
      if(t.isSuccessful())finishDeleteAccount(u);
      else{String msg=t.getException()==null?"Password verification failed":t.getException().getMessage();js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,"+JSONObject.quote(msg)+");");}
    });
  }

  private void deleteAccountData(){
    FirebaseUser u=auth==null?null:auth.getCurrentUser();
    if(u==null){js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,'Please sign in again.');");return;}
    String provider=authProviderNative();
    if("google.com".equals(provider)){pendingDeleteGoogle=true;beginGoogleSignIn();return;}
    js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,'Current password verification is required.');");
  }

  private void cloudRestore'''
s=s[:m.start()]+replacement+s[m.end():]

old='''      AuthCredential fc=GoogleAuthProvider.getCredential(g.getIdToken(),null);
      auth.signInWithCredential(fc).addOnCompleteListener(this,t->{
        if(t.isSuccessful())pushAuthState();
        else jsError(t.getException()==null?"Google sign-in failed":t.getException().getMessage());
      });'''
new='''      AuthCredential fc=GoogleAuthProvider.getCredential(g.getIdToken(),null);
      if(pendingDeleteGoogle){
        pendingDeleteGoogle=false;
        FirebaseUser current=auth==null?null:auth.getCurrentUser();
        if(current==null){js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,'Please sign in again.');");return;}
        current.reauthenticate(fc).addOnCompleteListener(this,t->{
          if(t.isSuccessful())finishDeleteAccount(current);
          else{String msg=t.getException()==null?"Google re-authentication failed":t.getException().getMessage();js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,"+JSONObject.quote(msg)+");");}
        });
        return;
      }
      auth.signInWithCredential(fc).addOnCompleteListener(this,t->{
        if(t.isSuccessful())pushAuthState();
        else jsError(t.getException()==null?"Google sign-in failed":t.getException().getMessage());
      });'''
if old not in s: raise SystemExit('Google credential anchor missing')
s=s.replace(old,new,1)

bridge='    @JavascriptInterface public void secureClearPrefix(String prefix){MainActivity.this.secureStoreClearPrefix(prefix);}\n'
add='''    @JavascriptInterface public boolean secureReplacePrefix(String prefix,String json){return MainActivity.this.secureStoreReplacePrefix(prefix,json);}
'''
if add.strip() not in s:
    if bridge not in s: raise SystemExit('secure bridge anchor missing')
    s=s.replace(bridge,bridge+add,1)
old='    @JavascriptInterface public void deleteAccountData(){runOnUiThread(() -> MainActivity.this.deleteAccountData());}\n'
new='''    @JavascriptInterface public String authProvider(){return MainActivity.this.authProviderNative();}
    @JavascriptInterface public void deleteAccountData(){runOnUiThread(() -> MainActivity.this.deleteAccountData());}
    @JavascriptInterface public void deleteAccountDataWithPassword(String password){runOnUiThread(() -> MainActivity.this.deleteAccountWithPassword(password));}
'''
if old not in s: raise SystemExit('delete bridge anchor missing')
s=s.replace(old,new,1)

cloud_anchor='''  private void cloudBackup(String json){
'''
helper='''  private void withAppCheck(Runnable action,java.util.function.Consumer<String> fail){
    try{
      FirebaseAppCheck.getInstance().getAppCheckToken(false)
        .addOnSuccessListener(token->action.run())
        .addOnFailureListener(e->fail.accept(e.getMessage()==null?"App integrity check failed":e.getMessage()));
    }catch(Exception e){fail.accept(e.getMessage()==null?"App integrity check failed":e.getMessage());}
  }

'''
if 'private void withAppCheck(' not in s:
    if cloud_anchor not in s: raise SystemExit('cloud backup helper anchor missing')
    s=s.replace(cloud_anchor,helper+cloud_anchor,1)

old='''    ref.putBytes(bytes,meta).addOnSuccessListener(x->{
      long now=System.currentTimeMillis();
      js("window.onCloudBackupResult&&window.onCloudBackupResult(true,'Backup saved',"+now+");");
    }).addOnFailureListener(e->js("window.onCloudBackupResult&&window.onCloudBackupResult(false,"+JSONObject.quote(e.getMessage()==null?"Backup failed":e.getMessage())+",0);"));'''
new='''    withAppCheck(()->ref.putBytes(bytes,meta).addOnSuccessListener(x->{
      long now=System.currentTimeMillis();
      js("window.onCloudBackupResult&&window.onCloudBackupResult(true,'Backup saved',"+now+");");
    }).addOnFailureListener(e->js("window.onCloudBackupResult&&window.onCloudBackupResult(false,"+JSONObject.quote(e.getMessage()==null?"Backup failed":e.getMessage())+",0);")),
    msg->js("window.onCloudBackupResult&&window.onCloudBackupResult(false,"+JSONObject.quote(msg)+",0);"));'''
if old not in s: raise SystemExit('cloudBackup put anchor missing')
s=s.replace(old,new,1)

old='''    ref.getBytes(25L*1024L*1024L).addOnSuccessListener(bytes->{
      String payload=new String(bytes,StandardCharsets.UTF_8);
      js("window.onCloudRestore&&window.onCloudRestore("+JSONObject.quote(payload)+");");
    }).addOnFailureListener(e->js("window.onCloudRestoreError&&window.onCloudRestoreError("+JSONObject.quote(e.getMessage()==null?"No backup found":e.getMessage())+");"));'''
new='''    withAppCheck(()->ref.getBytes(25L*1024L*1024L).addOnSuccessListener(bytes->{
      String payload=new String(bytes,StandardCharsets.UTF_8);
      js("window.onCloudRestore&&window.onCloudRestore("+JSONObject.quote(payload)+");");
    }).addOnFailureListener(e->js("window.onCloudRestoreError&&window.onCloudRestoreError("+JSONObject.quote(e.getMessage()==null?"No backup found":e.getMessage())+");")),
    msg->js("window.onCloudRestoreError&&window.onCloudRestoreError("+JSONObject.quote(msg)+");"));'''
if old not in s: raise SystemExit('cloudRestore get anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('v12.6 native hardening patch applied')
