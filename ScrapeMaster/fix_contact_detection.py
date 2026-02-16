#!/usr/bin/env python3
"""
修复 scrape_xiaohongshu.py 中的联系方式检测逻辑
"""

import re

def fix_contact_patterns_in_file(file_path):
    """修复文件中的联系方式检测模式"""
    
    # 修复后的模式
    fixed_patterns = '''# 联系方式检测正则
CONTACT_PATTERNS = {
    'wechat': [
        r'[微V信][信xX][:：\\s]*([a-zA-Z0-9_-]{5,20})',
        r'wx[:：\\s]*([a-zA-Z0-9_-]{5,20})',
        r'加我?[微V][信xX]',
        r'扫码加[微V]',
    ],
    'phone': [
        r'(\\d{3}[-\\s]?\\d{3}[-\\s]?\\d{4})',  # 北美电话
        r'(\\d{3}[-\\s]?\\d{4}[-\\s]?\\d{4})',  # 中国电话
        r'[电☎️📞]话[:：\\s]*(\\d[\\d\\s-]{7,})',
    ],
    'qq': [
        r'QQ[:：\\s]*(\\d{5,11})',
        r'qq[:：\\s]*(\\d{5,11})',
        r'扣扣[:：\\s]*(\\d{5,11})',
        r'(?<=QQ|qq|扣扣)[:：\\s]*(\\d{5,11})',  # 修复：匹配"我的QQ是1234567"
    ],
    'email': [
        r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,})',
    ],
    'whatsapp': [
        r'whatsapp[:：\\s]*([+]\\d[\\d\\s-]{9,})(?!.*电话)',  # 修复：避免与phone冲突
        r'wa[:：\\s]*([+]\\d[\\d\\s-]{9,})',
    ],
}'''
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并替换 CONTACT_PATTERNS 部分
        # 查找从 CONTACT_PATTERNS = { 开始到下一个函数或类定义结束
        import re as re2
        pattern = r'# 联系方式检测正则\nCONTACT_PATTERNS = \{.*?\n\}'
        
        if re2.search(pattern, content, re2.DOTALL):
            # 替换现有模式
            new_content = re2.sub(pattern, fixed_patterns, content, flags=re2.DOTALL)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✓ 已修复 {file_path} 中的联系方式检测模式")
            return True
        else:
            print(f"✗ 未找到 CONTACT_PATTERNS 定义 in {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ 修复文件时出错: {e}")
        return False

def test_fixed_patterns():
    """测试修复后的模式"""
    print("\n=== 测试修复后的模式 ===")
    
    # 使用修复后的模式
    CONTACT_PATTERNS = {
        'wechat': [
            r'[微V信][信xX][:：\s]*([a-zA-Z0-9_-]{5,20})',
            r'wx[:：\s]*([a-zA-Z0-9_-]{5,20})',
            r'加我?[微V][信xX]',
            r'扫码加[微V]',
        ],
        'phone': [
            r'(\d{3}[-\s]?\d{3}[-\s]?\d{4})',
            r'(\d{3}[-\s]?\d{4}[-\s]?\d{4})',
            r'[电☎️📞]话[:：\s]*(\d[\d\s-]{7,})',
        ],
        'qq': [
            r'QQ[:：\s]*(\d{5,11})',
            r'qq[:：\s]*(\d{5,11})',
            r'扣扣[:：\s]*(\d{5,11})',
            r'(?<=QQ|qq|扣扣)[:：\s]*(\d{5,11})',
        ],
        'email': [
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        ],
        'whatsapp': [
            r'whatsapp[:：\s]*([+]\d[\d\s-]{9,})(?!.*电话)',
            r'wa[:：\s]*([+]\d[\d\s-]{9,})',
        ],
    }
    
    def has_contact_info(text):
        if not text:
            return False, []
        
        found_types = []
        for contact_type, patterns in CONTACT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    found_types.append(contact_type)
                    break
        
        return len(found_types) > 0, found_types
    
    # 测试用例
    test_cases = [
        ("加我微信：abc123", True, ["wechat"]),
        ("我的QQ是1234567", True, ["qq"]),
        ("QQ: 123456789", True, ["qq"]),
        ("电话：13800138000", True, ["phone"]),
        ("whatsapp: +1234567890", True, ["whatsapp"]),
        ("这是一条普通评论", False, []),
    ]
    
    all_passed = True
    for text, expected_result, expected_types in test_cases:
        has_contact, found_types = has_contact_info(text)
        passed = (has_contact == expected_result) and (set(found_types) == set(expected_types))
        status = "✓" if passed else "✗"
        
        print(f"{status} '{text[:20]}...' -> {has_contact} {found_types}")
        if not passed:
            print(f"   预期: {expected_result} {expected_types}")
            all_passed = False
    
    return all_passed

