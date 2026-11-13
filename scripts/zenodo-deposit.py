#!/usr/bin/env python3
"""把成书与提示词存入 Zenodo，取一个可引用的 DOI。

用法：
  export ZENODO_TOKEN=xxx
  python3 scripts/zenodo-deposit.py --dry-run     # 建草稿、传文件、不发布
  python3 scripts/zenodo-deposit.py --publish     # 发布，DOI 立即生效（不可撤销）

注：Zenodo 对无浏览器 UA 的请求会返回 403「unusual traffic」，脚本统一带浏览器 UA。
"""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

BASE = "https://zenodo.org/api"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
ROOT = Path(__file__).resolve().parent.parent
VER = "1.50.0"

FILES = [
    ("book/润泽说 道可道之易传.pdf", "daokedao-yijing-v1.50.0.pdf"),
    ("book/润泽说 道可道之易传.html", "daokedao-yijing-v1.50.0.html"),
    ("book/润泽说 道可道之易传.md", "daokedao-yijing-v1.50.0.md"),
    ("prompt/润泽说·易传问答Agent（提示词与检索表）.pdf", "yijing-agent-prompt-v1.50.0.pdf"),
    ("packages/apk-1.50.0-yijing/道可道-易传-1.50.0.apk", "daokedao-yijing-reader-1.50.0.apk"),
]

META = {
    "metadata": {
        "title": "润泽说 道可道之易传（v1.50.0）",
        "upload_type": "publication",
        "publication_type": "book",
        "publication_date": "2026-11-13",
        "version": VER,
        "language": "zho",
        "license": "cc-by-nc-sa-4.0",
        "creators": [{"name": "润泽说易"}],
        "keywords": ["周易", "易传", "六十四卦", "系辞", "先秦思想", "中国哲学", "老庄"],
        "description": (
            "<p>《周易》六十四卦与《系辞》上下篇的完整读本：72 卷、50.5 万字，一卦一卷、七节同构。</p>"
            "<p>每卦七节：经文底本（王弼注本为正文，参《周易正义》《周易本义》《周易集解》，"
            "马王堆帛书作异文校勘）／时代社会背景／关键字造字溯源（分字形、先秦用例、汉人训释、"
            "本书所取四层）／逐爻深解兼通老庄／体系联动（综卦错卦互卦）／合与和／常见误读。</p>"
            "<p>全书主线为「人为之合」与「天道之和」之辨；卦爻不作吉凶断语，只标时位与边界。</p>"
            "<p>附件：成书 PDF（704 页）、单文件 HTML 阅读页、Markdown 母本、"
            "问答 Agent 提示词与检索表 PDF、安卓离线包（零权限、断网可用）。</p>"
        ),
        "related_identifiers": [
            {"relation": "isSupplementTo",
             "identifier": "https://github.com/q1z2q3-debug/daokedao-yijing",
             "resource_type": "software"},
            {"relation": "isAlternateIdentifier",
             "identifier": "https://q1z2q3-debug.github.io/daokedao-yijing/",
             "resource_type": "other"},
        ],
        "notes": "许可 CC BY-NC-SA 4.0。引用请注明书名与版本号 v1.50.0。",
    }
}


def call(url, token, data=None, method="POST", raw=None):
    body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
    req = urllib.request.Request(url, data=body, method=method, headers={
        "Authorization": f"Bearer {token}",
        "User-Agent": UA,
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--publish", action="store_true")
    args = ap.parse_args()

    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        sys.exit("缺少 ZENODO_TOKEN（zenodo.org → Settings → Applications → Personal access token，勾 deposit:write 与 deposit:actions）")

    dep = call(f"{BASE}/deposit/depositions", token, {}, "POST")
    print("草稿 id", dep["id"])
    call(f"{BASE}/deposit/depositions/{dep['id']}", token, META, "PUT")

    for src, name in FILES:
        p = ROOT / src
        if not p.exists():
            sys.exit(f"缺文件：{p}")
        req = urllib.request.Request(
            f"{dep['links']['bucket']}/{urllib.parse.quote(name)}",
            data=p.read_bytes(), method="PUT",
            headers={"Authorization": f"Bearer {token}", "User-Agent": UA,
                     "Content-Type": "application/octet-stream"})
        with urllib.request.urlopen(req, timeout=600) as r:
            d = json.load(r)
        print("  ↑", name, d.get("size"))

    if args.publish:
        out = call(f"{BASE}/deposit/depositions/{dep['id']}/actions/publish", token, method="POST")
        print("已发布 DOI:", out.get("doi"), out.get("links", {}).get("html"))
    else:
        print("草稿未发布：", dep["links"].get("html"))


if __name__ == "__main__":
    import urllib.parse
    main()
