#!/usr/bin/env python3
"""把本库同步为 HuggingFace 数据集镜像（永久可下载的文本存档）。

用法：
  export HF_TOKEN=hf_xxx          # huggingface.co → Settings → Access Tokens (write)
  python3 scripts/mirror-hf.py --repo q1z2q3/daokedao-yijing

只上传文本与成书产物；APK 走 GitHub Releases，避免数据集里塞二进制。
"""
import argparse
import os
import sys
from pathlib import Path

from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parent.parent

CARD = """---
language:
- zh
license: cc-by-nc-sa-4.0
pretty_name: 润泽说 道可道之易传
tags:
- classical-chinese
- yijing
- iching
- zhouyi
- digital-humanities
- commentary
task_categories:
- text-generation
size_categories:
- 100K<n<1M
---

# 润泽说 道可道之易传

《周易》六十四卦与《系辞》上下篇的完整读本：**72 卷、50.5 万字**，一卦一卷、七节同构。

在线阅读：<https://q1z2q3-debug.github.io/daokedao-yijing/>
永久存档（DOI）：<https://doi.org/10.5281/zenodo.24185930>
源码与逐版校订留痕：<https://github.com/q1z2q3-debug/daokedao-yijing>
离线 APK 与 PDF：见 GitHub Releases（`v1.50.0`）

## 文件

| 路径 | 内容 |
|---|---|
| `book/润泽说 道可道之易传.md` | 主本，72 卷全，Markdown 母本 |
| `book/润泽说 道可道之易传.html` | 单文件阅读页，版式与交互全内联 |
| `book/润泽说 道可道之易传.pdf` | 成书 PDF，704 页 |
| `book/润泽说 道可道之易传·投来稿清排本.md` | 投来原稿清排，只排版不增补 |
| `prompt/` | 篇目检索表、问答 Agent 系统提示词（二十五条判断） |
| `releases/v1.50.0/` | 当版冻结件与 SHA-256 清单 |
| `archive/tougao/` | 投来稿存档 25 卷，一字不改 |

## 体例

每卦七节：经文底本／时代社会背景／关键字造字溯源／逐爻深解兼通老庄／体系联动／合与和／常见误读。
底本：王弼注本为正文，参《周易正义》《周易本义》《周易集解》，马王堆帛书作异文校勘。

## 引用

```
润泽说易. (2026). 《润泽说 道可道之易传》(v1.50.0) [Book]. Zenodo.
https://doi.org/10.5281/zenodo.24185930
```

许可：CC BY-NC-SA 4.0（署名、非商业、相同方式共享）。
"""

ALLOW = [
    "book/*.md", "book/*.html", "book/*.pdf",
    "prompt/*", "releases/v1.50.0/*", "archive/tougao/*",
    "LICENSE", "CITATION.cff", "CHANGELOG.md", "VERSION", "README.md",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="q1z2q3/daokedao-yijing")
    args = ap.parse_args()
    token = os.environ.get("HF_TOKEN")
    if not token:
        sys.exit("缺少 HF_TOKEN")

    api = HfApi(token=token)
    api.create_repo(repo_id=args.repo, repo_type="dataset", private=False, exist_ok=True)

    api.upload_folder(folder_path=str(ROOT), repo_id=args.repo, repo_type="dataset",
                      allow_patterns=ALLOW, commit_message="mirror: v1.50.0 全量文本与成书产物")

    # 卡片最后传：--allow-patterns 里的 README.md 会先覆盖掉卡片
    card = CARD.format(repo=args.repo)
    (ROOT / ".hf-readme.tmp").write_text(card, encoding="utf-8")
    api.upload_file(path_or_fileobj=str(ROOT / ".hf-readme.tmp"), path_in_repo="README.md",
                    repo_id=args.repo, repo_type="dataset", commit_message="dataset card")
    (ROOT / ".hf-readme.tmp").unlink()
    print("✓ https://huggingface.co/datasets/" + args.repo)


if __name__ == "__main__":
    main()
