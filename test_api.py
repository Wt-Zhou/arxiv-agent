#!/usr/bin/env python3
"""
快速测试 API 连接
"""
import asyncio
import httpx
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config_loader import ConfigLoader
from llm_client import LLMClient


async def test_api():
    """测试 API 连接"""
    print("=" * 60)
    print("测试 API 连接")
    print("=" * 60)

    # 加载配置
    config = ConfigLoader('config.yaml')

    api_type = config.get_api_type()
    api_key = config.get_api_key()
    api_base_url = config.get_api_base_url()
    model = config.get_model_name()
    max_tokens = config.get_max_tokens()

    print(f"\n配置信息:")
    print(f"  API 类型: {api_type}")
    print(f"  API 端点: {api_base_url}")
    print(f"  模型: {model}")
    print(f"  Max Tokens: {max_tokens}")
    print(f"  API 密钥前缀: {api_key[:15]}..." if len(api_key) > 15 else f"  API 密钥: {api_key}")

    # 创建 LLM 客户端
    try:
        llm_client = LLMClient(
            api_type=api_type,
            api_key=api_key,
            base_url=api_base_url,
            model=model,
            max_tokens=max_tokens
        )

        print(f"\n✓ LLM 客户端初始化成功")

    except Exception as e:
        print(f"\n❌ LLM 客户端初始化失败: {e}")
        return

    # 测试简单的 API 调用
    print(f"\n开始测试 API 调用...")
    print(f"发送测试提示词: 'Hello, please respond with \"API test successful!\"'")

    try:
        async with httpx.AsyncClient() as client:
            response = await llm_client.chat_completion(
                prompt='Hello, please respond with "API test successful!"',
                client=client,
                max_tokens=50,
                temperature=0.7
            )

            print(f"\n✅ API 调用成功!")
            print(f"\n响应内容:")
            print(f"  {response}")

    except Exception as e:
        print(f"\n❌ API 调用失败:")
        print(f"  {e}")
        return

    print(f"\n{'=' * 60}")
    print("测试完成！API 配置正确，可以正常使用。")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(test_api())
