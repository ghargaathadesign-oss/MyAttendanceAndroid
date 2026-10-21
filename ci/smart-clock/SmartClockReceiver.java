package com.personal.attendance;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import com.google.android.gms.location.Geofence;
import com.google.android.gms.location.GeofencingEvent;
public final class SmartClockReceiver extends BroadcastReceiver {
  @Override public void onReceive(Context c,Intent i){if(i==null)return;if(Intent.ACTION_BOOT_COMPLETED.equals(i.getAction())||Intent.ACTION_MY_PACKAGE_REPLACED.equals(i.getAction())){SmartClockManager.reboot(c);return;}GeofencingEvent e=GeofencingEvent.fromIntent(i);if(e==null)return;if(e.hasError()){SmartClockManager.unavailable(c);return;}if(e.getTriggeringGeofences()!=null)for(Geofence f:e.getTriggeringGeofences())SmartClockManager.event(c,f.getRequestId(),e.getGeofenceTransition());}
}
