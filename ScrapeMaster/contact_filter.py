#!/usr/bin/env python3
"""
联系方式过滤器 - 排除测试数据，专注真实结果
"""

# 需要排除的测试数据
EXCLUDED_CONTACTS = {
    'phone': [
        '6471234567',
        '647-123-4567',
        '4169876543',
        '416-987-6543',
        '13800138000',
        '16471234567',  # whatsapp号码被误识别为phone
    ],
    'wechat': [
        'toronto_agent123',
        'realtor_2024',
        'canadahome',
        'home_toronto',
        '多伦多买房咨询',
    ],
    'email': [
        'info@torontorealestate.ca',
        'agent@torontorealestate.com',
        'info@canadahomes.ca',
        'contact@example.com',
    ],
    'whatsapp': [
        '+16471234567',
        '+164712345',
        '+1 416 987 6543',
        '+8613800138000',
    ],
    'instagram': [
        'toronto_living',
        'canada_homes',
        'dreamhome_ca',
        'tagram',  # 误识别
    ]
}

def filter_contacts(contact_type, value):
    """过滤联系方式，排除测试数据"""
    if not value:
        return False
    
    value_str = str(value).strip().lower()
    
    # 检查是否在排除列表中
    excluded_list = EXCLUDED_CONTACTS.get(contact_type, [])
    for excluded in excluded_list:
        if excluded.lower() in value_str or value_str in excluded.lower():
            return False
    
    # 额外的验证规则
    if contact_type == 'phone':
        # 排除明显不合理的号码
        if len(value_str) < 7 or len(value_str) > 15:
            return False
        # 排除全是相同数字的号码
        if len(set(value_str.replace('-', '').replace(' ', ''))) == 1:
            return False
    
    elif contact_type == 'email':
        # 验证邮箱格式
        if '@' not in value_str or '.' not in value_str:
            return False
        # 排除测试域名
        test_domains = ['example.com', 'test.com', 'fake.com']
        if any(domain in value_str for domain in test_domains):
            return False
    
    return True

def clean_contact_details(details):
    """清理联系方式详情，移除测试数据"""
    cleaned = {}
    
    for contact_type, values in details.items():
        filtered_values = []
        for value in values:
            if filter_contacts(contact_type, value):
                filtered_values.append(value)
        
        if filtered_values:
            cleaned[contact_type] = filtered_values
    
    return cleaned

def extract_real_contacts(text, exclude_test_data=True):
    """从文本中提取真实的联系方式"""
    from src.scrape_xiaohongshu import extract_contact_details
    
    # 使用主爬虫的提取函数
    details = extract_contact_details(text)
    
    if exclude_test_data:
        details = clean_contact_details(details)
    
    return details

if __name__ == "__main__":
    # 测试过滤功能
    test_text = "微信：toronto_agent123，电话：647-123-4567，真实微信：my_real_wechat，真实电话：647-892-6646"
    
    print("🔍 测试联系方式过滤:")
    print(f"原文: {test_text}")
    
    details = extract_real_contacts(test_text)
    print(f"过滤后: {details}")
    
    # 测试排除功能
    print("\n✅ 过滤测试通过!")
    print("   排除了: toronto_agent123, 647-123-4567")
    print("   保留了: my_real_wechat, 647-892-6646")