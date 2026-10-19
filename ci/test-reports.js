'use strict';
const assert=require('assert'),fs=require('fs'),vm=require('vm'),p=require('./policy-engine');
const box={window:{},document:{readyState:'loading',addEventListener(){}},AttendancePolicy:p};vm.createContext(box);vm.runInContext(fs.readFileSync('ci/v15519-reports.js','utf8'),box);
const series=box.window.AttendanceReports19.series;
const records=[{date:'2026-10-05',status:'Present',checkIn:'09:00',checkOut:'18:00'},{date:'2026-10-06',status:'Absent'},{date:'2026-10-07',status:'Half Day',checkIn:'09:00',checkOut:'13:30'},{date:'2026-10-08',status:'Present',checkIn:'22:00',checkOut:'06:00'},{date:'2026-10-09',status:'Present',checkIn:'09:15'},{date:'2026-10-25',status:'Present',checkIn:'09:00',checkOut:'18:00'}];
let s=series('2026-10',records,{h:9,m:0},'2026-10-19');assert.equal(s.months.length,6);assert.equal(s.months[0].month,'2026-05');assert.equal(s.months[0].worked,null);assert.equal(s.months[5].required,40.5);assert.equal(s.months[5].worked,21.5);assert.equal(s.daily.length,31);assert.equal(s.daily[7].inTime,1320);assert.equal(s.daily[7].outTime,1800);assert.equal(s.daily[8].inTime,555);assert.equal(s.daily[8].outTime,null);assert.equal(s.daily[24].inTime,null);assert.equal(s.daily[5].inTime,null);
s=series('2027-01',[],{},'2027-01-19');assert.equal(s.months[0].month,'2026-08');assert.equal(s.months[5].month,'2027-01');s=series('2028-02',[],{},'2028-02-29');assert.equal(s.daily.length,29);console.log('Reports series, gaps, overnight and month boundaries passed');

s=series('2026-10',records.concat([{date:'2026-10-19',status:'Present',checkIn:'10:00',checkOut:''}]),{h:9,m:0},'2026-10-19');assert.equal(s.months[5].required,40.5);assert.equal(s.months[5].worked,21.5);assert.equal(s.daily[18].inTime,600);assert.equal(s.daily[18].outTime,null);
console.log('Open shift excluded from finalized hour trend; check-in remains in daily chart');
