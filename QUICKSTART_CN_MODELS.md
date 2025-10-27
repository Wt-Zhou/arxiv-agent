# 国产模型快速入门指南

本指南帮助你快速配置 ArXiv Agent 使用便宜的国产模型。

## 推荐方案：DeepSeek（性价比最高）

### 第一步：获取 DeepSeek API Key

1. 访问 https://platform.deepseek.com/
2. 注册账号并登录
3. 在"API Keys"页面创建新的 API key
4. 充值（最低 ¥10，可用很久）

### 第二步：配置

方法1：使用示例配置文件
```bash
cp config.yaml.deepseek config.yaml
nano config.yaml  # 编辑配置文件，填入你的 API key
```

方法2：手动修改 config.yaml
```yaml
# 修改这几行
api_type: openai
api_base_url: https://api.deepseek.com
api_key: sk-xxxxxxxxxxxxx  # 你的 DeepSeek API key
model: deepseek-chat
max_tokens: 2048

# 可选：提高并发数（DeepSeek 便宜，可以加速）
max_concurrent: 10
batch_size: 30
detail_batch_size: 10
```

### 第三步：运行

```bash
python main.py
```

## 成本对比

处理 100 篇论文（约 500K tokens）的成本：

| 模型 | 成本 | 性能 |
|------|------|------|
| Claude Sonnet 4.5 | ¥40-50 | ⭐⭐⭐⭐⭐ |
| **DeepSeek** | **¥0.5-1** | ⭐⭐⭐⭐ |
| 通义千问 Turbo | ¥0.3-0.5 | ⭐⭐⭐ |
| GLM-4-Flash | 免费 | ⭐⭐⭐ |

**结论**: DeepSeek 价格是 Claude 的约 1/50，效果只差一点点，**强烈推荐**！

## 其他国产模型选择

### 通义千问（阿里云）

```yaml
api_type: openai
api_base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
api_key: sk-xxxxx  # 从 https://dashscope.console.aliyun.com/ 获取
model: qwen-turbo
```

### 智谱 GLM（有免费额度）

```yaml
api_type: openai
api_base_url: https://open.bigmodel.cn/api/paas/v4
api_key: xxxxx.xxxxx  # 从 https://open.bigmodel.cn/ 获取
model: glm-4-flash
```

## GitHub Actions 配置

在 GitHub 仓库的 Settings > Secrets and variables > Actions 中添加：

```
API_TYPE = openai
API_BASE_URL = https://api.deepseek.com
API_KEY = sk-xxxxxxxxxxxxx
MODEL_NAME = deepseek-chat
```

其他邮件配置保持不变。

## 常见问题

### Q: DeepSeek 效果怎么样？
A: 经过测试，DeepSeek 在论文分析、翻译、相关性判断等任务上表现优秀，与 Claude 差距很小，完全够用。

### Q: 会不会很慢？
A: 不会。由于便宜，你可以提高 `max_concurrent` 到 10-20，反而比 Claude 更快。

### Q: 安全吗？
A: DeepSeek 是正规的 AI 公司，API 调用是安全的。论文数据是公开的，不涉及隐私问题。

### Q: 如何切换回 Claude？
A: 只需修改 config.yaml：
```yaml
api_type: anthropic
api_base_url: https://api.anthropic.com
api_key: your-claude-key
model: claude-sonnet-4-5-20250929
```

## 详细文档

- 完整模型列表和配置：查看 `MODELS.md`
- 配置文件说明：查看 `config.yaml.example`
- 示例配置：查看 `config.yaml.deepseek` 和 `config.yaml.qwen`

## 开始使用

现在就试试 DeepSeek 吧！每天处理 50-100 篇论文，一个月只需要几块钱。
