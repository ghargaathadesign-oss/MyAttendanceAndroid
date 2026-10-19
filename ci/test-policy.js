'use strict';
const assert=require('assert');
const p=require('./policy-engine.js');
const s=p.normalizeSettings({});
assert.deepStrictEqual({h:s.h,m:s.m,otDelay:s.otDelay},{h:9,m:0,otDelay:30});
function rec(date,ci,co,status='Present',extra={}){return Object.assign({date,status,checkIn:ci,checkOut:co},extra)}
assert.strictEqual(p.balanceMinutes(rec('2026-10-05','09:00','18:00'),s),0);
assert.strictEqual(p.balanceMinutes(rec('2026-10-05','09:00','18:30'),s),0);
assert.strictEqual(p.balanceMinutes(rec('2026-10-05','09:00','19:00'),s),30);
assert.strictEqual(p.balanceMinutes(rec('2026-10-05','09:00','17:30'),s),-30);
assert.strictEqual(p.balanceMinutes(rec('2026-10-04','09:00','15:00','Week Off',{specialOT:true}),s),360);
assert.strictEqual(p.isSunday('2026-10-04'),true);
assert.strictEqual(p.requiredMinutes(rec('2026-10-04','09:00','10:15','Present'),s),0);
assert.strictEqual(p.balanceMinutes(rec('2026-10-04','09:00','10:15','Present'),s),75);
const sundayNormalized=p.normalizeRecord(rec('2026-10-04','09:00','10:15','Present'));
assert.strictEqual(sundayNormalized.ok,true);
assert.strictEqual(sundayNormalized.record.status,'Week Off');
assert.strictEqual(sundayNormalized.record.specialOT,true);
assert.strictEqual(p.balanceMinutes(rec('2026-10-06','','','Paid Leave'),s),0);
assert.strictEqual(p.balanceMinutes(rec('2026-10-06','','','Absent'),s),-540);
assert.strictEqual(p.balanceMinutes(rec('2026-10-06','09:00','17:00','Short Day'),s),-60);
assert.strictEqual(p.leaveAccrued(new Date('2026-10-05T12:00:00'),18,1.5),15);
assert.strictEqual(p.leaveAccrued(new Date('2026-12-05T12:00:00'),18,1.5),18);
assert.strictEqual(p.normalizeDate('5/10/2026'),'2026-10-05');
assert.strictEqual(p.normalizeDate('2026/10/5'),'2026-10-05');
assert.strictEqual(p.normalizeTime('9:05 AM'),'09:05');
assert.strictEqual(p.normalizeTime('6:30 PM'),'18:30');
assert.strictEqual(p.normalizeStatus('SD'),'Short Day');
assert.strictEqual(p.normalizeStatus('AB'),'Absent');
const sal=p.salaryMonth([rec('2026-08-03','','','Absent'),rec('2026-08-09','09:00','15:00','Week Off',{specialOT:true}),rec('2026-08-10','09:00','19:00')],'2026-08',s,{monthly:26000,otMultiplier:1});
assert.strictEqual(sal.specialOt,360);
assert.strictEqual(sal.normalOt,30);
assert.strictEqual(sal.shortfall,540);
assert.strictEqual(sal.paid,2);
assert(Math.abs(sal.baseEarned-(2*(26000/31)))<0.01);
assert(sal.earned>sal.baseEarned&&sal.earned<26000);
assert(sal.specialPay>0&&sal.normalOtPay>0);
const octoberSeven=[
 rec('2026-10-01','09:00','18:00'),
 rec('2026-10-02','09:00','18:00'),
 rec('2026-10-03','09:00','18:00'),
 rec('2026-10-04','09:00','18:00','Week Off',{specialOT:true}),
 rec('2026-10-05','09:00','18:00'),
 rec('2026-10-06','09:00','18:00'),
 rec('2026-10-07','09:00','18:13')
];
const octoberSalary=p.salaryMonth(octoberSeven,'2026-10',s,{monthly:40000,otMultiplier:1});
assert.strictEqual(octoberSalary.recordedDays,7);
assert.strictEqual(octoberSalary.paid,7);
assert(octoberSalary.earned>0&&octoberSalary.earned<40000);
assert(octoberSalary.baseEarned<10000);
assert(Math.abs(octoberSalary.baseEarned-(7*(40000/31)))<0.01);
const legacy={attendance_v8:JSON.stringify([
 {id:1,date:'5/10/2026',status:'SD',checkIn:'9:00 AM',checkOut:'5:00 PM',reason:'legacy'},
 {id:2,date:'2026/10/06',status:'AB',checkIn:'',checkOut:''}
]),attendance_settings_v8:JSON.stringify({h:9,m:0,otDelay:30})};
const norm=p.normalizeStorage(legacy);
assert.strictEqual(norm.ok,true);
const arr=JSON.parse(norm.storage.attendance_v8);
assert.strictEqual(arr[0].date,'2026-10-05');
assert.strictEqual(arr[0].status,'Present');
assert.strictEqual(arr[0].checkIn,'09:00');
assert.strictEqual(arr[0].checkOut,'17:00');
assert.strictEqual(arr[1].status,'Absent');
assert.strictEqual(p.validateStorage({bad_key:'x'}).ok,false);
console.log('policy tests passed');// Payroll is optional; caps follow each earned day's effective date.
function paidMonth(month){const parts=month.split('-').map(Number),days=new Date(parts[0],parts[1],0).getDate();return Array.from({length:days},(_,i)=>rec(month+'-'+String(i+1).padStart(2,'0'),'','','Paid Leave'))}
function payroll(month,monthly,basicDa,extra={}){return p.salaryMonth(paidMonth(month),month,s,Object.assign({monthly,basicDa,pfEnabled:true,esicEnabled:true},extra))}
let pay=payroll('2026-10',20000,15000);assert.equal(pay.pfDeduction,1800);assert.equal(pay.esicDeduction,150);assert.equal(pay.netEarned,18050);
assert.equal(payroll('2026-10',50000,40000).pfDeduction,3000);
assert.equal(payroll('2026-08',50000,40000).pfDeduction,1800);
assert.equal(payroll('2026-09',50000,30000).pfDeduction,2360);
assert.equal(payroll('2026-10',50000,40000,{pfFullWages:true}).pfDeduction,4800);
assert.equal(payroll('2026-10',21000,15000).esicDeduction,158);
assert.equal(payroll('2026-10',5000,3000).esicDeduction,0);
pay=p.salaryMonth([rec('2026-10-05','','','Paid Leave')],'2026-10',s,{monthly:31000,basicDa:15500,pfEnabled:true,esicEnabled:true});assert.equal(pay.pfDeduction,60);assert.equal(pay.esicDeduction,8);assert.equal(pay.netEarned,932);
const overtime=p.salaryMonth([rec('2026-10-05','09:00','20:30')],'2026-10',s,{monthly:31000,basicDa:15500,pfEnabled:true,esicEnabled:true});assert.equal(overtime.pfDeduction,60);assert(overtime.esicDeduction>pay.esicDeduction);
pay=p.salaryMonth([],'2026-11',s,{monthly:31000,basicDa:15500,pfEnabled:true,esicEnabled:true});assert.equal(pay.netEarned,0);assert.equal(pay.payrollDeduction,0);
pay=payroll('2026-10',20000,15000,{pfEnabled:false,esicEnabled:false});assert.equal(pay.netEarned,pay.earned);assert.equal(pay.payrollDeduction,0);
console.log('PF/ESIC payroll cases passed');
// OT leave cover exchanges time once, without consuming paid leave.
const coverRecords=[rec('2026-10-04','09:00','18:00','Week Off',{specialOT:true}),rec('2026-10-05','','','Absent'),rec('2026-10-06','','','Paid Leave')];
const coverOriginal=JSON.stringify(coverRecords);
let cover=p.salaryMonth(coverRecords,'2026-10',s,{monthly:31000,otMultiplier:2,otCoverEnabled:true,basicDa:15500,pfEnabled:true,esicEnabled:true});
assert.equal(cover.ot,540);assert.equal(cover.otUsedForLeave,540);assert.equal(cover.otCoveredDays,1);assert.equal(cover.otPaidMinutes,0);assert.equal(cover.otPay,0);assert.equal(cover.paid,2);assert.equal(cover.earned,2000);assert.equal(cover.pfDeduction,120);assert.equal(cover.esicDeduction,15);assert.equal(cover.otPaidLeaveRefund,1);assert.equal(JSON.stringify(coverRecords),coverOriginal);
cover=p.salaryMonth(coverRecords,'2026-10',s,{monthly:31000,otCoverEnabled:false});assert.equal(cover.otUsedForLeave,0);assert.equal(cover.paid,2);assert.equal(cover.otPay,1000);
cover=p.salaryMonth([rec('2026-10-04','09:00','13:30','Week Off',{specialOT:true}),rec('2026-10-05','','','Unpaid Leave')],'2026-10',s,{monthly:31000,otCoverEnabled:true});assert.equal(cover.otCoveredDays,.5);assert.equal(cover.paid,1.5);assert.equal(cover.unpaidDaysAfterOT,.5);
cover=p.salaryMonth([rec('2026-10-04','09:00','18:00','Week Off',{specialOT:true}),rec('2026-10-05','','','Paid Leave')],'2026-10',s,{monthly:31000,otCoverEnabled:true});assert.equal(cover.otCoveredDays,1);assert.equal(cover.otPaidMinutes,0);assert.equal(cover.otPaidLeaveRefund,1);
cover=p.salaryMonth([rec('2026-09-06','09:00','18:00','Week Off',{specialOT:true}),rec('2026-10-05','','','Absent')],'2026-10',s,{monthly:31000,otCoverEnabled:true});assert.equal(cover.otCoveredDays,0);assert.equal(cover.paid,0);
cover=p.salaryMonth([rec('2026-10-04','09:00','18:00','Week Off',{specialOT:true}),rec('2026-10-05','09:00','18:30'),rec('2026-10-06','','','Absent')],'2026-10',{h:8,m:0,otDelay:30},{monthly:31000,otMultiplier:2,otCoverEnabled:true});assert.equal(cover.otUsedForLeave,480);assert.equal(cover.otPaidMinutes,120);assert.equal(cover.normalOtPay,0);assert.equal(cover.specialPay,250);
console.log('OT leave cover cases passed');

