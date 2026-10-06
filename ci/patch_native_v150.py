from pathlib import Path
import re,sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/java/com/personal/attendance/MainActivity.java')
s=p.read_text(encoding='utf-8')

field_anchor='''  private String firebaseInitError="";\n'''
field='''  private volatile boolean openNotificationsAfterLoad=false;\n'''
if field.strip() not in s:
    if field_anchor not in s: raise SystemExit('v15 notification field anchor missing')
    s=s.replace(field_anchor,field_anchor+field,1)

create_anchor='''    initFirebase();\n'''
create_new='''    initFirebase();\n    AppMessagingService.ensureSubscribed(this);\n    openNotificationsAfterLoad=AppMessagingService.captureLaunchIntent(this,getIntent());\n'''
if 'AppMessagingService.ensureSubscribed(this);' not in s:
    if create_anchor not in s: raise SystemExit('v15 onCreate anchor missing')
    s=s.replace(create_anchor,create_new,1)

page_old='''      @Override public void onPageFinished(WebView view,String url){super.onPageFinished(view,url);pushAuthState();}\n'''
page_new='''      @Override public void onPageFinished(WebView view,String url){\n        super.onPageFinished(view,url);\n        pushAuthState();\n        pushNotificationState();\n        if(openNotificationsAfterLoad){openNotificationsAfterLoad=false;js("window.AttendanceV15&&window.AttendanceV15.openNotificationsFromPush&&window.AttendanceV15.openNotificationsFromPush();");}\n      }\n'''
if 'pushNotificationState();' not in s:
    if page_old not in s: raise SystemExit('v15 onPageFinished anchor missing')
    s=s.replace(page_old,page_new,1)

resume_old='''  @Override protected void onResume(){\n    super.onResume();\n    if(appLockEnabledNative())runOnUiThread(()->maybePromptAppLock());\n  }\n'''
resume_new='''  @Override protected void onResume(){\n    super.onResume();\n    if(appLockEnabledNative())runOnUiThread(()->maybePromptAppLock());\n    AppMessagingService.ensureSubscribed(this);\n    pushNotificationState();\n  }\n'''
if 'AppMessagingService.ensureSubscribed(this);\n    pushNotificationState();' not in s:
    if resume_old not in s: raise SystemExit('v15 onResume anchor missing')
    s=s.replace(resume_old,resume_new,1)

activity_anchor='''  @Override protected void onActivityResult(int r,int c,Intent d){\n'''
new_intent='''  @Override protected void onNewIntent(Intent intent){\n    super.onNewIntent(intent);\n    setIntent(intent);\n    openNotificationsAfterLoad=AppMessagingService.captureLaunchIntent(this,intent);\n    pushNotificationState();\n    if(openNotificationsAfterLoad){openNotificationsAfterLoad=false;js("window.AttendanceV15&&window.AttendanceV15.openNotificationsFromPush&&window.AttendanceV15.openNotificationsFromPush();");}\n  }\n\n'''
if '@Override protected void onNewIntent(Intent intent)' not in s:
    if activity_anchor not in s: raise SystemExit('v15 onNewIntent anchor missing')
    s=s.replace(activity_anchor,new_intent+activity_anchor,1)

