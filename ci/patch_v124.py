from pathlib import Path
import re, sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
p=assets/'app.js'
s=p.read_text(encoding='utf-8')

crypto_helpers=r'''
var docCryptoKeyPromise=null,docMigrationPromise=null;
function docUtf8(s){s=String(s==null?'':s);if(window.TextEncoder)return new TextEncoder().encode(s);var x=unescape(encodeURIComponent(s)),a=new Uint8Array(x.length),i;for(i=0;i<x.length;i++)a[i]=x.charCodeAt(i);return a}
function docUtf8Text(buf){var a=buf instanceof Uint8Array?buf:new Uint8Array(buf),i,x='';if(window.TextDecoder)return new TextDecoder('utf-8').decode(a);for(i=0;i<a.length;i++)x+=String.fromCharCode(a[i]);return decodeURIComponent(escape(x))}
function docBytesB64(buf){var a=buf instanceof Uint8Array?buf:new Uint8Array(buf),out='',i,chunk=32768;for(i=0;i<a.length;i+=chunk)out+=String.fromCharCode.apply(null,a.subarray(i,Math.min(i+chunk,a.length)));return btoa(out)}
function docB64Bytes(s){var b=atob(String(s||'')),a=new Uint8Array(b.length),i;for(i=0;i<b.length;i++)a[i]=b.charCodeAt(i);return a}
function docReadBuffer(blob){return new Promise(function(resolve,reject){if(blob instanceof ArrayBuffer){resolve(blob);return}if(blob&&blob.buffer instanceof ArrayBuffer&&!(blob instanceof Blob)){resolve(blob.buffer);return}var r=new FileReader();r.onload=function(){resolve(r.result)};r.onerror=function(){reject(r.error||new Error('Could not read document'))};r.readAsArrayBuffer(blob)})}
function docKey(){
 if(docCryptoKeyPromise)return docCryptoKeyPromise;
 docCryptoKeyPromise=new Promise(function(resolve,reject){
   try{
     if(!window.crypto||!crypto.subtle||!window.Android||!Android.secureGet||!Android.secureSet){reject(new Error('Secure document encryption is unavailable'));return}
     var sk=(window.attendanceUserPrefix||'attendance_guest__')+'document_file_key_v1',b64=Android.secureGet(sk),raw;
     if(!b64){raw=new Uint8Array(32);crypto.getRandomValues(raw);b64=docBytesB64(raw);if(!Android.secureSet(sk,b64)){reject(new Error('Could not protect document key'));return}}
     raw=docB64Bytes(b64);
     crypto.subtle.importKey('raw',raw,{name:'AES-GCM'},false,['encrypt','decrypt']).then(resolve,reject)
   }catch(e){reject(e)}
 });
 return docCryptoKeyPromise
}
function docEncryptBuffer(buf,aad){
 return docKey().then(function(key){var iv=new Uint8Array(12);crypto.getRandomValues(iv);return crypto.subtle.encrypt({name:'AES-GCM',iv:iv,additionalData:docUtf8(aad)},key,buf).then(function(cipher){return{iv:docBytesB64(iv),data:cipher}})})
}
function docDecryptBuffer(iv,cipher,aad){
 return docKey().then(function(key){return crypto.subtle.decrypt({name:'AES-GCM',iv:docB64Bytes(iv),additionalData:docUtf8(aad)},key,cipher)})
}
function docEncryptItem(item){
 var meta={type:item.type||'',name:item.name||'',issue:item.issue||'',expiry:item.expiry||'',notes:item.notes||'',fileName:item.fileName||'',mime:item.mime||'application/octet-stream',size:+item.size||0,createdAt:+item.createdAt||Date.now()};
 return docReadBuffer(item.blob).then(function(fileBuf){
   return Promise.all([
     docEncryptBuffer(docUtf8(JSON.stringify(meta)).buffer,'doc-meta:'+item.id),
     docEncryptBuffer(fileBuf,'doc-file:'+item.id)
   ]).then(function(parts){return{id:item.id,createdAt:meta.createdAt,secureVersion:1,metaIv:parts[0].iv,metaCipher:parts[0].data,blobIv:parts[1].iv,blobCipher:parts[1].data}})
 })
}
function docDecryptItem(item){
 if(!item||item.secureVersion!==1)return Promise.resolve(item);
 return Promise.all([
   docDecryptBuffer(item.metaIv,item.metaCipher,'doc-meta:'+item.id),
   docDecryptBuffer(item.blobIv,item.blobCipher,'doc-file:'+item.id)
 ]).then(function(parts){
   var meta=JSON.parse(docUtf8Text(parts[0])),out={id:item.id,type:meta.type||'',name:meta.name||'',issue:meta.issue||'',expiry:meta.expiry||'',notes:meta.notes||'',fileName:meta.fileName||'',mime:meta.mime||'application/octet-stream',size:+meta.size||0,createdAt:+meta.createdAt||item.createdAt||0};
   out.blob=new Blob([parts[1]],{type:out.mime});
   return out
 })
}
function docPutEncrypted(db,item){
 return new Promise(function(resolve,reject){var tx=db.transaction([DOC_STORE],'readwrite');tx.objectStore(DOC_STORE).put(item);tx.oncomplete=function(){resolve()};tx.onerror=function(){reject(tx.error||new Error('Could not encrypt stored document'))};tx.onabort=function(){reject(tx.error||new Error('Could not encrypt stored document'))}})
}
function docEnsureMigrated(db){
 if(docMigrationPromise)return docMigrationPromise;
 docMigrationPromise=new Promise(function(resolve,reject){
   var r=db.transaction([DOC_STORE],'readonly').objectStore(DOC_STORE).getAll();
   r.onerror=function(){reject(r.error||new Error('Could not inspect documents'))};
   r.onsuccess=function(){
     var list=r.result||[],i,chain=Promise.resolve();
     for(i=0;i<list.length;i++)(function(item){if(item&&item.secureVersion===1)return;chain=chain.then(function(){return docEncryptItem(item).then(function(enc){return docPutEncrypted(db,enc)})})})(list[i]);
     chain.then(resolve,reject)
   }
 });
 return docMigrationPromise
}
'''

