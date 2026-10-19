(function(){
'use strict';
function E(id){return document.getElementById(id)}
function A(){return window.AttendanceAppApi}
function t(s){return window.AttendanceI18n?AttendanceI18n.t(s):s}
function series(month,records,settings,today){
 var parts=month.split('-'),count=new Date(+parts[0],+parts[1],0).getDate(),map={},daily=[],months=[];
 records.forEach(function(r){if(r.date<=today)map[r.date]=r});
 for(var i=0;i<6;i++){var d=new Date(+parts[0],+parts[1]-6+i,1),ym=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0'),rr=records.filter(function(r){return r.date.slice(0,7)===ym&&r.date<=today}),required=0,worked=0;rr.forEach(function(r){required+=AttendancePolicy.requiredMinutes(r,settings);worked+=AttendancePolicy.workedMinutes(r)});months.push({month:ym,required:rr.length?required/60:null,worked:rr.length?worked/60:null})}
 function minute(time){var s=AttendancePolicy.normalizeTime(time);if(!s)return null;var p=s.split(':');return +p[0]*60+ +p[1]}
 for(var day=1;day<=count;day++){var date=month+'-'+String(day).padStart(2,'0'),r=map[date],inside=r?minute(r.checkIn):null,outside=r?minute(r.checkOut):null;if(inside!==null&&outside!==null&&outside<inside)outside+=1440;daily.push({date:date,inTime:inside,outTime:outside})}
 return{months:months,daily:daily};
}
function svgNode(name,attrs,text){var n=document.createElementNS('http://www.w3.org/2000/svg',name);Object.keys(attrs||{}).forEach(function(k){n.setAttribute(k,attrs[k])});if(text!==undefined)n.textContent=text;return n}
function hours(n){return n===null?'—':Number(n.toFixed(1))+'h'}
function clock(n){if(n===null)return '—';var extra=n>=1440?' +1 day':'';n=n%1440;return String(Math.floor(n/60)).padStart(2,'0')+':'+String(n%60).padStart(2,'0')+extra}
function chart(box,rows,keys,time){
 box.replaceChildren();box.className='reportLineChart';var width=time?720:360,height=235,left=time?66:40,right=width-16,top=18,bottom=195,values=[];
 rows.forEach(function(r){keys.forEach(function(k){if(r[k]!==null)values.push(r[k])})});var min=time&&values.length?Math.max(0,Math.floor(Math.min.apply(null,values)/120)*120-120):0,max=time&&values.length?Math.ceil(Math.max.apply(null,values)/120)*120+120:Math.max(1,Math.ceil(Math.max.apply(null,values.concat([1]))/10)*10);if(time&&!values.length)max=1440;
 var svg=svgNode('svg',{viewBox:'0 0 '+width+' '+height,role:'img','aria-label':t(time?'Monthly in and out times':'Required and worked hours by month')});if(time)svg.classList.add('timePlot');
 var desc=svgNode('desc',{},t('Missing records are gaps. Tap a point for details.'));svg.appendChild(desc);
 function x(i){return left+i*(right-left)/Math.max(1,rows.length-1)}function y(v){return bottom-(v-min)/(max-min)*(bottom-top)}
 for(var i=0;i<=4;i++){var v=min+(max-min)*i/4,yy=y(v);svg.appendChild(svgNode('line',{x1:left,x2:right,y1:yy,y2:yy,class:'chartGrid'}));svg.appendChild(svgNode('text',{x:left-7,y:yy+3,'text-anchor':'end',class:'chartAxis'},time?clock(Math.round(v)):Math.round(v)+'h'))}
 var output=document.createElement('p');output.className='chartReadout';output.textContent=t('Tap a point to see its values.');
 rows.forEach(function(r,i){if(time&&i!==0&&i!==rows.length-1&&(i+1)%5!==0)return;var label=time?String(i+1):new Date(r.month+'-01T12:00:00').toLocaleDateString(document.documentElement.lang==='hi'?'hi-IN':'en-IN',{month:'short',year:'2-digit'});svg.appendChild(svgNode('text',{x:x(i),y:bottom+22,'text-anchor':'middle',class:'chartAxis'},label))});
 keys.forEach(function(key,index){var path='',open=false;rows.forEach(function(r,i){var v=r[key];if(v===null){open=false;return}path+=(open?'L':'M')+x(i).toFixed(2)+','+y(v).toFixed(2)+' ';open=true});svg.appendChild(svgNode('path',{d:path,fill:'none',class:'chartSeries series'+index,'stroke-width':2.5,'stroke-linecap':'round','stroke-linejoin':'round'}));rows.forEach(function(r,i){if(r[key]===null)return;var point=svgNode('circle',{cx:x(i),cy:y(r[key]),r:time?5:4,class:'chartPoint series'+index,tabindex:0,role:'button','aria-label':(r.date||r.month)+', '+keys.map(function(k){return k+': '+(time?clock(r[k]):hours(r[k]))}).join(', ')});point.appendChild(svgNode('title',{},point.getAttribute('aria-label')));function show(){output.textContent=(r.date||r.month)+' · '+t(time?'In':'Required')+' '+(time?clock(r[keys[0]]):hours(r[keys[0]]))+' · '+t(time?'Out':'Worked')+' '+(time?clock(r[keys[1]]):hours(r[keys[1]]))}point.onclick=show;point.onkeydown=function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();show()}};svg.appendChild(point)})});
 var scroll=document.createElement('div');scroll.className='chartScroll';scroll.appendChild(svg);box.appendChild(scroll);
 var legend=document.createElement('div');legend.className='chartLegend';[time?'In time':'Required hours',time?'Out time':'Worked hours'].forEach(function(label,i){var span=document.createElement('span');span.className='legend'+i;span.textContent=t(label);legend.appendChild(span)});box.appendChild(legend);box.appendChild(output);
 if(!values.length){output.textContent=t('No recorded data for this period.')}
}
function render(month){if(!A())return;month=month||E('reportMonth').value||A().monthNow();if(!/^\d{4}-\d{2}$/.test(month))return;var data=series(month,A().dataGet(),A().setGet(),A().nowDate());chart(E('reportTrend'),data.months,['required','worked'],false);chart(E('reportPunchChart'),data.daily,['inTime','outTime'],true);E('reportPunchMonth').textContent=new Date(month+'-01T12:00:00').toLocaleDateString(document.documentElement.lang==='hi'?'hi-IN':'en-IN',{month:'long',year:'numeric'})}
window.AttendanceReports19={series:series,render:render};
function init(){document.addEventListener('attendance-language-changed',function(){if(E('screen-setting-reports').classList.contains('active'))render()})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
