#!/usr/bin/env python3
"""由主本阅读页生成 SEO 站点：首页、全书页、逐卦页、sitemap、robots、llms.txt。

输入：book/润泽说 道可道之易传.html（单文件阅读页，由 scripts/build.sh 生成）
输出：docs/ 下的静态站（GitHub Pages 直接服务）

用法：python3 scripts/build-site.py
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "book", "润泽说 道可道之易传.html")
DOCS = os.path.join(ROOT, "docs")

SITE = "https://q1z2q3-debug.github.io/daokedao-yijing"
BOOK = "润泽说 道可道之易传"
AUTHOR = "润泽说易"
VER = "v1.50.0"
DESC = ("《周易》六十四卦与《系辞》上下篇的完整读本：72 卷、50.5 万字，一卦一卷、七节同构；"
        "关键字回到先秦字形，逐爻兼通老庄，辨人为之合与天道之和。")

GUAS = """1 乾 qian|2 坤 kun|3 屯 zhun|4 蒙 meng|5 需 xu|6 讼 song|7 师 shi|8 比 bi|9 小畜 xiaoxu|10 履 lv|
11 泰 tai|12 否 pi|13 同人 tongren|14 大有 dayou|15 谦 qian|16 豫 yu|17 随 sui|18 蛊 gu|19 临 lin|20 观 guan|
21 噬嗑 shike|22 贲 bi|23 剥 bo|24 复 fu|25 无妄 wuwang|26 大畜 daxu|27 颐 yi|28 大过 daguo|29 坎 kan|30 离 li|
31 咸 xian|32 恒 heng|33 遁 dun|34 大壮 dazhuang|35 晋 jin|36 明夷 mingyi|37 家人 jiaren|38 睽 kui|39 蹇 jian|40 解 jie|
41 损 sun|42 益 yi|43 夬 guai|44 姤 gou|45 萃 cui|46 升 sheng|47 困 kun|48 井 jing|49 革 ge|50 鼎 ding|
51 震 zhen|52 艮 gen|53 渐 jian|54 归妹 guimei|55 丰 feng|56 旅 lv|57 巽 xun|58 兑 dui|59 涣 huan|60 节 jie|
61 中孚 zhongfu|62 小过 xiaoguo|63 既济 jiji|64 未济 weiji"""

ORDER, PY = [], {}
for chunk in GUAS.replace("\n", "|").split("|"):
    chunk = chunk.strip()
    if not chunk:
        continue
    no, name, py = chunk.split()
    ORDER.append(name)
    PY[name] = "%02d-%s" % (int(no), py)

EXTRA = {
    "总 序": ("zongxu", "总序", "易是一套观化、守分、待时的认知框架，不是卜筮秘册"),
    "前 言": ("qianyan", "前言", "一条主线「合与和」，以及这本书怎么读"),
    "凡 例": ("fanli", "凡例", "底本与校勘、每卦七节、两条标尺、取舍与行文"),
    "上篇｜系辞上": ("xici-shang", "系辞上", "一套占书，怎么被说成一部道书"),
    "下篇｜系辞下": ("xici-xia", "系辞下", "一部讲吉凶的书，自己写着「不可为典要」"),
    "附 录｜忧患九卦详释": ("youhuan-jiugua", "忧患九卦详释", "九个把手，不是九级台阶"),
    "后 记": ("houji", "后记", "吉凶是时位的显相，不是命运的判决"),
}

CSS_EXTRA = """
.bar a{color:var(--ochre);text-decoration:none;border-bottom:1px solid transparent}
.bar a:hover{border-bottom-color:var(--ochre)}
.navend{max-width:40rem;margin:2.4rem auto 4rem;padding:1.2rem 1.5rem 0;border-top:1px solid var(--line);
  display:flex;flex-wrap:wrap;gap:.6rem 1rem;justify-content:space-between;font-size:.92rem}
