(function(){
'use strict';
function E(id){return document.getElementById(id)}
function P(n){n=parseInt(n,10)||0;return n<10?'0'+n:String(n)}
function today(){var d=new Date();return d.getFullYear()+'-'+P(d.getMonth()+1)+'-'+P(d.getDate())}
function getRecords(){try{return JSON.parse(localStorage.getItem('attendance_v8')||'[]')||[]}catch(e){return[]}}
function putRecords(a){try{localStorage.setItem('attendance_v8',JSON.stringify(a));return true}catch(e){return false}}
function current(){var a=getRecords(),d=today(),i;for(i=0;i<a.length;i++)if(a[i].date===d)return a[i];return null}
function settings(){var s={h:9,m:0,otDelay:30};try{var o=JSON.parse(localStorage.getItem('attendance_settings_v8')||'{}')||{};if(typeof o.h!=='undefined')s.h=+o.h||0;if(typeof o.m!=='undefined')s.m=+o.m||0;if(typeof o.otDelay!=='undefined')s.otDelay=+o.otDelay||0}catch(e){}return s}
function minFrom(t){if(!t)return 0;var a=String(t).split(':');return(+a[0])*60+(+a[1])}
function workBetween(a,b){if(!a||!b)return 0;var x=minFrom(a),y=minFrom(b);if(y<x)y+=1440;return Math.max(0,y-x)}
function hm(n){n=Math.max(0,Math.round(n||0));return Math.floor(n/60)+'h '+P(n%60)+'m'}
function isSunday(date){var d=new Date(date+'T00:00:00');return !isNaN(d.getTime())&&d.getDay()===0}
function isSpecial(x){return !!(x&&(x.specialOT===true||x.status==='Holiday'||x.status==='Week Off'||isSunday(x.date)))}
function remove(id){var x=E(id);if(x&&x.parentNode)x.parentNode.removeChild(x)}

function showHolidayMode(){
 remove('holidayModeOverlay');
 var date=today(),x=current(),flag=false;
 try{flag=localStorage.getItem('attendance_special_ot_'+date)==='holiday'}catch(e){}
 if(x&&x.status==='Holiday')flag=true;
 var sunday=isSunday(date),o=document.createElement('div');
 o.id='holidayModeOverlay';o.className='holidayModeOverlay';
 o.innerHTML='<div class="holidayModeCard"><div class="holidayModeTitle">Special Work Day</div><div class="holidayModeText">'+(sunday?'Sunday is already an off day. All worked time today will count as overtime.':'Use this only when today is an official holiday.')+'</div><label class="holidayToggleRow"><span><b>Is today a holiday?</b><small>When enabled, there is no standard work-hour limit and every worked minute counts as overtime.</small></span><input type="checkbox" id="holidayModeSwitch" '+(flag?'checked':'')+'><i></i></label><div class="holidayModeActions"><button type="button" class="btn primary" id="holidayModeSave">Save</button><button type="button" class="btn ghost" id="holidayModeCancel">Cancel</button></div></div>';
 document.body.appendChild(o);
 E('holidayModeCancel').onclick=function(){remove('holidayModeOverlay')};
 E('holidayModeSave').onclick=function(){var on=E('holidayModeSwitch').checked,a=getRecords(),i,r=null;try{if(on)localStorage.setItem('attendance_special_ot_'+date,'holiday');else localStorage.removeItem('attendance_special_ot_'+date)}catch(e){}for(i=0;i<a.length;i++)if(a[i].date===date){r=a[i];break}if(r&&!r.checkIn){if(on){r.status='Holiday';r.specialOT=true;if(!r.reason)r.reason='Holiday'}else if(sunday){r.status='Week Off';r.specialOT=true;if(r.reason==='Holiday')r.reason=''}else{r.status='Present';r.specialOT=false;if(r.reason==='Holiday')r.reason=''}putRecords(a)}remove('holidayModeOverlay');if(window.appDialog)window.appDialog('Saved',on?'Today will be treated as a holiday. All worked time will count as overtime.':(sunday?'Sunday overtime mode remains active automatically.':'Today will use normal work-hour rules.'),[{label:'OK',kind:'primary'}])};
 o.onclick=function(e){if(e.target===o)remove('holidayModeOverlay')};
}

function bindLongPress(){
 var b=E('punchBtn');if(!b||b.getAttribute('data-v113-hold')==='1')return;b.setAttribute('data-v113-hold','1');
 var timer=null,suppress=false;
 function cancel(){if(timer){clearTimeout(timer);timer=null}}
 function start(){var x=current();if(x&&x.checkIn)return;cancel();timer=setTimeout(function(){timer=null;suppress=true;showHolidayMode();try{if(navigator.vibrate)navigator.vibrate(35)}catch(err){}},2000)}
 b.addEventListener('pointerdown',start);
 b.addEventListener('pointerup',function(){cancel();if(suppress)setTimeout(function(){suppress=false},500)});
 b.addEventListener('pointercancel',function(){cancel();suppress=false});
 b.addEventListener('pointerleave',function(){cancel()});
 b.addEventListener('contextmenu',function(e){e.preventDefault()});
 b.addEventListener('click',function(e){if(!suppress)return;e.preventDefault();e.stopImmediatePropagation();suppress=false},true);
}

window.confirmClockOut=function(record,outTime,done){
 remove('clockOutConfirmOverlay');
 var s=settings(),worked=workBetween(record.checkIn,outTime),std=s.h*60+s.m,special=isSpecial(record),title='Ready to clock out?',detail='',sub='Total time: '+hm(worked);
 if(special){var kind=record.status==='Holiday'?'holiday':(isSunday(record.date)?'Sunday':'off day');detail='Today is a '+kind+'. All '+hm(worked)+' worked today will count as overtime.'}
 else if(worked<std){detail='You have completed '+hm(worked)+' today. '+hm(std-worked)+' is still remaining from your '+hm(std)+' standard work time.'}
 else{var extra=Math.max(0,worked-std);detail='You have completed your '+hm(std)+' standard work time.'+(extra?' Extra worked time: '+hm(extra)+'.':'')}
 var o=document.createElement('div');o.id='clockOutConfirmOverlay';o.className='clockOutConfirmOverlay';o.innerHTML='<div class="clockOutConfirmCard"><div class="clockOutConfirmIcon">↗</div><div class="clockOutConfirmTitle">'+title+'</div><div class="clockOutConfirmText">'+detail+'</div><div class="clockOutConfirmSub">'+sub+'</div><div class="clockOutConfirmActions"><button type="button" id="clockOutCancel">Cancel</button><button type="button" id="clockOutYes">Yes, Clock Out</button></div></div>';document.body.appendChild(o);E('clockOutCancel').onclick=function(){remove('clockOutConfirmOverlay')};E('clockOutYes').onclick=function(){remove('clockOutConfirmOverlay');if(done)done()};o.onclick=function(e){if(e.target===o)remove('clockOutConfirmOverlay')};
};

function syncEditWhenOpened(){var modal=E('editModal');if(!modal)return;var obs=new MutationObserver(function(){if(!modal.classList.contains('show'))return;setTimeout(function(){var ids=['editPopupDate','editPopupStatus','editInH','editInM','editInP','editOutH','editOutM','editOutP'],i,z;for(i=0;i<ids.length;i++){z=E(ids[i]);if(z)try{z.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}z=E('editPopupDate');if(z&&z._v112CalBtn)z._v112CalBtn.textContent=z.value||'Select date'},0)});obs.observe(modal,{attributes:true,attributeFilter:['class']})}

function init(){bindLongPress();syncEditWhenOpened()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