// OT refunds Paid Leave before covering unpaid dates, without creating extra salary.
cover=p.salaryMonth([rec('2026-10-04','09:00','13:30','Week Off',{specialOT:true}),rec('2026-10-05','','','Paid Leave')],'2026-10',s,{monthly:31000,otCoverEnabled:true});assert.equal(cover.otPaidLeaveRefund,.5);assert.equal(cover.otLeaveAllocations['2026-10-05'],.5);assert.equal(cover.paid,2);assert.equal(cover.otPay,0);assert.equal(cover.net,0);
console.log('OT paid-leave refunds passed');

cover=p.salaryMonth([rec('2026-10-04','09:00','18:00','Week Off',{specialOT:true}),rec('2026-10-25','','','Paid Leave')],'2026-10',s,{monthly:31000,otCoverEnabled:true,asOfDate:'2026-10-19'});assert.equal(cover.otPaidLeaveRefund,0);assert.equal(cover.otPaidMinutes,540);

// An active shift is attendance, but has no finalized pay or OT until checkout.
for(const [date,status] of [['2026-10-19','Present'],['2026-10-18','Week Off'],['2026-10-19','Holiday']]){
 const open=rec(date,'10:00','',status),closed=rec(date,'10:00','19:00',status);
 const d=p.daily(open,s,date);assert.equal(d.pending,true);assert.equal(d.shortfall,0);assert.equal(d.required,0);
 const pending=p.salaryMonth([open],'2026-10',s,{monthly:31000,basicDa:15500,pfEnabled:true,esicEnabled:true,asOfDate:date});
 assert.equal(pending.net,0);assert.equal(pending.earned,0);assert.equal(pending.pfDeduction,0);assert.equal(pending.esicDeduction,0);
 assert(p.salaryMonth([closed],'2026-10',s,{monthly:31000,asOfDate:date}).earned>0);
}
assert.equal(p.daily(rec('2026-10-18','10:00','','Present'),s,'2026-10-19').pending,undefined); // Historical missing punches remain diagnosable.
assert.equal(p.daily(rec('2026-10-19','','','Absent'),s,'2026-10-19').shortfall,540);
assert.equal(p.salaryMonth([rec('2026-10-20','09:00','18:00')],'2026-10',s,{monthly:31000,asOfDate:'2026-10-19'}).earned,0);
const currentOT=[rec('2026-10-05','09:00','22:13'),rec('2026-10-19','10:00','')];
assert.equal(p.salaryMonth(currentOT,'2026-10',s,{monthly:31000,asOfDate:'2026-10-19'}).net,223);
assert.equal(p.daily(rec('2026-10-19','10:00','18:00'),s,'2026-10-19').shortfall,60);
assert.equal(p.daily(rec('2026-10-19','22:00','08:00'),s,'2026-10-19').overtime,30);
console.log('Open shift, completed shift, future record and payroll regression cases passed');

