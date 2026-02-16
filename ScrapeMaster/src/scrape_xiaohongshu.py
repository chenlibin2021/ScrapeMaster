#!/usr/bin/env python3
"""
小红书评论爬虫 - 专注抓取带联系方式的评论
"""
import json
import re
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright
import pandas as pd

# 联系方式检测正则
CONTACT_PATTERNS = {
    'wechat': [
        r'[微V信][信xX][:：\s]*([a-zA-Z0-9_-]{5,20})',
        r'wx[:：\s]*([a-zA-Z0-9_-]{5,20})',
        r'加我?[微V][信xX]',
        r'扫码加[微V]',
    ],
    'phone': [
        r'(\d{3}[-\s]?\d{3}[-\s]?\d{4})',  # 北美电话
        r'(\d{3}[-\s]?\d{4}[-\s]?\d{4})',  # 中国电话
        r'[电☎️📞]话[:：\s]*(\d[\d\s-]{7,})',
    ],
    'qq': [
        r'QQ[:：\s]*(\d{5,11})',
        r'[扣抠][:：\s]*(\d{5,11})',
    ],
    'email': [
        r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    ],
    'whatsapp': [
        r'whatsapp[:：\s]*([+\d\s-]{10,})',
        r'wa[:：\s]*([+\d\s-]{10,})',
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
    """提取具体的联系方式"""
    contacts = {}
    
    for contact_type, patterns in CONTACT_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if contact_type not in contacts:
                    contacts[contact_type] = []
                contacts[contact_type].extend(matches)
    
    return contacts

def scrape_sharon_comments(proxies=None, max_notes=None):
    """
    抓取Sharon多伦多地产的笔记评论
    proxies: 代理列表
    max_notes: 最多抓取多少条笔记（None = 全部）
    """
    
    results = []
    
    with sync_playwright() as p:
        # 启动浏览器（连接到已有的Chrome）
        print("🔗 连接到Chrome浏览器...")
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:18792")
        except Exception as e:
            print(f"❌ 无法连接到Chrome: {e}")
            print("请确保Chrome浏览器已打开并启用了Browser Relay")
            return results
        
        context = browser.contexts[0]
        page = context.pages[0]
        
        # 访问Sharon的主页
        sharon_profile_url = "https://www.xiaohongshu.com/user/profile/59e2f0de153c3c1961a1deb4"
        print(f"📍 访问 Sharon 主页...")
        
        try:
            page.goto(sharon_profile_url, timeout=30000)
            time.sleep(3)
            
            # 滚动加载更多笔记
            print("📜 滚动加载笔记列表...")
            for _ in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
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
                    return links;
                }
            """)
            
            print(f"✅ 找到 {len(note_links)} 条笔记")
            
            if max_notes:
                note_links = note_links[:max_notes]
                print(f"📌 限制为前 {max_notes} 条")
            
            # 遍历每条笔记
            for idx, note_url in enumerate(note_links, 1):
                print(f"\n[{idx}/{len(note_links)}] 处理笔记: {note_url}")
                
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
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    print(f"  ❌ 处理笔记出错: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ 抓取过程出错: {e}")
        
        finally:
            print("\n🏁 抓取完成")
    
    return results

def main():
    print("=" * 60)
    print("小红书评论爬虫 - Sharon多伦多地产")
    print("目标：抓取包含联系方式的评论")
    print("=" * 60)
    
    # 加载代理（可选）
    proxies = None
    try:
        with open('/home/chenlibin/.openclaw/workspace/working_proxies.json', 'r') as f:
            proxy_data = json.load(f)
            proxies = [p['proxy'] for p in proxy_data]
            print(f"✅ 加载了 {len(proxies)} 个代理")
    except:
        print("⚠️  未找到代理配置，使用当前网络")
    
    # 开始抓取（先测试5条笔记）
    print("\n🚀 开始抓取（测试模式：前10条笔记）...")
    results = scrape_sharon_comments(proxies=proxies, max_notes=10)
    
    if results:
        # 保存为Excel
        df = pd.DataFrame(results)
        output_file = f'/home/chenlibin/.openclaw/workspace/sharon_comments_with_contacts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
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
    else:
        print("\n⚠️  未找到包含联系方式的评论")

if __name__ == "__main__":
    main()
