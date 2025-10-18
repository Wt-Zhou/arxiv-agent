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
        arxiv_categories = config.get_arxiv_categories()
        max_results = config.get_max_results()
        days_back = args.days if args.days else config.get_days_back()
        output_dir = config.get_output_dir()
        min_relevance_config = config.get_min_relevance()

        print(f"研究方向: {', '.join(research_interests)}")
        print(f"ArXiv类别: {', '.join(arxiv_categories)}")
        print(f"搜索最近 {days_back} 天的论文")
        print(f"最大结果数: {max_results}")
        relevance_label = {'high': '高', 'medium': '中', 'low': '低'}.get(min_relevance_config, min_relevance_config)
        print(f"相关性阈值: {relevance_label}相关及以上")

        # 1. 搜索论文
        print(f"\n{'=' * 60}")
        print("步骤 1: 搜索ArXiv论文")
        print("=" * 60)

        searcher = ArxivSearcher(
            categories=arxiv_categories,
            max_results=max_results
        )

        papers = searcher.search_recent_papers(days_back=days_back)

        if not papers:
            print("未找到任何论文。")
            return

        print(f"找到 {len(papers)} 篇论文")

        # 2. 分析论文（可选）
        if not args.no_analysis:
            print(f"\n{'=' * 60}")
            print("步骤 2: 使用Claude分析论文相关性")
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

            # 使用两阶段异步分析（快速筛选 + 详细分析）
            analyzed_papers = asyncio.run(
                analyzer.two_stage_analyze_papers_async(papers, research_interests)
            )

            # 获取相关性阈值（命令行参数覆盖配置文件）
            min_relevance = args.min_relevance if args.min_relevance else config.get_min_relevance()

            # 过滤相关论文
            relevant_papers = analyzer.filter_relevant_papers(
                analyzed_papers,
                min_relevance=min_relevance
            )

            relevance_label = {'high': '高', 'medium': '中', 'low': '低'}.get(min_relevance, min_relevance)
            print(f"\n根据阈值（{relevance_label}相关及以上）找到 {len(relevant_papers)} 篇相关论文")

            papers_to_report = relevant_papers
        else:
            print("\n跳过AI分析")
            papers_to_report = papers

        # 3. 生成报告
        print(f"\n{'=' * 60}")
        print("步骤 3: 生成报告")
        print("=" * 60)

        generator = ReportGenerator(output_dir=output_dir)
        report_path = generator.generate_report(papers_to_report, research_interests)

        print(f"\n{'=' * 60}")
        print("完成!")
        print("=" * 60)
        print(f"报告已保存到: {report_path}")
        print(f"总论文数: {len(papers)}")
        if not args.no_analysis:
            print(f"相关论文数: {len(papers_to_report)}")

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

                    # 构建邮件摘要
                    if not args.no_analysis:
                        summary = f"""今日ArXiv论文分析报告已生成！

📊 统计信息：
- 总论文数: {len(papers)} 篇
- 相关论文数: {len(papers_to_report)} 篇
  - 高相关: {sum(1 for p in papers_to_report if p.get('relevance_level') == 'high')} 篇
  - 中相关: {sum(1 for p in papers_to_report if p.get('relevance_level') == 'medium')} 篇

🔍 研究方向：
{chr(10).join(f'  - {interest}' for interest in research_interests)}

详细内容请查看附件报告。"""
                    else:
                        summary = f"""今日ArXiv论文搜索完成！

📊 统计信息：
- 总论文数: {len(papers)} 篇

详细内容请查看附件报告。"""

                    # 发送邮件
                    sender.send_report(
                        receiver_emails=receiver_emails,
                        subject=subject,
                        report_path=report_path,
                        summary=summary
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
