(function(root,factory){
  var api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.AttendancePolicy=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
var VALID_STATUS={'Present':1,'Absent':1,'Paid Leave':1,'Unpaid Leave':1,'Half Day':1,'Holiday':1,'Week Off':1};
function n(v,d){v=Number(v);return isFinite(v)?v:d}
function clamp(v,min,max){return Math.min(max,Math.max(min,v))}
function normalizeSettings(input){
  input=input||{};
  var h=clamp(Math.floor(n(input.h,9)),0,23),m=clamp(Math.floor(n(input.m,0)),0,59),delay=clamp(Math.floor(n(input.otDelay,30)),0,180);
  if(h===0&&m===0)h=9;
  return{h:h,m:m,otDelay:delay,fmt:input.fmt==='24h'?'24h':'12h',leaveAccrualPerMonth:1.5,policyVersion:126};
}
function minuteOfDay(t){if(!t||!/^\d{1,2}:\d{2}$/.test(String(t)))return null;var p=String(t).split(':'),h=+p[0],m=+p[1];if(h<0||h>23||m<0||m>59)return null;return h*60+m}
function minutesBetween(a,b){var x=minuteOfDay(a),y=minuteOfDay(b);if(x==null||y==null)return 0;if(y<x)y+=1440;return Math.max(0,y-x)}
function workedMinutes(record){return record?minutesBetween(record.checkIn,record.checkOut):0}
function isSunday(date){var d=new Date(String(date||'')+'T00:00:00');return !isNaN(d.getTime())&&d.getDay()===0}
function isSpecial(record){return !!(record&&(record.specialOT===true||record.status==='Holiday'||record.status==='Week Off'||isSunday(record.date)))}
function standardMinutes(settings){var s=normalizeSettings(settings);return s.h*60+s.m}
function requiredMinutes(record,settings){if(!record)return 0;var std=standardMinutes(settings),st=record.status||'Present';if(st==='Paid Leave'||st==='Holiday'||st==='Week Off')return 0;if(st==='Half Day')return Math.round(std/2);return std}
function daily(record,settings){
  var s=normalizeSettings(settings),worked=workedMinutes(record),required=requiredMinutes(record,s),special=isSpecial(record),balance=0,st=record&&record.status||'Present';
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
function validDate(v){if(!/^\d{4}-\d{2}-\d{2}$/.test(String(v||'')))return false;var d=new Date(v+'T00:00:00');return !isNaN(d.getTime())&&d.toISOString().slice(0,10)===v}
function validTime(v){return v===''||v==null||minuteOfDay(v)!=null}
function validateRecord(r){if(!r||typeof r!=='object')return false;if(!validDate(r.date))return false;if(!VALID_STATUS[r.status||'Present'])return false;if(!validTime(r.checkIn)||!validTime(r.checkOut))return false;return true}
function validateStorage(storage){
  if(!storage||typeof storage!=='object'||Array.isArray(storage))return{ok:false,error:'Backup storage is not an object'};
  var keys=Object.keys(storage),i,k,v,total=0;if(keys.length>500)return{ok:false,error:'Backup contains too many settings records'};
  for(i=0;i<keys.length;i++){k=String(keys[i]);v=storage[k];if(k.indexOf('attendance_')!==0||k.indexOf('attendance_cloud_')===0)return{ok:false,error:'Backup contains an invalid storage key'};if(typeof v!=='string')return{ok:false,error:'Backup contains a non-text value'};total+=v.length;if(total>22*1024*1024)return{ok:false,error:'Backup payload is too large'};}
  try{
    if(typeof storage.attendance_v8==='string'){
      var a=JSON.parse(storage.attendance_v8);if(!Array.isArray(a)||a.length>10000)return{ok:false,error:'Attendance history is invalid'};for(i=0;i<a.length;i++)if(!validateRecord(a[i]))return{ok:false,error:'Attendance history contains an invalid record'};
    }
    if(typeof storage.attendance_settings_v8==='string'){var s=JSON.parse(storage.attendance_settings_v8);if(!s||typeof s!=='object')return{ok:false,error:'Work settings are invalid'};normalizeSettings(s)}
    if(typeof storage.attendance_salary_v9==='string'){var sal=JSON.parse(storage.attendance_salary_v9);if(!sal||typeof sal!=='object'||n(sal.monthly,-1)<0)return{ok:false,error:'Salary settings are invalid'}}
    if(typeof storage.attendance_leave_setup_v81==='string'){var l=JSON.parse(storage.attendance_leave_setup_v81);if(!l||typeof l!=='object'||!Array.isArray(l.categories))return{ok:false,error:'Leave settings are invalid'}}
  }catch(e){return{ok:false,error:'Backup contains malformed JSON data'}}
  return{ok:true,count:keys.length,totalChars:total};
}
return{normalizeSettings:normalizeSettings,standardMinutes:standardMinutes,minutesBetween:minutesBetween,workedMinutes:workedMinutes,isSunday:isSunday,isSpecial:isSpecial,requiredMinutes:requiredMinutes,daily:daily,balanceMinutes:balanceMinutes,salaryMonth:salaryMonth,leaveAccrued:leaveAccrued,validateRecord:validateRecord,validateStorage:validateStorage};
});