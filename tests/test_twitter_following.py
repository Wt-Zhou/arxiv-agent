#!/usr/bin/env python3
"""
测试Twitter关注列表功能
"""
import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from twitter_api_v2_fetcher import TwitterAPIv2Fetcher
from dotenv import load_dotenv

def test_following_list(username: str, bearer_token: str):
    """测试获取关注列表"""
    print("=" * 60)
    print("测试：获取Twitter关注列表")
    print("=" * 60)

    try:
        fetcher = TwitterAPIv2Fetcher(bearer_token=bearer_token)

        # 测试1：获取关注列表
        print(f"\n测试1: 获取 @{username} 的关注列表...")
        following = fetcher.get_following_list(username, max_results=10)

        if following:
            print(f"\n✅ 成功获取 {len(following)} 个关注用户:")
            for i, user in enumerate(following[:10], 1):
                print(f"  {i}. @{user}")
        else:
            print("❌ 未能获取关注列表")
            return

        # 测试2：从关注列表获取推文（只获取前3个用户）
        print(f"\n测试2: 从前3个关注用户获取推文...")
        test_users = following[:3]
        tweets = fetcher.get_tweets_from_list(
            usernames=test_users,
            tweets_per_user=3,
            days_back=7
        )

        if tweets:
            print(f"\n✅ 成功获取 {len(tweets)} 条推文")
            print("\n示例推文:")
            for i, tweet in enumerate(tweets[:3], 1):
                print(f"\n{i}. @{tweet['author_username']}")
                print(f"   {tweet['text'][:100]}...")
        else:
            print("❌ 未能获取推文")

        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    load_dotenv()

    # 从环境变量或配置获取
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    if not bearer_token:
        print("错误: 请在 .env 文件中设置 TWITTER_BEARER_TOKEN")
        print("或在 config.yaml 中配置 bearer_token")
        sys.exit(1)

    # 测试用户名（可以改成任何公开的Twitter账号）
    test_username = input("请输入要测试的Twitter用户名（不含@）: ").strip()

    if not test_username:
        print("未输入用户名，使用默认测试账号: ylecun")
        test_username = "ylecun"

    test_following_list(test_username, bearer_token)
