# GitHub Actions 部署指南

本文档说明如何将 ArXiv Agent 部署到 GitHub Actions，实现每日自动运行并发送邮件报告。

## 功能特性

- ✅ 每天自动运行（UTC 00:00，北京时间 08:00）
- ✅ 支持手动触发，可自定义参数
- ✅ 自动发送 HTML 格式邮件报告
- ✅ 报告文件上传为 Artifacts（保留 30 天）
- ✅ 可选：自动提交报告到 Git 仓库

## 部署步骤

### 1. 准备 GitHub 仓库

确保你的代码已经推送到 GitHub 仓库。

### 2. 配置 GitHub Secrets

在你的 GitHub 仓库中，进入 **Settings** > **Secrets and variables** > **Actions**，添加以下 Secrets：

#### 必需的 Secrets：

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `ANTHROPIC_API_KEY` | Claude API 密钥 | `sk-ant-api03-xxx` 或第三方代理密钥 |
| `EMAIL_SENDER` | 发送邮箱地址 | `your_email@163.com` |
| `EMAIL_PASSWORD` | 邮箱授权码（不是登录密码） | `ABCD1234EFGH5678` |
| `EMAIL_RECEIVER` | 接收邮箱地址 | `receiver@gmail.com` |

#### 可选的 Secrets：

| Secret 名称 | 说明 | 默认值 |
|------------|------|--------|
| `API_BASE_URL` | Claude API 端点（使用代理时） | 留空使用官方 API |
| `EMAIL_SMTP_SERVER` | SMTP 服务器地址 | `smtp.163.com` |
| `EMAIL_SMTP_PORT` | SMTP 服务器端口 | `465` |

### 3. 配置邮箱授权码

#### 163 邮箱：
1. 登录 163 邮箱网页版
2. 进入 **设置** > **POP3/SMTP/IMAP**
3. 开启 **IMAP/SMTP 服务**
4. 获取 **授权码**（不是邮箱登录密码）
5. 将授权码填入 `EMAIL_PASSWORD` Secret

#### QQ 邮箱：
1. 登录 QQ 邮箱网页版
2. 进入 **设置** > **账户**
3. 开启 **POP3/SMTP 服务**
4. 获取 **授权码**
5. SMTP 服务器：`smtp.qq.com`，端口：`465`

#### Gmail：
1. 开启两步验证
2. 生成应用专用密码
3. SMTP 服务器：`smtp.gmail.com`，端口：`465`

### 4. 启用 GitHub Actions

workflow 文件已经创建在 `.github/workflows/daily-arxiv.yml`，推送到 GitHub 后会自动启用。

### 5. 验证配置

#### 方法 1：手动触发测试
1. 进入仓库的 **Actions** 页面
2. 选择 **Daily ArXiv Paper Analysis** workflow
3. 点击 **Run workflow**
4. 可选：修改参数
   - `days_back`: 搜索最近几天的论文（默认 3 天）
   - `max_concurrent`: 最大并发数（默认 5）
5. 点击 **Run workflow** 按钮

#### 方法 2：等待定时运行
workflow 会在每天 UTC 00:00（北京时间 08:00）自动运行。

### 6. 查看运行结果

1. **查看日志**：在 Actions 页面点击对应的运行记录
2. **下载报告**：点击 Artifacts 下载生成的报告文件
3. **接收邮件**：检查接收邮箱是否收到 HTML 格式报告

## 自定义配置

### 修改运行时间

编辑 `.github/workflows/daily-arxiv.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 00:00，北京时间 08:00
  # 改为 UTC 22:00（北京时间 06:00）
  - cron: '0 22 * * *'
```

### 修改研究方向

编辑 `.github/workflows/daily-arxiv.yml` 中的 `research_interests` 和 `research_prompt` 部分。

### 禁用自动提交报告

如果不需要将报告提交到 Git 仓库，可以删除或注释掉最后的 "Commit and push reports" 步骤。

## 故障排查

### 问题 1：邮件发送失败

**可能原因**：
- 邮箱授权码错误
- SMTP 服务器/端口配置错误
- 邮箱未开启 SMTP 服务

**解决方法**：
1. 检查 Secrets 中的邮箱配置是否正确
2. 查看 Actions 运行日志中的错误信息
3. 确认邮箱已开启 SMTP/IMAP 服务

### 问题 2：API 调用失败

**可能原因**：
- API 密钥错误或过期
- API 额度不足
- 网络连接问题

**解决方法**：
1. 检查 `ANTHROPIC_API_KEY` 是否正确
2. 如果使用第三方代理，检查 `API_BASE_URL` 配置
3. 查看 API 余额和使用情况

### 问题 3：找不到论文

**可能原因**：
- ArXiv 分类配置不正确
- 搜索时间范围太短
- 网络问题导致无法访问 ArXiv

**解决方法**：
1. 检查 workflow 中的 `categories` 配置
2. 增加 `days_back` 参数
3. 查看运行日志确认问题

## 成本估算

### API 调用成本（Claude Sonnet 4.5）

假设每天：
- 获取 50 篇 ArXiv 论文 + 5 篇期刊文章 = 55 篇
- 第一阶段筛选：55 / 25 = 3 批次
- 筛选出 10 篇高相关论文
- 第二阶段详细分析：10 / 5 = 2 批次

**Token 使用估算**：
- 输入 Token：约 20K tokens/天
- 输出 Token：约 5K tokens/天

**费用估算**（官方 API）：
- 输入：$3/M tokens × 20K = $0.06/天
- 输出：$15/M tokens × 5K = $0.075/天
- **总计：约 $0.14/天，$4.2/月**

> 注意：使用第三方代理可能有不同的定价。

### GitHub Actions 成本

GitHub Actions 对公共仓库免费，私有仓库每月有 2000 分钟免费额度。
本 workflow 每次运行约 5-10 分钟，每月运行 30 次约 150-300 分钟，在免费额度内。

## 高级配置

### 多个接收邮箱

修改 workflow 中的 `receiver_email` 配置：

```yaml
receiver_email: "email1@gmail.com,email2@outlook.com"
```

### 仅工作日运行

```yaml
schedule:
  # 周一到周五运行
  - cron: '0 0 * * 1-5'
```

### 并行运行多个配置

可以创建多个 workflow 文件，使用不同的研究方向配置。

## 安全建议

1. ✅ 使用 GitHub Secrets 存储敏感信息，不要硬编码在代码中
2. ✅ 定期更新 API 密钥和邮箱授权码
3. ✅ 为私有仓库启用分支保护，防止意外修改
4. ✅ 定期检查 Actions 运行日志，确保没有异常活动

## 支持

如有问题，请：
1. 查看 Actions 运行日志
2. 查阅本文档的故障排查部分
3. 在 GitHub Issues 中提问
