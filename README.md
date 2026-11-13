# 润泽说 道可道之易传

《周易》六十四卦与《系辞》上下篇的**完整读本**：一本可印制、可讲习、可在手机上离线读的书。

**全书 72 卷／约 50.5 万字**：总序、前言、凡例、目录、系辞上、系辞下、附录（忧患九卦详释）、六十三卦卷（乾、坤合一卷，上经三十卦至下经三十四卦）、后记、封底。

> 这本书的全部工作，在于**把每个关键字还原到先秦的字形与字义，再让这些字自己把这一卦讲出来**。它不取象数占验，也不做空谈义理；象是载体，理是内核，落脚点是「人如何自处」。

---

## 一、体例：一卦一卷，七节同构

每卦固定七节，次序不动：

| 节 | 做什么 |
|---|---|
| 一、经文底本 | 卦辞、爻辞、《彖》《象》全文；王弼本为正文，参《周易正义》《周易本义》《周易集解》，马王堆帛书作异文 |
| 二、时代社会背景 | 这一卦在什么处境里成形，它要解决什么问题 |
| 三、关键字造字溯源 | 先看字怎么造，再看先秦怎么用，最后看它指向哪片实相（四层分开，不把汉人训释冒充甲骨本义） |
| 四、逐爻深解，兼通老庄 | 六爻逐爻：译／易／老子／庄子 四层＋《象》辞深读 |
| 五、体系联动 | 与综卦、错卦、互卦、前后卦的关系；近几卷常带副题 |
| 六、合与和 | 落到全书主线：人为之合／天道之和 |
| 七、常见误读 | 逐条校正通行误读（不属前六节之数） |

卷首为卷眼引语一句，卷末为「**下一卦X。**」与右署「—— 润泽说易」。

## 二、文件在哪

| 文件 | 用途 | 体量 |
|---|---|---|
| [`book/润泽说 道可道之易传.md`](book/润泽说%20道可道之易传.md) | **主本**。72 卷全，Markdown 母本，可印制、可 diff、可再加工 | 约 50.5 万非空白字 |
| [`book/润泽说 道可道之易传.html`](book/润泽说%20道可道之易传.html) | **阅读页**。单文件，版式与交互全内联，可离线打开 | 1.7 MB |
| [`book/润泽说 道可道之易传.pdf`](book/润泽说%20道可道之易传.pdf) | **成书 PDF**。A4／704 页，分段打印后合并，无空页 | 29 MB |
| [`packages/apk-1.50.0-yijing/`](packages/apk-1.50.0-yijing/) | **安卓离线包**。零权限、断网可用、字体内置 | 3.0 MB |
| [`book/润泽说 道可道之易传·投来稿清排本.md`](book/润泽说%20道可道之易传·投来稿清排本.md) | **原稿清排**。只收投来原话，只排版不增补，供对照追溯 | 25 卷 |
| [`prompt/易传篇目检索表.md`](prompt/易传篇目检索表.md) | 63 卦卷速查＋全书凡例索引（「全书几见」类断言的唯一依据） | — |
| [`prompt/润泽说·易传问答Agent（系统提示词）.md`](prompt/润泽说·易传问答Agent（系统提示词）.md) | 问答 Agent 口径：二十五条不可移动的判断＋十二条规则 | — |
| [`archive/tougao/`](archive/tougao/) | 投来稿存档。规矩三条：一字不改／收到即落盘／不补造 | 25 卷 |

主本是「解」，清排本是「稿」，检索表是「索引」，提示词是「口径」——四件各管一件事，不要互相替代。

## 三、在线读

站点：<https://q1z2q3-debug.github.io/daokedao-yijing/>

```
/                     首页：全书结构、四件产物入口、六十四卦索引
/book.html            全书一页（1.75 MB，单文件自包含）
/p/01-qian-kun/ …     逐卦页 70 个：每卦一个 canonical、独立 description、上下卦链接
/p/xici-shang/ 等     系辞上／下、忧患九卦、总序、前言、凡例、后记
/sitemap.xml          72 条
/robots.txt  /llms.txt
```

站点由脚本生成，不手改页面：

```bash
bash scripts/build.sh        # 主本 md → 阅读页 html（pandoc）
python3 scripts/build-site.py  # 阅读页 → docs/ 全站 + sitemap + robots + llms.txt
```

`docs/` 是构建产物，源头永远是 `book/…md`；改了正文就重跑上面两条，别就地编辑 HTML。

## 四、离线读

安卓：下载 `道可道-易传-1.50.0.apk` 安装。包名 `com.daokedao.yijing`，target 34，**不申请任何权限（无 INTERNET）**，正文与思源宋体子集全部内置，断网可读，退出记住位置；与《道可道》道德经 APK 包名不同，可并存。

