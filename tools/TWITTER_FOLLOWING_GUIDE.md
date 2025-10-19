# Twitter关注列表导入指南

由于Twitter API v2 Free tier不支持直接获取用户关注列表，这里提供两种方法导入您的Twitter关注列表。

---

## 方法1：浏览器控制台快速导入（推荐）⚡

### 步骤1：打开您的关注列表页面
访问：https://x.com/Weitao39385450/following

### 步骤2：滚动加载所有关注用户
向下滚动页面，直到加载完所有您关注的用户

### 步骤3：打开浏览器控制台
按 `F12` 或 `Ctrl+Shift+J` (Windows) / `Cmd+Option+J` (Mac)

### 步骤4：运行以下JavaScript代码

复制以下代码，粘贴到控制台，按回车：

```javascript
// 提取所有关注的用户名
let usernames = [];
document.querySelectorAll('[data-testid="UserCell"] a[href^="/"]').forEach(a => {
    let username = a.getAttribute('href').split('/')[1];
    if (username && !usernames.includes(username) && !username.includes('/')) {
        usernames.push(username);
    }
});

// 显示结果
console.log('找到 ' + usernames.length + ' 个关注用户:');
console.log(usernames.join('\n'));

// 自动复制到剪贴板
copy(usernames.join('\n'));
console.log('\n✅ 已复制到剪贴板！');
```

### 步骤5：运行导入工具

```bash
cd /home/zwt/code/arxiv-agent
source /home/zwt/anaconda3/etc/profile.d/conda.sh
conda activate arxiv-agent
python tools/update_twitter_following.py
```

然后粘贴刚才复制的用户名列表（Ctrl+V），输入完成后按回车确认，再输入一个空行结束。

---

## 方法2：从文件导入

### 步骤1：创建用户名文件
创建一个文本文件 `my_following.txt`，每行一个用户名：

```
ylecun
karpathy
_akhaliq
stanislavfort
...
```

### 步骤2：运行导入命令

```bash
python tools/update_twitter_following.py --file my_following.txt
```

---

## 验证导入结果

导入成功后，检查 `config.yaml` 文件：

```yaml
sources:
  twitter:
    following_usernames:
      - ylecun
      - karpathy
      - _akhaliq
      - ...
```

---

## 运行程序

```bash
python main.py
```

程序会自动从您导入的用户列表获取推文！

---

## 常见问题

### Q: 为什么不能直接用API获取关注列表？
A: Twitter API v2 Free tier只支持App-only认证，获取关注列表需要OAuth 2.0用户认证（需要申请Elevated access）。

### Q: 如何添加更多用户？
A: 重新运行导入工具，或直接编辑 `config.yaml` 文件。

### Q: 导入的用户会被覆盖吗？
A: 是的，每次运行导入工具会覆盖之前的列表。如果只想添加几个用户，建议直接编辑 `config.yaml`。

---

## 升级到完全自动化（可选）

如果您想实现完全自动获取关注列表，可以申请Twitter API的**Elevated access**：

1. 访问 https://developer.twitter.com/en/portal/petition/essential/basic-info
2. 填写申请表（说明用途：个人学术论文追踪）
3. 等待审批（通常24小时内）
4. 获得OAuth 2.0权限

获得Elevated access后，我可以帮您实现OAuth 2.0认证，真正实现自动获取关注列表。
