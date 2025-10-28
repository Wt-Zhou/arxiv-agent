"""
生成Markdown格式的论文报告
"""
import os
from datetime import datetime
from typing import List, Dict


class ReportGenerator:
    """Markdown报告生成器"""

    def __init__(self, output_dir: str = "reports"):
        """
        初始化报告生成器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_report(self, papers: List[Dict], research_interests: List[str], tweets: List[Dict] = None) -> str:
        """
        生成多源内容报告

        Args:
            papers: 论文列表（已包含分析结果）
            research_interests: 研究方向列表
            tweets: 推文列表（可选）

        Returns:
            报告文件路径
        """
        # 生成文件名
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"arxiv_papers_{date_str}.md"
        filepath = os.path.join(self.output_dir, filename)

        # 生成报告内容
        content = self._generate_content(papers, research_interests, date_str, tweets or [])

        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"报告已生成: {filepath}")
        return filepath

    def generate_html_report(self, papers: List[Dict], research_interests: List[str], tweets: List[Dict] = None) -> str:
        """
        生成HTML格式的报告（用于邮件）

        Args:
            papers: 论文列表（已包含分析结果）
            research_interests: 研究方向列表
            tweets: 推文列表（可选）

        Returns:
            HTML内容字符串
        """
        date_str = datetime.now().strftime('%Y-%m-%d')
        tweets = tweets or []

        # 生成HTML内容
        html_content = self._generate_html_content(papers, research_interests, date_str, tweets)

        return html_content

    def _generate_content(self, papers: List[Dict], research_interests: List[str], date_str: str, tweets: List[Dict] = None) -> str:
        """
        生成报告内容

        Args:
            papers: 论文列表
            research_interests: 研究方向列表
            date_str: 日期字符串
            tweets: 推文列表

        Returns:
            Markdown格式的报告内容
        """
        tweets = tweets or []
        lines = []

        # 标题
        lines.append(f"# 学术内容日报 - {date_str}\n")

        # 研究方向
        lines.append("## 研究方向\n")
        for interest in research_interests:
            lines.append(f"- {interest}")
        lines.append("")

        # 统计信息
        lines.append("## 统计信息\n")
        lines.append(f"- 总论文/文章数: {len(papers)}")
        if tweets:
            lines.append(f"- 总推文数: {len(tweets)}")

        # 按相关性级别统计（仅当有分析结果时显示）
        relevance_stats = {}
        for paper in papers:
            level = paper.get('relevance_level', 'unknown')
            if level != 'unknown':  # 只统计已分析的论文
                relevance_stats[level] = relevance_stats.get(level, 0) + 1

        if relevance_stats:  # 只有当有已分析的论文时才显示相关性分布
            lines.append("- 论文相关性分布:")
            for level in ['high', 'medium', 'low', 'none']:
                if level in relevance_stats:
                    lines.append(f"  - {level}: {relevance_stats[level]}")

        # 推文相关性统计
        if tweets:
            tweet_stats = {}
            for tweet in tweets:
                level = tweet.get('relevance_level', 'unknown')
                if level != 'unknown':
                    tweet_stats[level] = tweet_stats.get(level, 0) + 1
            if tweet_stats:
                lines.append("- 推文相关性分布:")
                for level in ['high', 'medium', 'low']:
                    if level in tweet_stats:
                        lines.append(f"  - {level}: {tweet_stats[level]}")

        lines.append("")

        # 生成核心发现摘要（论文+推文）
        high_papers = [p for p in papers if p.get('relevance_level') == 'high']
        high_tweets = [t for t in tweets if t.get('relevance_level') == 'high']

        if high_papers or high_tweets:
            lines.append("## 🔍 核心发现速览\n")

            # 论文摘要
            if high_papers:
                summary_by_topic = self._generate_topic_summary(high_papers)
                lines.extend(summary_by_topic)

            # Twitter热点摘要
            if high_tweets:
                lines.append("")
                twitter_summary = self._generate_twitter_summary(high_tweets)
                lines.extend(twitter_summary)

            lines.append("")

        # 按相关性分组
        medium_papers = [p for p in papers if p.get('relevance_level') == 'medium']
        low_papers = [p for p in papers if p.get('relevance_level') == 'low']
        unanalyzed_papers = [p for p in papers if p.get('relevance_level') in ['unknown', None]]

        # 高相关性论文
        if high_papers:
            lines.append("## 强烈推荐 (高相关性)\n")
            for paper in high_papers:
                lines.extend(self._format_paper(paper))

        # 中等相关性论文
        if medium_papers:
            lines.append("## 推荐阅读 (中等相关性)\n")
            for paper in medium_papers:
                lines.extend(self._format_paper(paper))

        # 低相关性论文
        if low_papers:
            lines.append("## 可能感兴趣 (低相关性)\n")
            for paper in low_papers:
                lines.extend(self._format_paper(paper))

        # 未分析的论文（按日期排序）
        if unanalyzed_papers:
            lines.append("## 所有论文 (未分析)\n")
            # 按更新日期或发布日期排序（最新的在前）
            unanalyzed_papers.sort(key=lambda x: x.get('updated', x.get('published', '')), reverse=True)
            for paper in unanalyzed_papers:
                lines.extend(self._format_paper(paper))

        # Twitter 推文部分
        if tweets:
            lines.append("---\n")
            lines.append("# Twitter 学术动态\n")

            # 按相关性分组
            high_tweets = [t for t in tweets if t.get('relevance_level') == 'high']
            medium_tweets = [t for t in tweets if t.get('relevance_level') == 'medium']
            low_tweets = [t for t in tweets if t.get('relevance_level') == 'low']

            # 高相关推文
            if high_tweets:
                lines.append("## 强烈推荐 (高相关性)\n")
                for tweet in high_tweets:
                    lines.extend(self._format_tweet(tweet))

            # 中等相关推文
            if medium_tweets:
                lines.append("## 值得关注 (中等相关性)\n")
                for tweet in medium_tweets:
                    lines.extend(self._format_tweet(tweet))

            # 低相关推文
            if low_tweets:
                lines.append("## 可能感兴趣 (低相关性)\n")
                for tweet in low_tweets:
                    lines.extend(self._format_tweet(tweet))

        return '\n'.join(lines)

    def _generate_topic_summary(self, papers: List[Dict]) -> List[str]:
        """
        生成助手风格的核心发现摘要

        Args:
            papers: 高相关论文列表

        Returns:
            摘要文本行列表
        """
        lines = []

        # 按主题分类（基于matched_interests字段）
        topic_papers = {}
        for paper in papers:
            interests = paper.get('matched_interests', [])
            source = paper.get('journal', paper.get('primary_category', 'ArXiv'))

            # 如果是CNS期刊，添加期刊标记
            is_cns = any(journal in str(source) for journal in ['Nature', 'Science', 'Cell'])

            if interests:
                for interest in interests:
                    if interest not in topic_papers:
                        topic_papers[interest] = []
                    topic_papers[interest].append((paper, is_cns))
            else:
                # 没有明确主题的归类为"其他"
                if '其他前沿研究' not in topic_papers:
                    topic_papers['其他前沿研究'] = []
                topic_papers['其他前沿研究'].append((paper, is_cns))

        # 生成助手风格的总结
        lines.append("根据您的研究兴趣，本期为您筛选出 **{}篇高相关论文**。以下是核心发现：\n".format(len(papers)))

        # 按主题输出，每个主题最多推荐2-3篇
        total_recommended = 0
        max_total = 10  # 总共不超过10篇

        for topic, topic_papers_list in sorted(topic_papers.items(), key=lambda x: -len(x[1])):
            if total_recommended >= max_total:
                break

            # 优先显示CNS期刊文章
            topic_papers_list.sort(key=lambda x: (not x[1], x[0].get('title', '')))

            # 每个主题推荐的数量
            recommend_count = min(3, len(topic_papers_list), max_total - total_recommended)
            if recommend_count == 0:
                continue

            lines.append(f"**{topic}**：本期找到{len(topic_papers_list)}篇相关论文，为您重点推荐以下{recommend_count}篇：\n")

            for i, (paper, is_cns) in enumerate(topic_papers_list[:recommend_count], 1):
                total_recommended += 1
                title = paper.get('title', '未知标题')
                source = paper.get('journal') if paper.get('journal') else f"ArXiv {paper.get('primary_category', 'unknown')}"

                # 生成符合GitHub MD规范的锚点（只保留字母数字和连字符）
                import re
                anchor = re.sub(r'[^\w\s-]', '', title.lower())  # 移除特殊字符
                anchor = re.sub(r'[\s_]+', '-', anchor)  # 空格和下划线转为连字符
                anchor = anchor[:80]  # 限制长度

                # CNS期刊特别标注
                source_tag = f"**{source}**" if is_cns else source

                # 简短说明（从summary或why_relevant提取）
                brief = paper.get('summary', paper.get('why_relevant', ''))
                if brief:
                    # 提取第一句话或前100字
                    brief = brief.split('。')[0].split('.')[0][:100].replace('\n', ' ').strip()

                lines.append(f"{i}. [{title}](#{anchor}) ({source_tag})")
                if brief:
                    lines.append(f"   - {brief}")
                lines.append("")

            # 如果还有更多论文
            remaining = len(topic_papers_list) - recommend_count
            if remaining > 0:
                lines.append(f"   *另有{remaining}篇{topic}相关论文，详见下文*\n")

        if total_recommended < len(papers):
            lines.append(f"\n其余 {len(papers) - total_recommended} 篇高相关论文详见下文「强烈推荐」部分。\n")

        return lines

    def _generate_twitter_summary(self, tweets: List[Dict]) -> List[str]:
        """
        生成Twitter热点摘要

        Args:
            tweets: 高相关推文列表

        Returns:
            摘要文本行列表
        """
        lines = []

        lines.append("**📱 Twitter学术动态**\n")

        # 分析推文主题
        topics = {}
        for tweet in tweets:
            text = tweet.get('text', '')
            # 简单的关键词提取（基于常见学术话题）
            keywords = []
            topic_keywords = {
                '自动驾驶': ['自动驾驶', 'autonomous driving', 'self-driving', 'Tesla', 'FSD'],
                '大语言模型': ['LLM', 'GPT', 'Claude', 'language model', '大语言模型', '大模型'],
                '强化学习': ['强化学习', 'reinforcement learning', 'RL', 'policy'],
                '具身智能': ['具身', 'embodied', 'robot', '机器人', 'manipulation'],
                'VLM/多模态': ['VLM', 'vision language', '多模态', 'multimodal', 'CLIP'],
            }

            for topic, kws in topic_keywords.items():
                if any(kw.lower() in text.lower() for kw in kws):
                    if topic not in topics:
                        topics[topic] = []
                    topics[topic].append(tweet)
                    break

        # 生成总结
        if not topics:
            lines.append(f"本期收集了{len(tweets)}条与您研究方向相关的学术讨论，涵盖了最新的技术动态和研究进展。")
        else:
            topic_summary = []
            for topic, topic_tweets in sorted(topics.items(), key=lambda x: -len(x[1]))[:3]:
                topic_summary.append(f"**{topic}**（{len(topic_tweets)}条）")

            lines.append(f"本期Twitter学术圈的热点话题包括：{' | '.join(topic_summary)}\n")

            # 挑选2-3条有代表性的推文
            sample_count = min(3, len(tweets))
            lines.append(f"为您精选{sample_count}条最具代表性的讨论：\n")

            for i, tweet in enumerate(tweets[:sample_count], 1):
                author = tweet.get('author_name', tweet.get('author_username', '未知'))
                text_preview = tweet.get('text', '')[:100].replace('\n', ' ').strip()
                if len(tweet.get('text', '')) > 100:
                    text_preview += '...'

                lines.append(f"{i}. **@{author}**：{text_preview}")

                # 添加相关性说明
                if tweet.get('why_relevant'):
                    relevance = tweet.get('why_relevant', '')[:80].replace('\n', ' ')
                    lines.append(f"   > {relevance}")

                lines.append("")

        lines.append(f"*完整Twitter动态详见下文「Twitter学术动态」部分*\n")

        return lines

    def _format_paper(self, paper: Dict) -> List[str]:
        """
        格式化单篇论文

        Args:
            paper: 论文信息

        Returns:
            格式化后的行列表
        """
        lines = []

        # 标题
        lines.append(f"### {paper.get('title', '无标题')}\n")

        # 基本信息
        published_date = paper.get('published') or paper.get('pub_date') or paper.get('date', '未知')
        updated_date = paper.get('updated')
        if updated_date and updated_date != published_date:
            lines.append(f"**发布日期:** {published_date} (更新: {updated_date})")
        else:
            lines.append(f"**发布日期:** {published_date}")

        # 作者和单位
        authors = paper.get('authors', [])
        if authors:
            authors_display = ', '.join(authors[:3])
            if len(authors) > 3:
                authors_display += f" 等 ({len(authors)}位作者)"
            lines.append(f"**作者:** {authors_display}")

        # 作者单位（如果有）
        if paper.get('affiliations'):
            lines.append(f"**单位:** {paper['affiliations']}")

        # 类别/期刊（ArXiv有category，期刊有journal）
        if paper.get('primary_category'):
            lines.append(f"**类别:** {paper['primary_category']}")
        elif paper.get('journal'):
            lines.append(f"**期刊:** {paper['journal']}")

        # 链接
        if paper.get('url'):
            lines.append(f"**论文链接:** {paper['url']}")
        if paper.get('pdf_url'):
            lines.append(f"**PDF链接:** {paper['pdf_url']}")

        # 相关性信息
        if paper.get('matched_interests'):
            lines.append(f"**相关领域:** {', '.join(paper['matched_interests'])}")

        # 摘要中文翻译（优先显示）
        if paper.get('abstract_zh'):
            lines.append(f"\n**摘要（中文）:**")
            lines.append(f"{paper['abstract_zh']}")

        # AI生成的总结（如果有）
        if paper.get('summary'):
            lines.append(f"\n**核心内容:**")
            lines.append(f"{paper['summary']}")

        lines.append("\n---\n")

        return lines

    def _format_tweet(self, tweet: Dict) -> List[str]:
        """
        格式化单条推文

        Args:
            tweet: 推文信息

        Returns:
            格式化后的行列表
        """
        lines = []

        # 作者信息
        author = f"@{tweet.get('author_username', 'unknown')}"
        if tweet.get('author_name'):
            author = f"{tweet.get('author_name')} ({author})"

        lines.append(f"### {author}\n")

        # 发布时间
        lines.append(f"**发布时间:** {tweet.get('created_at', 'unknown')}")

        # 推文内容
        lines.append(f"\n**内容:**")
        lines.append(f"{tweet.get('text', '')}")

        # AI分析的相关性说明
        if tweet.get('why_relevant'):
            lines.append(f"\n**相关性说明:**")
            lines.append(f"{tweet.get('why_relevant')}")

        # 互动数据
        if tweet.get('favorite_count') or tweet.get('retweet_count'):
            lines.append(f"\n**互动数据:**")
            lines.append(f"👍 {tweet.get('favorite_count', 0)} | 🔄 {tweet.get('retweet_count', 0)} | 💬 {tweet.get('reply_count', 0)}")

        # 推文链接
        lines.append(f"\n**链接:** {tweet.get('url', '')}")

        lines.append("\n---\n")

        return lines

    def generate_simple_list(self, papers: List[Dict]) -> str:
        """
        生成简单的论文列表（用于快速浏览）

        Args:
            papers: 论文列表

        Returns:
            简单列表的文本
        """
        lines = []

        for i, paper in enumerate(papers, 1):
            lines.append(f"{i}. **{paper['title']}**")
            lines.append(f"   - URL: {paper['url']}")
            lines.append(f"   - 相关性: {paper.get('relevance_level', 'unknown')}")
            if paper.get('matched_interests'):
                lines.append(f"   - 相关领域: {', '.join(paper['matched_interests'])}")
            lines.append("")

        return '\n'.join(lines)

    def _generate_paper_anchor(self, paper: Dict, index: int = 0) -> str:
        """
        生成论文的唯一锚点ID
        使用论文URL的hash或索引，确保唯一性和一致性

        Args:
            paper: 论文信息
            index: 论文索引（作为备选）

        Returns:
            锚点ID字符串
        """
        import hashlib

        # 优先使用论文URL生成hash作为锚点
        if paper.get('url'):
            url_hash = hashlib.md5(paper['url'].encode()).hexdigest()[:12]
            return f"paper-{url_hash}"
        elif paper.get('pdf_url'):
            url_hash = hashlib.md5(paper['pdf_url'].encode()).hexdigest()[:12]
            return f"paper-{url_hash}"
        else:
            # 使用标题hash
            title = paper.get('title', f'paper-{index}')
            title_hash = hashlib.md5(title.encode()).hexdigest()[:12]
            return f"paper-{title_hash}"

    def _generate_html_content(self, papers: List[Dict], research_interests: List[str], date_str: str, tweets: List[Dict] = None) -> str:
        """
        生成HTML格式的报告内容

        Args:
            papers: 论文列表
            research_interests: 研究方向列表
            date_str: 日期字符串
            tweets: 推文列表

        Returns:
            HTML格式的报告内容
        """
        import html
        tweets = tweets or []

        # 为每篇论文生成唯一锚点ID并存储（强制重新生成确保一致性）
        for i, paper in enumerate(papers):
            paper['anchor_id'] = self._generate_paper_anchor(paper, i)

        # CSS样式
        css_style = """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #34495e;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 8px;
                margin-top: 30px;
            }
            h3 {
                color: #16a085;
                margin-top: 20px;
            }
            .stats {
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
            }
            .stats ul {
                margin: 0;
                padding-left: 20px;
            }
            .summary {
                background-color: #e8f4f8;
                border-left: 4px solid #3498db;
                padding: 15px;
                margin: 20px 0;
            }
            .summary strong {
                color: #2980b9;
            }
            .paper {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 15px;
                margin: 15px 0;
                background-color: #fafafa;
            }
            .paper h3 {
                margin-top: 0;
                color: #2c3e50;
            }
            .paper-info {
                color: #666;
                font-size: 0.9em;
                margin: 5px 0;
            }
            .paper-abstract {
                background-color: white;
                padding: 10px;
                border-radius: 3px;
                margin: 10px 0;
                border-left: 3px solid #3498db;
            }
            .tweet {
                border: 1px solid #e1e8ed;
                border-radius: 5px;
                padding: 15px;
                margin: 15px 0;
                background-color: #f7f9fa;
            }
            .tweet-author {
                color: #1da1f2;
                font-weight: bold;
            }
            .tweet-content {
                margin: 10px 0;
                white-space: pre-wrap;
            }
            .cns-badge {
                background-color: #e74c3c;
                color: white;
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 0.8em;
                font-weight: bold;
                margin-left: 5px;
            }
            .high-relevance {
                border-left: 4px solid #27ae60;
            }
            .medium-relevance {
                border-left: 4px solid #f39c12;
            }
            a {
                color: #3498db;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            .separator {
                border-top: 1px solid #ddd;
                margin: 30px 0;
            }
            .emoji {
                font-size: 1.2em;
            }
            .abstract-content {
                margin: 10px 0;
                padding: 10px;
                background-color: white;
                border-radius: 3px;
                line-height: 1.8;
                color: #333;
            }
        </style>
        """

        # HTML开头
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='zh-CN'>",
            "<head>",
            "<meta charset='UTF-8'>",
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"<title>学术内容日报 - {date_str}</title>",
            css_style,
            "</head>",
            "<body>",
            "<div class='container'>"
        ]

        # 标题
        html_parts.append(f"<h1>学术内容日报 - {date_str}</h1>")

        # 研究方向
        html_parts.append("<h2>研究方向</h2>")
        html_parts.append("<ul>")
        for interest in research_interests:
            html_parts.append(f"<li>{html.escape(interest)}</li>")
        html_parts.append("</ul>")

        # 统计信息
        html_parts.append("<div class='stats'>")
        html_parts.append("<h2>统计信息</h2>")
        html_parts.append("<ul>")
        html_parts.append(f"<li>总论文/文章数: {len(papers)}</li>")
        if tweets:
            html_parts.append(f"<li>总推文数: {len(tweets)}</li>")

        # 论文相关性统计
        relevance_stats = {}
        for paper in papers:
            level = paper.get('relevance_level', 'unknown')
            if level != 'unknown':
                relevance_stats[level] = relevance_stats.get(level, 0) + 1

        if relevance_stats:
            html_parts.append("<li>论文相关性分布:<ul>")
            for level in ['high', 'medium', 'low', 'none']:
                if level in relevance_stats:
                    html_parts.append(f"<li>{level}: {relevance_stats[level]}</li>")
            html_parts.append("</ul></li>")

        # 推文相关性统计
        if tweets:
            tweet_stats = {}
            for tweet in tweets:
                level = tweet.get('relevance_level', 'unknown')
                if level != 'unknown':
                    tweet_stats[level] = tweet_stats.get(level, 0) + 1
            if tweet_stats:
                html_parts.append("<li>推文相关性分布:<ul>")
                for level in ['high', 'medium', 'low']:
                    if level in tweet_stats:
                        html_parts.append(f"<li>{level}: {tweet_stats[level]}</li>")
                html_parts.append("</ul></li>")

        html_parts.append("</ul>")
        html_parts.append("</div>")

        # 核心发现摘要
        high_papers = [p for p in papers if p.get('relevance_level') == 'high']
        high_tweets = [t for t in tweets if t.get('relevance_level') == 'high']

        if high_papers or high_tweets:
            html_parts.append("<div class='summary'>")
            html_parts.append("<h2><span class='emoji'>🔍</span> 核心发现速览</h2>")

            # 论文摘要
            if high_papers:
                summary_html = self._generate_topic_summary_html(high_papers)
                html_parts.append(summary_html)

            # Twitter摘要
            if high_tweets:
                twitter_summary_html = self._generate_twitter_summary_html(high_tweets)
                html_parts.append(twitter_summary_html)

            html_parts.append("</div>")

        # 分组论文
        medium_papers = [p for p in papers if p.get('relevance_level') == 'medium']
        low_papers = [p for p in papers if p.get('relevance_level') == 'low']

        # 高相关论文
        if high_papers:
            html_parts.append("<h2>强烈推荐 (高相关性)</h2>")
            for paper in high_papers:
                html_parts.append(self._format_paper_html(paper, 'high'))

        # 中等相关论文
        if medium_papers:
            html_parts.append("<h2>推荐阅读 (中等相关性)</h2>")
            for paper in medium_papers:
                html_parts.append(self._format_paper_html(paper, 'medium'))

        # Twitter推文
        if tweets:
            html_parts.append("<div class='separator'></div>")
            html_parts.append("<h1><span class='emoji'>📱</span> Twitter 学术动态</h1>")

            high_tweets_list = [t for t in tweets if t.get('relevance_level') == 'high']
            medium_tweets_list = [t for t in tweets if t.get('relevance_level') == 'medium']

            if high_tweets_list:
                html_parts.append("<h2>强烈推荐 (高相关性)</h2>")
                for tweet in high_tweets_list:
                    html_parts.append(self._format_tweet_html(tweet))

            if medium_tweets_list:
                html_parts.append("<h2>值得关注 (中等相关性)</h2>")
                for tweet in medium_tweets_list:
                    html_parts.append(self._format_tweet_html(tweet))

        # HTML结尾
        html_parts.append("</div>")
        html_parts.append("</body>")
        html_parts.append("</html>")

        return '\n'.join(html_parts)

    def _generate_topic_summary_html(self, papers: List[Dict]) -> str:
        """生成论文主题摘要的HTML"""
        import html
        import re

        parts = []
        parts.append(f"<p>根据您的研究兴趣，本期为您筛选出 <strong>{len(papers)}篇高相关论文</strong>。以下是核心发现：</p>")

        # 按主题分类
        topic_papers = {}
        for paper in papers:
            interests = paper.get('matched_interests', [])
            source = paper.get('journal', paper.get('primary_category', 'ArXiv'))
            is_cns = any(journal in str(source) for journal in ['Nature', 'Science', 'Cell'])

            if interests:
                for interest in interests:
                    if interest not in topic_papers:
                        topic_papers[interest] = []
                    topic_papers[interest].append((paper, is_cns))

        total_recommended = 0
        max_total = 10

        for topic, topic_papers_list in sorted(topic_papers.items(), key=lambda x: -len(x[1])):
            if total_recommended >= max_total:
                break

            topic_papers_list.sort(key=lambda x: (not x[1], x[0].get('title', '')))
            recommend_count = min(3, len(topic_papers_list), max_total - total_recommended)

            parts.append(f"<p><strong>{html.escape(topic)}</strong>：本期找到{len(topic_papers_list)}篇相关论文，为您重点推荐以下{recommend_count}篇：</p>")
            parts.append("<ol>")

            for paper, is_cns in topic_papers_list[:recommend_count]:
                total_recommended += 1
                title = html.escape(paper.get('title', '未知标题'))
                source = paper.get('journal') if paper.get('journal') else f"ArXiv {paper.get('primary_category', 'unknown')}"

                # 使用预先生成的锚点ID
                anchor = paper.get('anchor_id', 'unknown')

                cns_badge = '<span class="cns-badge">CNS</span>' if is_cns else ''
                brief = paper.get('summary', paper.get('why_relevant', ''))
                if brief:
                    brief = html.escape(brief.split('。')[0].split('.')[0][:100].strip())

                parts.append(f"<li><a href='#{anchor}'>{title}</a> ({html.escape(source)}) {cns_badge}")
                if brief:
                    parts.append(f"<br><small>{brief}</small>")
                parts.append("</li>")

            parts.append("</ol>")

            remaining = len(topic_papers_list) - recommend_count
            if remaining > 0:
                parts.append(f"<p><em>另有{remaining}篇{html.escape(topic)}相关论文，详见下文</em></p>")

        if total_recommended < len(papers):
            parts.append(f"<p><em>其余 {len(papers) - total_recommended} 篇高相关论文详见下文「强烈推荐」部分。</em></p>")

        return '\n'.join(parts)

    def _generate_twitter_summary_html(self, tweets: List[Dict]) -> str:
        """生成Twitter摘要的HTML"""
        import html

        parts = []
        parts.append("<p><strong><span class='emoji'>📱</span> Twitter学术动态</strong></p>")

        # 分析主题
        topics = {}
        topic_keywords = {
            '自动驾驶': ['自动驾驶', 'autonomous driving', 'self-driving', 'Tesla', 'FSD'],
            '大语言模型': ['LLM', 'GPT', 'Claude', 'language model', '大语言模型', '大模型'],
            '强化学习': ['强化学习', 'reinforcement learning', 'RL', 'policy'],
            '具身智能': ['具身', 'embodied', 'robot', '机器人', 'manipulation'],
            'VLM/多模态': ['VLM', 'vision language', '多模态', 'multimodal', 'CLIP'],
        }

        for tweet in tweets:
            text = tweet.get('text', '')
            for topic, kws in topic_keywords.items():
                if any(kw.lower() in text.lower() for kw in kws):
                    if topic not in topics:
                        topics[topic] = []
                    topics[topic].append(tweet)
                    break

        if topics:
            topic_summary = [f"<strong>{html.escape(topic)}</strong>（{len(tweets)}条）"
                           for topic, tweets in sorted(topics.items(), key=lambda x: -len(x[1]))[:3]]
            parts.append(f"<p>本期Twitter学术圈的热点话题包括：{' | '.join(topic_summary)}</p>")

        sample_count = min(3, len(tweets))
        parts.append(f"<p>为您精选{sample_count}条最具代表性的讨论：</p>")
        parts.append("<ol>")

        for tweet in tweets[:sample_count]:
            author = html.escape(tweet.get('author_name', tweet.get('author_username', '未知')))
            text_preview = html.escape(tweet.get('text', '')[:100].strip())
            if len(tweet.get('text', '')) > 100:
                text_preview += '...'

            parts.append(f"<li><strong>@{author}</strong>: {text_preview}")
            if tweet.get('why_relevant'):
                relevance = html.escape(tweet.get('why_relevant', '')[:80])
                parts.append(f"<br><em>{relevance}</em>")
            parts.append("</li>")

        parts.append("</ol>")
        parts.append("<p><em>完整Twitter动态详见下文「Twitter学术动态」部分</em></p>")

        return '\n'.join(parts)

    def _format_paper_html(self, paper: Dict, relevance: str = 'medium') -> str:
        """格式化单篇论文为HTML"""
        import html
        import re
        import urllib.parse

        # 使用预先生成的锚点ID
        title = paper.get('title', '未知标题')
        anchor = paper.get('anchor_id', 'unknown')

        relevance_class = f"{relevance}-relevance"

        parts = [f"<div class='paper {relevance_class}' id='{anchor}'>"]
        parts.append(f"<h3>{html.escape(title)}</h3>")

        # 基本信息
        published = paper.get('published') or paper.get('pub_date') or paper.get('date', '未知')
        parts.append(f"<div class='paper-info'><strong>发布日期:</strong> {html.escape(str(published))}</div>")

        # 作者
        authors = paper.get('authors', [])
        if authors:
            authors_display = ', '.join(authors[:3])
            if len(authors) > 3:
                authors_display += f" 等 ({len(authors)}位作者)"
            parts.append(f"<div class='paper-info'><strong>作者:</strong> {html.escape(authors_display)}</div>")

        # 作者单位（如果有）
        if paper.get('affiliations'):
            parts.append(f"<div class='paper-info'><strong>单位:</strong> {html.escape(paper['affiliations'])}</div>")

        # 期刊/类别
        if paper.get('journal'):
            journal = paper['journal']
            is_cns = any(j in journal for j in ['Nature', 'Science', 'Cell'])
            cns_badge = '<span class="cns-badge">CNS</span>' if is_cns else ''
            parts.append(f"<div class='paper-info'><strong>期刊:</strong> {html.escape(journal)} {cns_badge}</div>")
        elif paper.get('primary_category'):
            parts.append(f"<div class='paper-info'><strong>类别:</strong> {html.escape(paper['primary_category'])}</div>")

        # 相关领域
        if paper.get('matched_interests'):
            interests = ', '.join(paper['matched_interests'])
            parts.append(f"<div class='paper-info'><strong>相关领域:</strong> {html.escape(interests)}</div>")

        # 链接
        if paper.get('url'):
            parts.append(f"<div class='paper-info'><strong>论文链接:</strong> <a href='{html.escape(paper['url'])}' target='_blank'>{html.escape(paper['url'])}</a></div>")
        if paper.get('pdf_url'):
            parts.append(f"<div class='paper-info'><strong>PDF链接:</strong> <a href='{html.escape(paper['pdf_url'])}' target='_blank'>{html.escape(paper['pdf_url'])}</a></div>")


        # 生成唯一ID（用于展开/折叠功能）
        paper_id = anchor

        # 摘要显示格式：核心内容（一句话）+ 完整摘要
        if paper.get('abstract_zh') or paper.get('summary'):
            parts.append("<div class='paper-abstract'>")

            # AI生成的核心内容（显示第一句话作为总结）
            if paper.get('summary'):
                summary = paper['summary']
                # 提取第一句话作为核心内容
                first_sentence = summary.split('。')[0]
                if not first_sentence.endswith('。'):
                    first_sentence = first_sentence.split('.')[0]
                # 限制长度，避免过长
                if len(first_sentence) > 200:
                    first_sentence = first_sentence[:200] + '...'

                parts.append(f"<strong>核心内容:</strong>")
                parts.append(f"<div class='abstract-content'>{html.escape(first_sentence)}...</div>")

            # 中文摘要（显示完整内容）
            if paper.get('abstract_zh'):
                abstract_zh = paper['abstract_zh']
                parts.append(f"<strong>摘要:</strong>")
                parts.append(f"<div class='abstract-content'>{html.escape(abstract_zh)}</div>")

            parts.append("</div>")

        parts.append("</div>")
        return '\n'.join(parts)

    def _format_tweet_html(self, tweet: Dict) -> str:
        """格式化单条推文为HTML"""
        import html

        parts = ["<div class='tweet'>"]

        # 作者
        author = f"@{tweet.get('author_username', 'unknown')}"
        if tweet.get('author_name'):
            author = f"{tweet.get('author_name')} ({author})"
        parts.append(f"<div class='tweet-author'>{html.escape(author)}</div>")

        # 时间
        parts.append(f"<div class='paper-info'>{html.escape(str(tweet.get('created_at', 'unknown')))}</div>")

        # 内容
        parts.append(f"<div class='tweet-content'>{html.escape(tweet.get('text', ''))}</div>")

        # 相关性说明
        if tweet.get('why_relevant'):
            parts.append(f"<div class='paper-info'><strong>相关性:</strong> {html.escape(tweet['why_relevant'])}</div>")

        # 互动数据
        if tweet.get('favorite_count') or tweet.get('retweet_count'):
            parts.append(f"<div class='paper-info'>👍 {tweet.get('favorite_count', 0)} | 🔄 {tweet.get('retweet_count', 0)} | 💬 {tweet.get('reply_count', 0)}</div>")

        # 链接
        if tweet.get('url'):
            parts.append(f"<div class='paper-info'><a href='{html.escape(tweet['url'])}' target='_blank'>查看推文</a></div>")

        parts.append("</div>")
        return '\n'.join(parts)
