#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""由 prompt 下两份 md 生成《提示词与检索表》PDF。
用法：python3 scripts/build-prompt-pdf.py
产物：prompt/润泽说·易传问答Agent（提示词与检索表）.pdf
依赖：pandoc、chromium（路径见 CHROME）
"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "prompt", "润泽说·易传问答Agent（系统提示词）.md")
T = os.path.join(ROOT, "prompt", "易传篇目检索表.md")
OUT = os.path.join(ROOT, "prompt", "润泽说·易传问答Agent（提示词与检索表）.pdf")
TMP = "/tmp/zprompt.html"
CHROME = "/opt/vm/preinstall/ms-playwright/chromium-1169/chrome-linux/chrome"
VER = open(os.path.join(ROOT, "VERSION"), encoding="utf-8").read().strip()

CSS = """
body{font-family:"Noto Serif SC","Songti SC","DejaVu Sans",Georgia,serif;font-size:10.5pt;line-height:1.85;color:#1a1713;margin:0}
h1{font-size:17pt;text-align:center;margin:0 0 6mm;page-break-before:always;page-break-after:avoid}
h1:first-of-type{page-break-before:avoid;font-size:20pt;margin-top:22mm}
h2{font-size:11.6pt;margin:6mm 0 2mm;page-break-after:avoid;color:#5a3d1c}
h3{font-size:10.6pt;margin:4mm 0 1.5mm;page-break-after:avoid}
p{margin:0 0 2.2mm;text-align:justify}
table{border-collapse:collapse;width:100%;font-size:9pt;margin:3mm 0;table-layout:fixed}
th,td{border:1px solid #bbb;padding:1.2mm 1.6mm;vertical-align:top;line-height:1.55;overflow-wrap:break-word}
thead{background:#f1ede4}
tr{page-break-inside:avoid}
ol,ul{margin:1mm 0 3mm 6mm}
li{margin:0.8mm 0}
blockquote{margin:3mm 0;padding-left:4mm;border-left:2px solid #8a5a2b;color:#4a443c;font-size:9.6pt}
code{font-family:"DejaVu Sans Mono",monospace;font-size:8.6pt}
@page{size:A4;margin:16mm 15mm 18mm}
h1,h2,h3,th{orphans:2;widows:2}
"""

COVER = """<h1>润泽说·易传问答 Agent</h1>
<p style="text-align:center;letter-spacing:.2em;color:#8a8378">系统提示词 ＋ 篇目检索表</p>
<p style="text-align:center;color:#7a736a;font-size:9.5pt">《润泽说 道可道之易传》v%s　｜　上经三十卦已全，下经至夬十三卦</p>
<div style="max-width:118mm;margin:13mm auto 0;font-size:10pt;line-height:2;color:#3a342c">
一、<b>系统提示词</b>——身份、骨架、六条不可移动的判断、十二条回答规则、语气。<br>
二、<b>篇目检索表</b>——全书 48 卷顺序；前四卷详表；上经三十卦与下经十三卦速查（卦体／卦辞／卷眼／主眼）；全书凡例索引。<br>
三、<b>怎么用</b>——先认卷，再认节；问字源走四层；凡例型断言查索引，不在索引里不作断言。
</div>
<hr style="border:none;border-top:1px solid #ccc;margin:10mm 0 0">
<p style="text-align:center;color:#8a8378;letter-spacing:.24em;font-size:9.5pt;margin-top:2mm">道 可 道 之 易 传 · 问 答 件</p>
""" % VER

W = {2: [17, 83], 3: [9, 31, 60], 5: [9, 10, 23, 27, 31]}


def frag(path):
    return subprocess.run(
        ["pandoc", "-f", "markdown-yaml_metadata_block+hard_line_breaks+pipe_tables",
         "-t", "html5", "--wrap=none", path],
        capture_output=True, text=True, check=True).stdout


def fix_cols(html):
    """按列数替换 pandoc 自带的等宽 colgroup。"""
    def rep(m):
        block = m.group(0)
        w = W.get(len(re.findall(r"<th[ >]", block)))
        if not w:
            return block
        cols = "<colgroup>" + "".join('<col style="width:%d%%" />' % x for x in w) + "</colgroup>"
        if "<colgroup>" in block:
            return re.sub(r"<colgroup>.*?</colgroup>", cols, block, count=1, flags=re.S)
        return block.replace("<table>", "<table>" + cols, 1)
    return re.sub(r"<table>[\s\S]*?</thead>", rep, html)


def main():
    html = ("<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>"
            "<title>润泽说 道可道之易传 系统提示词与检索表 v%s</title><style>%s</style></head><body>"
            % (VER, CSS)) + COVER + fix_cols(frag(P)) + fix_cols(frag(T)) + "</body></html>"
    open(TMP, "w", encoding="utf-8").write(html)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", "--print-to-pdf=" + OUT, "file://" + TMP],
                   check=True, capture_output=True)
    print("已生成：%s（%d B）" % (OUT, os.path.getsize(OUT)))


if __name__ == "__main__":
    main()
