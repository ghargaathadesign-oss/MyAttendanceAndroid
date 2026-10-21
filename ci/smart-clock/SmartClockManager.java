package com.personal.attendance;

import android.Manifest;
import android.app.Activity;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationManager;
import android.os.Build;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;
import androidx.core.content.ContextCompat;
import com.google.android.gms.location.Geofence;
import com.google.android.gms.location.GeofencingRequest;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.location.Priority;
import com.google.android.gms.tasks.CancellationTokenSource;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import org.json.JSONArray;
import org.json.JSONObject;
import java.security.KeyStore;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.UUID;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

public final class SmartClockManager {
  public static final int LOCATION_PERMISSION=7828;
  private static final String PREFS="smart_clock_private_v1",ALIAS="attendance_smart_clock_v1";
  private static final Object LOCK=new Object();
  private static boolean processRegistered=false;
  private SmartClockManager(){}
  private static SharedPreferences prefs(Context c){return c.getSharedPreferences(PREFS,Context.MODE_PRIVATE);}
  private static String owner(){try{FirebaseUser u=FirebaseAuth.getInstance().getCurrentUser();return u!=null&&u.isEmailVerified()?u.getUid():"";}catch(Exception e){return "";}}
  private static SecretKey key() throws Exception {KeyStore k=KeyStore.getInstance("AndroidKeyStore");k.load(null);if(k.containsAlias(ALIAS))return (SecretKey)k.getKey(ALIAS,null);KeyGenerator g=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");g.init(new KeyGenParameterSpec.Builder(ALIAS,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT).setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build());return g.generateKey();}
  private static JSONObject read(Context c,String uid){if(uid.isEmpty())return new JSONObject();try{String raw=prefs(c).getString("user_"+uid,"");if(raw.isEmpty())return new JSONObject();String[] p=raw.split(":");Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.DECRYPT_MODE,key(),new GCMParameterSpec(128,Base64.decode(p[0],Base64.NO_WRAP)));cipher.updateAAD(uid.getBytes(java.nio.charset.StandardCharsets.UTF_8));return new JSONObject(new String(cipher.doFinal(Base64.decode(p[1],Base64.NO_WRAP)),java.nio.charset.StandardCharsets.UTF_8));}catch(Exception e){return new JSONObject();}}
  private static void write(Context c,String uid,JSONObject o) throws Exception {if(uid.isEmpty())throw new Exception("Sign in to use Smart Clock.");Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.ENCRYPT_MODE,key());cipher.updateAAD(uid.getBytes(java.nio.charset.StandardCharsets.UTF_8));String raw=Base64.encodeToString(cipher.getIV(),Base64.NO_WRAP)+":"+Base64.encodeToString(cipher.doFinal(o.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8)),Base64.NO_WRAP);if(!prefs(c).edit().putString("user_"+uid,raw).commit())throw new Exception("Could not save Smart Clock.");}
  public static boolean fine(Context c){return ContextCompat.checkSelfPermission(c,Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED;}
  public static boolean background(Context c){return Build.VERSION.SDK_INT<29||ContextCompat.checkSelfPermission(c,Manifest.permission.ACCESS_BACKGROUND_LOCATION)==PackageManager.PERMISSION_GRANTED;}
  private static boolean locationOn(Context c){LocationManager m=(LocationManager)c.getSystemService(Context.LOCATION_SERVICE);return m!=null&&(Build.VERSION.SDK_INT>=28?m.isLocationEnabled():(m.isProviderEnabled(LocationManager.GPS_PROVIDER)||m.isProviderEnabled(LocationManager.NETWORK_PROVIDER)));}
  private static PendingIntent pending(Context c){Intent i=new Intent(c,SmartClockReceiver.class).setAction("com.personal.attendance.SMART_CLOCK");return PendingIntent.getBroadcast(c,7828,i,PendingIntent.FLAG_UPDATE_CURRENT|(Build.VERSION.SDK_INT>=31?PendingIntent.FLAG_MUTABLE:0));}
  private static String day(long time){return new SimpleDateFormat("yyyy-MM-dd",Locale.US).format(new Date(time));}
  private static String time(long value){return new SimpleDateFormat("HH:mm",Locale.US).format(new Date(value));}
  public static String snapshot(Context c){synchronized(LOCK){String uid=owner();JSONObject o=read(c,uid);try{o.put("signedIn",!uid.isEmpty());o.put("precisePermission",fine(c));o.put("backgroundPermission",background(c));o.put("locationOn",locationOn(c));o.put("today",day(System.currentTimeMillis()));o.put("events",todayEvents(o));o.put("monitoring",o.optBoolean("enabled")&&fine(c)&&background(c)&&locationOn(c)&&o.optString("fenceId").equals(prefs(c).getString("active","")));o.remove("pendingEntry");o.remove("inside");}catch(Exception ignored){}return o.toString();}}
  private static JSONArray todayEvents(JSONObject o){JSONArray result=new JSONArray(),events=o.optJSONArray("events");if(events!=null)for(int i=0;i<events.length();i++){JSONObject e=events.optJSONObject(i);if(e!=null&&day(System.currentTimeMillis()).equals(e.optString("date")))result.put(e);}return result;}
  public static void save(Activity c,String json){synchronized(LOCK){try{String uid=owner();JSONObject input=new JSONObject(json),o=read(c,uid);boolean enabled=input.optBoolean("enabled");double lat=input.optDouble("latitude",Double.NaN),lon=input.optDouble("longitude",Double.NaN);int radius=input.optInt("radius",150);if(enabled&&(!Double.isFinite(lat)||!Double.isFinite(lon)||lat< -90||lat>90||lon< -180||lon>180||radius<100||radius>1000))throw new Exception("Set valid office coordinates and a radius from 100 to 1000 metres.");boolean changed=o.optDouble("latitude",999)!=lat||o.optDouble("longitude",999)!=lon||o.optInt("radius",150)!=radius||o.optBoolean("enabled")!=enabled;
    o.put("enabled",enabled);if(Double.isFinite(lat))o.put("latitude",lat);if(Double.isFinite(lon))o.put("longitude",lon);o.put("radius",radius);
    if(changed){o.put("fenceId",UUID.randomUUID().toString());o.put("events",new JSONArray());o.put("pendingEntry",0);o.put("inside",false);}o.put("error","");write(c,uid,o);refresh(c);notify(c,"Saved. Location detections are suggestions only.");
  }catch(Exception e){notify(c,e.getMessage());}}}
  public static void clear(Activity c){synchronized(LOCK){try{String uid=owner();JSONObject o=read(c,uid);o.put("events",new JSONArray());o.put("pendingEntry",0);o.put("inside",false);write(c,uid,o);notify(c,"Detected times cleared.");}catch(Exception e){notify(c,"Could not clear detected times.");}}}
  public static void notify(Context c,String message){if(c instanceof MainActivity)((MainActivity)c).smartClockChanged(message);}
  private static void remove(Context c,String id){try{LocationServices.getGeofencingClient(c).removeGeofences(java.util.Collections.singletonList(id));}catch(Exception ignored){}}
  public static void refresh(Context context){Context c=context.getApplicationContext();synchronized(LOCK){if(!processRegistered){String old=prefs(c).getString("active","");if(!old.isEmpty())remove(c,old);prefs(c).edit().remove("active").apply();processRegistered=true;}String uid=owner();JSONObject o=read(c,uid);String active=prefs(c).getString("active",""),id=o.optString("fenceId");boolean allowed=!uid.isEmpty()&&o.optBoolean("enabled")&&fine(c)&&background(c)&&locationOn(c)&&!id.isEmpty();String wanted=allowed?id:"";
    if(!active.isEmpty()&&!active.equals(wanted)){remove(c,active);prefs(c).edit().remove("active").apply();}
    if(!allowed||active.equals(wanted))return;
    try{o.put("inside",false);o.put("pendingEntry",0);write(c,uid,o);Geofence fence=new Geofence.Builder().setRequestId(id).setCircularRegion(o.getDouble("latitude"),o.getDouble("longitude"),(float)o.getInt("radius")).setExpirationDuration(Geofence.NEVER_EXPIRE).setTransitionTypes(Geofence.GEOFENCE_TRANSITION_ENTER|Geofence.GEOFENCE_TRANSITION_DWELL|Geofence.GEOFENCE_TRANSITION_EXIT).setLoiteringDelay(120000).setNotificationResponsiveness(60000).build();GeofencingRequest request=new GeofencingRequest.Builder().setInitialTrigger(GeofencingRequest.INITIAL_TRIGGER_DWELL).addGeofence(fence).build();
      LocationServices.getGeofencingClient(c).addGeofences(request,pending(c)).addOnSuccessListener(v->{synchronized(LOCK){JSONObject current=read(c,uid);if(owner().equals(uid)&&current.optBoolean("enabled")&&id.equals(current.optString("fenceId"))){prefs(c).edit().putString("active",id).apply();notify(context,"");}else remove(c,id);}}).addOnFailureListener(e->{synchronized(LOCK){try{JSONObject current=read(c,uid);if(id.equals(current.optString("fenceId"))){current.put("error","Monitoring could not start. Check location permissions and Google Play services, then reopen Smart Clock.");write(c,uid,current);}}catch(Exception ignored){}notify(context,"Monitoring could not start. Check location permissions and Google Play services.");}});
    }catch(Exception e){notify(context,"Monitoring could not start. Check office settings and location permissions.");}
  }}
  public static void reboot(Context c){prefs(c).edit().remove("active").apply();refresh(c);}
  public static void unavailable(Context c){prefs(c).edit().remove("active").apply();}
  public static void event(Context c,String id,int transition){synchronized(LOCK){try{String uid=owner();JSONObject o=read(c,uid);if(uid.isEmpty()||!o.optBoolean("enabled")||!id.equals(o.optString("fenceId"))||!fine(c)||!background(c))return;long now=System.currentTimeMillis();SmartClockCore.State state=new SmartClockCore.State();state.pendingEntry=o.optLong("pendingEntry");if(state.pendingEntry>0&&!day(state.pendingEntry).equals(day(now)))state.pendingEntry=0;state.inside=o.optBoolean("inside");long stamp=SmartClockCore.accept(state,transition,now);o.put("pendingEntry",state.pendingEntry);o.put("inside",state.inside);JSONArray events=todayEvents(o);if(stamp>0){JSONObject e=new JSONObject();e.put("id",UUID.randomUUID().toString());e.put("kind",transition==SmartClockCore.EXIT?"out":"in");e.put("timestamp",stamp);e.put("date",day(stamp));e.put("time",time(stamp));events.put(e);while(events.length()>40)events.remove(1);}o.put("events",events);write(c,uid,o);}catch(Exception ignored){}}}
  public static void forget(Context c,String uid){synchronized(LOCK){JSONObject o=read(c,uid);String id=o.optString("fenceId");if(!id.isEmpty())remove(c,id);SharedPreferences.Editor e=prefs(c).edit().remove("user_"+uid);if(id.equals(prefs(c).getString("active","")))e.remove("active");e.commit();}}
  private static void requestFine(Activity a){if(prefs(a).getBoolean("foregroundAsked",false)&&!a.shouldShowRequestPermissionRationale(Manifest.permission.ACCESS_FINE_LOCATION)){new android.app.AlertDialog.Builder(a).setTitle("Enable precise location").setMessage("Smart Clock needs precise location for your office boundary. You can enable it under Permissions → Location in Android settings.").setPositiveButton("Open settings",(d,w)->a.startActivity(new Intent(android.provider.Settings.ACTION_APPLICATION_DETAILS_SETTINGS,android.net.Uri.parse("package:"+a.getPackageName())))).setNegativeButton("Cancel",null).show();return;}prefs(a).edit().putBoolean("foregroundAsked",true).apply();a.requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION,Manifest.permission.ACCESS_COARSE_LOCATION},LOCATION_PERMISSION);}
  public static void requestPermissions(Activity a){if(!fine(a)){requestFine(a);return;}if(!background(a)){if(Build.VERSION.SDK_INT==29){a.requestPermissions(new String[]{Manifest.permission.ACCESS_BACKGROUND_LOCATION},LOCATION_PERMISSION);return;}new android.app.AlertDialog.Builder(a).setTitle("Allow background location").setMessage("Smart Clock detects office arrivals and departures while the app is closed. In Android settings choose Location → Allow all the time and enable Precise location. Detected times stay on this phone and require your confirmation before attendance is saved.").setPositiveButton("Open settings",(d,w)->a.startActivity(new Intent(android.provider.Settings.ACTION_APPLICATION_DETAILS_SETTINGS,android.net.Uri.parse("package:"+a.getPackageName())))).setNegativeButton("Cancel",null).show();return;}refresh(a);notify(a,"");}
  public static void captureOffice(Activity a){if(owner().isEmpty()){notify(a,"Sign in to set your office location.");return;}if(!fine(a)){requestFine(a);notify(a,"Grant precise location, then tap Use current location again.");return;}String uid=owner();CancellationTokenSource cancel=new CancellationTokenSource();new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(cancel::cancel,20000);LocationServices.getFusedLocationProviderClient(a).getCurrentLocation(Priority.PRIORITY_HIGH_ACCURACY,cancel.getToken()).addOnSuccessListener(l->{if(!owner().equals(uid))return;if(l==null||!l.hasAccuracy()||l.getAccuracy()>150||(Build.VERSION.SDK_INT>=31?l.isMock():l.isFromMockProvider())||System.currentTimeMillis()-l.getTime()>120000){notify(a,"A precise current location was not available. Try outdoors or enter office coordinates.");return;}if(a instanceof MainActivity)((MainActivity)a).smartClockOffice(l.getLatitude(),l.getLongitude(),l.getAccuracy());}).addOnFailureListener(e->notify(a,"Could not read current location. Check GPS and try again."));}
}
