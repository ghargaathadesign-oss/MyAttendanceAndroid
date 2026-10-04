(function(root,factory){
  var api=factory(root);
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.AttendanceTransferCrypto=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
'use strict';
var ITERATIONS=600000;
function wc(){var x=root.crypto;if(!x||!x.subtle||!x.getRandomValues)throw new Error('Secure transfer encryption is unavailable');return x}
function enc(){return new TextEncoder()}
function dec(){return new TextDecoder('utf-8')}
function validPin(pin){return /^\d{6,12}$/.test(String(pin||''))}
function b64(bytes){var a=bytes instanceof Uint8Array?bytes:new Uint8Array(bytes),s='',i,chunk=32768;for(i=0;i<a.length;i+=chunk)s+=String.fromCharCode.apply(null,a.subarray(i,Math.min(a.length,i+chunk)));return btoa(s)}
function unb64(v){var s=atob(String(v||'')),a=new Uint8Array(s.length),i;for(i=0;i<s.length;i++)a[i]=s.charCodeAt(i);return a}
function aad(uid){return enc().encode('MyAttendance|switch-device|v6|'+String(uid||''))}
function derive(pin,salt,iterations){
  pin=String(pin||'');if(!validPin(pin))return Promise.reject(new Error('Transfer PIN must be 6 to 12 digits.'));
  var c=wc(),it=Math.max(300000,Math.floor(Number(iterations)||ITERATIONS));
  return c.subtle.importKey('raw',enc().encode(pin),'PBKDF2',false,['deriveKey']).then(function(base){
    return c.subtle.deriveKey({name:'PBKDF2',salt:salt,iterations:it,hash:'SHA-256'},base,{name:'AES-GCM',length:256},false,['encrypt','decrypt']);
  });
}
function encrypt(plain,pin,uid){
  var c=wc(),salt=new Uint8Array(16),iv=new Uint8Array(12);c.getRandomValues(salt);c.getRandomValues(iv);
  return derive(pin,salt,ITERATIONS).then(function(key){
    return c.subtle.encrypt({name:'AES-GCM',iv:iv,additionalData:aad(uid),tagLength:128},key,enc().encode(String(plain==null?'':plain)));
  }).then(function(buf){
    return JSON.stringify({version:6,portable:true,encrypted:true,cipher:'AES-256-GCM',kdf:'PBKDF2-HMAC-SHA256',iterations:ITERATIONS,userUid:String(uid||''),savedAt:new Date().toISOString(),salt:b64(salt),iv:b64(iv),ciphertext:b64(new Uint8Array(buf))});
  });
}
function decrypt(payload,pin,uid){
  var o=typeof payload==='string'?JSON.parse(payload):payload;
  if(!o||o.version!==6||o.portable!==true||o.encrypted!==true||o.cipher!=='AES-256-GCM'||o.kdf!=='PBKDF2-HMAC-SHA256')return Promise.reject(new Error('Switch-device backup format is unsupported.'));
  uid=String(uid||'');if(o.userUid&&uid&&String(o.userUid)!==uid)return Promise.reject(new Error('This backup belongs to a different account.'));
  var salt=unb64(o.salt),iv=unb64(o.iv),ct=unb64(o.ciphertext),c=wc();
  if(salt.length!==16||iv.length!==12||!ct.length)return Promise.reject(new Error('Switch-device backup is damaged.'));
  return derive(pin,salt,o.iterations).then(function(key){
    return c.subtle.decrypt({name:'AES-GCM',iv:iv,additionalData:aad(uid||o.userUid),tagLength:128},key,ct);
  }).then(function(buf){return dec().decode(buf)}).catch(function(e){
    if(e&&/belongs|digits|unsupported|damaged/i.test(String(e.message||'')))throw e;
    throw new Error('Transfer PIN is incorrect or the backup is damaged.');
  });
}
return{VERSION:6,ITERATIONS:ITERATIONS,validPin:validPin,encrypt:encrypt,decrypt:decrypt};
});