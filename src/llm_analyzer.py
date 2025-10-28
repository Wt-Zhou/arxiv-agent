"""
使用LLM分析论文相关性 - 两阶段优化版本
使用OpenAI官方Python SDK
"""
import os
import asyncio
import httpx
from typing import Dict, List, Tuple, Optional
from llm_client import LLMClient


class LLMAnalyzer:
    """使用LLM分析论文相关性（两阶段：快速筛选 + 详细分析）"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        max_tokens: int = 4096,
        base_url: Optional[str] = None,
        max_concurrent: int = 5,
        batch_size: int = 25,
        detail_batch_size: int = 8
    ):
        """
        初始化LLM分析器

        Args:
            api_key: API密钥
            model: 使用的模型名称
            max_tokens: 最大token数
            base_url: 自定义API端点 (可选)
            max_concurrent: 最大并发请求数 (默认5)
            batch_size: 第一阶段批量筛选时每批论文数量 (默认25)
            detail_batch_size: 第二阶段批量详细分析时每批论文数量 (默认8)
        """
        # 创建LLM客户端
        self.llm_client = LLMClient(
            api_key=api_key,
            base_url=base_url,
            model=model,
            max_tokens=max_tokens
        )

        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.detail_batch_size = detail_batch_size

    async def _call_api_async(self, prompt: str, client: httpx.AsyncClient, max_tokens: int = None) -> str:
        """
        异步调用LLM API

        Args:
            prompt: 提示词
            client: httpx异步客户端
            max_tokens: 最大token数（如果不指定，使用默认值）

        Returns:
            API响应文本
        """
        return await self.llm_client.chat_completion(
            prompt=prompt,
            client=client,
            max_tokens=max_tokens,
            temperature=0.7
        )

    async def _batch_filter_relevance_async(self, papers_batch: List[Dict], research_interests: List[str], client: httpx.AsyncClient, semaphore: asyncio.Semaphore, research_prompt: str = None) -> List[Tuple[int, str, List[str]]]:
        """
        批量快速筛选论文相关性（第一阶段）

        Args:
            papers_batch: 一批论文
            research_interests: 研究方向列表
            client: httpx异步客户端
            semaphore: 并发控制信号量
            research_prompt: 研究兴趣的详细描述（可选，如果提供则优先使用）

        Returns:
            [(论文索引, 相关性级别, 匹配领域), ...]
        """
        async with semaphore:
            # 构建批量筛选的提示词
            papers_text = ""
            for idx, paper in papers_batch:
                papers_text += f"\n【论文{idx}】\n"
                papers_text += f"标题: {paper['title']}\n"
                papers_text += f"摘要: {paper['abstract'][:800]}...\n"  # 增加摘要长度以获取更多信息

            # 根据是否提供了 research_prompt 来构建不同的用户研究方向描述
            if research_prompt:
                research_description = f"""用户的研究兴趣描述：
{research_prompt}"""
            else:
                research_description = f"""用户的研究方向：
{', '.join(research_interests)}"""

            prompt = f"""你是一个AI研究助手。请判断以下论文是否与用户的研究方向相关。

{research_description}

{papers_text}

请对每篇论文按以下格式回答（务必包含论文编号）：

【论文X】相关性: 高/中/低/无关  |  匹配领域: XXX, XXX（如果无关则写"无"）

相关性判断标准：
- **高相关**：论文核心内容直接服务于用户的研究方向，方法和应用场景高度契合
- **中相关**：论文涉及用户关注的技术或方法，虽然应用场景不完全相同，但有借鉴价值或潜在迁移可能
- **低相关**：论文提到了相关的概念或技术，但不是核心内容，仅有间接联系
- **无关**：论文内容与用户研究方向完全无关

