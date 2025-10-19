#!/usr/bin/env python3
"""
ArXiv Agent - 自动搜索和分析ArXiv论文

使用方法:
    python main.py [选项]

选项:
    --config PATH       配置文件路径 (默认: config.yaml)
    --days N           搜索最近N天的论文 (覆盖配置文件)
    --no-analysis      仅搜索，不进行AI分析
    --min-relevance    最小相关性级别: high/medium/low (默认: medium)
    --max-concurrent   最大并发请求数 (默认: 5)
    --help             显示帮助信息
"""
import os
import sys
import asyncio
import argparse
from dotenv import load_dotenv

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config_loader import ConfigLoader
from arxiv_searcher import ArxivSearcher
from llm_analyzer import LLMAnalyzer
from report_generator import ReportGenerator
from email_sender import EmailSender
from journal_fetcher import JournalFetcher
from twitter_api_v2_fetcher import TwitterAPIv2Fetcher
from twitter_analyzer import TwitterAnalyzer


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='ArXiv Agent - 自动搜索和分析ArXiv论文')
    parser.add_argument('--config', type=str, default='config.yaml', help='配置文件路径')
    parser.add_argument('--days', type=int, help='搜索最近N天的论文')
    parser.add_argument('--no-analysis', action='store_true', help='仅搜索，不进行AI分析')
    parser.add_argument('--min-relevance', type=str,
                        choices=['high', 'medium', 'low'],
                        help='最小相关性级别（覆盖配置文件）')
    parser.add_argument('--max-concurrent', type=int, default=5,
                        help='最大并发请求数（默认: 5）')

    args = parser.parse_args()

    try:
        # 加载配置
        print("=" * 60)
        print("ArXiv Agent - 论文搜索与分析")
        print("=" * 60)
        print(f"\n正在加载配置文件: {args.config}")

        config = ConfigLoader(args.config)

        research_interests = config.get_research_interests()
        research_prompt = config.get_research_prompt()
        arxiv_categories = config.get_arxiv_categories()
        max_results = config.get_max_results()
        days_back = args.days if args.days else config.get_days_back()
        output_dir = config.get_output_dir()
        min_relevance_config = config.get_min_relevance()

        print(f"研究方向: {', '.join(research_interests)}")
        if research_prompt:
            print(f"研究兴趣描述: 已设置（使用自定义描述进行相关性分析）")
        print(f"ArXiv类别: {', '.join(arxiv_categories)}")
        print(f"搜索最近 {days_back} 天的论文")
        print(f"最大结果数: {max_results}")
        relevance_label = {'high': '高', 'medium': '中', 'low': '低'}.get(min_relevance_config, min_relevance_config)
        print(f"相关性阈值: {relevance_label}相关及以上")

        # 1. 从启用的数据源获取内容
        print(f"\n{'=' * 60}")
        print("步骤 1: 从数据源获取内容")
        print("=" * 60)

        enabled_sources = config.get_enabled_sources()
        print(f"启用的数据源: {', '.join(enabled_sources)}\n")

        all_papers = []
        all_tweets = []

        # ArXiv 论文
        if 'arxiv' in enabled_sources:
            print(f"{'=' * 60}")
            print("1.1 搜索 ArXiv 论文")
            print("=" * 60)

            searcher = ArxivSearcher(
                categories=arxiv_categories,
                max_results=max_results
            )
            papers = searcher.search_recent_papers(days_back=days_back)
            all_papers.extend(papers)
            print(f"✅ ArXiv: 找到 {len(papers)} 篇论文\n")

        # CNS 期刊文章
        if 'journals' in enabled_sources:
            print(f"{'=' * 60}")
            print("1.2 获取 CNS 期刊文章")
            print("=" * 60)

            journal_config = config.get('sources', {}).get('journals', {})
            journal_days = journal_config.get('days_back', 7)
            selected_journals = journal_config.get('selected_journals', None)

            journal_fetcher = JournalFetcher(selected_journals=selected_journals)
            journal_articles = journal_fetcher.fetch_recent_articles(days_back=journal_days)
            all_papers.extend(journal_articles)
            print(f"✅ 期刊: 找到 {len(journal_articles)} 篇文章\n")

        # # Twitter 推文（已注释）
        # if 'twitter' in enabled_sources:
        #     print(f"{'=' * 60}")
        #     print("1.3 获取 Twitter 推文")
        #     print("=" * 60)
        #
        #     twitter_config = config.get_twitter_config()
        #     bearer_token = twitter_config.get('bearer_token') or os.getenv('TWITTER_BEARER_TOKEN')
        #
        #     if bearer_token:
        #         try:
        #             twitter_fetcher = TwitterAPIv2Fetcher(bearer_token=bearer_token)
        #
        #             # 根据配置选择获取模式
        #             my_username = twitter_config.get('my_username', '').strip()
        #             following_usernames = twitter_config.get('following_usernames', [])
        #
        #             if my_username:
        #                 # 模式3：从您的关注列表获取
        #                 print(f"使用模式：从 @{my_username} 的关注列表获取推文")
        #                 tweets = twitter_fetcher.get_tweets_from_my_following(
        #                     my_username=my_username,
        #                     tweets_per_user=twitter_config.get('tweets_per_user', 5),
        #                     days_back=twitter_config.get('days_back', 7),
        #                     max_users=twitter_config.get('max_following', 50)
        #                 )
        #             elif following_usernames:
        #                 # 模式2：从指定用户列表获取
        #                 print(f"使用模式：从指定的 {len(following_usernames)} 个用户获取推文")
        #                 tweets = twitter_fetcher.get_tweets_from_list(
        #                     usernames=following_usernames,
        #                     tweets_per_user=twitter_config.get('tweets_per_user', 5),
        #                     days_back=twitter_config.get('days_back', 7)
        #                 )
        #             else:
        #                 # 模式1：根据研究兴趣搜索
        #                 print("使用模式：根据研究兴趣搜索推文")
        #                 tweets = twitter_fetcher.search_by_research_interests(
        #                     research_interests=research_interests[:5],  # 限制关键词数量
        #                     max_results=twitter_config.get('max_tweets', 50),
        #                     days_back=twitter_config.get('days_back', 7)
        #                 )
        #
        #             all_tweets = tweets
        #             print(f"✅ Twitter: 找到 {len(tweets)} 条推文\n")
        #         except Exception as e:
        #             print(f"⚠️  Twitter 获取失败: {e}\n")
        #     else:
        #         print("⚠️  未配置 Twitter Bearer Token，跳过\n")

        if not all_papers:
            print("未找到任何内容。")
            return

        print(f"{'=' * 60}")
        print(f"总计: 论文/文章 {len(all_papers)} 篇")
        print("=" * 60)

        papers = all_papers

        # 2. 分析内容（可选）
        if not args.no_analysis:
            print(f"\n{'=' * 60}")
            print("步骤 2: 使用Claude分析内容相关性")
            print("=" * 60)

            # 获取API配置（优先从config.yaml，然后从.env）
            api_key = config.get_api_key() or os.getenv('ANTHROPIC_AUTH_TOKEN') or os.getenv('ANTHROPIC_API_KEY')
            api_base_url = config.get_api_base_url() or os.getenv('ANTHROPIC_BASE_URL')

            if not api_key:
                print("错误: 未找到API密钥")
                print("请在config.yaml中设置api_key，或在.env文件中设置ANTHROPIC_AUTH_TOKEN")
                return

            # 获取并发配置（命令行参数覆盖配置文件）
            max_concurrent = args.max_concurrent if args.max_concurrent != 5 else config.get_max_concurrent()

            analyzer = LLMAnalyzer(
                api_key=api_key,
                model=config.get_claude_model(),
                max_tokens=config.get_claude_max_tokens(),
                base_url=api_base_url,
                max_concurrent=max_concurrent,
                batch_size=config.get_batch_size(),
                detail_batch_size=config.get_detail_batch_size()
            )

            # 分析论文和文章
            if papers:
                print(f"\n分析 {len(papers)} 篇论文/文章...")
                analyzed_papers = asyncio.run(
                    analyzer.two_stage_analyze_papers_async(papers, research_interests, research_prompt)
                )
            else:
                analyzed_papers = []

            # 分析推文
            analyzed_tweets = []
            if all_tweets:
                print(f"\n分析 {len(all_tweets)} 条推文...")
                twitter_analyzer = TwitterAnalyzer(
                    api_key=api_key,
                    model=config.get_claude_model(),
                    max_tokens=config.get_claude_max_tokens(),
                    base_url=api_base_url,
                    max_concurrent=max_concurrent
                )
                analyzed_tweets = asyncio.run(
                    twitter_analyzer.analyze_tweets_async(all_tweets, research_interests, research_prompt)
                )

            # 获取相关性阈值（命令行参数覆盖配置文件）
            min_relevance = args.min_relevance if args.min_relevance else config.get_min_relevance()

            # 过滤相关论文
            relevant_papers = analyzer.filter_relevant_papers(
                analyzed_papers,
                min_relevance=min_relevance
            ) if analyzed_papers else []

            # 过滤相关推文
            relevant_tweets = [t for t in analyzed_tweets if t.get('relevance_level') in ['high', 'medium']] if analyzed_tweets else []

            relevance_label = {'high': '高', 'medium': '中', 'low': '低'}.get(min_relevance, min_relevance)
            print(f"\n根据阈值（{relevance_label}相关及以上）:")
            print(f"  - 相关论文/文章: {len(relevant_papers)} 篇")
            print(f"  - 相关推文: {len(relevant_tweets)} 条")

            papers_to_report = relevant_papers
            tweets_to_report = relevant_tweets
        else:
            print("\n跳过AI分析")
            papers_to_report = papers
            tweets_to_report = all_tweets

        # 3. 生成报告
        print(f"\n{'=' * 60}")
        print("步骤 3: 生成报告")
        print("=" * 60)

        generator = ReportGenerator(output_dir=output_dir)
        report_path = generator.generate_report(papers_to_report, research_interests, tweets_to_report)

        print(f"\n{'=' * 60}")
        print("完成!")
        print("=" * 60)
        print(f"报告已保存到: {report_path}")
        print(f"总论文/文章数: {len(papers)}")
        if all_tweets:
            print(f"总推文数: {len(all_tweets)}")
        if not args.no_analysis:
            print(f"相关论文/文章数: {len(papers_to_report)}")
            if tweets_to_report:
                print(f"相关推文数: {len(tweets_to_report)}")

        # 4. 发送邮件（如果启用）
        if config.is_email_enabled():
            print(f"\n{'=' * 60}")
            print("步骤 4: 发送邮件通知")
            print("=" * 60)

            email_config = config.get_email_config()

            try:
                sender = EmailSender(
                    smtp_server=email_config.get('smtp_server'),
                    smtp_port=email_config.get('smtp_port', 587),
                    sender_email=email_config.get('sender_email'),
                    sender_password=email_config.get('sender_password'),
                    use_ssl=email_config.get('use_ssl', False)
                )

                # 收件人邮箱（支持多个，用逗号分隔）
                receiver_str = email_config.get('receiver_email', '')
                receiver_emails = [email.strip() for email in receiver_str.split(',') if email.strip()]

                if not receiver_emails:
                    print("⚠️  未配置收件人邮箱，跳过邮件发送")
                else:
                    # 构建邮件主题
                    from datetime import datetime
                    subject_prefix = email_config.get('subject_prefix', '[ArXiv每日论文]')
                    subject = f"{subject_prefix} {datetime.now().strftime('%Y-%m-%d')}"

                    # 生成HTML格式的报告内容
                    print("正在生成HTML格式报告...")
                    html_content = generator.generate_html_report(
                        papers_to_report,
                        research_interests,
                        tweets_to_report
                    )

                    # 发送HTML格式邮件（MD报告作为附件）
                    sender.send_html_report(
                        receiver_emails=receiver_emails,
                        subject=subject,
                        html_content=html_content,
                        attachments=[report_path]
                    )

            except Exception as e:
                print(f"❌ 邮件发送配置错误: {e}")
                import traceback
                traceback.print_exc()

    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
