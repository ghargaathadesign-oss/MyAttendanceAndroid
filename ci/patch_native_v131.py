from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/java/com/personal/attendance/MainActivity.java')
s=p.read_text(encoding='utf-8')

anchor='''  public class AndroidBridge {
'''
methods='''  private long diagnosticsDirectoryBytes(File f){
    if(f==null||!f.exists())return 0L;
    if(f.isFile())return Math.max(0L,f.length());
    long total=0L;
    File[] children=f.listFiles();
    if(children!=null)for(File child:children)total+=diagnosticsDirectoryBytes(child);
    return total;
  }

  private boolean diagnosticsBackupKeyPresent(String uid){
    try{
      if(uid==null||uid.isEmpty())return false;
      KeyStore keyStore=KeyStore.getInstance("AndroidKeyStore");
      keyStore.load(null);
      return keyStore.containsAlias(backupKeyAlias(uid));
    }catch(Exception e){return false;}
  }

  private String diagnosticsSummaryNative(){
    JSONObject o=new JSONObject();
    try{
      FirebaseUser u=auth==null?null:auth.getCurrentUser();
      boolean signed=u!=null;
      o.put("versionName",BuildConfig.VERSION_NAME);
      o.put("versionCode",BuildConfig.VERSION_CODE);
      o.put("sdk",Build.VERSION.SDK_INT);
      o.put("androidRelease",Build.VERSION.RELEASE==null?"":Build.VERSION.RELEASE);
      o.put("signedIn",signed);
      o.put("emailVerified",signed&&u.isEmailVerified());
      o.put("authProvider",signed?authProviderNative():"");
      o.put("secureStorage",secureStoreAvailable());
      o.put("deviceSecure",deviceSecurityReady());
      o.put("backupKeyPresent",signed&&diagnosticsBackupKeyPresent(u.getUid()));
      o.put("appCheckEnabled",BuildConfig.FIREBASE_APP_CHECK_ENABLED);
      o.put("webViewFileAccess",webView!=null&&webView.getSettings().getAllowFileAccess());
      o.put("safeBrowsing",webView!=null&&webView.getSettings().getSafeBrowsingEnabled());
      int secureCount=0;
      if(signed){
        String safe=u.getUid().replaceAll("[^A-Za-z0-9_-]","_");
        try{secureCount=new JSONArray(secureStoreKeys("attendance_user_"+safe+"__")).length();}catch(Exception ignored){}
      }
      o.put("secureKeyCount",secureCount);
      o.put("cacheBytes",diagnosticsDirectoryBytes(getCacheDir()));
    }catch(Exception e){
      try{o.put("diagnosticsError",true);}catch(Exception ignored){}
    }
    return o.toString();
  }

  private void diagnosticsCloudBackupNative(){
    FirebaseUser u=auth==null?null:auth.getCurrentUser();
    StorageReference ref=backupRef();
    if(u==null||!u.isEmailVerified()||ref==null){
      JSONObject out=new JSONObject();
      try{out.put("ok",false);out.put("exists",false);out.put("reason","Account verification required");}catch(Exception ignored){}
      js("window.onDiagnosticsCloudStatus&&window.onDiagnosticsCloudStatus("+out.toString()+");");
      return;
    }
    ref.getBytes(25L*1024L*1024L).addOnSuccessListener(bytes->{
      JSONObject out=new JSONObject();
      try{
        out.put("ok",true);
        out.put("exists",true);
        out.put("bytes",bytes==null?0:bytes.length);
        JSONObject env=new JSONObject(new String(bytes,StandardCharsets.UTF_8));
        int v=env.optInt("version",0);
        out.put("version",v);
        boolean device=false,transfer=false,legacy=false;
        if(v==7&&env.optBoolean("combined")){
          device=env.has("device");
          transfer=env.has("transfer");
          legacy=env.has("legacy");
        }else if(v==6&&env.optBoolean("portable"))transfer=true;
        else if(v==5&&env.optBoolean("encrypted"))device=true;
        else legacy=true;
        out.put("hasDevice",device);
        out.put("hasTransfer",transfer);
        out.put("hasLegacy",legacy);
      }catch(Exception e){
        try{out.put("ok",true);out.put("exists",true);out.put("version",0);out.put("hasLegacy",true);}catch(Exception ignored){}
      }
      js("window.onDiagnosticsCloudStatus&&window.onDiagnosticsCloudStatus("+out.toString()+");");
    }).addOnFailureListener(e->{
      JSONObject out=new JSONObject();
      try{
        if(e instanceof StorageException&&((StorageException)e).getErrorCode()==StorageException.ERROR_OBJECT_NOT_FOUND){
          out.put("ok",true);out.put("exists",false);
        }else{
          out.put("ok",false);out.put("exists",false);out.put("reason","Cloud backup check failed");
        }
      }catch(Exception ignored){}
      js("window.onDiagnosticsCloudStatus&&window.onDiagnosticsCloudStatus("+out.toString()+");");
    });
  }

  private void clearDiagnosticsCacheNative(){
    boolean ok=true;
    try{
      File dir=getCacheDir();
      File[] children=dir==null?null:dir.listFiles();
      if(children!=null)for(File child:children)deleteFileTree(child);
    }catch(Exception e){ok=false;}
    final boolean result=ok;
    runOnUiThread(()->{
      try{if(webView!=null)webView.clearCache(true);}catch(Exception ignored){}
      js("window.onDiagnosticsCacheCleared&&window.onDiagnosticsCacheCleared("+result+");");
    });
  }

'''
if methods.strip() not in s:
    if anchor not in s: raise SystemExit('AndroidBridge anchor missing')
    s=s.replace(anchor,methods+anchor,1)

bridge_anchor='''    @JavascriptInterface public String authProvider(){return MainActivity.this.authProviderNative();}
'''
bridge='''    @JavascriptInterface public String diagnosticsSummary(){return MainActivity.this.diagnosticsSummaryNative();}
    @JavascriptInterface public void diagnosticsCloudBackup(){MainActivity.this.diagnosticsCloudBackupNative();}
    @JavascriptInterface public void clearDiagnosticsCache(){new Thread(() -> MainActivity.this.clearDiagnosticsCacheNative()).start();}
'''
if bridge.strip() not in s:
    if bridge_anchor not in s: raise SystemExit('diagnostics bridge anchor missing')
    s=s.replace(bridge_anchor,bridge+bridge_anchor,1)

p.write_text(s,encoding='utf-8')
print('v13.1 native diagnostics patch applied')
