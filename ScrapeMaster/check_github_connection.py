#!/usr/bin/env python3
"""
检查GitHub连接状态和Git配置
"""

import subprocess
import os
import sys

def run_command(cmd):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def check_git_config():
    """检查Git配置"""
    print("🔍 检查Git配置")
    print("=" * 50)
    
    checks = [
        ("用户信息", "git config --get user.name"),
        ("邮箱", "git config --get user.email"),
        ("远程仓库", "git remote -v"),
        ("当前分支", "git branch --show-current"),
        ("提交状态", "git status --short"),
    ]
    
    for name, cmd in checks:
        code, out, err = run_command(cmd)
        status = "✅" if code == 0 and out.strip() else "⚠️"
        print(f"{status} {name}:")
        if out.strip():
            print(f"  {out.strip()}")
        if err.strip():
            print(f"  错误: {err.strip()}")
        print()

def check_github_connection():
    """检查GitHub连接"""
    print("🌐 检查GitHub连接")
    print("=" * 50)
    
    # 检查HTTPS连接
    print("测试HTTPS连接到GitHub...")
    code, out, err = run_command("curl -s -I https://github.com")
    if code == 0 and "200 OK" in out:
        print("✅ HTTPS连接正常")
    else:
        print("❌ HTTPS连接失败")
        if err:
            print(f"  错误: {err}")
    
    print()
    
    # 检查SSH连接
    print("测试SSH连接到GitHub...")
    code, out, err = run_command("ssh -T git@github.com 2>&1")
    if "successfully authenticated" in out:
        print("✅ SSH连接正常")
        print(f"  消息: {out.strip()}")
    elif "Permission denied" in out:
        print("⚠️ SSH连接需要配置密钥")
    else:
        print("❌ SSH连接失败")
        if out:
            print(f"  输出: {out.strip()}")
        if err:
            print(f"  错误: {err.strip()}")

def check_local_commits():
    """检查本地提交状态"""
    print("📝 检查本地提交")
    print("=" * 50)
    
    # 检查未推送的提交
    code, out, err = run_command("git log --oneline origin/main..HEAD 2>/dev/null || git log --oneline -10")
    
    if code == 0 and out:
        lines = out.strip().split('\n')
        print(f"📊 有 {len(lines)} 个本地提交等待推送:")
        for line in lines[:10]:  # 显示前10个
            print(f"  {line}")
        
        if len(lines) > 10:
            print(f"  ... 还有 {len(lines)-10} 个提交")
    else:
        print("✅ 没有未推送的提交")
    
    print()
    
    # 检查未跟踪的文件
    code, out, err = run_command("git status --porcelain")
    if code == 0 and out:
        files = [line for line in out.strip().split('\n') if line]
        untracked = [f for f in files if f.startswith('??')]
        modified = [f for f in files if not f.startswith('??')]
        
        if modified:
            print(f"📋 有 {len(modified)} 个已跟踪文件的修改:")
            for f in modified[:5]:
                print(f"  {f}")
            if len(modified) > 5:
                print(f"  ... 还有 {len(modified)-5} 个文件")
        
        if untracked:
            print(f"📋 有 {len(untracked)} 个未跟踪的文件:")
            for f in untracked[:5]:
                print(f"  {f[3:]}")
            if len(untracked) > 5:
                print(f"  ... 还有 {len(untracked)-5} 个文件")
    else:
        print("✅ 工作区干净")

def suggest_solutions():
    """提供解决方案建议"""
    print("💡 解决方案建议")
    print("=" * 50)
    
    print("基于当前状态，推荐以下方案:")
    print()
    
    print("1. 🎯 快速解决方案（GitHub令牌）")
    print("   a. 访问: https://github.com/settings/tokens")
    print("   b. 生成新的个人访问令牌（选择 repo 权限）")
    print("   c. 运行:")
    print("      git remote set-url origin https://chenlibin2021:TOKEN@github.com/chenlibin2021/ScrapeMaster.git")
    print("      git push origin main")
    print()
    
    print("2. 🔐 长期解决方案（SSH密钥）")
    print("   a. 生成SSH密钥: ssh-keygen -t ed25519 -C \"your-email\"")
    print("   b. 添加公钥到GitHub设置")
    print("   c. 运行:")
    print("      git remote set-url origin git@github.com:chenlibin2021/ScrapeMaster.git")
    print("      git push origin main")
    print()
    
    print("3. 📄 查看详细指南")
    print("   查看文件: GITHUB_PUSH_SOLUTION.md")
    print()

def main():
    print("GitHub连接诊断工具")
    print("=" * 60)
    
    # 检查是否在Git仓库中
    if not os.path.exists(".git"):
        print("❌ 当前目录不是Git仓库")
        print("请切换到ScrapeMaster目录运行")
        return 1
    
    check_git_config()
    check_github_connection()
    check_local_commits()
    suggest_solutions()
    
    print("=" * 60)
    print("🎯 下一步:")
    print("1. 按照建议配置GitHub认证")
    print("2. 运行: git push origin main")
    print("3. 验证代码已同步到GitHub")
    print()
    print("📁 相关文件:")
    print("  - GITHUB_PUSH_SOLUTION.md: 详细解决方案")
    print("  - PROJECT_STATUS_SUMMARY.md: 项目状态")
    print("  - conversation_summary_20260216.md: 对话记录")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())