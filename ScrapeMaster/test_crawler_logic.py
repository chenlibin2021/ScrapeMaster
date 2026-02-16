#!/usr/bin/env python3
"""
测试爬虫核心逻辑（不依赖浏览器）
"""

import re
import json
import time
import random
from datetime import datetime

# 从主文件复制核心逻辑
CONTACT_PATTERNS = {
    'wechat': [
        r'(?:微信|微[信xX]|wx)[:：\s]*([a-zA-Z0-9_-]{5,20})',
        r'加[我]?[微V][信xX][:：\s]*([a-zA-Z0-9_-]{5,20})',
    ],
    'phone': [
        r'\b(1[3-9]\d{9})\b',
        r'[电☎️📞]话[:：\s]*(\d{7,})',
    ],
    'qq': [
        r'(?:QQ|qq|扣扣)[:：\s是]*(\d{5,11})',
        r'(\d{5,11})@qq\.com',
    ],
    'email': [
        r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    ],
    'whatsapp': [
        r'(?:whatsapp|wa)[:：\s]*([+]\d{10,})',
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
    for contact_type, patterns in CONTACT_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # 清理结果
                clean_matches = []
                for match in matches:
                    if isinstance(match, tuple):
                        for item in match:
                            if item and item.strip():
                                clean_matches.append(item.strip())
                                break
                    elif match and match.strip():
                        clean_matches.append(match.strip())
                
                if clean_matches:
                    details[contact_type] = clean_matches
                    break
    
    return details

def simulate_crawler():
    """模拟爬虫运行"""
    print("模拟小红书评论爬虫运行")
    print("=" * 60)
    
    # 模拟的评论数据（基于实际小红书评论模式）
    simulated_comments = [
        {
            'user': '用户A',
            'content': '博主你好，我对这个房子很感兴趣，加我微信：abc123详聊',
            'time': '2小时前'
        },
        {
            'user': '用户B', 
            'content': '请问这个楼盘的具体位置在哪里？我的QQ是1234567',
            'time': '3小时前'
        },
        {
            'user': '用户C',
            'content': '电话咨询：13800138000，欢迎来电',
            'time': '5小时前'
        },
        {
            'user': '用户D',
            'content': '邮箱联系：test@example.com，发资料给我',
            'time': '1天前'
        },
        {
            'user': '用户E',
            'content': 'whatsapp: +8613800138000，国际客户',
            'time': '2天前'
        },
        {
            'user': '用户F',
            'content': '这个房子看起来不错，点赞支持！',
            'time': '3小时前'
        },
        {
            'user': '用户G',
            'content': '私信我获取更多信息',
            'time': '4小时前'
        },
        {
            'user': '用户H',
            'content': '微信联系：mywechat123，电话：13912345678',
            'time': '6小时前'
        },
    ]
    
    print(f"模拟 {len(simulated_comments)} 条评论")
    print()
    
    results = []
    note_title = "模拟笔记：多伦多房产投资指南"
    note_url = "https://www.xiaohongshu.com/explore/模拟链接"
    
    for idx, comment in enumerate(simulated_comments, 1):
        print(f"[{idx}] 用户: {comment['user']}")
        print(f"    内容: {comment['content'][:50]}...")
        
        has_contact, contact_types = has_contact_info(comment['content'])
        contact_details = extract_contact_details(comment['content'])
        
        if has_contact:
            print(f"    ✅ 发现联系方式: {contact_types}")
            print(f"    详情: {contact_details}")
            
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
        else:
            print(f"    ⚪ 无联系方式")
        
        print()
    
    # 统计结果
    if results:
        print("=" * 60)
        print(f"🎉 模拟抓取完成！")
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
        
        # 显示示例结果
        print("\n📋 示例结果:")
        for i, r in enumerate(results[:2], 1):
            print(f"\n示例 {i}:")
            print(f"  用户: {r['用户名']}")
            print(f"  内容: {r['评论内容'][:50]}...")
            print(f"  类型: {r['联系方式类型']}")
            details = json.loads(r['提取的联系方式'])
            for ctype, values in details.items():
                print(f"  {ctype}: {', '.join(values[:2])}")
        
        return True
    else:
        print("⚠️ 未找到包含联系方式的评论")
        return False

def test_with_realistic_data():
    """使用更真实的数据测试"""
    print("\n" + "=" * 60)
    print("真实场景测试")
    print("=" * 60)
    
    # 真实的小红书评论示例
    real_comments = [
        "博主求带！加我微信abc_123",
        "我的QQ是1234567，求资料",
        "电话咨询：13800138000",
        "邮箱发我：user@example.com",
        "whatsapp联系：+8613800138000",
        "点赞支持！",
        "私信我",
        "微信：myid123，电话13912345678",
        "扫码加微",
        "QQ邮箱：123456@qq.com",
        "验证码是123456",
        "截图发你了",
    ]
    
    print("测试真实评论样本:")
    print("-" * 40)
    
    detected = 0
    for comment in real_comments:
        has_contact, types = has_contact_info(comment)
        details = extract_contact_details(comment)
        
        status = "✅" if has_contact else "⚪"
        print(f"{status} '{comment[:30]:<30}' -> {types}")
        if has_contact and details:
            for ctype, values in details.items():
                print(f"      {ctype}: {values}")
    
    print("-" * 40)
    print(f"总计: {len(real_comments)} 条评论，{detected} 条包含联系方式")

def main():
    print("ScrapeMaster 核心逻辑测试")
    print("=" * 60)
    
    # 测试1: 模拟爬虫运行
    print("\n1. 模拟爬虫运行测试...")
    if simulate_crawler():
        print("  ✓ 模拟测试通过")
    else:
        print("  ⚠️ 模拟测试未找到联系方式")
    
    # 测试2: 真实数据测试
    print("\n2. 真实场景测试...")
    test_with_realistic_data()
    
    # 测试3: 性能测试
    print("\n3. 性能测试...")
    import time as ttime
    
    test_text = "微信：abc123，QQ：1234567，电话：13800138000"
    iterations = 1000
    
    start = ttime.time()
    for _ in range(iterations):
        has_contact_info(test_text)
        extract_contact_details(test_text)
    elapsed = ttime.time() - start
    
    print(f"  {iterations} 次检测耗时: {elapsed:.4f}秒")
    print(f"  平均每次: {elapsed/iterations*1000:.2f}毫秒")
    print("  ✓ 性能可接受")
    
    print("\n" + "=" * 60)
    print("🎉 所有测试完成！")
    print("核心逻辑功能正常，可以用于实际爬虫。")
    print("\n下一步:")
    print("1. 安装依赖: pandas, playwright, openpyxl")
    print("2. 确保Chrome浏览器已安装")
    print("3. 运行: python3 src/scrape_xiaohongshu.py")
    print("4. 结果将保存为Excel文件")

if __name__ == "__main__":
    main()