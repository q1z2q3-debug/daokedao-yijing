#!/usr/bin/env bash
# 把本库同步到其它代码托管平台（Gitee / GitLab / Codeberg 等）。
#
# 用法：
#   ./scripts/mirror.sh gitee    # 需先配置 remote 与凭据
#   ./scripts/mirror.sh gitlab
#
# 前置：各平台建好同名空库，并把带凭据的 URL 加为 remote，例如
#   git remote add gitee https://<user>:<token>@gitee.com/<user>/daokedao-yijing.git
#   git remote add gitlab https://oauth2:<token>@gitlab.com/<user>/daokedao-yijing.git
#
# 只推 main 与版本 tag，不动历史；失败即停，不吞错误。
set -euo pipefail
REMOTE=${1:?用法: ./scripts/mirror.sh <remote 名>}
git remote get-url "$REMOTE" >/dev/null || { echo "没有这个 remote：$REMOTE（见脚本头部注释）"; exit 1; }
git -c http.version=HTTP/1.1 push "$REMOTE" main --follow-tags
echo "✓ 已同步到 $REMOTE"
