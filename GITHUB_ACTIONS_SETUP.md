# GitHub Actions 部署指南

本文档说明如何将 ArXiv Agent 部署到 GitHub Actions，实现每日自动运行并发送邮件报告。

---

## ⚡ 快速开始（5分钟）

如果您想快速上手，只需完成以下步骤：

### 📋 前置准备

- ✅ GitHub 账户
- ✅ OpenAI API 密钥（或第三方代理密钥）
- ✅ 163/QQ/Gmail 邮箱（用于发送报告）

### 🚀 5分钟部署步骤

#### 1️⃣ Fork 或上传代码到 GitHub

将此项目代码推送到你的 GitHub 仓库。

#### 2️⃣ 配置 Secrets（必需）

进入仓库 **Settings** > **Secrets and variables** > **Actions**，点击 **New repository secret**，添加以下 4 个 Secrets：

| Secret 名称 | 值 | 说明 |
|------------|---|------|
| `OPENAI_API_KEY` | `sk-proj-xxx` | OpenAI API 密钥 |
| `EMAIL_SENDER` | `your@163.com` | 发送邮箱 |
| `EMAIL_PASSWORD` | `ABCD1234` | 邮箱授权码（不是密码） |
| `EMAIL_RECEIVER` | `receiver@gmail.com` | 接收邮箱 |

**💡 如何获取邮箱授权码？**

**163邮箱**：
1. 登录网页版 → 设置 → POP3/SMTP/IMAP
2. 开启服务 → 获取授权码

**QQ邮箱**：
1. 登录网页版 → 设置 → 账户
2. 开启POP3/SMTP → 获取授权码
3. 额外添加Secret：`EMAIL_SMTP_SERVER` = `smtp.qq.com`

**Gmail**：
1. 开启两步验证
2. 生成应用专用密码
3. 额外添加Secrets：
   - `EMAIL_SMTP_SERVER` = `smtp.gmail.com`
   - `EMAIL_SMTP_PORT` = `465`

#### 3️⃣ 手动测试运行

1. 进入仓库的 **Actions** 页面
2. 选择 **Daily ArXiv Paper Analysis** workflow
3. 点击 **Run workflow** 按钮
4. 等待运行完成（约5-10分钟）
5. 检查邮箱是否收到报告

#### 4️⃣ 完成！🎉

现在系统会在每天 UTC 00:00（北京时间 08:00）自动运行并发送邮件报告。

---

## 📚 详细配置说明

### 功能特性

- ✅ 每天自动运行（UTC 00:00，北京时间 08:00）
- ✅ 支持手动触发，可自定义参数
- ✅ 自动发送 HTML 格式邮件报告
- ✅ 报告文件上传为 Artifacts（保留 30 天）
- ✅ 可选：自动提交报告到 Git 仓库
- ✅ 使用 OpenAI GPT 模型进行智能分析
- ✅ **可选：Twitter 学术动态爬取与分析（无需 API）**

### 完整的 Secrets 配置

#### 必需的 Secrets：

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-proj-xxx` 或第三方代理密钥 |
| `EMAIL_SENDER` | 发送邮箱地址 | `your_email@163.com` |
| `EMAIL_PASSWORD` | 邮箱授权码（不是登录密码） | `ABCD1234EFGH5678` |
| `EMAIL_RECEIVER` | 接收邮箱地址 | `receiver@gmail.com` |

#### 可选的 Secrets：

| Secret 名称 | 说明 | 默认值 |
|------------|------|--------|
| `API_BASE_URL` | OpenAI API 端点（使用代理时） | `https://api.openai.com/v1` |
| `MODEL_NAME` | 使用的模型名称 | `gpt-4o` |
| `EMAIL_SMTP_SERVER` | SMTP 服务器地址 | `smtp.163.com` |
| `EMAIL_SMTP_PORT` | SMTP 服务器端口 | `465` |
| `TWITTER_ENABLED` | 启用 Twitter 学术动态爬取 | `false` |

### 获取 OpenAI API 密钥

