"""
学术期刊文章获取模块
支持Nature、Science、Cell及其子刊
"""
import feedparser
import httpx
from typing import List, Dict
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class JournalFetcher:
    """学术期刊文章获取器"""

    # Nature系列期刊RSS feeds
    NATURE_JOURNALS = {
        'Nature': 'https://www.nature.com/nature.rss',
        'Nature Machine Intelligence': 'https://www.nature.com/natmachintell.rss',
        'Nature Communications': 'https://www.nature.com/ncomms.rss',
        'Nature Methods': 'https://www.nature.com/nmeth.rss',
        'Nature Biotechnology': 'https://www.nature.com/nbt.rss',
        'Nature Neuroscience': 'https://www.nature.com/neuro.rss',
        'Nature Genetics': 'https://www.nature.com/ng.rss',
        'Nature Physics': 'https://www.nature.com/nphys.rss',
        'Nature Chemistry': 'https://www.nature.com/nchem.rss',
        'Nature Materials': 'https://www.nature.com/nmat.rss',
        'Nature Reviews': 'https://www.nature.com/natrevmats.rss'
    }

    # Science系列期刊
    SCIENCE_JOURNALS = {
        'Science': 'https://www.science.org/rss/news_current.xml',
        'Science Robotics': 'https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=scirobotics',
        'Science Advances': 'https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=sciadv'
    }

    # Cell系列期刊
    CELL_JOURNALS = {
        'Cell': 'https://www.cell.com/cell/current.rss',
        'Cell Reports': 'https://www.cell.com/cell-reports/current.rss',
        'Cell Systems': 'https://www.cell.com/cell-systems/current.rss',
        'Neuron': 'https://www.cell.com/neuron/current.rss',
        'Molecular Cell': 'https://www.cell.com/molecular-cell/current.rss',
        'Developmental Cell': 'https://www.cell.com/developmental-cell/current.rss'
    }

    def __init__(self, selected_journals: List[str] = None):
        """
        初始化期刊获取器

        Args:
            selected_journals: 要获取的期刊列表（如果为None则获取所有）
        """
        self.selected_journals = selected_journals
        self.all_journals = {
            **self.NATURE_JOURNALS,
            **self.SCIENCE_JOURNALS,
            **self.CELL_JOURNALS
        }

    def fetch_recent_articles(self, days_back: int = 7) -> List[Dict]:
        """
        获取最近的文章

        Args:
            days_back: 获取最近几天的文章

        Returns:
            文章列表
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)

        print(f"\n正在从学术期刊获取最近 {days_back} 天的文章...")

        # 确定要获取的期刊
        journals_to_fetch = {}
        if self.selected_journals:
            for journal_name in self.selected_journals:
                if journal_name in self.all_journals:
                    journals_to_fetch[journal_name] = self.all_journals[journal_name]
                else:
                    print(f"⚠️  未找到期刊: {journal_name}")
        else:
            journals_to_fetch = self.all_journals

        print(f"将从 {len(journals_to_fetch)} 个期刊获取文章:\n  {', '.join(journals_to_fetch.keys())}\n")

        all_articles = []

        for journal_name, rss_url in journals_to_fetch.items():
            print(f"  正在获取 {journal_name}...")

            try:
                articles = self._fetch_from_rss(journal_name, rss_url, cutoff_date)
                all_articles.extend(articles)
                print(f"    ✓ 找到 {len(articles)} 篇文章")

            except Exception as e:
                print(f"    ✗ 获取失败: {e}")

        print(f"\n✅ 共找到 {len(all_articles)} 篇文章")

        # 按发表时间降序排序
        all_articles.sort(key=lambda x: x.get('published_date', ''), reverse=True)

        return all_articles

    def _fetch_from_rss(self, journal_name: str, rss_url: str, cutoff_date: datetime) -> List[Dict]:
        """
        从RSS feed获取文章

        Args:
            journal_name: 期刊名称
            rss_url: RSS feed URL
            cutoff_date: 截止日期

        Returns:
            文章列表
        """
        try:
            # 解析RSS feed
            feed = feedparser.parse(rss_url)

            articles = []

            for entry in feed.entries:
                # 解析发表日期
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_date = datetime(*entry.updated_parsed[:6])

                # 只保留指定日期范围内的文章
                if published_date and published_date >= cutoff_date:
                    # 提取摘要
                    abstract = ''
                    if hasattr(entry, 'summary'):
                        # 使用BeautifulSoup清理HTML标签
                        soup = BeautifulSoup(entry.summary, 'html.parser')
                        abstract = soup.get_text().strip()[:500]  # 限制长度

                    # 提取作者
                    authors = []
                    if hasattr(entry, 'authors'):
                        authors = [a.get('name', '') for a in entry.authors if a.get('name')]
                    elif hasattr(entry, 'author'):
                        authors = [entry.author]

                    articles.append({
                        'title': entry.title if hasattr(entry, 'title') else '',
                        'journal': journal_name,
                        'authors': authors,
                        'abstract': abstract,
                        'url': entry.link if hasattr(entry, 'link') else '',
                        'published_date': published_date.strftime('%Y-%m-%d') if published_date else '',
                        'source_type': 'journal'
                    })

            return articles

        except Exception as e:
            print(f"      解析RSS失败: {e}")
            return []

    def get_available_journals(self) -> Dict[str, List[str]]:
        """
        获取所有可用的期刊列表

        Returns:
            按系列分类的期刊字典
        """
        return {
            'Nature系列': list(self.NATURE_JOURNALS.keys()),
            'Science系列': list(self.SCIENCE_JOURNALS.keys()),
            'Cell系列': list(self.CELL_JOURNALS.keys())
        }
