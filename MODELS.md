# 支持的 LLM 模型配置指南

ArXiv Agent 现在支持多种 LLM 提供商，包括 Anthropic Claude 和各种 OpenAI 兼容的国产模型。

## 快速开始

在 `config.yaml` 中设置两个关键参数：
- `api_type`: 选择 `anthropic` 或 `openai`
- `api_base_url`: API 端点地址
- `api_key`: API 密钥
- `model`: 模型名称

## 支持的模型提供商

### 1. Anthropic Claude（原始支持）

**优点**: 效果最好，推理能力强
**缺点**: 价格较贵

```yaml
api_type: anthropic
api_base_url: https://api.anthropic.com  # 或使用代理
api_key: your-anthropic-api-key
model: claude-sonnet-4-5-20250929
max_tokens: 1024
```

**价格参考**:
- Claude Sonnet 4.5: $3/M输入, $15/M输出
- Claude Haiku 3.5: $0.8/M输入, $4/M输出

### 2. DeepSeek（强烈推荐）🌟

**优点**: **极其便宜**且效果优秀，性价比最高
**缺点**: 无明显缺点

```yaml
api_type: openai
api_base_url: https://api.deepseek.com
api_key: your-deepseek-api-key
model: deepseek-chat
max_tokens: 2048
```

**价格参考**:
- deepseek-chat: ¥0.27/M输入, ¥1.1/M输出（**约为 Claude 的 1/100 价格**）
- deepseek-reasoner: ¥0.55/M输入, ¥2.19/M输出（深度思考模型）

**申请地址**: https://platform.deepseek.com/

### 3. 阿里通义千问 Qwen

**优点**: 国内访问快，价格适中
**缺点**: 需要阿里云账号

```yaml
api_type: openai
api_base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
api_key: your-qwen-api-key
model: qwen-turbo  # 或 qwen-plus, qwen-max
max_tokens: 2048
```

**价格参考**:
- qwen-turbo: ¥0.3/M输入, ¥0.6/M输出
- qwen-plus: ¥0.8/M输入, ¥2/M输出
- qwen-max: ¥4/M输入, ¥12/M输出

**申请地址**: https://dashscope.console.aliyun.com/

### 4. 智谱AI ChatGLM

**优点**: 有免费额度
**缺点**: 免费版本限制较多

```yaml
api_type: openai
api_base_url: https://open.bigmodel.cn/api/paas/v4
api_key: your-glm-api-key
model: glm-4-flash  # 或 glm-4, glm-4-plus
max_tokens: 2048
```

**价格参考**:
- glm-4-flash: 免费版本（有调用限制）
- glm-4: ¥0.1/M输入, ¥0.1/M输出
- glm-4-plus: ¥5/M输入, ¥50/M输出

**申请地址**: https://open.bigmodel.cn/

### 5. 月之暗面 Moonshot (Kimi)

**优点**: 长文本支持好
**缺点**: 价格中等

```yaml
api_type: openai
api_base_url: https://api.moonshot.cn/v1
api_key: your-moonshot-api-key
model: moonshot-v1-8k  # 或 moonshot-v1-32k, moonshot-v1-128k
max_tokens: 2048
```

**价格参考**:
- moonshot-v1-8k: ¥12/M tokens
- moonshot-v1-32k: ¥24/M tokens
- moonshot-v1-128k: ¥60/M tokens

**申请地址**: https://platform.moonshot.cn/

### 6. 字节跳动豆包

**优点**: 性价比高，免费额度
**缺点**: 需要火山引擎账号

```yaml
api_type: openai
api_base_url: https://ark.cn-beijing.volces.com/api/v3
api_key: your-doubao-api-key
model: doubao-pro-32k  # 或其他豆包模型
max_tokens: 2048
```

**申请地址**: https://console.volcengine.com/ark

## 性价比对比

按照每百万 tokens 的成本（输入+输出平均）：

1. **DeepSeek**: ¥0.68/M（最便宜，强烈推荐）⭐⭐⭐⭐⭐
2. **通义千问 Turbo**: ¥0.45/M（第二便宜）⭐⭐⭐⭐
3. **智谱 GLM-4**: ¥0.1/M（免费版本）⭐⭐⭐
4. **月之暗面**: ¥12/M ⭐⭐
5. **Claude**: $9/M ≈ ¥65/M（最贵但效果最好）⭐⭐⭐⭐⭐

## 性能建议

### 预算充足（追求最佳效果）
```yaml
api_type: anthropic
model: claude-sonnet-4-5-20250929
max_concurrent: 5  # 控制并发避免费用过高
```

### 性价比优先（推荐）⭐
```yaml
api_type: openai
api_base_url: https://api.deepseek.com
model: deepseek-chat
max_concurrent: 10  # DeepSeek 便宜，可以提高并发
batch_size: 30
detail_batch_size: 10
```

### 完全免费（测试用）
```yaml
api_type: openai
api_base_url: https://open.bigmodel.cn/api/paas/v4
model: glm-4-flash
max_concurrent: 3  # 免费版本有限制
```

## 配置示例文件

项目提供了以下配置示例文件：

- `config.yaml.example`: 完整配置说明（包含所有模型）
- `config.yaml.deepseek`: DeepSeek 专用配置
- `config.yaml.qwen`: 通义千问专用配置

使用方法：
```bash
# 使用 DeepSeek
cp config.yaml.deepseek config.yaml
# 编辑 config.yaml，填入你的 API key
nano config.yaml
```

## 环境变量支持

你也可以通过环境变量设置 API key：

```bash
# Anthropic
export ANTHROPIC_API_KEY="your-key"

# OpenAI 兼容（国产模型）
export OPENAI_API_KEY="your-key"
# 或
export API_KEY="your-key"
```

## 故障排除

### 1. API 调用失败

检查：
- API key 是否正确
- api_base_url 是否正确
- 网络连接是否正常
- 账户余额是否充足

### 2. 模型不支持

确保：
- `api_type` 设置正确（anthropic 或 openai）
- `model` 名称与提供商匹配
- 查看提供商文档确认模型名称

### 3. 请求超时

尝试：
- 降低 `max_concurrent` 并发数
- 减少 `batch_size` 批次大小
- 增加 `max_tokens` 避免截断

## 推荐配置

对于日常使用，我们推荐使用 **DeepSeek**：

```yaml
api_type: openai
api_base_url: https://api.deepseek.com
api_key: your-deepseek-api-key
model: deepseek-chat
max_tokens: 2048
max_concurrent: 10
batch_size: 30
detail_batch_size: 10
```

**理由**:
- 价格是 Claude 的约 1/100
- 效果接近 Claude，满足论文分析需求
- 可以提高并发数，加快处理速度
- 支持更大的 token 数

如需更详细的信息，请查看各提供商的官方文档。
