from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/java/com/personal/attendance/MainActivity.java')
s=p.read_text()

needle='  private void cloudRestore(){\n'
insert='''  private void deleteAccountData(){\n    FirebaseUser u=auth==null?null:auth.getCurrentUser();\n    if(u==null){js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,\'Please sign in again.\');");return;}\n    StorageReference ref=cloudStorage==null?null:cloudStorage.getReference().child("users").child(u.getUid()).child("backups").child("latest.json");\n    Runnable deleteUser=()->u.delete().addOnCompleteListener(this,t->{\n      if(t.isSuccessful()){js("window.onProfileDeleteResult&&window.onProfileDeleteResult(true,\'Profile deleted\');");}\n      else{String m=t.getException()==null?"Could not delete account":t.getException().getMessage();js("window.onProfileDeleteResult&&window.onProfileDeleteResult(false,"+JSONObject.quote(m)+");");}\n    });\n    if(ref==null){deleteUser.run();return;}\n    ref.delete().addOnCompleteListener(this,t->deleteUser.run());\n  }\n\n'''
if needle not in s: raise SystemExit('cloudRestore anchor missing')
s=s.replace(needle,insert+needle,1)
bridge='    @JavascriptInterface public void cloudRestore(){MainActivity.this.cloudRestore();}\n'
repl=bridge+'    @JavascriptInterface public void deleteAccountData(){runOnUiThread(() -> MainActivity.this.deleteAccountData());}\n'
if bridge not in s: raise SystemExit('bridge anchor missing')
s=s.replace(bridge,repl,1)

old='''        try{\n          String[] accepts=p.getAcceptTypes();\n          ArrayList<String> types=new ArrayList<>();\n          if(accepts!=null){\n            for(String a:accepts){\n              if(a==null)continue;\n              for(String t:a.split(",")){\n                t=t.trim();\n                if(t.contains("/"))types.add(t);\n              }\n            }\n          }\n          if(!types.isEmpty())i.putExtra(Intent.EXTRA_MIME_TYPES,types.toArray(new String[0]));\n        }catch(Exception ignored){}'''
new='''        try{\n          String[] accepts=p.getAcceptTypes();\n          ArrayList<String> types=new ArrayList<>();\n          boolean csvRequest=false;\n          if(accepts!=null){\n            for(String a:accepts){\n              if(a==null)continue;\n              for(String t:a.split(",")){\n                t=t.trim();\n                String lower=t.toLowerCase();\n                if(lower.contains("csv")||lower.equals(".csv"))csvRequest=true;\n                if(t.contains("/"))types.add(t);\n              }\n            }\n          }\n          // CSV providers report several inconsistent MIME types. For CSV imports,\n          // keep */* so files exported by this app remain selectable everywhere.\n          if(!csvRequest&&!types.isEmpty())i.putExtra(Intent.EXTRA_MIME_TYPES,types.toArray(new String[0]));\n        }catch(Exception ignored){}'''
if old not in s: raise SystemExit('file chooser block missing')
s=s.replace(old,new,1)
p.write_text(s)