重要提示：
- 必须包含【论文X】标记
- 采用**宽松的标准**：只要论文涉及相关技术、方法或应用场景，即使不是完全匹配，也应标记为"中相关"或"高相关"
- 特别关注：机器人、自动驾驶、视觉、语言、多模态、强化学习、世界模型等相关论文
- 顶级期刊（Nature、Science、Cell等）的创新方法通常有迁移价值，应给予更高评分
- 不要过于严格，宁可多筛选出一些潜在相关的论文"""

            try:
                response_text = await self._call_api_async(prompt, client, max_tokens=3072)

                # 解析批量响应
                results = []
                lines = response_text.strip().split('\n')

                for line in lines:
                    line = line.strip()
                    if '【论文' in line and '】' in line:
                        try:
                            # 提取论文编号
                            paper_idx = int(line.split('【论文')[1].split('】')[0])

                            # 提取相关性
                            relevance = 'none'
                            if '相关性' in line or '相关度' in line:
                                if '高' in line:
                                    relevance = 'high'
                                elif '中' in line:
                                    relevance = 'medium'
                                elif '低' in line:
                                    relevance = 'low'
                                elif '无关' in line:
                                    relevance = 'none'

                            # 提取匹配领域
                            matched = []
                            if '匹配领域' in line or '相关领域' in line:
                                parts = line.split('匹配领域:' if '匹配领域' in line else '相关领域:')
                                if len(parts) > 1:
                                    fields_text = parts[1].strip()
                                    if fields_text and '无' not in fields_text:
                                        matched = [f.strip() for f in fields_text.replace('、', ',').split(',') if f.strip()]

                            results.append((paper_idx, relevance, matched))
                        except (ValueError, IndexError) as e:
                            print(f"  ⚠️  解析论文结果时出错: {line[:50]}... - {e}")
                            continue

                return results

            except Exception as e:
                import traceback
                error_msg = f"{type(e).__name__}: {str(e)}"
                print(f"  ⚠️  批量筛选时出错: {error_msg}")
                print(f"  详细错误信息:\n{traceback.format_exc()}")
                # 返回所有论文标记为unknown
                return [(idx, 'unknown', []) for idx, _ in papers_batch]

    async def _batch_analyze_detailed_async(self, papers_batch: List[Tuple[int, Dict]], client: httpx.AsyncClient, semaphore: asyncio.Semaphore) -> List[Tuple[int, Dict]]:
        """
        批量详细分析论文（第二阶段）

        Args:
            papers_batch: 一批论文 [(索引, 论文), ...]
            client: httpx异步客户端
            semaphore: 并发控制信号量

        Returns:
            [(论文索引, 详细分析结果), ...]
        """
        async with semaphore:
            # 构建批量详细分析的提示词
            papers_text = ""
            for idx, paper in papers_batch:
                authors_str = ', '.join(paper.get('authors', [])[:5])
                if len(paper.get('authors', [])) > 5:
                    authors_str += f' 等 ({len(paper.get("authors", []))}位作者)'

                papers_text += f"\n{'='*60}\n"
                papers_text += f"【论文{idx}】\n"
                papers_text += f"标题：{paper['title']}\n"
                papers_text += f"作者：{authors_str}\n"
                papers_text += f"摘要（英文）：{paper['abstract']}\n"

            prompt = f"""请对以下论文进行详细分析。

{papers_text}

请对每篇论文按以下格式回答（务必包含论文编号）：

【论文X】
1. 作者单位：XXX（如果摘要中提到了作者单位，请列出；如果没有提到，写"未在摘要中说明"）
2. 摘要中文翻译：XXX（将上述英文摘要完整翻译成中文，保持学术性和准确性）
3. 核心内容：XXX（1-2句话概括论文的核心创新点和贡献）

