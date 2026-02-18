#!/bin/bash
# 启动Chrome用于小红书爬虫（支持WSL环境）

echo "🚀 启动Chrome浏览器用于小红书爬虫..."
echo "=========================================="

# WSL环境：Chrome通常安装在Windows上
if [[ -n "$WSL_DISTRO_NAME" ]]; then
    echo "🌐 检测到WSL环境"
    
    # 尝试查找Windows Chrome路径
    WIN_CHROME_PATHS=(
        "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
        "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"
        "/mnt/c/Users/$USER/AppData/Local/Google/Chrome/Application/chrome.exe"
    )
    
    CHROME_CMD=""
    for path in "${WIN_CHROME_PATHS[@]}"; do
        if [[ -f "$path" ]]; then
            CHROME_CMD="$path"
            echo "✅ 找到Windows Chrome: $CHROME_CMD"
            break
        fi
    done
    
    if [[ -z "$CHROME_CMD" ]]; then
        echo "⚠️  未找到Windows Chrome，请手动启动:"
        echo "   1. 打开Windows Chrome浏览器"
        echo "   2. 添加启动参数: --remote-debugging-port=18792"
        echo "   3. 导航到: https://www.xiaohongshu.com"
        echo ""
        echo "📋 手动启动命令示例:"
        echo '   "C:\Program Files\Google\Chrome\Application\chrome.exe" ^'
        echo '   --remote-debugging-port=18792 ^'
        echo '   --user-data-dir="%USERPROFILE%\.chrome-scrapemaster-profile" ^'
        echo '   --no-first-run ^'
        echo '   --no-default-browser-check ^'
        echo '   "https://www.xiaohongshu.com"'
        exit 0
    fi
else
    # Linux环境
    echo "🐧 检测到Linux环境"
    
    # 检查Chrome是否已安装
    if ! command -v google-chrome &> /dev/null && ! command -v chrome &> /dev/null; then
        echo "❌ Chrome未安装，请先安装Chrome浏览器"
        echo "下载地址: https://www.google.com/chrome/"
        exit 1
    fi
    
    # 查找Chrome可执行文件
    CHROME_CMD=""
    for cmd in google-chrome chrome; do
        if command -v $cmd &> /dev/null; then
            CHROME_CMD=$cmd
            break
        fi
    done
    
    echo "✅ 找到Chrome: $CHROME_CMD"
fi

if [[ -n "$CHROME_CMD" ]]; then
    # 启动Chrome并启用远程调试
    echo "🔧 启动Chrome（启用远程调试端口18792）..."
    
    # 使用不同的端口避免与OpenClaw Gateway冲突
    CHROME_PORT=18793
    
    if [[ -n "$WSL_DISTRO_NAME" ]]; then
        # WSL: 使用cmd.exe启动Windows Chrome
        cmd.exe /c "start \"\" \"$CHROME_CMD\" \
            --remote-debugging-port=$CHROME_PORT \
            --user-data-dir=\"%USERPROFILE%\\.chrome-scrapemaster-profile\" \
            --no-first-run \
            --no-default-browser-check \
            \"https://www.xiaohongshu.com\"" &
    else
        # Linux: 直接启动
        $CHROME_CMD \
            --remote-debugging-port=$CHROME_PORT \
            --user-data-dir="$HOME/.chrome-scrapemaster-profile" \
            --no-first-run \
            --no-default-browser-check \
            "https://www.xiaohongshu.com" &
    fi
    
    echo "📊 远程调试地址: http://localhost:$CHROME_PORT"
    
    CHROME_PID=$!
    echo "✅ Chrome已启动"
else
    echo "📝 请手动启动Chrome（见上方说明）"
    CHROME_PID="MANUAL"
fi

CHROME_PID=$!
echo "✅ Chrome已启动，PID: $CHROME_PID"
echo "📊 远程调试地址: http://localhost:18792"

# 等待Chrome启动
sleep 3

echo ""
echo "📋 下一步操作:"
echo "1. 登录小红书账户（如果需要）"
echo "2. 导航到目标用户页面"
echo "3. 安装OpenClaw Browser Relay扩展（如果未安装）"
echo "4. 点击工具栏的OpenClaw图标连接标签页"
echo "5. 在另一个终端运行爬虫:"
echo "   cd ScrapeMaster"
echo "   python3 src/scrape_xiaohongshu_chrome.py"
echo ""
echo "🛑 停止Chrome: kill $CHROME_PID"
echo "=========================================="

# 保存PID到文件
echo $CHROME_PID > /tmp/chrome_scrapemaster.pid
echo "📝 PID已保存到: /tmp/chrome_scrapemaster.pid"