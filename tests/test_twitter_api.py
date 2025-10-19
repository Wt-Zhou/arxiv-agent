#!/usr/bin/env python3
"""
测试 Twitter API v2 免费版功能
"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config_loader import ConfigLoader
from twitter_api_v2_fetcher import TwitterAPIv2Fetcher


def test_twitter_api_v2():
    """测试 Twitter API v2"""
    print("=" * 60)
    print("测试：Twitter API v2 免费版")
    print("=" * 60)

    # 加载配置
    config = ConfigLoader('config.yaml')
    twitter_config = config.get_twitter_config()

    # 获取 Bearer Token
    bearer_token = twitter_config.get('bearer_token') or os.getenv('TWITTER_BEARER_TOKEN')

    if not bearer_token:
        print("\n❌ 未配置 Twitter Bearer Token")
        print("\n请按照 TWITTER_FREE_GUIDE.md 中的步骤：")
        print("1. 访问 https://developer.x.com/en/portal/dashboard")
        print("2. 申请免费开发者账号（5分钟）")
        print("3. 获取 Bearer Token")
        print("4. 配置到 config.yaml 或 .env 文件")
        print("\n注意：完全免费！每月 10,000 条推文额度")
        return

    print(f"\n✅ 已配置 Bearer Token: {bearer_token[:20]}...")

    # 创建获取器
    fetcher = TwitterAPIv2Fetcher(bearer_token=bearer_token)

    # 测试1：获取指定用户的推文
    print("\n" + "=" * 60)
    print("测试 1: 获取指定用户的推文")
    print("=" * 60)

    test_users = ['ylecun', 'karpathy', '_akhaliq']  # 知名AI研究者

    print(f"\n测试获取 @{test_users[0]} 的最近推文...")
    tweets = fetcher.get_user_tweets(
        username=test_users[0],
        max_results=5,
        days_back=7
    )

    if tweets:
        print(f"\n找到 {len(tweets)} 条推文:")
        for i, tweet in enumerate(tweets[:3], 1):
            print(f"\n{i}. {tweet['text'][:150]}...")
            print(f"   时间: {tweet['created_at']}")
            print(f"   互动: 👍{tweet['favorite_count']} 🔄{tweet['retweet_count']}")
            print(f"   链接: {tweet['url']}")

    # 测试2：从多个用户获取推文
    print("\n" + "=" * 60)
    print("测试 2: 从多个用户获取推文")
    print("=" * 60)

    all_tweets = fetcher.get_tweets_from_list(
        usernames=test_users[:2],  # 只测试前2个
        tweets_per_user=3,
        days_back=7
    )

    if all_tweets:
        print(f"\n最新的3条推文:")
        for i, tweet in enumerate(all_tweets[:3], 1):
            print(f"\n{i}. [@{tweet['author_username']}] {tweet['text'][:100]}...")

    # 测试3：搜索相关推文
    print("\n" + "=" * 60)
    print("测试 3: 搜索相关推文")
    print("=" * 60)

    search_tweets = fetcher.search_recent_tweets(
        query='"autonomous driving" OR "self-driving" AI',
        max_results=10,
        days_back=7
    )

    if search_tweets:
        print(f"\n找到 {len(search_tweets)} 条相关推文")
        for i, tweet in enumerate(search_tweets[:3], 1):
            print(f"\n{i}. [@{tweet['author_username']}] {tweet['text'][:120]}...")

    # 测试4：根据研究兴趣搜索
    print("\n" + "=" * 60)
    print("测试 4: 根据研究兴趣搜索")
    print("=" * 60)

    research_interests = config.get_research_interests()
    interest_tweets = fetcher.search_by_research_interests(
        research_interests=research_interests[:3],  # 前3个关键词
        max_results=15,
        days_back=7
    )

    if interest_tweets:
        print(f"\n找到 {len(interest_tweets)} 条相关推文")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

    total_fetched = len(tweets) + len(all_tweets) + len(search_tweets) + len(interest_tweets)
    print(f"\n本次测试共获取 {total_fetched} 条推文")
    print(f"免费额度剩余：约 {10000 - total_fetched} 条/月")

    print("\n如果测试成功，可以在 config.yaml 中：")
    print("1. 设置 twitter.enabled: true")
    print("2. 设置 sources.twitter.enabled: true")
    print("3. 配置 twitter.following_usernames 列表")


if __name__ == '__main__':
    test_twitter_api_v2()
