(function(root,factory){
  var api=factory(root);
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.AttendanceBackupCrypto=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
'use strict';
var ITERATIONS=310000;
function c(){var x=root.crypto;if(!x||!x.subtle||!x.getRandomValues)throw new Error('Secure backup encryption is unavailable');return x}
function enc(){return new TextEncoder()}
function dec(){return new TextDecoder('utf-8')}
function b64(bytes){var a=bytes instanceof Uint8Array?bytes:new Uint8Array(bytes),s='',i,chunk=32768;for(i=0;i<a.length;i+=chunk)s+=String.fromCharCode.apply(null,a.subarray(i,Math.min(a.length,i+chunk)));return btoa(s)}
function unb64(v){var s=atob(String(v||'')),a=new Uint8Array(s.length),i;for(i=0;i<s.length;i++)a[i]=s.charCodeAt(i);return a}
function aad(uid){return enc().encode('MyAttendance|cloud-backup|v4|'+String(uid||''))}
function derive(password,salt,iterations){
  password=String(password||'');if(password.length<8)return Promise.reject(new Error('Recovery password must be at least 8 characters.'));
  var wc=c(),it=Math.max(100000,Math.floor(Number(iterations)||ITERATIONS));
  return wc.subtle.importKey('raw',enc().encode(password),'PBKDF2',false,['deriveKey']).then(function(base){
    return wc.subtle.deriveKey({name:'PBKDF2',salt:salt,iterations:it,hash:'SHA-256'},base,{name:'AES-GCM',length:256},false,['encrypt','decrypt']);
  });
}
function encrypt(plain,password,uid){
  var wc=c(),salt=new Uint8Array(16),iv=new Uint8Array(12);wc.getRandomValues(salt);wc.getRandomValues(iv);
  return derive(password,salt,ITERATIONS).then(function(key){
    return wc.subtle.encrypt({name:'AES-GCM',iv:iv,additionalData:aad(uid),tagLength:128},key,enc().encode(String(plain==null?'':plain)));
  }).then(function(buf){
    return JSON.stringify({version:4,encrypted:true,cipher:'AES-256-GCM',kdf:'PBKDF2-HMAC-SHA256',iterations:ITERATIONS,userUid:String(uid||''),savedAt:new Date().toISOString(),salt:b64(salt),iv:b64(iv),ciphertext:b64(new Uint8Array(buf))});
  });
}
function decrypt(payload,password,uid){
  var o=typeof payload==='string'?JSON.parse(payload):payload;if(!o||o.version!==4||o.encrypted!==true||o.cipher!=='AES-256-GCM'||o.kdf!=='PBKDF2-HMAC-SHA256')return Promise.reject(new Error('Encrypted backup format is unsupported'));
  uid=String(uid||'');if(o.userUid&&uid&&String(o.userUid)!==uid)return Promise.reject(new Error('This backup belongs to a different account.'));
  var wc=c(),salt=unb64(o.salt),iv=unb64(o.iv),ct=unb64(o.ciphertext);if(salt.length!==16||iv.length!==12||!ct.length)return Promise.reject(new Error('Encrypted backup is damaged'));
  return derive(password,salt,o.iterations).then(function(key){return wc.subtle.decrypt({name:'AES-GCM',iv:iv,additionalData:aad(uid||o.userUid),tagLength:128},key,ct)}).then(function(buf){return dec().decode(buf)}).catch(function(e){if(e&&/belongs|password|unsupported|damaged/i.test(String(e.message||'')))throw e;throw new Error('Recovery password is incorrect or the backup is damaged.');});
}
function isV4(payload){try{var o=typeof payload==='string'?JSON.parse(payload):payload;return !!(o&&o.version===4&&o.encrypted===true)}catch(e){return false}}
return{VERSION:4,ITERATIONS:ITERATIONS,encrypt:encrypt,decrypt:decrypt,isV4:isV4};
});