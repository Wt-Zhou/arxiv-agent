"""
Twitter RSS获取模块（基于Nitter）
完全免费，无需API，无需爬虫
"""
import feedparser
import requests
from typing import List, Dict
from datetime import datetime, timedelta
import time


class TwitterRSSFetcher:
    """使用Nitter RSS获取Twitter内容（最稳定的免费方案）"""

    # Nitter公共实例列表（如果一个失败会自动尝试下一个）
    NITTER_INSTANCES = [
        'https://nitter.net',
        'https://nitter.privacydev.net',
        'https://nitter.poast.org',
        'https://nitter.1d4.us',
    ]

    def __init__(self, timeout: int = 10):
        """
        初始化Twitter RSS获取器

        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.working_instance = None

    def _find_working_instance(self) -> str:
        """找到一个可用的Nitter实例"""
        if self.working_instance:
            return self.working_instance

        print("  🔍 寻找可用的Nitter实例...")
        for instance in self.NITTER_INSTANCES:
            try:
                response = requests.get(f"{instance}/elonmusk/rss", timeout=5)
                if response.status_code == 200:
                    self.working_instance = instance
                    print(f"  ✅ 使用实例: {instance}")
                    return instance
            except:
                continue

        raise Exception("所有Nitter实例都不可用，请稍后重试")

    def get_user_tweets(self, username: str, max_results: int = 10, days_back: int = 7) -> List[Dict]:
        """
        获取指定用户的最近推文

        Args:
            username: Twitter用户名（不含@）
            max_results: 最多获取多少条
            days_back: 获取最近几天的推文

        Returns:
            推文列表
        """
        try:
            instance = self._find_working_instance()
            rss_url = f"{instance}/{username}/rss"

            # 获取RSS feed
            feed = feedparser.parse(rss_url)

            if not feed.entries:
                return []

            # 计算时间范围
            cutoff_date = datetime.now() - timedelta(days=days_back)

            # 解析推文
            tweets = []
            for entry in feed.entries[:max_results]:
                # 解析发布时间
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])

                # 过滤时间范围
                if pub_date and pub_date < cutoff_date:
                    continue

                # 提取推文内容
                text = entry.get('title', '') or entry.get('summary', '')
                # 清理HTML标签
                if text:
                    import re
                    text = re.sub(r'<[^>]+>', '', text)
                    text = re.sub(r'https?://\S+', '', text)  # 移除链接
                    text = text.strip()

                if not text:
                    continue

                tweets.append({
                    'id': entry.get('id', ''),
                    'text': text,
                    'created_at': pub_date.strftime('%Y-%m-%d %H:%M:%S') if pub_date else '',
                    'url': entry.get('link', ''),
                    'author_username': username,
                    'author_name': username,
                    'favorite_count': 0,  # RSS不提供
                    'retweet_count': 0,   # RSS不提供
                    'reply_count': 0,     # RSS不提供
                    'source_type': 'nitter_rss'
                })

            return tweets

        except Exception as e:
            print(f"  ❌ 获取 @{username} 失败: {e}")
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
        print(f"\n📱 正在从 {len(usernames)} 个 Twitter 账号获取推文（RSS）...")
        print(f"每个账号获取最多 {tweets_per_user} 条推文（最近{days_back}天）\n")

        all_tweets = []
        for i, username in enumerate(usernames, 1):
            print(f"  [{i}/{len(usernames)}] 📥 @{username}...", end=' ')
            tweets = self.get_user_tweets(username, tweets_per_user, days_back)

            if tweets:
                all_tweets.extend(tweets)
                print(f"✅ {len(tweets)}条")
            else:
                print("❌")

            # 避免请求过快
            if i < len(usernames):
                time.sleep(1)

        print(f"\n✅ 总共获取 {len(all_tweets)} 条推文")
        return all_tweets


# 推荐的学术Twitter账号
RECOMMENDED_ACCOUNTS = {
    'ai_research': [
        '_akhaliq',       # AI Papers Daily（每日AI论文更新，强烈推荐）
        'labmlai',        # LabML.ai（ML论文解析）
        'paperswithcode', # Papers with Code
    ],
    'researchers': [
        'karpathy',       # Andrej Karpathy（前Tesla AI主管）
        'hardmaru',       # David Ha（VLM、生成模型）
        'ylecun',         # Yann LeCun（深度学习先驱）
        'goodfellow_ian', # Ian Goodfellow（GAN发明者）
    ],
    'autonomous_driving': [
        'DrJimFan',       # Jim Fan（NVIDIA，具身智能）
        'Comma_ai',       # Comma.ai（开源自动驾驶）
    ],
    'embodied_ai': [
        'hausman_k',      # Karol Hausman（Google，机器人）
        'chelseabfinn',   # Chelsea Finn（Stanford，元学习）
    ]
}


if __name__ == '__main__':
    # 测试代码
    fetcher = TwitterRSSFetcher()

    # 测试获取单个用户
    print("=" * 60)
    print("测试Twitter RSS获取功能")
    print("=" * 60)

    test_users = ['_akhaliq', 'karpathy']
    tweets = fetcher.get_tweets_from_list(test_users, tweets_per_user=3, days_back=1)

    if tweets:
        print(f"\n📝 示例推文：")
        for i, tweet in enumerate(tweets[:5], 1):
            print(f"\n{i}. @{tweet['author_username']}")
            print(f"   时间: {tweet['created_at']}")
            print(f"   内容: {tweet['text'][:150]}...")
            print(f"   链接: {tweet['url']}")
    else:
        print("\n⚠️  未获取到推文，可能Nitter实例暂时不可用")
