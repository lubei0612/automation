#!/bin/bash
set -e
if [ -d "/testbed" ]; then
    rm -rf /testbed
fi
# 创建 testbed 目录
mkdir -p /testbed

echo ">>> Cloning repository: eslint/eslint..."
# Clone 代码到 /testbed/repo_name
git clone https://github.com/eslint/eslint.git /testbed/eslint

echo ">>> Checking out commit: 4e5e9befb95bc1fc7fbcb145825b8e0451e5bc6c..."
cd /testbed/eslint
git checkout 4e5e9befb95bc1fc7fbcb145825b8e0451e5bc6c

echo ">>> Repository setup complete."
