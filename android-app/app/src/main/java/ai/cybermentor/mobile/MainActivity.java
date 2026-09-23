package ai.cybermentor.mobile;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.speech.RecognizerIntent;
import android.speech.tts.TextToSpeech;
import android.util.Base64;
import android.view.Window;
import android.view.WindowInsetsController;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.util.ArrayList;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;

public class MainActivity extends Activity implements TextToSpeech.OnInitListener {
    private static final String OPENAI_ENDPOINT = "https://api.openai.com/v1/responses";
    private static final String OPENAI_MODELS_ENDPOINT = "https://api.openai.com/v1/models";
    private static final String GITHUB_REPO = "chandra980/CyberMentorAI";
    private static final String RELEASE_ENDPOINT = "https://api.github.com/repos/" + GITHUB_REPO + "/releases/latest";
    private static final String FEED_ENDPOINT = "https://raw.githubusercontent.com/" + GITHUB_REPO + "/main/data/cyber_feed.json";
    private static final String KEY_ALIAS = "CyberMentorAI.OpenAIKey";
    private static final String PREFS = "cybermentor_secure";
    private static final String PREF_KEY = "api_key_enc";
    private static final int FILE_CHOOSER_CODE = 2201;
    private static final int VOICE_CODE = 2202;

    private WebView webView;
    private ValueCallback<Uri[]> fileCallback;
    private final ExecutorService executor = Executors.newFixedThreadPool(3);
    private TextToSpeech tts;

    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        Window w=getWindow();
        w.setStatusBarColor(Color.rgb(7,17,31));
        w.setNavigationBarColor(Color.rgb(7,17,31));
        if (android.os.Build.VERSION.SDK_INT>=30) {
            w.setDecorFitsSystemWindows(true);
            WindowInsetsController c=w.getInsetsController();
            if(c!=null)c.setSystemBarsAppearance(0,WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS);
        }
        tts=new TextToSpeech(this,this);
        webView=new WebView(this);
        webView.setBackgroundColor(Color.rgb(7,17,31));
        setContentView(webView);
        WebSettings s=webView.getSettings();
        s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setDatabaseEnabled(true);
        s.setAllowFileAccess(true); s.setAllowContentAccess(true); s.setMediaPlaybackRequiresUserGesture(false);
        webView.setWebViewClient(new WebViewClient(){
            @Override public boolean shouldOverrideUrlLoading(WebView view, android.webkit.WebResourceRequest request){
                Uri u=request.getUrl();
                if("http".equals(u.getScheme())||"https".equals(u.getScheme())){
                    startActivity(new Intent(Intent.ACTION_VIEW,u)); return true;
                }
                return false;
            }
        });
        webView.setWebChromeClient(new WebChromeClient(){
            @Override public boolean onShowFileChooser(WebView v,ValueCallback<Uri[]> cb,FileChooserParams p){
                if(fileCallback!=null)fileCallback.onReceiveValue(null); fileCallback=cb;
                try { startActivityForResult(p.createIntent(),FILE_CHOOSER_CODE); return true; }
                catch(ActivityNotFoundException e){ fileCallback=null; return false; }
            }
        });
        webView.addJavascriptInterface(new NativeBridge(this),"AndroidAI");
        webView.loadUrl("file:///android_asset/index.html");
    }

    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data){
        super.onActivityResult(requestCode,resultCode,data);
        if(requestCode==FILE_CHOOSER_CODE){
            if(fileCallback==null)return;
            fileCallback.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(resultCode,data));
            fileCallback=null; return;
        }
        if(requestCode==VOICE_CODE && resultCode==RESULT_OK && data!=null){
            ArrayList<String> rs=data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
            if(rs!=null&&!rs.isEmpty()) js("window.CyberMentorNative&&window.CyberMentorNative.onVoiceResult("+JSONObject.quote(rs.get(0))+")");
        }
    }

    @Override public void onBackPressed(){ if(webView!=null&&webView.canGoBack())webView.goBack(); else super.onBackPressed(); }
    @Override protected void onDestroy(){ if(tts!=null){tts.stop();tts.shutdown();} executor.shutdownNow(); if(webView!=null)webView.destroy(); super.onDestroy(); }
    @Override public void onInit(int status){ if(status==TextToSpeech.SUCCESS&&tts!=null)tts.setLanguage(Locale.US); }
    private void js(String s){ runOnUiThread(()->webView.evaluateJavascript(s,null)); }

    private static String readBody(HttpURLConnection c,boolean err)throws Exception{
        InputStream st=err?c.getErrorStream():c.getInputStream(); if(st==null)return "";
        BufferedReader br=new BufferedReader(new InputStreamReader(st,StandardCharsets.UTF_8)); StringBuilder sb=new StringBuilder(); String line;
        while((line=br.readLine())!=null)sb.append(line).append('\n'); return sb.toString().trim();
    }
    private void post(String id,String endpoint,String bearer,String payload){
        executor.submit(()->{HttpURLConnection c=null; try{
            c=(HttpURLConnection)new URL(endpoint).openConnection(); c.setRequestMethod("POST"); c.setConnectTimeout(30000); c.setReadTimeout(180000); c.setDoOutput(true);
            c.setRequestProperty("Content-Type","application/json"); c.setRequestProperty("Accept","application/json");
            if(bearer!=null&&!bearer.isBlank())c.setRequestProperty("Authorization","Bearer "+bearer);
            byte[] b=payload.getBytes(StandardCharsets.UTF_8); c.setFixedLengthStreamingMode(b.length); try(OutputStream os=c.getOutputStream()){os.write(b);}
            int code=c.getResponseCode(); String body=readBody(c,code>=400); JSONObject env=new JSONObject(); env.put("status",code); env.put("body",body);
            js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult("+JSONObject.quote(id)+","+(code>=200&&code<300)+","+JSONObject.quote(env.toString())+")");
        }catch(Exception e){js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult("+JSONObject.quote(id)+",false,"+JSONObject.quote(e.getMessage())+")");}
        finally{if(c!=null)c.disconnect();}});
    }
    private String bestOpenAIModel(String key)throws Exception{
        HttpURLConnection c=null;
        try{
            c=(HttpURLConnection)new URL(OPENAI_MODELS_ENDPOINT).openConnection();
            c.setConnectTimeout(20000); c.setReadTimeout(30000);
            c.setRequestProperty("Accept","application/json");
            c.setRequestProperty("Authorization","Bearer "+key);
            int code=c.getResponseCode(); String body=readBody(c,code>=400);
            if(code<200||code>=300)throw new Exception("Model catalog request failed");
            org.json.JSONArray a=new JSONObject(body).optJSONArray("data");
            if(a==null||a.length()==0)throw new Exception("No models available");
            String best=""; int bestMajor=-1,bestMinor=-1,bestTier=-1;
            java.util.regex.Pattern p=java.util.regex.Pattern.compile("gpt-(\\d+)(?:\\.(\\d+))?");
            for(int i=0;i<a.length();i++){
                JSONObject o=a.optJSONObject(i); if(o==null)continue;
                String id=o.optString("id","");
                String low=id.toLowerCase(java.util.Locale.ROOT);
                if(!id.startsWith("gpt-")||low.contains("audio")||low.contains("image")||low.contains("realtime")||low.contains("transcribe")||low.contains("tts")||low.contains("embedding")||low.contains("search")||low.contains("cyber")||low.contains("daybreak"))continue;
                java.util.regex.Matcher m=p.matcher(id);
                int major=0,minor=0;if(m.find()){major=Integer.parseInt(m.group(1));if(m.group(2)!=null)minor=Integer.parseInt(m.group(2));}
                int tier=low.contains("sol")?3:(low.contains("terra")?2:(low.contains("luna")?1:2));
                if(major>bestMajor||(major==bestMajor&&minor>bestMinor)||(major==bestMajor&&minor==bestMinor&&tier>bestTier)||(major==bestMajor&&minor==bestMinor&&tier==bestTier&&id.compareTo(best)>0)){
                    best=id;bestMajor=major;bestMinor=minor;bestTier=tier;
                }
            }
            if(best.isEmpty())throw new Exception("No compatible GPT model found");
            return best;
        }finally{if(c!=null)c.disconnect();}
    }

    private void get(String id,String endpoint,String bearer,String cb){
        executor.submit(()->{HttpURLConnection c=null; try{
            c=(HttpURLConnection)new URL(endpoint).openConnection(); c.setConnectTimeout(20000); c.setReadTimeout(40000); c.setRequestProperty("Accept","application/json"); c.setRequestProperty("User-Agent","CyberMentorAI-Android/2.0");
            if(bearer!=null&&!bearer.isBlank())c.setRequestProperty("Authorization","Bearer "+bearer);
            int code=c.getResponseCode(); String body=readBody(c,code>=400);
            js("window.CyberMentorNative&&window.CyberMentorNative."+cb+"("+JSONObject.quote(id)+","+(code>=200&&code<300)+","+JSONObject.quote(body)+")");
        }catch(Exception e){js("window.CyberMentorNative&&window.CyberMentorNative."+cb+"("+JSONObject.quote(id)+",false,"+JSONObject.quote(e.getMessage())+")");}
        finally{if(c!=null)c.disconnect();}});
    }

    private SecretKey key()throws Exception{
        KeyStore ks=KeyStore.getInstance("AndroidKeyStore"); ks.load(null);
        if(ks.containsAlias(KEY_ALIAS))return ((KeyStore.SecretKeyEntry)ks.getEntry(KEY_ALIAS,null)).getSecretKey();
        KeyGenerator kg=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
        kg.init(new KeyGenParameterSpec.Builder(KEY_ALIAS,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT).setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build());
        return kg.generateKey();
    }
    private void saveKey(String raw)throws Exception{
        Cipher c=Cipher.getInstance("AES/GCM/NoPadding"); c.init(Cipher.ENCRYPT_MODE,key());
        String packed=Base64.encodeToString(c.getIV(),Base64.NO_WRAP)+":"+Base64.encodeToString(c.doFinal(raw.getBytes(StandardCharsets.UTF_8)),Base64.NO_WRAP);
        getSharedPreferences(PREFS,MODE_PRIVATE).edit().putString(PREF_KEY,packed).apply();
    }
    private String loadKey()throws Exception{
        String p=getSharedPreferences(PREFS,MODE_PRIVATE).getString(PREF_KEY,null); if(p==null||p.isBlank())return null;
        String[] a=p.split(":",2); Cipher c=Cipher.getInstance("AES/GCM/NoPadding"); c.init(Cipher.DECRYPT_MODE,key(),new GCMParameterSpec(128,Base64.decode(a[0],Base64.NO_WRAP)));
        return new String(c.doFinal(Base64.decode(a[1],Base64.NO_WRAP)),StandardCharsets.UTF_8);
    }

    public final class NativeBridge {
        private final Context ctx; NativeBridge(Context c){ctx=c;}
        @JavascriptInterface public void toast(String msg){runOnUiThread(()->Toast.makeText(ctx,msg==null?"":msg,Toast.LENGTH_SHORT).show());}
        @JavascriptInterface public boolean hasApiKey(){try{return loadKey()!=null;}catch(Exception e){return false;}}
        @JavascriptInterface public String saveApiKey(String k){try{if(k==null||k.trim().length()<20)return "Invalid key";saveKey(k.trim());return "OK";}catch(Exception e){return "Save failed: "+e.getMessage();}}
        @JavascriptInterface public void clearApiKey(){getSharedPreferences(PREFS,MODE_PRIVATE).edit().remove(PREF_KEY).apply();}
        @JavascriptInterface public void chat(String id,String payload){
            executor.submit(()->{
                try{
                    String k=loadKey();
                    if(k==null){js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult("+JSONObject.quote(id)+",false,'SETUP_REQUIRED')");return;}
                    JSONObject o=new JSONObject(payload);o.remove("provider");
                    String model=o.optString("model","").trim();
                    if(model.isEmpty()){
                        model=bestOpenAIModel(k);
                        o.put("model",model);
                        js("window.CyberMentorNative&&window.CyberMentorNative.onAutoModel("+JSONObject.quote(model)+")");
                    }
                    post(id,OPENAI_ENDPOINT,k,o.toString());
                }catch(Exception e){js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult("+JSONObject.quote(id)+",false,"+JSONObject.quote(e.getMessage())+")");}
            });
        }
        @JavascriptInterface public void backendChat(String id,String base,String token,String payload){
            if(base==null||(!base.startsWith("https://")&&!base.startsWith("http://127.0.0.1")&&!base.startsWith("http://localhost"))){js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult("+JSONObject.quote(id)+",false,'Backend must use HTTPS or localhost')");return;}
            post(id,base.endsWith("/")?base+"api/chat":base+"/api/chat",token,payload);
        }
        @JavascriptInterface public void startVoice(){runOnUiThread(()->{Intent i=new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);try{startActivityForResult(i,VOICE_CODE);}catch(Exception e){Toast.makeText(ctx,"Speech recognition unavailable",Toast.LENGTH_SHORT).show();}});}
        @JavascriptInterface public void speak(String t){if(tts!=null&&t!=null&&!t.isBlank())tts.speak(t,TextToSpeech.QUEUE_FLUSH,null,"cm");}
        @JavascriptInterface public void shareText(String title,String text){runOnUiThread(()->{Intent i=new Intent(Intent.ACTION_SEND);i.setType("text/plain");i.putExtra(Intent.EXTRA_SUBJECT,title);i.putExtra(Intent.EXTRA_TEXT,text);startActivity(Intent.createChooser(i,"Share"));});}
        @JavascriptInterface public String appVersion(){try{return ctx.getPackageManager().getPackageInfo(ctx.getPackageName(),0).versionName;}catch(Exception e){return "unknown";}}
        @JavascriptInterface public void refreshOpenAIModels(String id){try{String k=loadKey();if(k==null){js("window.CyberMentorNative&&window.CyberMentorNative.onModelCatalog("+JSONObject.quote(id)+",false,'No API key saved')");return;}get(id,OPENAI_MODELS_ENDPOINT,k,"onModelCatalog");}catch(Exception e){}}
        @JavascriptInterface public void fetchCyberFeed(String id){get(id,FEED_ENDPOINT,null,"onCyberFeed");}
        @JavascriptInterface public void checkForUpdates(String id){get(id,RELEASE_ENDPOINT,null,"onUpdateInfo");}
        @JavascriptInterface public void openUrl(String u){runOnUiThread(()->{try{Uri x=Uri.parse(u);if("https".equals(x.getScheme()))startActivity(new Intent(Intent.ACTION_VIEW,x));}catch(Exception e){}});}
        @JavascriptInterface public void openApiKeyPage(){runOnUiThread(()->startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse("https://platform.openai.com/api-keys"))));}
        @JavascriptInterface public void openAppSettings(){runOnUiThread(()->{Intent i=new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);i.setData(Uri.parse("package:"+getPackageName()));startActivity(i);});}
    }
}
