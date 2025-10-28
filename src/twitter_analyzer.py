"""
Twitter内容分析模块
使用LLM分析推文的相关性（使用OpenAI官方Python SDK）
"""
import asyncio
import httpx
from typing import List, Dict, Optional
from llm_client import LLMClient


class TwitterAnalyzer:
    """Twitter内容分析器"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        max_tokens: int = 4096,
        base_url: Optional[str] = None,
        max_concurrent: int = 5
    ):
        """
        初始化分析器

        Args:
            api_key: API密钥
            model: 模型名称
            max_tokens: 最大token数
            base_url: 自定义API端点
            max_concurrent: 最大并发请求数
        """
        self.llm_client = LLMClient(
            api_key=api_key,
            base_url=base_url,
            model=model,
            max_tokens=max_tokens
        )
        self.max_concurrent = max_concurrent

    async def _call_api_async(self, prompt: str, client: httpx.AsyncClient, max_tokens: int = None) -> str:
        """调用LLM API"""
        return await self.llm_client.chat_completion(
            prompt=prompt,
            client=client,
            max_tokens=max_tokens,
            temperature=0.7
        )

    async def analyze_tweets_async(self, tweets: List[Dict], research_interests: List[str] = None,
                                   research_prompt: str = None) -> List[Dict]:
        """
        异步分析推文的相关性

        Args:
            tweets: 推文列表
            research_interests: 研究方向列表
            research_prompt: 研究兴趣描述

        Returns:
            带有分析结果的推文列表
        """
        if not tweets:
            return []

        print(f"\n正在分析 {len(tweets)} 条推文的相关性...")

        # 构建研究方向描述
        if research_prompt:
            research_description = f"用户的研究兴趣：\n{research_prompt}"
        else:
            research_description = f"用户的研究方向：{', '.join(research_interests)}"

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async with httpx.AsyncClient(
            limits=httpx.Limits(max_connections=self.max_concurrent * 2,
                              max_keepalive_connections=self.max_concurrent),
            timeout=httpx.Timeout(60.0, connect=10.0)
        ) as client:
            # 分批处理（每批10条）
            batch_size = 10
            batches = []
            for i in range(0, len(tweets), batch_size):
                batch = tweets[i:min(i + batch_size, len(tweets))]
                batches.append(batch)

            print(f"分为 {len(batches)} 个批次进行分析...\n")

            tasks = [
                self._analyze_tweet_batch_async(batch, research_description, client, semaphore)
                for batch in batches
            ]

            all_results = []
            for i, task in enumerate(asyncio.as_completed(tasks), 1):
                results = await task
                all_results.extend(results)
                print(f"  [{i}/{len(batches)}] ✓ 完成批次 {i}")

        # 合并分析结果到推文
        for i, tweet in enumerate(tweets):
            if i < len(all_results):
                tweet.update(all_results[i])

        # 过滤相关推文
        relevant_tweets = [t for t in tweets if t.get('is_relevant', False)]

        print(f"\n✅ 分析完成！")
        print(f"   - 总推文数: {len(tweets)}")
        print(f"   - 相关推文: {len(relevant_tweets)}")

        high_rel = sum(1 for t in tweets if t.get('relevance_level') == 'high')
        medium_rel = sum(1 for t in tweets if t.get('relevance_level') == 'medium')
        print(f"   - 高相关: {high_rel}")
        print(f"   - 中相关: {medium_rel}")

        return tweets

    async def _analyze_tweet_batch_async(self, tweets_batch: List[Dict], research_description: str,
                                        client: httpx.AsyncClient, semaphore: asyncio.Semaphore) -> List[Dict]:
        """批量分析推文"""
        async with semaphore:
            # 构建批量分析提示词
            tweets_text = ""
            for i, tweet in enumerate(tweets_batch):
                tweets_text += f"\n【推文{i}】\n"
                tweets_text += f"作者: @{tweet['author_username']} ({tweet['author_name']})\n"
                tweets_text += f"粉丝数: {tweet['author_followers']}\n"
                tweets_text += f"内容: {tweet['text']}\n"
                tweets_text += f"互动: 👍{tweet['favorite_count']} 🔄{tweet['retweet_count']} 💬{tweet['reply_count']}\n"

            prompt = f"""你是一个AI研究助手。请判断以下Twitter推文是否与用户的研究方向相关。

{research_description}

{tweets_text}

请对每条推文按以下格式回答：

【推文X】相关性: 高/中/低/无关  |  原因: XXX（1-2句话说明为什么相关或不相关）

注意：
- 必须包含【推文X】标记
- 技术讨论、论文分享、会议信息、研究动态都可能相关
- 业界新闻如果与研究方向相关也算相关"""

            try:
                response_text = await self._call_api_async(prompt, client, max_tokens=2048)

                # 解析响应
                results = []
                lines = response_text.strip().split('\n')

                for line in lines:
                    line = line.strip()
                    if '【推文' in line and '】' in line:
                        try:
                            # 提取推文编号
                            tweet_idx = int(line.split('【推文')[1].split('】')[0])

                            # 提取相关性
                            relevance = 'none'
                            if '相关性' in line:
                                if '高' in line.split('相关性')[1].split('|')[0]:
                                    relevance = 'high'
                                elif '中' in line.split('相关性')[1].split('|')[0]:
                                    relevance = 'medium'
                                elif '低' in line.split('相关性')[1].split('|')[0]:
                                    relevance = 'low'

                            # 提取原因
                            reason = ''
                            if '原因' in line:
                                reason = line.split('原因:')[-1].strip()

                            results.append({
                                'relevance_level': relevance,
                                'is_relevant': relevance in ['high', 'medium'],
                                'relevance_reason': reason
                            })

                        except (ValueError, IndexError) as e:
                            results.append({
                                'relevance_level': 'unknown',
                                'is_relevant': False,
                                'relevance_reason': '解析失败'
                            })

                # 确保结果数量与推文数量一致
                while len(results) < len(tweets_batch):
                    results.append({
                        'relevance_level': 'unknown',
                        'is_relevant': False,
                        'relevance_reason': '未分析'
                    })

                return results

            except Exception as e:
                print(f"  ⚠️  批量分析推文时出错: {e}")
                return [{
                    'relevance_level': 'unknown',
                    'is_relevant': False,
                    'relevance_reason': f'分析失败: {e}'
                } for _ in tweets_batch]
