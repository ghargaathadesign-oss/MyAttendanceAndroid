import fs from 'node:fs';
import {initializeTestEnvironment,assertSucceeds,assertFails} from '@firebase/rules-unit-testing';
import {ref,uploadString,getBytes,deleteObject,listAll} from 'firebase/storage';

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
  const owner=env.authenticatedContext('support-owner',{email:'pratik.kumar.kashyap@gmail.com',email_verified:true});
  const fakeOwner=env.authenticatedContext('fake-owner',{email:'pratik.kumar.kashyap@gmail.com',email_verified:false});
  const message='support/alice/messages/alice/001.json',options={contentType:'application/json',customMetadata:{senderUid:'alice',support:'false'}};
  await assertSucceeds(uploadString(ref(alice.storage(),message),'{"text":"Help"}','raw',options));
  await assertSucceeds(getBytes(ref(owner.storage(),message)));
  await assertSucceeds(listAll(ref(owner.storage(),'support')));
  await assertSucceeds(listAll(ref(alice.storage(),'support/alice/messages')));
  await assertFails(listAll(ref(bob.storage(),'support')));
  await assertFails(getBytes(ref(bob.storage(),message)));
  await assertFails(getBytes(ref(fakeOwner.storage(),message)));
  await assertFails(uploadString(ref(alice.storage(),message),'{}','raw',options));
  await assertFails(uploadString(ref(bob.storage(),'support/alice/messages/bob/002.json'),'{}','raw',{contentType:'application/json',customMetadata:{senderUid:'bob',support:'false'}}));
  await assertFails(uploadString(ref(alice.storage(),'support/alice/messages/alice/003.json'),'{}','raw',{contentType:'application/json',customMetadata:{senderUid:'alice',support:'true'}}));
  await assertSucceeds(uploadString(ref(owner.storage(),'support/alice/messages/support-owner/004.json'),'{"text":"Reply"}','raw',{contentType:'application/json',customMetadata:{senderUid:'support-owner',support:'true'}}));
  await assertFails(getBytes(ref(owner.storage(),'users/alice/backups/latest.json')));
  await assertSucceeds(deleteObject(ref(alice.storage(),message)));
  console.log('storage rules tests passed');
} finally {
  await env.cleanup();
}