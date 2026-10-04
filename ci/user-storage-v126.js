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
var SECURE_DONE='myattendance_v123_secure_migrated_'+safe;
var RECOVERY_KEY='myattendance_v126_restore_recovery_'+safe;

function isLogical(k){return typeof k==='string'&&k.indexOf('attendance_')===0&&k.indexOf('attendance_user_')!==0&&k.indexOf('attendance_guest__')!==0}
function physical(k){k=String(k);return isLogical(k)?prefix+k:k}
function rawKeys(){var out=[],i,k;for(i=0;i<localStorage.length;i++){k=rawKey.call(localStorage,i);if(k!=null)out.push(String(k))}return out}
function isLegacyKey(k){return k.indexOf('attendance_')===0&&k.indexOf('attendance_user_')!==0&&k.indexOf('attendance_guest__')!==0}
function nativeSecureReady(){if(!uid||!window.Android||!Android.secureGet||!Android.secureSet||!Android.secureRemove||!Android.secureKeys)return false;try{return !Android.secureStorageAvailable||!!Android.secureStorageAvailable()}catch(e){return false}}
var secureReady=nativeSecureReady();
function secureGetPhysical(k){try{return Android.secureGet(String(k))}catch(e){return null}}
function secureSetPhysical(k,v){try{return !!Android.secureSet(String(k),String(v))}catch(e){return false}}
function secureRemovePhysical(k){try{Android.secureRemove(String(k));return true}catch(e){return false}}
function secureKeys(){if(!secureReady)return[];try{var a=JSON.parse(String(Android.secureKeys(prefix)||'[]'));return Array.isArray(a)?a:[]}catch(e){return[]}}
function secureClearPrefix(){try{if(secureReady&&Android.secureClearPrefix)Android.secureClearPrefix(prefix)}catch(e){}}

function migrateV12Plaintext(){
 if(!uid)return false;
 var owner=rawGet.call(localStorage,LEGACY_OWNER),keys=rawKeys(),i,k,v;
 if(!owner){owner=uid;rawSet.call(localStorage,LEGACY_OWNER,uid)}
 if(owner===uid){for(i=0;i<keys.length;i++){k=keys[i];if(!isLegacyKey(k))continue;if(rawGet.call(localStorage,prefix+k)==null){v=rawGet.call(localStorage,k);if(v!=null)rawSet.call(localStorage,prefix+k,v)}}}
 return owner===uid;
}
var ownsLegacy=migrateV12Plaintext();

function migrateToKeystore(){
 if(!secureReady||!uid)return;
 var done=rawGet.call(localStorage,SECURE_DONE),keys=rawKeys(),i,k,v,logical,ok=true,stored;
 if(done==='1')return;
 for(i=0;i<keys.length;i++){
   k=keys[i];if(k.indexOf(prefix)!==0)continue;logical=k.slice(prefix.length);if(logical.indexOf('attendance_')!==0)continue;v=rawGet.call(localStorage,k);if(v==null)continue;
   stored=secureGetPhysical(k);if(stored!==v){if(!secureSetPhysical(k,v)){ok=false;continue}stored=secureGetPhysical(k)}
   if(stored===v)rawRemove.call(localStorage,k);else ok=false;
 }
 if(ownsLegacy){
   keys=rawKeys();
   for(i=0;i<keys.length;i++){
     k=keys[i];if(!isLegacyKey(k))continue;v=rawGet.call(localStorage,k);if(v==null)continue;stored=secureGetPhysical(prefix+k);
     if(stored!==v){if(!secureSetPhysical(prefix+k,v)){ok=false;continue}stored=secureGetPhysical(prefix+k)}
     if(stored===v)rawRemove.call(localStorage,k);else ok=false;
   }
 }
 if(ok)rawSet.call(localStorage,SECURE_DONE,'1');
}
migrateToKeystore();

proto.getItem=function(k){if(this!==window.localStorage)return rawGet.call(this,k);k=String(k);if(isLogical(k)&&secureReady)return secureGetPhysical(prefix+k);return rawGet.call(this,physical(k))};
proto.setItem=function(k,v){if(this!==window.localStorage)return rawSet.call(this,k,v);k=String(k);if(isLogical(k)&&secureReady){if(!secureSetPhysical(prefix+k,String(v)))throw new Error('Secure storage write failed');return}return rawSet.call(this,physical(k),String(v))};
proto.removeItem=function(k){if(this!==window.localStorage)return rawRemove.call(this,k);k=String(k);if(isLogical(k)&&secureReady){secureRemovePhysical(prefix+k);return}return rawRemove.call(this,physical(k))};

window.attendanceRuntimeUid=uid;
window.attendanceUserPrefix=prefix;
window.attendanceSecureLocalStorage=secureReady;
window.attendanceUserKey=function(k){return physical(k)};
window.attendanceUserDb=function(name){return prefix+String(name||'')};

window.attendanceSnapshotCurrentUser=function(){
 var o={},a,i,k,logical,v;
 if(secureReady){a=secureKeys();for(i=0;i<a.length;i++){k=String(a[i]);if(k.indexOf(prefix)!==0)continue;logical=k.slice(prefix.length);if(logical.indexOf('attendance_')!==0||logical.indexOf('attendance_cloud_')===0)continue;v=secureGetPhysical(k);if(v!=null)o[logical]=v}return o}
 a=rawKeys();for(i=0;i<a.length;i++){k=a[i];if(k.indexOf(prefix)!==0)continue;logical=k.slice(prefix.length);if(logical.indexOf('attendance_')!==0||logical.indexOf('attendance_cloud_')===0)continue;v=rawGet.call(localStorage,k);if(v!=null)o[logical]=v}return o;
};

