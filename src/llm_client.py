"""
通用LLM客户端 - 使用OpenAI官方Python SDK
"""
import os
import asyncio
from typing import Optional
from openai import OpenAI


class LLMClient:
    """LLM客户端，使用OpenAI官方Python SDK"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o",
        max_tokens: int = 4096,
    ):
        """
        初始化LLM客户端

        Args:
            api_key: API密钥
            base_url: API基础URL（可选，默认为OpenAI官方API）
            model: 模型名称
            max_tokens: 最大token数
        """
        self.api_key = (api_key or
                       os.getenv('OPENAI_API_KEY') or
                       os.getenv('API_KEY'))

        if self.api_key:
            self.api_key = self.api_key.strip()

        if not self.api_key:
            raise ValueError("未提供API密钥，请设置 api_key 参数或 OPENAI_API_KEY 环境变量")

        # 设置默认base_url
        if not base_url:
            base_url = "https://api.openai.com/v1"

        self.base_url = base_url
        self.model = model
        self.max_tokens = max_tokens

        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        print(f"✓ 使用 OpenAI API")
        print(f"  - 模型: {self.model}")
        print(f"  - 端点: {self.base_url}")

    async def chat_completion(
        self,
        prompt: str,
        client: Optional[object] = None,  # 保留参数以兼容旧代码，但不使用
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        调用OpenAI API进行对话补全

        Args:
            prompt: 提示词
            client: 废弃参数（保留以兼容旧代码）
            max_tokens: 最大token数（可选，覆盖默认值）
            temperature: 温度参数

        Returns:
            API响应文本
        """
        # 使用asyncio.to_thread将同步调用转为异步
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content
