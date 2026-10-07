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
assert.strictEqual(arr[0].status,'Short Day');
assert.strictEqual(arr[0].checkIn,'09:00');
assert.strictEqual(arr[0].checkOut,'17:00');
assert.strictEqual(arr[1].status,'Absent');
assert.strictEqual(p.validateStorage({bad_key:'x'}).ok,false);
console.log('policy tests passed');