#!/bin/bash
# ScrapeMaster 隐身模式爬虫运行脚本

set -e  # 出错时停止

echo "================================================"
echo "ScrapeMaster 隐身模式爬虫"
echo "================================================"

# 检查Python依赖
echo "🔍 检查Python依赖..."
python3 -c "
try:
    import pandas
    import playwright
    import openpyxl
    print('✅ 所有依赖已安装')
except ImportError as e:
    print(f'❌ 依赖缺失: {e}')
    print('请运行: pip install pandas playwright openpyxl')
    exit(1)
"

# 检查Playwright浏览器
echo "🔍 检查Playwright浏览器..."
if [ ! -d "$HOME/.cache/ms-playwright" ]; then
    echo "⚠️  Playwright浏览器未安装"
    echo "正在安装Playwright Chromium..."
    python3 -m playwright install chromium
else
    echo "✅ Playwright浏览器已安装"
fi

# 运行隐身模式爬虫
echo ""
echo "🚀 启动隐身模式爬虫..."
echo "模式: 无头模式 (隐藏浏览器界面)"
echo "笔记数: 5条 (测试模式)"
echo "================================================"

python3 src/scrape_xiaohongshu_incognito.py <<EOF
2
5
EOF

echo ""
echo "================================================"
echo "爬虫运行完成！"
echo "结果保存在: sharon_comments_incognito_*.xlsx"
echo "================================================"