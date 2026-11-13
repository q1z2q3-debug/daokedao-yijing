---
title: "把 50 万字古籍做成 3 MB 安卓阅读器：一条从 Markdown 到 APK 的流水线"
published: false
description: "不用 Gradle、不装 Android Studio：一份 Markdown 母本，派生阅读页、704 页 PDF、零权限 APK 与 70 个可检索页面。踩过的坑与能抄的代码。"
tags: opensource, android, webdev, chinese
canonical_url: https://q1z2q3-debug.github.io/daokedao-yijing/
---

写了一部《周易》的读本，收工时是 72 卷、50.5 万字、A4 排版 704 页。到这一步，「它讲了什么」已经不是最难的问题，「别人怎么读到它」才是——在地铁上、在没网的地方、在手机上。

仓库：[q1z2q3-debug/daokedao-yijing](https://github.com/q1z2q3-debug/daokedao-yijing)　在线阅读：[q1z2q3-debug.github.io/daokedao-yijing](https://q1z2q3-debug.github.io/daokedao-yijing/)

## 一个源，四件产物

规矩只有一条：**HTML 是唯一成品，其余都从它派生。**

| 产物 | 做法 | 体量 |
|---|---|---|
| 阅读页 | Markdown → pandoc → 单文件 HTML | 1.75 MB |
| 成书 PDF | Chromium 打印，分段后合并 | 29 MB／704 页 |
| 离线包 | 同一个 HTML 塞进 WebView 壳 | 3.0 MB APK |
| 检索站 | 由同一个 HTML 拆成 70 页 | 4.5 MB |

APK 不是第二套实现，它就是那个文件加字体内嵌。

## 第一步：让 HTML 真的能离线

原页面从 CDN 取字体，联网没事，飞行模式就是一片宋体缺失。构建时改成内嵌子集：

```bash
pyftsubset NotoSerifSC-Regular.otf \
  --text-file=charset.txt \
  --unicodes="U+4DC0-4DFF,U+2630-2640" \
  --flavor=woff2 --layout-features='*'
```

两处值得抄：

- **字符集从正文里扫，不靠猜。** 全书实际用字 3,100 个，两个字重压缩后约 2.5 MB；换成完整 CJK 字体就是 20 MB。
- **别漏符号区段。** 卦符 `䷀`—`䷿` 在 U+4DC0–U+4DFF，三爻符号 `☰`—`☷` 在 U+2630–U+2640，都**不在** CJK 统一汉字区。按 `\u4e00-\u9fff` 取字集，这些字全变豆腐块。

结果：文件里**外链清零**，字体 base64 内嵌，1.75 MB，断网可开。

## 第二步：不上 Gradle 也能出 APK

环境里没有 Android Studio，而一个 WebView 壳本来也不需要它。六步：

```
aapt2 compile  → res.zip
aapt2 link     → 资源 + R.java + assets + manifest
javac          → classes
d8             → classes.dex
zipalign       → 4 字节对齐
apksigner      → v1/v2/v3
```

两个坑：

1. **`platform-34_r03.zip` 是 404。** `build-tools_r34-linux.zip` 正常，配对的 platform 包已经下架；改用 `platform-35_r02.zip` 取 `android.jar`，manifest 里 `targetSdk 34`，没问题。
2. **手机版式要用手机视口验，不是窄桌面窗口。** Chromium `--window-size=420` 不认 `<meta name="viewport">`，页面按桌面宽度渲染，右边被裁掉——一个假溢出。Playwright 用 `is_mobile=True` 复核，`scrollWidth == 390`，其实一点没溢出。差点去改一段本来就对的 CSS。

manifest 里**零权限**，连 `INTERNET` 都没有：

```xml
<uses-permission android:name="android.permission.INTERNET" /> <!-- 删掉 -->
```

壳里再加 `setBlockNetworkLoads(true)`，正文里就算混进一个 `<img>` 也发不出去。`versionCode 15000` 对应 `1.50.0`，下一版 `15100`，同一签名密钥可直接覆盖安装。

## 第三步：一本书拆成 70 页，因为单个大页面谁也搜不到

如果只发一个 1.75 MB 的整书页：只有一个 `<title>`、没有 description、没有 canonical，「未济卦 解读」这种长尾词一个也接不住。

于是站点构建按 `<h1>` 切分同一份 HTML，逐段套模板：

- `/p/64-weiji/` —— 每卦一个目录，独立 canonical，描述取本段开头的卷眼（50–75 字）
- 上一卦／下一卦链接，爬虫从任何一页都能走通全链
- `sitemap.xml`（72 条）、`robots.txt`、`llms.txt`（给 AI 爬虫的纯文本摘要）
- JSON-LD：每页 `Article`，首页 `Book` + `hasPart`
- 一张 1200×630 分享图，用 Pillow 确定性生成，不用手搓

生成器约 250 行 Python，一秒跑完：

```bash
python3 scripts/build-site.py   # 70 页 + sitemap + robots + llms.txt
```

两条后见之明：

- **描述从正文取，不要拼标题。** 第一版把标题、署名、首段拼在一起，产出 `第 64 卦：未济。下 经｜未济 润泽说易 到不了岸…` 这种垃圾；改取卷眼就干净了。
- **生成器要进仓库。** 页面是构建产物，源一动，站点应该一条命令就重新正确，而不是一个手改过的 HTML 文件夹。

## 第四步：发版

GitHub 附件有几个脾气：

- **非 ASCII 文件名会被洗掉。** `道可道-易传-1.50.0.apk` 传上去变成 `-.-1.50.0.apk`。附件名一律 ASCII，中文标题放 release 正文。
- **上传要带 `Accept: application/vnd.github+json`**，否则 `uploads.github.com` 回一个 HTML 400，什么也不说。
- 打 `v*` tag 的 workflow 会自动挂上 PDF、APK 与提示词 PDF，发版就是打一个 tag。

## 给同类项目的话

1. 选一件产物当唯一真相，其余全部派生。书、PDF、APK 分开维护，两版之内必然打架。
2. 字体子集从真实语料扫，符号区段单独补。
3. 长文本要拆页、要有描述；一个巨页在搜索结果里等于不存在。
4. 零权限是优点。一个连不上网的阅读器，也就泄不了任何东西——用户是看得见的。

书是 CC BY-NC-SA 4.0。APK 在 [releases](https://github.com/q1z2q3-debug/daokedao-yijing/releases/latest)，3 MB，无权限，飞行模式可用。
