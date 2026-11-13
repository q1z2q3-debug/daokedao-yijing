#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""由 archive/tougao 拼装《投来稿清排本》。可重复运行。
用法：python3 scripts/build-qingpai.py
产物：book/润泽说 道可道之易传·投来稿清排本.md 与 .html
"""
import glob, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "archive", "tougao")
MD = os.path.join(ROOT, "book", "润泽说 道可道之易传·投来稿清排本.md")
HTML = os.path.join(ROOT, "book", "润泽说 道可道之易传·投来稿清排本.html")

HEAD = """# 润泽说　道可道之易传·投来稿清排本

<p style="text-align:center;color:#8a8378;letter-spacing:.24em;font-size:14px;margin:16px 0 4px">原稿存档　一字未改</p>

> 本卷只做一件事：把投来的原稿排清

## 关于本卷

**一、本卷是原稿，不是定本。**

与它并行的《润泽说　道可道之易传》是校订后的定本；本卷保存的是投来时的原样，一字未改——包括可疑的字、不通的句、异体的形。

两卷并读，才能看出改了什么、为什么改。

**二、只做排版，不做校订。**

原稿的小标题、编号、分段，整理成统一的层级；措辞、标点、引语、卦符，一概不动。

**三、缺档说明。**

卦序 001—039（乾至蹇，三十九卦、三十八卷——乾与坤合为一卷）的投来原稿未存——早期卦稿的中间态只落在临时目录，会话压缩与目录清理之后已不可回溯。

不从主稿回填、不凭记忆补造。主稿那些卷是校订本，不能冒充原稿。

逐版改了什么、依据是什么，见 `CHANGELOG.md`（v1.20.0—v1.37.0）。

**四、此后每卦收到即落盘。**

`archive/tougao/<卦序>-<卦名>-原稿.md`，再由本脚本拼装。

---
"""

FOOT = """
<p style="text-align:center;color:#8a8378;letter-spacing:.24em;font-size:0.95em;margin:28px 0 0">润泽说易　存</p>
"""

CSS = """<style>
:root{--ink:#2b2620;--soft:#7a736a;--line:#e3ddd2;--bg:#faf8f4;--accent:#8a5a2b;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font-family:"Noto Serif SC","Songti SC","DejaVu Sans",Georgia,serif;font-size:16px;line-height:1.95;-webkit-font-smoothing:antialiased}
main{max-width:760px;margin:0 auto;padding:56px 24px 96px}
h1{font-size:1.5em;line-height:1.6;letter-spacing:.04em;margin:2.2em 0 .6em;padding-bottom:.35em;border-bottom:1px solid var(--line);page-break-before:always}
h1:first-of-type{page-break-before:avoid;border-bottom:none;font-size:1.9em;text-align:center;margin-top:0}
h2{font-size:1.12em;letter-spacing:.06em;color:var(--accent);margin:2em 0 .7em;page-break-after:avoid}
h3{font-size:1em;letter-spacing:.04em;margin:1.5em 0 .5em;page-break-after:avoid}
p{margin:0 0 .85em;text-align:justify}
blockquote{margin:1.4em 0;padding:.2em 0 .2em 1em;border-left:3px solid var(--accent);color:#4a443c}
ol,ul{margin:.6em 0 1em 1.4em}
li{margin:.3em 0}
strong{font-weight:600}
hr{border:none;border-top:1px solid var(--line);margin:2.4em 0}
@media(max-width:600px){main{padding:28px 16px 64px;font-size:15px}}
@media print{body{background:#fff;font-size:10.5pt}main{max-width:none;padding:0}h1{page-break-before:always}h1:first-of-type{page-break-before:avoid}}
</style>
"""

def main():
    files = sorted(glob.glob(os.path.join(SRC, "[0-9][0-9][0-9]-*.md")))
    if not files:
        sys.exit("archive/tougao 下没有原稿文件")
    body = []
    toc = []
    for f in files:
        name = os.path.basename(f)
        text = open(f, encoding="utf-8").read().strip()
        # 原稿首行是「# 卦名」，降为 h1 之下的一卷；保留原文
        text = re.sub(r"^# ", "## ", text, count=1)
        body.append(text)
        toc.append("- `%s`" % name)
    doc = HEAD + "\n**已存原稿**\n\n" + "\n".join(toc) + "\n\n---\n\n" + "\n\n---\n\n".join(body) + "\n" + FOOT
    open(MD, "w", encoding="utf-8").write(doc)

    html_body = subprocess.run(
        ["pandoc", "-f", "markdown-yaml_metadata_block+hard_line_breaks+pipe_tables",
         "-t", "html5", "--wrap=none", MD],
        capture_output=True, text=True, check=True).stdout
    page = ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 64 64\'%3E%3Crect width=\'64\' height=\'64\' rx=\'10\' fill=\'%238a5a2b\'/%3E%3Ctext x=\'32\' y=\'45\' font-size=\'34\' text-anchor=\'middle\' fill=\'%23faf8f4\'%3E易%3C/text%3E%3C/svg%3E">'
            "<title>润泽说 道可道之易传·投来稿清排本</title>" + CSS
            + "</head><body><main>" + html_body + "</main></body></html>")
    open(HTML, "w", encoding="utf-8").write(page)
    print("已生成：%s\n已生成：%s（%d 卷）" % (MD, HTML, len(files)))

if __name__ == "__main__":
    main()
