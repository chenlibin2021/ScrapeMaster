# ScrapeMaster 🕷️

通用爬虫应用，专注于小红书数据抓取和联系方式提取。

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Chrome浏览器（推荐）
- Git（版本管理）

### 安装依赖
```bash
# 安装Python依赖
pip install pandas playwright openpyxl beautifulsoup4 lxml

# 安装Playwright浏览器（可选）
python -m playwright install chromium
```

### 运行爬虫
```bash
# 1. 系统Chrome版本（推荐）
python src/scrape_xiaohongshu_chrome.py

# 2. 隐身模式版本
python src/scrape_xiaohongshu_incognito.py

# 3. 模拟测试（不依赖浏览器）
python test_with_mock_data.py
```

## 📁 项目结构

```
ScrapeMaster/
├── src/                    # 源代码
│   ├── scrape_xiaohongshu.py          # 主爬虫文件
│   ├── scrape_xiaohongshu_chrome.py   # Chrome连接版本（推荐）
│   ├── scrape_xiaohongshu_incognito.py # 隐身模式版本
│   ├── extract_comments.py            # 评论提取工具
│   ├── get_proxies.py                 # 代理管理
│   ├── scrape_xiaohongshu.js          # JavaScript版本
│   └── scrape_browser.js              # 浏览器自动化
├── docs/                   # 项目文档
├── data/                   # 数据文件
├── config/                 # 配置文件
├── scripts/                # 工具脚本
└── tests/                  # 测试文件
```

## 🎯 核心功能

### 联系方式检测
- **微信**：支持中文ID和多种格式
- **电话**：中国手机号和加拿大本地格式
- **WhatsApp**：国际号码格式
- **邮箱**：标准邮箱格式
- **Instagram**：社交媒体账号

### 数据导出
- Excel格式（.xlsx）
- 自动时间戳命名
- 完整元数据保存

### 浏览器支持
- 系统Chrome连接（Browser Relay）
- 隐身模式浏览
- 无头模式运行

## 🔧 技术栈

### 后端
- **Python 3.12**
- **Playwright**：浏览器自动化
- **Pandas**：数据处理
- **OpenPyXL**：Excel导出

### 前端
- **JavaScript**：浏览器脚本
- **Playwright**：跨浏览器支持

## 📊 使用示例

### 基本使用
```python
# 导入核心功能
from src.scrape_xiaohongshu_chrome import scrape_sharon_comments_chrome

# 运行爬虫
results = scrape_sharon_comments_chrome(max_notes=5)

# 保存结果
import pandas as pd
df = pd.DataFrame(results)
df.to_excel('results.xlsx', index=False)
```

### 自定义配置
```python
# 使用代理
proxies = [
    'http://proxy1:port',
    'http://proxy2:port'
]

# 自定义设置
results = scrape_sharon_comments_chrome(
    proxies=proxies,
    max_notes=10,
    headless=True  # 无头模式
)
```

## 🧪 测试

### 单元测试
```bash
# 运行所有测试
python test_final_verification.py
python test_with_mock_data.py
python test_modern_contacts.py
```

### 模拟测试
```bash
# 不依赖浏览器的完整测试
python test_with_mock_data.py
```

## 🔒 隐私与安全

### 隐身模式
- 使用独立浏览器实例
- 不保存cookies和历史记录
- 关闭后自动清理

### 反检测措施
- 修改User-Agent
- 随机延迟请求
- 绕过自动化检测

## 📈 性能优化

### 检测性能
- 平均检测时间：0.01毫秒/次
- 支持批量处理
- 内存效率优化

### 浏览器优化
- 智能滚动加载
- 连接复用
- 错误重试机制

## 🤝 贡献指南

### 开发流程
1. Fork仓库
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

### 代码规范
- 遵循PEP 8
- 添加类型提示
- 编写文档字符串
- 包含单元测试

## 📚 文档

### 项目文档
- `docs/`：详细技术文档
- `PROJECT_STATUS_SUMMARY.md`：项目状态
- `GITHUB_PUSH_SOLUTION.md`：GitHub配置指南

### 对话记录
- `conversation_summary_20260216.md`：完整开发记录
- `conversation_mobile_summary.md`：移动端摘要

## 🐛 故障排除

### 常见问题

#### 1. Chrome连接失败
```bash
# 确保：
# 1. Chrome浏览器已打开
# 2. 安装OpenClaw Browser Relay扩展
# 3. 点击工具栏图标连接标签页
```

#### 2. Playwright依赖缺失
```bash
# 安装系统依赖
sudo apt-get install libnspr4 libnss3 libasound2
```

#### 3. GitHub推送失败
```bash
# 查看解决方案
cat GITHUB_PUSH_SOLUTION.md
```

### 调试模式
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 支持与联系

### 问题反馈
- GitHub Issues：报告bug和功能请求
- 文档更新：直接提交PR

### 项目维护
- **GitHub**：https://github.com/chenlibin2021/ScrapeMaster
- **开发者**：Daniel Chen

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🚀 开发路线图

### 短期目标
- [ ] 集成Scrapy框架
- [ ] 可视化配置界面
- [ ] 多平台支持扩展

### 长期目标
- [ ] Docker容器化
- [ ] RESTful API
- [ ] 分布式爬取

---

*最后更新：2026-02-16*
*版本：1.0.0*