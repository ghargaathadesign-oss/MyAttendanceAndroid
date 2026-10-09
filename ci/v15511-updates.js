(function(){
'use strict';
function E(id){return document.getElementById(id)}
function A(){return window.AttendanceAppApi}
function n(v){return Number(Number(v||0).toFixed(2))}
function cfg(){try{return JSON.parse(localStorage.getItem('attendance_leave_setup_v81')||'{}')||{}}catch(e){return{}}}
function leaveAllowance(month){var c=cfg(),now=A().monthNow(),months=month>now?(month.slice(0,4)===now.slice(0,4)?+now.slice(5,7):0):+month.slice(5,7);return{annual:c.total==null?18:Math.max(0,+c.total||0),monthly:(c.total==null?18:Math.max(0,+c.total||0))/12,additional:Math.max(0,+c.additional||0),months:months}}
function renderPunchTimes(){var api=A();if(!api)return;var r=api.dataGet().find(function(x){return x.date===api.nowDate()}),el=E('todayStatus');if(!el)return;var active=r&&r.checkIn&&!r.checkOut;el.classList.toggle('punchTimeSections',!!active);if(!active)return;var s=api.setGet(),d=new Date(),parts=r.checkIn.split(':'),elapsed=d.getHours()*60+d.getMinutes()-(+parts[0]*60+ +parts[1]);if(elapsed<0)elapsed+=1440;var special=AttendancePolicy.isSpecial(r),left=special?0:Math.max(0,s.h*60+s.m-elapsed);function hm(v){return String(Math.floor(v/60)).padStart(2,'0')+':'+String(v%60).padStart(2,'0')}
 var html='<section><small>Remaining Time</small><b>'+hm(left)+'</b></section><section><small>Passed Time</small><b>'+hm(elapsed)+'</b></section>';if(el.innerHTML!==html)el.innerHTML=html;
}
var oldDetails=window.renderSalaryMonthDetails;
window.renderSalaryMonthDetails=function(c){oldDetails(c);var month=window.salarySelectedMonth,api=A(),records=api.dataGet(),today=api.nowDate(),days=c.days,offDates={},holDates={},used=0,yearUsed=0,p=month.split('-'),allow=leaveAllowance(month);
 for(var d=1;d<=days;d++){var date=p[0]+'-'+p[1]+'-'+String(d).padStart(2,'0');if(AttendancePolicy.isSunday(date))offDates[date]=true}
 records.forEach(function(r){if(r.date.slice(0,4)===p[0]&&r.date<=month+'-31'&&r.date<=today&&r.status==='Paid Leave')yearUsed++;if(r.date.slice(0,7)!==month)return;if(r.status==='Paid Leave')used++;if(r.status==='Holiday')holDates[r.date]=true;if(r.status==='Week Off')offDates[r.date]=true});
 var elapsedOff=Object.keys(offDates).filter(function(d){return d<=today}).length,elapsedHol=Object.keys(holDates).filter(function(d){return d<=today}).length,cards=E('salaryBreakdown').querySelectorAll('.salaryInfoCard');
 function set(i,value,info){cards[i].querySelector('b').textContent=value;cards[i].querySelector('.salaryCardInfo').textContent=info}
 set(0,elapsedOff+' / '+Object.keys(offDates).length,'Weekoffs passed / total this month, including worked weekoffs. Holidays passed / recorded: '+elapsedHol+' / '+Object.keys(holDates).length+'.');
 set(1,n(used)+' days',n(allow.monthly)+' days allowed per month · '+allow.annual+' per year · '+allow.additional+' additional granted.');
 var accrued=allow.monthly*allow.months;
 set(2,n(Math.max(0,accrued+allow.additional-yearUsed))+' days',n(accrued)+' accrued + '+allow.additional+' granted − '+yearUsed+' used. Annual allowance ÷ 12; unused accrued leave carries forward.');
};
function closeDropdowns(e){if(e&&e.target&&e.target.closest&&e.target.closest('.customSelectMenu,.v112CalPickMenu'))return;document.querySelectorAll('.customSelect.open,.v112CalPick.open').forEach(function(el){el.classList.remove('open')})}
function searchSettings(){var q=E('settingsSearch').value.trim().toLowerCase(),count=0;document.querySelectorAll('#screen-settings .settingsMenuRow,#screen-settings .settingsLogoutRow').forEach(function(row){var match=!q||(row.textContent+' '+(row.getAttribute('data-setting')||'')).toLowerCase().indexOf(q)>=0;row.hidden=!match;if(match)count++});E('settingsSearchEmpty').hidden=!!count}
function init(){E('settingsSearch').addEventListener('input',searchSettings);E('additionalLeaves').addEventListener('input',function(){var annual=Number(E('totalLeaves').value)||0;E('leaveSetupPreview').textContent='Annual: '+annual+' ÷ 12 = '+n(annual/12)+' days/month · Additional: '+(Number(this.value)||0)+' days'});document.addEventListener('scroll',closeDropdowns,true);document.addEventListener('touchmove',closeDropdowns,{capture:true,passive:true});document.addEventListener('wheel',closeDropdowns,{capture:true,passive:true});window.addEventListener('resize',closeDropdowns);apiRefresh()}
function apiRefresh(){if(A())A().renderAll();renderPunchTimes()}
window.AttendanceV15511={renderPunchTimes:renderPunchTimes,leaveAllowance:leaveAllowance};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
