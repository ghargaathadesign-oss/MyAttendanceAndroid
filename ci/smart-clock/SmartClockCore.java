package com.personal.attendance;

/** Pure transition state: detections never write attendance. */
public final class SmartClockCore {
  public static final int ENTER=1, EXIT=2, DWELL=4;
  public static final class State {public long pendingEntry;public boolean inside;}
  public static long accept(State s,int transition,long now){
    if(transition==ENTER){if(!s.inside&&s.pendingEntry==0)s.pendingEntry=now;return 0;}
    if(transition==DWELL){if(s.inside)return 0;long arrival=s.pendingEntry>0&&s.pendingEntry<=now?s.pendingEntry:now;s.pendingEntry=0;s.inside=true;return arrival;}
    if(transition==EXIT){s.pendingEntry=0;if(!s.inside)return 0;s.inside=false;return now;}
    return 0;
  }
}
