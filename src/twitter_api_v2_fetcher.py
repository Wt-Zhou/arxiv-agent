"""
基于 Twitter API v2 的推文获取模块（免费版）
使用官方 API，每月 10,000 条推文免费额度
"""
import tweepy
from typing import List, Dict
from datetime import datetime, timedelta


class TwitterAPIv2Fetcher:
    """使用 Twitter API v2 获取推文（免费版）"""

    def __init__(self, bearer_token: str):
        """
        初始化 Twitter API v2 客户端

        Args:
            bearer_token: Twitter API Bearer Token
        """
        self.client = tweepy.Client(bearer_token=bearer_token)

    def get_user_tweets(self, username: str, max_results: int = 10, days_back: int = 7) -> List[Dict]:
        """
        获取指定用户的最近推文

        Args:
            username: Twitter 用户名（不含@）
            max_results: 最多获取多少条（最大100）
            days_back: 获取最近几天的推文

        Returns:
            推文列表
        """
        try:
            # 获取用户信息
            user = self.client.get_user(username=username, user_fields=['public_metrics'])

            if not user.data:
                print(f"  ⚠️  未找到用户: @{username}")
                return []

            user_id = user.data.id
            user_data = user.data

            # 计算时间范围
            start_time = datetime.utcnow() - timedelta(days=days_back)

            # 获取推文（API要求max_results最小为5）
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=max(5, min(max_results, 100)),  # API限制：最小5，最大100
                start_time=start_time,
                tweet_fields=['created_at', 'public_metrics', 'entities'],
                exclude=['retweets', 'replies']  # 排除转推和回复
            )

            if not tweets.data:
                return []

            # 转换为标准格式
            result = []
            for tweet in tweets.data:
                result.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S') if tweet.created_at else '',
                    'url': f"https://twitter.com/{username}/status/{tweet.id}",
                    'author_username': username,
                    'author_name': user_data.name,
                    'author_followers': user_data.public_metrics['followers_count'],
                    'favorite_count': tweet.public_metrics['like_count'] if tweet.public_metrics else 0,
                    'retweet_count': tweet.public_metrics['retweet_count'] if tweet.public_metrics else 0,
                    'reply_count': tweet.public_metrics['reply_count'] if tweet.public_metrics else 0,
                    'source_type': 'twitter_api_v2'
                })

            return result

        except tweepy.errors.TweepyException as e:
            print(f"  ❌ 获取 @{username} 的推文失败: {e}")
            return []

    def get_tweets_from_list(self, usernames: List[str], tweets_per_user: int = 5,
                            days_back: int = 7) -> List[Dict]:
        """
        从多个用户获取推文

        Args:
            usernames: 用户名列表
            tweets_per_user: 每个用户获取的推文数
            days_back: 获取最近几天的推文

        Returns:
            所有推文列表
        """
        print(f"\n正在从 {len(usernames)} 个 Twitter 账号获取推文...")
        print(f"每个账号获取最多 {tweets_per_user} 条推文\n")

        all_tweets = []

        for i, username in enumerate(usernames, 1):
            print(f"  [{i}/{len(usernames)}] 获取 @{username}...")

            tweets = self.get_user_tweets(
                username=username,
                max_results=tweets_per_user,
                days_back=days_back
            )

            all_tweets.extend(tweets)
            print(f"    ✓ 找到 {len(tweets)} 条推文")

        # 按时间降序排序
        all_tweets.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        print(f"\n✅ 共获取 {len(all_tweets)} 条推文")
        return all_tweets

    def search_recent_tweets(self, query: str, max_results: int = 50, days_back: int = 7) -> List[Dict]:
        """
        搜索最近的推文

        Args:
            query: 搜索查询（支持Twitter搜索语法）
            max_results: 最多返回多少条（最大100）
            days_back: 搜索最近几天的推文

        Returns:
            推文列表
        """
        print(f"\n正在搜索推文: {query}")

        try:
            # 计算时间范围
            start_time = datetime.utcnow() - timedelta(days=days_back)

            # 搜索推文
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                start_time=start_time,
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                expansions=['author_id'],
                user_fields=['username', 'name', 'public_metrics']
            )

            if not tweets.data:
                print("  未找到相关推文")
                return []

            # 构建用户信息字典
            users = {user.id: user for user in tweets.includes['users']} if tweets.includes and 'users' in tweets.includes else {}

            # 转换为标准格式
            result = []
            for tweet in tweets.data:
                user = users.get(tweet.author_id)

                result.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S') if tweet.created_at else '',
                    'url': f"https://twitter.com/i/status/{tweet.id}",
                    'author_username': user.username if user else '',
                    'author_name': user.name if user else '',
                    'author_followers': user.public_metrics['followers_count'] if user and user.public_metrics else 0,
                    'favorite_count': tweet.public_metrics['like_count'] if tweet.public_metrics else 0,
                    'retweet_count': tweet.public_metrics['retweet_count'] if tweet.public_metrics else 0,
                    'reply_count': tweet.public_metrics['reply_count'] if tweet.public_metrics else 0,
                    'source_type': 'twitter_api_v2'
                })

            print(f"✅ 找到 {len(result)} 条推文")
            return result

        except tweepy.errors.TweepyException as e:
            print(f"❌ 搜索失败: {e}")
            return []

    def search_by_research_interests(self, research_interests: List[str],
                                     max_results: int = 50, days_back: int = 7) -> List[Dict]:
        """
        根据研究兴趣搜索推文

        Args:
            research_interests: 研究方向关键词列表
            max_results: 最多返回多少条
            days_back: 搜索最近几天

        Returns:
            推文列表
        """
        # 构建搜索查询（使用 OR 连接关键词）
        query = ' OR '.join([f'"{interest}"' for interest in research_interests[:10]])  # 限制关键词数量

        # 添加语言过滤（可选）
        query += ' lang:en'  # 只搜索英文推文

        return self.search_recent_tweets(query, max_results, days_back)

    def get_following_list(self, username: str, max_results: int = 100) -> List[str]:
        """
        获取指定用户的关注列表

        Args:
            username: Twitter用户名（不含@）
            max_results: 最多获取多少个关注（默认100）

        Returns:
            关注的用户名列表
        """
        try:
            print(f"\n正在获取 @{username} 的关注列表...")

            # 获取用户信息
            user = self.client.get_user(username=username)
            if not user.data:
                print(f"  ⚠️  未找到用户: @{username}")
                return []

            user_id = user.data.id

            # 获取关注列表
            following = self.client.get_users_following(
                id=user_id,
                max_results=min(max_results, 1000),  # API最大支持1000
                user_fields=['username', 'name', 'description', 'public_metrics']
            )

            if not following.data:
                print("  未找到关注的用户")
                return []

            # 提取用户名
            usernames = [user.username for user in following.data]

            print(f"✅ 找到 {len(usernames)} 个关注的用户")
            return usernames

        except tweepy.errors.TweepyException as e:
            print(f"❌ 获取关注列表失败: {e}")
            return []

    def get_tweets_from_my_following(self, my_username: str, tweets_per_user: int = 5,
                                     days_back: int = 7, max_users: int = 50) -> List[Dict]:
        """
        从您关注的人获取推文

        Args:
            my_username: 您的Twitter用户名（不含@）
            tweets_per_user: 每个用户获取的推文数
            days_back: 获取最近几天的推文
            max_users: 最多从多少个关注用户获取（避免超额度）

        Returns:
            所有推文列表
        """
        # 获取关注列表
        following = self.get_following_list(my_username, max_results=max_users)

        if not following:
            print("未找到关注的用户")
            return []

        # 从关注列表获取推文
        return self.get_tweets_from_list(
            usernames=following,
            tweets_per_user=tweets_per_user,
            days_back=days_back
        )
