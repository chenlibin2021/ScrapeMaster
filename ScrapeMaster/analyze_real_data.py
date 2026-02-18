#!/usr/bin/env python3
"""
分析真实的小红书页面数据
过滤测试数据，专注真实结果
"""

import re
import pandas as pd
from datetime import datetime
from contact_filter import extract_real_contacts, EXCLUDED_CONTACTS

def analyze_real_page_data(page_text):
    """分析真实页面数据"""
    print("🔍 分析真实小红书页面数据")
    print("=" * 60)
    
    # 分割文本行
    lines = page_text.split('\n')
    
    results = {
        "user_info": {},
        "notes": [],
        "real_contacts": []
    }
    
    # 1. 提取用户信息
    print("1. 📊 提取用户信息...")
    user_keywords = ['小红书号', '关注', '粉丝', '获赞', '笔记']
    user_data = {}
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # 查找用户名
        if 'Sharon多伦多地产' in line and len(line) < 50:
            user_data['username'] = line
        
        # 查找其他用户信息
        for keyword in user_keywords:
            if keyword in line:
                # 提取数字
                numbers = re.findall(r'[\d\.万]+', line)
                if numbers:
                    user_data[keyword] = numbers[0]
    
    results["user_info"] = user_data
    
    # 2. 提取笔记信息
    print("2. 📝 提取笔记信息...")
    note_patterns = [
        r'(.+?)\nSharon多伦多地产\n\d+',  # 笔记标题模式
    ]
    
    notes_found = []
    for i in range(len(lines) - 3):
        # 查找笔记标题模式
        if 'Sharon多伦多地产' in lines[i+1] and lines[i+2].isdigit():
            title = lines[i].strip()
            if title and len(title) > 5 and title not in notes_found:
                notes_found.append(title)
    
    results["notes"] = notes_found[:20]  # 取前20条
    
    # 3. 查找真实联系方式
    print("3. 📞 查找真实联系方式...")
    
    # 排除公司联系信息（小红书官方）
    company_keywords = ['9501-3888', '4006676810', '沪ICP备', '营业执照']
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or len(line) < 10:
            continue
        
        # 跳过公司信息
        if any(keyword in line for keyword in company_keywords):
            continue
        
        # 提取联系方式
        contacts = extract_real_contacts(line)
        
        if contacts:
            # 添加上下文
            context_start = max(0, i-1)
            context_end = min(len(lines), i+2)
            context = '\n'.join(lines[context_start:context_end])
            
            results["real_contacts"].append({
                "text": line,
                "context": context,
                "contacts": contacts
            })
    
    return results

def create_clean_report(results):
    """创建干净的报表"""
    print("\n4. 📋 生成干净的报告...")
    
    records = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 用户信息
    if results["user_info"]:
        user_record = {
            "数据类型": "用户信息",
            "用户名": results["user_info"].get("username", "未知"),
            "小红书号": results["user_info"].get("小红书号", ""),
            "粉丝数": results["user_info"].get("粉丝", "0"),
            "笔记数": results["user_info"].get("笔记", "0"),
            "关注数": results["user_info"].get("关注", "0"),
            "获赞数": results["user_info"].get("获赞", "0"),
            "抓取时间": timestamp,
            "数据来源": "真实页面",
            "备注": "已过滤测试数据"
        }
        records.append(user_record)
    
    # 笔记信息
    for i, note in enumerate(results["notes"], 1):
        note_record = {
            "数据类型": "笔记标题",
            "序号": i,
            "标题": note,
            "抓取时间": timestamp,
            "数据来源": "真实页面",
            "备注": "真实笔记标题"
        }
        records.append(note_record)
    
    # 联系方式
    for i, contact_info in enumerate(results["real_contacts"], 1):
        contacts = contact_info["contacts"]
        
        contact_record = {
            "数据类型": "联系方式",
            "序号": i,
            "来源文本": contact_info["text"][:100],
            "微信": ", ".join(contacts.get('wechat', [])),
            "电话": ", ".join(contacts.get('phone', [])),
            "WhatsApp": ", ".join(contacts.get('whatsapp', [])),
            "邮箱": ", ".join(contacts.get('email', [])),
            "Instagram": ", ".join(contacts.get('instagram', [])),
            "抓取时间": timestamp,
            "数据来源": "真实页面",
            "备注": "已过滤测试数据",
            "验证状态": "待验证"
        }
        records.append(contact_record)
    
    return records

