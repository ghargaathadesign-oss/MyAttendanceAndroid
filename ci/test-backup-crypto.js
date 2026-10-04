'use strict';
if(typeof globalThis.btoa!=='function')globalThis.btoa=s=>Buffer.from(s,'binary').toString('base64');
if(typeof globalThis.atob!=='function')globalThis.atob=s=>Buffer.from(s,'base64').toString('binary');
const assert=require('assert');
const b=require('./backup-crypto.js');
(async()=>{
 const plain=JSON.stringify({version:3,userUid:'uid-1',storage:{attendance_v8:'[]'}});
 const enc=await b.encrypt(plain,'correct horse battery','uid-1');
 const env=JSON.parse(enc);
 assert.strictEqual(env.version,4);assert.strictEqual(env.cipher,'AES-256-GCM');assert.strictEqual(env.kdf,'PBKDF2-HMAC-SHA256');
 assert.strictEqual(await b.decrypt(enc,'correct horse battery','uid-1'),plain);
 let wrong=false;try{await b.decrypt(enc,'wrong password','uid-1')}catch(e){wrong=true}assert(wrong);
 let other=false;try{await b.decrypt(enc,'correct horse battery','uid-2')}catch(e){other=true}assert(other);
 console.log('backup crypto tests passed');
})().catch(e=>{console.error(e);process.exit(1)});