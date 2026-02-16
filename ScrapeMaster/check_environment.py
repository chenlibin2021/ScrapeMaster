#!/usr/bin/env python3
"""
环境检查脚本
验证运行ScrapeMaster所需的所有条件
"""

import sys
import subprocess
import os
from pathlib import Path

def print_header(text):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"🔍 {text}")
    print(f"{'='*60}")

def run_command(cmd, check_output=False):
    """运行命令并返回结果"""
    try:
        if check_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_python():
    """检查Python环境"""
    print_header("Python环境检查")
    
    checks = [
        ("Python版本", "python3 --version"),
        ("pip版本", "python3 -m pip --version"),
        ("虚拟环境", "python3 -c \"import sys; print('虚拟环境' if hasattr(sys, 'real_prefix') or sys.base_prefix != sys.prefix else '系统环境')\""),
    ]
    
    all_ok = True
    for name, cmd in checks:
        success, out, err = run_command(cmd)
        status = "✅" if success else "❌"
        print(f"{status} {name}: {out if out else '未安装'}")
        if err and not success:
            print(f"   错误: {err}")
        if not success:
            all_ok = False
    
    return all_ok

def check_dependencies():
    """检查Python依赖"""
    print_header("Python依赖检查")
    
    dependencies = [
        ("pandas", "数据处理"),
        ("playwright", "浏览器自动化"),
        ("openpyxl", "Excel导出"),
        ("bs4", "HTML解析 (beautifulsoup4)"),
        ("lxml", "XML处理"),
    ]
    
    missing = []
    for package, description in dependencies:
        success, out, err = run_command(f"python3 -c \"import {package}\"")
        status = "✅" if success else "❌"
        print(f"{status} {package}: {description}")
        if not success:
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  缺失依赖: {', '.join(missing)}")
        print("安装命令: python3 -m pip install " + " ".join(missing))
        return False
    else:
        print("\n✅ 所有依赖已安装")
        return True

def check_browser():
    """检查浏览器环境"""
    print_header("浏览器环境检查")
    
    # 检查Chrome
    chrome_ok, chrome_out, chrome_err = run_command("which google-chrome || which chromium-browser || which chrome")
    
    # 检查Playwright Chromium
    browsers_dir = Path.home() / ".cache" / "ms-playwright"
    playwright_chromium = browsers_dir.exists() and any("chromium" in str(p) for p in browsers_dir.iterdir())
    
    if chrome_ok:
        print(f"✅ Chrome/Chromium: {chrome_out}")
    elif playwright_chromium:
        print("✅ Playwright Chromium: 已安装 (可用于标准版本)")
        chrome_ok = True
    else:
        print("❌ Chrome/Chromium: 未找到")
        print("   请安装Chrome浏览器或运行: python3 -m playwright install chromium")
    
    # 检查Playwright
    playwright_ok, playwright_out, playwright_err = run_command("python3 -m playwright --version")
    
    if playwright_ok:
        print(f"✅ Playwright: {playwright_out}")
        
        # 检查浏览器安装
        browsers_dir = Path.home() / ".cache" / "ms-playwright"
        if browsers_dir.exists():
            print(f"✅ Playwright浏览器: 已安装")
        else:
            print("⚠️  Playwright浏览器: 未安装")
            print("   运行: python3 -m playwright install chromium")
    else:
        print("❌ Playwright: 未正确安装")
    
    return chrome_ok

def check_git():
    """检查Git配置"""
    print_header("Git配置检查")
    
    checks = [
        ("Git版本", "git --version"),
        ("用户配置", "git config --get user.name"),
        ("邮箱配置", "git config --get user.email"),
        ("远程仓库", "git remote -v"),
    ]
    
    all_ok = True
    for name, cmd in checks:
        success, out, err = run_command(cmd)
        status = "✅" if success and out else "⚠️"
        print(f"{status} {name}: {out if out else '未配置'}")
        if not success and name != "远程仓库":  # 远程仓库可能未设置
            all_ok = False
    
    return all_ok

def check_project_files():
    """检查项目文件"""
    print_header("项目文件检查")
    
    required_files = [
        ("src/scrape_xiaohongshu.py", "主爬虫文件"),
        ("src/scrape_xiaohongshu_chrome.py", "Chrome版本"),
        ("README.md", "项目说明"),
        ("requirements.txt", "依赖列表"),
    ]
    
    all_exist = True
    for file_path, description in required_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}: {description}")
        if not exists:
            all_exist = False
    
    return all_exist

def suggest_next_steps(python_ok, deps_ok, browser_ok, git_ok, files_ok):
    """根据检查结果建议下一步"""
    print_header("下一步建议")
    
    issues = []
    
    if not python_ok:
        issues.append("Python环境配置")
    
    if not deps_ok:
        issues.append("安装Python依赖")
    
    if not browser_ok:
        issues.append("安装Chrome浏览器")
    
    if not git_ok:
        issues.append("配置Git")
    
    if not files_ok:
        issues.append("检查项目文件")
    
    if not issues:
        print("🎉 所有检查通过！")
        print("\n🚀 可以运行爬虫:")
        print("1. python3 src/scrape_xiaohongshu_chrome.py")
        print("2. python3 test_with_mock_data.py (模拟测试)")
        return True
    else:
        print(f"⚠️  需要解决的问题: {', '.join(issues)}")
        print("\n🔧 建议操作:")
        
        if "Python环境配置" in issues:
            print("   • 安装Python 3.8+ 和 pip")
        
        if "安装Python依赖" in issues:
            print("   • 运行: python3 -m pip install pandas playwright openpyxl beautifulsoup4 lxml")
        
        if "安装Chrome浏览器" in issues:
            print("   • 安装Chrome浏览器")
            print("   • 或运行: python3 -m playwright install chromium")
        
        if "配置Git" in issues:
            print("   • 运行: git config --global user.name 'Your Name'")
            print("   • 运行: git config --global user.email 'your.email@example.com'")
        
        return False

def main():
    """主函数"""
    print("ScrapeMaster 环境检查工具")
    print("=" * 60)
    print("检查运行爬虫所需的所有条件")
    print("=" * 60)
    
    # 检查当前目录
    if not os.path.exists("src"):
        print("⚠️  请在ScrapeMaster目录中运行此脚本")
        print("当前目录:", os.getcwd())
        return 1
    
    # 执行各项检查
    python_ok = check_python()
    deps_ok = check_dependencies()
    browser_ok = check_browser()
    git_ok = check_git()
    files_ok = check_project_files()
    
    # 总结和建议
    ready = suggest_next_steps(python_ok, deps_ok, browser_ok, git_ok, files_ok)
    
    print("\n" + "=" * 60)
    if ready:
        print("✅ 环境检查完成 - 可以开始使用ScrapeMaster!")
    else:
        print("⚠️  环境检查完成 - 需要先解决上述问题")
    
    print("\n📚 相关文档:")
    print("  • README.md - 项目说明")
    print("  • GITHUB_PUSH_SOLUTION.md - GitHub配置")
    print("  • conversation_mobile_summary.md - 开发记录")
    
    return 0 if ready else 1

if __name__ == "__main__":
    sys.exit(main())