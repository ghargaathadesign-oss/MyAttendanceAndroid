(function(root,factory){
  var api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.AttendancePolicy=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
var VALID_STATUS={'Present':1,'Absent':1,'Paid Leave':1,'Unpaid Leave':1,'Half Day':1,'Short Day':1,'Holiday':1,'Week Off':1};
var STATUS_ALIASES={
  'p':'Present','present':'Present',
  'a':'Absent','ab':'Absent','absent':'Absent',
  'pl':'Paid Leave','paid leave':'Paid Leave','paidleave':'Paid Leave',
  'ul':'Unpaid Leave','unpaid leave':'Unpaid Leave','unpaidleave':'Unpaid Leave',
  'hd':'Half Day','half day':'Half Day','halfday':'Half Day',
  'sd':'Short Day','short':'Short Day','short day':'Short Day','shortday':'Short Day',
  'h':'Holiday','holiday':'Holiday',
  'wo':'Week Off','week off':'Week Off','weekoff':'Week Off','off':'Week Off','sunday':'Week Off'
};
function n(v,d){v=Number(v);return isFinite(v)?v:d}
function clamp(v,min,max){return Math.min(max,Math.max(min,v))}
function pad(v){return(v<10?'0':'')+v}
function normalizeSettings(input){
  input=input||{};
  var h=clamp(Math.floor(n(input.h,9)),0,23),m=clamp(Math.floor(n(input.m,0)),0,59),delay=clamp(Math.floor(n(input.otDelay,30)),0,180);
  if(h===0&&m===0)h=9;
  return{h:h,m:m,otDelay:delay,fmt:input.fmt==='24h'?'24h':'12h',leaveAccrualPerMonth:1.5,policyVersion:128};
}
function normalizeDate(v){
  var s=String(v==null?'':v).trim(),m,y,mo,d,out,dt;
  if(!s)return null;
  m=s.match(/^(\d{4})[-\/.](\d{1,2})[-\/.](\d{1,2})(?:[T\s].*)?$/);
  if(m){y=+m[1];mo=+m[2];d=+m[3]}
  else{
    m=s.match(/^(\d{1,2})[-\/.](\d{1,2})[-\/.](\d{4})$/);
    if(!m)return null;d=+m[1];mo=+m[2];y=+m[3];
  }
  if(y<2000||y>2200||mo<1||mo>12||d<1||d>31)return null;
  out=y+'-'+pad(mo)+'-'+pad(d);dt=new Date(out+'T00:00:00');
  return !isNaN(dt.getTime())&&dt.getFullYear()===y&&dt.getMonth()===mo-1&&dt.getDate()===d?out:null;
}
function normalizeTime(v){
  if(v==null)return'';
  var s=String(v).trim(),m,h,mi,amp;
  if(!s||/^(?:-|--|n\/?a|null|none)$/i.test(s))return'';
  m=s.match(/^(\d{1,2}):(\d{2})(?::\d{2})?\s*([ap]m)?$/i);
  if(!m)return null;
  h=+m[1];mi=+m[2];amp=(m[3]||'').toLowerCase();
  if(mi<0||mi>59)return null;
  if(amp){
    if(h<1||h>12)return null;
    if(amp==='am'&&h===12)h=0;else if(amp==='pm'&&h!==12)h+=12;
  }else if(h<0||h>23)return null;
  return pad(h)+':'+pad(mi);
}
function normalizeStatus(v){
  var s=String(v==null?'':v).trim();
  if(!s)return'Present';
  var key=s.toLowerCase().replace(/\s+/g,' ');
  if(STATUS_ALIASES[key])return STATUS_ALIASES[key];
  if(VALID_STATUS[s])return s;
  return null;
}
function minuteOfDay(t){var s=normalizeTime(t);if(s==null||s==='')return null;var p=s.split(':');return(+p[0])*60+(+p[1])}
function minutesBetween(a,b){var x=minuteOfDay(a),y=minuteOfDay(b);if(x==null||y==null)return 0;if(y<x)y+=1440;return Math.max(0,y-x)}
function workedMinutes(record){return record?minutesBetween(record.checkIn,record.checkOut):0}
function isSunday(date){var x=normalizeDate(date);if(!x)return false;var d=new Date(x+'T00:00:00');return d.getDay()===0}
function isSpecial(record){return !!(record&&(record.specialOT===true||normalizeStatus(record.status)==='Holiday'||normalizeStatus(record.status)==='Week Off'||isSunday(record.date)))}
function standardMinutes(settings){var s=normalizeSettings(settings);return s.h*60+s.m}
function requiredMinutes(record,settings){if(!record)return 0;var std=standardMinutes(settings),st=normalizeStatus(record.status)||'Present';if(st==='Paid Leave'||st==='Holiday'||st==='Week Off')return 0;if(st==='Half Day')return Math.round(std/2);return std}
function daily(record,settings){
  var s=normalizeSettings(settings),worked=workedMinutes(record),required=requiredMinutes(record,s),special=isSpecial(record),balance=0,st=normalizeStatus(record&&record.status)||'Present';
  if(special)balance=worked;
  else if(st==='Paid Leave'||st==='Holiday'||st==='Week Off')balance=0;
  else if(st==='Absent'||st==='Unpaid Leave')balance=-required;
  else{var diff=worked-required;balance=diff>0?Math.max(0,diff-s.otDelay):diff}
  return{worked:worked,required:required,balance:balance,overtime:Math.max(0,balance),shortfall:Math.max(0,-balance),special:special};
}
function balanceMinutes(record,settings){return daily(record,settings).balance}
function salaryMonth(records,month,settings,salary){
  var s=normalizeSettings(settings),sal=salary||{},monthly=Math.max(0,n(sal.monthly,0)),mult=clamp(n(sal.otMultiplier,1),0,5),p=String(month||'').split('-'),year=+p[0],mon=+p[1],days=(year&&mon)?new Date(year,mon,0).getDate():30,std=Math.max(1,standardMinutes(s)),dayRate=monthly/days,hourRate=dayRate/(std/60),normalOt=0,specialOt=0,shortfall=0,i,r,d;
  records=Array.isArray(records)?records:[];
  for(i=0;i<records.length;i++){
    r=records[i];if(!r||String(r.date||'').slice(0,7)!==month)continue;d=daily(r,s);
    if(d.special)specialOt+=d.worked;else normalOt+=d.overtime;
    shortfall+=d.shortfall;
  }
  var deduction=(shortfall/60)*hourRate,normalOtPay=(normalOt/60)*hourRate*mult,specialPay=(specialOt/60)*hourRate,earned=Math.max(0,monthly-deduction+normalOtPay+specialPay),paid=clamp(days-(shortfall/std),0,days);
  return{days:days,paid:paid,ot:normalOt+specialOt,net:(normalOt+specialOt)-shortfall,shortfall:shortfall,dayRate:dayRate,hourRate:hourRate,otPay:normalOtPay+specialPay,normalOt:normalOt,specialOt:specialOt,normalOtPay:normalOtPay,specialPay:specialPay,deduction:deduction,baseSalary:monthly,earned:earned};
}
function leaveAccrued(asOf,totalCap,rate){
  var d=asOf instanceof Date?asOf:new Date(asOf||Date.now());if(isNaN(d.getTime()))d=new Date();
  var r=n(rate,1.5);if(r<0)r=0;var accrued=(d.getMonth()+1)*r,cap=n(totalCap,18);if(cap>0)accrued=Math.min(accrued,cap);return Math.round(accrued*100)/100;
}
function normalizeRecord(r){
  if(!r||typeof r!=='object'||Array.isArray(r))return{ok:false,error:'Record is not an object'};
  var date=normalizeDate(r.date),status=normalizeStatus(r.status),ci=normalizeTime(r.checkIn),co=normalizeTime(r.checkOut);
  if(!date)return{ok:false,error:'Invalid date'};
  if(status==null)return{ok:false,error:'Invalid status'};
  if(ci==null)return{ok:false,error:'Invalid check-in time'};
  if(co==null)return{ok:false,error:'Invalid check-out time'};
  var out={},k;
  for(k in r)if(Object.prototype.hasOwnProperty.call(r,k))out[k]=r[k];
  out.id=String(r.id==null?'':r.id).slice(0,128);
  out.date=date;out.status=status;out.checkIn=ci;out.checkOut=co;
  out.reason=String(r.reason==null?'':r.reason).slice(0,1000);
  out.notes=String(r.notes==null?'':r.notes).slice(0,5000);
  if(r.specialOT===true||r.specialOT===false)out.specialOT=!!r.specialOT;
  return{ok:true,record:out};
}
function validateRecord(r){return normalizeRecord(r).ok}
function basicStorageCheck(storage){
  if(!storage||typeof storage!=='object'||Array.isArray(storage))return{ok:false,error:'Backup storage is not an object'};
  var keys=Object.keys(storage),i,k,v,total=0;if(keys.length>500)return{ok:false,error:'Backup contains too many settings records'};
  for(i=0;i<keys.length;i++){k=String(keys[i]);v=storage[k];if(k.indexOf('attendance_')!==0||k.indexOf('attendance_cloud_')===0)return{ok:false,error:'Backup contains an invalid storage key'};if(typeof v!=='string')return{ok:false,error:'Backup contains a non-text value'};total+=v.length;if(total>22*1024*1024)return{ok:false,error:'Backup payload is too large'};}
  return{ok:true,count:keys.length,totalChars:total};
}
function normalizeStorage(storage){
  var base=basicStorageCheck(storage);if(!base.ok)return base;
  var out={},keys=Object.keys(storage),i,k,a,nr;
  for(i=0;i<keys.length;i++){k=keys[i];out[k]=storage[k]}
  try{
    if(typeof out.attendance_v8==='string'){
      a=JSON.parse(out.attendance_v8);
      if(!Array.isArray(a)||a.length>10000)return{ok:false,error:'Attendance history is invalid'};
      for(i=0;i<a.length;i++){nr=normalizeRecord(a[i]);if(!nr.ok)return{ok:false,error:'Attendance record '+(i+1)+' is invalid: '+nr.error};a[i]=nr.record}
      out.attendance_v8=JSON.stringify(a);
    }
    if(typeof out.attendance_settings_v8==='string'){
      var settings=JSON.parse(out.attendance_settings_v8);if(!settings||typeof settings!=='object'||Array.isArray(settings))return{ok:false,error:'Work settings are invalid'};out.attendance_settings_v8=JSON.stringify(Object.assign({},settings,normalizeSettings(settings)));
    }
    if(typeof out.attendance_salary_v9==='string'){var sal=JSON.parse(out.attendance_salary_v9);if(!sal||typeof sal!=='object'||n(sal.monthly,-1)<0)return{ok:false,error:'Salary settings are invalid'}}
    if(typeof out.attendance_leave_setup_v81==='string'){var l=JSON.parse(out.attendance_leave_setup_v81);if(!l||typeof l!=='object'||!Array.isArray(l.categories))return{ok:false,error:'Leave settings are invalid'}}
  }catch(e){return{ok:false,error:'Backup contains malformed JSON data'}}
  return{ok:true,storage:out,count:base.count,totalChars:base.totalChars};
}
function validateStorage(storage){var x=normalizeStorage(storage);return x.ok?{ok:true,count:x.count,totalChars:x.totalChars}:x}
return{normalizeSettings:normalizeSettings,normalizeDate:normalizeDate,normalizeTime:normalizeTime,normalizeStatus:normalizeStatus,standardMinutes:standardMinutes,minutesBetween:minutesBetween,workedMinutes:workedMinutes,isSunday:isSunday,isSpecial:isSpecial,requiredMinutes:requiredMinutes,daily:daily,balanceMinutes:balanceMinutes,salaryMonth:salaryMonth,leaveAccrued:leaveAccrued,normalizeRecord:normalizeRecord,validateRecord:validateRecord,normalizeStorage:normalizeStorage,validateStorage:validateStorage};
});