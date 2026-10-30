'use strict';
const assert=require('assert'),fs=require('fs'),vm=require('vm');
// Fix the payroll clock so month-end and future-date behavior stay deterministic.
const RealDate=Date,context={module:{exports:{}},Date:class extends RealDate{constructor(...args){super(...(args.length?args:['2026-10-31T12:00:00']))}static now(){return new RealDate('2026-10-31T12:00:00').getTime()}}};
vm.runInNewContext(fs.readFileSync(require.resolve('./policy-engine.js'),'utf8'),context);const p=context.module.exports;
const settings={h:9,m:0,otDelay:30},salary={monthly:40000,basicDa:20000,otMultiplier:1,pfEnabled:true,esicEnabled:true,autoWeekOffs:true,asOfDate:'2026-10-30',employmentStartDate:'2026-10-01'};
const rows=[];for(let day=1;day<=30;day++){if(day===11||day===25)continue;rows.push({date:'2026-10-'+String(day).padStart(2,'0'),status:day===15?'Paid Leave':day===20?'Half Day Holiday':'Present',checkIn:day===15?'':'09:00',checkOut:day===15?'':'18:00',holidayWorkMinutes:day===20?180:undefined})}
rows.find(r=>r.date.endsWith('-01')).checkOut='17:00';rows.find(r=>r.date.endsWith('-02')).checkOut='17:00';rows.find(r=>r.date.endsWith('-03')).checkOut='16:18';rows.find(r=>r.date.endsWith('-04')).checkOut='13:00';rows.find(r=>r.date.endsWith('-18')).checkOut='18:54';rows.find(r=>r.date.endsWith('-06')).checkOut='04:11';rows.find(r=>r.date.endsWith('-20')).checkOut='12:00';
const original=JSON.stringify(rows),old=p.salaryMonth(rows,'2026-10',settings,{...salary,autoWeekOffs:false});assert.equal(Math.round(old.netEarned),36551);assert.equal(old.ot,1415);assert.equal(old.shortfall,222);
const fixed=p.salaryMonth(rows,'2026-10',settings,salary);assert.equal(fixed.autoWeekOffDays,2);assert.equal(fixed.weekOffDays,4);assert.equal(JSON.stringify(fixed.autoWeekOffDates),JSON.stringify(['2026-10-11','2026-10-25']));assert.equal(Math.round(fixed.netEarned),38957);assert.equal(fixed.pfDeduction,2291);assert.equal(fixed.esicDeduction,312);assert.equal(fixed.recordedDays,28);assert.equal(JSON.stringify(rows),original);assert.equal(fixed.ot,old.ot);assert.equal(fixed.net,old.net);
const full=p.salaryMonth(rows.concat({date:'2026-10-31',status:'Present',checkIn:'09:00',checkOut:'18:00'}),'2026-10',settings,{...salary,asOfDate:'2026-10-31'});assert.equal(Math.round(full.netEarned),40161);assert.equal(full.pfDeduction,2368);assert.equal(full.esicDeduction,322);
const saved=rows.concat(fixed.autoWeekOffDates.map(date=>({date,status:'Week Off'})));const explicit=p.salaryMonth(saved,'2026-10',settings,salary);assert.equal(explicit.netEarned,fixed.netEarned);assert.equal(explicit.autoWeekOffDays,0);
assert.equal(p.salaryMonth([],'2026-10',settings,salary).earned,0);
assert.equal(p.salaryMonth(rows,'2026-11',settings,{...salary,asOfDate:'2026-12-01'}).earned,0);
const joined=p.salaryMonth(rows,'2026-10',settings,{...salary,employmentStartDate:'2026-10-12',asOfDate:'2026-10-24'});assert.equal(joined.autoWeekOffDays,0);
const earlier=p.salaryMonth(rows,'2026-10',settings,{...salary,asOfDate:'2026-10-20'});assert.equal(earlier.autoWeekOffDays,1);assert.equal(earlier.weekOffDays,3);
const sparse=p.salaryMonth([{date:'2026-10-19',status:'Present',checkIn:'09:00',checkOut:'18:00'}],'2026-10',settings,{...salary,employmentStartDate:undefined,asOfDate:'2026-10-24'});assert.equal(sparse.paid,1);assert.equal(sparse.autoWeekOffDays,0);
console.log('Paid Sunday regression: exact screenshot, completed 31st, PF/ESIC, no duplicates, no mutation, joining date, cutoff, empty and future months passed');