// Attendance credit changes at exactly six hours; pay stays proportional for 6+ hours.
for(const [minutes,status,paid] of [[269,'Half Day',269/540],[270,'Half Day',.5],[330,'Half Day',.5],[359,'Half Day',.5],[360,'Present',360/540],[361,'Present',361/540],[480,'Present',480/540],[540,'Present',1]]){
 const end=9*60+minutes,r=rec('2026-10-05','09:00',String(Math.floor(end/60)).padStart(2,'0')+':'+String(end%60).padStart(2,'0'),'Half Day');
 assert.equal(p.attendanceStatus(r),status);assert.equal(p.normalizeRecord(r).record.status,status);const d=p.daily(r,s);assert.equal(d.overtime,0);
 const result=p.salaryMonth([r],'2026-10',s,{monthly:31000});assert(Math.abs(result.paid-paid)<1e-9);assert(Math.abs(result.baseEarned-1000*paid)<1e-8);
}
assert.equal(p.attendanceStatus(rec('2026-10-05','22:00','04:00','Half Day')),'Present');
assert.equal(p.attendanceStatus(rec('2026-10-05','10:00','','Present')),'Present');
assert.equal(p.attendanceStatus(rec('2026-10-04','09:00','10:00','Present')),'Week Off');
assert.equal(p.attendanceStatus(rec('2026-10-05','09:00','10:00','Holiday')),'Holiday');
const otDifference=p.salaryMonth([rec('2026-10-04','00:00','14:45','Week Off'),rec('2026-10-05','09:00','20:30'),rec('2026-10-06','09:00','17:15','Short Day')],'2026-10',s,{monthly:31000});assert.equal(otDifference.ot,1005);assert.equal(otDifference.remainingShortfall,45);assert.equal(otDifference.net,960);
console.log('Six-hour threshold, hourly salary, half-day OT and 16h45 gross / 16h net cases passed');
