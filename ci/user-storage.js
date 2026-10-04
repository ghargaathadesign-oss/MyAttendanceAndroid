(function(){
'use strict';
var proto=window.Storage&&Storage.prototype;
if(!proto||!window.localStorage)return;
var rawGet=proto.getItem,rawSet=proto.setItem,rawRemove=proto.removeItem,rawKey=proto.key;
var uid='';
try{if(window.Android&&Android.currentUserUid)uid=String(Android.currentUserUid()||'')}catch(e){uid=''}
var safe=uid?uid.replace(/[^A-Za-z0-9_-]/g,'_'):'';
var prefix=uid?'attendance_user_'+safe+'__':'attendance_guest__';
var LEGACY_OWNER='myattendance_v12_legacy_owner';
var DONE_KEY=prefix+'myattendance_v12_migrated';

function isLogical(k){return typeof k==='string'&&k.indexOf('attendance_')===0&&k.indexOf('attendance_user_')!==0&&k.indexOf('attendance_guest__')!==0}
function physical(k){k=String(k);return isLogical(k)?prefix+k:k}
function rawKeys(){var out=[],i,k;for(i=0;i<localStorage.length;i++){k=rawKey.call(localStorage,i);if(k!=null)out.push(String(k))}return out}
function legacyKeys(){var a=rawKeys(),out=[],i,k;for(i=0;i<a.length;i++){k=a[i];if(k.indexOf('attendance_')===0&&k.indexOf('attendance_user_')!==0&&k.indexOf('attendance_guest__')!==0)out.push(k)}return out}
function migrateLocal(){
 if(!uid)return false;
 var done=rawGet.call(localStorage,DONE_KEY);if(done==='1')return rawGet.call(localStorage,LEGACY_OWNER)===uid;
 var owner=rawGet.call(localStorage,LEGACY_OWNER),keys=legacyKeys(),i,k,v;
 if(!owner){owner=uid;rawSet.call(localStorage,LEGACY_OWNER,uid)}
 if(owner===uid){
   for(i=0;i<keys.length;i++){k=keys[i];if(rawGet.call(localStorage,prefix+k)==null){v=rawGet.call(localStorage,k);if(v!=null)rawSet.call(localStorage,prefix+k,v)}}
 }
 return owner===uid;
}
var ownsLegacy=migrateLocal();

proto.getItem=function(k){if(this===window.localStorage)return rawGet.call(this,physical(k));return rawGet.call(this,k)};
proto.setItem=function(k,v){if(this===window.localStorage)return rawSet.call(this,physical(k),String(v));return rawSet.call(this,k,v)};
proto.removeItem=function(k){if(this===window.localStorage)return rawRemove.call(this,physical(k));return rawRemove.call(this,k)};

window.attendanceRuntimeUid=uid;
window.attendanceUserPrefix=prefix;
window.attendanceUserKey=function(k){return physical(k)};
window.attendanceUserDb=function(name){return prefix+String(name||'')};
window.attendanceSnapshotCurrentUser=function(){
 var o={},a=rawKeys(),i,k,logical,v;
 for(i=0;i<a.length;i++){k=a[i];if(k.indexOf(prefix)!==0)continue;logical=k.slice(prefix.length);if(logical.indexOf('attendance_')!==0||logical.indexOf('attendance_cloud_')===0)continue;v=rawGet.call(localStorage,k);if(v!=null)o[logical]=v}
 return o;
};
window.attendanceClearCurrentUser=function(){
 var a=rawKeys(),i,k;for(i=0;i<a.length;i++){k=a[i];if(k.indexOf(prefix)===0)rawRemove.call(localStorage,k)}
 try{indexedDB.deleteDatabase(prefix+'attendance_docs_v81')}catch(e){}
};
window.attendanceRestoreCurrentUser=function(o){
 if(!o||typeof o!=='object')return false;
 var a=rawKeys(),i,k,logical,v;
 for(i=0;i<a.length;i++){k=a[i];if(k.indexOf(prefix)!==0)continue;logical=k.slice(prefix.length);if(logical.indexOf('attendance_')===0&&logical.indexOf('attendance_cloud_')!==0)rawRemove.call(localStorage,k)}
 for(k in o)if(Object.prototype.hasOwnProperty.call(o,k)){
   logical=String(k);
   if(logical.indexOf(prefix)===0)logical=logical.slice(prefix.length);
   else if(logical.indexOf('attendance_user_')===0){var p=logical.indexOf('__');if(p>=0)logical=logical.slice(p+2)}
   if(logical.indexOf('attendance_')!==0||logical.indexOf('attendance_cloud_')===0)continue;
   v=o[k];rawSet.call(localStorage,prefix+logical,String(v))
 }
 return true;
};

function migrateDocs(){
 return new Promise(function(resolve){
   if(!uid||!ownsLegacy){rawSet.call(localStorage,DONE_KEY,'1');resolve();return}
   var oldName='attendance_docs_v81',newName=prefix+oldName,created=false,oldReq;
   try{oldReq=indexedDB.open(oldName,1)}catch(e){rawSet.call(localStorage,DONE_KEY,'1');resolve();return}
   oldReq.onupgradeneeded=function(){created=true};
   oldReq.onerror=function(){rawSet.call(localStorage,DONE_KEY,'1');resolve()};
   oldReq.onsuccess=function(ev){
     var oldDb=ev.target.result;
     if(!oldDb.objectStoreNames.contains('documents')){oldDb.close();if(created)try{indexedDB.deleteDatabase(oldName)}catch(e){}rawSet.call(localStorage,DONE_KEY,'1');resolve();return}
     var tx=oldDb.transaction(['documents'],'readonly'),get=tx.objectStore('documents').getAll();
     get.onerror=function(){oldDb.close();rawSet.call(localStorage,DONE_KEY,'1');resolve()};
     get.onsuccess=function(){
       var items=get.result||[];oldDb.close();
       if(!items.length){rawSet.call(localStorage,DONE_KEY,'1');resolve();return}
       var nr=indexedDB.open(newName,1);
       nr.onupgradeneeded=function(e){var db=e.target.result;if(!db.objectStoreNames.contains('documents'))db.createObjectStore('documents',{keyPath:'id'})};
       nr.onerror=function(){rawSet.call(localStorage,DONE_KEY,'1');resolve()};
       nr.onsuccess=function(e){var db=e.target.result,t=db.transaction(['documents'],'readwrite'),st=t.objectStore('documents'),i;for(i=0;i<items.length;i++)st.put(items[i]);t.oncomplete=function(){db.close();rawSet.call(localStorage,DONE_KEY,'1');resolve()};t.onerror=function(){db.close();rawSet.call(localStorage,DONE_KEY,'1');resolve()}}
     }
   }
 })
}
window.attendanceStorageReady=migrateDocs();
})();