db_old="function dbOpen(cb){var r=indexedDB.open(DOC_DB,1);r.onupgradeneeded=function(e){var db=e.target.result;if(!db.objectStoreNames.contains(DOC_STORE))db.createObjectStore(DOC_STORE,{keyPath:'id'})};r.onsuccess=function(e){cb(e.target.result)};r.onerror=function(){toast('Could not open document storage')}}"
db_new=crypto_helpers+"\nfunction dbOpen(cb){var r=indexedDB.open(DOC_DB,1);r.onupgradeneeded=function(e){var db=e.target.result;if(!db.objectStoreNames.contains(DOC_STORE))db.createObjectStore(DOC_STORE,{keyPath:'id'})};r.onsuccess=function(e){var db=e.target.result;docEnsureMigrated(db).then(function(){cb(db)}).catch(function(){try{db.close()}catch(x){}toast('Could not unlock encrypted document storage')})};r.onerror=function(){toast('Could not open document storage')}}"
if db_old not in s: raise SystemExit('dbOpen anchor missing')
s=s.replace(db_old,db_new,1)

save_old="function saveDocument(){var f=E('docFile').files[0],name=E('docName').value.trim();if(!f){toast('Please select a document');return}if(!name){toast('Please enter document name');return}var item={id:idNew(),type:E('docType').value,name:name,issue:E('docIssue').value,expiry:E('docExpiry').value,notes:E('docNotes').value.trim(),fileName:f.name,mime:f.type||'application/octet-stream',size:f.size,createdAt:Date.now(),blob:f};dbOpen(function(db){var tx=db.transaction([DOC_STORE],'readwrite');tx.objectStore(DOC_STORE).put(item);tx.oncomplete=function(){E('docName').value='';E('docIssue').value='';E('docExpiry').value='';E('docNotes').value='';E('docFile').value='';E('docFileLabel').textContent='Select document';toast('Document saved');renderDocuments()}})}"
save_new="function saveDocument(){var f=E('docFile').files[0],name=E('docName').value.trim();if(!f){toast('Please select a document');return}if(!name){toast('Please enter document name');return}var item={id:idNew(),type:E('docType').value,name:name,issue:E('docIssue').value,expiry:E('docExpiry').value,notes:E('docNotes').value.trim(),fileName:f.name,mime:f.type||'application/octet-stream',size:f.size,createdAt:Date.now(),blob:f};toast('Encrypting document…');docEncryptItem(item).then(function(enc){dbOpen(function(db){var tx=db.transaction([DOC_STORE],'readwrite');tx.objectStore(DOC_STORE).put(enc);tx.oncomplete=function(){E('docName').value='';E('docIssue').value='';E('docExpiry').value='';E('docNotes').value='';E('docFile').value='';E('docFileLabel').textContent='Select document';toast('Document encrypted and saved');renderDocuments()};tx.onerror=function(){toast('Could not save encrypted document')}})}).catch(function(){toast('Document encryption failed')})}"
if save_old not in s: raise SystemExit('saveDocument anchor missing')
s=s.replace(save_old,save_new,1)

