# 多模型支持更新日志

## 版本 2.0 - 多模型支持

### 新增功能

✅ **支持多种 LLM 提供商**
- Anthropic Claude（原有支持）
- OpenAI 兼容 API（新增）
  - DeepSeek（强烈推荐，性价比最高）
  - 通义千问 Qwen
  - 智谱AI ChatGLM
  - 月之暗面 Moonshot
  - 字节豆包
  - 其他 OpenAI 兼容的模型

### 新增文件

1. **src/llm_client.py** - 通用 LLM 客户端
   - 支持 Anthropic 和 OpenAI 两种 API 格式
   - 统一的接口设计

2. **config.yaml.deepseek** - DeepSeek 配置示例
3. **config.yaml.qwen** - 通义千问配置示例
4. **MODELS.md** - 详细的模型配置指南
5. **QUICKSTART_CN_MODELS.md** - 国产模型快速入门

### 修改文件

1. **src/llm_analyzer.py**
   - 使用新的 LLMClient
   - 新增 `api_type` 参数

2. **src/twitter_analyzer.py**
   - 使用新的 LLMClient
   - 新增 `api_type` 参数

3. **src/config_loader.py**
   - 新增 `get_api_type()` 方法
   - 新增 `get_model_name()` 方法
   - 新增 `get_max_tokens()` 方法
   - 向后兼容旧的配置方法

4. **main.py**
   - 传递 `api_type` 参数给分析器
   - 更新错误提示信息

5. **config.yaml.example**
   - 添加多种模型的配置示例
   - 详细的注释说明

6. **.github/workflows/daily-arxiv.yml**
   - 支持新的环境变量格式
   - 向后兼容原有配置

### 配置变更

#### 新配置格式（推荐）

```yaml
# API 类型
api_type: openai  # 或 anthropic

# 统一的配置项
api_base_url: https://api.deepseek.com
api_key: your-api-key
model: deepseek-chat
max_tokens: 2048
```

#### 旧配置格式（仍然支持）

```yaml
api_base_url: https://api.anthropic.com
api_key: your-api-key
claude_model: claude-sonnet-4-5-20250929
claude_max_tokens: 1024
```

### 向后兼容性

✅ **完全向后兼容**
- 原有的 `claude_model` 和 `claude_max_tokens` 配置仍然有效
- 默认 `api_type` 为 `anthropic`
- 不需要修改现有配置即可正常运行

### 环境变量支持

新增环境变量：
- `API_TYPE` - API 类型
- `OPENAI_API_KEY` - OpenAI 兼容模型的 API key
- `MODEL_NAME` - 模型名称

原有环境变量仍然支持：
- `ANTHROPIC_API_KEY`
- `ANTHROPIC_BASE_URL`

### GitHub Actions 更新

需要添加的新 Secrets（如果使用国产模型）：
- `API_TYPE` - 设为 `openai`
- `API_KEY` - 你的模型 API key
- `MODEL_NAME` - 模型名称（如 `deepseek-chat`）

原有 Secrets 仍然支持：
- `ANTHROPIC_API_KEY`
- `API_BASE_URL`

### 性能优化建议

使用 DeepSeek 等便宜模型时，可以提高并发参数：

```yaml
max_concurrent: 10      # 原来建议 5
batch_size: 30          # 原来建议 25
detail_batch_size: 10   # 原来建议 5
```

### 成本对比

以处理 100 篇论文为例：

| 模型 | 成本 | 相对 Claude |
|------|------|------------|
| Claude Sonnet 4.5 | ¥40-50 | 1x |
| DeepSeek | ¥0.5-1 | **1/50** |
| Qwen Turbo | ¥0.3-0.5 | 1/100 |
| GLM-4-Flash | 免费 | 免费 |

### 迁移指南

#### 从 Claude 迁移到 DeepSeek

1. 获取 DeepSeek API key：https://platform.deepseek.com/
2. 修改 config.yaml：

```yaml
# 改这几行
api_type: openai
api_base_url: https://api.deepseek.com
api_key: sk-xxxxxxxxx  # 你的 DeepSeek key
model: deepseek-chat
max_tokens: 2048

# 可选：提高并发
max_concurrent: 10
```

3. 运行：`python main.py`

### 已知问题

无

### 测试状态

✅ 基本功能测试通过
✅ 配置加载测试通过
✅ 向后兼容性测试通过

### 下一步

考虑的未来改进：
- [ ] 支持更多模型提供商
- [ ] 自动选择最佳模型
- [ ] 成本统计和优化建议
- [ ] 模型性能对比工具

---

更新时间：2025-10-26
版本：2.0.0
