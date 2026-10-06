package com.personal.attendance;

import android.Manifest;
import android.app.AlarmManager;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;

import androidx.core.app.NotificationCompat;
import androidx.core.content.ContextCompat;

import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

public final class ReminderManager {
  static final String PREFS="attendance_reminders_v14";
  static final String CHANNEL_ID="attendance_reminders";
  static final String TYPE_CLOCK_IN="clock_in";
  static final String TYPE_CLOCK_OUT="clock_out";
  static final String TYPE_MISSED="missed";
  private ReminderManager(){}

  static SharedPreferences prefs(Context c){return c.getSharedPreferences(PREFS,Context.MODE_PRIVATE);}
  static String today(){return new SimpleDateFormat("yyyy-MM-dd",Locale.US).format(new Date());}
  static String safeTime(String v,String fallback){return v!=null&&v.matches("^(?:[01]\\d|2[0-3]):[0-5]\\d$")?v:fallback;}
  static boolean enabled(Context c,String type){SharedPreferences p=prefs(c);if(TYPE_CLOCK_IN.equals(type))return p.getBoolean("clockInEnabled",false);if(TYPE_CLOCK_OUT.equals(type))return p.getBoolean("clockOutEnabled",false);return p.getBoolean("missedEnabled",false);}
  static String time(Context c,String type){SharedPreferences p=prefs(c);if(TYPE_CLOCK_IN.equals(type))return safeTime(p.getString("clockInTime","09:30"),"09:30");if(TYPE_CLOCK_OUT.equals(type))return safeTime(p.getString("clockOutTime","18:30"),"18:30");return safeTime(p.getString("missedTime","21:00"),"21:00");}
  static int requestCode(String type){return TYPE_CLOCK_IN.equals(type)?7401:TYPE_CLOCK_OUT.equals(type)?7402:7403;}

  public static JSONObject settingsJson(Context c){
    SharedPreferences p=prefs(c);JSONObject o=new JSONObject();
    try{
      o.put("clockInEnabled",p.getBoolean("clockInEnabled",false));o.put("clockInTime",safeTime(p.getString("clockInTime","09:30"),"09:30"));
      o.put("clockOutEnabled",p.getBoolean("clockOutEnabled",false));o.put("clockOutTime",safeTime(p.getString("clockOutTime","18:30"),"18:30"));
      o.put("missedEnabled",p.getBoolean("missedEnabled",false));o.put("missedTime",safeTime(p.getString("missedTime","21:00"),"21:00"));
      o.put("permission",permissionState(c));
    }catch(Exception ignored){}
    return o;
  }

  public static void saveSettings(Context c,String json) throws Exception{
    JSONObject o=new JSONObject(json==null?"{}":json);SharedPreferences.Editor e=prefs(c).edit();
    e.putBoolean("clockInEnabled",o.optBoolean("clockInEnabled",false));e.putString("clockInTime",safeTime(o.optString("clockInTime","09:30"),"09:30"));
    e.putBoolean("clockOutEnabled",o.optBoolean("clockOutEnabled",false));e.putString("clockOutTime",safeTime(o.optString("clockOutTime","18:30"),"18:30"));
    e.putBoolean("missedEnabled",o.optBoolean("missedEnabled",false));e.putString("missedTime",safeTime(o.optString("missedTime","21:00"),"21:00"));e.apply();
    createChannel(c);scheduleAll(c);
  }

  public static void syncTodayState(Context c,String date,String checkIn,String checkOut){prefs(c).edit().putString("todayDate",date==null?"":date).putString("todayCheckIn",checkIn==null?"":checkIn).putString("todayCheckOut",checkOut==null?"":checkOut).apply();}
  public static String permissionState(Context c){if(Build.VERSION.SDK_INT<33)return"not_required";return ContextCompat.checkSelfPermission(c,Manifest.permission.POST_NOTIFICATIONS)==PackageManager.PERMISSION_GRANTED?"granted":"not_granted";}
  public static void createChannel(Context c){if(Build.VERSION.SDK_INT>=26){NotificationManager n=(NotificationManager)c.getSystemService(Context.NOTIFICATION_SERVICE);if(n!=null){NotificationChannel ch=new NotificationChannel(CHANNEL_ID,"Attendance reminders",NotificationManager.IMPORTANCE_DEFAULT);ch.setDescription("Clock-in, clock-out and missed-punch reminders");n.createNotificationChannel(ch);}}}

  static PendingIntent pending(Context c,String type){Intent i=new Intent(c,ReminderReceiver.class).setAction("com.personal.attendance.REMINDER").putExtra("type",type);return PendingIntent.getBroadcast(c,requestCode(type),i,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);}
  public static void cancel(Context c,String type){AlarmManager am=(AlarmManager)c.getSystemService(Context.ALARM_SERVICE);if(am!=null)am.cancel(pending(c,type));}
  public static void scheduleAll(Context c){scheduleType(c,TYPE_CLOCK_IN);scheduleType(c,TYPE_CLOCK_OUT);scheduleType(c,TYPE_MISSED);}
  public static void scheduleType(Context c,String type){
    if(!enabled(c,type)){cancel(c,type);return;}String[] t=time(c,type).split(":");Calendar cal=Calendar.getInstance();cal.set(Calendar.HOUR_OF_DAY,Integer.parseInt(t[0]));cal.set(Calendar.MINUTE,Integer.parseInt(t[1]));cal.set(Calendar.SECOND,0);cal.set(Calendar.MILLISECOND,0);if(cal.getTimeInMillis()<=System.currentTimeMillis())cal.add(Calendar.DAY_OF_YEAR,1);AlarmManager am=(AlarmManager)c.getSystemService(Context.ALARM_SERVICE);if(am!=null)am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,cal.getTimeInMillis(),pending(c,type));
  }

  public static boolean shouldNotify(Context c,String type){
    if(!enabled(c,type))return false;SharedPreferences p=prefs(c);boolean same=today().equals(p.getString("todayDate",""));String in=same?p.getString("todayCheckIn",""):"",out=same?p.getString("todayCheckOut",""):"";
    if(TYPE_CLOCK_IN.equals(type))return in==null||in.isEmpty();
    if(TYPE_CLOCK_OUT.equals(type))return in!=null&&!in.isEmpty()&&(out==null||out.isEmpty());
    return in==null||in.isEmpty()||out==null||out.isEmpty();
  }

  public static void showNotification(Context c,String type,boolean force){
    if(!force&&!shouldNotify(c,type))return;if(Build.VERSION.SDK_INT>=33&&ContextCompat.checkSelfPermission(c,Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)return;createChannel(c);
    String title="My Attendance",body;
    if(TYPE_CLOCK_IN.equals(type))body="Time to clock in.";else if(TYPE_CLOCK_OUT.equals(type))body="You are still clocked in. Remember to clock out.";else body="Today's attendance looks incomplete. Check your punches.";
    Intent open=new Intent(c,MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TOP);PendingIntent content=PendingIntent.getActivity(c,7800+requestCode(type),open,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
    NotificationCompat.Builder b=new NotificationCompat.Builder(c,CHANNEL_ID).setSmallIcon(com.personal.attendance.R.drawable.app_icon).setContentTitle(title).setContentText(body).setAutoCancel(true).setContentIntent(content).setPriority(NotificationCompat.PRIORITY_DEFAULT);
    NotificationManager n=(NotificationManager)c.getSystemService(Context.NOTIFICATION_SERVICE);if(n!=null)n.notify(8000+requestCode(type),b.build());
  }
}
