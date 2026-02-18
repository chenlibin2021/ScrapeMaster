# Chrome Browser Relay 运行指南

## 📋 前提条件

### 已完成的：
- ✅ GitHub认证配置（SSH密钥）
- ✅ 代码推送完成
- ✅ 核心功能测试通过
- ✅ Python依赖安装完成

### 需要准备的：
1. **Chrome浏览器** - 已安装
2. **OpenClaw Browser Relay扩展** - 需要安装
3. **小红书账户** - 可能需要登录

## 🚀 运行步骤

### 步骤1：安装Browser Relay扩展

**方法A：从Chrome网上应用店安装（推荐）**
1. 打开Chrome浏览器
2. 访问：https://chrome.google.com/webstore/detail/openclaw-browser-relay
3. 点击"添加到Chrome"
4. 确认安装

**方法B：手动安装**
1. 下载扩展文件（如果需要，我可以提供）
2. 打开Chrome → 更多工具 → 扩展程序
3. 开启"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择扩展文件夹

### 步骤2：启动Chrome用于爬虫

**选项A：使用启动脚本（推荐）**
```bash
cd ScrapeMaster
./start_chrome_for_scraping.sh
```

**选项B：手动启动**
```bash
# 启动Chrome并启用远程调试
google-chrome \
    --remote-debugging-port=18792 \
    --user-data-dir="$HOME/.chrome-scrapemaster-profile" \
    --no-first-run \
    --no-default-browser-check \
    "https://www.xiaohongshu.com" &
```

### 步骤3：配置浏览器

1. **登录小红书**（如果需要查看完整内容）
2. **导航到目标用户**：Sharon多伦多地产
3. **连接Browser Relay**：
   - 点击Chrome工具栏的OpenClaw图标
   - 确保扩展已连接（图标显示为活动状态）

### 步骤4：运行爬虫

```bash
cd ScrapeMaster
python3 src/scrape_xiaohongshu_chrome.py
```

## 🔧 故障排除

### 常见问题1：无法连接到Chrome
```
❌ 无法连接到Chrome: BrowserType.connect_over_cdp: Unexpected status 401
```

**解决方案：**
1. 确保Chrome已启动并启用远程调试
2. 检查端口18792是否被占用
3. 确认Browser Relay扩展已连接

### 常见问题2：扩展未连接
**症状**：OpenClaw图标显示为灰色或未激活

**解决方案：**
1. 刷新目标页面
2. 点击扩展图标重新连接
3. 检查扩展是否已启用

### 常见问题3：小红书需要登录
**症状**：无法查看完整评论内容

**解决方案：**
1. 在Chrome中登录小红书账户
2. 确保登录状态持久
3. 使用隐身模式避免登录冲突

## 📊 预期输出

成功运行后，你应该看到：
```
============================================================
小红书评论爬虫 - Sharon多伦多地产
目标：抓取包含联系方式的评论
============================================================
✅ 代理配置加载成功: 0个可用代理
🚀 开始抓取（测试模式：前10条笔记）...
🔗 连接到Chrome浏览器...
✅ 连接成功
📄 打开小红书页面...
🔍 分析页面内容...
📊 找到 15 条笔记
🔍 分析评论...
💾 导出结果到Excel...
✅ 抓取完成！结果已保存到: xiaohongshu_results_20260216_xxxxxx.xlsx
```

## 🎯 高级配置

### 自定义目标用户
编辑 `src/scrape_xiaohongshu_chrome.py` 中的：
```python
TARGET_USER = "Sharon多伦多地产"  # 修改为目标用户名
```

### 调整抓取数量
```python
MAX_NOTES = 10  # 修改为想要抓取的笔记数量
```

### 使用代理
创建 `data/working_proxies.json` 文件包含代理列表

## ⚠️ 注意事项

1. **遵守网站规则**：不要过于频繁请求
2. **尊重隐私**：仅收集公开信息
3. **数据用途**：仅用于合法目的
4. **性能考虑**：大量抓取可能需要代理

## 📞 技术支持

遇到问题请检查：
1. `check_environment.py` - 环境检查
2. `test_with_mock_data.py` - 功能测试
3. 查看错误日志

或联系开发者获取帮助。

---

*文档版本：1.0*
*更新日期：2026-02-16*