.navend a{color:var(--ochre);text-decoration:none}
"""

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>{title}</title>
<meta name="description" content="{desc}" />
<link rel="canonical" href="{url}" />
<meta name="robots" content="index,follow,max-image-preview:large" />
<meta name="author" content="{author}" />
<meta property="og:type" content="article" />
<meta property="og:site_name" content="{book}" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{desc}" />
<meta property="og:url" content="{url}" />
<meta property="og:image" content="{site}/og.png" />
<meta property="og:locale" content="zh_CN" />
<meta property="article:published_time" content="2026-11-13" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{title}" />
<meta name="twitter:description" content="{desc}" />
<meta name="twitter:image" content="{site}/og.png" />
<link rel="icon" href="{site}/favicon.svg" />
<script type="application/ld+json">
{jsonld}
</script>
<style>
{css}
{css_extra}
</style>
</head>
<body>
<div class="bar">
  <a class="mark" href="{site}/">润泽说 · 易传</a>
  <a href="{site}/book.html">读全书</a>
</div>
<main id="book">
{body}
</main>
<div class="navend"><div>{prev}</div><div>{nxt}</div></div>
</body>
</html>
"""


def write(path, text):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)


def load():
    s = open(SRC, encoding="utf-8").read()
    style = re.search(r"<style>[\s\S]*?</style>", s).group(0)
    style = style[len("<style>"):-len("</style>")].strip()
    body = s[s.index('<main id="book">') + len('<main id="book">'): s.index("</main>")]
    # 阅读页的浮动进度条固定定位在壳里才成立，分页页一并去掉
    style = style.replace("position:fixed;top:0;left:0;height:2px", "display:none;height:2px")
    return style, body


def split_h1(body):
    marks = [(m.start(), m.end(), html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip())
             for m in re.finditer(r"<h1[^>]*>([\s\S]*?)</h1>", body)]
    out = []
    for i, (a, b, name) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
        out.append((name, body[a:end]))
    return out


def plain(section):
    s = re.sub(r"<blockquote[\s\S]*?</blockquote>",
               lambda m: "「" + re.sub(r"<[^>]+>", "", m.group(0)).strip() + "」", section)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(re.sub(r"\s+", " ", s)).strip()
    return re.sub(r"[「」\"]", "", s)


def meta_desc(section, prefix, tail):
    """描述 = 前缀 + 卷眼 + 统一尾句；卷眼取首条 blockquote，无则取正文首句。"""
    bq = re.search(r"<blockquote>[\s\S]*?</blockquote>", section)
    eye = ""
    if bq:
        eye = re.sub(r"<[^>]+>", "", bq.group(0)).strip()
    else:
        first = re.search(r"<p[^>]*>([\s\S]*?)</p>", re.sub(r"^[\s\S]*?</h1>", "", section))
        if first:
            eye = re.sub(r"<[^>]+>", "", first.group(1)).strip()
    eye = re.sub(r"\s+", " ", html.unescape(eye)).strip("「」")
    if "｜" in prefix:
        return (prefix + "。" + tail)[:152].replace('"', "”")
    d = "%s，%s。%s" % (prefix, eye, tail) if eye else "%s。%s" % (prefix, tail)
    return d[:152].replace('"', "”")



LAND = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>{book}｜周易六十四卦与系辞全本读本（{ver}）</title>
<meta name="description" content="{desc}" />
<link rel="canonical" href="{site}/" />
<meta name="robots" content="index,follow,max-image-preview:large" />
<meta name="author" content="{author}" />
<meta property="og:type" content="book" />
<meta property="og:site_name" content="{book}" />
<meta property="og:title" content="{book}｜周易六十四卦全本读本" />
<meta property="og:description" content="{desc}" />
<meta property="og:url" content="{site}/" />
<meta property="og:image" content="{site}/og.png" />
<meta property="og:locale" content="zh_CN" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{book}｜周易六十四卦全本读本" />
<meta name="twitter:description" content="{desc}" />
<meta name="twitter:image" content="{site}/og.png" />
<link rel="icon" href="{site}/favicon.svg" />
<link rel="stylesheet" href="https://miaoda.feishu.cn/fonts/css2?family=Noto+Serif+SC:wght@400;600;700&display=swap" />
<script type="application/ld+json">
{jsonld}
</script>
<style>
:root{{--paper:#F5F2ED;--ink:#1B1815;--ochre:#994433;--line:#DCD3C2;--soft:#FBF7EE;--muted:#6E6357}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);
  font-family:"Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif;
  font-size:16.5px;line-height:1.95;letter-spacing:.02em;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:46rem;margin:0 auto;padding:1.6rem 1.5rem 4rem}}
.bar{{display:flex;align-items:center;justify-content:space-between;gap:1rem;
  padding:.7rem 0;border-bottom:1px solid var(--line);font-size:.85rem}}
