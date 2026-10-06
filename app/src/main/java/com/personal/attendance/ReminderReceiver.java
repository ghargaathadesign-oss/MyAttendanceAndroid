package com.personal.attendance;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public class ReminderReceiver extends BroadcastReceiver {
  @Override public void onReceive(Context context,Intent intent){
    if(intent==null)return;String action=intent.getAction();
    if(Intent.ACTION_BOOT_COMPLETED.equals(action)){ReminderManager.scheduleAll(context);return;}
    String type=intent.getStringExtra("type");if(type==null)return;
    ReminderManager.showNotification(context,type,false);ReminderManager.scheduleType(context,type);
  }
}
