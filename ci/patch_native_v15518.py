from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text();anchor='  public class AndroidBridge{'
if anchor not in s:raise SystemExit('Missing AndroidBridge')
s=s.replace(anchor,anchor+'''
    @JavascriptInterface public void inviteEmployee(String email){runOnUiThread(()->{
      String to=email==null?"":email.trim();
      if(!android.util.Patterns.EMAIL_ADDRESS.matcher(to).matches()){toast("Enter a valid employee email address");return;}
      String subject="You’re invited to My Attendance";
      String body="Hi,\\n\\nYou’re invited to use My Attendance to track your attendance, leave and salary.\\n\\nDownload the app:\\nhttps://github.com/ghargaathadesign-oss/MyAttendanceAndroid/releases/latest\\n\\nOpen the link and install the signed APK, then sign in with your own account.";
      android.content.Intent mail=new android.content.Intent(android.content.Intent.ACTION_SENDTO,android.net.Uri.parse("mailto:"+android.net.Uri.encode(to)+"?subject="+android.net.Uri.encode(subject)+"&body="+android.net.Uri.encode(body)));
      mail.putExtra(android.content.Intent.EXTRA_EMAIL,new String[]{to});mail.putExtra(android.content.Intent.EXTRA_SUBJECT,subject);mail.putExtra(android.content.Intent.EXTRA_TEXT,body);
      try{startActivity(mail);}catch(android.content.ActivityNotFoundException e){toast("Install an email app to send invitations");}
    });}
''',1);p.write_text(s)
print('Native email invitation composer prepared')
