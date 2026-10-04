from pathlib import Path
import re,sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/java/com/personal/attendance/MainActivity.java')
s=p.read_text(encoding='utf-8')

if 'private boolean deletionInProgress=false;' not in s:
    s=s.replace('  private boolean pendingDeleteGoogle=false;\n','  private boolean pendingDeleteGoogle=false;\n  private boolean deletionInProgress=false;\n',1)

pat=re.compile(r'''  private void finishDeleteAccount\(FirebaseUser u\)\{.*?\n  \}\n\n  private void deleteAccountWithPassword''',re.S)
m=pat.search(s)
if not m: raise SystemExit('finishDeleteAccount anchor missing')
replacement='''  private void deleteProgress(String msg){
    js("window.onProfileDeleteProgress&&window.onProfileDeleteProgress("+JSONObject.quote(msg==null?"":msg)+");");
  }

  private void deleteFileTree(File f){
    try{
      if(f==null||!f.exists())return;
      if(f.isDirectory()){
        File[] children=f.listFiles();
        if(children!=null)for(File child:children)deleteFileTree(child);
      }
      f.delete();
    }catch(Exception ignored){}
  }

  private void deleteUserCryptoArtifacts(String uid){
    String safe=String.valueOf(uid==null?"":uid).replaceAll("[^A-Za-z0-9_-]","_");
    try{secureStoreClearPrefix("attendance_user_"+safe+"__");}catch(Exception ignored){}
    try{
      KeyStore keyStore=KeyStore.getInstance("AndroidKeyStore");
      keyStore.load(null);
      String alias=backupKeyAlias(uid);
      if(keyStore.containsAlias(alias))keyStore.deleteEntry(alias);
    }catch(Exception ignored){}
    try{deleteFileTree(new File(getCacheDir(),"shared_documents"));}catch(Exception ignored){}
    try{if(webView!=null)runOnUiThread(()->webView.clearCache(true));}catch(Exception ignored){}
  }

  private void finishDeleteAccount(FirebaseUser u){
    if(u==null){js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,'Please sign in again. No data was deleted.');");return;}
    if(deletionInProgress){js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,'Profile deletion is already in progress.');");return;}
    if(cloudStorage==null){js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,'Cloud storage is unavailable. No data was deleted.');");return;}
    deletionInProgress=true;
    final String uid=u.getUid();
    deleteProgress("Removing cloud backup…");
    StorageReference ref=cloudStorage.getReference().child("users").child(uid).child("backups").child("latest.json");
    Runnable deleteUser=()->{
      deleteProgress("Deleting Firebase account…");
      u.delete().addOnCompleteListener(this,t->{
        if(t.isSuccessful()){
          deleteProgress("Removing encrypted local data…");
          deleteUserCryptoArtifacts(uid);
          try{if(auth!=null)auth.signOut();}catch(Exception ignored){}
          deletionInProgress=false;
          js("window.onProfileDeleteResult&&window.onProfileDeleteResult(true,'Profile deleted securely');");
        }else{
          deletionInProgress=false;
          String msg=t.getException()==null?"Could not delete Firebase account":t.getException().getMessage();
          js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,"+JSONObject.quote(msg+". Your local data was kept. The cloud backup may already have been removed; re-authenticate and retry.")+");");
        }
      });
    };
    ref.delete().addOnSuccessListener(x->deleteUser.run()).addOnFailureListener(e->{
      if(e instanceof StorageException&&((StorageException)e).getErrorCode()==StorageException.ERROR_OBJECT_NOT_FOUND){
        deleteUser.run();
      }else{
        deletionInProgress=false;
        String msg=e.getMessage()==null?"Could not remove cloud backup":e.getMessage();
        js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,"+JSONObject.quote(msg+". Nothing local was erased and the Firebase account was not deleted.")+");");
      }
    });
  }

  private void deleteAccountWithPassword'''
s=s[:m.start()]+replacement+s[m.end():]

old='''    AuthCredential credential=EmailAuthProvider.getCredential(u.getEmail(),password==null?"":password);
    u.reauthenticate(credential).addOnCompleteListener(this,t->{
      if(t.isSuccessful())finishDeleteAccount(u);
      else{String msg=t.getException()==null?"Password verification failed":t.getException().getMessage();js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,"+JSONObject.quote(msg)+");");}
    });'''
new='''    deleteProgress("Verifying your Firebase account…");
    AuthCredential credential=EmailAuthProvider.getCredential(u.getEmail(),password==null?"":password);
    u.reauthenticate(credential).addOnCompleteListener(this,t->{
      if(t.isSuccessful())finishDeleteAccount(u);
      else{
        String msg=t.getException()==null?"Password verification failed":t.getException().getMessage();
        js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,"+JSONObject.quote(msg+". No data was deleted.")+");");
      }
    });'''
if old not in s: raise SystemExit('password reauth anchor missing')
s=s.replace(old,new,1)

old='''          @Override public void onError(GetCredentialException e){jsError(e.getMessage()==null?"Google sign-in cancelled":e.getMessage());}'''
new='''          @Override public void onError(GetCredentialException e){
            String msg=e.getMessage()==null?"Google verification cancelled":e.getMessage();
            if(pendingDeleteGoogle){
              pendingDeleteGoogle=false;
              js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,"+JSONObject.quote(msg+". No data was deleted.")+");");
            }else jsError(msg);
          }'''
if old not in s: raise SystemExit('Google credential onError anchor missing')
s=s.replace(old,new,1)

old='''    }catch(Exception e){jsError(e.getMessage());}
  }

  private void handleCredential'''
new='''    }catch(Exception e){
      if(pendingDeleteGoogle){
        pendingDeleteGoogle=false;
        js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,"+JSONObject.quote((e.getMessage()==null?"Google verification failed":e.getMessage())+". No data was deleted.")+");");
      }else jsError(e.getMessage());
    }
  }

  private void handleCredential'''
if old not in s: raise SystemExit('beginGoogleSignIn catch anchor missing')
s=s.replace(old,new,1)

old='''      if(!(result.getCredential() instanceof CustomCredential)){jsError("Google credential was not returned.");return;}'''
new='''      if(!(result.getCredential() instanceof CustomCredential)){
        if(pendingDeleteGoogle){pendingDeleteGoogle=false;js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,'Google credential was not returned. No data was deleted.');");}
        else jsError("Google credential was not returned.");
        return;
      }'''
if old not in s: raise SystemExit('custom credential anchor missing')
s=s.replace(old,new,1)

old='''      if(!GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL.equals(c.getType())){jsError("Unsupported Google credential type.");return;}'''
new='''      if(!GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL.equals(c.getType())){
        if(pendingDeleteGoogle){pendingDeleteGoogle=false;js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,'Unsupported Google credential. No data was deleted.');");}
        else jsError("Unsupported Google credential type.");
        return;
      }'''
if old not in s: raise SystemExit('google credential type anchor missing')
s=s.replace(old,new,1)

# Do not let a generic credential parsing exception leave a pending delete armed.
old='''    }catch(Exception e){jsError(e.getMessage());}
  }

  private void emailSignUp'''
new='''    }catch(Exception e){
      if(pendingDeleteGoogle){
        pendingDeleteGoogle=false;
        js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,"+JSONObject.quote((e.getMessage()==null?"Google verification failed":e.getMessage())+". No data was deleted.")+");");
      }else jsError(e.getMessage());
    }
  }

  private void emailSignUp'''
if old not in s: raise SystemExit('handleCredential catch anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('v12.9 native secure deletion patch applied')
