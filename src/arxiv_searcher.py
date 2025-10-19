"""
ArXiv论文搜索模块
"""
import arxiv
from datetime import datetime, timedelta
from typing import List, Dict
from dateutil import parser as date_parser


class ArxivSearcher:
    """ArXiv论文搜索器"""

    def __init__(self, categories: List[str], max_results: int = 100):
        """
        初始化搜索器

        Args:
            categories: 要搜索的arxiv类别列表
            max_results: 最大返回结果数
        """
        self.categories = categories
        self.max_results = max_results

    def search_recent_papers(self, days_back: int = 1) -> List[Dict]:
        """
        搜索最近几天的论文

        Args:
            days_back: 向前搜索的天数

        Returns:
            论文信息列表
        """
        # 计算日期范围（使用UTC时间，确保包含今天和最新论文）
        end_date = datetime.utcnow() + timedelta(days=1)  # 加1天确保包含今天的所有论文
        start_date = end_date - timedelta(days=days_back + 1)

        print(f"搜索时间范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')} (UTC)")

        papers = []
        total_fetched = 0

        for category in self.categories:
            print(f"搜索类别: {category}")

            # 构建查询
            query = f"cat:{category}"

            # 创建搜索客户端（获取更多结果以确保覆盖时间范围）
            search = arxiv.Search(
                query=query,
                max_results=self.max_results * 2,  # 获取2倍结果，确保不漏掉论文
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )

            # 执行搜索
            category_count = 0
            try:
                for result in search.results():
                    # 检查提交日期（使用published或updated中较新的）
                    submitted_date = result.published
                    updated_date = result.updated if hasattr(result, 'updated') else result.published
                    effective_date = max(submitted_date, updated_date)

                    # 只保留指定日期范围内的论文
                    if effective_date >= start_date.replace(tzinfo=effective_date.tzinfo):
                        paper_info = {
                            'title': result.title,
                            'authors': [author.name for author in result.authors],
                            'abstract': result.summary,
                            'url': result.entry_id,
                            'pdf_url': result.pdf_url,
                            'published': result.published.strftime('%Y-%m-%d'),
                            'updated': updated_date.strftime('%Y-%m-%d'),
                            'categories': result.categories,
                            'primary_category': result.primary_category
                        }
                        papers.append(paper_info)
                        category_count += 1
                    else:
                        # 由于是按时间降序排列，如果遇到超出范围的论文就可以停止
                        break
            except arxiv.UnexpectedEmptyPageError:
                # ArXiv API返回空页面，说明已经没有更多结果了
                # 这是正常情况，不需要报错
                pass

            print(f"  找到 {category_count} 篇论文")
            total_fetched += category_count

        # 去重（有些论文可能属于多个类别）
        unique_papers = self._deduplicate_papers(papers)

        # 按日期统计论文数量
        date_stats = {}
        for paper in unique_papers:
            date = paper.get('updated', paper['published'])
            date_stats[date] = date_stats.get(date, 0) + 1

        print(f"\n共找到 {len(unique_papers)} 篇论文")
        print("按日期分布:")
        for date in sorted(date_stats.keys(), reverse=True):
            print(f"  {date}: {date_stats[date]} 篇")

        return unique_papers

    def _deduplicate_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        根据URL去重论文

        Args:
            papers: 论文列表

        Returns:
            去重后的论文列表
        """
        seen_urls = set()
        unique_papers = []

        for paper in papers:
            if paper['url'] not in seen_urls:
                seen_urls.add(paper['url'])
                unique_papers.append(paper)

        return unique_papers
