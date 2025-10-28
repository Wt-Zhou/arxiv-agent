# ArXiv Agent

🤖 自动搜索和分析学术论文的智能 Agent，使用 OpenAI GPT 模型帮助筛选与你研究方向相关的最新论文，并自动发送精美的 HTML 邮件报告。

## ✨ 功能特性

### 📚 多数据源支持
- **ArXiv 论文**: 从 ArXiv 获取多个类别的最新论文
- **CNS 期刊**: 支持 Nature、Science、Cell 系列顶级期刊
- **Twitter 学术动态**: 自动爬取 50 个顶级学术账号的最新推文（可选）

### 🧠 智能分析
- **AI 驱动**: 使用 OpenAI GPT 模型分析论文与研究方向的相关性
- **两阶段筛选**: 快速批量筛选 + 详细深度分析
- **相关性评级**: 自动分为高、中、低相关性三个等级
- **并发处理**: 异步并发请求，速度提升 5-10 倍

### 📧 精美报告
- **HTML 邮件**: 自动发送格式精美的 HTML 邮件报告
- **主题总结**: AI 生成研究热点总结
- **CNS 徽章**: 顶级期刊论文特殊标识
- **响应式设计**: 支持桌面和移动端阅读

### ☁️ 云端自动化
- **GitHub Actions**: 每日自动运行，完全免费
- **零维护**: 无需本地服务器，在云端执行
- **灵活配置**: 支持手动触发和参数自定义

## 🚀 快速开始

### 方式一：GitHub Actions（推荐，完全免费）

1. **Fork 本仓库**

2. **配置 Secrets**（Settings > Secrets and variables > Actions）
   - `OPENAI_API_KEY`: OpenAI API 密钥
   - `EMAIL_SENDER`: 发送邮箱
   - `EMAIL_PASSWORD`: 邮箱授权码
   - `EMAIL_RECEIVER`: 接收邮箱

3. **启用 Actions**
   - 进入 Actions 页面
   - 点击 "Run workflow" 测试

完成！每天自动运行并发送邮件报告。📖 [详细指南](GITHUB_ACTIONS_SETUP.md)

---

### 方式二：本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/arxiv-agent.git
cd arxiv-agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置文件
cp config.yaml.example config.yaml
# 编辑 config.yaml，填入你的 API 密钥和邮箱配置

# 4. 运行
python main.py

# 5. 查看报告
# - 邮箱中查看 HTML 格式报告
# - 或查看本地文件: reports/arxiv_papers_YYYY-MM-DD.md
```

---

## ⚙️ 性能优化

本项目采用**两阶段筛选 + 异步并发**架构，大幅提升分析效率：

### 两阶段筛选策略
1. **快速批量筛选**：每批 25 篇论文，快速过滤无关内容
2. **详细深度分析**：每批 5-8 篇论文，生成完整分析报告

### 并发处理优势
- **默认并发数**: 5 个同时请求
- **速度提升**: 相比串行处理快 **5-10 倍**
- **连接复用**: 自动复用 TCP 连接，减少握手开销

**性能对比**:
- 串行处理: 100篇论文 ≈ 200秒
- 并发处理(5): 100篇论文 ≈ 40秒 ⚡
- 并发处理(10): 100篇论文 ≈ 20秒 ⚡⚡

可在 `config.yaml` 中调整 `max_concurrent`、`batch_size`、`detail_batch_size` 参数。

---

## 📝 配置说明

### 常用命令行参数

```bash
python main.py --days 3              # 搜索最近3天的论文
python main.py --min-relevance high  # 只显示高相关性论文
python main.py --no-analysis         # 不使用AI分析（节省API调用）
python main.py --max-concurrent 10   # 设置并发数为10
```

### 配置文件详解

复制 `config.yaml.example` 为 `config.yaml`，然后编辑：

```yaml
# ============================================================
# 1. 研究方向配置
# ============================================================
research_interests:
  - 自动驾驶
  - 具身智能
  - 强化学习
  - VLM (Vision Language Models)

research_prompt: |
  详细描述你的研究兴趣...（可选，用于更精准的相关性分析）

