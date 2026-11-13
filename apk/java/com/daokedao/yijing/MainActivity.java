package com.daokedao.yijing;

import android.app.Activity;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/**
 * 单页阅读壳：把 assets/book.html（《润泽说 道可道之易传》v1.50.0 阅读页）
 * 装进一个不联网、不申请权限的窗口里读。
 *
 * 只做三件事：
 *   1. 全离线加载（assets 内置正文字体，无任何网络请求）
 *   2. 记住读到哪儿（退出时存滚动位置，下次接着读）
 *   3. 返回键退回上一处目录跳转
 */
public class MainActivity extends Activity {

    private static final String ASSET_URL = "file:///android_asset/book.html";
    private static final int PAPER = 0xFFF4F1EA;

    private WebView web;
    private SharedPreferences sp;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        sp = getSharedPreferences("reader", MODE_PRIVATE);

        web = new WebView(this);
        web.setBackgroundColor(PAPER);
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowFileAccessFromFileURLs(false);
        s.setAllowUniversalAccessFromFileURLs(false);
        s.setBlockNetworkLoads(true);   // 全书离线，拒绝任何网络加载
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setTextZoom(100);
        s.setCacheMode(WebSettings.LOAD_NO_CACHE);

        web.setWebViewClient(new WebViewClient());
        web.setBackgroundColor(PAPER);
        setContentView(web);
        web.loadUrl(ASSET_URL);

        final int savedY = sp.getInt("scrollY", 0);
        if (savedY > 0) {
            web.postDelayed(new Runnable() {
                @Override
                public void run() {
                    web.scrollTo(0, savedY);
                }
            }, 600);
        }
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && web != null && web.canGoBack()) {
            web.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (web != null && sp != null) {
            sp.edit().putInt("scrollY", web.getScrollY()).apply();
        }
    }

    @Override
    protected void onDestroy() {
        if (web != null) {
            web.setVisibility(View.GONE);
            web.destroy();
            web = null;
        }
        super.onDestroy();
    }
}
