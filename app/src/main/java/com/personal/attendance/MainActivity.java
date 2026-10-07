package com.personal.attendance;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ContentValues;
import android.content.Intent;
import android.content.MutableContextWrapper;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.CancellationSignal;
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

import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;
import androidx.credentials.CredentialManager;
import androidx.credentials.CredentialManagerCallback;
import androidx.credentials.CustomCredential;
import androidx.credentials.GetCredentialRequest;
import androidx.credentials.GetCredentialResponse;
import androidx.credentials.exceptions.GetCredentialException;

import com.google.android.libraries.identity.googleid.GetGoogleIdOption;
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential;
import com.google.firebase.FirebaseApp;
import com.google.firebase.FirebaseOptions;
import com.google.firebase.auth.AuthCredential;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.auth.GoogleAuthProvider;
import com.google.firebase.storage.FirebaseStorage;
import com.google.firebase.storage.StorageMetadata;
import com.google.firebase.storage.StorageReference;

import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

public class MainActivity extends Activity {
  private WebView webView;
  private ValueCallback<Uri[]> chooser;
  private static final int FILE_REQ=4102;
  private static final String WEB_CLIENT_ID="312314814209-5nm1pj6a89o6aglpismq5vb4k9lqtglb.apps.googleusercontent.com";
  private static final String FIREBASE_API_KEY=BuildConfig.FIREBASE_API_KEY;
  private static final String FIREBASE_APP_ID="1:312314814209:android:764780f6a72c65b9a38500";
  private static final String FIREBASE_PROJECT_ID="my-attendance-c5c23";
  private static final String FIREBASE_STORAGE_BUCKET="my-attendance-c5c23.firebasestorage.app";
  private static final String FIREBASE_SENDER_ID="312314814209";
  private FirebaseAuth auth;
  private FirebaseStorage cloudStorage;
  private CredentialManager credentialManager;
  private String firebaseInitError="";

