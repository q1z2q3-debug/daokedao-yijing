# 道可道·易传 阅读器 APK · v1.50.0

离线阅读《润泽说 道可道之易传》v1.50.0 全本（72 卷：总序、前言、凡例、目录、系辞上、系辞下、附录、六十三卦卷、后记、封底）。

| 项 | 值 |
|---|---|
| 包名 | `com.daokedao.yijing` |
| 版本 | versionName 1.50.0 / versionCode 15000 |
| minSdk / targetSdk | 21 / 34 |
| 权限 | **无**（不申请 INTERNET，完全离线） |
| 内容 | 单文件阅读页 1,750,553 B ＋ 思源宋体子集 2 字重（3,100 用字，另含 ䷀—䷿ 卦符与八卦符号） |
| 体积 | 3,126,298 B |
| 证书 SHA-256 | `2B:DC:24:68:38:52:14:BD:D3:A7:D9:35:0E:59:06:95:4F:62:6E:32:B9:0D:3F:A5:E2:B2:19:74:A8:5A:6C:EA`（与道德经 APK 同一密钥，便于同系列共存升级） |

## 安装

手机允许「安装未知来源应用」后点开即装。与《道可道》道德经 APK **包名不同，可并存**，桌面显示为「道可道·易传」。

断网可用；字体已内置；退出时记住读到哪儿，下次接着读；返回键退回上一处目录跳转。

## 重建

    cd apk-yijing
    python3 prepare-assets.py                      # 由最新全本阅读页生成 assets 并子集化字体
    SDK=/tmp/apkbuild BUILD_TOOLS=/tmp/apkbuild/android-14 \
      JAVA_HOME=/tmp/apkbuild/jdk-11.0.33+10 bash build.sh

工具链与道德经 APK 同一条链：build-tools 34（`aapt2`／`d8`／`zipalign`／`apksigner`）、platform-35 的 `android.jar`、JDK 11。签名密钥不入库，放 `~/.daokedao-vault/`（`apk-signing.jks` ＋ `apk-signing.pass`）。

## 校验

    sha256sum -c SHA256SUMS

## 与 v1.0.0 旧包的关系

`packages/v1.0.0`（道德经）与 `packages/v2.3.0`（道德经）为另一部书；本包为易传首包，故不存在升级冲突。
