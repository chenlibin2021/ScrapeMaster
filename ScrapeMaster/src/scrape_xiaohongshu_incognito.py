#!/usr/bin/env python3
"""
小红书评论爬虫 - 隐身模式版本
专注抓取带联系方式的评论，使用隐身浏览器避免cookie干扰
"""
import json
import re
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright
import pandas as pd

# 优化后的联系方式检测正则（专注常用联系方式）
CONTACT_PATTERNS = {
    'wechat': [
        # 微信 - 最常用的联系方式（支持中文ID）
        r'(?:微信|微[信xX]|wx|wechat)[:：\s联系]*([a-zA-Z0-9_.\u4e00-\u9fa5-]{3,20})',
        r'加[我]?[微V][信xX][:：\s]*([a-zA-Z0-9_.\u4e00-\u9fa5-]{3,20})',
        r'微[信xX][:：\s]*([a-zA-Z0-9_.\u4e00-\u9fa5-]{3,20})',
        r'扫码加[微V][信xX]?',
    ],
    'phone': [
        # 电话 - 中国手机号
        r'\b(1[3-9]\d{9})\b',
        # 电话 - 带格式（加拿大本地）
        r'\b(\d{3}[-\s]?\d{3}[-\s]?\d{4})\b',
        # 电话关键词
        r'[电☎️📞]话[:：\s]*(\d{7,})',
        # 手机号
        r'手机[号]?[:：\s]*(\d{7,})',
    ],
    'whatsapp': [
        # WhatsApp - 海外常用（避免与phone冲突）
        r'(?:whatsapp|wa|WhatsApp)[:：\s]*([+]\d[\d\s-]{9,})(?!.*(?:电话|手机|phone))',
        r'\bwhatsapp\b.*?([+]\d[\d\s-]{9,})',
    ],
    'email': [
        # 邮箱 - 商务联系
        r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'邮箱[:：\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    ],
    'instagram': [
        # Instagram - 年轻用户常用
        r'(?:ins|instagram|IG)[:：\s]*@?([a-zA-Z0-9_.]{1,30})',
        r'@([a-zA-Z0-9_.]{1,30})(?=\s*(?:ins|instagram|IG|$))',
    ],
}

def has_contact_info(text):
    """检测文本是否包含联系方式"""
    if not text:
        return False, []
    
    found_types = []
    for contact_type, patterns in CONTACT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                found_types.append(contact_type)
                break
    
    return len(found_types) > 0, found_types

def extract_contact_details(text):
    """提取具体的联系方式 - 优化版避免冲突"""
    if not text:
        return {}
    
    details = {}
    
    # 按优先级顺序处理，避免冲突
    # 1. whatsapp优先（避免被误判为phone）
    # 2. wechat
    # 3. phone  
    # 4. email
    # 5. instagram
    priority_order = ['whatsapp', 'wechat', 'phone', 'email', 'instagram']
    
    for contact_type in priority_order:
        patterns = CONTACT_PATTERNS.get(contact_type, [])
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            contact_matches = []
            
            for match in matches:
                groups = match.groups()
                if groups:
                    for group in groups:
                        if group and group.strip():
                            cleaned = group.strip()
                            if cleaned and cleaned not in contact_matches:
                                contact_matches.append(cleaned)
                            break
                else:
                    full_match = match.group(0).strip()
                    if full_match and full_match not in contact_matches:
                        contact_matches.append(full_match)
            
            if contact_matches:
                details[contact_type] = contact_matches
                break  # 找到一种模式就停止
    
    return details

def scrape_sharon_comments_incognito(proxies=None, max_notes=None, headless=False):
    """
    抓取Sharon多伦多地产的笔记评论 - 隐身模式
    proxies: 代理列表
    max_notes: 最多抓取多少条笔记（None = 全部）
    headless: 是否无头模式（True = 隐藏浏览器界面）
    """
    
    results = []
    
    with sync_playwright() as p:
        # 启动隐身浏览器
        print("🚀 启动隐身浏览器...")
        try:
            # 启动Chromium浏览器，使用隐身模式
            browser = p.chromium.launch(
                headless=headless,  # 控制是否显示浏览器界面
                args=[
                    '--incognito',  # 隐身模式
                    '--disable-blink-features=AutomationControlled',  # 避免被检测为自动化
                    '--disable-dev-shm-usage',  # 避免内存问题
                    '--no-sandbox',  # Docker/容器环境需要
                ]
            )
            
            # 创建隐身上下文
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                bypass_csp=True,  # 绕过内容安全策略
            )
            
            page = context.new_page()
            
            print(f"✅ 隐身浏览器已启动 ({'无头模式' if headless else '可见模式'})")
            
        except Exception as e:
            print(f"❌ 启动浏览器失败: {e}")
            print("请确保Playwright Chromium已正确安装")
            print("运行: python3 -m playwright install chromium")
            return results
        
        try:
            # 访问Sharon的主页
            sharon_profile_url = "https://www.xiaohongshu.com/user/profile/59e2f0de153c3c1961a1deb4"
            print(f"📍 访问 Sharon 主页: {sharon_profile_url}")
            
            page.goto(sharon_profile_url, timeout=30000)
            time.sleep(3)
            
            # 检查是否需要登录
            page_content = page.content()
            if "登录" in page_content or "login" in page_content.lower():
                print("⚠️  检测到登录页面，小红书可能需要登录才能查看完整内容")
                print("   尝试继续访问，但可能只能看到有限内容")
            
            # 滚动加载更多笔记
            print("📜 滚动加载笔记列表...")
            for i in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
                print(f"   滚动 {i+1}/5 完成")
            
            # 获取所有笔记链接
            note_links = page.evaluate("""
                () => {
                    const links = [];
                    const elements = document.querySelectorAll('a[href*="/explore/"]');
                    elements.forEach(el => {
                        const href = el.getAttribute('href');
                        if (href && href.includes('/explore/')) {
                            const fullUrl = href.startsWith('http') ? href : 'https://www.xiaohongshu.com' + href;
                            if (!links.includes(fullUrl)) {
                                links.push(fullUrl);
                            }
                        }
                    });
                    return links.slice(0, 20);  # 限制数量避免过多请求
                }
            """)
            
            print(f"✅ 找到 {len(note_links)} 条笔记")
            
            if max_notes:
                note_links = note_links[:max_notes]
                print(f"📌 限制为前 {max_notes} 条")
            
            # 遍历每条笔记
            for idx, note_url in enumerate(note_links, 1):
                print(f"\n[{idx}/{len(note_links)}] 处理笔记: {note_url[:60]}...")
                
                try:
                    page.goto(note_url, timeout=30000)
                    time.sleep(3)
                    
                    # 获取笔记标题
                    note_title = page.evaluate("""
                        () => {
                            const titleEl = document.querySelector('h1, .title, [class*="title"]');
                            return titleEl ? titleEl.innerText : '无标题';
                        }
                    """) or "无标题"
                    
                    print(f"  📝 标题: {note_title[:50]}...")
                    
                    # 滚动加载评论
                    print(f"  💬 加载评论...")
                    for _ in range(3):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(1.5)
                    
                    # 点击"展开更多评论"按钮（如果有）
                    try:
                        expand_buttons = page.query_selector_all('button:has-text("展开"), button:has-text("更多")')
                        for btn in expand_buttons[:3]:
                            btn.click()
                            time.sleep(1)
                    except:
                        pass
                    
                    # 提取评论
                    comments = page.evaluate("""
                        () => {
                            const comments = [];
                            const commentEls = document.querySelectorAll('[class*="comment"], .note-item, [class*="Comment"]');
                            
                            commentEls.forEach(el => {
                                const userEl = el.querySelector('[class*="user"], [class*="name"], .author');
                                const contentEl = el.querySelector('[class*="content"], [class*="text"], p');
                                const timeEl = el.querySelector('[class*="time"], [class*="date"], time');
                                
                                if (contentEl && contentEl.innerText.trim()) {
                                    comments.push({
                                        user: userEl ? userEl.innerText.trim() : '未知用户',
                                        content: contentEl.innerText.trim(),
                                        time: timeEl ? timeEl.innerText.trim() : ''
                                    });
                                }
                            });
                            
                            return comments;
                        }
                    """)
                    
                    print(f"  📊 提取到 {len(comments)} 条评论")
                    
                    # 过滤包含联系方式的评论
                    filtered_count = 0
                    for comment in comments:
                        has_contact, contact_types = has_contact_info(comment['content'])
                        
                        if has_contact:
                            filtered_count += 1
                            contact_details = extract_contact_details(comment['content'])
                            
                            results.append({
                                '笔记标题': note_title,
                                '笔记链接': note_url,
                                '用户名': comment['user'],
                                '评论内容': comment['content'],
                                '评论时间': comment['time'],
                                '联系方式类型': ', '.join(contact_types),
                                '提取的联系方式': json.dumps(contact_details, ensure_ascii=False),
                                '抓取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            })
                    
                    if filtered_count > 0:
                        print(f"  ✅ 发现 {filtered_count} 条包含联系方式的评论")
                    else:
                        print(f"  ⚠️  未发现包含联系方式的评论")
                    
                    # 随机延迟，避免被封
                    delay = random.uniform(3, 6)
                    print(f"  ⏳ 等待 {delay:.1f} 秒后继续...")
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"  ❌ 处理笔记出错: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ 抓取过程出错: {e}")
        
        finally:
            # 关闭浏览器
            print("\n🏁 抓取完成，关闭浏览器...")
            try:
                browser.close()
            except:
                pass
    
    return results

def main():
    print("=" * 60)
    print("小红书评论爬虫 - 隐身模式")
    print("目标：抓取Sharon多伦多地产的评论（使用隐身浏览器）")
    print("=" * 60)
    
    # 加载代理（可选）
    proxies = None
    try:
        with open('data/working_proxies.json', 'r') as f:
            proxy_data = json.load(f)
            proxies = [p['proxy'] for p in proxy_data]
            print(f"✅ 加载了 {len(proxies)} 个代理")
    except:
        print("⚠️  未找到代理配置，使用当前网络")
    
    # 用户选择模式
    print("\n🎯 选择运行模式:")
    print("1. 可见模式 (显示浏览器界面)")
    print("2. 无头模式 (隐藏浏览器界面，更快)")
    
    choice = input("请输入选择 (1 或 2，默认 2): ").strip()
    headless = choice != "1"
    
    # 设置抓取数量
    try:
        max_notes = int(input("请输入最多抓取笔记数 (默认 5): ").strip() or "5")
    except:
        max_notes = 5
        print(f"使用默认值: {max_notes}")
    
    print(f"\n🚀 开始抓取 ({'无头模式' if headless else '可见模式'})...")
    print(f"📌 最多抓取 {max_notes} 条笔记")
    
    # 开始抓取
    results = scrape_sharon_comments_incognito(
        proxies=proxies, 
        max_notes=max_notes,
        headless=headless
    )
    
    if results:
        # 保存为Excel
        df = pd.DataFrame(results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'sharon_comments_incognito_{timestamp}.xlsx'
        
        df.to_excel(output_file, index=False, engine='openpyxl')
        
        print(f"\n🎉 成功！")
        print(f"📁 文件已保存: {output_file}")
        print(f"📊 总共找到 {len(results)} 条包含联系方式的评论")
        
        # 统计联系方式类型
        contact_type_counts = {}
        for r in results:
            types = r['联系方式类型'].split(', ')
            for t in types:
                contact_type_counts[t] = contact_type_counts.get(t, 0) + 1
        
        print("\n📈 联系方式分布:")
        for ctype, count in sorted(contact_type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {ctype}: {count} 条")
        
        # 显示示例
        print("\n📋 示例结果 (前3条):")
        for i, r in enumerate(results[:3], 1):
            print(f"\n示例 {i}:")
            print(f"  用户: {r['用户名']}")
            print(f"  内容: {r['评论内容'][:60]}...")
            print(f"  类型: {r['联系方式类型']}")
            details = json.loads(r['提取的联系方式'])
            for ctype, values in details.items():
                print(f"  {ctype}: {', '.join(values[:2])}")
    else:
        print("\n⚠️  未找到包含联系方式的评论")
        print("可能的原因:")
        print("1. 小红书需要登录才能查看完整内容")
        print("2. 该博主没有包含联系方式的评论")
        print("3. 反爬虫机制阻止了访问")
        print("4. 网络连接问题")

if __name__ == "__main__":
    main()