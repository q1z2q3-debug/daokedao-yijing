#!/usr/bin/env bash
# 由主本 Markdown 重建单文件 HTML 阅读页。
# 用法：bash scripts/build.sh
set -euo pipefail
cd "$(dirname "$0")/.."

MD="book/润泽说 道可道之易传.md"
HTML="book/润泽说 道可道之易传.html"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

command -v pandoc >/dev/null || { echo "需要 pandoc"; exit 1; }

# 1. Markdown -> HTML5 片段。必须带 -yaml_metadata_block，
#    否则文件名含「·」时，首个 --- 会被当作 YAML 头，整篇静默失败。
pandoc "$MD" -f markdown-yaml_metadata_block+hard_line_breaks -t html5 --wrap=none -o "$TMP/body.html"

# 2. 表格修复：包 <div class="tbl">，按列数注入 <colgroup>。
python3 - "$TMP/body.html" <<'PY'
import re, sys

path = sys.argv[1]
body = open(path, encoding="utf-8").read()

def plain(x):
    return re.sub(r"<[^>]+>", "", x).strip()

def fix(m):
    t = m.group(0)
    rows = re.findall(r"<tr[^>]*>([\s\S]*?)</tr>", t)
    n = len(re.findall(r"<t[hd]", rows[0])) if rows else 0
    cls = ' class="wide"' if n > 3 else ""
    cg = ""
    if 0 < n <= 3 and "<colgroup>" not in t:
        if n == 3:
            firsts = [plain(c) for r in rows[1:]
                      for c in re.findall(r"<td[^>]*>([\s\S]*?)</td>", r)][0::3]
            L = max((len(f) for f in firsts), default=3)
            if L <= 4:                       # 短首列会被压成一字一行
                f1 = min(34, 8 + 5.5 * L)
                cg = ('<colgroup><col style="width:{}%"><col style="width:{}%">'
                      '<col style="width:{}%"></colgroup>').format(
                          round(f1, 1), round((100 - f1) * .46, 1), round((100 - f1) * .54, 1))
            else:
                cg = ('<colgroup><col style="width:33.33%"><col style="width:33.33%">'
                      '<col style="width:33.34%"></colgroup>')
        else:
            w = round(100 / n, 2)
            cg = "<colgroup>" + "".join('<col style="width:%s%%">' % w for _ in range(n)) + "</colgroup>"
    tt = t.replace("<table>", "<table>" + cg, 1) if cg else t
    return '<div class="tbl">' + tt.replace("<table", "<table" + cls, 1) + "</div>"

open(path, "w", encoding="utf-8").write(re.sub(r"<table[\s\S]*?</table>", fix, body))
PY

# 3. 只替换 <main id="book"> 与 </main> 之间。
python3 - "$HTML" "$TMP/body.html" <<'PY'
import sys
path, tpl = sys.argv[1], sys.argv[2]
h = open(path, encoding="utf-8").read()
body = open(tpl, encoding="utf-8").read()
a = h.index('<main id="book">') + len('<main id="book">')
b = h.index('</main>')
open(path, "w", encoding="utf-8").write(h[:a] + "\n" + body + "\n" + h[b:])
PY

echo "已重建：$HTML"
