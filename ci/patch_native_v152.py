from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/java/com/personal/attendance/MainActivity.java')
s=p.read_text(encoding='utf-8')

field_anchor='''  private volatile boolean openNotificationsAfterLoad=false;\n'''
field='''  private static final String UPDATE_MANIFEST_URL="https://raw.githubusercontent.com/ghargaathadesign-oss/MyAttendanceAndroid/main/update-manifest.json";\n'''
if field.strip() not in s:
    if field_anchor not in s: raise SystemExit('v15.2 update manifest field anchor missing')
    s=s.replace(field_anchor,field_anchor+field,1)

resume_old='''  @Override protected void onResume(){\n    super.onResume();\n    if(appLockEnabledNative())runOnUiThread(()->maybePromptAppLock());\n    AppMessagingService.ensureSubscribed(this);\n    pushNotificationState();\n  }\n'''
resume_new='''  @Override protected void onResume(){\n    super.onResume();\n    if(appLockEnabledNative())runOnUiThread(()->maybePromptAppLock());\n    AppMessagingService.ensureSubscribed(this);\n    pushNotificationState();\n    checkForUpdatesNative(false);\n  }\n'''
if 'checkForUpdatesNative(false);' not in s:
    if resume_old not in s: raise SystemExit('v15.2 onResume anchor missing')
    s=s.replace(resume_old,resume_new,1)

method_anchor='''  public class AndroidBridge{\n'''
methods=r'''  private void checkForUpdatesNative(boolean force){
    try{
      android.content.SharedPreferences sp=getSharedPreferences("attendance_update_check_v152",MODE_PRIVATE);
      long now=System.currentTimeMillis(),last=sp.getLong("last_check",0L);
      if(!force&&now-last<30L*60L*1000L)return;
      sp.edit().putLong("last_check",now).apply();
    }catch(Exception ignored){}
    new Thread(()->{
      java.net.HttpURLConnection c=null;
      try{
        java.net.URL u=new java.net.URL(UPDATE_MANIFEST_URL);
        c=(java.net.HttpURLConnection)u.openConnection();
        c.setConnectTimeout(12000);c.setReadTimeout(12000);c.setInstanceFollowRedirects(true);
        c.setRequestProperty("Accept","application/json");
        c.setRequestProperty("User-Agent","My-Attendance/"+BuildConfig.VERSION_NAME);
        c.connect();
        int code=c.getResponseCode();
        if(code<200||code>=300)throw new java.io.IOException("Update check failed (HTTP "+code+").");
        java.io.ByteArrayOutputStream out=new java.io.ByteArrayOutputStream();
        try(java.io.InputStream in=c.getInputStream()){
          byte[] buf=new byte[8192];int n,total=0;
          while((n=in.read(buf))>0){
            total+=n;if(total>256*1024)throw new java.io.IOException("Update manifest is too large.");
            out.write(buf,0,n);
          }
        }
        JSONObject m=new JSONObject(out.toString("UTF-8"));
        int newCode=m.optInt("versionCode",0);
        String version=m.optString("versionName","").trim();
        String apk=m.optString("apkUrl","").trim();
        String sha=m.optString("sha256","").trim().toLowerCase(java.util.Locale.US);
        String changes=m.optString("changelog","").trim();
        if(newCode<=BuildConfig.VERSION_CODE){
          js("window.onUpdateCheckResult&&window.onUpdateCheckResult('up_to_date','You already have the latest version.');");
          return;
        }
        Uri apkUri=Uri.parse(apk);
        if(!"https".equalsIgnoreCase(apkUri.getScheme()))throw new SecurityException("Update manifest contains an insecure APK URL.");
        if(!sha.matches("^[0-9a-f]{64}$"))throw new SecurityException("Update manifest checksum is invalid.");
        JSONObject item=new JSONObject();
        item.put("id","update-"+newCode);
        item.put("type","update");
        item.put("title","My Attendance v"+version+" is available");
        item.put("body","A new My Attendance update is ready. Tap to review and install.");
        item.put("version",version);item.put("versionCode",newCode);
        item.put("apkUrl",apk);item.put("sha256",sha);item.put("changelog",changes);
        item.put("receivedAt",System.currentTimeMillis());item.put("read",false);
        AppMessagingService.publishItem(MainActivity.this,item);
        pushNotificationState();
        js("window.onUpdateCheckResult&&window.onUpdateCheckResult('available','My Attendance v"+version+" is available.');");
      }catch(Exception e){
        String msg=e.getMessage()==null?"Could not check for updates.":e.getMessage();
        js("window.onUpdateCheckResult&&window.onUpdateCheckResult('error',"+JSONObject.quote(msg)+");");
      }finally{if(c!=null)c.disconnect();}
    },"attendance-update-check").start();
  }

'''
if 'private void checkForUpdatesNative(boolean force)' not in s:
    if method_anchor not in s: raise SystemExit('v15.2 AndroidBridge anchor missing')
    s=s.replace(method_anchor,methods+method_anchor,1)

bridge_anchor='''    @JavascriptInterface public String notificationState(){return AppMessagingService.state(MainActivity.this).toString();}\n'''
bridge='''    @JavascriptInterface public void checkForUpdates(){MainActivity.this.checkForUpdatesNative(true);}\n    @JavascriptInterface public void refreshPushRegistration(){AppMessagingService.ensureSubscribed(MainActivity.this);pushNotificationState();}\n'''
if '@JavascriptInterface public void checkForUpdates()' not in s:
    if bridge_anchor not in s: raise SystemExit('v15.2 notification bridge anchor missing')
    s=s.replace(bridge_anchor,bridge_anchor+bridge,1)

p.write_text(s,encoding='utf-8')
print('v15.2 push diagnostics and fallback update checker native patch applied')
