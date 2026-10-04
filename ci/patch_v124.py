from pathlib import Path
import re, sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
app=assets/'app.js'
s=app.read_text(encoding='utf-8')

pat=r"function saveDocument\(\)\{.*?\nfunction getDoc\(id,cb\)\{.*?\nfunction blobBase64"
repl="""function saveDocument(){var f=E('docFile').files[0],name=E('docName').value.trim();if(!f){toast('Please select a document');return}if(!name){toast('Please enter document name');return}var id=idNew(),created=Date.now(),meta={type:E('docType').value,name:name,issue:E('docIssue').value,expiry:E('docExpiry').value,notes:E('docNotes').value.trim(),fileName:f.name,mime:f.type||'application/octet-stream',size:f.size};if(!window.attendanceDocEncryptFile){toast('Encrypted document storage is unavailable');return}toast('Encrypting document…');window.attendanceDocEncryptFile(meta,f,id,created).then(function(item){dbOpen(function(db){var tx=db.transaction([DOC_STORE],'readwrite');tx.objectStore(DOC_STORE).put(item);tx.oncomplete=function(){E('docName').value='';E('docIssue').value='';E('docExpiry').value='';E('docNotes').value='';E('docFile').value='';E('docFileLabel').textContent='Select document';toast('Encrypted document saved');renderDocuments()};tx.onerror=function(){toast('Could not save encrypted document')}})}).catch(function(){toast('Document encryption failed')})}
function getDoc(id,cb){dbOpen(function(db){var r=db.transaction([DOC_STORE],'readonly').objectStore(DOC_STORE).get(id);r.onsuccess=function(){var item=r.result;if(!item){cb(null);return}if(window.attendanceDocDecryptRecord){window.attendanceDocDecryptRecord(item).then(function(d){cb(d)}).catch(function(){toast('Could not decrypt document');cb(null)})}else cb(item)}})}
function blobBase64"""
s2,n=re.subn(pat,repl,s,count=1,flags=re.S)
if n!=1: raise SystemExit('document save/get anchor not found')
s=s2

pat2=r"function renderDocuments\(\)\{.*?\nfunction exportDoc"
repl2="""function renderDocuments(){dbOpen(function(db){var r=db.transaction([DOC_STORE],'readonly').objectStore(DOC_STORE).getAll();r.onsuccess=function(){var list=r.result||[],out='',i,raw,m,d,failed=0;list.sort(function(a,b){return (b.createdAt||0)-(a.createdAt||0)});for(i=0;i<list.length;i++){raw=list[i];m=window.attendanceDocMeta?window.attendanceDocMeta(raw):raw;if(!m){failed++;continue}d={id:raw.id,createdAt:raw.createdAt,type:m.type||'Other',name:m.name||'Document',issue:m.issue||'',expiry:m.expiry||'',notes:m.notes||'',fileName:m.fileName||'document'};out+='<div class="docCard"><div class="docTop"><span class="docAnim lottieIcon dynamicLottie" data-lottie="documents.json"></span><div class="docInfo"><b>'+esc(d.name)+'</b><small>'+esc(d.type)+' • '+esc(d.fileName)+'</small></div></div><div class="docMeta">'+(d.issue?'Issued: '+d.issue:'')+(d.expiry?' • Expires: '+d.expiry:'')+(d.notes?' • '+esc(d.notes):'')+'</div><div class="docActions"><button class="btn ghost docShare" data-id="'+d.id+'">Share</button><button class="btn ghost docExport" data-id="'+d.id+'">Export</button><button class="btn dangerBtn docDelete" data-id="'+d.id+'">Delete</button></div></div>'}if(failed)out+='<div class="empty">'+failed+' encrypted document'+(failed===1?'':'s')+' could not be opened on this device.</div>';E('documentList').innerHTML=out||'<div class="empty">No job documents saved yet.</div>';initLottie(E('documentList'))}})}
function exportDoc"""
s2,n=re.subn(pat2,repl2,s,count=1,flags=re.S)
if n!=1: raise SystemExit('renderDocuments anchor not found')
s=s2

old="function startUserScopedApp(){var go=function(){init()};if(window.attendanceStorageReady&&typeof window.attendanceStorageReady.then==='function')window.attendanceStorageReady.then(go).catch(go);else go()}"
new="function startUserScopedApp(){var go=function(){init()},ready=window.attendanceDocumentsReady||window.attendanceStorageReady;if(ready&&typeof ready.then==='function')ready.then(go).catch(go);else go()}"
if old not in s: raise SystemExit('startup readiness anchor not found')
s=s.replace(old,new,1)

app.write_text(s,encoding='utf-8')

index=assets/'index.html'
html=index.read_text(encoding='utf-8')
needle='<script src="user-storage.js"></script>\n<script src="app.js"></script>'
if needle not in html: raise SystemExit('user-storage/app script anchor missing')
html=html.replace(needle,'<script src="user-storage.js"></script>\n<script src="document-crypto.js"></script>\n<script src="app.js"></script>',1)
index.write_text(html,encoding='utf-8')
print('v12.4 encrypted document patch applied')