window.attendanceClearCurrentUser=function(){
 var a,i,k;if(secureReady){secureClearPrefix();try{Android.secureRemove(RECOVERY_KEY)}catch(e){}}
 a=rawKeys();for(i=0;i<a.length;i++){k=a[i];if(k.indexOf(prefix)===0)rawRemove.call(localStorage,k)}
 try{indexedDB.deleteDatabase(prefix+'attendance_docs_v81')}catch(e){}
};

window.attendanceRestoreCurrentUser=function(o){
 if(!o||typeof o!=='object'||Array.isArray(o))return false;
 if(window.AttendancePolicy&&AttendancePolicy.validateStorage){var check=AttendancePolicy.validateStorage(o);if(!check.ok)return false}
 var old=window.attendanceSnapshotCurrentUser(),a,i,k,logical,map={},verify,ok=true;
 function buildMap(src){var m={},q,l;for(q in src)if(Object.prototype.hasOwnProperty.call(src,q)){l=String(q);if(l.indexOf(prefix)===0)l=l.slice(prefix.length);else if(l.indexOf('attendance_user_')===0){var p=l.indexOf('__');if(p>=0)l=l.slice(p+2)}if(l.indexOf('attendance_')!==0||l.indexOf('attendance_cloud_')===0)continue;m[prefix+l]=String(src[q])}return m}
 if(secureReady&&window.Android&&Android.secureReplacePrefix){
   try{Android.secureSet(RECOVERY_KEY,JSON.stringify(old))}catch(e){}
   map=buildMap(o);try{ok=!!Android.secureReplacePrefix(prefix,JSON.stringify(map))}catch(e){ok=false}
   if(!ok)return false;
   verify=window.attendanceSnapshotCurrentUser();
   for(k in o)if(Object.prototype.hasOwnProperty.call(o,k)){logical=String(k);if(logical.indexOf(prefix)===0)logical=logical.slice(prefix.length);else if(logical.indexOf('attendance_user_')===0){var pp=logical.indexOf('__');if(pp>=0)logical=logical.slice(pp+2)}if(logical.indexOf('attendance_')!==0||logical.indexOf('attendance_cloud_')===0)continue;if(String(verify[logical])!==String(o[k])){ok=false;break}}
   if(!ok){try{Android.secureReplacePrefix(prefix,JSON.stringify(buildMap(old)))}catch(e){}return false}
   try{Android.secureRemove(RECOVERY_KEY)}catch(e){}return true;
 }
 try{
   a=rawKeys();for(i=0;i<a.length;i++){k=a[i];if(k.indexOf(prefix)===0)rawRemove.call(localStorage,k)}
   for(k in o)if(Object.prototype.hasOwnProperty.call(o,k)){logical=String(k);if(logical.indexOf(prefix)===0)logical=logical.slice(prefix.length);else if(logical.indexOf('attendance_user_')===0){var p2=logical.indexOf('__');if(p2>=0)logical=logical.slice(p2+2)}if(logical.indexOf('attendance_')!==0||logical.indexOf('attendance_cloud_')===0)continue;rawSet.call(localStorage,prefix+logical,String(o[k]))}
   return true;
 }catch(e){try{a=rawKeys();for(i=0;i<a.length;i++){k=a[i];if(k.indexOf(prefix)===0)rawRemove.call(localStorage,k)};for(k in old)if(Object.prototype.hasOwnProperty.call(old,k))rawSet.call(localStorage,prefix+k,String(old[k]))}catch(ignore){}return false}
};

function migrateDocs(){
 return new Promise(function(resolve){
   if(!uid||!ownsLegacy){resolve();return}
   var oldName='attendance_docs_v81',newName=prefix+oldName,created=false,oldReq;
   try{oldReq=indexedDB.open(oldName,1)}catch(e){resolve();return}
   oldReq.onupgradeneeded=function(){created=true};oldReq.onerror=function(){resolve()};
   oldReq.onsuccess=function(ev){
     var oldDb=ev.target.result;
     if(!oldDb.objectStoreNames.contains('documents')){oldDb.close();if(created)try{indexedDB.deleteDatabase(oldName)}catch(e){}resolve();return}
     var tx=oldDb.transaction(['documents'],'readonly'),get=tx.objectStore('documents').getAll();
     get.onerror=function(){oldDb.close();resolve()};
     get.onsuccess=function(){var items=get.result||[];oldDb.close();if(!items.length){resolve();return}var nr=indexedDB.open(newName,1);nr.onupgradeneeded=function(e){var db=e.target.result;if(!db.objectStoreNames.contains('documents'))db.createObjectStore('documents',{keyPath:'id'})};nr.onerror=function(){resolve()};nr.onsuccess=function(e){var db=e.target.result,t=db.transaction(['documents'],'readwrite'),st=t.objectStore('documents'),i;for(i=0;i<items.length;i++)st.put(items[i]);t.oncomplete=function(){db.close();resolve()};t.onerror=function(){db.close();resolve()}}}
   }
 })
}
window.attendanceStorageReady=migrateDocs();
})();