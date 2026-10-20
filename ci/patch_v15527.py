from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
def rep(s,a,b):
 if a not in s:raise SystemExit('Missing v15527 anchor '+a[:100])
 return s.replace(a,b,1)
f=p/'v15511-updates.js';s=f.read_text();s=rep(s,"var special=AttendancePolicy.isSpecial(r),left=special?0:Math.max(0,s.h*60+s.m-elapsed);", "var special=AttendancePolicy.isSpecial(r),target=AttendancePolicy.attendanceStatus(r)==='Half Day Holiday'?AttendancePolicy.requiredMinutes(r,s):s.h*60+s.m,left=special?0:Math.max(0,target-elapsed);");f.write_text(s)
f=p/'v112-fixes.js';s=f.read_text();s=rep(s,"s=getSettings(),std=s.h*60+s.m;", "s=getSettings(),std=window.AttendancePolicy&&AttendancePolicy.attendanceStatus(x)==='Half Day Holiday'?AttendancePolicy.requiredMinutes(x,s):s.h*60+s.m;");f.write_text(s)
print('v15.5.27 remaining time and progress ring follow the saved half-day holiday target')
