package com.personal.attendance;
public final class SmartClockCoreTest {
  private static void eq(long expected,long actual){if(expected!=actual)throw new AssertionError(expected+" != "+actual);}
  public static void main(String[] args){SmartClockCore.State s=new SmartClockCore.State();eq(0,SmartClockCore.accept(s,2,1000));eq(0,SmartClockCore.accept(s,1,2000));eq(0,SmartClockCore.accept(s,2,3000));eq(0,s.pendingEntry);eq(0,SmartClockCore.accept(s,1,4000));eq(0,SmartClockCore.accept(s,1,5000));eq(4000,SmartClockCore.accept(s,4,124000));eq(0,SmartClockCore.accept(s,4,125000));eq(130000,SmartClockCore.accept(s,2,130000));eq(0,SmartClockCore.accept(s,2,131000));eq(150000,SmartClockCore.accept(s,4,150000));eq(180000,SmartClockCore.accept(s,2,180000));eq(0,SmartClockCore.accept(s,99,190000));System.out.println("Smart Clock transition core passed: pass-by suppression, dwell, duplicate events, repeated visits and exit ordering");}
}
