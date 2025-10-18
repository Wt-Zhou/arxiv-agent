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

    def generate_report(self, papers: List[Dict], research_interests: List[str]) -> str:
        """
        生成论文报告

        Args:
            papers: 论文列表（已包含分析结果）
            research_interests: 研究方向列表

        Returns:
            报告文件路径
        """
        # 生成文件名
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"arxiv_papers_{date_str}.md"
        filepath = os.path.join(self.output_dir, filename)

        # 生成报告内容
        content = self._generate_content(papers, research_interests, date_str)

        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"报告已生成: {filepath}")
        return filepath

    def _generate_content(self, papers: List[Dict], research_interests: List[str], date_str: str) -> str:
        """
        生成报告内容

        Args:
            papers: 论文列表
            research_interests: 研究方向列表
            date_str: 日期字符串

        Returns:
            Markdown格式的报告内容
        """
        lines = []

        # 标题
        lines.append(f"# ArXiv 论文日报 - {date_str}\n")

        # 研究方向
        lines.append("## 研究方向\n")
        for interest in research_interests:
            lines.append(f"- {interest}")
        lines.append("")

        # 统计信息
        lines.append("## 统计信息\n")
        lines.append(f"- 总论文数: {len(papers)}")

        # 按相关性级别统计（仅当有分析结果时显示）
        relevance_stats = {}
        for paper in papers:
            level = paper.get('relevance_level', 'unknown')
            if level != 'unknown':  # 只统计已分析的论文
                relevance_stats[level] = relevance_stats.get(level, 0) + 1

        if relevance_stats:  # 只有当有已分析的论文时才显示相关性分布
            lines.append("- 相关性分布:")
            for level in ['high', 'medium', 'low', 'none']:
                if level in relevance_stats:
                    lines.append(f"  - {level}: {relevance_stats[level]}")

        lines.append("")

        # 按相关性分组
        high_papers = [p for p in papers if p.get('relevance_level') == 'high']
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

        return '\n'.join(lines)

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
        lines.append(f"### {paper['title']}\n")

        # 基本信息
        if paper.get('updated') and paper.get('updated') != paper['published']:
            lines.append(f"**发布日期:** {paper['published']} (更新: {paper['updated']})")
        else:
            lines.append(f"**发布日期:** {paper['published']}")

        # 作者和单位
        authors_display = ', '.join(paper['authors'][:3])
        if len(paper['authors']) > 3:
            authors_display += f" 等 ({len(paper['authors'])}位作者)"
        lines.append(f"**作者:** {authors_display}")

        # 作者单位（如果有）
        if paper.get('affiliations'):
            lines.append(f"**单位:** {paper['affiliations']}")

        lines.append(f"**类别:** {paper['primary_category']}")

        # 链接
        lines.append(f"**论文链接:** {paper['url']}")
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
