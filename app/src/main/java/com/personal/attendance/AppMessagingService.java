package com.personal.attendance;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;

import androidx.core.app.NotificationCompat;
import androidx.core.content.ContextCompat;

import com.google.firebase.FirebaseApp;
import com.google.firebase.FirebaseOptions;
import com.google.firebase.messaging.FirebaseMessaging;
import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.Map;

public class AppMessagingService extends FirebaseMessagingService {
  private static final String PREFS="attendance_push_v15";
  private static final String KEY_INBOX="inbox";
  private static final String CHANNEL_ID="attendance_updates";
  private static final int MAX_ITEMS=60;
  private static final String FIREBASE_APP_ID="1:312314814209:android:764780f6a72c65b9a38500";
  private static final String FIREBASE_PROJECT_ID="my-attendance-c5c23";
  private static final String FIREBASE_STORAGE_BUCKET="my-attendance-c5c23.firebasestorage.app";
  private static final String FIREBASE_SENDER_ID="312314814209";

  @Override public void onCreate(){
    super.onCreate();
    ensureFirebase(this);
    ensureChannel(this);
  }

  @Override public void onNewToken(String token){
    super.onNewToken(token);
    ensureFirebase(this);
    ensureSubscribed(this);
  }

  @Override public void onMessageReceived(RemoteMessage message){
    super.onMessageReceived(message);
    ensureChannel(this);
    JSONObject item=fromRemoteMessage(message);
    if(item==null)return;
    saveItem(this,item);
    showSystemNotification(this,item);
  }

  public static void ensureFirebase(Context context){
    try{
      if(!FirebaseApp.getApps(context).isEmpty())return;
      String apiKey=BuildConfig.FIREBASE_API_KEY;
      if(apiKey==null||apiKey.trim().isEmpty())return;
      FirebaseOptions options=new FirebaseOptions.Builder()
        .setApiKey(apiKey)
        .setApplicationId(FIREBASE_APP_ID)
        .setProjectId(FIREBASE_PROJECT_ID)
        .setStorageBucket(FIREBASE_STORAGE_BUCKET)
        .setGcmSenderId(FIREBASE_SENDER_ID)
        .build();
      FirebaseApp.initializeApp(context,options);
    }catch(Exception ignored){}
  }

  public static void ensureSubscribed(Context context){
    try{
      ensureFirebase(context);
      FirebaseMessaging fm=FirebaseMessaging.getInstance();
      fm.subscribeToTopic("attendance_all");
      fm.subscribeToTopic("attendance_updates");
    }catch(Exception ignored){}
  }

  private static SharedPreferences prefs(Context context){return context.getSharedPreferences(PREFS,Context.MODE_PRIVATE);}
  private static JSONArray inbox(Context context){
    try{return new JSONArray(prefs(context).getString(KEY_INBOX,"[]"));}
    catch(Exception e){return new JSONArray();}
  }

  private static String pick(Map<String,String> data,String key){
    if(data==null)return "";
    String v=data.get(key);return v==null?"":v.trim();
  }

  private static String pick(Bundle data,String key){
    if(data==null)return "";
    Object v=data.get(key);return v==null?"":String.valueOf(v).trim();
  }

  private static int intValue(String value){try{return Integer.parseInt(value);}catch(Exception e){return 0;}}

  private static JSONObject fromRemoteMessage(RemoteMessage message){
    try{
      Map<String,String> data=message.getData();
      RemoteMessage.Notification n=message.getNotification();
      String id=pick(data,"id");if(id.isEmpty())id=message.getMessageId();if(id==null||id.isEmpty())id=String.valueOf(System.currentTimeMillis());
      String type=pick(data,"type");if(type.isEmpty())type="general";
      String title=pick(data,"title");if(title.isEmpty()&&n!=null&&n.getTitle()!=null)title=n.getTitle();
      String body=pick(data,"body");if(body.isEmpty()&&n!=null&&n.getBody()!=null)body=n.getBody();
      if(title.isEmpty())title="update".equalsIgnoreCase(type)?"App update available":"My Attendance";
      JSONObject o=new JSONObject();
      o.put("id",id);o.put("type",type.toLowerCase());o.put("title",title);o.put("body",body);
      o.put("version",pick(data,"version"));o.put("versionCode",intValue(pick(data,"versionCode")));
      o.put("apkUrl",pick(data,"apkUrl"));o.put("sha256",pick(data,"sha256"));o.put("changelog",pick(data,"changelog"));
      o.put("receivedAt",System.currentTimeMillis());o.put("read",false);
      return o;
    }catch(Exception e){return null;}
  }

  private static JSONObject fromLaunchBundle(Bundle b){
    try{
      String type=pick(b,"type");
      String title=pick(b,"title");if(title.isEmpty())title=pick(b,"gcm.n.title");
      String body=pick(b,"body");if(body.isEmpty())body=pick(b,"gcm.n.body");
      String id=pick(b,"id");if(id.isEmpty())id=pick(b,"google.message_id");
      boolean meaningful=!type.isEmpty()||!title.isEmpty()||!body.isEmpty()||!pick(b,"apkUrl").isEmpty();
      if(!meaningful)return null;
      if(id.isEmpty())id=String.valueOf(System.currentTimeMillis());
      if(type.isEmpty())type="general";
      if(title.isEmpty())title="update".equalsIgnoreCase(type)?"App update available":"My Attendance";
      JSONObject o=new JSONObject();
      o.put("id",id);o.put("type",type.toLowerCase());o.put("title",title);o.put("body",body);
      o.put("version",pick(b,"version"));o.put("versionCode",intValue(pick(b,"versionCode")));
      o.put("apkUrl",pick(b,"apkUrl"));o.put("sha256",pick(b,"sha256"));o.put("changelog",pick(b,"changelog"));
      o.put("receivedAt",System.currentTimeMillis());o.put("read",false);
      return o;
    }catch(Exception e){return null;}
  }

