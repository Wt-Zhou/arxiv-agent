"""
Twitter Selenium爬虫（无需API）
使用浏览器自动化技术爬取推文
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from typing import List, Dict
from datetime import datetime, timedelta
import time
import re


class TwitterSeleniumScraper:
    """使用Selenium爬取Twitter（无需登录，公开推文）"""

    def __init__(self, headless: bool = True):
        """
        初始化Selenium爬虫

        Args:
            headless: 是否使用无头模式（不显示浏览器窗口）
        """
        self.headless = headless
        self.driver = None

    def _init_driver(self):
        """初始化Chrome浏览器"""
        if self.driver:
            return

        options = Options()
        if self.headless:
            options.add_argument('--headless=new')  # 新版headless模式
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        # 禁用图片加载以提速
        prefs = {'profile.managed_default_content_settings.images': 2}
        options.add_experimental_option('prefs', prefs)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        try:
            # 使用webdriver_manager自动下载和管理chromedriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(60)  # 增加到60秒
            self.driver.set_script_timeout(60)  # 脚本执行超时
        except Exception as e:
            raise Exception(f"Chrome驱动初始化失败: {e}\n请确保已安装Chrome浏览器")

    def _close_driver(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

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
            self._init_driver()

            # 访问用户主页（带重试）
            url = f'https://twitter.com/{username}'
            max_retries = 2
            for retry in range(max_retries):
                try:
                    self.driver.get(url)
                    # 等待页面加载
                    time.sleep(5)
                    break
                except Exception as e:
                    if retry < max_retries - 1:
                        print(f"  ⚠️  页面加载失败，重试中...")
                        time.sleep(3)
                    else:
                        raise e

            # 检查是否需要登录（如果看到登录提示说明账号是私密的）
            if "login" in self.driver.current_url.lower():
                print(f"  ⚠️  @{username} 需要登录才能查看")
                return []

            tweets = []
            # 使用UTC时区的cutoff_date，以便与Twitter的时间戳比较
            from datetime import timezone
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            scroll_count = 0
            max_scrolls = 5  # 最多滚动5次

            while len(tweets) < max_results and scroll_count < max_scrolls:
                # 查找推文元素
                try:
                    # Twitter的推文article标签
                    tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')

                    for tweet_elem in tweet_elements:
                        if len(tweets) >= max_results:
                            break

                        try:
                            # 提取推文文本
                            text_elem = tweet_elem.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                            text = text_elem.text if text_elem else ""

                            # 提取时间
                            time_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'time')
                            datetime_str = time_elem.get_attribute('datetime') if time_elem else ""

                            # 提取链接
                            link_elems = tweet_elem.find_elements(By.CSS_SELECTOR, 'a[href*="/status/"]')
                            tweet_url = ""
                            for link in link_elems:
                                href = link.get_attribute('href')
                                if href and '/status/' in href:
                                    tweet_url = href
                                    break

                            # 解析时间
                            pub_date = None
                            if datetime_str:
                                try:
                                    pub_date = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                                except:
                                    pass

                            # 过滤重复和时间范围
                            if not text or any(t['text'] == text for t in tweets):
                                continue

                            if pub_date and pub_date < cutoff_date:
                                continue

                            tweets.append({
                                'id': tweet_url.split('/status/')[-1] if tweet_url else '',
                                'text': text,
                                'created_at': pub_date.strftime('%Y-%m-%d %H:%M:%S') if pub_date else '',
                                'url': tweet_url,
                                'author_username': username,
                                'author_name': username,
                                'favorite_count': 0,
                                'retweet_count': 0,
                                'reply_count': 0,
                                'source_type': 'selenium'
                            })

                        except Exception as e:
                            continue

                    # 滚动页面加载更多
                    if len(tweets) < max_results:
                        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                        time.sleep(2)
                        scroll_count += 1
                    else:
                        break

                except NoSuchElementException:
                    break

            return tweets[:max_results]

        except Exception as e:
            print(f"  ❌ 爬取失败: {str(e)[:100]}")
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
        print(f"\n📱 正在使用Selenium爬取 {len(usernames)} 个 Twitter 账号...")
        print(f"每个账号获取最多 {tweets_per_user} 条推文（最近{days_back}天）")
        print("⚠️  使用浏览器自动化，速度较慢，请耐心等待...\n")

        all_tweets = []

        try:
            self._init_driver()

            for i, username in enumerate(usernames, 1):
                print(f"  [{i}/{len(usernames)}] 📥 @{username}...", end=' ', flush=True)

                tweets = self.get_user_tweets(username, tweets_per_user, days_back)

                if tweets:
                    all_tweets.extend(tweets)
                    print(f"✅ {len(tweets)}条")
                else:
                    print("❌")

                # 避免请求过快
                time.sleep(2)

        finally:
            self._close_driver()

        print(f"\n✅ 总共获取 {len(all_tweets)} 条推文")
        return all_tweets


if __name__ == '__main__':
    # 测试代码
    print("=" * 60)
    print("测试 Selenium Twitter 爬虫")
    print("=" * 60)
    print("\n⚠️  注意：")
    print("1. 需要安装 Chrome 浏览器")
    print("2. 需要安装 chromedriver")
    print("3. 速度较慢，每个账号需要10-20秒\n")

    try:
        scraper = TwitterSeleniumScraper(headless=True)

        # 测试获取2个用户
        test_users = ['karpathy', 'ylecun'][:1]  # 先测试1个
        tweets = scraper.get_tweets_from_list(test_users, tweets_per_user=3, days_back=7)

        if tweets:
            print(f"\n📝 示例推文：")
            for i, tweet in enumerate(tweets[:3], 1):
                print(f"\n{i}. @{tweet['author_username']}")
                print(f"   时间: {tweet['created_at']}")
                print(f"   内容: {tweet['text'][:150]}...")
                print(f"   链接: {tweet['url']}")
        else:
            print("\n⚠️  未获取到推文")
            print("可能原因：")
            print("1. Chrome/chromedriver未正确安装")
            print("2. Twitter反爬虫限制")
            print("3. 网络连接问题")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n请确保：")
        print("1. 已安装Chrome浏览器")
        print("2. 已安装selenium: pip install selenium")
        print("3. 已安装chromedriver并在PATH中")
