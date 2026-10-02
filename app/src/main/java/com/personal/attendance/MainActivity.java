package com.personal.attendance;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ContentValues;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import androidx.core.content.FileProvider;
import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

public class MainActivity extends Activity {
  private WebView webView;
  private ValueCallback<Uri[]> chooser;
  private static final int FILE_REQ=4102;

  @SuppressWarnings("deprecation")
  @SuppressLint({"SetJavaScriptEnabled","AddJavascriptInterface"})
  @Override public void onCreate(Bundle b){
    super.onCreate(b);
    webView=new WebView(this);
    setContentView(webView);
    WebSettings s=webView.getSettings();
    s.setJavaScriptEnabled(true);
    s.setDomStorageEnabled(true);
    s.setDatabaseEnabled(true);
    s.setAllowFileAccess(true);
    s.setAllowContentAccess(true);
    // Lottie loads local JSON animation files with XHR/fetch from file:///android_asset/.
    // Modern Android WebView blocks file-to-file requests unless this is explicitly enabled.
    s.setAllowFileAccessFromFileURLs(true);
    s.setTextZoom(100);
    webView.setWebViewClient(new WebViewClient());
    webView.addJavascriptInterface(new AndroidBridge(this),"Android");
    webView.setWebChromeClient(new WebChromeClient(){
      @Override public boolean onShowFileChooser(WebView w,ValueCallback<Uri[]> cb,FileChooserParams p){
        if(chooser!=null)chooser.onReceiveValue(null);
        chooser=cb;
        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("*/*");
        try{
          String[] accepts=p.getAcceptTypes();
          ArrayList<String> types=new ArrayList<>();
          if(accepts!=null){
            for(String a:accepts){
              if(a==null)continue;
              for(String t:a.split(",")){
                t=t.trim();
                if(t.contains("/"))types.add(t);
              }
            }
          }
          if(!types.isEmpty())i.putExtra(Intent.EXTRA_MIME_TYPES,types.toArray(new String[0]));
        }catch(Exception ignored){}
        startActivityForResult(i,FILE_REQ);
        return true;
      }
    });
    webView.loadUrl("file:///android_asset/index.html");
  }

  @Override protected void onActivityResult(int r,int c,Intent d){
    super.onActivityResult(r,c,d);
    if(r==FILE_REQ&&chooser!=null){
      Uri[] v=null;
      if(c==RESULT_OK&&d!=null&&d.getData()!=null)v=new Uri[]{d.getData()};
      chooser.onReceiveValue(v);
      chooser=null;
    }
  }

  private void closeFromBack(){super.onBackPressed();}

  @Override public void onBackPressed(){
    if(webView==null){closeFromBack();return;}
    webView.evaluateJavascript("(function(){try{if(window.appBack)return !!window.appBack();var active=document.querySelector('.screen.active');if(active&&active.id!=='screen-home'){var home=document.querySelector('.navBtn[data-screen=\"home\"]');if(home){home.click();return true;}}return false;}catch(e){return false;}})();", value -> {
      if(!"true".equals(value))closeFromBack();
    });
  }

  public static class AndroidBridge{
    private final Activity a;
    AndroidBridge(Activity activity){this.a=activity;}
    private String safeName(String name){if(name==null||name.trim().isEmpty())return "document";return name.replaceAll("[\\\\/:*?\"<>|]","_");}
    private void saveBytes(String name,String mime,byte[] bytes,String folder) throws Exception{
      name=safeName(name);
      if(mime==null||mime.trim().isEmpty())mime="application/octet-stream";
      if(Build.VERSION.SDK_INT>=29){
        ContentValues v=new ContentValues();
        v.put(MediaStore.Downloads.DISPLAY_NAME,name);
        v.put(MediaStore.Downloads.MIME_TYPE,mime);
        v.put(MediaStore.Downloads.RELATIVE_PATH,Environment.DIRECTORY_DOWNLOADS+"/My Attendance/"+folder);
        Uri u=a.getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,v);
        if(u==null)throw new Exception("Unable to create file");
        try(OutputStream o=a.getContentResolver().openOutputStream(u)){o.write(bytes);}
      }else{
        File dir=new File(a.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS),"My Attendance/"+folder);
        dir.mkdirs();
        File f=new File(dir,name);
        try(FileOutputStream o=new FileOutputStream(f)){o.write(bytes);}
      }
    }
    @JavascriptInterface public void saveCsv(String name,String content){
      try{
        if(name==null||name.trim().isEmpty())name="attendance.csv";
        if(!name.toLowerCase().endsWith(".csv"))name+=".csv";
        saveBytes(name,"text/csv",content.getBytes(StandardCharsets.UTF_8),"Backups");
        toast("CSV saved to Downloads/My Attendance/Backups");
      }catch(Exception e){toast("CSV save failed: "+e.getMessage());}
    }
    @JavascriptInterface public void saveBase64File(String name,String mime,String base64){
      try{
        byte[] bytes=Base64.decode(base64,Base64.DEFAULT);
        saveBytes(name,mime,bytes,"Documents");
        toast("Document saved to Downloads/My Attendance/Documents");
      }catch(Exception e){toast("Document export failed: "+e.getMessage());}
    }
    @JavascriptInterface public void shareBase64File(String name,String mime,String base64){
      try{
        name=safeName(name);
        if(mime==null||mime.trim().isEmpty())mime="application/octet-stream";
        byte[] bytes=Base64.decode(base64,Base64.DEFAULT);
        File dir=new File(a.getCacheDir(),"shared_documents");
        if(!dir.exists())dir.mkdirs();
        File f=new File(dir,name);
        try(FileOutputStream o=new FileOutputStream(f)){o.write(bytes);}
        Uri uri=FileProvider.getUriForFile(a,a.getPackageName()+".fileprovider",f);
        Intent send=new Intent(Intent.ACTION_SEND);
        send.setType(mime);
        send.putExtra(Intent.EXTRA_STREAM,uri);
        send.putExtra(Intent.EXTRA_SUBJECT,name);
        send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        a.startActivity(Intent.createChooser(send,"Share document"));
      }catch(Exception e){toast("Document share failed: "+e.getMessage());}
    }
    @JavascriptInterface public void toast(String m){a.runOnUiThread(() -> Toast.makeText(a,m,Toast.LENGTH_SHORT).show());}
  }
}
