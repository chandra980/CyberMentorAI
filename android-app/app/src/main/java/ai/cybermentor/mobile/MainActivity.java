package ai.cybermentor.mobile;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.speech.RecognizerIntent;
import android.speech.tts.TextToSpeech;
import android.util.Base64;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.webkit.JavascriptInterface;
import android.webkit.RenderProcessGoneDetail;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.webkit.WebViewAssetLoader;

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
    private static final String TAG = "CyberMentorAI";
    private static final String START_URL = "https://appassets.androidplatform.net/assets/index.html";
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
    private WebViewAssetLoader assetLoader;
    private ValueCallback<Uri[]> fileCallback;
    private final ExecutorService executor = Executors.newFixedThreadPool(3);
    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private TextToSpeech tts;
    private boolean uiReady = false;
    private boolean recoveryAttempted = false;

    private final Runnable startupWatchdog = () -> {
        if (!uiReady && !isFinishing()) {
            Log.e(TAG, "UI readiness watchdog expired");
            recoverWebView("The interface did not finish loading.");
        }
    };

    @Override
    public void onCreate(Bundle state) {
        super.onCreate(state);
        try {
            configureSystemBars();
            verifyWebViewProvider();
            createWebApp();
        } catch (Throwable startupError) {
            Log.e(TAG, "Startup failure", startupError);
            showStartupFallback(startupError);
        }
    }

    private void configureSystemBars() {
        Window w = getWindow();
        w.setStatusBarColor(Color.TRANSPARENT);
        w.setNavigationBarColor(Color.TRANSPARENT);
        w.getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
        );
    }

    private void verifyWebViewProvider() {
        if (android.os.Build.VERSION.SDK_INT >= 26) {
            android.content.pm.PackageInfo pkg = WebView.getCurrentWebViewPackage();
            if (pkg == null) {
                throw new IllegalStateException("No enabled Android WebView provider was found");
            }
            Log.i(TAG, "WEBVIEW_PROVIDER " + pkg.packageName + " " + pkg.versionName);
        }
    }

    private void createWebApp() {
        uiReady = false;
        mainHandler.removeCallbacks(startupWatchdog);

        assetLoader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .addPathHandler("/res/", new WebViewAssetLoader.ResourcesPathHandler(this))
                .build();

        WebView.setWebContentsDebuggingEnabled(false);
        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(5, 11, 18));
        webView.setOverScrollMode(View.OVER_SCROLL_NEVER);
        webView.setOnApplyWindowInsetsListener((view, insets) -> {
            view.setPadding(
                    insets.getSystemWindowInsetLeft(),
                    insets.getSystemWindowInsetTop(),
                    insets.getSystemWindowInsetRight(),
                    insets.getSystemWindowInsetBottom()
            );
            return insets;
        });
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(false);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setSupportZoom(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setUserAgentString(settings.getUserAgentString() + " CyberMentorAI-Android/3.3");
        if (android.os.Build.VERSION.SDK_INT >= 26) {
            try {
                settings.setSafeBrowsingEnabled(true);
            } catch (Throwable t) {
                Log.w(TAG, "Safe Browsing setup unavailable", t);
            }
        }

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                Uri uri = request == null ? null : request.getUrl();
                if (uri != null) {
                    WebResourceResponse response = assetLoader.shouldInterceptRequest(uri);
                    if (response != null) return response;
                }
                return super.shouldInterceptRequest(view, request);
            }

            @Override
            @SuppressWarnings("deprecation")
            public WebResourceResponse shouldInterceptRequest(WebView view, String url) {
                try {
                    WebResourceResponse response = assetLoader.shouldInterceptRequest(Uri.parse(url));
                    if (response != null) return response;
                } catch (Throwable ignored) {
                }
                return super.shouldInterceptRequest(view, url);
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request == null ? null : request.getUrl();
                return handleExternalNavigation(uri);
            }

            @Override
            @SuppressWarnings("deprecation")
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                try {
                    return handleExternalNavigation(Uri.parse(url));
                } catch (Throwable ignored) {
                    return true;
                }
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                Log.i(TAG, "WEBAPP_READY " + url);
                mainHandler.removeCallbacks(startupWatchdog);
                mainHandler.postDelayed(startupWatchdog, 12000);
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                super.onReceivedError(view, request, error);
                if (request != null && request.isForMainFrame()) {
                    String detail = error == null ? "unknown" : String.valueOf(error.getDescription());
                    Log.e(TAG, "Main-frame WebView error: " + detail);
                    recoverWebView("The local interface failed to load: " + detail);
                }
            }

            @Override
            public boolean onRenderProcessGone(WebView view, RenderProcessGoneDetail detail) {
                Log.e(TAG, "WebView renderer exited; crash=" + (detail != null && detail.didCrash()));
                recoverWebView("Android WebView renderer stopped unexpectedly.");
                return true;
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb, FileChooserParams params) {
                if (fileCallback != null) fileCallback.onReceiveValue(null);
                fileCallback = cb;
                try {
                    startActivityForResult(params.createIntent(), FILE_CHOOSER_CODE);
                    return true;
                } catch (ActivityNotFoundException e) {
                    fileCallback = null;
                    Toast.makeText(MainActivity.this, "No file picker is available", Toast.LENGTH_SHORT).show();
                    return false;
                }
            }
        });

        webView.addJavascriptInterface(new NativeBridge(this), "AndroidAI");
        webView.loadUrl(START_URL);
        mainHandler.postDelayed(startupWatchdog, 18000);
    }

    private boolean handleExternalNavigation(Uri uri) {
        if (uri == null) return true;
        String scheme = uri.getScheme();
        String host = uri.getHost();
        if ("https".equalsIgnoreCase(scheme) && "appassets.androidplatform.net".equalsIgnoreCase(host)) {
            return false;
        }
        if ("https".equalsIgnoreCase(scheme) || "http".equalsIgnoreCase(scheme)) {
            try {
                startActivity(new Intent(Intent.ACTION_VIEW, uri));
            } catch (Exception e) {
                Toast.makeText(this, "No browser is available for this link", Toast.LENGTH_SHORT).show();
            }
            return true;
        }
        return true;
    }

    private void markUiReady() {
        uiReady = true;
        recoveryAttempted = false;
        mainHandler.removeCallbacks(startupWatchdog);
        Log.i(TAG, "UI_READY");
    }

    private void recoverWebView(String reason) {
        runOnUiThread(() -> {
            if (isFinishing()) return;
            if (recoveryAttempted) {
                showStartupFallback(new RuntimeException(reason));
                return;
            }
            recoveryAttempted = true;
            Log.w(TAG, "Attempting WebView recovery: " + reason);
            try {
                mainHandler.removeCallbacks(startupWatchdog);
                if (webView != null) {
                    webView.removeJavascriptInterface("AndroidAI");
                    webView.stopLoading();
                    webView.loadUrl("about:blank");
                    webView.clearHistory();
                    webView.destroy();
                    webView = null;
                }
                createWebApp();
                Toast.makeText(this, "CyberMentor recovered the interface", Toast.LENGTH_SHORT).show();
            } catch (Throwable t) {
                Log.e(TAG, "WebView recovery failed", t);
                showStartupFallback(t);
            }
        });
    }

    private void showStartupFallback(Throwable error) {
        mainHandler.removeCallbacks(startupWatchdog);
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setGravity(Gravity.CENTER);
        box.setPadding(44, 44, 44, 44);
        box.setBackgroundColor(Color.rgb(5, 11, 18));

        TextView title = new TextView(this);
        title.setText("CyberMentor AI Recovery");
        title.setTextColor(Color.rgb(44, 228, 180));
        title.setTextSize(22);
        title.setGravity(Gravity.CENTER);
        box.addView(title, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView body = new TextView(this);
        body.setTextColor(Color.WHITE);
        body.setTextSize(15);
        body.setGravity(Gravity.CENTER);
        body.setPadding(0, 26, 0, 26);
        String webViewInfo = "unknown";
        try {
            if (android.os.Build.VERSION.SDK_INT >= 26) {
                android.content.pm.PackageInfo p = WebView.getCurrentWebViewPackage();
                if (p != null) webViewInfo = p.packageName + " " + p.versionName;
            }
        } catch (Throwable ignored) {
        }
        String diagnostic = error == null ? "Unknown startup error" :
                error.getClass().getSimpleName() + ": " + String.valueOf(error.getMessage());
        body.setText(
                "The app opened in recovery mode because Android WebView could not finish startup.\n\n" +
                "Android " + android.os.Build.VERSION.RELEASE + " (API " + android.os.Build.VERSION.SDK_INT + ")\n" +
                "WebView: " + webViewInfo + "\n\n" +
                "Diagnostic: " + diagnostic
        );
        box.addView(body, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));

        Button retry = new Button(this);
        retry.setText("RETRY CYBERMENTOR");
        retry.setOnClickListener(v -> {
            recoveryAttempted = false;
            try {
                verifyWebViewProvider();
                createWebApp();
            } catch (Throwable t) {
                showStartupFallback(t);
            }
        });
        box.addView(retry, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        Button update = new Button(this);
        update.setText("UPDATE ANDROID SYSTEM WEBVIEW");
        update.setOnClickListener(v -> openWebViewStore());
        box.addView(update, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        Button appSettings = new Button(this);
        appSettings.setText("OPEN APP SETTINGS");
        appSettings.setOnClickListener(v -> {
            try {
                Intent i = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
                i.setData(Uri.parse("package:" + getPackageName()));
                startActivity(i);
            } catch (Exception ignored) {
            }
        });
        box.addView(appSettings, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        setContentView(box);
    }

    private void openWebViewStore() {
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=com.google.android.webview")));
        } catch (Exception first) {
            try {
                startActivity(new Intent(Intent.ACTION_VIEW,
                        Uri.parse("https://play.google.com/store/apps/details?id=com.google.android.webview")));
            } catch (Exception ignored) {
            }
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == FILE_CHOOSER_CODE) {
            if (fileCallback == null) return;
            fileCallback.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(resultCode, data));
            fileCallback = null;
            return;
        }
        if (requestCode == VOICE_CODE && resultCode == RESULT_OK && data != null) {
            ArrayList<String> results = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
            if (results != null && !results.isEmpty()) {
                js("window.CyberMentorNative&&window.CyberMentorNative.onVoiceResult(" +
                        JSONObject.quote(results.get(0)) + ")");
            }
        }
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    @Override
    protected void onDestroy() {
        mainHandler.removeCallbacks(startupWatchdog);
        if (tts != null) {
            try {
                tts.stop();
                tts.shutdown();
            } catch (Exception ignored) {
            }
        }
        executor.shutdownNow();
        if (webView != null) {
            try {
                webView.removeJavascriptInterface("AndroidAI");
                webView.stopLoading();
                webView.destroy();
            } catch (Exception ignored) {
            }
        }
        super.onDestroy();
    }

    @Override
    public void onInit(int status) {
        if (status == TextToSpeech.SUCCESS && tts != null) tts.setLanguage(Locale.US);
    }

    private void js(String script) {
        runOnUiThread(() -> {
            if (webView != null && !isFinishing()) {
                try {
                    webView.evaluateJavascript(script, null);
                } catch (Throwable t) {
                    Log.w(TAG, "JavaScript bridge call failed", t);
                }
            }
        });
    }

    private static String readBody(HttpURLConnection connection, boolean error) throws Exception {
        InputStream stream = error ? connection.getErrorStream() : connection.getInputStream();
        if (stream == null) return "";
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8))) {
            StringBuilder out = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) out.append(line).append('\n');
            return out.toString().trim();
        }
    }

    private void post(String id, String endpoint, String bearer, String payload) {
        executor.submit(() -> {
            HttpURLConnection connection = null;
            try {
                connection = (HttpURLConnection) new URL(endpoint).openConnection();
                connection.setRequestMethod("POST");
                connection.setConnectTimeout(30000);
                connection.setReadTimeout(180000);
                connection.setDoOutput(true);
                connection.setRequestProperty("Content-Type", "application/json");
                connection.setRequestProperty("Accept", "application/json");
                connection.setRequestProperty("User-Agent", "CyberMentorAI-Android/3.3");
                if (bearer != null && !bearer.trim().isEmpty()) {
                    connection.setRequestProperty("Authorization", "Bearer " + bearer);
                }
                byte[] bytes = payload.getBytes(StandardCharsets.UTF_8);
                connection.setFixedLengthStreamingMode(bytes.length);
                try (OutputStream os = connection.getOutputStream()) {
                    os.write(bytes);
                }
                int code = connection.getResponseCode();
                String body = readBody(connection, code >= 400);
                JSONObject envelope = new JSONObject();
                envelope.put("status", code);
                envelope.put("body", body);
                js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult(" +
                        JSONObject.quote(id) + "," + (code >= 200 && code < 300) + "," +
                        JSONObject.quote(envelope.toString()) + ")");
            } catch (Exception e) {
                js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult(" +
                        JSONObject.quote(id) + ",false," + JSONObject.quote(e.getMessage()) + ")");
            } finally {
                if (connection != null) connection.disconnect();
            }
        });
    }

    private String bestOpenAIModel(String apiKey) throws Exception {
        HttpURLConnection connection = null;
        try {
            connection = (HttpURLConnection) new URL(OPENAI_MODELS_ENDPOINT).openConnection();
            connection.setConnectTimeout(20000);
            connection.setReadTimeout(30000);
            connection.setRequestProperty("Accept", "application/json");
            connection.setRequestProperty("Authorization", "Bearer " + apiKey);
            connection.setRequestProperty("User-Agent", "CyberMentorAI-Android/3.3");
            int code = connection.getResponseCode();
            String body = readBody(connection, code >= 400);
            if (code < 200 || code >= 300) {
                throw new Exception("OpenAI models HTTP " + code + ": " + body);
            }

            org.json.JSONArray models = new JSONObject(body).optJSONArray("data");
            if (models == null || models.length() == 0) throw new Exception("No models available for this API project");

            java.util.HashSet<String> available = new java.util.HashSet<>();
            for (int i = 0; i < models.length(); i++) {
                JSONObject item = models.optJSONObject(i);
                if (item != null) available.add(item.optString("id", ""));
            }

            // Prefer current general-purpose Responses models in capability order.
            // Only a model actually returned by this API project can be selected.
            String[] preferred = new String[] {
                    "gpt-6-astra",
                    "gpt-6-sol",
                    "gpt-6-luna",
                    "gpt-5.6",
                    "gpt-5.6-sol",
                    "gpt-5.6-terra",
                    "gpt-5.6-luna"
            };
            for (String candidate : preferred) {
                if (available.contains(candidate)) return candidate;
            }

            // Fallback for projects exposing another GPT text model.
            String best = "";
            int bestMajor = -1, bestMinor = -1, bestTier = -1;
            java.util.regex.Pattern pattern = java.util.regex.Pattern.compile("gpt-(\\d+)(?:\\.(\\d+))?");
            for (String id : available) {
                String low = id.toLowerCase(Locale.ROOT);
                if (!id.startsWith("gpt-") ||
                        low.contains("audio") || low.contains("image") || low.contains("realtime") ||
                        low.contains("transcribe") || low.contains("tts") || low.contains("embedding") ||
                        low.contains("search") || low.contains("moderation") || low.contains("cyber") ||
                        low.contains("daybreak") || low.contains("instruct")) continue;

                java.util.regex.Matcher matcher = pattern.matcher(id);
                int major = 0, minor = 0;
                if (matcher.find()) {
                    major = Integer.parseInt(matcher.group(1));
                    if (matcher.group(2) != null) minor = Integer.parseInt(matcher.group(2));
                }
                int tier = low.contains("astra") ? 4 :
                        (low.contains("sol") ? 3 :
                        (low.contains("terra") ? 2 :
                        (low.contains("luna") ? 1 : 2)));
                if (major > bestMajor ||
                        (major == bestMajor && minor > bestMinor) ||
                        (major == bestMajor && minor == bestMinor && tier > bestTier) ||
                        (major == bestMajor && minor == bestMinor && tier == bestTier && id.compareTo(best) > 0)) {
                    best = id;
                    bestMajor = major;
                    bestMinor = minor;
                    bestTier = tier;
                }
            }
            if (best.isEmpty()) throw new Exception("No compatible GPT text model is available for this API project");
            return best;
        } finally {
            if (connection != null) connection.disconnect();
        }
    }

    private void postOpenAI(String id, String apiKey, JSONObject originalRequest) {
        executor.submit(() -> {
            JSONObject request;
            try {
                request = new JSONObject(originalRequest.toString());
            } catch (Exception e) {
                js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult(" +
                        JSONObject.quote(id) + ",false," + JSONObject.quote("Invalid request: " + e.getMessage()) + ")");
                return;
            }

            boolean reasoningRetried = false;
            boolean modelRetried = false;
            boolean transientRetried = false;

            for (int attempt = 0; attempt < 4; attempt++) {
                HttpURLConnection connection = null;
                try {
                    connection = (HttpURLConnection) new URL(OPENAI_ENDPOINT).openConnection();
                    connection.setRequestMethod("POST");
                    connection.setConnectTimeout(30000);
                    connection.setReadTimeout(180000);
                    connection.setDoOutput(true);
                    connection.setRequestProperty("Content-Type", "application/json");
                    connection.setRequestProperty("Accept", "application/json");
                    connection.setRequestProperty("Authorization", "Bearer " + apiKey);
                    connection.setRequestProperty("User-Agent", "CyberMentorAI-Android/3.3");

                    byte[] bytes = request.toString().getBytes(StandardCharsets.UTF_8);
                    connection.setFixedLengthStreamingMode(bytes.length);
                    try (OutputStream os = connection.getOutputStream()) {
                        os.write(bytes);
                    }

                    int code = connection.getResponseCode();
                    String body = readBody(connection, code >= 400);
                    if (code >= 200 && code < 300) {
                        JSONObject envelope = new JSONObject();
                        envelope.put("status", code);
                        envelope.put("body", body);
                        js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult(" +
                                JSONObject.quote(id) + ",true," + JSONObject.quote(envelope.toString()) + ")");
                        return;
                    }

                    String low = body == null ? "" : body.toLowerCase(Locale.ROOT);

                    // If a model/account rejects a reasoning option, retry once with the provider default.
                    if (!reasoningRetried && code == 400 && request.has("reasoning") &&
                            (low.contains("reasoning") || low.contains("effort"))) {
                        reasoningRetried = true;
                        request.remove("reasoning");
                        js("window.CyberMentorNative&&window.CyberMentorNative.onAutoRecovery(" +
                                JSONObject.quote("Reasoning setting was reset automatically for model compatibility.") + ")");
                        continue;
                    }

                    // If a stored/manual model became unavailable, recover to the best model currently exposed.
                    if (!modelRetried && (code == 400 || code == 404) &&
                            (low.contains("model") || low.contains("unsupported"))) {
                        modelRetried = true;
                        String fallback = bestOpenAIModel(apiKey);
                        if (!fallback.equals(request.optString("model", ""))) {
                            request.put("model", fallback);
                            request.remove("reasoning");
                            js("window.CyberMentorNative&&window.CyberMentorNative.onAutoModel(" +
                                    JSONObject.quote(fallback) + ")");
                            js("window.CyberMentorNative&&window.CyberMentorNative.onAutoRecovery(" +
                                    JSONObject.quote("Model routing was repaired automatically. Retrying with " + fallback + ".") + ")");
                            continue;
                        }
                    }

                    // Retry one transient provider failure; do not retry billing/authentication errors.
                    if (!transientRetried && (code == 500 || code == 502 || code == 503 || code == 504)) {
                        transientRetried = true;
                        try { Thread.sleep(1200L); } catch (InterruptedException ignored) { Thread.currentThread().interrupt(); }
                        continue;
                    }

                    JSONObject envelope = new JSONObject();
                    envelope.put("status", code);
                    envelope.put("body", body == null ? "" : body);
                    js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult(" +
                            JSONObject.quote(id) + ",false," + JSONObject.quote(envelope.toString()) + ")");
                    return;
                } catch (Exception e) {
                    if (!transientRetried) {
                        transientRetried = true;
                        try { Thread.sleep(800L); } catch (InterruptedException ignored) { Thread.currentThread().interrupt(); }
                        continue;
                    }
                    js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult(" +
                            JSONObject.quote(id) + ",false," + JSONObject.quote("NETWORK_ERROR: " + e.getMessage()) + ")");
                    return;
                } finally {
                    if (connection != null) connection.disconnect();
                }
            }

            js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult(" +
                    JSONObject.quote(id) + ",false,'REQUEST_RETRY_EXHAUSTED')");
        });
    }

    private void get(String id, String endpoint, String bearer, String callback) {
        executor.submit(() -> {
            HttpURLConnection connection = null;
            try {
                connection = (HttpURLConnection) new URL(endpoint).openConnection();
                connection.setConnectTimeout(20000);
                connection.setReadTimeout(40000);
                connection.setRequestProperty("Accept", "application/json");
                connection.setRequestProperty("User-Agent", "CyberMentorAI-Android/3.3");
                if (bearer != null && !bearer.trim().isEmpty()) {
                    connection.setRequestProperty("Authorization", "Bearer " + bearer);
                }
                int code = connection.getResponseCode();
                String body = readBody(connection, code >= 400);
                js("window.CyberMentorNative&&window.CyberMentorNative." + callback + "(" +
                        JSONObject.quote(id) + "," + (code >= 200 && code < 300) + "," +
                        JSONObject.quote(body) + ")");
            } catch (Exception e) {
                js("window.CyberMentorNative&&window.CyberMentorNative." + callback + "(" +
                        JSONObject.quote(id) + ",false," + JSONObject.quote(e.getMessage()) + ")");
            } finally {
                if (connection != null) connection.disconnect();
            }
        });
    }

    private SecretKey getOrCreateKey() throws Exception {
        KeyStore keyStore = KeyStore.getInstance("AndroidKeyStore");
        keyStore.load(null);
        if (keyStore.containsAlias(KEY_ALIAS)) {
            return ((KeyStore.SecretKeyEntry) keyStore.getEntry(KEY_ALIAS, null)).getSecretKey();
        }
        KeyGenerator generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
        generator.init(new KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT
        ).setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .build());
        return generator.generateKey();
    }

    private void resetStoredKey() {
        getSharedPreferences(PREFS, MODE_PRIVATE).edit().remove(PREF_KEY).commit();
        try {
            KeyStore keyStore = KeyStore.getInstance("AndroidKeyStore");
            keyStore.load(null);
            if (keyStore.containsAlias(KEY_ALIAS)) keyStore.deleteEntry(KEY_ALIAS);
        } catch (Exception ignored) {
        }
    }

    private void saveKey(String raw) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, getOrCreateKey());
        String packed = Base64.encodeToString(cipher.getIV(), Base64.NO_WRAP) + ":" +
                Base64.encodeToString(cipher.doFinal(raw.getBytes(StandardCharsets.UTF_8)), Base64.NO_WRAP);
        if (!getSharedPreferences(PREFS, MODE_PRIVATE).edit().putString(PREF_KEY, packed).commit()) {
            throw new IllegalStateException("Secure storage write failed");
        }
    }

    private String loadKey() throws Exception {
        String packed = getSharedPreferences(PREFS, MODE_PRIVATE).getString(PREF_KEY, null);
        if (packed == null || packed.trim().isEmpty()) return null;
        String[] parts = packed.split(":", 2);
        if (parts.length != 2) throw new IllegalStateException("Stored key format is invalid");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(
                Cipher.DECRYPT_MODE,
                getOrCreateKey(),
                new GCMParameterSpec(128, Base64.decode(parts[0], Base64.NO_WRAP))
        );
        return new String(cipher.doFinal(Base64.decode(parts[1], Base64.NO_WRAP)), StandardCharsets.UTF_8);
    }

    public final class NativeBridge {
        private final Context context;

        NativeBridge(Context context) {
            this.context = context;
        }

        @JavascriptInterface
        public void reportUiReady() {
            runOnUiThread(MainActivity.this::markUiReady);
        }

        @JavascriptInterface
        public void toast(String msg) {
            runOnUiThread(() -> Toast.makeText(context, msg == null ? "" : msg, Toast.LENGTH_SHORT).show());
        }

        @JavascriptInterface
        public boolean hasApiKey() {
            try {
                return loadKey() != null;
            } catch (Exception e) {
                Log.w(TAG, "Stored API key could not be read; clearing corrupted key", e);
                resetStoredKey();
                return false;
            }
        }

        @JavascriptInterface
        public String saveApiKey(String key) {
            if (key == null || key.trim().length() < 20) return "Invalid key";
            try {
                saveKey(key.trim());
                return "OK";
            } catch (Exception first) {
                Log.w(TAG, "Secure key save failed; rebuilding keystore entry", first);
                try {
                    resetStoredKey();
                    saveKey(key.trim());
                    return "OK";
                } catch (Exception second) {
                    Log.e(TAG, "Secure key save failed after recovery", second);
                    return "Save failed: secure storage is unavailable";
                }
            }
        }

        @JavascriptInterface
        public void clearApiKey() {
            resetStoredKey();
        }

        @JavascriptInterface
        public void chat(String id, String payload) {
            executor.submit(() -> {
                try {
                    String key;
                    try {
                        key = loadKey();
                    } catch (Exception storageError) {
                        resetStoredKey();
                        key = null;
                    }
                    if (key == null) {
                        js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult(" +
                                JSONObject.quote(id) + ",false,'SETUP_REQUIRED')");
                        return;
                    }
                    JSONObject request = new JSONObject(payload);
                    request.remove("provider");
                    String model = request.optString("model", "").trim();
                    if (model.isEmpty()) {
                        model = bestOpenAIModel(key);
                        request.put("model", model);
                        js("window.CyberMentorNative&&window.CyberMentorNative.onAutoModel(" +
                                JSONObject.quote(model) + ")");
                    }
                    postOpenAI(id, key, request);
                } catch (Exception e) {
                    js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult(" +
                            JSONObject.quote(id) + ",false," + JSONObject.quote(e.getMessage()) + ")");
                }
            });
        }

        @JavascriptInterface
        public void backendChat(String id, String base, String token, String payload) {
            if (base == null ||
                    (!base.startsWith("https://") &&
                    !base.startsWith("http://127.0.0.1") &&
                    !base.startsWith("http://localhost"))) {
                js("window.CyberMentorNative&&window.CyberMentorNative.onApiResult(" +
                        JSONObject.quote(id) + ",false,'Backend must use HTTPS or localhost')");
                return;
            }
            post(id, base.endsWith("/") ? base + "api/chat" : base + "/api/chat", token, payload);
        }

        @JavascriptInterface
        public void startVoice() {
            runOnUiThread(() -> {
                Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
                try {
                    startActivityForResult(intent, VOICE_CODE);
                } catch (Exception e) {
                    Toast.makeText(context, "Speech recognition is unavailable", Toast.LENGTH_SHORT).show();
                }
            });
        }

        @JavascriptInterface
        public void speak(String text) {
            if (text == null || text.trim().isEmpty()) return;
            runOnUiThread(() -> {
                if (tts == null) {
                    tts = new TextToSpeech(MainActivity.this, status -> {
                        if (status == TextToSpeech.SUCCESS && tts != null) {
                            tts.setLanguage(Locale.US);
                            tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "cm");
                        }
                    });
                } else {
                    tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "cm");
                }
            });
        }

        @JavascriptInterface
        public void shareText(String title, String text) {
            runOnUiThread(() -> {
                Intent intent = new Intent(Intent.ACTION_SEND);
                intent.setType("text/plain");
                intent.putExtra(Intent.EXTRA_SUBJECT, title);
                intent.putExtra(Intent.EXTRA_TEXT, text);
                startActivity(Intent.createChooser(intent, "Share"));
            });
        }

        @JavascriptInterface
        public String appVersion() {
            try {
                return context.getPackageManager().getPackageInfo(context.getPackageName(), 0).versionName;
            } catch (Exception e) {
                return "unknown";
            }
        }

        @JavascriptInterface
        public void refreshOpenAIModels(String id) {
            try {
                String key = loadKey();
                if (key == null) {
                    js("window.CyberMentorNative&&window.CyberMentorNative.onModelCatalog(" +
                            JSONObject.quote(id) + ",false,'No API key saved')");
                    return;
                }
                get(id, OPENAI_MODELS_ENDPOINT, key, "onModelCatalog");
            } catch (Exception e) {
                resetStoredKey();
                js("window.CyberMentorNative&&window.CyberMentorNative.onModelCatalog(" +
                        JSONObject.quote(id) + ",false,'Saved API key could not be read')");
            }
        }

        @JavascriptInterface
        public void fetchCyberFeed(String id) {
            get(id, FEED_ENDPOINT, null, "onCyberFeed");
        }

        @JavascriptInterface
        public void checkForUpdates(String id) {
            get(id, RELEASE_ENDPOINT, null, "onUpdateInfo");
        }

        @JavascriptInterface
        public void openUrl(String url) {
            runOnUiThread(() -> {
                try {
                    Uri uri = Uri.parse(url);
                    if ("https".equalsIgnoreCase(uri.getScheme())) {
                        startActivity(new Intent(Intent.ACTION_VIEW, uri));
                    }
                } catch (Exception ignored) {
                }
            });
        }

        @JavascriptInterface
        public void openApiKeyPage() {
            runOnUiThread(() -> {
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://platform.openai.com/api-keys")));
                } catch (Exception e) {
                    Toast.makeText(context, "No browser is available", Toast.LENGTH_SHORT).show();
                }
            });
        }

        @JavascriptInterface
        public void openApiBillingPage() {
            runOnUiThread(() -> {
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW,
                            Uri.parse("https://platform.openai.com/settings/organization/billing/overview")));
                } catch (Exception e) {
                    Toast.makeText(context, "No browser is available", Toast.LENGTH_SHORT).show();
                }
            });
        }


        @JavascriptInterface
        public void openAppSettings() {
            runOnUiThread(() -> {
                Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
                intent.setData(Uri.parse("package:" + getPackageName()));
                startActivity(intent);
            });
        }
    }
}