注意：
- 必须包含【论文X】标记
- 作者单位只从摘要中提取，不要推测
- 中文翻译要完整、准确、流畅
- 核心内容要突出创新点"""

            try:
                response_text = await self._call_api_async(prompt, client, max_tokens=4096)

                # 解析批量响应
                results = []
                current_paper_idx = None
                current_data = {'affiliations': None, 'abstract_zh': '', 'summary': ''}
                current_section = None
                current_content = []

                lines = response_text.strip().split('\n')

                for line in lines:
                    line_stripped = line.strip()

                    # 检测新论文开始
                    if '【论文' in line_stripped and '】' in line_stripped:
                        # 保存上一篇论文的数据
                        if current_paper_idx is not None:
                            if current_section and current_content:
                                content_text = '\n'.join(current_content).strip()
                                if current_section == 'abstract_zh':
                                    current_data['abstract_zh'] = content_text
                                elif current_section == 'summary':
                                    current_data['summary'] = content_text
                                elif current_section == 'affiliations' and '未在摘要中说明' not in content_text:
                                    current_data['affiliations'] = content_text
                            results.append((current_paper_idx, current_data.copy()))

                        # 开始新论文
                        try:
                            current_paper_idx = int(line_stripped.split('【论文')[1].split('】')[0])
                            current_data = {'affiliations': None, 'abstract_zh': '', 'summary': ''}
                            current_section = None
                            current_content = []
                        except (ValueError, IndexError):
                            continue

                    # 检测章节
                    elif current_paper_idx is not None:
                        if '作者单位' in line_stripped or ('单位' in line_stripped and ':' in line_stripped):
                            if current_section and current_content:
                                content_text = '\n'.join(current_content).strip()
                                if current_section == 'abstract_zh':
                                    current_data['abstract_zh'] = content_text
                                elif current_section == 'summary':
                                    current_data['summary'] = content_text
                            current_section = 'affiliations'
                            current_content = []
                            if '：' in line_stripped or ':' in line_stripped:
                                separator = '：' if '：' in line_stripped else ':'
                                content = line_stripped.split(separator, 1)[-1].strip()
                                if content and '未在摘要中说明' not in content:
                                    current_data['affiliations'] = content

                        elif '摘要中文翻译' in line_stripped or ('摘要' in line_stripped and '翻译' in line_stripped):
                            if current_section and current_content:
                                content_text = '\n'.join(current_content).strip()
                                if current_section == 'summary':
                                    current_data['summary'] = content_text
                                elif current_section == 'affiliations' and '未在摘要中说明' not in content_text:
                                    current_data['affiliations'] = content_text
                            current_section = 'abstract_zh'
                            current_content = []
                            if '：' in line_stripped:
                                content = line_stripped.split('：', 1)[-1].strip()
                                if content:
                                    current_content.append(content)

                        elif '核心内容' in line_stripped or ('核心' in line_stripped and '创新' in line_stripped):
                            if current_section and current_content:
                                content_text = '\n'.join(current_content).strip()
                                if current_section == 'abstract_zh':
                                    current_data['abstract_zh'] = content_text
                                elif current_section == 'affiliations' and '未在摘要中说明' not in content_text:
                                    current_data['affiliations'] = content_text
                            current_section = 'summary'
                            current_content = []
                            if '：' in line_stripped:
                                content = line_stripped.split('：', 1)[-1].strip()
                                if content:
                                    current_content.append(content)

                        elif current_section and line_stripped and not line_stripped.startswith(('1.', '2.', '3.', '注意', '=')):
                            current_content.append(line_stripped)

                # 保存最后一篇论文
                if current_paper_idx is not None:
                    if current_section and current_content:
                        content_text = '\n'.join(current_content).strip()
                        if current_section == 'abstract_zh':
                            current_data['abstract_zh'] = content_text
                        elif current_section == 'summary':
                            current_data['summary'] = content_text
                        elif current_section == 'affiliations' and '未在摘要中说明' not in content_text:
                            current_data['affiliations'] = content_text
                    results.append((current_paper_idx, current_data))

                return results

            except Exception as e:
                import traceback
                error_msg = f"{type(e).__name__}: {str(e)}"
                print(f"  ⚠️  批量详细分析时出错: {error_msg}")
                print(f"  详细错误信息:\n{traceback.format_exc()}")
                # 返回所有论文的空结果
                return [(idx, {'affiliations': None, 'abstract_zh': '', 'summary': '', 'reason': f'分析失败: {error_msg}'}) for idx, _ in papers_batch]


    async def two_stage_analyze_papers_async(self, papers: List[Dict], research_interests: List[str], research_prompt: str = None) -> List[Dict]:
        """
        两阶段异步分析论文（优化版）

        第一阶段：批量快速筛选相关性（每批25篇，只判断相关性）
        第二阶段：对相关论文进行详细分析（翻译、单位等）

        Args:
            papers: 论文列表
            research_interests: 研究方向列表
            research_prompt: 研究兴趣的详细描述（可选，如果提供则优先使用）

        Returns:
            带有分析结果的论文列表
        """
        total = len(papers)
        print(f"\n{'='*60}")
        print(f"🚀 第一阶段：批量快速筛选 {total} 篇论文的相关性")
        print(f"   - 批次大小: {self.batch_size} 篇/批")
        print(f"   - 并发数: {self.max_concurrent}")
        if research_prompt:
            print(f"   - 使用模式: 自定义研究兴趣描述")
        else:
            print(f"   - 使用模式: 关键词列表")
        print(f"{'='*60}")

        # 第一阶段：批量筛选相关性
        semaphore = asyncio.Semaphore(self.max_concurrent)
        all_papers_with_relevance = papers.copy()

        async with httpx.AsyncClient(
            limits=httpx.Limits(max_connections=self.max_concurrent * 2, max_keepalive_connections=self.max_concurrent),
            timeout=httpx.Timeout(60.0, connect=10.0)
        ) as client:
            # 将论文分批
            batches = []
            for i in range(0, total, self.batch_size):
                batch = [(j, papers[j]) for j in range(i, min(i + self.batch_size, total))]
                batches.append(batch)

            print(f"分为 {len(batches)} 个批次进行筛选...\n")

            # 并发处理所有批次
            tasks = [
                self._batch_filter_relevance_async(batch, research_interests, client, semaphore, research_prompt)
                for batch in batches
            ]

            batch_results = []
            for i, task in enumerate(asyncio.as_completed(tasks), 1):
                result = await task
                batch_results.extend(result)
                print(f"  [{i}/{len(batches)}] ✓ 完成批次 {i}")

            # 合并筛选结果到论文数据
            for paper_idx, relevance, matched in batch_results:
                if 0 <= paper_idx < len(all_papers_with_relevance):
                    all_papers_with_relevance[paper_idx]['relevance_level'] = relevance
                    all_papers_with_relevance[paper_idx]['matched_interests'] = matched
                    all_papers_with_relevance[paper_idx]['is_relevant'] = relevance in ['high', 'medium']

            # 统计相关论文
            relevant_papers = [p for p in all_papers_with_relevance if p.get('is_relevant', False)]
            print(f"\n✅ 第一阶段完成！筛选出 {len(relevant_papers)}/{total} 篇相关论文")

            if not relevant_papers:
                print("未找到相关论文，跳过第二阶段")
                return all_papers_with_relevance

            # 第二阶段：批量详细分析相关论文
            print(f"\n{'='*60}")
            print(f"🔍 第二阶段：批量详细分析 {len(relevant_papers)} 篇相关论文")
            print(f"   - 批次大小: {self.detail_batch_size} 篇/批")
            print(f"{'='*60}\n")

            # 为每篇论文创建索引映射
            paper_index_map = {id(paper): i for i, paper in enumerate(relevant_papers)}

            # 将相关论文分批
            detail_batches = []
            for i in range(0, len(relevant_papers), self.detail_batch_size):
                batch = [(paper_index_map[id(relevant_papers[j])], relevant_papers[j])
                         for j in range(i, min(i + self.detail_batch_size, len(relevant_papers)))]
                detail_batches.append(batch)

            print(f"分为 {len(detail_batches)} 个批次进行详细分析...\n")

            # 并发处理所有批次
            detail_tasks = [
                self._batch_analyze_detailed_async(batch, client, semaphore)
                for batch in detail_batches
            ]

            all_details = []
            for i, task in enumerate(asyncio.as_completed(detail_tasks), 1):
                batch_details = await task
                all_details.extend(batch_details)
                print(f"  [{i}/{len(detail_batches)}] ✓ 完成批次 {i} ({len(batch_details)} 篇)")

            # 更新论文详细信息
            for paper_idx, details in all_details:
                if 0 <= paper_idx < len(relevant_papers):
                    relevant_papers[paper_idx].update(details)

        print(f"\n✅ 分析完成！")
        print(f"   - 总论文数: {total}")
        print(f"   - 相关论文: {len(relevant_papers)}")
        print(f"   - 高相关: {sum(1 for p in all_papers_with_relevance if p.get('relevance_level') == 'high')}")
        print(f"   - 中相关: {sum(1 for p in all_papers_with_relevance if p.get('relevance_level') == 'medium')}")

        return all_papers_with_relevance

    def filter_relevant_papers(self, analyzed_papers: List[Dict], min_relevance: str = 'medium') -> List[Dict]:
        """
        过滤出相关的论文

        Args:
            analyzed_papers: 已分析的论文列表
            min_relevance: 最小相关性级别 ('high', 'medium', 'low')

        Returns:
            相关论文列表
        """
        relevance_order = {'high': 3, 'medium': 2, 'low': 1, 'none': 0, 'unknown': 0}
        min_level = relevance_order.get(min_relevance, 2)

        relevant_papers = [
            paper for paper in analyzed_papers
            if relevance_order.get(paper.get('relevance_level', 'unknown'), 0) >= min_level
        ]

        # 按相关性排序
        relevant_papers.sort(
            key=lambda x: relevance_order.get(x.get('relevance_level', 'unknown'), 0),
            reverse=True
        )

        return relevant_papers