method_anchor='''  public class AndroidBridge{\n'''
methods=r'''  private void pushNotificationState(){
    try{js("window.onNativeNotificationState&&window.onNativeNotificationState("+JSONObject.quote(AppMessagingService.state(this).toString())+");");}
    catch(Exception ignored){}
  }

  private boolean canInstallUpdatesNative(){
    return Build.VERSION.SDK_INT<26||getPackageManager().canRequestPackageInstalls();
  }

  private void openInstallPermissionNative(){
    if(Build.VERSION.SDK_INT<26)return;
    try{
      Intent i=new Intent(android.provider.Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,Uri.parse("package:"+getPackageName()));
      startActivity(i);
    }catch(Exception e){
      try{startActivity(new Intent(android.provider.Settings.ACTION_SECURITY_SETTINGS));}catch(Exception ignored){}
    }
  }

  private String sha256File(File file) throws Exception{
    java.security.MessageDigest md=java.security.MessageDigest.getInstance("SHA-256");
    try(java.io.InputStream in=new java.io.FileInputStream(file)){
      byte[] buf=new byte[65536];int n;while((n=in.read(buf))>0)md.update(buf,0,n);
    }
    byte[] d=md.digest();StringBuilder sb=new StringBuilder();for(byte b:d)sb.append(String.format(java.util.Locale.US,"%02x",b));return sb.toString();
  }

  private byte[] signingDigest(android.content.pm.PackageInfo pi) throws Exception{
    android.content.pm.Signature[] sigs;
    if(Build.VERSION.SDK_INT>=28&&pi.signingInfo!=null){
      sigs=pi.signingInfo.hasMultipleSigners()?pi.signingInfo.getApkContentsSigners():pi.signingInfo.getSigningCertificateHistory();
    }else sigs=pi.signatures;
    if(sigs==null||sigs.length==0)throw new IllegalArgumentException("APK signing certificate is missing.");
    return java.security.MessageDigest.getInstance("SHA-256").digest(sigs[0].toByteArray());
  }

  private long packageVersionCode(android.content.pm.PackageInfo pi){
    return Build.VERSION.SDK_INT>=28?pi.getLongVersionCode():pi.versionCode;
  }

  private void verifyDownloadedUpdate(File apk,String expectedSha,String expectedVersion) throws Exception{
    String sha=expectedSha==null?"":expectedSha.trim().toLowerCase(java.util.Locale.US);
    if(!sha.isEmpty()){
      if(!sha.matches("^[0-9a-f]{64}$"))throw new IllegalArgumentException("Update checksum is invalid.");
      String actual=sha256File(apk);if(!sha.equals(actual))throw new SecurityException("Update checksum verification failed.");
    }
    int flags=Build.VERSION.SDK_INT>=28?android.content.pm.PackageManager.GET_SIGNING_CERTIFICATES:android.content.pm.PackageManager.GET_SIGNATURES;
    android.content.pm.PackageManager pm=getPackageManager();
    android.content.pm.PackageInfo incoming=pm.getPackageArchiveInfo(apk.getAbsolutePath(),flags);
    if(incoming==null)throw new IllegalArgumentException("Downloaded file is not a valid Android app update.");
    if(!getPackageName().equals(incoming.packageName))throw new SecurityException("Update package does not match My Attendance.");
    long newCode=packageVersionCode(incoming);if(newCode<=BuildConfig.VERSION_CODE)throw new IllegalArgumentException("This update is not newer than the installed version.");
    if(expectedVersion!=null&&!expectedVersion.trim().isEmpty()&&incoming.versionName!=null&&!expectedVersion.trim().equals(incoming.versionName))throw new SecurityException("Update version does not match the notification.");
    android.content.pm.PackageInfo current=pm.getPackageInfo(getPackageName(),flags);
    if(!java.util.Arrays.equals(signingDigest(current),signingDigest(incoming)))throw new SecurityException("Update signature does not match the installed app.");
  }

  private void launchUpdateInstaller(File apk){
    runOnUiThread(()->{
      try{
        Uri uri=FileProvider.getUriForFile(MainActivity.this,getPackageName()+".fileprovider",apk);
        Intent i=new Intent(Intent.ACTION_VIEW);i.setDataAndType(uri,"application/vnd.android.package-archive");i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_ACTIVITY_NEW_TASK);
        js("window.onUpdateInstallResult&&window.onUpdateInstallResult('ready','Update verified. Confirm Install on the Android screen.');");
        startActivity(i);
      }catch(Exception e){js("window.onUpdateInstallResult&&window.onUpdateInstallResult('error',"+JSONObject.quote(e.getMessage()==null?"Could not open the installer":e.getMessage())+");");}
    });
  }

  private void installUpdateNative(String url,String expectedSha,String expectedVersion){
    String value=url==null?"":url.trim();
    if(value.isEmpty()){js("window.onUpdateInstallResult&&window.onUpdateInstallResult('error','This update does not include a download link.');");return;}
    Uri parsed;try{parsed=Uri.parse(value);}catch(Exception e){parsed=null;}
    if(parsed==null||!"https".equalsIgnoreCase(parsed.getScheme())){js("window.onUpdateInstallResult&&window.onUpdateInstallResult('error','Only secure HTTPS update links are allowed.');");return;}
    if(!canInstallUpdatesNative()){
      js("window.onUpdateInstallResult&&window.onUpdateInstallResult('permission','Allow My Attendance to install apps, then tap Install Update again.');");
      runOnUiThread(this::openInstallPermissionNative);return;
    }
    new Thread(()->{
      java.net.HttpURLConnection c=null;
      try{
        js("window.onUpdateInstallResult&&window.onUpdateInstallResult('downloading','Downloading update…');");
        java.net.URL u=new java.net.URL(value);c=(java.net.HttpURLConnection)u.openConnection();c.setConnectTimeout(20000);c.setReadTimeout(60000);c.setInstanceFollowRedirects(true);c.setRequestProperty("User-Agent","My-Attendance/"+BuildConfig.VERSION_NAME);c.connect();
        int code=c.getResponseCode();if(code<200||code>=300)throw new java.io.IOException("Update download failed (HTTP "+code+").");
        long total=c.getContentLengthLong();if(total>250L*1024L*1024L)throw new java.io.IOException("Update file is unexpectedly large.");
        File dir=new File(getCacheDir(),"updates");if(!dir.exists()&&!dir.mkdirs())throw new java.io.IOException("Could not prepare update storage.");
        File apk=new File(dir,"My-Attendance-update.apk");long read=0;int last=-1;
        try(java.io.InputStream in=c.getInputStream();java.io.FileOutputStream out=new java.io.FileOutputStream(apk)){
          byte[] buf=new byte[65536];int n;while((n=in.read(buf))>0){out.write(buf,0,n);read+=n;if(total>0){int pct=(int)Math.min(99,(read*100L)/total);if(pct>=last+3){last=pct;js("window.onUpdateDownloadProgress&&window.onUpdateDownloadProgress("+pct+");");}}}
        }
        if(apk.length()<1024L*1024L)throw new java.io.IOException("Downloaded update file is incomplete.");
        js("window.onUpdateDownloadProgress&&window.onUpdateDownloadProgress(100);");
        verifyDownloadedUpdate(apk,expectedSha,expectedVersion);
        launchUpdateInstaller(apk);
      }catch(Exception e){js("window.onUpdateInstallResult&&window.onUpdateInstallResult('error',"+JSONObject.quote(e.getMessage()==null?"Update installation failed":e.getMessage())+");");}
      finally{if(c!=null)c.disconnect();}
    },"attendance-update-download").start();
  }

'''
if 'private void pushNotificationState()' not in s:
    if method_anchor not in s: raise SystemExit('v15 AndroidBridge anchor missing')
    s=s.replace(method_anchor,methods+method_anchor,1)

