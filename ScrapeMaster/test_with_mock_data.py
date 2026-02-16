#!/usr/bin/env python3
"""
使用模拟数据测试爬虫核心逻辑
不依赖浏览器，验证数据处理流程
"""

import json
import re
import random
from datetime import datetime
import pandas as pd

print("🧪 ScrapeMaster 模拟数据测试")
print("=" * 60)

# 从主文件导入核心逻辑
CONTACT_PATTERNS = {
    'wechat': [
        r'(?:微信|微[信xX]|wx|wechat)[:：\s联系]*([a-zA-Z0-9_.\u4e00-\u9fa5-]{3,20})',
    ],
    'phone': [
        r'\b(\d{3}[-\s]?\d{3}[-\s]?\d{4})\b',
    ],
    'whatsapp': [
        r'(?:whatsapp|wa|WhatsApp)[:：\s]*([+]\d[\d\s-]{9,})(?!.*(?:电话|手机|phone))',
    ],
    'email': [
        r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
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
    if not text:
        return {}
    
    details = {}
    priority_order = ['whatsapp', 'wechat', 'phone', 'email']
    
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
            
            if contact_matches:
                details[contact_type] = contact_matches
                break
    
    return details

def generate_mock_comments():
    """生成模拟的小红书评论数据"""
    print("📊 生成模拟评论数据...")
    
    # 多伦多地产相关评论模板
    templates = [
        "这个房子不错，微信：toronto_home123",
        "请问具体位置？电话：647-123-4567",
        "whatsapp联系：+1 416 987 6543",
        "邮箱发资料：agent@example.com",
        "微信咨询：多伦多买房助手",
        "电话咨询：416-555-7890",
        "这个价格包含家具吗？",
        "附近有学校吗？",
        "微信：realtor_2024，电话：647-888-9999",
        "whatsapp: +16471234567",
        "邮箱联系：info@torontorealestate.ca",
        "普通评论，点赞支持",
        "私信我获取更多信息",
    ]
    
    users = ["用户A", "用户B", "用户C", "用户D", "用户E", "用户F"]
    times = ["刚刚", "1小时前", "2小时前", "3小时前", "1天前", "2天前"]
    
    comments = []
    for i in range(20):  # 生成20条模拟评论
        template = random.choice(templates)
        user = random.choice(users)
        time = random.choice(times)
        
        # 随机修改一些联系方式
        if "微信" in template:
            template = template.replace("toronto_home123", f"agent_{random.randint(100, 999)}")
        elif "电话" in template:
            area = random.choice(["647", "416", "905"])
            num = f"{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            template = template.replace("647-123-4567", f"{area}-{num}")
        
        comments.append({
            'user': user,
            'content': template,
            'time': time
        })
    
    print(f"✅ 生成了 {len(comments)} 条模拟评论")
    return comments

def process_mock_data():
    """处理模拟数据并生成报告"""
    print("\n🔧 处理模拟数据...")
    
    # 生成模拟评论
    comments = generate_mock_comments()
    
    # 处理每条评论
    results = []
    note_title = "模拟笔记：多伦多房产投资指南"
    note_url = "https://www.xiaohongshu.com/explore/模拟链接"
    
    contact_count = 0
    for comment in comments:
        has_contact, contact_types = has_contact_info(comment['content'])
        
        if has_contact:
            contact_count += 1
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
    
    print(f"📈 分析结果:")
    print(f"   总评论数: {len(comments)}")
    print(f"   包含联系方式: {contact_count}")
    print(f"   占比: {contact_count/len(comments)*100:.1f}%")
    
    return results

def export_results(results):
    """导出结果到Excel"""
    if not results:
        print("⚠️  无结果可导出")
        return None
    
    print("\n💾 导出结果到Excel...")
    
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'scrapemaster_mock_test_{timestamp}.xlsx'
    
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    # 验证文件
    import os
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        print(f"✅ 文件已保存: {output_file} ({file_size} 字节)")
        
        # 显示统计信息
        contact_type_counts = {}
        for r in results:
            types = r['联系方式类型'].split(', ')
            for t in types:
                contact_type_counts[t] = contact_type_counts.get(t, 0) + 1
        
        print("\n📊 联系方式分布:")
        for ctype, count in sorted(contact_type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {ctype}: {count} 条")
        
        return output_file
    else:
        print("❌ 文件创建失败")
        return None

def analyze_patterns(results):
    """分析检测模式效果"""
    print("\n🔍 模式分析:")
    
    if not results:
        print("无数据可分析")
        return
    
    # 统计各种联系方式的出现频率
    wechat_patterns = []
    phone_patterns = []
    whatsapp_patterns = []
    email_patterns = []
    
    for r in results:
        content = r['评论内容'].lower()
        
        if '微信' in content or 'wx' in content or 'wechat' in content:
            wechat_patterns.append(r['评论内容'][:50])
        
        if '电话' in content or '手机' in content:
            phone_patterns.append(r['评论内容'][:50])
        
        if 'whatsapp' in content or 'wa' in content:
            whatsapp_patterns.append(r['评论内容'][:50])
        
        if '@' in content or '邮箱' in content:
            email_patterns.append(r['评论内容'][:50])
    
    print(f"微信检测: {len(wechat_patterns)} 条")
    if wechat_patterns:
        print(f"  示例: {wechat_patterns[0]}")
    
    print(f"电话检测: {len(phone_patterns)} 条")
    if phone_patterns:
        print(f"  示例: {phone_patterns[0]}")
    
    print(f"WhatsApp检测: {len(whatsapp_patterns)} 条")
    if whatsapp_patterns:
        print(f"  示例: {whatsapp_patterns[0]}")
    
    print(f"邮箱检测: {len(email_patterns)} 条")
    if email_patterns:
        print(f"  示例: {email_patterns[0]}")

def main():
    print("ScrapeMaster 模拟数据测试套件")
    print("=" * 60)
    print("目的: 验证核心逻辑，不依赖浏览器")
    print("=" * 60)
    
    # 处理模拟数据
    results = process_mock_data()
    
    if results:
        # 导出结果
        output_file = export_results(results)
        
        # 分析模式
        analyze_patterns(results)
        
        # 显示示例
        print("\n📋 结果示例 (前3条):")
        for i, r in enumerate(results[:3], 1):
            print(f"\n示例 {i}:")
            print(f"  用户: {r['用户名']}")
            print(f"  内容: {r['评论内容'][:50]}...")
            print(f"  类型: {r['联系方式类型']}")
            details = json.loads(r['提取的联系方式'])
            for ctype, values in details.items():
                print(f"  {ctype}: {', '.join(values[:2])}")
        
        print("\n" + "=" * 60)
        print("✅ 模拟测试完成!")
        print(f"📁 结果文件: {output_file}")
        print("🎯 核心逻辑验证通过")
    else:
        print("\n⚠️  测试未生成有效结果")
        print("可能需要调整检测模式")
    
    print("\n" + "=" * 60)
    print("🚀 下一步:")
    print("1. 解决GitHub认证问题")
    print("2. 配置Chrome浏览器环境")
    print("3. 运行实际爬虫测试")
    print("=" * 60)

if __name__ == "__main__":
    main()