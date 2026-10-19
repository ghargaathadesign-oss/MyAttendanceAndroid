(function(){
'use strict';
var A=window.AttendanceAppApi;
if(window.renderFriendlyLeaves){var leaves=window.renderFriendlyLeaves;window.renderFriendlyLeaves=function(){return A.withView(leaves,this,arguments)}}
function resumed(){if(!document.hidden){A.invalidateData()}}
document.addEventListener('visibilitychange',resumed);
new MutationObserver(function(ms){ms.forEach(function(m){var el=m.target;if((el.classList.contains('screen')&&el.classList.contains('active'))||(el.id==='editModal'&&el.classList.contains('show')))requestAnimationFrame(function(){if(window.attendanceDecorateSelects)attendanceDecorateSelects(el);if(window.attendanceDecorateDates)attendanceDecorateDates(el)})})}).observe(document.body,{attributes:true,subtree:true,attributeFilter:['class']});
window.addEventListener('storage',function(e){if(e.key&&e.key.indexOf('attendance_')===0)resumed()});
})();
