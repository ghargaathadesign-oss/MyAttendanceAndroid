'use strict';
const assert=require('assert');
const d=require('./diagnostics-core.js');
const p=require('./policy-engine.js');
const storage={
 attendance_v8:JSON.stringify([{id:'x',date:'2026-10-05',status:'Present',checkIn:'09:00',checkOut:'18:00',notes:'SUPER_SECRET_NOTE'}]),
 attendance_settings_v8:JSON.stringify({h:9,m:0,otDelay:30}),
 attendance_salary_v9:JSON.stringify({monthly:999999}),
 attendance_profile_v81:JSON.stringify({name:'PRIVATE NAME',email:'secret@example.com'})
};
const local=d.inspectStorage(storage,p);
assert.strictEqual(local.ok,true);
assert.strictEqual(local.recordCount,1);
const report=d.buildSupportReport({
 native:{versionName:'3.5',versionCode:21,sdk:35,androidRelease:'15',signedIn:true,emailVerified:true,authProvider:'password',secureStorage:true,deviceSecure:true,backupKeyPresent:true,webViewFileAccess:false,safeBrowsing:true,appCheckEnabled:false,uid:'SECRET_UID',email:'secret@example.com'},
 local,
 documents:{ok:true,count:2,contents:'PRIVATE_DOCUMENT'},
 cloud:{ok:true,exists:true,version:7,hasDevice:true,hasTransfer:true,hasLegacy:false,bytes:1234,payload:'SECRET_BACKUP'},
 health:{level:'good',issues:[],warnings:[]}
});
for(const secret of ['SUPER_SECRET_NOTE','999999','PRIVATE NAME','secret@example.com','SECRET_UID','PRIVATE_DOCUMENT','SECRET_BACKUP']){
 assert.strictEqual(report.includes(secret),false,'support report leaked '+secret);
}
assert(report.includes('Attendance records: 1'));
assert(report.includes('Same-device backup present: Yes'));
console.log('diagnostics privacy tests passed');