  public static synchronized void saveItem(Context context,JSONObject item){
    if(item==null)return;
    try{
      String id=item.optString("id","");
      JSONArray old=inbox(context),out=new JSONArray();
      out.put(item);
      for(int i=0;i<old.length()&&out.length()<MAX_ITEMS;i++){
        JSONObject x=old.optJSONObject(i);if(x==null)continue;
        if(!id.isEmpty()&&id.equals(x.optString("id","")))continue;
        out.put(x);
      }
      prefs(context).edit().putString(KEY_INBOX,out.toString()).apply();
    }catch(Exception ignored){}
  }

  public static synchronized JSONObject state(Context context){
    JSONObject out=new JSONObject();
    try{
      JSONArray a=inbox(context);int unread=0;
      for(int i=0;i<a.length();i++){JSONObject x=a.optJSONObject(i);if(x!=null&&!x.optBoolean("read",false))unread++;}
      out.put("items",a);out.put("unread",unread);out.put("permission",permissionState(context));
      out.put("versionName",BuildConfig.VERSION_NAME);out.put("versionCode",BuildConfig.VERSION_CODE);
    }catch(Exception ignored){}
    return out;
  }

  public static synchronized void markAllRead(Context context){
    try{
      JSONArray a=inbox(context);for(int i=0;i<a.length();i++){JSONObject x=a.optJSONObject(i);if(x!=null)x.put("read",true);}
      prefs(context).edit().putString(KEY_INBOX,a.toString()).apply();
    }catch(Exception ignored){}
  }

  public static synchronized void markRead(Context context,String id){
    if(id==null||id.trim().isEmpty())return;
    try{
      JSONArray a=inbox(context);for(int i=0;i<a.length();i++){JSONObject x=a.optJSONObject(i);if(x!=null&&id.equals(x.optString("id","")))x.put("read",true);}
      prefs(context).edit().putString(KEY_INBOX,a.toString()).apply();
    }catch(Exception ignored){}
  }

  public static synchronized void clear(Context context){prefs(context).edit().remove(KEY_INBOX).apply();}

  public static String permissionState(Context context){
    if(Build.VERSION.SDK_INT<33)return "not_required";
    return ContextCompat.checkSelfPermission(context,android.Manifest.permission.POST_NOTIFICATIONS)==android.content.pm.PackageManager.PERMISSION_GRANTED?"granted":"denied";
  }

  public static boolean captureLaunchIntent(Context context,Intent intent){
    if(intent==null)return false;
    boolean open=intent.getBooleanExtra("open_notifications",false);
    Bundle b=intent.getExtras();
    if(b!=null){
      JSONObject item=fromLaunchBundle(b);
      if(item!=null){saveItem(context,item);open=true;}
    }
    return open;
  }

  private static void ensureChannel(Context context){
    if(Build.VERSION.SDK_INT<26)return;
    NotificationManager nm=(NotificationManager)context.getSystemService(Context.NOTIFICATION_SERVICE);if(nm==null)return;
    NotificationChannel ch=new NotificationChannel(CHANNEL_ID,"My Attendance updates",NotificationManager.IMPORTANCE_DEFAULT);
    ch.setDescription("App updates and important My Attendance notifications");nm.createNotificationChannel(ch);
  }

  private static void showSystemNotification(Context context,JSONObject item){
    try{
      if("denied".equals(permissionState(context)))return;
      ensureChannel(context);
      Intent open=new Intent(context,MainActivity.class);open.putExtra("open_notifications",true);open.putExtra("push_id",item.optString("id",""));
      open.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP);
      int request=Math.abs(item.optString("id",String.valueOf(System.currentTimeMillis())).hashCode());
      int flags=PendingIntent.FLAG_UPDATE_CURRENT;if(Build.VERSION.SDK_INT>=23)flags|=PendingIntent.FLAG_IMMUTABLE;
      PendingIntent pi=PendingIntent.getActivity(context,request,open,flags);
      NotificationCompat.Builder b=new NotificationCompat.Builder(context,CHANNEL_ID)
        .setSmallIcon(R.drawable.ic_notification)
        .setContentTitle(item.optString("title","My Attendance"))
        .setContentText(item.optString("body",""))
        .setStyle(new NotificationCompat.BigTextStyle().bigText(item.optString("body","")))
        .setAutoCancel(true).setContentIntent(pi).setPriority(NotificationCompat.PRIORITY_DEFAULT);
      NotificationManager nm=(NotificationManager)context.getSystemService(Context.NOTIFICATION_SERVICE);if(nm!=null)nm.notify(request,b.build());
    }catch(Exception ignored){}
  }
}
