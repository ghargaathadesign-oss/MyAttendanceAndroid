(function(){
'use strict';
var DB_NAME=window.attendanceUserDb?window.attendanceUserDb('attendance_docs_v81'):'attendance_docs_v81';
var STORE='documents';
var CHUNK=512*1024;

function nativeReady(){
 try{return !!(window.Android&&Android.secureEncryptValue&&Android.secureDecryptValue)}catch(e){return false}
}
function openDb(){
 return new Promise(function(resolve,reject){
  var r=indexedDB.open(DB_NAME,1);
  r.onupgradeneeded=function(e){var db=e.target.result;if(!db.objectStoreNames.contains(STORE))db.createObjectStore(STORE,{keyPath:'id'})};
  r.onsuccess=function(e){resolve(e.target.result)};
  r.onerror=function(){reject(r.error||new Error('Could not open document storage'))};
 });
}
function readAll(db){
 return new Promise(function(resolve,reject){
  var r=db.transaction([STORE],'readonly').objectStore(STORE).getAll();
  r.onsuccess=function(){resolve(r.result||[])};
  r.onerror=function(){reject(r.error||new Error('Could not read documents'))};
 });
}
function putOne(db,item){
 return new Promise(function(resolve,reject){
  var tx=db.transaction([STORE],'readwrite');
  tx.objectStore(STORE).put(item);
  tx.oncomplete=function(){resolve(item)};
  tx.onerror=function(){reject(tx.error||new Error('Could not save encrypted document'))};
 });
}
function blobToBase64(blob){
 return new Promise(function(resolve,reject){
  var r=new FileReader();
  r.onload=function(e){var d=String(e.target.result||''),p=d.indexOf(',');resolve(p>=0?d.slice(p+1):d)};
  r.onerror=function(){reject(new Error('Could not read document'))};
  r.readAsDataURL(blob);
 });
}
function b64ToBlob(b64,mime){
 var bin=atob(String(b64||'')),len=bin.length,arr=new Uint8Array(len),i;
 for(i=0;i<len;i++)arr[i]=bin.charCodeAt(i);
 return new Blob([arr],{type:mime||'application/octet-stream'});
}
function enc(ctx,value){
 if(!nativeReady())throw new Error('Encrypted document storage is unavailable');
 var out=Android.secureEncryptValue(String(ctx),String(value==null?'':value));
 if(!out)throw new Error('Document encryption failed');
 return String(out);
}
function dec(ctx,value){
 if(!nativeReady())throw new Error('Encrypted document storage is unavailable');
 var out=Android.secureDecryptValue(String(ctx),String(value||''));
 if(out==null)throw new Error('Document decryption failed');
 return String(out);
}
function metaOf(item){
 return {
  type:item.type||'Other',
  name:item.name||'Document',
  issue:item.issue||'',
  expiry:item.expiry||'',
  notes:item.notes||'',
  fileName:item.fileName||'document',
  mime:item.mime||'application/octet-stream',
  size:+item.size||0
 };
}
function encryptMeta(id,meta){return enc('doc:'+id+':meta',JSON.stringify(meta))}
function decryptMeta(item){
 if(item.encVersion===2){
  return JSON.parse(dec('doc:'+item.id+':meta',item.metaEnc));
 }
 return metaOf(item);
}
function encryptChunks(id,b64){
 var out=[],i,n=0,part;
 for(i=0;i<b64.length;i+=CHUNK){
  part=b64.slice(i,i+CHUNK);
  out.push(enc('doc:'+id+':chunk:'+n,part));
  n++;
 }
 return out;
}
function decryptChunks(item){
 var out='',i;
 for(i=0;i<(item.chunks||[]).length;i++)out+=dec('doc:'+item.id+':chunk:'+i,item.chunks[i]);
 return out;
}
function encryptedRecord(id,createdAt,meta,b64){
 return {id:id,createdAt:createdAt||Date.now(),encVersion:2,metaEnc:encryptMeta(id,meta),chunks:encryptChunks(id,b64)};
}
function encryptFile(meta,file,id,createdAt){
 return blobToBase64(file).then(function(b64){return encryptedRecord(id,createdAt,meta,b64)});
}
function migrateOne(db,item){
 if(!item||item.encVersion===2||!item.blob)return Promise.resolve(false);
 return blobToBase64(item.blob).then(function(b64){
  var r=encryptedRecord(item.id,item.createdAt||Date.now(),metaOf(item),b64);
  return putOne(db,r).then(function(){return true});
 }).catch(function(){return false});
}
function migrateAll(){
 if(!nativeReady())return Promise.resolve();
 return openDb().then(function(db){
  return readAll(db).then(function(items){
   var p=Promise.resolve(),i,migrated=0,failed=0;
   for(i=0;i<items.length;i++)(function(it){
    p=p.then(function(){return migrateOne(db,it).then(function(ok){if(ok)migrated++;else if(it&&it.encVersion!==2)failed++})});
   })(items[i]);
   return p.then(function(){db.close();window.attendanceDocumentCryptoMigration={migrated:migrated,failed:failed}});
  },function(err){db.close();throw err});
 });
}

window.attendanceDocEncryptFile=function(meta,file,id,createdAt){
 return encryptFile(meta,file,id,createdAt);
};
window.attendanceDocMeta=function(item){
 try{return decryptMeta(item)}catch(e){return null}
};
window.attendanceDocDecryptRecord=function(item){
 return new Promise(function(resolve,reject){
  try{
   if(!item){resolve(null);return}
   if(item.encVersion!==2){resolve(item);return}
   var meta=decryptMeta(item),b64=decryptChunks(item),out={id:item.id,createdAt:item.createdAt};
   var k;for(k in meta)if(Object.prototype.hasOwnProperty.call(meta,k))out[k]=meta[k];
   out.blob=b64ToBlob(b64,meta.mime);
   resolve(out);
  }catch(e){reject(e)}
 });
};
window.attendanceDocumentsReady=Promise.resolve(window.attendanceStorageReady).then(migrateAll).catch(function(e){
 window.attendanceDocumentCryptoMigration={migrated:0,failed:-1,error:String(e&&e.message||e)};
});
})();