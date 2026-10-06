from pathlib import Path
import re,sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/java/com/personal/attendance/MainActivity.java')
s=p.read_text(encoding='utf-8')

field_anchor='''  private volatile boolean diagnosticsSafeBrowsing=true;\n'''
fields='''  private volatile boolean appLockPromptActive=false;\n  private volatile boolean appLockSessionUnlocked=false;\n  private volatile long appLockBackgroundAt=0L;\n'''
if fields.strip() not in s:
    if field_anchor not in s: raise SystemExit('v14 app lock field anchor missing')
    s=s.replace(field_anchor,field_anchor+fields,1)

method_anchor='''  private void initFirebase(){\n'''
methods=r'''  private android.content.SharedPreferences appSecurityPrefs(){
    return getSharedPreferences("attendance_security_v14",MODE_PRIVATE);
  }

  private boolean appLockEnabledNative(){return appSecurityPrefs().getBoolean("appLockEnabled",false);}
  private int appLockTimeoutNative(){int v=appSecurityPrefs().getInt("appLockTimeout",30);return v==0||v==30||v==60||v==300?v:30;}

  private String appLockStateNative(){
    JSONObject o=new JSONObject();
    try{o.put("enabled",appLockEnabledNative());o.put("timeoutSeconds",appLockTimeoutNative());o.put("deviceSecure",deviceSecurityReady());}catch(Exception ignored){}
    return o.toString();
  }

  private void setAppLockConfigNative(boolean enabled,int timeoutSeconds){
    final int safeTimeout=(timeoutSeconds==0||timeoutSeconds==30||timeoutSeconds==60||timeoutSeconds==300)?timeoutSeconds:30;
    boolean current=appLockEnabledNative();
    Runnable apply=()->{
      appSecurityPrefs().edit().putBoolean("appLockEnabled",enabled).putInt("appLockTimeout",safeTimeout).apply();
      appLockSessionUnlocked=enabled;
      appLockBackgroundAt=0L;
      js("window.onAppLockConfigResult&&window.onAppLockConfigResult(true,"+JSONObject.quote(enabled?"App lock enabled.":"App lock disabled.")+");");
    };
    if(current==enabled){apply.run();return;}
    appLockPromptActive=true;
    deviceAuthenticate(enabled?"Enable App Lock":"Disable App Lock","Verify with your phone security.",()->{
      appLockPromptActive=false;apply.run();
    },msg->{
      appLockPromptActive=false;
      js("window.onAppLockConfigResult&&window.onAppLockConfigResult(false,"+JSONObject.quote(msg==null?"Device verification cancelled":msg)+");");
    });
  }

  private void maybePromptAppLock(){
    if(!appLockEnabledNative()||appLockPromptActive)return;
    long now=System.currentTimeMillis();
    int timeout=appLockTimeoutNative();
    boolean expired=!appLockSessionUnlocked||(appLockBackgroundAt>0L&&now-appLockBackgroundAt>=timeout*1000L);
    if(!expired)return;
    appLockPromptActive=true;
    if(webView!=null)webView.setVisibility(android.view.View.INVISIBLE);
    deviceAuthenticate("Unlock My Attendance","Use fingerprint, face, PIN, pattern or device password.",()->{
      appLockSessionUnlocked=true;appLockBackgroundAt=0L;appLockPromptActive=false;
      runOnUiThread(()->{if(webView!=null)webView.setVisibility(android.view.View.VISIBLE);});
    },msg->{
      appLockSessionUnlocked=false;appLockPromptActive=false;
      runOnUiThread(()->{if(webView!=null)webView.setVisibility(android.view.View.INVISIBLE);finish();});
    });
  }

  private void saveReminderSettingsNative(String json){
    try{
      ReminderManager.saveSettings(this,json);
      js("window.onReminderSettingsSaved&&window.onReminderSettingsSaved(true,'Reminders saved.');");
    }catch(Exception e){
      js("window.onReminderSettingsSaved&&window.onReminderSettingsSaved(false,"+JSONObject.quote(e.getMessage()==null?"Could not save reminders":e.getMessage())+");");
    }
  }

  private void requestReminderPermissionNative(){
    if(Build.VERSION.SDK_INT>=33&&checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=android.content.pm.PackageManager.PERMISSION_GRANTED){
      runOnUiThread(()->requestPermissions(new String[]{android.Manifest.permission.POST_NOTIFICATIONS},7420));
    }
  }

  private JSONArray backupHistoryArray(JSONObject env){
    JSONArray h=env.optJSONArray("history");return h==null?new JSONArray():h;
  }

  private void pushCurrentDeviceIntoHistory(JSONObject out) throws Exception{
    if(!out.has("device"))return;
    JSONObject device=out.optJSONObject("device");if(device==null)return;
    long saved=device.optLong("savedAt",out.optLong("savedAt",System.currentTimeMillis()));
    String id=String.valueOf(saved);
    JSONArray old=backupHistoryArray(out),next=new JSONArray();
    JSONObject entry=new JSONObject();entry.put("id",id);entry.put("savedAt",saved);entry.put("device",device);next.put(entry);
    for(int i=0;i<old.length()&&next.length()<5;i++){
      JSONObject e=old.optJSONObject(i);if(e==null)continue;if(id.equals(e.optString("id","")))continue;next.put(e);
    }
    out.put("history",next);
  }

  private void cloudBackupHistoryListNative(){
    StorageReference ref=backupRef();
    if(ref==null){js("window.onCloudBackupHistoryError&&window.onCloudBackupHistoryError('Please sign in with a verified account first');");return;}
    ref.getBytes(25L*1024L*1024L).addOnSuccessListener(bytes->{
      try{
        JSONObject env=new JSONObject(new String(bytes,StandardCharsets.UTF_8));JSONArray h=backupHistoryArray(env),list=new JSONArray();
        for(int i=0;i<h.length();i++){JSONObject e=h.optJSONObject(i);if(e==null)continue;JSONObject row=new JSONObject();row.put("id",e.optString("id",""));row.put("savedAt",e.optLong("savedAt",0L));list.put(row);}
        js("window.onCloudBackupHistory&&window.onCloudBackupHistory("+list.toString()+");");
      }catch(Exception e){js("window.onCloudBackupHistoryError&&window.onCloudBackupHistoryError('Backup history is invalid.');");}
    }).addOnFailureListener(e->js("window.onCloudBackupHistoryError&&window.onCloudBackupHistoryError("+JSONObject.quote(e.getMessage()==null?"Could not load backup history":e.getMessage())+");"));
  }

  private void deliverHistoryRestoreAfterAuth(String uid,String historyId){
    StorageReference ref=backupRef();
    if(ref==null){js("window.onCloudRestoreError&&window.onCloudRestoreError('Please sign in with a verified account first');");return;}
    ref.getBytes(25L*1024L*1024L).addOnSuccessListener(bytes->{
      try{
        JSONObject env=new JSONObject(new String(bytes,StandardCharsets.UTF_8));JSONArray h=backupHistoryArray(env);JSONObject found=null;
        for(int i=0;i<h.length();i++){JSONObject e=h.optJSONObject(i);if(e!=null&&historyId.equals(e.optString("id",""))){found=e;break;}}
        if(found==null)throw new IllegalArgumentException("Restore point was not found.");
        JSONObject device=found.optJSONObject("device");if(device==null)throw new IllegalArgumentException("Restore point has no device backup.");
        String plain=decryptDeviceBackup(uid,device.toString());
        js("window.onDeviceCloudRestore&&window.onDeviceCloudRestore("+JSONObject.quote(plain)+");");
      }catch(Exception e){js("window.onCloudRestoreError&&window.onCloudRestoreError("+JSONObject.quote(e.getMessage()==null?"Could not restore backup history":e.getMessage())+");");}
    }).addOnFailureListener(e->js("window.onCloudRestoreError&&window.onCloudRestoreError("+JSONObject.quote(e.getMessage()==null?"Could not load restore point":e.getMessage())+");"));
  }

  private void secureCloudRestoreHistoryNative(String historyId){
    FirebaseUser u=auth==null?null:auth.getCurrentUser();
    if(u==null||!u.isEmailVerified()){js("window.onCloudRestoreError&&window.onCloudRestoreError('Please sign in with a verified account first');");return;}
    String id=historyId==null?"":historyId.trim();if(!id.matches("^[0-9]{10,20}$")){js("window.onCloudRestoreError&&window.onCloudRestoreError('Restore point is invalid.');");return;}
    deviceAuthenticate("Restore Backup","Verify with your phone security.",()->deliverHistoryRestoreAfterAuth(u.getUid(),id),msg->js("window.onCloudRestoreError&&window.onCloudRestoreError("+JSONObject.quote(msg)+");"));
  }

'''
if 'private String appLockStateNative()' not in s:
    if method_anchor not in s: raise SystemExit('v14 method anchor missing')
    s=s.replace(method_anchor,methods+method_anchor,1)

