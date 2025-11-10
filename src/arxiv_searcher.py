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
        # 验证参数类型
        if not isinstance(days_back, int):
            print(f"⚠️  Warning: days_back should be int, got {type(days_back).__name__}: '{days_back}'")
            try:
                days_back = int(days_back)
                print(f"   Converted to int: {days_back}")
            except (ValueError, TypeError) as e:
                print(f"   ❌ Error: Cannot convert to int: {e}")
                print(f"   Using default value: 1")
                days_back = 1

        # 计算日期范围（使用UTC时间，确保包含今天和最新论文）
        from datetime import timezone
        now = datetime.now(timezone.utc)  # 使用带时区的当前时间

        # 添加12小时缓冲以捕获前一天晚上发布的论文（ArXiv通常在UTC晚上更新）
        # 使用日期级别的比较避免时间点差异
        buffer_hours = 12
        start_date = (now - timedelta(days=days_back, hours=buffer_hours)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_date = (now + timedelta(days=1)).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        print(f"搜索时间范围: {start_date.strftime('%Y-%m-%d %H:%M')} 至 {end_date.strftime('%Y-%m-%d %H:%M')} (UTC)")
        print(f"参数: days_back={days_back}, 缓冲时间: {buffer_hours}小时")
        print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")

        papers = []
        total_fetched = 0

        for category in self.categories:
            print(f"搜索类别: {category}")

            # 构建查询
            query = f"cat:{category}"
            print(f"  查询: {query}, 请求数量: {self.max_results * 3}")

            # 创建搜索客户端（获取更多结果以确保覆盖时间范围）
            # 使用 LastUpdatedDate 排序，确保最新更新的论文排在前面（包括新提交和已有论文的更新）
            search = arxiv.Search(
                query=query,
                max_results=self.max_results * 3,  # 获取3倍结果，确保充分覆盖日期范围
                sort_by=arxiv.SortCriterion.LastUpdatedDate,  # 使用更新日期排序（不是提交日期）
                sort_order=arxiv.SortOrder.Descending
            )

            # 执行搜索
            category_count = 0
            fetched_count = 0
            skipped_count = 0
            consecutive_skips = 0  # 连续跳过计数器
            try:
                for result in search.results():
                    fetched_count += 1

                    # 使用更新日期进行过滤（与排序方式一致）
                    updated_date = result.updated if hasattr(result, 'updated') else result.published
                    effective_date = updated_date  # 统一使用更新日期

                    # 调试：输出前几篇论文的日期信息
                    if fetched_count <= 3:
                        print(f"  [调试] 论文 {fetched_count}: {result.title[:50]}...")
                        print(f"         更新日期: {updated_date}")
                        print(f"         有效日期: {effective_date}, 起始日期: {start_date}")

                    # 只保留指定日期范围内的论文（两者都是带时区的）
                    if effective_date >= start_date:
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
                        consecutive_skips = 0  # 重置连续跳过计数器
                    else:
                        skipped_count += 1
                        consecutive_skips += 1  # 增加连续跳过计数器

                        # 调试输出
                        if fetched_count <= 5:
                            print(f"  [调试] 跳过：论文日期 {effective_date} < 起始日期 {start_date}")

                        # 只有连续跳过50篇后才停止（防止因为一篇旧论文就中断）
                        if consecutive_skips >= 50:
                            print(f"  [调试] 连续跳过 {consecutive_skips} 篇论文，停止搜索该类别")
                            break

                    # 安全限制：获取到max_results*3篇后停止
                    if fetched_count >= self.max_results * 3:
                        print(f"  [调试] 已获取 {fetched_count} 篇，达到上限，停止搜索")
                        break
            except arxiv.UnexpectedEmptyPageError as e:
                # ArXiv API返回空页面，说明已经没有更多结果了
                print(f"  [调试] ArXiv返回空页面：{e}")
                print(f"  [调试] 已获取 {fetched_count} 篇，匹配 {category_count} 篇，跳过 {skipped_count} 篇")
            except Exception as e:
                # 捕获其他所有异常并输出详细信息
                print(f"  ❌ Error searching category {category}: {type(e).__name__}: {e}")
                import traceback
                print(f"  Stack trace:")
                traceback.print_exc()
                print(f"  Continuing with next category...")
                continue

            match_rate = (category_count / fetched_count * 100) if fetched_count > 0 else 0
            print(f"  找到 {category_count} 篇论文 (从 {fetched_count} 篇中筛选，匹配率 {match_rate:.1f}%)")
            total_fetched += category_count

        # 去重（有些论文可能属于多个类别）
        unique_papers = self._deduplicate_papers(papers)

        # 按日期统计论文数量
        date_stats = {}
        for paper in unique_papers:
            date = paper.get('updated', paper['published'])
            date_stats[date] = date_stats.get(date, 0) + 1

        print(f"\n共找到 {len(unique_papers)} 篇论文")

        if len(unique_papers) == 0:
            print("⚠️  WARNING: ArXiv returned 0 papers!")
            print("   Possible causes:")
            print("   1. Configuration error (days_back is a string instead of int)")
            print("   2. Date range calculation error")
            print("   3. ArXiv API issue")
            print("   4. No papers published in the specified date range")
            print(f"   Search parameters: days_back={days_back}, categories={self.categories}")
        else:
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
