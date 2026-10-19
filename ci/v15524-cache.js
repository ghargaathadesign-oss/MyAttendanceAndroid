// Synchronous render snapshots only: never retain account data between renders.
var viewFrame=null,dataRevision=0,lastPaintRevision=-1,changeQueued=false;
var viewStats={frames:0,reads:0,dataParses:0,salaryCalculations:0};
function viewRead(key){if(!viewFrame)return localStorage.getItem(key);if(!Object.prototype.hasOwnProperty.call(viewFrame.reads,key)){viewStats.reads++;viewFrame.reads[key]=localStorage.getItem(key)}return viewFrame.reads[key]}
function withView(fn,self,args){if(viewFrame)return fn.apply(self,args||[]);viewStats.frames++;viewFrame={reads:Object.create(null),data:null,salary:Object.create(null)};try{return fn.apply(self,args||[])}finally{viewFrame=null}}
function resetView(){if(viewFrame){viewFrame.reads=Object.create(null);viewFrame.data=null;viewFrame.salary=Object.create(null)}}
function dataChanged(key){dataRevision++;resetView();
 if(/^(attendance_v8|attendance_settings_|attendance_salary_|attendance_leave_|attendance_ot_cover_)/.test(key)){
  if(window.AttendanceV14)AttendanceV14.onDataChanged();if(window.AttendanceV15)AttendanceV15.onDataChanged();
 }
 if(changeQueued)return;changeQueued=true;
 Promise.resolve().then(function(){changeQueued=false;if(lastPaintRevision===dataRevision||document.hidden)return;var rev=dataRevision;requestAnimationFrame(function(){if(lastPaintRevision<rev&&!document.hidden)renderAll()})});
}
function wrapView(fn,paint){return function(){var result=withView(fn,this,arguments);if(paint)lastPaintRevision=dataRevision;return result}}
renderAll=wrapView(renderAll,true);renderScreen=wrapView(renderScreen,false);renderHome=wrapView(renderHome,false);renderSalary=wrapView(renderSalary,false);
var clockTick=tick,lastTickKey='';tick=function(){if(document.hidden||activeScreen()!=='home')return;var key=Math.floor(Date.now()/60000)+'|'+dataRevision;if(key===lastTickKey)return;lastTickKey=key;return withView(clockTick,this,arguments)};
