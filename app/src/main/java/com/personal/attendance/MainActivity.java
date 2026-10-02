package com.personal.attendance;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ContentValues;
import android.content.Context;
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
import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

public class MainActivity extends Activity {
  private WebView webView;
  private ValueCallback<Uri[]> chooser;
  private static final int FILE_REQ=4102;

  @SuppressLint({"SetJavaScriptEnabled","AddJavascriptInterface"})
  @Override public void onCreate(Bundle b){
    super.onCreate(b);
    webView=new WebView(this); setContentView(webView);
    WebSettings s=webView.getSettings(); s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setDatabaseEnabled(true); s.setAllowFileAccess(true); s.setAllowContentAccess(true); s.setTextZoom(100);
    webView.setWebViewClient(new WebViewClient(){
      @Override public void onPageFinished(WebView view,String url){
        super.onPageFinished(view,url);
        String inject="(function(){if(!document.getElementById('extrasCss')){var l=document.createElement('link');l.id='extrasCss';l.rel='stylesheet';l.href='extras.css';document.head.appendChild(l);}if(!document.getElementById('extrasJs')){var s=document.createElement('script');s.id='extrasJs';s.src='extras.js';document.body.appendChild(s);}})();";
        view.evaluateJavascript(inject,null);
      }
    });
    webView.addJavascriptInterface(new AndroidBridge(this),"Android");
    webView.setWebChromeClient(new WebChromeClient(){
      @Override public boolean onShowFileChooser(WebView w,ValueCallback<Uri[]> cb,FileChooserParams p){
        if(chooser!=null)chooser.onReceiveValue(null); chooser=cb;
        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT); i.addCategory(Intent.CATEGORY_OPENABLE); i.setType("*/*");
        try{
          String[] accepts=p.getAcceptTypes(); ArrayList<String> types=new ArrayList<>();
          if(accepts!=null){for(String a:accepts){if(a==null)continue;for(String t:a.split(",")){t=t.trim();if(t.contains("/"))types.add(t);}}}
          if(!types.isEmpty())i.putExtra(Intent.EXTRA_MIME_TYPES,types.toArray(new String[0]));
        }catch(Exception ignored){}
        startActivityForResult(i,FILE_REQ); return true;
      }
    });
    webView.loadUrl("file:///android_asset/index.html");
  }
  @Override protected void onActivityResult(int r,int c,Intent d){super.onActivityResult(r,c,d);if(r==FILE_REQ&&chooser!=null){Uri[] v=null;if(c==RESULT_OK&&d!=null&&d.getData()!=null)v=new Uri[]{d.getData()};chooser.onReceiveValue(v);chooser=null;}}
  @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();}

  public static class AndroidBridge{
    private final Context c; AndroidBridge(Context c){this.c=c;}
    private String safeName(String name){if(name==null||name.trim().isEmpty())return "document";return name.replaceAll("[\\\\/:*?\"<>|]","_");}
    private void saveBytes(String name,String mime,byte[] bytes,String folder) throws Exception{
      name=safeName(name); if(mime==null||mime.trim().isEmpty())mime="application/octet-stream";
      if(Build.VERSION.SDK_INT>=29){
        ContentValues v=new ContentValues();v.put(MediaStore.Downloads.DISPLAY_NAME,name);v.put(MediaStore.Downloads.MIME_TYPE,mime);v.put(MediaStore.Downloads.RELATIVE_PATH,Environment.DIRECTORY_DOWNLOADS+"/My Attendance/"+folder);
        Uri u=c.getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,v); if(u==null)throw new Exception("Unable to create file");
        try(OutputStream o=c.getContentResolver().openOutputStream(u)){o.write(bytes);}
      }else{
        File dir=new File(c.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS),"My Attendance/"+folder);dir.mkdirs();File f=new File(dir,name);try(FileOutputStream o=new FileOutputStream(f)){o.write(bytes);}
      }
    }
    @JavascriptInterface public void saveCsv(String name,String content){
      try{if(name==null||name.trim().isEmpty())name="attendance.csv";if(!name.toLowerCase().endsWith(".csv"))name+=".csv";saveBytes(name,"text/csv",content.getBytes(StandardCharsets.UTF_8),"Backups");toast("CSV saved to Downloads/My Attendance/Backups");}catch(Exception e){toast("CSV save failed: "+e.getMessage());}
    }
    @JavascriptInterface public void saveBase64File(String name,String mime,String base64){
      try{byte[] bytes=Base64.decode(base64,Base64.DEFAULT);saveBytes(name,mime,bytes,"Documents");toast("Document saved to Downloads/My Attendance/Documents");}catch(Exception e){toast("Document export failed: "+e.getMessage());}
    }
    @JavascriptInterface public void toast(String m){Toast.makeText(c,m,Toast.LENGTH_SHORT).show();}
  }
}