bridge_anchor='''    @JavascriptInterface public String reminderSettings(){return ReminderManager.settingsJson(MainActivity.this).toString();}\n'''
bridge=r'''    @JavascriptInterface public String notificationState(){return AppMessagingService.state(MainActivity.this).toString();}
    @JavascriptInterface public void markNotificationRead(String id){AppMessagingService.markRead(MainActivity.this,id);pushNotificationState();}
    @JavascriptInterface public void markAllNotificationsRead(){AppMessagingService.markAllRead(MainActivity.this);pushNotificationState();}
    @JavascriptInterface public void clearNotifications(){AppMessagingService.clear(MainActivity.this);pushNotificationState();}
    @JavascriptInterface public boolean canInstallUpdates(){return MainActivity.this.canInstallUpdatesNative();}
    @JavascriptInterface public void openInstallPermission(){runOnUiThread(()->MainActivity.this.openInstallPermissionNative());}
    @JavascriptInterface public void installUpdate(String url,String sha256,String version){MainActivity.this.installUpdateNative(url,sha256,version);}
'''
if '@JavascriptInterface public String notificationState()' not in s:
    if bridge_anchor not in s: raise SystemExit('v15 bridge insertion anchor missing')
    s=s.replace(bridge_anchor,bridge+bridge_anchor,1)

p.write_text(s,encoding='utf-8')
print('v15 native push notification and secure update installer patch applied')
