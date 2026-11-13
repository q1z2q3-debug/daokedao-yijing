#!/usr/bin/env python3
"""把 publish/ 下的稿子发到 dev.to（Forem API v1）。

用法：
  export DEVTO_API_KEY=xxxx            # dev.to → Settings → Extensions → DEV Community API Keys
  python3 scripts/publish-devto.py publish/devto-en.md --draft
  python3 scripts/publish-devto.py publish/devto-en.md          # 真发

只依赖标准库。稿子头部用 YAML front matter（title / description / tags / canonical_url），
脚本解析它并发给 API；已发布的文章会返回 url，可据此在 dev.to 后台改。
"""
import json
import os
import re
import sys
import urllib.request

API = "https://dev.to/api/articles"


def parse(path):
    s = open(path, encoding="utf-8").read()
    m = re.match(r"---\n([\s\S]*?)\n---\n([\s\S]*)", s)
    if not m:
        sys.exit("稿子缺少 front matter（--- 开头的一段）")
    head, body = m.group(1), m.group(2).strip()
    meta = {}
    for line in head.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()][:4]
    return {
        "title": meta["title"],
        "body_markdown": body,
        "published": meta.get("published", "false").lower() == "true",
        "tags": tags,
        "description": meta.get("description", ""),
        "canonical_url": meta.get("canonical_url", ""),
    }


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    key = os.environ.get("DEVTO_API_KEY")
    if not key:
        sys.exit("缺少环境变量 DEVTO_API_KEY（dev.to → Settings → Extensions 生成）")
    art = parse(sys.argv[1])
    draft = "--draft" in sys.argv
    art["published"] = False if draft else art["published"]

    req = urllib.request.Request(
        API,
        data=json.dumps({"article": art}).encode(),
        headers={"api-key": key, "Content-Type": "application/json", "Accept": "application/vnd.forem.api-v1+json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    print("已提交：", d.get("url"), "published=", d.get("published"))


if __name__ == "__main__":
    main()