#### 官方 OpenAI API：
1. 访问 [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. 登录你的 OpenAI 账户
3. 创建新的 API 密钥
4. 复制密钥并填入 `OPENAI_API_KEY` Secret

#### 第三方代理（如 ChatAnywhere）：
1. 如果使用第三方代理服务，获取对应的 API 密钥
2. 设置 `API_BASE_URL` Secret 为代理地址（如 `https://api.chatanywhere.tech/v1`）
3. 将代理提供的 API 密钥填入 `OPENAI_API_KEY`

### 手动运行参数

手动触发 workflow 时，可以自定义以下参数：

| 参数名 | 说明 | 默认值 |
|-------|------|--------|
| `days_back` | 搜索最近几天的论文 | `1` |
| `max_concurrent` | 最大并发请求数 | `5` |
| `min_relevance` | 相关性阈值（high/medium/low） | `medium` |

### 查看运行结果

#### 方式1：邮件报告
检查 `EMAIL_RECEIVER` 邮箱，会收到精美的 HTML 格式报告，包含：
- 论文标题、摘要、链接
- AI 生成的核心内容总结
- 相关性分析
- 可展开/折叠的详细摘要
- 💾 一键下载按钮（自动命名）

#### 方式2：下载 Artifacts
在 Actions 运行详情页，点击 **Artifacts** 下载报告文件（保留30天）。

#### 方式3：Git 仓库
报告会自动提交到仓库的 `reports/` 目录（可选功能）。

---

## ⚙️ 自定义配置

### 修改运行时间

编辑 `.github/workflows/daily-arxiv.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 00:00，北京时间 08:00
  # 改为 UTC 22:00（北京时间 06:00）
  - cron: '0 22 * * *'
  # 仅工作日运行（周一到周五）
  - cron: '0 0 * * 1-5'
```

### 修改研究方向

编辑 `.github/workflows/daily-arxiv.yml` 中的 `research_interests` 和 `research_prompt` 部分（第55-71行）：

```yaml
research_interests:
  - 你的研究方向1
  - 你的研究方向2
  - 你的研究方向3

research_prompt: |
  详细描述你的研究兴趣...
```

### 切换 GPT 模型

设置 `MODEL_NAME` Secret 为不同的模型：
- `gpt-4o` - 最强大的多模态模型（推荐）
- `gpt-4o-mini` - 快速且经济
- `gpt-3.5-turbo` - 最经济的选择

### 多个接收邮箱

修改 workflow 中的 `receiver_email` 配置：

```yaml
receiver_email: "email1@gmail.com,email2@outlook.com"
```

### 禁用自动提交报告

如果不需要将报告提交到 Git 仓库，可以删除或注释掉最后的 "Commit and push reports" 步骤。

---

## 📱 Twitter 学术动态功能

### 功能说明

Twitter 功能可以自动爬取学术账号的最新推文，并通过 AI 分析其与你研究方向的相关性，与论文一起发送到邮件报告中。

**特点**：
- ✅ 使用 Selenium 浏览器自动化（无需 Twitter API）
- ✅ 完全免费，无额度限制
- ✅ 自动分析推文相关性
- ✅ 与论文报告整合在同一封邮件

### 启用 Twitter 功能

#### 方法：配置 GitHub Secret

在 GitHub 仓库的 **Settings** > **Secrets and variables** > **Actions** 中添加：

```
Secret 名称: TWITTER_ENABLED
Secret 值: true
```

### 默认配置

GitHub Actions 配置文件中已预设 **10 个热门学术账号**：

| 账号 | 说明 |
|------|------|
| `karpathy` | Andrej Karpathy (Eureka Labs) |
| `OpenAI` | OpenAI 官方 |
| `ylecun` | Yann LeCun (Meta AI Chief) |
| `DeepMind` | DeepMind 官方 |
| `chelseabfinn` | Chelsea Finn (Stanford, Physical Intelligence) |
| `danijarh` | Danijar Hafner (Google DeepMind 世界模型) |
| `_akhaliq` | AK (Papers with Code，每日 AI 论文) |
| `hardmaru` | David Ha (Stability AI，世界模型) |
| `svlevine` | Sergey Levine (UC Berkeley 强化学习) |
| `NVIDIAAI` | NVIDIA AI 官方 |

**配置参数**：
- `days_back: 7` - 获取最近 7 天的推文
- `tweets_per_user: 2` - 每个账号获取 2 条推文

### 性能与时间

| 账号数量 | 预计时间 | 说明 |
|---------|---------|------|
| 10 个 | 2-3 分钟 | 默认配置 |
| 20 个 | 4-6 分钟 | 需修改配置文件 |
| 50 个 | 8-12 分钟 | 完整账号列表 |

**注意事项**：
- Twitter 有反爬虫机制，部分账号可能超时（正常现象）
- 超时不会影响其他账号的爬取
- 如果大部分账号都失败，可暂时禁用 Twitter 功能

### 自定义 Twitter 账号列表

如需添加更多账号或修改列表，编辑 `.github/workflows/daily-arxiv.yml` 文件的 Twitter 配置部分：

```yaml
twitter:
  enabled: ${TWITTER_ENABLED}
  days_back: 7
  tweets_per_user: 2
  following_usernames:
    - karpathy
    - OpenAI
    # 添加更多账号...
    - your_favorite_researcher
```

**50 个完整账号配置**：参考本地 `config.yaml` 文件中的完整列表，包括：
- 顶级 AI 研究者（Geoffrey Hinton, Yann LeCun 等）
- 机器人与具身智能（Chelsea Finn, Marco Pavone 等）
- 强化学习与世界模型（Danijar Hafner, David Ha 等）
- 顶级研究机构（Stanford AI Lab, DeepMind, OpenAI 等）
- 会议与主题账号（CoRL, IEEE ICRA, Deep RL 等）

### Twitter 推文在报告中的展示

#### 1. 核心概览部分
显示推文主题总结和代表性讨论：
```
📱 Twitter 学术动态
本期 Twitter 学术圈的热点话题包括：大语言模型（3条）| 强化学习（2条）
为您精选 3 条最具代表性的讨论：
1. @karpathy: 推文预览...
```

#### 2. 独立章节
按相关性分级展示：
```
📱 Twitter 学术动态

强烈推荐 (高相关性)
━━━━━━━━━━━━━━━━━━━━━━━
@OpenAI
2025-10-28 13:06:48
推文内容...
相关性: 与您关注的 xxx 直接相关
👍 2341 | 🔄 567 | 💬 123
查看推文

值得关注 (中等相关性)
━━━━━━━━━━━━━━━━━━━━━━━
...
```

### 禁用 Twitter 功能

如需禁用 Twitter 功能：
1. 删除 `TWITTER_ENABLED` Secret
2. 或将其值改为 `false`

---

## 💰 成本估算

### API 调用成本

#### 不启用 Twitter：
假设每天：
- 获取 50 篇 ArXiv 论文 + 5 篇期刊文章 = 55 篇
- 第一阶段筛选：55 / 15 = 4 批次
- 筛选出 15 篇相关论文
- 第二阶段详细分析：15 / 5 = 3 批次

**Token 使用估算**：
- 输入 Token：约 25K tokens/天
- 输出 Token：约 8K tokens/天

#### 启用 Twitter（10 个账号）：
额外增加：
- Twitter 推文分析：约 10 条推文
- 额外 Token：约 5K 输入 + 2K 输出

**总计**（含 Twitter）：
- 输入 Token：约 30K tokens/天
- 输出 Token：约 10K tokens/天

**费用估算**（OpenAI 官方 API，2025年定价）：

| 模型 | 每天成本（无 Twitter） | 每天成本（含 Twitter） | 每月成本（含 Twitter） | 说明 |
|------|---------------------|---------------------|---------------------|------|
| gpt-4o | ~$0.14 | ~$0.17 | ~$5.1 | 最强大，推荐 |
| gpt-4o-mini | ~$0.01 | ~$0.015 | ~$0.45 | 经济实惠 |
| gpt-3.5-turbo | ~$0.025 | ~$0.03 | ~$0.9 | 最便宜 |

> 注意：
> - 使用第三方代理可能有不同的定价
> - Twitter 功能增加约 20% 的 API 成本
> - 50 个 Twitter 账号约增加 50% 成本

### GitHub Actions 成本

GitHub Actions 对公共仓库免费，私有仓库每月有 2000 分钟免费额度。

| 配置 | 每次运行时间 | 每月总时长（30次） | 状态 |
|------|------------|------------------|------|
| 不启用 Twitter | 5-10 分钟 | 150-300 分钟 | ✅ 免费额度内 |
| 启用 Twitter（10 账号） | 7-13 分钟 | 210-390 分钟 | ✅ 免费额度内 |
| 启用 Twitter（50 账号） | 13-22 分钟 | 390-660 分钟 | ✅ 免费额度内 |

**总结**：即使启用 50 个 Twitter 账号，每月约 660 分钟，仍在 2000 分钟免费额度内。

---

## ❓ 故障排查

### Q: 没有收到邮件？

**可能原因**：
- 邮箱授权码错误
- SMTP 服务器/端口配置错误
- 邮箱未开启 SMTP 服务

**解决方法**：
1. 检查 Secrets 中的邮箱配置是否正确
2. 确认使用的是**授权码**而不是登录密码
3. 查看 Actions 运行日志中的错误信息
4. 确认邮箱已开启 SMTP/IMAP 服务
5. 检查垃圾邮件文件夹

### Q: API 调用失败？

**可能原因**：
- API 密钥错误或过期
- API 额度不足
- 网络连接问题

**解决方法**：
1. 检查 `OPENAI_API_KEY` 是否正确
2. 如果使用第三方代理，检查 `API_BASE_URL` 配置
3. 查看 OpenAI 账户余额和使用情况
4. 检查是否触发了速率限制

### Q: 筛选出的论文太少？

**可能原因**：
- 相关性阈值设置过高
- 研究方向描述不够明确
- ArXiv 分类配置不正确

**解决方法**：
1. 手动运行时，设置 `min_relevance` 为 `low` 以获取更多论文
2. 优化 `research_prompt` 描述，更具体地说明研究方向
3. 增加 `days_back` 参数值
4. 检查 workflow 中的 `categories` 配置
5. 当前 `batch_size` 已优化为 15（提高准确性）

### Q: 找不到论文？

**可能原因**：
- ArXiv 分类配置不正确
- 搜索时间范围太短
- 网络问题导致无法访问 ArXiv

**解决方法**：
1. 检查 workflow 中的 `categories` 配置
2. 增加 `days_back` 参数
3. 查看运行日志确认问题

### Q: HTML报告中的功能无法使用？

**可能原因**：
- 邮件客户端不支持 JavaScript
- 浏览器安全设置

**解决方法**：
1. 下载 HTML 报告到本地，用浏览器打开
2. 确保浏览器允许运行 JavaScript
3. 使用现代浏览器（Chrome、Safari、Firefox）

### Q: Twitter 爬取失败或没有推文？

**可能原因**：
- Chrome 浏览器未正确安装
- Twitter 反爬虫限制
- 网络连接问题
- 账号用户名错误

**解决方法**：
1. 检查 Actions 日志中的详细错误信息
2. 确认 `TWITTER_ENABLED` 设置为 `true`
3. 部分账号超时是正常现象，不影响其他账号
4. 检查账号用户名是否正确（不含 @ 符号）
5. 如果大部分账号都失败，可暂时禁用 Twitter 功能

### Q: Twitter 功能拖慢整体运行时间？

**可能原因**：
- Twitter 账号配置过多
- 部分账号响应慢或被限制

**解决方法**：
1. 减少 Twitter 账号数量（只保留最关注的账号）
2. 调整 `tweets_per_user` 参数（从 2 改为 1）
3. 如果不需要 Twitter 功能，直接禁用（删除 TWITTER_ENABLED Secret）

### Q: Twitter 推文分析不准确？

**可能原因**：
- 推文内容与研究方向不相关
- AI 模型分析偏差

**解决方法**：
1. 优化 `research_prompt` 描述，更明确研究方向
2. 调整关注的 Twitter 账号，选择更相关的学术账号
3. 检查报告中的推文是否确实不相关

---

## 🔒 安全建议

1. ✅ 使用 GitHub Secrets 存储敏感信息，不要硬编码在代码中
2. ✅ 定期更新 API 密钥和邮箱授权码
3. ✅ 为私有仓库启用分支保护，防止意外修改
4. ✅ 定期检查 Actions 运行日志，确保没有异常活动
5. ✅ 监控 OpenAI API 使用情况，防止意外超额消费
6. ✅ 不要在公共仓库中提交包含密钥的配置文件

---

## 📖 配置示例

### 完整的 Secrets 配置示例

#### 基础配置（必需）
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
EMAIL_SENDER=your_email@163.com
EMAIL_PASSWORD=ABCD1234EFGH5678
EMAIL_RECEIVER=receiver@gmail.com
```

#### 完整配置（包含可选项）
```
# API 配置
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
API_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o

# 邮件配置
EMAIL_SENDER=your_email@163.com
EMAIL_PASSWORD=ABCD1234EFGH5678
EMAIL_RECEIVER=receiver@gmail.com
EMAIL_SMTP_SERVER=smtp.163.com
EMAIL_SMTP_PORT=465

# Twitter 配置（可选）
TWITTER_ENABLED=true
```

---

## 🆘 需要帮助？

如有问题，请：
1. 查看 Actions 运行日志
2. 查阅本文档的故障排查部分
3. 在 [GitHub Issues](../../issues) 中提问
4. 查看 [OpenAI API 文档](https://platform.openai.com/docs)

---

## 📚 相关文档

- [项目 README](README.md)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