# ============================================================
# 2. 数据源配置
# ============================================================
sources:
  # ArXiv论文源
  arxiv:
    enabled: true
    categories:
      - cs.RO  # Robotics
      - cs.CV  # Computer Vision
      - cs.AI  # Artificial Intelligence
      - cs.LG  # Machine Learning
      - cs.CL  # Computation and Language
    max_results: 50
    days_back: 3

  # 学术期刊源（Nature、Science、Cell系列）
  journals:
    enabled: true
    days_back: 7
    selected_journals:
      - Nature
      - Science
      - Nature Machine Intelligence
      - Science Robotics

  # Twitter推文源（可选，自动爬取学术账号推文）
  twitter:
    enabled: false  # 改为 true 启用
    days_back: 1
    tweets_per_user: 3
    following_usernames:  # 已配置50个顶级学术账号/机构
      - geoffreyhinton  # Geoffrey Hinton (深度学习三巨头)
      - ylecun          # Yann LeCun (Meta AI Chief)
      - karpathy        # Andrej Karpathy (Eureka Labs)
      - chelseabfinn    # Chelsea Finn (Stanford, Physical Intelligence)
      - danijarh        # Danijar Hafner (Google DeepMind世界模型)
      - OpenAI          # OpenAI官方
      - DeepMind        # DeepMind官方
      # ... 更多账号见 config.yaml

# ============================================================
# 3. OpenAI API 配置
# ============================================================
base_url: https://api.openai.com/v1  # 官方API，或使用代理
api_key: your-openai-api-key-here
model: gpt-4o
max_tokens: 4096

# ============================================================
# 4. 筛选与性能配置
# ============================================================
min_relevance: medium           # 最小相关性：high/medium/low
max_concurrent: 5               # 最大并发请求数
batch_size: 25                  # 第一阶段批量筛选每批论文数
detail_batch_size: 5            # 第二阶段详细分析每批论文数

# ============================================================
# 5. 输出与通知配置
# ============================================================
output_dir: reports

email:
  enabled: true
  smtp_server: smtp.163.com
  smtp_port: 465
  use_ssl: true
  sender_email: your_email@163.com
  sender_password: your_auth_code      # 邮箱授权码
  receiver_email: receiver@gmail.com
  subject_prefix: "[ArXiv每日论文]"
