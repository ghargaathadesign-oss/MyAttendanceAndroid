from pathlib import Path
import re, sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/java/com/personal/attendance/MainActivity.java')
s=p.read_text(encoding='utf-8')

anchor='''  private void secureCloudBackup(String json){
'''
methods='''  private JSONObject compositeBackupBase(String existing,String uid) throws Exception{
    JSONObject out=new JSONObject();
    out.put("version",7);
    out.put("combined",true);
    out.put("userUid",uid);
    out.put("savedAt",System.currentTimeMillis());
    if(existing==null||existing.trim().isEmpty())return out;
    try{
      JSONObject old=new JSONObject(existing);
      int v=old.optInt("version",0);
      if(v==7&&old.optBoolean("combined")){
        if(old.has("device"))out.put("device",old.get("device"));
        if(old.has("transfer"))out.put("transfer",old.get("transfer"));
        if(old.has("legacy"))out.put("legacy",old.get("legacy"));
      }else if(v==6&&old.optBoolean("portable")){
        out.put("transfer",old);
      }else if(v==5&&old.optBoolean("encrypted")){
        out.put("device",old);
      }else{
        out.put("legacy",old);
      }
    }catch(Exception ignored){}
    return out;
  }

  private void uploadComposite(JSONObject out,boolean transferResult){
    StorageReference ref=backupRef();
    if(ref==null){
      if(transferResult)js("window.onCloudTransferBackupResult&&window.onCloudTransferBackupResult(false,'Please sign in with a verified account first',0);");
      else js("window.onCloudBackupResult&&window.onCloudBackupResult(false,'Please sign in with a verified account first',0);");
      return;
    }
    byte[] bytes=out.toString().getBytes(StandardCharsets.UTF_8);
    StorageMetadata meta=new StorageMetadata.Builder().setContentType("application/json").setCustomMetadata("source","My Attendance Android").build();
    ref.putBytes(bytes,meta).addOnSuccessListener(x->{
      long now=System.currentTimeMillis();
      if(transferResult)js("window.onCloudTransferBackupResult&&window.onCloudTransferBackupResult(true,'Switch-device backup saved',"+now+");");
      else js("window.onCloudBackupResult&&window.onCloudBackupResult(true,'Backup saved',"+now+");");
    }).addOnFailureListener(e->{
      String msg=e.getMessage()==null?"Backup failed":e.getMessage();
      if(transferResult)js("window.onCloudTransferBackupResult&&window.onCloudTransferBackupResult(false,"+JSONObject.quote(msg)+",0);");
      else js("window.onCloudBackupResult&&window.onCloudBackupResult(false,"+JSONObject.quote(msg)+",0);");
    });
  }

  private void saveCompositeBackup(String devicePayload,String transferPayload,boolean transferResult){
    FirebaseUser u=auth==null?null:auth.getCurrentUser();
    StorageReference ref=backupRef();
    if(u==null||!u.isEmailVerified()||ref==null){
      if(transferResult)js("window.onCloudTransferBackupResult&&window.onCloudTransferBackupResult(false,'Please sign in with a verified account first',0);");
      else js("window.onCloudBackupResult&&window.onCloudBackupResult(false,'Please sign in with a verified account first',0);");
      return;
    }
    java.util.function.Consumer<String> merge=existing->{
      try{
        JSONObject out=compositeBackupBase(existing,u.getUid());
        if(devicePayload!=null)out.put("device",new JSONObject(devicePayload));
        if(transferPayload!=null)out.put("transfer",new JSONObject(transferPayload));
        uploadComposite(out,transferResult);
      }catch(Exception e){
        String msg=e.getMessage()==null?"Could not prepare backup":e.getMessage();
        if(transferResult)js("window.onCloudTransferBackupResult&&window.onCloudTransferBackupResult(false,"+JSONObject.quote(msg)+",0);");
        else js("window.onCloudBackupResult&&window.onCloudBackupResult(false,"+JSONObject.quote(msg)+",0);");
      }
    };
    ref.getBytes(25L*1024L*1024L).addOnSuccessListener(bytes->merge.accept(new String(bytes,StandardCharsets.UTF_8))).addOnFailureListener(e->{
      if(e instanceof StorageException&&((StorageException)e).getErrorCode()==StorageException.ERROR_OBJECT_NOT_FOUND)merge.accept(null);
      else{
        String msg=e.getMessage()==null?"Could not read existing backup":e.getMessage();
        if(transferResult)js("window.onCloudTransferBackupResult&&window.onCloudTransferBackupResult(false,"+JSONObject.quote(msg)+",0);");
        else js("window.onCloudBackupResult&&window.onCloudBackupResult(false,"+JSONObject.quote(msg)+",0);");
      }
    });
  }

  private void cloudTransferBackup(String payload){
    try{
      JSONObject o=new JSONObject(payload==null?"{}":payload);
      if(o.optInt("version")!=6||!o.optBoolean("portable"))throw new IllegalArgumentException("Invalid switch-device backup");
      saveCompositeBackup(null,o.toString(),true);
    }catch(Exception e){
      js("window.onCloudTransferBackupResult&&window.onCloudTransferBackupResult(false,"+JSONObject.quote(e.getMessage()==null?"Could not create switch-device backup":e.getMessage())+",0);");
    }
  }

  private void cloudTransferRestore(){
    StorageReference ref=backupRef();
    if(ref==null){js("window.onCloudRestoreError&&window.onCloudRestoreError('Please sign in with a verified account first');");return;}
    ref.getBytes(25L*1024L*1024L).addOnSuccessListener(bytes->{
      String payload=new String(bytes,StandardCharsets.UTF_8);
      try{
        JSONObject o=new JSONObject(payload);
        if(o.optInt("version")==7&&o.optBoolean("combined")&&o.has("transfer")){
          js("window.onCloudTransferRestore&&window.onCloudTransferRestore("+JSONObject.quote(String.valueOf(o.get("transfer")))+");");
        }else if(o.optInt("version")==6&&o.optBoolean("portable")){
          js("window.onCloudTransferRestore&&window.onCloudTransferRestore("+JSONObject.quote(payload)+");");
        }else{
          js("window.onCloudRestoreError&&window.onCloudRestoreError('No switch-device backup found. Create Backup for New Device first.');");
        }
      }catch(Exception e){
        js("window.onCloudRestoreError&&window.onCloudRestoreError('Switch-device backup is invalid.');");
      }
    }).addOnFailureListener(e->js("window.onCloudRestoreError&&window.onCloudRestoreError("+JSONObject.quote(e.getMessage()==null?"No backup found":e.getMessage())+");"));
  }

'''
if 'private void cloudTransferBackup(' not in s:
    if anchor not in s: raise SystemExit('secureCloudBackup anchor missing')
    s=s.replace(anchor,methods+anchor,1)

