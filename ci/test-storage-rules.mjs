import fs from 'node:fs';
import {initializeTestEnvironment,assertSucceeds,assertFails} from '@firebase/rules-unit-testing';
import {ref,uploadString,getBytes,deleteObject} from 'firebase/storage';

const projectId='demo-my-attendance';
const env=await initializeTestEnvironment({projectId,storage:{rules:fs.readFileSync('storage.rules','utf8')}});
try{
  const alice=env.authenticatedContext('alice',{email:'alice@example.com',email_verified:true});
  const bob=env.authenticatedContext('bob',{email:'bob@example.com',email_verified:true});
  const unverified=env.authenticatedContext('alice',{email:'alice@example.com',email_verified:false});
  const anon=env.unauthenticatedContext();
  const good=ref(alice.storage(),'users/alice/backups/latest.json');
  await assertSucceeds(uploadString(good,'{"version":4}','raw',{contentType:'application/json'}));
  await assertSucceeds(getBytes(good));
  await assertFails(getBytes(ref(bob.storage(),'users/alice/backups/latest.json')));
  await assertFails(getBytes(ref(anon.storage(),'users/alice/backups/latest.json')));
  await assertFails(uploadString(ref(unverified.storage(),'users/alice/backups/latest.json'),'{}','raw',{contentType:'application/json'}));
  await assertFails(uploadString(ref(alice.storage(),'users/bob/backups/latest.json'),'{}','raw',{contentType:'application/json'}));
  await assertFails(uploadString(ref(alice.storage(),'users/alice/backups/latest.json'),'not-json','raw',{contentType:'text/plain'}));
  await assertFails(uploadString(ref(alice.storage(),'public/test.json'),'{}','raw',{contentType:'application/json'}));
  await assertSucceeds(deleteObject(good));
  console.log('storage rules tests passed');
} finally {
  await env.cleanup();
}