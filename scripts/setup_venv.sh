#!/usr/bin/env bash
# 创建并配置 Python venv，安装 backend 依赖。
# 用法：从仓库根目录执行 ./scripts/setup_venv.sh 或 bash scripts/setup_venv.sh

set -e
cd "$(dirname "$0")/.."

if [[ ! -d .venv ]]; then
  echo "Creating .venv..."
  python3 -m venv .venv
fi

echo "Installing backend dependencies (may take several minutes)..."
.venv/bin/pip install -r backend/requirements.txt

echo "Done. Activate with: source .venv/bin/activate"
