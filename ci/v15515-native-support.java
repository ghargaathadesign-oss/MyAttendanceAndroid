  private static final String SUPPORT_OWNER_EMAIL="pratik.kumar.kashyap@gmail.com";
  private final java.util.concurrent.ExecutorService supportWorker=java.util.concurrent.Executors.newSingleThreadExecutor();
  private boolean isSupportOwner(FirebaseUser user){return user!=null&&user.isEmailVerified()&&SUPPORT_OWNER_EMAIL.equals(user.getEmail());}
  private FirebaseUser supportUser() throws Exception {FirebaseUser u=auth==null?null:auth.getCurrentUser();if(u==null||!u.isEmailVerified())throw new Exception("Sign in with a verified account to use chat.");return u;}
  private String supportThread(FirebaseUser u,String requested) throws Exception {
    String id=isSupportOwner(u)?requested:u.getUid();
    if(id==null||!id.matches("[A-Za-z0-9_-]{1,128}"))throw new Exception("Choose a conversation first.");return id;
  }
  private com.google.firebase.storage.StorageReference supportRoot(){return com.google.firebase.storage.FirebaseStorage.getInstance().getReference().child("support");}
  private <T> T supportAwait(com.google.android.gms.tasks.Task<T> task) throws Exception {return com.google.android.gms.tasks.Tasks.await(task,15,java.util.concurrent.TimeUnit.SECONDS);}
  private String supportError(Exception e){if(e instanceof com.google.firebase.storage.StorageException){int c=((com.google.firebase.storage.StorageException)e).getErrorCode();if(c==com.google.firebase.storage.StorageException.ERROR_NOT_AUTHORIZED)return "Chat access is unavailable. Contact support or try again after signing in.";}return "Could not connect. Check your internet connection and try again.";}
  private final java.util.Map<String,org.json.JSONObject> supportMessageCache=new java.util.HashMap<>();
  private org.json.JSONArray supportMessages(FirebaseUser u,String id) throws Exception {
    java.util.ArrayList<org.json.JSONObject> rows=new java.util.ArrayList<>();
    com.google.firebase.storage.ListResult senders=supportAwait(supportRoot().child(id).child("messages").listAll());
    for(com.google.firebase.storage.StorageReference sender:senders.getPrefixes()){
      java.util.ArrayList<com.google.firebase.storage.StorageReference> files=new java.util.ArrayList<>();String page=null;
      do{com.google.firebase.storage.ListResult batch=supportAwait(page==null?sender.list(1000):sender.list(1000,page));files.addAll(batch.getItems());page=batch.getPageToken();}while(page!=null);
      files.sort((a,b)->b.getName().compareTo(a.getName()));
      for(int i=0;i<Math.min(100,files.size());i++){
        com.google.firebase.storage.StorageReference file=files.get(i);
        String cacheKey=u.getUid()+":"+file.getPath();org.json.JSONObject cached=supportMessageCache.get(cacheKey);
        if(cached!=null){rows.add(cached);continue;}
        org.json.JSONObject body=new org.json.JSONObject(new String(supportAwait(file.getBytes(8192)),java.nio.charset.StandardCharsets.UTF_8));
        com.google.firebase.storage.StorageMetadata meta=supportAwait(file.getMetadata());
        org.json.JSONObject row=new org.json.JSONObject();row.put("text",body.optString("text"));row.put("createdAt",meta.getCreationTimeMillis());row.put("mine",sender.getName().equals(u.getUid()));row.put("support","true".equals(meta.getCustomMetadata("support")));rows.add(row);supportMessageCache.put(cacheKey,row);
      }
    }
    rows.sort((a,b)->Long.compare(a.optLong("createdAt"),b.optLong("createdAt")));return new org.json.JSONArray(rows);
  }
  private void supportLoadNative(String requested){supportWorker.execute(()->{try{
    FirebaseUser u=supportUser();boolean owner=isSupportOwner(u);org.json.JSONObject result=new org.json.JSONObject();result.put("ok",true);result.put("owner",owner);
    if(owner&&(requested==null||requested.isEmpty())){
      org.json.JSONArray threads=new org.json.JSONArray();com.google.firebase.storage.ListResult list=supportAwait(supportRoot().listAll());
      for(com.google.firebase.storage.StorageReference thread:list.getPrefixes()){
        try{org.json.JSONObject info=new org.json.JSONObject(new String(supportAwait(thread.child("profile.json").getBytes(4096)),java.nio.charset.StandardCharsets.UTF_8));info.put("uid",thread.getName());threads.put(info);}catch(com.google.firebase.storage.StorageException e){if(e.getErrorCode()!=com.google.firebase.storage.StorageException.ERROR_OBJECT_NOT_FOUND)throw e;}
      }result.put("threads",threads);
    }else result.put("messages",supportMessages(u,supportThread(u,requested)));
    js("window.onSupportState&&window.onSupportState("+org.json.JSONObject.quote(result.toString())+");");
  }catch(Exception e){js("window.onSupportState&&window.onSupportState("+org.json.JSONObject.quote("{\"ok\":false,\"error\":"+org.json.JSONObject.quote(supportError(e))+"}")+");");}});}
  private void supportSendNative(String requested,String text){supportWorker.execute(()->{try{
    FirebaseUser u=supportUser();String id=supportThread(u,requested);String message=text==null?"":text.trim();if(message.isEmpty()||message.length()>2000)throw new Exception("Message length is invalid.");
    com.google.firebase.storage.StorageMetadata metadata=new com.google.firebase.storage.StorageMetadata.Builder().setContentType("application/json").setCustomMetadata("senderUid",u.getUid()).setCustomMetadata("support",String.valueOf(isSupportOwner(u))).build();
    if(!isSupportOwner(u)){org.json.JSONObject profile=new org.json.JSONObject();profile.put("name",u.getDisplayName()==null?"":u.getDisplayName());profile.put("email",u.getEmail());supportAwait(supportRoot().child(id).child("profile.json").putBytes(profile.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8),metadata));}
    org.json.JSONObject body=new org.json.JSONObject();body.put("text",message);String messageId=String.format(java.util.Locale.US,"%013d",System.currentTimeMillis())+"-"+java.util.UUID.randomUUID()+".json";
    supportAwait(supportRoot().child(id).child("messages").child(u.getUid()).child(messageId).putBytes(body.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8),metadata));
    js("window.onSupportSent&&window.onSupportSent(true,'');");
  }catch(Exception e){js("window.onSupportSent&&window.onSupportSent(false,"+org.json.JSONObject.quote(supportError(e))+");");}});}
  private void supportClearNative(String requested){supportWorker.execute(()->{try{
    FirebaseUser u=supportUser();String id=supportThread(u,requested);com.google.firebase.storage.StorageReference root=supportRoot().child(id);
    com.google.firebase.storage.ListResult senders=supportAwait(root.child("messages").listAll());
    for(com.google.firebase.storage.StorageReference sender:senders.getPrefixes()){com.google.firebase.storage.ListResult files=supportAwait(sender.listAll());for(com.google.firebase.storage.StorageReference file:files.getItems())supportAwait(file.delete());}
    try{supportAwait(root.child("profile.json").delete());}catch(com.google.firebase.storage.StorageException e){if(e.getErrorCode()!=com.google.firebase.storage.StorageException.ERROR_OBJECT_NOT_FOUND)throw e;}
    supportMessageCache.clear();
    js("window.onSupportCleared&&window.onSupportCleared(true,'');");
  }catch(Exception e){js("window.onSupportCleared&&window.onSupportCleared(false,"+org.json.JSONObject.quote(supportError(e))+");");}});}