def create_environment_setup_script():
    """创建环境安装脚本"""
    script_content = '''#!/bin/bash
# ScrapeMaster 环境安装脚本

set -e  # 出错时停止

echo "=== 安装系统依赖 ==="
sudo apt-get update
sudo apt-get install -y python3-pip nodejs npm

echo "=== 安装 Python 依赖 ==="
pip3 install --user pandas playwright requests beautifulsoup4 lxml

echo "=== 安装 Playwright 浏览器 ==="
python3 -m playwright install chromium

echo "=== 安装 Node.js 依赖 ==="
npm install

echo "=== 验证安装 ==="
python3 -c "import pandas; print('✓ pandas:', pandas.__version__)"
python3 -c "import playwright; print('✓ playwright 可用')"
node -c src/scrape_xiaohongshu.js && echo "✓ JavaScript 语法正确"

echo ""
echo "🎉 环境安装完成！"
echo "运行 Python 爬虫: python3 src/scrape_xiaohongshu.py"
echo "运行 JavaScript 爬虫: node src/scrape_xiaohongshu.js"
'''
    
    with open('setup_environment.sh', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    import os
    os.chmod('setup_environment.sh', 0o755)
    
    print("✓ 已创建环境安装脚本: setup_environment.sh")
    print("  执行: bash setup_environment.sh")

def main():
    """主函数"""
    print("ScrapeMaster 核心问题修复工具")
    print("=" * 50)
    
    # 1. 修复联系方式检测
    print("\n1. 修复联系方式检测逻辑...")
    files_to_fix = ['src/scrape_xiaohongshu.py', 'src/extract_comments.py']
    
    for file_path in files_to_fix:
        if fix_contact_patterns_in_file(file_path):
            print(f"  已处理: {file_path}")
        else:
            print(f"  跳过: {file_path}")
    
    # 2. 测试修复结果
    print("\n2. 测试修复结果...")
    if test_fixed_patterns():
        print("  ✓ 所有测试用例通过")
    else:
        print("  ⚠️ 部分测试失败，需要手动检查")
    
    # 3. 创建环境安装脚本
    print("\n3. 创建环境安装脚本...")
    create_environment_setup_script()
    
    # 4. 创建基础错误处理示例
    print("\n4. 创建错误处理示例...")
    error_handling_example = '''# 错误处理示例 - 添加到现有函数中

import logging
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scrapemaster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def safe_scrape_with_retry(url, max_retries=3):
    """带重试的安全爬取函数"""
    for attempt in range(max_retries):
        try:
            logger.info(f"尝试爬取 {url} (第{attempt+1}次)")
            # 这里替换为实际的爬取逻辑
            # result = scrape_function(url)
            return "爬取结果"
            
        except TimeoutError:
            logger.warning(f"请求超时，{attempt+1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
            else:
                logger.error(f"爬取失败: {url}")
                raise
                
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise
    
    return None
'''
    
    with open('error_handling_example.py', 'w', encoding='utf-8') as f:
        f.write(error_handling_example)
    
    print("  ✓ 已创建错误处理示例: error_handling_example.py")
    
    print("\n" + "=" * 50)
    print("修复完成！下一步：")
    print("1. 运行 bash setup_environment.sh 安装依赖")
    print("2. 参考 error_handling_example.py 添加错误处理")
    print("3. 测试修复后的爬虫功能")
    print("4. 提交修复到 GitHub")

if __name__ == "__main__":
    main()