old_copy='''        if(old.has("legacy"))out.put("legacy",old.get("legacy"));'''
new_copy='''        if(old.has("legacy"))out.put("legacy",old.get("legacy"));
        if(old.has("history"))out.put("history",old.get("history"));'''
if 'if(old.has("history"))out.put("history",old.get("history"));' not in s:
    if old_copy not in s: raise SystemExit('v14 composite history copy anchor missing')
    s=s.replace(old_copy,new_copy,1)

old_replace='''        if(devicePayload!=null)out.put("device",new JSONObject(devicePayload));
        if(transferPayload!=null)out.put("transfer",new JSONObject(transferPayload));'''
new_replace='''        if(devicePayload!=null){
          pushCurrentDeviceIntoHistory(out);
          out.put("device",new JSONObject(devicePayload));
        }
        if(transferPayload!=null)out.put("transfer",new JSONObject(transferPayload));'''
if 'pushCurrentDeviceIntoHistory(out);' not in s:
    if old_replace not in s: raise SystemExit('v14 device history anchor missing')
    s=s.replace(old_replace,new_replace,1)

diag_anchor='''      o.put("safeBrowsing",diagnosticsSafeBrowsing);'''
diag_new='''      o.put("safeBrowsing",diagnosticsSafeBrowsing);
      o.put("appLockEnabled",appLockEnabledNative());
      o.put("reminderPermission",ReminderManager.permissionState(this));'''
