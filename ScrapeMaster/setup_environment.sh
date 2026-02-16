#!/bin/bash
# ScrapeMaster 环境安装脚本

set -e  # 出错时停止

echo "=== 安装系统依赖 ==="
sudo apt-get update
sudo apt-get install -y python3-pip nodejs npm

echo "=== 安装 Python 依赖 ==="
pip3 install --user pandas playwright requests beautifulsoup4 lxml

echo "=== 安装 Playwright 浏览器 ==="
python3 -m playwright install chromium

echo "=== 安装 Node.js 依赖 ==="
npm install

echo "=== 验证安装 ==="
python3 -c "import pandas; print('✓ pandas:', pandas.__version__)"
python3 -c "import playwright; print('✓ playwright 可用')"
node -c src/scrape_xiaohongshu.js && echo "✓ JavaScript 语法正确"

echo ""
echo "🎉 环境安装完成！"
echo "运行 Python 爬虫: python3 src/scrape_xiaohongshu.py"
echo "运行 JavaScript 爬虫: node src/scrape_xiaohongshu.js"
