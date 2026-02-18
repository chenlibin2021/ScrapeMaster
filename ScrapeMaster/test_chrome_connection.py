#!/usr/bin/env python3
"""
测试Chrome Browser Relay连接
"""

from playwright.sync_api import sync_playwright
import time

def test_chrome_connection():
    """测试连接到Chrome Browser Relay"""
    print("🔗 测试Chrome Browser Relay连接")
    print("=" * 50)
    
    # 尝试连接到Chrome
    with sync_playwright() as p:
        print("1. 初始化Playwright... ✅")
        
        try:
            print("2. 尝试连接到Chrome (localhost:18793)...")
            browser = p.chromium.connect_over_cdp("http://localhost:18793")
            print("   ✅ 连接成功!")
            
            print("3. 获取浏览器信息...")
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            print(f"   ✅ 上下文: {len(browser.contexts)}个")
            
            print("4. 获取页面信息...")
            pages = context.pages if hasattr(context, 'pages') else []
            print(f"   ✅ 页面: {len(pages)}个")
            
            if pages:
                page = pages[0]
                print(f"5. 当前页面URL: {page.url}")
                print(f"6. 页面标题: {page.title()}")
            else:
                print("5. 没有打开的页面，创建新页面...")
                page = context.new_page()
                page.goto("https://www.xiaohongshu.com")
                print(f"   ✅ 导航到: {page.url}")
                print(f"   ✅ 页面标题: {page.title()}")
            
            print("7. 测试页面操作...")
            page_content = page.content()[:200] + "..." if len(page.content()) > 200 else page.content()
            print(f"   ✅ 页面内容预览: {page_content}")
            
            browser.close()
            print("\n🎉 Chrome连接测试完全成功!")
            return True
            
        except Exception as e:
            print(f"\n❌ 连接失败: {e}")
            print("\n🔧 故障排除建议:")
            print("1. 确保Chrome已启动并启用远程调试:")
            print("   google-chrome --remote-debugging-port=18792")
            print("2. 安装OpenClaw Browser Relay扩展")
            print("3. 点击工具栏的OpenClaw图标连接标签页")
            print("4. 检查端口18792是否被占用")
            return False

if __name__ == "__main__":
    print("🚀 Chrome Browser Relay连接测试")
    print("=" * 50)
    print("请确保:")
    print("1. Chrome浏览器正在运行")
    print("2. 已启用远程调试端口18792")
    print("3. OpenClaw Browser Relay扩展已安装并连接")
    print("=" * 50)
    
    success = test_chrome_connection()
    
    if success:
        print("\n✅ 现在可以运行爬虫:")
        print("   python3 src/scrape_xiaohongshu_chrome.py")
    else:
        print("\n❌ 请先解决连接问题")
        print("   参考: RUN_CHROME_GUIDE.md")