if 'o.put("appLockEnabled",appLockEnabledNative());' not in s:
    if diag_anchor not in s: raise SystemExit('v14 diagnostics security anchor missing')
    s=s.replace(diag_anchor,diag_new,1)

diag_cloud_anchor='''        out.put("hasLegacy",legacy);'''
diag_cloud_new='''        out.put("hasLegacy",legacy);
        JSONArray hist=env.optJSONArray("history");out.put("historyCount",hist==null?0:hist.length());'''
if 'out.put("historyCount"' not in s:
    if diag_cloud_anchor not in s: raise SystemExit('v14 diagnostics history anchor missing')
    s=s.replace(diag_cloud_anchor,diag_cloud_new,1)

lifecycle_anchor='''  @Override protected void onActivityResult(int r,int c,Intent d){'''
lifecycle='''  @Override protected void onPause(){
    if(appLockEnabledNative()&&!appLockPromptActive)appLockBackgroundAt=System.currentTimeMillis();
    super.onPause();
  }

  @Override protected void onResume(){
    super.onResume();
    if(appLockEnabledNative())runOnUiThread(()->maybePromptAppLock());
  }

'''
if '@Override protected void onPause(){' not in s:
    if lifecycle_anchor not in s: raise SystemExit('v14 lifecycle anchor missing')
    s=s.replace(lifecycle_anchor,lifecycle+lifecycle_anchor,1)

bridge_anchor='''    @JavascriptInterface public void clearDiagnosticsCache(){new Thread(() -> MainActivity.this.clearDiagnosticsCacheNative()).start();}\n'''
bridge_add='''    @JavascriptInterface public String reminderSettings(){return ReminderManager.settingsJson(MainActivity.this).toString();}
    @JavascriptInterface public void saveReminderSettings(String json){MainActivity.this.saveReminderSettingsNative(json);}
    @JavascriptInterface public void requestNotificationPermission(){MainActivity.this.requestReminderPermissionNative();}
    @JavascriptInterface public void syncTodayPunchState(String date,String checkIn,String checkOut){ReminderManager.syncTodayState(MainActivity.this,date,checkIn,checkOut);}
    @JavascriptInterface public void sendTestReminder(){ReminderManager.showNotification(MainActivity.this,ReminderManager.TYPE_MISSED,true);}
    @JavascriptInterface public String appLockState(){return MainActivity.this.appLockStateNative();}
    @JavascriptInterface public void setAppLockConfig(boolean enabled,int timeoutSeconds){MainActivity.this.setAppLockConfigNative(enabled,timeoutSeconds);}
    @JavascriptInterface public void cloudBackupHistoryList(){MainActivity.this.cloudBackupHistoryListNative();}
    @JavascriptInterface public void secureCloudRestoreHistory(String historyId){MainActivity.this.secureCloudRestoreHistoryNative(historyId);}
'''
if '@JavascriptInterface public String reminderSettings()' not in s:
    if bridge_anchor not in s: raise SystemExit('v14 bridge anchor missing')
    s=s.replace(bridge_anchor,bridge_anchor+bridge_add,1)

p.write_text(s,encoding='utf-8')
print('v14 native reminders, app lock and embedded backup history patch applied')
