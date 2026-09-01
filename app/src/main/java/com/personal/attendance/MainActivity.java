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

public class MainActivity extends Activity {
  private WebView webView;
  private ValueCallback<Uri[]> chooser;
  private static final int FILE_REQ=4102;

  @SuppressLint({"SetJavaScriptEnabled","AddJavascriptInterface"})
  @Override public void onCreate(Bundle b){
    super.onCreate(b);
    webView=new WebView(this); setContentView(webView);
    WebSettings s=webView.getSettings(); s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setAllowFileAccess(true); s.setAllowContentAccess(true); s.setTextZoom(100);
    webView.setWebViewClient(new WebViewClient()); webView.addJavascriptInterface(new AndroidBridge(this),"Android");
    webView.setWebChromeClient(new WebChromeClient(){
      @Override public boolean onShowFileChooser(WebView w,ValueCallback<Uri[]> cb,FileChooserParams p){
        if(chooser!=null)chooser.onReceiveValue(null); chooser=cb;
        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT); i.addCategory(Intent.CATEGORY_OPENABLE); i.setType("text/*");
        i.putExtra(Intent.EXTRA_MIME_TYPES,new String[]{"text/csv","text/plain","application/vnd.ms-excel"}); startActivityForResult(i,FILE_REQ); return true;
      }
    });
    webView.loadUrl("file:///android_asset/index.html");
  }
  @Override protected void onActivityResult(int r,int c,Intent d){super.onActivityResult(r,c,d);if(r==FILE_REQ&&chooser!=null){Uri[] v=null;if(c==RESULT_OK&&d!=null&&d.getData()!=null)v=new Uri[]{d.getData()};chooser.onReceiveValue(v);chooser=null;}}
  @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();}

  public static class AndroidBridge{
    private final Context c; AndroidBridge(Context c){this.c=c;}
    @JavascriptInterface public void saveCsv(String name,String content){
      try{
        if(name==null||name.trim().isEmpty())name="attendance.csv"; if(!name.toLowerCase().endsWith(".csv"))name+=".csv";
        if(Build.VERSION.SDK_INT>=29){
          ContentValues v=new ContentValues();v.put(MediaStore.Downloads.DISPLAY_NAME,name);v.put(MediaStore.Downloads.MIME_TYPE,"text/csv");v.put(MediaStore.Downloads.RELATIVE_PATH,Environment.DIRECTORY_DOWNLOADS+"/My Attendance");
          Uri u=c.getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,v); if(u==null)throw new Exception("Unable to create file");
          try(OutputStream o=c.getContentResolver().openOutputStream(u)){o.write(content.getBytes(StandardCharsets.UTF_8));}
          toast("CSV saved to Downloads/My Attendance");
        }else{
          File dir=new File(c.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS),"My Attendance");dir.mkdirs();File f=new File(dir,name);try(FileOutputStream o=new FileOutputStream(f)){o.write(content.getBytes(StandardCharsets.UTF_8));}toast("CSV saved");
        }
      }catch(Exception e){toast("CSV save failed: "+e.getMessage());}
    }
    @JavascriptInterface public void toast(String m){Toast.makeText(c,m,Toast.LENGTH_SHORT).show();}
  }
}
