from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text();anchor='  public class AndroidBridge{'
method='''  private String authSnapshotNative(){
    org.json.JSONObject state=new org.json.JSONObject();
    try{
      FirebaseUser user=auth==null?null:auth.getCurrentUser();
      state.put("signedIn",user!=null);state.put("emailVerified",user!=null&&user.isEmailVerified());
      state.put("supportOwner",isSupportOwner(user));
      if(user!=null){state.put("uid",user.getUid());state.put("name",user.getDisplayName()==null?"":user.getDisplayName());state.put("email",user.getEmail()==null?"":user.getEmail());state.put("photo",user.getPhotoUrl()==null?"":user.getPhotoUrl().toString());}
      if(auth==null)state.put("setupError",firebaseInitError.isEmpty()?"Firebase initialization failed":firebaseInitError);
    }catch(Exception ignored){}
    return state.toString();
  }

'''
if anchor not in s:raise SystemExit('Snapshot bridge anchor missing')
s=s.replace(anchor,method+anchor+'\n    @JavascriptInterface public String authSnapshot(){return authSnapshotNative();}\n',1);p.write_text(s)
print('v15.5.16 authoritative native session snapshot applied')