old='''          String encrypted=encryptDeviceBackup(u.getUid(),json);
          cloudBackup(encrypted);'''
new='''          String encrypted=encryptDeviceBackup(u.getUid(),json);
          saveCompositeBackup(encrypted,null,false);'''
if old not in s: raise SystemExit('device backup save anchor missing')
s=s.replace(old,new,1)

pat=re.compile(r'''  private void cloudRestoreAfterDeviceAuth\(String uid\)\{.*?\n  \}\n''',re.S)
m=pat.search(s)
if not m: raise SystemExit('device restore method missing')
replacement='''  private void cloudRestoreAfterDeviceAuth(String uid){
    StorageReference ref=backupRef();
    if(ref==null){js("window.onCloudRestoreError&&window.onCloudRestoreError('Please sign in with a verified account first');");return;}
    ref.getBytes(25L*1024L*1024L).addOnSuccessListener(bytes->{
      String payload=new String(bytes,StandardCharsets.UTF_8);
      try{
        JSONObject o=new JSONObject(payload);
        if(o.optInt("version")==7&&o.optBoolean("combined")){
          if(o.has("device")){
            String device=String.valueOf(o.get("device"));
            String plain=decryptDeviceBackup(uid,device);
            js("window.onDeviceCloudRestore&&window.onDeviceCloudRestore("+JSONObject.quote(plain)+");");
          }else if(o.has("legacy")){
            js("window.onCloudRestore&&window.onCloudRestore("+JSONObject.quote(String.valueOf(o.get("legacy")))+");");
          }else if(o.has("transfer")){
            js("window.onCloudRestoreError&&window.onCloudRestoreError('This backup is for switching devices. Use Restore on New Device and enter the Transfer PIN.');");
          }else{
            js("window.onCloudRestoreError&&window.onCloudRestoreError('No backup data found.');");
          }
        }else if(o.optBoolean("encrypted")&&o.optInt("version")==5){
          String plain=decryptDeviceBackup(uid,payload);
          js("window.onDeviceCloudRestore&&window.onDeviceCloudRestore("+JSONObject.quote(plain)+");");
        }else{
          js("window.onCloudRestore&&window.onCloudRestore("+JSONObject.quote(payload)+");");
        }
      }catch(Exception e){
        js("window.onCloudRestoreError&&window.onCloudRestoreError("+JSONObject.quote(e.getMessage()==null?"Could not unlock backup on this device":e.getMessage())+");");
      }
    }).addOnFailureListener(e->js("window.onCloudRestoreError&&window.onCloudRestoreError("+JSONObject.quote(e.getMessage()==null?"No backup found":e.getMessage())+");"));
  }
'''
s=s[:m.start()]+replacement+s[m.end():]

bridge='''    @JavascriptInterface public void secureCloudRestore(){MainActivity.this.secureCloudRestore();}
'''
add='''    @JavascriptInterface public void cloudTransferBackup(String json){MainActivity.this.cloudTransferBackup(json);}
    @JavascriptInterface public void cloudTransferRestore(){MainActivity.this.cloudTransferRestore();}
'''
if add.strip() not in s:
    if bridge not in s: raise SystemExit('secure cloud bridge anchor missing')
    s=s.replace(bridge,bridge+add,1)

p.write_text(s,encoding='utf-8')
print('v12.8 composite device + transfer backup patch applied')