```

### ArXiv类别参考

常用类别:
- `cs.AI` - Artificial Intelligence
- `cs.CL` - Computation and Language (NLP)
- `cs.CV` - Computer Vision and Pattern Recognition
- `cs.LG` - Machine Learning
- `cs.RO` - Robotics
- `cs.NE` - Neural and Evolutionary Computing
- `stat.ML` - Machine Learning (Statistics)

完整列表: https://arxiv.org/category_taxonomy

### 邮箱配置指南

**163 邮箱**：
1. 登录网页版 > 设置 > POP3/SMTP/IMAP
2. 开启 IMAP/SMTP 服务
3. 获取授权码（不是登录密码）
4. SMTP: `smtp.163.com:465`

**QQ 邮箱**：
1. 设置 > 账户 > POP3/SMTP 服务
2. 生成授权码
3. SMTP: `smtp.qq.com:465`

**Gmail**：
1. 开启两步验证
2. 生成应用专用密码
3. SMTP: `smtp.gmail.com:465`

---

## 📧 报告示例

### HTML 邮件报告
程序会自动发送精美的 HTML 格式邮件，包含：

**📊 核心发现**
- 本周研究热点总结（AI 生成）
- 重点推荐论文（高相关性）
- 统计数据可视化

**📑 详细论文列表**
- 按相关性分组（高/中/低）
- CNS 期刊特殊标识徽章
- 每篇论文包含：
  - 标题和作者
  - 发布日期和来源
  - AI 生成的中文摘要
  - 相关性分析和推荐理由
  - 论文链接和 PDF 下载

**🎨 响应式设计**
- 桌面端和移动端自适应
- 卡片式布局，清晰美观
- 直接点击标题跳转到论文

### Markdown 报告
同时会在 `reports/` 目录生成 Markdown 文件：
- 文件名格式：`arxiv_papers_YYYY-MM-DD.md`
- 方便本地查看和版本管理

## 定时自动运行

### 🚀 推荐方式：使用 GitHub Actions（云端运行，完全免费）

GitHub Actions 可以在云端每天自动运行，无需本地服务器，完全免费！

**优势**：
- ✅ 无需本地服务器24小时运行
- ✅ GitHub Actions 对公共仓库完全免费
- ✅ 自动发送 HTML 格式邮件报告
- ✅ 报告文件自动上传保存
- ✅ 支持手动触发和自定义参数

**快速设置**（5分钟）：

1. **Fork 或上传代码到 GitHub**

2. **配置 GitHub Secrets**
   - 进入仓库 **Settings** > **Secrets and variables** > **Actions**
   - 添加以下 Secrets：
     - `OPENAI_API_KEY`: 你的 OpenAI API 密钥
     - `EMAIL_SENDER`: 发送邮箱（如 your@163.com）
     - `EMAIL_PASSWORD`: 邮箱授权码（不是登录密码）
     - `EMAIL_RECEIVER`: 接收邮箱
     - （可选）`API_BASE_URL`: API 端点（使用代理时）

3. **启用 Actions**
   - workflow 文件已包含在 `.github/workflows/daily-arxiv.yml`
   - 推送代码后自动启用

4. **测试运行**
   - 进入 **Actions** 页面
   - 选择 **Daily ArXiv Paper Analysis**
   - 点击 **Run workflow** 手动测试

完成！每天 UTC 00:00（北京时间 08:00）会自动运行并发送邮件。

📖 **详细配置指南**: [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)

---

### 使用Cron (Linux/Mac)

编辑crontab:

```bash
crontab -e
```

添加定时任务（每天早上8点运行）:

```
0 8 * * * cd /home/zwt/code/arxiv-agent && /usr/bin/python3 main.py
```

### 使用Windows任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（每天特定时间）
4. 设置操作: 启动程序
   - 程序: `python`
   - 参数: `main.py`
   - 起始位置: `/home/zwt/code/arxiv-agent`

## 📁 项目结构

```
arxiv-agent/
├── .github/
│   └── workflows/
│       └── daily-arxiv.yml         # GitHub Actions 配置
├── src/                            # 源代码目录
│   ├── __init__.py
│   ├── arxiv_searcher.py          # ArXiv 搜索模块
│   ├── journal_fetcher.py         # 期刊文章获取模块
│   ├── llm_analyzer.py            # LLM 分析模块（两阶段）
│   ├── report_generator.py        # 报告生成模块（MD + HTML）
│   ├── email_sender.py            # 邮件发送模块
│   └── config_loader.py           # 配置加载模块
├── reports/                        # 生成的报告目录
│   └── arxiv_papers_YYYY-MM-DD.md
├── main.py                         # 主程序入口
├── config.yaml.example             # 配置文件模板
├── requirements.txt                # Python 依赖
├── README.md                       # 项目说明
└── GITHUB_ACTIONS_SETUP.md        # GitHub Actions 部署指南
```

## 💻 运行示例

```
============================================================
ArXiv Agent - 学术论文追踪与分析
============================================================

📖 研究方向: 自动驾驶, 具身智能, 强化学习, VLM
🔍 数据源: ArXiv, CNS期刊
⚙️  并发数: 5 | 批次大小: 25, 5

============================================================
1.1 获取 ArXiv 论文
============================================================
  类别 cs.RO: 找到 18 篇论文
  类别 cs.CV: 找到 32 篇论文
  类别 cs.AI: 找到 25 篇论文
  类别 cs.LG: 找到 28 篇论文
  类别 cs.CL: 找到 15 篇论文
✅ ArXiv: 找到 118 篇论文

============================================================
1.2 获取 CNS 期刊文章
============================================================
  Nature: 找到 2 篇文章
  Science: 找到 1 篇文章
  Nature Machine Intelligence: 找到 3 篇文章
  Science Robotics: 找到 1 篇文章
✅ 期刊: 找到 7 篇文章

============================================================
总计: 论文/文章 125 篇
============================================================

============================================================
2.1 第一阶段: 批量筛选（快速过滤）
============================================================
  批次 1/5: 分析 25 篇论文... ✓ 找到 8 篇相关
  批次 2/5: 分析 25 篇论文... ✓ 找到 6 篇相关
  批次 3/5: 分析 25 篇论文... ✓ 找到 5 篇相关
  批次 4/5: 分析 25 篇论文... ✓ 找到 4 篇相关
  批次 5/5: 分析 25 篇论文... ✓ 找到 3 篇相关

筛选结果: 26 篇相关论文（高: 12, 中: 14）

