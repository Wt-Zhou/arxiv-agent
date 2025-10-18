# ArXiv Agent

自动搜索和分析ArXiv论文的智能Agent，使用Claude AI帮助筛选与你研究方向相关的最新论文。

## 功能特性

- **自动搜索**: 从ArXiv获取指定类别的最新论文
- **智能分析**: 使用Claude AI分析论文与你研究方向的相关性
- **相关性评级**: 自动将论文分为高、中、低相关性
- **精美报告**: 生成Markdown格式的论文报告，包含标题、摘要、链接等
- **灵活配置**: 支持自定义研究方向、ArXiv类别、搜索天数等
- **定时运行**: 可配合cron等工具实现每日自动运行

## 快速开始

### 5分钟上手

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置API密钥
cp .env.example .env
# 编辑 .env 文件，添加你的 API 密钥

# 3. 运行
python main.py

# 4. 查看报告
cat reports/arxiv_papers_$(date +%Y-%m-%d).md
```

就这么简单！程序会自动搜索ArXiv、使用Claude AI分析相关性、生成精美的Markdown报告。

### 常用命令

```bash
python main.py --days 3              # 搜索最近3天的论文
python main.py --min-relevance high  # 只显示高相关性论文
python main.py --no-analysis         # 不使用AI分析（节省API调用）
python main.py --max-concurrent 10   # 设置并发数为10（加快分析速度）
```

### 性能优化

本项目使用**异步并发 + 连接复用**技术，大幅提升论文分析速度：

- **默认并发数**: 5个同时请求
- **速度提升**: 相比串行处理快 **5-10倍**
- **连接复用**: 自动复用TCP连接，减少握手开销
- **可配置**: 在 `config.yaml` 中设置 `max_concurrent` 或使用 `--max-concurrent` 参数

**性能对比**:
- 串行处理: 100篇论文 ≈ 200秒
- 并发处理(5): 100篇论文 ≈ 40秒 ⚡
- 并发处理(10): 100篇论文 ≈ 20秒 ⚡⚡

详细架构设计请查看: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 安装

### 1. 克隆或下载项目

```bash
cd /home/zwt/code/arxiv-agent
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API密钥

创建 `.env` 文件:

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加你的Anthropic API密钥:

```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

获取API密钥: https://console.anthropic.com/

## 配置

编辑 `config.yaml` 文件来自定义设置:

```yaml
# 你的研究方向
research_interests:
  - 自动驾驶
  - 具身智能
  - 强化学习
  - VLM (Vision Language Models)

# ArXiv类别
arxiv_categories:
  - cs.RO  # Robotics
  - cs.CV  # Computer Vision
  - cs.AI  # Artificial Intelligence
  - cs.LG  # Machine Learning
  - cs.CL  # Computation and Language

# 每次搜索获取的论文数量上限
max_results: 100

# 搜索最近几天的论文
days_back: 1

# Claude模型配置
claude_model: claude-3-5-sonnet-20241022
claude_max_tokens: 1024

# 输出报告路径
output_dir: reports
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

## 使用方法

### 基本使用

搜索最近一天的论文并分析:

```bash
python main.py
```

### 高级选项

搜索最近3天的论文:

```bash
python main.py --days 3
```

仅搜索，不使用AI分析（节省API调用）:

```bash
python main.py --no-analysis
```

只显示高相关性的论文:

```bash
python main.py --min-relevance high
```

使用自定义配置文件:

```bash
python main.py --config my_config.yaml
```

查看所有选项:

```bash
python main.py --help
```

## 输出报告

报告会保存在 `reports/` 目录下，文件名格式为 `arxiv_papers_YYYY-MM-DD.md`

报告内容包括:
- 研究方向列表
- 统计信息（总论文数、相关性分布）
- 按相关性分组的论文列表:
  - **强烈推荐** (高相关性)
  - **推荐阅读** (中等相关性)
  - **可能感兴趣** (低相关性)

每篇论文包含:
- 标题
- 作者
- 发布日期
- 类别
- 论文链接和PDF链接
- AI生成的摘要总结
- 相关领域匹配
- 推荐理由

## 定时自动运行

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

## 项目结构

```
arxiv-agent/
├── main.py                 # 主程序入口
├── config.yaml            # 配置文件
├── requirements.txt       # Python依赖
├── .env                   # API密钥（需自行创建）
├── .env.example          # API密钥示例
├── README.md             # 说明文档
├── src/                  # 源代码目录
│   ├── __init__.py
│   ├── arxiv_searcher.py      # ArXiv搜索模块
│   ├── llm_analyzer.py        # Claude分析模块
│   ├── report_generator.py    # 报告生成模块
│   └── config_loader.py       # 配置加载模块
└── reports/              # 生成的报告目录
    └── arxiv_papers_YYYY-MM-DD.md
```

## 示例输出

```
============================================================
ArXiv Agent - 论文搜索与分析
============================================================

正在加载配置文件: config.yaml
研究方向: 自动驾驶, 具身智能, 强化学习, VLM (Vision Language Models)
ArXiv类别: cs.RO, cs.CV, cs.AI, cs.LG, cs.CL
搜索最近 1 天的论文
最大结果数: 100

============================================================
步骤 1: 搜索ArXiv论文
============================================================
搜索类别: cs.RO
搜索类别: cs.CV
搜索类别: cs.AI
搜索类别: cs.LG
搜索类别: cs.CL
共找到 87 篇论文
找到 87 篇论文

============================================================
步骤 2: 使用Claude分析论文相关性
============================================================
正在分析论文 1/87: Vision-Language Models for Autonomous Driving...
正在分析论文 2/87: Reinforcement Learning in Robotics...
...

找到 23 篇相关论文

============================================================
步骤 3: 生成报告
============================================================
报告已生成: reports/arxiv_papers_2025-10-18.md

============================================================
完成!
============================================================
报告已保存到: reports/arxiv_papers_2025-10-18.md
总论文数: 87
相关论文数: 23
```

## 常见问题

### 1. API密钥错误

**问题**: `错误: 未找到ANTHROPIC_API_KEY环境变量`

**解决**: 确保创建了 `.env` 文件并正确设置了API密钥

### 2. 没有找到论文

**问题**: `未找到任何论文`

**解决**:
- 检查网络连接
- 尝试增加 `days_back` 参数
- 检查ArXiv类别是否正确

### 3. API调用过多

**问题**: 担心API调用费用

**解决**:
- 使用 `--no-analysis` 跳过AI分析
- 减少 `max_results` 数量
- 增加 `days_back` 但减少运行频率

### 4. 相关性判断不准确

**问题**: AI判断的相关性不符合预期

**解决**:
- 在 `config.yaml` 中更具体地描述研究方向
- 调整 `--min-relevance` 参数
- 查看完整报告中的推荐理由

## 技术栈

- **Python 3.7+**
- **arxiv** - ArXiv API客户端
- **anthropic** - Claude API客户端
- **PyYAML** - 配置文件解析
- **python-dotenv** - 环境变量管理

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 作者

Created with Claude Code

## 更新日志

### v1.0.0 (2025-10-18)
- 初始版本
- 支持ArXiv论文搜索
- 集成Claude AI分析
- Markdown报告生成
- 命令行界面
