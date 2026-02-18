#!/usr/bin/env python3
"""
测试通过OpenClaw Gateway连接到Chrome
"""

from playwright.sync_api import sync_playwright

def test_openclaw_gateway():
    """测试OpenClaw Gateway连接"""
    print("🔗 测试OpenClaw Gateway浏览器连接")
    print("=" * 50)
    
    with sync_playwright() as p:
        print("1. 初始化Playwright... ✅")
        
        try:
            print("2. 连接到OpenClaw Gateway WebSocket...")
            # 使用WebSocket连接（Browser Relay使用ws://）
            browser = p.chromium.connect_over_cdp("ws://127.0.0.1:18792/cdp")
            print("   ✅ 连接成功!")
            
            print("3. 获取浏览器上下文...")
            # 获取第一个上下文或创建新上下文
            if browser.contexts:
                context = browser.contexts[0]
                print(f"   ✅ 使用现有上下文")
            else:
                context = browser.new_context()
                print(f"   ✅ 创建新上下文")
            
            print("4. 获取或创建页面...")
            if context.pages:
                page = context.pages[0]
                print(f"   ✅ 使用现有页面: {page.url}")
            else:
                page = context.new_page()
                print(f"   ✅ 创建新页面")
                page.goto("https://www.xiaohongshu.com")
                print(f"   ✅ 导航到小红书: {page.url}")
            
            print("5. 测试页面操作...")
            title = page.title()
            print(f"   ✅ 页面标题: {title}")
            
            # 获取当前URL
            current_url = page.url
            print(f"   ✅ 当前URL: {current_url}")
            
            # 简单页面交互测试
            if "xiaohongshu" in current_url:
                print("6. 检测到小红书页面，测试元素查找...")
                try:
                    # 尝试查找常见元素
                    page.wait_for_load_state("networkidle")
                    
                    # 检查页面内容
                    content = page.content()[:500]
                    print(f"   ✅ 页面内容预览: {content[:100]}...")
                    
                    # 检查是否有登录相关元素
                    login_elements = page.locator("text=登录").count()
                    if login_elements > 0:
                        print(f"   ⚠️  检测到登录提示 ({login_elements}处)")
                    else:
                        print("   ✅ 页面似乎已登录或不需要登录")
                        
                except Exception as e:
                    print(f"   ⚠️  页面交互测试跳过: {e}")
            
            print("\n🎉 OpenClaw Gateway连接测试完全成功!")
            print("\n🚀 现在可以运行爬虫:")
            print("   python3 src/scrape_xiaohongshu_chrome.py")
            
            # 保持浏览器打开供爬虫使用
            return True, browser
            
        except Exception as e:
            print(f"\n❌ 连接失败: {e}")
            print("\n🔧 故障排除建议:")
            print("1. 确保OpenClaw Gateway正在运行")
            print("2. 确保Chrome浏览器已打开")
            print("3. 确保OpenClaw Browser Relay扩展已连接")
            print("4. 检查OpenClaw Gateway日志")
            return False, None

if __name__ == "__main__":
    print("🚀 OpenClaw Gateway浏览器连接测试")
    print("=" * 50)
    print("前提条件:")
    print("1. OpenClaw Gateway正在运行")
    print("2. Chrome浏览器已打开")
    print("3. OpenClaw Browser Relay扩展已连接")
    print("=" * 50)
    
    success, browser = test_openclaw_gateway()
    
    if not success:
        print("\n❌ 测试失败，请检查上述条件")
        exit(1)