#!/usr/bin/env python3
"""从 yijing/book/ 的 v1.50.0 阅读页生成 APK 用的 assets。

做两件事：
  1. 把外链字体（miaoda.feishu.cn）换成本地 @font-face，实现完全离线；
  2. 用系统 Noto Serif CJK 子集化出只含本书用字的 woff（400 / 600）。

产物不入库（体积大、可由本脚本重建）：
  apk-yijing/assets/book.html
  apk-yijing/assets/fonts/YiSerif-Regular.woff
  apk-yijing/assets/fonts/YiSerif-Bold.woff

用法：python3 prepare-assets.py
"""
import html
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "yijing", "book", "润泽说 道可道之易传.html")
ASSETS = os.path.join(HERE, "assets")
FONTS = os.path.join(ASSETS, "fonts")

NOTO = {
    "Regular": ("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", 2),
    "Bold": ("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", 2),
}

FACE = """<style>
@font-face{font-family:"YiSerif";src:url("fonts/YiSerif-Regular.woff") format("woff");font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:"YiSerif";src:url("fonts/YiSerif-Bold.woff") format("woff");font-weight:600 900;font-style:normal;font-display:swap}
</style>"""

LINK = ('<link rel="stylesheet" href="https://miaoda.feishu.cn/fonts/css2'
        '?family=Noto+Serif+SC:wght@400;600;700&display=swap" />')

OLD_SERIF = '--serif:"Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif;'
NEW_SERIF = ('--serif:"YiSerif","Noto Serif SC","Source Han Serif SC",'
             '"Songti SC","SimSun",serif;')


def build_html():
    s = open(SRC, encoding="utf-8").read()
    assert s.count(LINK) == 1, "字体外链结构变了，请检查 book html"
    s = s.replace(LINK, FACE)
    assert s.count(OLD_SERIF) == 1, "--serif 变量结构变了"
    s = s.replace(OLD_SERIF, NEW_SERIF)
    os.makedirs(ASSETS, exist_ok=True)
    dst = os.path.join(ASSETS, "book.html")
    open(dst, "w", encoding="utf-8").write(s)
    print("book.html  %d 字节  外链剩余 %d" % (os.path.getsize(dst), s.count("https://")))
    return s


def char_set(doc):
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", doc)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = html.unescape(t)
    base = {c for c in t if not c.isspace()}
    base |= {chr(i) for i in range(32, 127)}
    # 卦符与常用标点：六爻符号 ䷀—䷿、八卦符号、中文引号书名号等
    base |= {chr(i) for i in range(0x4DC0, 0x4E00)}
    base |= {chr(i) for i in range(0x2630, 0x2640)}
    base |= set("　、。《》「」『』（）—…·：；！？〔〕【】“”‘’％＋－×＝／　")
    return "".join(sorted(base))


def build_fonts(chars):
    from fontTools import subset

    os.makedirs(FONTS, exist_ok=True)
    for weight, (path, index) in NOTO.items():
        opts = subset.Options()
        opts.font_number = index
        opts.hinting = False
        opts.desubroutinize = True
        opts.layout_features = ["*"]
        opts.name_IDs = ["*"]
        opts.name_languages = ["*"]
        opts.notdef_outline = True
        font = subset.load_font(path, opts)
        sub = subset.Subsetter(options=opts)
        sub.populate(text=chars)
        sub.subset(font)
        font.flavor = "woff"
        dst = os.path.join(FONTS, "YiSerif-%s.woff" % weight)
        font.save(dst)
        print("YiSerif-%s.woff  %d 字节" % (weight, os.path.getsize(dst)))


if __name__ == "__main__":
    doc = build_html()
    cs = char_set(doc)
    print("用字 %d 个" % len(cs))
    build_fonts(cs)
    print("✓ assets 就绪")