.bar .mark{{letter-spacing:.3em;color:var(--ochre);font-weight:600}}
.bar a{{color:var(--muted);text-decoration:none;border-bottom:1px solid transparent}}
.bar a:hover{{color:var(--ochre);border-bottom-color:var(--ochre)}}
header{{padding:3.2rem 0 2rem;border-bottom:1px solid var(--line)}}
.kick{{font-size:.78rem;letter-spacing:.34em;color:var(--ochre);margin-bottom:1.2rem}}
h1{{font-size:2.1rem;line-height:1.4;margin:0 0 .8rem;letter-spacing:.04em}}
.lead{{color:var(--muted);font-size:1.02rem;margin:0 0 1.6rem;max-width:34rem}}
.cta{{display:flex;flex-wrap:wrap;gap:.7rem;margin:0}}
.cta a{{display:inline-block;padding:.55rem 1.15rem;border:1px solid var(--ochre);color:var(--ochre);
  text-decoration:none;font-size:.92rem;border-radius:1px}}
.cta a.primary{{background:var(--ochre);color:#FBF7EE}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(6.5rem,1fr));gap:1px;
  background:var(--line);border:1px solid var(--line);margin:2.4rem 0 0}}
.stat{{background:var(--soft);padding:.9rem 1rem}}
.stat b{{display:block;font-size:1.35rem;line-height:1.3;color:var(--ochre)}}
.stat span{{font-size:.78rem;color:var(--muted);letter-spacing:.06em}}
section{{padding:2.6rem 0 0}}
h2{{font-size:1.05rem;letter-spacing:.18em;margin:0 0 .3rem;font-weight:600}}
.note{{color:var(--muted);font-size:.86rem;margin:0 0 1.3rem}}
.list{{display:grid;grid-template-columns:repeat(auto-fill,minmax(13.5rem,1fr));gap:.1rem 1.4rem}}
.list a{{display:flex;align-items:baseline;gap:.55rem;padding:.34rem 0;text-decoration:none;color:var(--ink);
  border-bottom:1px solid rgba(220,211,194,.55);font-size:.95rem}}
.list a:hover{{color:var(--ochre)}}
.list .hex{{font-size:1.05rem;color:var(--ochre);flex:none;line-height:1}}
.list .no{{font-size:.72rem;color:var(--muted);flex:none;min-width:1.5rem;text-align:right;
  font-variant-numeric:tabular-nums}}
.list .nm{{flex:1}}
.rows{{display:grid;gap:.1rem}}
.rows a{{display:flex;flex-wrap:nowrap;align-items:baseline;gap:.9rem;padding:.55rem 0;text-decoration:none;
  color:var(--ink);border-bottom:1px solid rgba(220,211,194,.55);font-size:.95rem}}
.rows a span:first-child{{flex:none;white-space:nowrap}}
.rows a:hover{{color:var(--ochre)}}
.rows span{{color:var(--muted);font-size:.82rem}}
.rows a span:last-child{{flex:1;text-align:right;line-height:1.6}}
footer{{margin-top:3rem;padding-top:1.2rem;border-top:1px solid var(--line);color:var(--muted);font-size:.82rem}}
footer a{{color:var(--ochre);text-decoration:none}}
@media(max-width:560px){{h1{{font-size:1.58rem;letter-spacing:.02em}}.wrap{{padding:1.2rem 1.15rem 3rem}}
 header{{padding:2.2rem 0 1.5rem}} .stats{{grid-template-columns:repeat(2,1fr)}} .rows a{{display:block}} .rows a span:last-child{{display:block;text-align:left;margin-top:.15rem}} .list{{grid-template-columns:1fr;gap:0}}}}
</style>
</head>
<body>
<div class="wrap">
<div class="bar"><span class="mark">道可道 · 易传</span><a href="{repo}" rel="noopener">GitHub 源码</a></div>

<header>
<div class="kick">周易 · 六十四卦 · 系辞上下</div>
<h1>{book}</h1>
<p class="lead">一卦一卷，七节同构：经文底本、时代背景、关键字造字溯源、逐爻深解兼通老庄、体系联动、合与和、常见误读。全书 {ver}，{nchar} 字。</p>
<div class="cta">
<a class="primary" href="{site}/book.html">开始读（全书一页）</a>
<a href="{site}/p/01-qian-kun/">从乾坤读起</a>
<a href="{releases}" rel="noopener">PDF 与离线安卓包</a>
</div>
<div class="stats">
<div class="stat"><b>72</b><span>卷</span></div>
<div class="stat"><b>63</b><span>卦卷</span></div>
<div class="stat"><b>50.5万</b><span>字</span></div>
<div class="stat"><b>704</b><span>页 PDF</span></div>
</div>
</header>

