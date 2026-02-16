#!/usr/bin/env python3
"""
直接通过CDP提取小红书评论数据
"""
import json
import re
from datetime import datetime

def extract_contacts_from_text(text):
    """从文本中提取联系方式"""
    contacts = []
    
    # 微信
    wechat_matches = re.findall(r'[微V信][信xX][:：\s]*([a-zA-Z0-9_-]{5,20})', text, re.IGNORECASE)
    wechat_matches += re.findall(r'wx[:：\s]*([a-zA-Z0-9_-]{5,20})', text, re.IGNORECASE)
    if wechat_matches:
        contacts.append({'type': 'wechat', 'values': wechat_matches})
    
    # 电话
    phone_matches = re.findall(r'(\d{3}[-\s]?\d{3}[-\s]?\d{4})', text)
    phone_matches += re.findall(r'(\d{3}[-\s]?\d{4}[-\s]?\d{4})', text)
    if phone_matches:
        contacts.append({'type': 'phone', 'values': phone_matches})
    
    # QQ
    qq_matches = re.findall(r'QQ[:：\s]*(\d{5,11})', text, re.IGNORECASE)
    if qq_matches:
        contacts.append({'type': 'qq', 'values': qq_matches})
    
    # 邮箱
    email_matches = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    if email_matches:
        contacts.append({'type': 'email', 'values': email_matches})
    
    return contacts

def main():
    print("📋 小红书评论数据提取")
    print("=" * 50)
    
    # 从之前的快照中提取数据
    try:
        with open('/home/chenlibin/.openclaw/workspace/browser_snapshot.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print("❌ 无法读取浏览器快照")
        print("💡 请确保浏览器页面已打开")
        return
    
    # 简单提取评论相关信息
    print(f"📄 文本长度: {len(content)} 字符")
    
    # 查找可能的评论内容
    lines = content.split('\n')
    comments = []
    
    # 简单关键词匹配
    contact_keywords = ['微信', 'VX', 'wx', '加我', '电话', '手机', 'QQ', '扣扣', '@', 'whatsapp', 'wa', '联系']
    
    for i, line in enumerate(lines):
        line = line.strip()
        if len(line) > 20:  # 假设评论内容较长
            # 检查是否包含联系方式关键词
            has_contact = any(keyword in line.lower() for keyword in [k.lower() for k in contact_keywords])
            has_contact = has_contact or re.search(r'\d{10,}', line)  # 长数字可能是电话
            
            if has_contact:
                contacts = extract_contacts_from_text(line)
                if contacts:
                    comments.append({
                        'content': line[:200] + ('...' if len(line) > 200 else ''),
                        'contacts': contacts,
                        'line_number': i + 1
                    })
    
    print(f"✅ 找到 {len(comments)} 条可能包含联系方式的评论")
    
    if comments:
        # 保存结果
        output_file = f'/home/chenlibin/.openclaw/workspace/xiaohongshu_comments_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        result = {
            'extracted_at': datetime.now().isoformat(),
            'total_comments': len(comments),
            'comments': comments,
            'summary': {
                'wechat_count': sum(1 for c in comments if any(ct['type'] == 'wechat' for ct in c['contacts'])),
                'phone_count': sum(1 for c in comments if any(ct['type'] == 'phone' for ct in c['contacts'])),
                'qq_count': sum(1 for c in comments if any(ct['type'] == 'qq' for ct in c['contacts'])),
                'email_count': sum(1 for c in comments if any(ct['type'] == 'email' for ct in c['contacts']))
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"📁 数据已保存到: {output_file}")
        print(f"📊 统计:")
        print(f"  - 微信: {result['summary']['wechat_count']} 条")
        print(f"  - 电话: {result['summary']['phone_count']} 条")
        print(f"  - QQ: {result['summary']['qq_count']} 条")
        print(f"  - 邮箱: {result['summary']['email_count']} 条")
        
        # 显示前几条
        print("\n📋 前5条评论:")
        for i, comment in enumerate(comments[:5]):
            print(f"{i+1}. {comment['content'][:80]}...")
            for contact in comment['contacts']:
                print(f"   {contact['type']}: {contact['values'][:3]}")
            print()
        
        # 生成CSV格式
        csv_file = output_file.replace('.json', '.csv')
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write('序号,评论内容,联系方式类型,具体联系方式\n')
            for i, comment in enumerate(comments):
                contact_types = []
                contact_values = []
                for ct in comment['contacts']:
                    contact_types.append(ct['type'])
                    contact_values.append(';'.join(ct['values'][:3]))
                
                f.write(f'{i+1},"{comment["content"]}","{",".join(contact_types)}","{";".join(contact_values)}"\n')
        
        print(f"📄 CSV文件: {csv_file}")
        print("💾 你可以复制这个文件到你的文档文件夹")
        
    else:
        print("⚠️  未找到包含联系方式的评论")
        print("💡 可能原因:")
        print("1. 当前页面不是笔记详情页")
        print("2. 评论中没有用户留下联系方式")
        print("3. 需要打开具体的笔记页面")

if __name__ == "__main__":
    main()
