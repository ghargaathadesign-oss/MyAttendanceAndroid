from pathlib import Path
import shutil
base=Path('app/src/main/java/com/personal/attendance')
def rep(s,a,b):
 if a not in s:raise SystemExit('Missing native Smart Clock anchor '+a[:100])
 return s.replace(a,b,1)
f=base/'MainActivity.java';s=f.read_text()
s=rep(s,'  private void pushAuthState(){','  private void pushAuthState(){\n    SmartClockManager.refresh(this);')
s=rep(s,'    super.onResume();','    super.onResume();\n    SmartClockManager.refresh(this);\n    smartClockChanged("");')
anchor='  private void js(String code)'
methods='''  public void smartClockChanged(String message){js("window.onSmartClockState&&window.onSmartClockState("+JSONObject.quote(message==null?"":message)+");");}
  public void smartClockOffice(double latitude,double longitude,float accuracy){js("window.onSmartClockOffice&&window.onSmartClockOffice("+latitude+","+longitude+","+accuracy+");");}
  @Override public void onRequestPermissionsResult(int requestCode,String[] permissions,int[] grantResults){super.onRequestPermissionsResult(requestCode,permissions,grantResults);if(requestCode==SmartClockManager.LOCATION_PERMISSION){SmartClockManager.refresh(this);smartClockChanged("");}}
'''
s=rep(s,anchor,methods+anchor)
s=rep(s,'    @JavascriptInterface public String reminderSettings()', '''    @JavascriptInterface public String smartClockState(){return SmartClockManager.snapshot(MainActivity.this);}
    @JavascriptInterface public void saveSmartClock(String json){runOnUiThread(()->SmartClockManager.save(MainActivity.this,json));}
    @JavascriptInterface public void clearSmartClockTimes(){runOnUiThread(()->SmartClockManager.clear(MainActivity.this));}
    @JavascriptInterface public void requestSmartClockPermissions(){runOnUiThread(()->SmartClockManager.requestPermissions(MainActivity.this));}
    @JavascriptInterface public void captureSmartClockOffice(){runOnUiThread(()->{try{SmartClockManager.captureOffice(MainActivity.this);}catch(Exception e){smartClockChanged("Could not read current location. Check location permission.");}});}
    @JavascriptInterface public String reminderSettings()''')
s=rep(s,'  private void deleteUserCryptoArtifacts(String uid){','  private void deleteUserCryptoArtifacts(String uid){\n    SmartClockManager.forget(this,uid);')
f.write_text(s)
for name in ['SmartClockCore.java','SmartClockManager.java','SmartClockReceiver.java']:shutil.copy(Path('ci/smart-clock')/name,base/name)
f=base/'ReminderManager.java';s=f.read_text();s=rep(s,'SharedPreferences p=prefs(c);if(TYPE_CLOCK_IN.equals(type))', 'SharedPreferences p=prefs(c);if(!p.getBoolean("masterEnabled",true))return false;if(TYPE_CLOCK_IN.equals(type))');s=rep(s,'      o.put("clockInEnabled",', '      o.put("masterEnabled",p.getBoolean("masterEnabled",true));\n      o.put("clockInEnabled",');s=rep(s,'    e.putBoolean("clockInEnabled",', '    e.putBoolean("masterEnabled",o.optBoolean("masterEnabled",true));\n    e.putBoolean("clockInEnabled",');f.write_text(s)
f=Path('app/src/main/AndroidManifest.xml');s=f.read_text();s=rep(s,'    <uses-permission android:name="android.permission.INTERNET" />','''    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />''');s=rep(s,'        <provider','''        <receiver android:name=".SmartClockReceiver" android:exported="false">
            <intent-filter><action android:name="android.intent.action.BOOT_COMPLETED" /><action android:name="android.intent.action.MY_PACKAGE_REPLACED" /></intent-filter>
        </receiver>
        <provider''');f.write_text(s)
print('Native geofencing, encrypted per-account suggestions and separate location permissions prepared')
