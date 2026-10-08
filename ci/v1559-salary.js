(function(){
'use strict';
var KEY='attendance_salary_adjustments_v1559';
function E(id){return document.getElementById(id)}
function A(){return window.AttendanceAppApi}
function adjustments(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){return{}}}
function num(n){return Number(n||0).toFixed(2).replace(/\.00$/,'')}
function row(label,value){var el=document.createElement('div');el.className='salaryDetailRow';var l=document.createElement('span'),v=document.createElement('b');l.textContent=label;v.textContent=value;el.appendChild(l);el.appendChild(v);return el}
window.renderSalaryMonthDetails=function(c){
 var month=window.salarySelectedMonth||A().monthNow(),records=A().dataGet(),used=0,yearUsed=0,hol=0,off=0,p=month.split('-'),y=+p[0],m=+p[1],d,accrued=Math.min(18,m*1.5),adj=adjustments()[month]||{amount:0,type:'add',reason:''},amount=Number(adj.amount)||0;
 E('salaryMonth').value=month;window.salarySelectedMonth=month;
 records.forEach(function(r){if(r.date.slice(0,4)===p[0]&&r.date<=month+'-31'&&r.status==='Paid Leave')yearUsed++;if(r.date.slice(0,7)!==month)return;if(r.status==='Paid Leave')used++;if(r.status==='Holiday')hol++;if(r.status==='Week Off'&&!AttendancePolicy.isSunday(r.date))off++});
 for(d=1;d<=c.days;d++)if(new Date(y,m-1,d).getDay()===0)off++;
 var box=E('salaryBreakdown');box.textContent='';
 [['Daily rate calculation',A().money(c.baseSalary)+' ÷ '+c.days+' calendar days'],['Hourly rate',A().money(c.hourRate)+' · daily rate ÷ standard hours'],['Paid days calculation',num(c.paid)+' recorded paid day equivalents'],['Overtime',A().durationText(c.ot)+' · '+A().money(c.otPay)],['Holidays / weekoffs',hol+' / '+off],['Paid leave taken this month',num(used)+' days'],['Monthly paid leave allowance','1.5 days · 18 per year'],['Accrued through selected month',num(accrued)+' days'],['Paid leave used through selected month',num(yearUsed)+' days'],['Accrued leave remaining',num(Math.max(0,accrued-yearUsed))+' days'],['Base earned salary',A().money(c.baseEarned)],['Manual adjustment',(adj.type==='subtract'?'−':'+')+A().money(amount)+(adj.reason?' · '+adj.reason:'')]].forEach(function(x){box.appendChild(row(x[0],x[1]))});
 var note=document.createElement('p');note.className='helpText';note.textContent='Paid days include recorded paid leave, holidays and weekoffs. Short time reduces paid-day equivalents. Normal OT uses your saved multiplier; all Sunday / holiday worked time receives an additional hourly payment. Leave accrual is shown separately from the saved annual Leave Setup balance.';box.appendChild(note);
 E('salaryAdjustmentType').value=adj.type;E('salaryAdjustmentAmount').value=amount||'';E('salaryAdjustmentReason').value=adj.reason||'';
 E('salaryFinalAmount').textContent=A().money(c.earned+(adj.type==='subtract'?-amount:amount));
};
function refresh(){if(A())A().renderAll()}
function move(delta){var p=window.salarySelectedMonth.split('-'),d=new Date(+p[0],+p[1]-1+delta,1);window.salarySelectedMonth=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0');E('salaryAdjustmentStatus').textContent='';refresh()}
function init(){
 window.salarySelectedMonth=A()?A().monthNow():new Date().toISOString().slice(0,7);
 E('salaryPrevMonth').onclick=function(){move(-1)};E('salaryNextMonth').onclick=function(){move(1)};
 E('salaryMonth').onchange=function(){if(!/^\d{4}-\d{2}$/.test(this.value))return;window.salarySelectedMonth=this.value;E('salaryAdjustmentStatus').textContent='';refresh()};
 E('saveSalaryAdjustment').onclick=function(){var raw=E('salaryAdjustmentAmount').value,value=raw===''?0:Number(raw),status=E('salaryAdjustmentStatus');if(!isFinite(value)||value<0){status.textContent='Enter a valid non-negative amount';return}var all=adjustments();all[window.salarySelectedMonth]={amount:value,type:E('salaryAdjustmentType').value,reason:E('salaryAdjustmentReason').value.trim()};if(!A().verifiedStorageSet(KEY,all,'salary adjustments')){status.textContent='Could not save adjustment';return}refresh();status.textContent='Adjustment saved for '+window.salarySelectedMonth};refresh();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