  @SuppressWarnings("deprecation")
  @SuppressLint({"SetJavaScriptEnabled","AddJavascriptInterface"})
  @Override public void onCreate(Bundle b){
    super.onCreate(b);
    initFirebase();
    credentialManager=CredentialManager.create(this);
    webView=new WebView(this);
    setContentView(webView);
    WebSettings s=webView.getSettings();
    s.setJavaScriptEnabled(true);
    s.setDomStorageEnabled(true);
    s.setDatabaseEnabled(true);
    s.setCacheMode(WebSettings.LOAD_NO_CACHE);
    s.setAllowFileAccess(true);
    s.setAllowContentAccess(true);
    s.setAllowFileAccessFromFileURLs(true);
    s.setTextZoom(100);
    webView.setWebViewClient(new WebViewClient(){
      @Override public void onPageFinished(WebView view,String url){super.onPageFinished(view,url);pushAuthState();}
    });
    webView.addJavascriptInterface(new AndroidBridge(),"Android");
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

  private void initFirebase(){
    try{
      if(FIREBASE_API_KEY==null||FIREBASE_API_KEY.trim().isEmpty())throw new IllegalStateException("Firebase API key was not supplied at build time.");
      if(FirebaseApp.getApps(this).isEmpty()){
        FirebaseOptions options=new FirebaseOptions.Builder()
          .setApiKey(FIREBASE_API_KEY)
          .setApplicationId(FIREBASE_APP_ID)
          .setProjectId(FIREBASE_PROJECT_ID)
          .setStorageBucket(FIREBASE_STORAGE_BUCKET)
          .setGcmSenderId(FIREBASE_SENDER_ID)
          .build();
        FirebaseApp.initializeApp(this,options);
      }
      auth=FirebaseAuth.getInstance();
      cloudStorage=FirebaseStorage.getInstance();
      firebaseInitError="";
    }catch(Exception e){
      auth=null;
      cloudStorage=null;
      firebaseInitError=e.getMessage()==null?"Firebase initialization failed":e.getMessage();
    }
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

  private void js(String code){if(webView!=null)runOnUiThread(() -> webView.evaluateJavascript(code,null));}
  private void jsError(String msg){js("window.onNativeAuthError&&window.onNativeAuthError("+JSONObject.quote(msg==null?"Unknown error":msg)+");");}
  private void jsNotice(String msg){js("window.onNativeAuthNotice&&window.onNativeAuthNotice("+JSONObject.quote(msg==null?"":msg)+");");}

  private void pushAuthState(){
    try{
      JSONObject o=new JSONObject();
      FirebaseUser u=auth==null?null:auth.getCurrentUser();
      o.put("signedIn",u!=null);
      o.put("emailVerified",u!=null&&u.isEmailVerified());
      if(u!=null){
        o.put("uid",u.getUid());
        o.put("name",u.getDisplayName()==null?"":u.getDisplayName());
        o.put("email",u.getEmail()==null?"":u.getEmail());
        o.put("photo",u.getPhotoUrl()==null?"":u.getPhotoUrl().toString());
      }
      if(auth==null)o.put("setupError",firebaseInitError.isEmpty()?"Firebase initialization failed":firebaseInitError);
      js("window.onNativeAuthChanged&&window.onNativeAuthChanged("+o.toString()+");");
    }catch(Exception e){jsError(e.getMessage());}
  }

  private void beginGoogleSignIn(){
    if(auth==null){jsError("Firebase initialization failed: "+firebaseInitError);return;}
    try{
      GetGoogleIdOption option=new GetGoogleIdOption.Builder()
        .setFilterByAuthorizedAccounts(false)
        .setServerClientId(WEB_CLIENT_ID)
        .setAutoSelectEnabled(false)
        .build();
      GetCredentialRequest request=new GetCredentialRequest.Builder().addCredentialOption(option).build();
      credentialManager.getCredentialAsync(
        new MutableContextWrapper(this),request,new CancellationSignal(),ContextCompat.getMainExecutor(this),
        new CredentialManagerCallback<GetCredentialResponse,GetCredentialException>(){
          @Override public void onResult(GetCredentialResponse result){handleCredential(result);}
          @Override public void onError(GetCredentialException e){jsError(e.getMessage()==null?"Google sign-in cancelled":e.getMessage());}
        }
      );
    }catch(Exception e){jsError(e.getMessage());}
  }

  private void handleCredential(GetCredentialResponse result){
    try{
      if(!(result.getCredential() instanceof CustomCredential)){jsError("Google credential was not returned.");return;}
      CustomCredential c=(CustomCredential)result.getCredential();
      if(!GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL.equals(c.getType())){jsError("Unsupported Google credential type.");return;}
      GoogleIdTokenCredential g=GoogleIdTokenCredential.createFrom(c.getData());
      AuthCredential fc=GoogleAuthProvider.getCredential(g.getIdToken(),null);
      auth.signInWithCredential(fc).addOnCompleteListener(this,t->{
        if(t.isSuccessful())pushAuthState();
        else jsError(t.getException()==null?"Google sign-in failed":t.getException().getMessage());
      });
    }catch(Exception e){jsError(e.getMessage());}
  }

  private void emailSignUp(String email,String password){
    if(auth==null){jsError("Firebase initialization failed: "+firebaseInitError);return;}
    auth.createUserWithEmailAndPassword(email,password).addOnCompleteListener(this,t->{
      if(!t.isSuccessful()){jsError(t.getException()==null?"Could not create account":t.getException().getMessage());return;}
      FirebaseUser u=auth.getCurrentUser();
      if(u==null){jsError("Account was created but user session is unavailable.");return;}
      u.sendEmailVerification().addOnCompleteListener(this,v->{
        if(v.isSuccessful())jsNotice("Verification email sent. Open the email and tap the verification link.");
        else jsError(v.getException()==null?"Could not send verification email":v.getException().getMessage());
        pushAuthState();
      });
    });
  }

  private void emailSignIn(String email,String password){
    if(auth==null){jsError("Firebase initialization failed: "+firebaseInitError);return;}
    auth.signInWithEmailAndPassword(email,password).addOnCompleteListener(this,t->{
      if(t.isSuccessful())pushAuthState();
      else jsError(t.getException()==null?"Email or password is incorrect":t.getException().getMessage());
    });
  }

  private void resendVerification(){
    FirebaseUser u=auth==null?null:auth.getCurrentUser();
    if(u==null){jsError("Please sign in again.");return;}
    if(u.isEmailVerified()){jsNotice("Your email is already verified.");pushAuthState();return;}
    u.sendEmailVerification().addOnCompleteListener(this,t->{
      if(t.isSuccessful())jsNotice("Verification email sent again.");
      else jsError(t.getException()==null?"Could not resend verification email":t.getException().getMessage());
    });
  }

  private void checkEmailVerified(){
    FirebaseUser u=auth==null?null:auth.getCurrentUser();
    if(u==null){jsError("Please sign in again.");return;}
    u.reload().addOnCompleteListener(this,t->{
      if(!t.isSuccessful()){jsError(t.getException()==null?"Could not check verification":t.getException().getMessage());return;}
      FirebaseUser fresh=auth.getCurrentUser();
      if(fresh!=null&&fresh.isEmailVerified())jsNotice("Email verified successfully.");
      else jsNotice("Email is not verified yet. Open the verification email and tap the link first.");
      pushAuthState();
    });
  }

  private void resetPassword(String email){
    if(auth==null){jsError("Firebase initialization failed: "+firebaseInitError);return;}
    auth.sendPasswordResetEmail(email).addOnCompleteListener(this,t->{
      if(t.isSuccessful())jsNotice("Password reset email sent.");
      else jsError(t.getException()==null?"Could not send reset email":t.getException().getMessage());
    });
  }

  private StorageReference backupRef(){
    FirebaseUser u=auth==null?null:auth.getCurrentUser();
    if(u==null||cloudStorage==null||!u.isEmailVerified())return null;
    return cloudStorage.getReference().child("users").child(u.getUid()).child("backups").child("latest.json");
  }

  private void cloudBackup(String json){
    StorageReference ref=backupRef();
    if(ref==null){js("window.onCloudBackupResult&&window.onCloudBackupResult(false,'Please sign in with a verified account first',0);");return;}
    byte[] bytes=(json==null?"{}":json).getBytes(StandardCharsets.UTF_8);
    StorageMetadata meta=new StorageMetadata.Builder().setContentType("application/json").setCustomMetadata("source","My Attendance Android").build();
    ref.putBytes(bytes,meta).addOnSuccessListener(x->{
      long now=System.currentTimeMillis();
      js("window.onCloudBackupResult&&window.onCloudBackupResult(true,'Backup saved',"+now+");");
    }).addOnFailureListener(e->js("window.onCloudBackupResult&&window.onCloudBackupResult(false,"+JSONObject.quote(e.getMessage()==null?"Backup failed":e.getMessage())+",0);"));
  }

  private void cloudRestore(){
    StorageReference ref=backupRef();
    if(ref==null){js("window.onCloudRestoreError&&window.onCloudRestoreError('Please sign in with a verified account first');");return;}
    ref.getBytes(25L*1024L*1024L).addOnSuccessListener(bytes->{
      String payload=new String(bytes,StandardCharsets.UTF_8);
      js("window.onCloudRestore&&window.onCloudRestore("+JSONObject.quote(payload)+");");
    }).addOnFailureListener(e->js("window.onCloudRestoreError&&window.onCloudRestoreError("+JSONObject.quote(e.getMessage()==null?"No backup found":e.getMessage())+");"));
  }

  public class AndroidBridge{
    private String safeName(String name){if(name==null||name.trim().isEmpty())return "document";return name.replaceAll("[\\\\/:*?\"<>|]","_");}
    private void saveBytes(String name,String mime,byte[] bytes,String folder) throws Exception{
      name=safeName(name);
      if(mime==null||mime.trim().isEmpty())mime="application/octet-stream";
      if(Build.VERSION.SDK_INT>=29){
        ContentValues v=new ContentValues();
        v.put(MediaStore.Downloads.DISPLAY_NAME,name);
        v.put(MediaStore.Downloads.MIME_TYPE,mime);
        v.put(MediaStore.Downloads.RELATIVE_PATH,Environment.DIRECTORY_DOWNLOADS+"/My Attendance/"+folder);
        Uri u=getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,v);
        if(u==null)throw new Exception("Unable to create file");
        try(OutputStream o=getContentResolver().openOutputStream(u)){o.write(bytes);}
      }else{
        File dir=new File(getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS),"My Attendance/"+folder);
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
      try{saveBytes(name,mime,Base64.decode(base64,Base64.DEFAULT),"Documents");toast("Document saved to Downloads/My Attendance/Documents");}
      catch(Exception e){toast("Document export failed: "+e.getMessage());}
    }
    @JavascriptInterface public void shareBase64File(String name,String mime,String base64){
      try{
        name=safeName(name);if(mime==null||mime.trim().isEmpty())mime="application/octet-stream";
        File dir=new File(getCacheDir(),"shared_documents");if(!dir.exists())dir.mkdirs();
        File f=new File(dir,name);try(FileOutputStream o=new FileOutputStream(f)){o.write(Base64.decode(base64,Base64.DEFAULT));}
        Uri uri=FileProvider.getUriForFile(MainActivity.this,getPackageName()+".fileprovider",f);
        Intent send=new Intent(Intent.ACTION_SEND);send.setType(mime);send.putExtra(Intent.EXTRA_STREAM,uri);send.putExtra(Intent.EXTRA_SUBJECT,name);send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        startActivity(Intent.createChooser(send,"Share document"));
      }catch(Exception e){toast("Document share failed: "+e.getMessage());}
    }
    @JavascriptInterface public void googleSignIn(){runOnUiThread(() -> beginGoogleSignIn());}
    @JavascriptInterface public void emailSignUp(String email,String password){runOnUiThread(() -> MainActivity.this.emailSignUp(email,password));}
    @JavascriptInterface public void emailSignIn(String email,String password){runOnUiThread(() -> MainActivity.this.emailSignIn(email,password));}
    @JavascriptInterface public void resendVerification(){runOnUiThread(() -> MainActivity.this.resendVerification());}
    @JavascriptInterface public void checkEmailVerified(){runOnUiThread(() -> MainActivity.this.checkEmailVerified());}
    @JavascriptInterface public void resetPassword(String email){runOnUiThread(() -> MainActivity.this.resetPassword(email));}
    @JavascriptInterface public void authState(){pushAuthState();}
    @JavascriptInterface public void googleSignOut(){runOnUiThread(()->{if(auth!=null)auth.signOut();pushAuthState();});}
    @JavascriptInterface public void cloudBackup(String json){MainActivity.this.cloudBackup(json);}
    @JavascriptInterface public void cloudRestore(){MainActivity.this.cloudRestore();}
    @JavascriptInterface public void toast(String m){runOnUiThread(() -> Toast.makeText(MainActivity.this,m,Toast.LENGTH_SHORT).show());}
  }
}
