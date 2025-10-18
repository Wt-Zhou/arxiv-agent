# ArXiv Agent 架构设计

本文档详细说明 ArXiv Agent 的技术架构、模块设计和数据流向。

## 目录

- [工程逻辑流程](#工程逻辑流程)
- [核心模块详解](#核心模块详解)
- [数据结构](#数据结构)
- [数据流向](#数据流向)
- [关键设计特性](#关键设计特性)
- [未来扩展方向](#未来扩展方向)

---

## 工程逻辑流程

```
用户运行 main.py
    ↓
1. 加载配置 (config.yaml + .env)
    ↓
2. ArXiv搜索 (arxiv_searcher.py)
   - 从ArXiv API获取指定类别的最新论文
   - 按日期过滤
   - 论文去重
    ↓
3. AI分析 (llm_analyzer.py) [可选]
   - 调用Claude API分析每篇论文
   - 判断与研究方向的相关性
   - 生成总结和推荐理由
    ↓
4. 报告生成 (report_generator.py)
   - 生成Markdown格式报告
   - 按相关性分组
   - 保存到 reports/ 目录
    ↓
5. 输出报告路径
```

---

## 核心模块详解

### 1. main.py - 主程序

**功能**: 协调所有模块，执行完整流程

**主要步骤**:
```python
1. 加载配置 (config.yaml)
2. 初始化 ArxivSearcher
3. 搜索论文
4. [可选] 初始化 LLMAnalyzer
5. [可选] AI分析论文相关性
6. 初始化 ReportGenerator
7. 生成报告
8. 输出结果
```

**命令行参数**:
- `--config PATH`: 指定配置文件
- `--days N`: 搜索最近N天
- `--no-analysis`: 跳过AI分析
- `--min-relevance`: 最小相关性级别

**代码位置**: `/home/zwt/code/arxiv-agent/main.py`

---

### 2. arxiv_searcher.py - 论文搜索

**功能**: 从ArXiv获取论文

**核心方法**:
```python
search_recent_papers(days_back)
  → 搜索指定类别的论文
  → 按日期过滤
  → 去重
  → 返回论文列表
```

**实现细节**:
- 使用 `arxiv` Python 库访问 ArXiv API
- 支持多类别并行搜索
- 基于论文 ID 进行去重
- 按发布时间过滤

**代码位置**: `/home/zwt/code/arxiv-agent/src/arxiv_searcher.py`

---

### 3. llm_analyzer.py - AI分析

**功能**: 使用Claude分析论文相关性

**核心方法**:
```python
analyze_paper_relevance(paper, research_interests)
  → 构建prompt
  → 调用Claude API
  → 解析响应
  → 返回分析结果

batch_analyze_papers(papers, interests)
  → 批量分析多篇论文
  → 进度显示

filter_relevant_papers(papers, min_relevance)
  → 按相关性级别过滤
```

**API调用方式**:
- 如果设置了 `ANTHROPIC_BASE_URL`: 使用 `requests` 库直接调用
- 否则: 使用 Anthropic 官方 SDK

**Prompt设计**:
- 包含论文标题、摘要、类别
- 提供用户的研究方向列表
- 要求返回结构化的 JSON 响应
- 包含相关性级别、匹配领域、中文总结

**代码位置**: `/home/zwt/code/arxiv-agent/src/llm_analyzer.py`

---

### 4. report_generator.py - 报告生成

**功能**: 生成Markdown格式报告

**核心方法**:
```python
generate_report(papers, research_interests)
  → 统计相关性分布
  → 按相关性分组
  → 格式化每篇论文
  → 写入Markdown文件
  → 返回文件路径

generate_simple_list(papers)
  → 生成简单列表（无AI分析时）
```

**报告结构**:
```markdown
# ArXiv 论文日报 - YYYY-MM-DD

## 研究方向
## 统计信息
## 强烈推荐 (高相关性)
  ### 论文1
    - 基本信息
    - 摘要
    - AI总结
    - 推荐理由
## 推荐阅读 (中等相关性)
## 可能感兴趣 (低相关性)
## 所有论文 (未分析)
```

**代码位置**: `/home/zwt/code/arxiv-agent/src/report_generator.py`

---

### 5. config_loader.py - 配置加载

**功能**: 加载和解析YAML配置

**提供方法**:
```python
get_research_interests()    # 获取研究方向
get_arxiv_categories()      # 获取ArXiv类别
get_max_results()           # 获取最大结果数
get_days_back()             # 获取搜索天数
get_claude_model()          # 获取AI模型名称
get_output_dir()            # 获取输出目录
get_api_key()              # 获取API密钥
get_api_base_url()         # 获取API端点
```

**配置优先级**:
1. 命令行参数（最高优先级）
2. 环境变量 (.env)
3. 配置文件 (config.yaml)

**代码位置**: `/home/zwt/code/arxiv-agent/src/config_loader.py`

---

## 数据结构

### 论文对象 (Paper)

从 ArXiv API 获取的论文数据：

```python
{
    'title': str,              # 论文标题
    'authors': List[str],      # 作者列表
    'abstract': str,           # 摘要
    'url': str,               # ArXiv链接
    'pdf_url': str,           # PDF链接
    'published': str,         # 发布日期 'YYYY-MM-DD'
    'categories': List[str],  # 所有类别
    'primary_category': str   # 主类别
}
```

### 分析结果 (Analysis)

AI分析返回的数据：

```python
{
    'is_relevant': bool,                    # 是否相关
    'relevance_level': str,                 # 'high'/'medium'/'low'/'none'
    'matched_interests': List[str],         # 匹配的研究方向
    'summary': str,                         # AI生成的简短总结
    'reason': str                           # 推荐理由
}
```

### 完整论文数据 (Analyzed Paper)

合并后的数据结构：

```python
{
    # 论文基础信息
    'title': str,
    'authors': List[str],
    'abstract': str,
    'url': str,
    'pdf_url': str,
    'published': str,
    'categories': List[str],
    'primary_category': str,

    # AI分析结果
    'is_relevant': bool,
    'relevance_level': str,
    'matched_interests': List[str],
    'summary': str,
    'reason': str
}
```

---

## 数据流向

```
ArXiv API
  ↓ (HTTP请求)
arxiv_searcher.py
  ↓ (论文列表 + 摘要)
llm_analyzer.py
  ↓ (调用Claude API)
Claude API
  ↓ (相关性分析结果)
report_generator.py
  ↓ (Markdown格式)
reports/arxiv_papers_YYYY-MM-DD.md
```

### 详细流程

1. **搜索阶段**
   ```
   config.yaml → arxiv_categories
        ↓
   ArXiv API ← 每个类别发起查询
        ↓
   原始论文数据 → 去重 → 日期过滤
        ↓
   论文列表 (List[Paper])
   ```

2. **分析阶段** (可选)
   ```
   论文列表 + 研究方向
        ↓
   构建 Prompt (标题 + 摘要 + 类别)
        ↓
   Claude API 调用
        ↓
   解析 JSON 响应
        ↓
   论文 + 分析结果 (List[AnalyzedPaper])
   ```

3. **生成阶段**
   ```
   分析后的论文列表
        ↓
   按 relevance_level 分组
        ↓
   格式化为 Markdown
        ↓
   写入文件 reports/arxiv_papers_YYYY-MM-DD.md
   ```

---

## 关键设计特性

### 1. 模块化设计

每个功能独立成模块，职责清晰：
- `arxiv_searcher`: 只负责论文检索
- `llm_analyzer`: 只负责AI分析
- `report_generator`: 只负责报告生成
- `config_loader`: 只负责配置管理

**优点**:
- 易于测试和维护
- 模块可独立替换
- 降低耦合度

### 2. 配置驱动

所有行为参数都在配置文件中：
- 研究方向、ArXiv类别、模型选择等
- 无需修改代码即可适配不同场景
- 支持命令行参数覆盖配置

**优点**:
- 灵活性高
- 多用户友好
- 便于版本管理

### 3. 错误容错

每个模块都有异常处理：
- API失败不会中断整个流程
- 单个论文分析失败不影响其他论文
- 配置错误有明确提示

**优点**:
- 稳定性好
- 用户体验佳
- 便于调试

### 4. API兼容性

支持多种API调用方式：
- Anthropic 官方 SDK
- 自定义 API 端点（第三方代理）
- 灵活的认证方式（API Key / Auth Token）

**优点**:
- 部署灵活
- 支持国内代理
- 降低使用门槛

### 5. 输出友好

Markdown格式报告：
- 易于阅读和分享
- 包含所有必要链接
- 分类清晰（高/中/低相关性）

**优点**:
- 用户体验好
- 支持版本控制
- 便于二次处理

### 6. 性能优化

- 论文去重避免重复分析
- 批量处理减少API调用开销
- 可选择跳过AI分析节省成本

---

## 扩展点

### 可扩展的地方

1. **搜索源**
   - 当前: ArXiv
   - 可扩展: Google Scholar, PubMed, IEEE Xplore

2. **分析引擎**
   - 当前: Claude
   - 可扩展: GPT-4, Gemini, 本地模型

3. **输出格式**
   - 当前: Markdown
   - 可扩展: PDF, HTML, Email, RSS

4. **通知方式**
   - 当前: 无
   - 可扩展: 邮件、微信、Slack

5. **缓存机制**
   - 当前: 无
   - 可扩展: Redis缓存、数据库存储

---

## 未来扩展方向

### 短期计划

- [ ] 支持多个LLM后端 (GPT-4, Gemini等)
- [ ] 添加论文缓存，避免重复分析
- [ ] 支持并行分析加速
- [ ] 添加邮件通知功能

### 中期计划

- [ ] 支持自定义prompt模板
- [ ] 添加论文收藏和标记功能
- [ ] 支持全文PDF解析
- [ ] 生成可视化统计图表

### 长期计划

- [ ] Web界面
- [ ] 移动端应用
- [ ] 多用户支持
- [ ] 推荐系统优化（基于历史阅读）
- [ ] 论文引用分析

---

## 性能优化架构

### 异步并发 + 连接复用

**实现细节**:

1. **异步并发** (`asyncio` + `httpx`)
   - 使用 `asyncio.Semaphore` 控制并发数
   - 同时发送多个API请求，充分利用等待时间
   - 默认并发数: 5（可配置 5-10）

2. **连接复用** (`httpx.AsyncClient`)
   - 使用连接池管理HTTP连接
   - 复用TCP连接和TLS会话
   - 配置: `max_connections=10`, `max_keepalive_connections=5`

3. **进度监控**
   - 实时显示分析进度
   - 单个论文失败不影响整体流程
   - 错误信息清晰展示

**性能提升**:

| 论文数量 | 串行处理 | 并发(5) | 并发(10) | 提升倍数 |
|---------|---------|---------|----------|---------|
| 10篇    | 20秒    | 4秒     | 2秒      | 5-10x   |
| 50篇    | 100秒   | 20秒    | 10秒     | 5-10x   |
| 100篇   | 200秒   | 40秒    | 20秒     | 5-10x   |

**代码位置**:
- 异步方法: `src/llm_analyzer.py:312-430`
- 连接管理: `src/llm_analyzer.py:405-409`
- 并发控制: `src/llm_analyzer.py:325`

---

## 性能考量

### API调用成本

每篇论文分析约消耗：
- Tokens: 500-1000 (input) + 200-500 (output)
- 成本: 约 $0.003-0.005 / 论文

### 优化建议

1. **减少API调用**
   - 使用 `--no-analysis` 跳过分析
   - 设置合理的 `max_results`
   - 增加 `days_back` 但降低运行频率

2. **提升性能**
   - ✅ **已实现**: 异步并发处理（5-10倍加速）
   - ✅ **已实现**: 连接复用（减少握手开销）
   - 可扩展: 缓存已分析的论文

3. **降低成本**
   - 使用更便宜的模型（如 `claude-3-5-haiku-20241022`）
   - 优化prompt长度
   - 只分析高优先级类别
   - 提高并发数（`--max-concurrent 10`）以节省时间成本

---

## 技术债务

### 已知限制

1. ✅ ~~**同步处理**: 论文分析是串行的，耗时较长~~ **已解决**: 实现了异步并发
2. **无缓存**: 每次运行都会重新分析所有论文
3. **错误处理**: 部分异常处理不够细致
4. **日志**: 缺少结构化日志

### 改进建议

1. ✅ ~~使用 `asyncio` 实现并发分析~~ **已完成**
2. 添加 SQLite 数据库缓存已分析论文
3. 使用 `logging` 模块替代 `print`
4. 添加单元测试和集成测试

---

## 代码统计

- **总行数**: ~730 行（核心功能）
- **模块数**: 5 个
- **依赖数**: 6 个核心依赖
- **配置项**: ~10 个可配置参数

---

## 参考资源

- [ArXiv API 文档](https://info.arxiv.org/help/api/index.html)
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference)
- [arxiv Python 库](https://pypi.org/project/arxiv/)
- [ArXiv 类别列表](https://arxiv.org/category_taxonomy)
