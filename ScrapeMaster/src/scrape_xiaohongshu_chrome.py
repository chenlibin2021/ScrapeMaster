#!/usr/bin/env python3
"""
小红书评论爬虫 - 使用系统Chrome浏览器
专注抓取带联系方式的评论，使用现有Chrome实例
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
                break
    
    return details

def scrape_sharon_comments_chrome(proxies=None, max_notes=None):
    """
    抓取Sharon多伦多地产的笔记评论 - 使用系统Chrome
    proxies: 代理列表
    max_notes: 最多抓取多少条笔记（None = 全部）
    """
    
    results = []
    
    with sync_playwright() as p:
        print("🔗 尝试连接到系统Chrome浏览器...")
        
        try:
            # 方法1：尝试连接到已运行的Chrome（通过Browser Relay）
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:18792")
            print("✅ 连接到已运行的Chrome浏览器（Browser Relay）")
            
        except Exception as e:
            print(f"❌ 无法连接到现有Chrome: {e}")
            print("请确保：")
            print("1. Chrome浏览器已打开")
            print("2. 已安装OpenClaw Browser Relay扩展")
            print("3. 在目标标签页点击了OpenClaw工具栏图标")
            return results
        
        try:
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            # 访问Sharon的主页
            sharon_profile_url = "https://www.xiaohongshu.com/user/profile/59e2f0de153c3c1961a1deb4"
            print(f"📍 访问 Sharon 主页: {sharon_profile_url}")
            
            page.goto(sharon_profile_url, timeout=30000)
            time.sleep(3)
            
            # 检查页面内容
            page_title = page.title()
            print(f"📄 页面标题: {page_title}")
            
            # 检查是否需要登录
            page_content = page.content()
            if "登录" in page_content or "login" in page_content.lower():
                print("⚠️  检测到登录页面，小红书可能需要登录才能查看完整内容")
                print("   请先手动登录小红书，然后重新运行爬虫")
                return results
            
            # 滚动加载更多笔记
            print("📜 滚动加载笔记列表...")
            for i in range(3):  # 减少滚动次数，避免被封
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
                print(f"   滚动 {i+1}/3 完成")
            
            # 获取所有笔记链接（简化选择器）
            note_links = page.evaluate("""
                () => {
                    const links = [];
                    // 尝试多种选择器
                    const selectors = [
                        'a[href*="/explore/"]',
                        'a[href*="/discovery/"]',
                        '.note-item a',
                        '[class*="note"] a'
                    ];
                    
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            const href = el.getAttribute('href');
                            if (href && (href.includes('/explore/') || href.includes('/discovery/'))) {
                                const fullUrl = href.startsWith('http') ? href : 'https://www.xiaohongshu.com' + href;
                                if (!links.includes(fullUrl)) {
                                    links.push(fullUrl);
                                }
                            }
                        }
                        if (links.length > 0) break;
                    }
                    
                    return links.slice(0, 10);  # 限制数量
                }
            """)
            
            print(f"✅ 找到 {len(note_links)} 条笔记")
            
            if max_notes and len(note_links) > max_notes:
                note_links = note_links[:max_notes]
                print(f"📌 限制为前 {max_notes} 条")
            
            if not note_links:
                print("⚠️  未找到笔记链接，可能：")
                print("   1. 页面结构已变化")
                print("   2. 需要登录才能查看")
                print("   3. 反爬虫机制阻止")
                return results
            
            # 遍历每条笔记
            for idx, note_url in enumerate(note_links, 1):
                print(f"\n[{idx}/{len(note_links)}] 处理笔记...")
                
                try:
                    # 在新标签页中打开笔记
                    new_page = context.new_page()
                    new_page.goto(note_url, timeout=30000)
                    time.sleep(3)
                    
                    # 获取笔记标题
                    note_title = new_page.evaluate("""
                        () => {
                            // 尝试多种标题选择器
                            const selectors = [
                                'h1',
                                '.title',
                                '[class*="title"]',
                                '[class*="Title"]',
                                'header h1',
                                'header h2'
                            ];
                            
                            for (const selector of selectors) {
                                const el = document.querySelector(selector);
                                if (el && el.innerText.trim()) {
                                    return el.innerText.trim();
                                }
                            }
                            return '无标题';
                        }
                    """) or "无标题"
                    
                    print(f"  📝 标题: {note_title[:50]}...")
                    
                    # 滚动加载评论
                    print(f"  💬 加载评论...")
                    for _ in range(2):  # 减少滚动
                        new_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(2)
                    
                    # 提取评论
                    comments = new_page.evaluate("""
                        () => {
                            const comments = [];
                            // 尝试多种评论选择器
                            const selectors = [
                                '[class*="comment"]',
                                '[class*="Comment"]',
                                '.note-item',
                                '.comment-item',
                                '.comment-list li',
                                '.comment-content'
                            ];
                            
                            for (const selector of selectors) {
                                const elements = document.querySelectorAll(selector);
                                if (elements.length > 0) {
                                    elements.forEach(el => {
                                        const userEl = el.querySelector('[class*="user"], [class*="name"], .author, .username');
                                        const contentEl = el.querySelector('[class*="content"], [class*="text"], p, .text, .comment-text');
                                        const timeEl = el.querySelector('[class*="time"], [class*="date"], time, .timestamp');
                                        
                                        if (contentEl && contentEl.innerText.trim()) {
                                            comments.push({
                                                user: userEl ? userEl.innerText.trim() : '未知用户',
                                                content: contentEl.innerText.trim(),
                                                time: timeEl ? timeEl.innerText.trim() : ''
                                            });
                                        }
                                    });
                                    break;
                                }
                            }
                            
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
                    
                    # 关闭标签页
                    new_page.close()
                    
                    # 随机延迟
                    delay = random.uniform(4, 8)
                    print(f"  ⏳ 等待 {delay:.1f} 秒后继续...")
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"  ❌ 处理笔记出错: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ 抓取过程出错: {e}")
        
        finally:
            print("\n🏁 抓取完成")
            # 不关闭浏览器，让用户继续使用
    
    return results

def main():
    print("=" * 60)
    print("小红书评论爬虫 - 系统Chrome版本")
    print("目标：抓取Sharon多伦多地产的评论（使用现有Chrome浏览器）")
    print("=" * 60)
    
    print("\n⚠️  重要提示：")
    print("1. 请先打开Chrome浏览器")
    print("2. 安装OpenClaw Browser Relay扩展")
    print("3. 访问小红书并登录（如果需要）")
    print("4. 在小红书页面点击OpenClaw工具栏图标")
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
    
    # 设置抓取数量
    max_notes = 3  # 测试模式，少量笔记
    print(f"\n🚀 开始测试抓取...")
    print(f"📌 最多抓取 {max_notes} 条笔记（测试模式）")
    
    input("按Enter键开始抓取（确保Chrome已连接）...")
    
    # 开始抓取
    results = scrape_sharon_comments_chrome(
        proxies=proxies, 
        max_notes=max_notes
    )
    
    if results:
        # 保存为Excel
        df = pd.DataFrame(results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'sharon_comments_chrome_{timestamp}.xlsx'
        
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
        print("\n📋 示例结果:")
        for i, r in enumerate(results[:2], 1):
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
        print("3. Chrome浏览器未正确连接")
        print("4. 页面结构已变化，需要更新选择器")

if __name__ == "__main__":
    main()