============================================================
2.2 第二阶段: 详细分析（深度解读）
============================================================
  批次 1/5: 详细分析 5 篇论文... ✓
  批次 2/5: 详细分析 5 篇论文... ✓
  批次 3/5: 详细分析 5 篇论文... ✓
  批次 4/5: 详细分析 5 篇论文... ✓
  批次 5/5: 详细分析 6 篇论文... ✓

============================================================
3. 生成报告
============================================================
正在生成 Markdown 报告...
正在生成 HTML 格式报告...
正在发送邮件到 receiver@gmail.com...

✅ 报告已生成: reports/arxiv_papers_2025-10-19.md
✅ 邮件已发送成功

============================================================
✨ 完成！
============================================================
📊 总论文数: 125 篇
📌 相关论文: 26 篇（高: 12, 中: 14）
⏱️  用时: 45.3 秒
```

## ❓ 常见问题

### 1. 邮件发送失败

**问题**: 邮件无法发送或提示认证失败

**解决**:
- 确认使用的是**邮箱授权码**，不是登录密码
- 检查 SMTP 服务器和端口配置是否正确
- 确认邮箱已开启 SMTP/IMAP 服务
- 查看错误日志获取详细信息

### 2. GitHub Actions 运行失败

**问题**: Actions 页面显示错误

**解决**:
- 检查所有必需的 Secrets 是否已配置
- 查看 Actions 运行日志，定位具体错误
- 确认 API 密钥有效且有足够额度
- 参考 [GitHub Actions 部署指南](GITHUB_ACTIONS_SETUP.md)

### 3. 没有找到论文

**问题**: 未找到任何论文或论文数量很少

**解决**:
- 增加 `days_back` 参数（如 3-7 天）
- 检查 ArXiv 类别配置是否正确
- 检查网络连接
- 尝试手动访问 ArXiv 确认可访问性

### 4. API 调用成本问题

**问题**: 担心 API 调用费用过高

**解决**:
- 两阶段筛选已经优化了 API 使用效率
- 调整 `max_results` 减少获取的论文数量
- 增加 `days_back` 但降低运行频率
- 使用 `min_relevance: high` 只保留高相关论文
- **成本估算**: 约 $0.10-0.30/天 或 $3-9/月（根据使用的GPT模型）

### 5. 相关性判断不准确

**问题**: AI 判断的相关性不符合预期

**解决**:
- 在 `config.yaml` 中填写详细的 `research_prompt`
- 更具体地描述研究方向和关注点
- 调整 `min_relevance` 阈值
- 查看报告中的推荐理由，理解 AI 的判断逻辑

### 6. 期刊获取速度慢

**问题**: 获取 CNS 期刊文章时间较长

**解决**:
- 在 `selected_journals` 中只选择你关注的期刊
- 减少期刊数量可显著提升速度
- 期刊更新频率低，可以设置更长的 `days_back`

---

## 🛠️ 技术栈

- **Python 3.10+**
- **arxiv** - ArXiv API 客户端
- **openai** - OpenAI 官方 Python SDK
- **PyYAML** - 配置文件解析
- **python-dateutil** - 日期处理
- **feedparser** - RSS/Atom 解析（期刊源）

---

## 📄 许可证

MIT License

---

## 👨‍💻 作者

Created with ❤️ by [Claude Code](https://claude.com/claude-code)

---

## 📅 更新日志

### v2.0.0 (2025-10-19)
- ✨ 新增 GitHub Actions 自动化支持
- ✨ 新增 HTML 邮件报告功能
- ✨ 新增 CNS 期刊数据源
- ⚡ 实现两阶段筛选策略，提升效率
- ⚡ 优化并发处理架构
- 🎨 精美的响应式 HTML 报告设计
- 📧 自动邮件发送功能
- 📝 完善的文档和部署指南

### v1.0.0 (2025-10-18)
- 🎉 初始版本
- 📚 支持 ArXiv 论文搜索
- 🧠 集成 OpenAI GPT 模型分析
- 📄 Markdown 报告生成
- 💻 命令行界面

---

## 🔗 相关链接

- [GitHub Actions 部署指南](GITHUB_ACTIONS_SETUP.md)
- [ArXiv 类别列表](https://arxiv.org/category_taxonomy)
- [OpenAI API 文档](https://platform.openai.com/docs)

---

**⭐ 如果觉得有用，请给个星标！**
