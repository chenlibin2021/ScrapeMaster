#!/usr/bin/env python3
"""
ScrapeMaster 代码验证测试
在不安装依赖的情况下验证核心逻辑
"""

import re
import json
import sys

# 从原文件复制联系方式检测逻辑
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
    """从文本中提取具体的联系方式"""
    if not text:
        return {}
    
    details = {}
    for contact_type, patterns in CONTACT_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                details[contact_type] = matches
                break
    
    return details

def test_contact_detection():
    """测试联系方式检测功能"""
    print("=== 联系方式检测测试 ===")
    
    test_cases = [
        ("加我微信：abc123", True, ["wechat"]),
        ("我的QQ是1234567", True, ["qq"]),
        ("电话：13800138000", True, ["phone"]),
        ("email: test@example.com", True, ["email"]),
        ("whatsapp: +1234567890", True, ["whatsapp"]),
        ("这是一条普通评论", False, []),
        ("wx: mywechat123", True, ["wechat"]),
        ("扫码加微", True, ["wechat"]),
    ]
    
    all_passed = True
    for text, expected_result, expected_types in test_cases:
        has_contact, found_types = has_contact_info(text)
        details = extract_contact_details(text)
        
        passed = (has_contact == expected_result) and (set(found_types) == set(expected_types))
        status = "✓" if passed else "✗"
        
        print(f"{status} 文本: '{text[:20]}...'")
        print(f"   预期: {expected_result} {expected_types}")
        print(f"   实际: {has_contact} {found_types}")
        print(f"   详情: {details}")
        
        if not passed:
            all_passed = False
    
    return all_passed

def test_proxy_file():
    """测试代理文件"""
    print("\n=== 代理文件测试 ===")
    
    try:
        with open("data/working_proxies.json", "r", encoding="utf-8") as f:
            proxies = json.load(f)
        
        print(f"✓ 代理文件读取成功，共 {len(proxies)} 个代理")
        
        # 检查代理格式
        valid_count = 0
        for proxy in proxies[:3]:  # 只检查前3个
            if "proxy" in proxy and "working" in proxy:
                valid_count += 1
        
        if valid_count == min(3, len(proxies)):
            print("✓ 代理格式正确")
            return True
        else:
            print("✗ 代理格式有问题")
            return False
            
    except Exception as e:
        print(f"✗ 代理文件读取失败: {e}")
        return False

def test_code_structure():
    """测试代码文件结构"""
    print("\n=== 代码结构测试 ===")
    
    files_to_check = [
        "src/scrape_xiaohongshu.py",
        "src/extract_comments.py", 
        "src/get_proxies.py",
        "src/scrape_xiaohongshu.js",
        "src/scrape_browser.js",
    ]
    
    all_exist = True
    for file_path in files_to_check:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            print(f"✓ {file_path}: {len(lines)} 行")
        except Exception as e:
            print(f"✗ {file_path}: 无法读取 - {e}")
            all_exist = False
    
    return all_exist

def main():
    """主测试函数"""
    print("ScrapeMaster 代码验证测试")
    print("=" * 50)
    
    tests = [
        ("联系方式检测", test_contact_detection),
        ("代理文件", test_proxy_file),
        ("代码结构", test_code_structure),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n执行测试: {test_name}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"测试失败: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有基础验证测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
        return 1

if __name__ == "__main__":
    sys.exit(main())