get_old="function getDoc(id,cb){dbOpen(function(db){var r=db.transaction([DOC_STORE],'readonly').objectStore(DOC_STORE).get(id);r.onsuccess=function(){cb(r.result)}})}"
get_new="function getDoc(id,cb){dbOpen(function(db){var r=db.transaction([DOC_STORE],'readonly').objectStore(DOC_STORE).get(id);r.onsuccess=function(){if(!r.result){cb(null);return}docDecryptItem(r.result).then(cb).catch(function(){toast('Could not decrypt document');cb(null)})};r.onerror=function(){toast('Could not read document');cb(null)}})}"
if get_old not in s: raise SystemExit('getDoc anchor missing')
s=s.replace(get_old,get_new,1)

render_old=re.search(r"function renderDocuments\(\)\{dbOpen\(function\(db\)\{var r=db\.transaction\(\[DOC_STORE\],'readonly'\)\.objectStore\(DOC_STORE\)\.getAll\(\);r\.onsuccess=function\(\)\{.*?\}\}\)\}",s,re.S)
if not render_old: raise SystemExit('renderDocuments anchor missing')
render_new="""function renderDocuments(){dbOpen(function(db){var r=db.transaction([DOC_STORE],'readonly').objectStore(DOC_STORE).getAll();r.onsuccess=function(){var raw=r.result||[];Promise.all(raw.map(function(x){return docDecryptItem(x)})).then(function(list){var out='',i,d;list.sort(function(a,b){return b.createdAt-a.createdAt});for(i=0;i<list.length;i++){d=list[i];out+='<div class="docCard"><div class="docTop"><span class="docAnim lottieIcon dynamicLottie" data-lottie="documents.json"></span><div class="docInfo"><b>'+esc(d.name)+'</b><small>'+esc(d.type)+' • '+esc(d.fileName)+'</small></div></div><div class="docMeta">'+(d.issue?'Issued: '+d.issue:'')+(d.expiry?' • Expires: '+d.expiry:'')+(d.notes?' • '+esc(d.notes):'')+'</div><div class="docActions"><button class="btn ghost docShare" data-id="'+d.id+'">Share</button><button class="btn ghost docExport" data-id="'+d.id+'">Export</button><button class="btn dangerBtn docDelete" data-id="'+d.id+'">Delete</button></div></div>'}E('documentList').innerHTML=out||'<div class="empty">No job documents saved yet.</div>';initLottie(E('documentList'))}).catch(function(){E('documentList').innerHTML='<div class="empty">Could not decrypt saved documents.</div>';toast('Could not decrypt saved documents')})};r.onerror=function(){toast('Could not read document list')}})}"""
s=s[:render_old.start()]+render_new+s[render_old.end():]

p.write_text(s,encoding='utf-8')
print('v12.4 encrypted IndexedDB document patch applied')