def main():
    """主函数"""
    print("🚀 真实数据收集与分析")
    print("=" * 60)
    print("目标：从真实页面提取数据，过滤测试信息")
    print("排除的测试数据:")
    for contact_type, values in EXCLUDED_CONTACTS.items():
        print(f"  {contact_type}: {', '.join(values[:3])}...")
    print("=" * 60)
    
    # 这里应该从browser工具获取真实数据
    # 为了演示，使用之前获取的页面文本
    
    page_text = """Sharon多伦多地产
小红书号：950717389
🏆多伦多TOP0.5%地产人Remax💎
💼前世界500强高级经理人 谈判专家
🏠 楼花VIP| 豪宅｜装修 2022全公司业绩第一名
📮@Sharon多伦多好房推荐@多村Sharon咨询
加拿大
279
关注
4144
粉丝
1.1万
获赞与收藏
已关注
笔记
收藏
Newmarket轻奢独立屋4⃣️4⃣️2⃣️近高速学校🏠
Sharon多伦多地产
10
安省涨租赶租 N1 N2 N4 N12 N11 N9一网打尽
Sharon多伦多地产
228
Newmarket 四年新4⃣️4⃣️2⃣️独立屋 实用方正
Sharon多伦多地产
28
拍卖房🏠法拍房 一分钟避雷视频 捡漏不踩坑
Sharon多伦多地产
42
Oakville 核心区🈚️管理费独立镇屋105万 ❗️
Sharon多伦多地产
11
Centricity 🏠楼花测评 3⃣️个卖点一网打尽
Sharon多伦多地产
9
Newmarket 最新成交30年房龄大家觉得怎么样
Sharon多伦多地产
8
🇨🇦买房 物业类型全介绍 ➕优缺点对比🏠
Sharon多伦多地产
11
独家代理🏠Newmarket 豪宅三车库5400尺
Sharon多伦多地产
8
🇨🇦Open House 看房清单 N个不可忽略细节
Sharon多伦多地产
86
🇨🇦买房不求人 👉3⃣️个一定要保存的网站
Sharon多伦多地产
275
独家代理 渔人村豪华联排 面对公园好房🏠
Sharon多伦多地产
15
北约克中心 豪华全翻建🏠 超美设计师独立屋
Sharon多伦多地产
15
地产经纪自己都买了啥❓🤔楼花PDI交付全攻略
Sharon多伦多地产
71
万锦附近笋盘 137W 买442 独立屋不抢Offer
Sharon多伦多地产
25
99%的买家都不知道的土地价值大公开㊙️🏠
Sharon多伦多地产
91
万锦欧式豪华庄园 9亩占地 万尺豪宅
Sharon多伦多地产
12
实地考察North Core 楼花投资详解 👍超详细
Sharon多伦多地产
25
多伦多公寓卖房 高价卖房公式四部曲💰💰💰
Sharon多伦多地产
19
渔人村 绝版好宅🏠朝南➕Ravine➕走出地下室
Sharon多伦多地产
21
海外买家税📈涨到25% 真的要醉了😵‍💫😵‍💫
Sharon多伦多地产
15
旺市绝美TH 大量升级4⃣️个卧室 近高速商圈
Sharon多伦多地产
21
东贵林豪宅天花板🏠 泳池Party 绝美厨房
Sharon多伦多地产
29
疫情以来 加息之后 📈多伦多社区涨跌排行榜
Sharon多伦多地产
157
🇨🇦大多伦多八月市场 别看感觉—看数据
Sharon多伦多地产
15
🏠建商升级- 如何花小钱办大事 避坑骗 1⃣️
Sharon多伦多地产
34
实力帮客人省了💰15W➕🏠 做得到从不是运气
Sharon多伦多地产
70"""
    
    # 分析数据
    results = analyze_real_page_data(page_text)
    
    # 显示结果摘要
    print(f"\n📊 分析结果摘要:")
    print(f"   用户信息: {len(results['user_info'])} 项")
    print(f"   笔记标题: {len(results['notes'])} 条")
    print(f"   真实联系方式: {len(results['real_contacts'])} 处")
    
    if results["real_contacts"]:
        print("\n🔍 发现的联系方式:")
        for i, contact in enumerate(results["real_contacts"], 1):
            print(f"   {i}. 文本: {contact['text'][:50]}...")
            print(f"      类型: {list(contact['contacts'].keys())}")
    
    # 创建干净的报告
    records = create_clean_report(results)
    
    if records:
        # 保存到Excel
        df = pd.DataFrame(records)
        filename = f"real_xiaohongshu_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        
        print(f"\n💾 干净数据已保存到: {filename}")
        print(f"📊 总计 {len(records)} 条记录")
        
        # 显示数据预览
        print("\n📋 数据预览:")
        print(df[['数据类型', '序号'] + [col for col in df.columns if col not in ['数据类型', '序号']]].head(10).to_string())
    
    print("\n" + "=" * 60)
    print("✅ 分析完成！数据已过滤测试信息")
    print("=" * 60)

if __name__ == "__main__":
    main()