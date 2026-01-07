#!/usr/bin/env python3
"""
测试不同的 API 端点格式
"""
import asyncio
import httpx

API_KEY = "cr_ffb35f4cce250becb75e629899c0f281555fcde4602fb7f92083ec3da10af4dd"
MODEL = "claude-sonnet-4-5-20250929"

# 常见的端点格式
ENDPOINTS_TO_TEST = [
    "https://leyitop.top/api",
    "https://leyitop.top/api/chat/completions",
    "https://leyitop.top/api/v1/chat/completions",
    "https://leyitop.top/v1/chat/completions",
    "https://leyitop.top/chat/completions",
]


async def test_endpoint(endpoint: str):
    """测试单个端点"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "max_tokens": 50,
        "temperature": 0.7,
        "messages": [{"role": "user", "content": "Hello"}]
    }

    print(f"\n测试端点: {endpoint}")
    print("-" * 60)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(endpoint, json=data, headers=headers)

            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功！")
                print(f"响应: {result}")
                return True
            else:
                print(f"❌ 失败")
                print(f"错误: {response.text[:200]}")
                return False

    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False


async def main():
    """主函数"""
    print("=" * 60)
    print("测试不同的 API 端点格式")
    print("=" * 60)

    for endpoint in ENDPOINTS_TO_TEST:
        success = await test_endpoint(endpoint)
        if success:
            print(f"\n🎉 找到正确的端点: {endpoint}")
            break

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(main())