<section>
<h2>卷首</h2>
<p class="note">为什么这么读：底本、体例、两条标尺。</p>
<div class="rows">{prelude}</div>
</section>

<section>
<h2>上经 · 三十卦</h2>
<p class="note">乾坤为首，坎离为终。</p>
<div class="list">{upper}</div>
</section>

<section>
<h2>下经 · 三十四卦</h2>
<p class="note">咸恒为始，既济未济为终。</p>
<div class="list">{lower}</div>
</section>

<section>
<h2>系辞与附录</h2>
<p class="note">彖象之外，易之所以为易。</p>
<div class="rows">{tail}</div>
</section>

<footer>
<p>许可：<a href="{repo}/blob/main/LICENSE" rel="noopener">CC BY-NC-SA 4.0</a>（署名、非商业、相同方式共享）。引用请注明书名与版本号。</p>
<p>当前版本 {ver} · 六十四卦已全，此后只作修订与勘误 · <a href="{repo}" rel="noopener">github.com/q1z2q3-debug/daokedao-yijing</a></p>
</footer>
</div>
</body>
</html>
"""


def build_landing(entries):
    hexchar = {ORDER[i]: chr(0x4DC0 + i) for i in range(64)}
    prelude = "".join(
        '<a href="%s"><span>%s</span><span>%s</span></a>' % (SITE + "/p/" + EXTRA[k][0] + "/", EXTRA[k][1], EXTRA[k][2])
        for k in ("总 序", "前 言", "凡 例")
    )
    tail = "".join(
        '<a href="%s"><span>%s</span><span>%s</span></a>' % (SITE + "/p/" + EXTRA[k][0] + "/", EXTRA[k][1], EXTRA[k][2])
        for k in ("上篇｜系辞上", "下篇｜系辞下", "附 录｜忧患九卦详释", "后 记")
    )
    upper, lower = [], []
    for i, g in enumerate(ORDER, 1):
        item = ('<a href="%s/p/%s/"><span class="hex">%s</span><span class="no">%d</span>'
                '<span class="nm">%s</span></a>' % (SITE, PY[g], hexchar[g], i, g))
        (upper if i <= 30 else lower).append(item)
    upper.insert(0, ('<a href="%s/p/01-qian-kun/"><span class="hex">%s</span><span class="no">1·2</span>'
                     '<span class="nm">乾 · 坤</span></a>' % (SITE, chr(0x4DC0))))
    upper = "".join(upper).replace('<a href="%s/p/01-qian/"><span class="hex">䷀</span><span class="no">1</span><span class="nm">乾</span></a>' % SITE, "")
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Book",
        "name": BOOK,
        "alternateName": "道可道之易传",
        "description": DESC,
        "inLanguage": "zh-CN",
        "bookEdition": VER,
        "numberOfPages": 704,
        "author": {"@type": "Person", "name": AUTHOR},
        "publisher": {"@type": "Person", "name": AUTHOR},
        "datePublished": "2026-11-13",
        "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "url": SITE + "/",
        "image": SITE + "/og.png",
        "hasPart": [{"@type": "Chapter", "name": "%s卦" % g, "url": "%s/p/%s/" % (SITE, PY[g])} for g in ORDER],
    }
    write(os.path.join(DOCS, "index.html"), LAND.format(
        book=BOOK, ver=VER, desc=DESC, site=SITE, author=AUTHOR,
        repo="https://github.com/q1z2q3-debug/daokedao-yijing",
        releases="https://github.com/q1z2q3-debug/daokedao-yijing/releases/latest",
        nchar="50.5 万", prelude=prelude, upper=upper, lower="".join(lower), tail=tail,
        jsonld=json.dumps(jsonld, ensure_ascii=False, indent=1)))

    write(os.path.join(DOCS, "favicon.svg"),
          '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
          '<rect width="64" height="64" fill="#F5F2ED"/><text x="32" y="45" font-size="36" '
          'text-anchor="middle" fill="#994433" font-family="serif">易</text></svg>')


def main():
    css, body = load()
    secs = split_h1(body)

    entries = []  # dict(title,url,slug,desc,body,kind,name)
    for name, sec in secs:
        if name in ("目 录", "封 底"):
            continue
        if "经｜" in name:
            gname = name.split("｜")[1].strip()
            if "·" in gname:
                gname, nums, slugs = "乾 · 坤", [1, 2], "01-qian-kun"
                title = "乾卦与坤卦（第 1、2 卦）｜%s" % BOOK
                prefix = "乾卦与坤卦（第 1、2 卦）"
            else:
                n = ORDER.index(gname) + 1
                nums, slugs = [n], PY[gname]
                title = "%s卦（第 %d 卦）｜%s" % (gname, n, BOOK)
                prefix = "%s卦（第 %d 卦）" % (gname, n)
        elif name in EXTRA:
            slugs, short, tip = EXTRA[name]
            title = "%s｜%s" % (short, BOOK)
            prefix = "%s｜%s：%s" % (short, BOOK, tip)
        else:
            continue
        desc = meta_desc(sec, prefix, "一卦一卷，七节同构；逐爻深解，兼通老庄，辨人为之合与天道之和")
        entries.append(dict(title=title, desc=desc, body=sec, slug="p/" + slugs,
                            url="%s/p/%s/" % (SITE, slugs)))

    for i, e in enumerate(entries):
        prev = entries[i - 1] if i else None
        nxt = entries[i + 1] if i + 1 < len(entries) else None
        jsonld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": e["title"],
            "description": e["desc"],
            "inLanguage": "zh-CN",
            "url": e["url"],
            "mainEntityOfPage": {"@type": "WebPage", "@id": e["url"]},
            "author": {"@type": "Person", "name": AUTHOR},
            "publisher": {"@type": "Person", "name": AUTHOR},
            "isPartOf": {"@type": "Book", "name": BOOK, "bookEdition": VER,
                         "numberOfPages": 704, "inLanguage": "zh-CN", "url": SITE + "/"},
            "datePublished": "2026-11-13",
        }
        write(os.path.join(DOCS, e["slug"], "index.html"), PAGE.format(
            title=e["title"], desc=e["desc"], url=e["url"], book=BOOK, site=SITE, author=AUTHOR,
            jsonld=json.dumps(jsonld, ensure_ascii=False, indent=1),
            css=css, css_extra=CSS_EXTRA, body=e["body"],
            prev=('<a href="%s">← %s</a>' % (prev["url"], re.sub(r"｜.*", "", prev["title"]))) if prev else "&nbsp;",
            nxt=('<a href="%s">%s →</a>' % (nxt["url"], re.sub(r"｜.*", "", nxt["title"]))) if nxt else "&nbsp;",
        ))

    # sitemap：首页、全书、逐页
    urls = [(SITE + "/", "1.0"), (SITE + "/book.html", "0.9")]
    urls += [(e["url"], "0.8") for e in entries]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, p in urls:
        sm.append("  <url><loc>%s</loc><priority>%s</priority><lastmod>2026-11-13</lastmod></url>" % (u, p))
    sm.append("</urlset>")
    write(os.path.join(DOCS, "sitemap.xml"), "\n".join(sm) + "\n")
    write(os.path.join(DOCS, "robots.txt"),
          "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE)

    build_landing(entries)
    write(os.path.join(DOCS, "llms.txt"), """# {book}（{ver}）

> {desc}

- 全书阅读页：{site}/book.html
- 成书 PDF（704 页，29 MB）：https://github.com/q1z2q3-debug/daokedao-yijing/releases/download/{ver}/daokedao-yijing-v1.50.0.pdf
- 安卓离线包（零权限、断网可用）：https://github.com/q1z2q3-debug/daokedao-yijing/releases/download/{ver}/daokedao-yijing-reader-1.50.0.apk
- 源码与逐版校订留痕：https://github.com/q1z2q3-debug/daokedao-yijing
- 全书索引：{site}/sitemap.xml

## 体例
每卦七节：经文底本／时代社会背景／关键字造字溯源／逐爻深解兼通老庄／体系联动／合与和／常见误读。
底本：王弼注本为正文，参《周易正义》《周易本义》《周易集解》，马王堆帛书作异文校勘。

## 许可
CC BY-NC-SA 4.0。引用请注明书名与版本号。
""".format(book=BOOK, ver=VER, desc=DESC, site=SITE))

    print("页面 %d（含首页与全书页共 %d 条 sitemap）" % (len(entries), len(urls)))
    return entries


if __name__ == "__main__":
    main()
