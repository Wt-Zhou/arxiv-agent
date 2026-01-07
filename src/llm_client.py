"""
通用LLM客户端 - 支持多种API提供商
"""
import os
import httpx
from typing import Optional, Dict, Any


class LLMClient:
    """通用LLM客户端，支持 Anthropic 和 OpenAI 兼容的 API"""

    def __init__(
        self,
        api_type: str = "anthropic",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 1024,
    ):
        """
        初始化LLM客户端

        Args:
            api_type: API类型 ("anthropic" 或 "openai")
            api_key: API密钥
            base_url: API基础URL（可选）
            model: 模型名称
            max_tokens: 最大token数
        """
        self.api_type = api_type.lower()

        # 安全地获取 API key
        self.api_key = (api_key or
                       os.getenv('API_KEY') or
                       os.getenv('ANTHROPIC_API_KEY') or
                       os.getenv('OPENAI_API_KEY'))

        if self.api_key:
            self.api_key = self.api_key.strip()

        if not self.api_key:
            raise ValueError(f"未提供API密钥，请设置 api_key 参数或环境变量")

        # 设置默认base_url (处理空字符串的情况)
        self.base_url = base_url.strip() if base_url else None

        if not self.base_url:
            if self.api_type == "anthropic":
                self.base_url = "https://api.anthropic.com"
            elif self.api_type == "openai":
                self.base_url = "https://api.openai.com/v1"

        self.model = model
        self.max_tokens = max_tokens

        print(f"✓ 使用 {self.api_type.upper()} API")
        print(f"  - 模型: {self.model}")
        print(f"  - 端点: {self.base_url}")

    async def chat_completion(
        self,
        prompt: str,
        client: httpx.AsyncClient,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        调用LLM API进行对话补全

        Args:
            prompt: 提示词
            client: httpx异步客户端
            max_tokens: 最大token数（可选，覆盖默认值）
            temperature: 温度参数

        Returns:
            API响应文本
        """
        if self.api_type == "anthropic":
            return await self._call_anthropic(prompt, client, max_tokens, temperature)
        elif self.api_type == "openai":
            return await self._call_openai(prompt, client, max_tokens, temperature)
        else:
            raise ValueError(f"不支持的API类型: {self.api_type}")

    async def _call_anthropic(
        self,
        prompt: str,
        client: httpx.AsyncClient,
        max_tokens: Optional[int],
        temperature: float,
    ) -> str:
        """调用 Anthropic Claude API"""
        endpoint = f"{self.base_url}/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = await client.post(endpoint, json=data, headers=headers, timeout=60.0)

        if response.status_code == 200:
            result = response.json()
            return result['content'][0]['text']
        else:
            error_msg = f"Anthropic API错误: {response.status_code} - {response.text[:500]}"
            error_msg += f"\n请求端点: {endpoint}"
            error_msg += f"\n模型: {self.model}"
            error_msg += f"\nAPI密钥前缀: {self.api_key[:10]}..." if len(self.api_key) > 10 else ""
            raise Exception(error_msg)

    async def _call_openai(
        self,
        prompt: str,
        client: httpx.AsyncClient,
        max_tokens: Optional[int],
        temperature: float,
    ) -> str:
        """调用 OpenAI 兼容 API（支持国产模型）"""
        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = await client.post(endpoint, json=data, headers=headers, timeout=60.0)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"OpenAI API错误: {response.status_code} - {response.text[:200]}")
