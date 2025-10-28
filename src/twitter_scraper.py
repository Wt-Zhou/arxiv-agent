"""
Twitter免费爬虫模块（基于snscrape）
无需API密钥，完全免费
"""
import subprocess
import json
from typing import List, Dict
from datetime import datetime, timedelta


class TwitterScraper:
    """使用snscrape爬取Twitter内容（无需API）"""

    def __init__(self):
        """初始化Twitter爬虫"""
        self.check_snscrape_installed()

    def check_snscrape_installed(self):
        """检查snscrape是否已安装"""
        try:
            subprocess.run(['snscrape', '--version'],
                         capture_output=True,
                         check=True,
                         timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("\n⚠️  snscrape未安装，正在安装...")
            print("运行：pip install snscrape")
            raise ImportError("请先安装snscrape: pip install snscrape")

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
            # 计算日期范围
            since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

            # 构建snscrape命令
            # 使用TwitterUserScraper获取用户推文
            cmd = [
                'snscrape',
                '--jsonl',  # 输出JSON Lines格式
                '--max-results', str(max_results),
                '--since', since_date,
                f'twitter-user:{username}'
            ]

            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )

            # 解析JSON Lines输出
            tweets = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    tweet_data = json.loads(line)
                    tweets.append({
                        'id': tweet_data.get('id', ''),
                        'text': tweet_data.get('content', ''),
                        'created_at': tweet_data.get('date', ''),
                        'url': tweet_data.get('url', ''),
                        'author_username': username,
                        'author_name': tweet_data.get('user', {}).get('displayname', username),
                        'favorite_count': tweet_data.get('likeCount', 0),
                        'retweet_count': tweet_data.get('retweetCount', 0),
                        'reply_count': tweet_data.get('replyCount', 0),
                        'source_type': 'snscrape'
                    })
                except json.JSONDecodeError:
                    continue

            return tweets

        except subprocess.TimeoutExpired:
            print(f"  ⚠️  获取 @{username} 超时")
            return []
        except subprocess.CalledProcessError as e:
            print(f"  ❌ 获取 @{username} 失败: {e.stderr}")
            return []
        except Exception as e:
            print(f"  ❌ 意外错误: {str(e)}")
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
        print(f"\n📱 正在从 {len(usernames)} 个 Twitter 账号爬取推文...")
        print(f"每个账号获取最多 {tweets_per_user} 条推文（最近{days_back}天）\n")

        all_tweets = []
        for username in usernames:
            print(f"  📥 抓取 @{username}...", end=' ')
            tweets = self.get_user_tweets(username, tweets_per_user, days_back)

            if tweets:
                all_tweets.extend(tweets)
                print(f"✅ 获取 {len(tweets)} 条")
            else:
                print("❌ 失败")

        print(f"\n✅ 总共获取 {len(all_tweets)} 条推文")
        return all_tweets


# 推荐的学术Twitter账号
RECOMMENDED_ACCOUNTS = {
    'ai_research': [
        '_akhaliq',       # AI Papers Daily（每日AI论文更新）
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
    scraper = TwitterScraper()

    # 测试获取单个用户
    test_users = ['_akhaliq', 'karpathy']
    tweets = scraper.get_tweets_from_list(test_users, tweets_per_user=3, days_back=3)

    if tweets:
        print(f"\n示例推文：")
        for i, tweet in enumerate(tweets[:3], 1):
            print(f"\n{i}. @{tweet['author_username']}: {tweet['text'][:100]}...")
            print(f"   ❤️  {tweet['favorite_count']} | 🔄 {tweet['retweet_count']}")
