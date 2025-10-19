#!/usr/bin/env python3
"""
Twitter关注列表导入工具

使用方法：
1. 打开 https://x.com/你的用户名/following
2. 滚动页面加载所有关注的用户
3. 在浏览器控制台运行以下JavaScript代码复制用户名：

   // 复制以下代码到浏览器控制台（F12）
   let usernames = [];
   document.querySelectorAll('[data-testid="UserCell"] a[href^="/"]').forEach(a => {
       let username = a.getAttribute('href').split('/')[1];
       if (username && !usernames.includes(username)) {
           usernames.push(username);
       }
   });
   console.log(usernames.join('\n'));
   copy(usernames.join('\n'));  // 自动复制到剪贴板

4. 将复制的用户名粘贴到下方提示

或者手动创建一个文本文件，每行一个用户名，然后运行：
   python tools/update_twitter_following.py --file usernames.txt
"""

import sys
import os
import yaml
import argparse

def update_config_with_usernames(usernames: list, config_path: str = 'config.yaml'):
    """
    更新配置文件中的following_usernames

    Args:
        usernames: 用户名列表
        config_path: 配置文件路径
    """
    # 读取配置文件
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析YAML
    config = yaml.safe_load(content)

    # 更新following_usernames
    if 'sources' in config and 'twitter' in config['sources']:
        config['sources']['twitter']['following_usernames'] = usernames
    else:
        print("⚠️  配置文件结构不正确，请检查config.yaml")
        return False

    # 写回配置文件
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    print(f"✅ 已更新 {len(usernames)} 个用户到配置文件")
    print(f"📝 配置文件: {config_path}")
    print(f"\n前10个用户:")
    for i, username in enumerate(usernames[:10], 1):
        print(f"  {i}. @{username}")
    if len(usernames) > 10:
        print(f"  ... 还有 {len(usernames) - 10} 个")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='导入Twitter关注列表到配置文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--file', '-f', help='从文件读取用户名列表（每行一个）')
    parser.add_argument('--config', '-c', default='config.yaml', help='配置文件路径')

    args = parser.parse_args()

    usernames = []

    if args.file:
        # 从文件读取
        if not os.path.exists(args.file):
            print(f"❌ 文件不存在: {args.file}")
            return

        with open(args.file, 'r', encoding='utf-8') as f:
            usernames = [line.strip().lstrip('@') for line in f if line.strip()]

        print(f"从文件读取了 {len(usernames)} 个用户名")
    else:
        # 交互式输入
        print("=" * 60)
        print("Twitter关注列表导入工具")
        print("=" * 60)
        print("\n请输入用户名列表（每行一个，输入空行结束）:")
        print("提示: 可以从浏览器控制台复制粘贴\n")

        while True:
            line = input().strip()
            if not line:
                break
            # 移除@符号
            username = line.lstrip('@')
            if username and username not in usernames:
                usernames.append(username)

        if not usernames:
            print("\n❌ 未输入任何用户名")
            return

    # 更新配置文件
    print(f"\n准备更新配置文件...")
    success = update_config_with_usernames(usernames, args.config)

    if success:
        print(f"\n✨ 完成！现在可以运行 python main.py 获取这些用户的推文")


if __name__ == '__main__':
    main()
