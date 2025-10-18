# ArXiv Agent - GitHub Actions 自动化部署指南

本文档介绍如何将 ArXiv Agent 部署到 GitHub Actions，实现每天自动搜索和分析论文，并通过邮件发送报告。

## 📋 部署概览

- **运行平台**: GitHub Actions
- **运行时间**: 每天早上8点（北京时间）
- **费用**: 完全免费（在GitHub免费额度内）
- **通知方式**: 邮件发送报告

---

## 🚀 快速开始

### 第1步：准备 GitHub 仓库

1. 确保代码已推送到 GitHub 仓库
2. 确保 `.gitignore` 已包含 `config.yaml`（防止敏感信息泄露）

### 第2步：设置 GitHub Secrets

在 GitHub 仓库中设置以下 Secrets（用于存储敏感信息）：

**操作步骤：**
1. 打开你的 GitHub 仓库
2. 点击 **Settings**（设置）
3. 左侧菜单选择 **Secrets and variables** → **Actions**
4. 点击 **New repository secret**
5. 依次添加以下 Secrets：

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `ANTHROPIC_API_KEY` | Claude API密钥 | `sk-ant-...` 或代理服务的key |
| `EMAIL_SENDER` | 发件人邮箱 | `your_email@163.com` |
| `EMAIL_PASSWORD` | 邮箱授权码 | `ABCDEFGHIJKLMNOP` |
| `EMAIL_RECEIVER` | 收件人邮箱 | `receiver@gmail.com` |

**⚠️ 重要提示：**
- `EMAIL_PASSWORD` 是邮箱的**授权码**，不是登录密码！
- 如何获取授权码：
  - **163邮箱**：设置 → POP3/SMTP/IMAP → 开启SMTP服务 → 生成授权码
  - **QQ邮箱**：设置 → 账户 → POP3/IMAP/SMTP → 生成授权码
  - **Gmail**：账户设置 → 应用专用密码

### 第3步：修改配置模板（可选）

编辑 `config.yaml.example`，修改以下内容：

```yaml
# 修改研究方向
research_interests:
  - 你的研究方向1
  - 你的研究方向2

# 修改搜索类别
arxiv_categories:
  - cs.AI
  - cs.LG

# 修改邮箱服务器配置（如果使用其他邮箱）
email:
    smtp_server: smtp.163.com  # 根据你的邮箱修改
    smtp_port: 465
    use_ssl: true
```

### 第4步：触发首次运行

**方式1：手动触发（推荐，用于测试）**
1. 打开 GitHub 仓库
2. 点击 **Actions** 标签
3. 左侧选择 **Daily ArXiv Paper Analysis**
4. 点击右侧 **Run workflow** 按钮
5. 点击 **Run workflow** 确认

**方式2：等待定时触发**
- 工作流会在每天早上8点（北京时间）自动运行

### 第5步：查看运行结果

1. **查看运行日志**
   - GitHub仓库 → Actions → 选择最新的运行记录
   - 查看每个步骤的详细日志

2. **查看生成的报告**
   - 在运行记录页面，向下滚动到 **Artifacts** 部分
   - 下载 `arxiv-report-xxx` 文件
   - 解压查看 Markdown 格式的报告

3. **查看邮件**
   - 检查收件箱（可能在垃圾邮件中）
   - 邮件包含统计信息和报告附件

---

## ⚙️ 高级配置

### 修改运行时间

编辑 `.github/workflows/daily-arxiv.yml`：

```yaml
on:
  schedule:
    # Cron 表达式：分 时 日 月 周
    - cron: '0 0 * * *'  # 每天 UTC 0:00 = 北京时间 8:00
```

**常用时间示例：**
- 每天早上8点（北京）：`'0 0 * * *'`（UTC 0:00）
- 每天晚上8点（北京）：`'0 12 * * *'`（UTC 12:00）
- 每天中午12点（北京）：`'0 4 * * *'`（UTC 4:00）
- 每周一早上8点：`'0 0 * * 1'`

**在线Cron表达式生成器**: https://crontab.guru/

### 修改搜索参数

编辑 `config.yaml.example`：

```yaml
# 搜索天数
days_back: 3  # 搜索最近3天的论文

# 每个类别的论文数量
max_results: 100  # 每个类别获取100篇

# 相关性阈值
min_relevance: high  # 只保留高相关的论文
```

### 禁用邮件通知

如果不需要邮件，在 `config.yaml.example` 中设置：

```yaml
email:
    enabled: false
```

---

## 🐛 故障排查

### 问题1：工作流运行失败

**可能原因：**
- GitHub Secrets 未正确设置
- API密钥无效或额度不足

**解决方案：**
1. 检查 Actions 运行日志，查看具体错误
2. 验证所有 Secrets 都已正确添加
3. 测试 API 密钥是否有效

### 问题2：没有收到邮件

**可能原因：**
- 邮箱配置错误
- 邮件在垃圾邮件中
- 邮箱授权码过期

**解决方案：**
1. 检查 `EMAIL_SENDER`、`EMAIL_PASSWORD`、`EMAIL_RECEIVER` 是否正确
2. 确认使用的是授权码，不是登录密码
3. 查看 Actions 日志中的邮件发送部分
4. 检查垃圾邮件文件夹

### 问题3：找不到相关论文

**可能原因：**
- 研究方向与arxiv论文不匹配
- 相关性阈值设置过高

**解决方案：**
1. 修改 `research_interests`，使用更通用的关键词
2. 降低 `min_relevance` 阈值（改为 `medium` 或 `low`）
3. 增加 `days_back` 搜索更多天的论文

---

## 📊 监控和维护

### 查看运行历史

GitHub仓库 → Actions → 选择工作流 → 查看所有运行记录

### 暂停自动运行

如果需要暂时停止定时运行：

1. GitHub仓库 → Actions
2. 左侧选择 **Daily ArXiv Paper Analysis**
3. 点击右上角 **...** → **Disable workflow**

恢复：点击 **Enable workflow**

### 报告保存时间

- GitHub Actions Artifacts 默认保存 **30天**
- 可以在工作流文件中修改 `retention-days` 参数

---

## 🔐 安全注意事项

1. ✅ **不要**将 `config.yaml` 提交到 GitHub（已在 `.gitignore` 中）
2. ✅ **使用** GitHub Secrets 存储所有敏感信息
3. ✅ **使用**邮箱授权码，不要使用登录密码
4. ✅ **定期**更换 API 密钥和邮箱授权码
5. ✅ **不要**在代码中硬编码任何密钥

---

## 📞 获取帮助

如果遇到问题：

1. 查看 [GitHub Actions 文档](https://docs.github.com/actions)
2. 检查项目的 Issues 页面
3. 查看 Actions 运行日志中的详细错误信息

---

## ✨ 下一步

部署完成后，你可以：

- ✅ 每天早上收到最新的论文分析报告
- ✅ 在 GitHub Actions 中查看历史报告
- ✅ 根据需要调整搜索参数和时间
- ✅ 添加更多研究方向

祝你使用愉快！🎉
