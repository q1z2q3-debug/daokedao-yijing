# 易传 APK 构建链

把 `../yijing/book/润泽说 道可道之易传.html`（v1.50.0 阅读页）打成离线安装包。
与 `../apk/`（道德经线）同一条链，只是包名、应用名、字体命名不同。

| 文件 | 作用 |
|---|---|
| `prepare-assets.py` | 把外链字体换成本地 `@font-face`，再用系统 Noto Serif CJK 子集化出 3,100 用字的两个字重 |
| `build.sh` | aapt2 编译／链接 → javac → d8 → zipalign → apksigner（六步） |
| `AndroidManifest.xml` | `com.daokedao.yijing`，零权限，target 34 |
| `java/com/daokedao/yijing/MainActivity.java` | 单页 WebView 壳：离线、断网、记住滚动位置、返回键回目录 |
| `res/` | 纸色主题（`#F4F1EA`）＋ 五档图标 |

产物：`dist/道可道-易传-1.50.0.apk`（3,126,298 B），入库副本在 `../packages/apk-1.50.0-yijing/`。

## 重建

    python3 prepare-assets.py
    SDK=/tmp/apkbuild BUILD_TOOLS=/tmp/apkbuild/android-14 \
      JAVA_HOME=/tmp/apkbuild/jdk-11.0.33+10 bash build.sh

`assets/`、`build/`、`dist/` 均不入库（已在 `.gitignore`），可由上面两条命令重建。

## 换版号

改三处：`AndroidManifest.xml` 的 `versionCode`／`versionName`，`build.sh` 的 `VERCODE`／`VERNAME`。
versionCode 建议 `易传版本号×10000`（1.50.0 → 15000），与道德经的 `×10000` 口径一致。
