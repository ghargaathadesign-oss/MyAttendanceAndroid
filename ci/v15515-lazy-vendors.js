(function(){
'use strict';
var excelPromise=null;
window.loadAttendanceExcel=function(){
 if(window.ExcelJS)return Promise.resolve();
 if(excelPromise)return excelPromise;
 excelPromise=new Promise(function(resolve,reject){
  var script=document.createElement('script');script.src='exceljs.min.js';script.async=true;
  script.onload=function(){if(window.ExcelJS)resolve();else{excelPromise=null;reject(new Error('Excel engine could not load.'))}};
  script.onerror=function(){script.remove();excelPromise=null;reject(new Error('Excel engine could not load.'))};
  document.head.appendChild(script);
 });
 return excelPromise;
};
})();