自己重建：

    cd apk
    python3 prepare-assets.py
    SDK=/tmp/apkbuild BUILD_TOOLS=/tmp/apkbuild/android-14 \
      JAVA_HOME=/tmp/apkbuild/jdk-11.0.33+10 bash build.sh

## 五、改一个字，要动四处

本书按「版本即事实」维护，任何改动都走同一条流水线：

```
改主稿 md → 重建 html → 打印 pdf → 同步检索表与提示词
         → CHANGELOG → VERSION → releases/ 冻结（SHA-256 清单）
         → commit → tag → push
```

`releases/vX/` 里是当版冻结件与 `MANIFEST.sha256`；`CHANGELOG.md` 是逐版校订留痕（最新在最上），每一处改动都注明依据与落点。校验：

    cd releases/v1.50.0 && sha256sum -c MANIFEST.sha256

## 六、三本一条线

本库是《道可道》系列的第三部。三本共用一条判断——**万物皆客，你我皆自主**；各管一段：

| 书 | 管什么 | 落点 |
|---|---|---|
| 《道德经》 | 取景：无与有是两副取景，妙与徼是同一道体的两面 | 道为根，朴、无、知止 |
| 《庄子》 | 谁在取景：把站在旁边选景的那个人也拆了 | 破执、齐物、逍遥 |
| 《易传》 | 取景的这套工具立不立得住：卦是象，爻是变，辞是言 | 阴阳时位，安身、处事、应变 |

**道是一，而易是一的万千显化。**

## 七、许可

[CC BY-NC-SA 4.0](LICENSE)：署名、非商业、相同方式共享。引用请注明书名与版本号（如「《润泽说 道可道之易传》v1.50.0」）。

## 永久存档与引用

本版已在三处留存，互为备份：

| 位置 | 用途 | 地址 |
|---|---|---|
| Zenodo（DOI） | 学术引用、长期存档 | [10.5281/zenodo.24185930](https://doi.org/10.5281/zenodo.24185930) |
| HuggingFace 数据集 | 全文检索、语料取用 | <https://huggingface.co/datasets/q1z2q3/daokedao-yijing> |
| GitHub Releases | 成书 PDF / APK / 提示词下载 | <https://github.com/q1z2q3-debug/daokedao-yijing/releases/tag/v1.50.0> |

引用格式：

```
润泽说易. (2026). 《润泽说 道可道之易传》(v1.50.0) [Book]. Zenodo.
https://doi.org/10.5281/zenodo.24185930
```

## 八、版本

当前 **v1.50.0**（2026-11-13）。六十四卦已全，卦卷六十三；此后只作修订与勘误，不再新增卦卷。

## 九、镜像与同步状态

| 平台 | 状态 | 说明 |
|---|---|---|
| GitHub 私库（主库） | ✅ 已同步 | 写作与发版在此进行；`releases/` 冻结、`archive/` 存档、CHANGELOG 全留痕 |
| GitHub 公库（本库） | ✅ 已开源 | 公开可 clone；CC BY-NC-SA 4.0 |
| GitHub Pages | ✅ 已上线 | `docs/index.html` 即全书阅读页，手机可直接读 |
| GitHub Release | ✅ 已发布 | v1.50.0 附 PDF／APK／提示词 PDF 三件；打 `v*` tag 时 workflow 自动重建 Release |
| Gitee／GitLab／Codeberg | ⏳ 待配置 | 一键脚本已备：`scripts/mirror.sh gitee`，只需先把带凭据的 remote 加进来 |
| dev.to | ✅ 已发布（英文） | [505,000 Chinese characters, 3 MB APK](https://dev.to/q1z2q3debug/505000-chinese-characters-3-mb-apk-shipping-a-classical-text-as-an-offline-reader-1l3h)：build log，canonical 回指本站；中文稿 `publish/devto-zh.md` 待发 |
| 公众号／知乎／豆瓣 | ⏳ 未做 | 需人工排版与账号，不是镜像能解决的 |

镜像只推 `main` 与版本 tag，不重写历史；失败即停，不吞错误。

## 十、检索（SEO）做了哪些

- 每卦一页、独立 canonical 与 50–75 字描述；描述取自该卷卷眼，不拼标题
- `sitemap.xml` 72 条、`robots.txt`、`llms.txt`
- JSON-LD：逐页 `Article`，首页 `Book` + `hasPart`（六十四章）
- Open Graph／Twitter Card，共用一张 1200×630 分享图 `docs/og.png`
- 仓库 topics：`yijing` `iching` `zhouyi` `chinese-classics` 等

站点上线后可在 Google Search Console／Bing 站长工具提交 `sitemap.xml`（需你用自己账号登录，我无法代填）。
