'use strict';
const assert=require('assert'),P=require('./policy-engine.js');
const settings={h:9,m:0,otDelay:30},salary={monthly:31000,otMultiplier:1,asOfDate:'2026-10-20'};
function row(ci='09:00',co='13:30',target=270){return {id:'holiday',date:'2026-10-05',status:'Half Day Holiday',checkIn:ci,checkOut:co,holidayWorkMinutes:target}}
let r=row(),d=P.daily(r,settings,'2026-10-20'),c=P.salaryMonth([r],'2026-10',settings,salary);
assert.equal(P.attendanceStatus(r),'Half Day Holiday');assert.equal(d.required,270);assert.equal(d.worked,270);assert.equal(d.special,false);assert.equal(d.balance,0);assert.equal(c.paid,1);assert.equal(c.baseEarned,1000);assert.equal(c.ot,0);assert.deepEqual(c.otLeaveAllocations,{});
r=row('09:00','12:00',180);assert.equal(P.requiredMinutes(r,settings),180);assert.equal(P.salaryMonth([r],'2026-10',settings,salary).earned,1000);
r=row('09:00','11:00',180);c=P.salaryMonth([r],'2026-10',settings,salary);assert.equal(c.shortfall,60);assert(Math.abs(c.earned-(1000-1000/9))<1e-8);
r=row('09:00','14:00');assert.equal(P.daily(r,settings).overtime,0);r.checkOut='14:30';assert.equal(P.daily(r,settings).overtime,30);
r=row('22:00','02:30');assert.equal(P.salaryMonth([r],'2026-10',settings,salary).paid,1);
r=row('09:00','');r.date='2026-10-20';d=P.daily(r,settings,'2026-10-20');assert(d.pending);c=P.salaryMonth([r],'2026-10',settings,salary);assert.equal(c.earned,0);assert.equal(c.net,0);
r=row('','');assert.equal(P.salaryMonth([r],'2026-10',settings,salary).paid,.5);
r=row();r.date='2026-10-21';assert.equal(P.salaryMonth([r],'2026-10',settings,salary).earned,0);
r=row();r.date='2026-10-04';assert.equal(P.normalizeRecord(r).record.status,'Week Off');assert.equal(P.requiredMinutes(r,settings),0);
for(const invalid of [-1,0,1.5,'bad',1440])assert.equal(P.normalizeRecord({...row(),holidayWorkMinutes:invalid}).ok,false);
const storage=P.normalizeStorage({attendance_v8:JSON.stringify([row()])});assert(storage.ok);assert.equal(JSON.parse(storage.storage.attendance_v8)[0].holidayWorkMinutes,270);
r=row();delete r.holidayWorkMinutes;assert.equal(P.requiredMinutes(r,settings),270);
r=row('09:00','15:00');r.status='Present';assert.equal(P.attendanceStatus(r),'Present');assert.equal(P.requiredMinutes(r,settings),540);
console.log('Half Day Holiday: full-day credit, custom target, shortfall, OT grace, overnight, open/future records, Sunday and backup cases passed');
