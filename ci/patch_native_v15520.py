from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text();anchor='  public class AndroidBridge{'
if anchor not in s:raise SystemExit('Missing Android bridge')
s=s.replace(anchor,anchor+'''
    @JavascriptInterface public void shareAppInvite(){runOnUiThread(()->{
      android.content.Intent share=new android.content.Intent(android.content.Intent.ACTION_SEND);
      share.setType("text/plain");share.putExtra(android.content.Intent.EXTRA_SUBJECT,"You’re invited to My Attendance");
      share.putExtra(android.content.Intent.EXTRA_TEXT,"You’re invited to My Attendance. Track your attendance, leave and salary.\\n\\nDownload the Android app:\\nhttps://my-attendance-download.lively-cloud-6542.chatgpt.site");
      try{startActivity(android.content.Intent.createChooser(share,"Share My Attendance"));}catch(android.content.ActivityNotFoundException e){toast("No sharing app is available");}
    });}
''',1);p.write_text(s)
print('Native Android invite share sheet prepared')
