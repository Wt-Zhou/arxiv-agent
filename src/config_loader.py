"""
配置文件加载器
"""
import os
import yaml
from typing import Dict, Any


class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置加载器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件

        Returns:
            配置字典
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return config

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置项名称
            default: 默认值

        Returns:
            配置值
        """
        return self.config.get(key, default)

    def get_research_interests(self) -> list:
        """获取研究方向列表"""
        return self.get('research_interests', [])

    def get_research_prompt(self) -> str:
        """获取研究兴趣的详细描述"""
        prompt = self.get('research_prompt', None)
        # 如果prompt存在且不为空字符串，返回去除首尾空白后的内容
        if prompt and isinstance(prompt, str) and prompt.strip():
            return prompt.strip()
        return None

    def get_arxiv_categories(self) -> list:
        """获取arxiv类别列表"""
        # 优先从sources.arxiv.categories读取
        arxiv_config = self.get('sources', {}).get('arxiv', {})
        categories = arxiv_config.get('categories', None)
        if categories:
            return categories
        # 向后兼容旧配置
        return self.get('arxiv_categories', [])

    def get_max_results(self) -> int:
        """获取最大结果数"""
        # 优先从sources.arxiv.max_results读取
        arxiv_config = self.get('sources', {}).get('arxiv', {})
        max_results = arxiv_config.get('max_results', None)
        if max_results:
            try:
                return int(max_results)
            except (ValueError, TypeError) as e:
                print(f"⚠️  Warning: Invalid max_results value '{max_results}' ({type(max_results).__name__}), using default 100")
                print(f"   Error: {e}")
                return 100
        # 向后兼容旧配置
        return int(self.get('max_results', 100))

    def get_days_back(self) -> int:
        """获取搜索天数（ArXiv）"""
        # 优先从sources.arxiv.days_back读取
        arxiv_config = self.get('sources', {}).get('arxiv', {})
        days_back = arxiv_config.get('days_back', None)
        if days_back:
            try:
                return int(days_back)
            except (ValueError, TypeError) as e:
                print(f"⚠️  Warning: Invalid days_back value '{days_back}' ({type(days_back).__name__}), using default 1")
                print(f"   Error: {e}")
                return 1
        # 向后兼容旧配置
        return int(self.get('days_back', 1))

    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.get('model', 'gpt-4o')

    def get_max_tokens(self) -> int:
        """获取最大token数"""
        return self.get('max_tokens', 4096)

    def get_output_dir(self) -> str:
        """获取输出目录"""
        return self.get('output_dir', 'reports')

    def get_api_base_url(self) -> str:
        """获取API端点（默认为OpenAI官方API）"""
        return self.get('base_url', 'https://api.openai.com/v1')

    def get_api_key(self) -> str:
        """获取API密钥（优先从环境变量读取）"""
        # 优先从环境变量读取
        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('API_KEY')
        if api_key:
            return api_key.strip()

        # 其次从配置文件读取
        api_key = self.get('api_key', None)
        return api_key.strip() if api_key else None

    def get_max_concurrent(self) -> int:
        """获取最大并发请求数"""
        max_concurrent = self.get('max_concurrent', 5)
        try:
            return int(max_concurrent)
        except (ValueError, TypeError) as e:
            print(f"⚠️  Warning: Invalid max_concurrent value '{max_concurrent}' ({type(max_concurrent).__name__}), using default 5")
            print(f"   Error: {e}")
            return 5

    def get_batch_size(self) -> int:
        """获取批量筛选时每批论文数量"""
        return self.get('batch_size', 25)

    def get_detail_batch_size(self) -> int:
        """获取详细分析时每批论文数量"""
        return self.get('detail_batch_size', 8)

    def get_min_relevance(self) -> str:
        """获取最小相关性级别"""
        return self.get('min_relevance', 'medium')

    def get_email_config(self) -> Dict[str, Any]:
        """获取邮件配置（支持环境变量覆盖）"""
        email_config = self.get('email', {}).copy()

        # 从环境变量覆盖敏感信息
        if os.getenv('EMAIL_SENDER'):
            email_config['sender_email'] = os.getenv('EMAIL_SENDER')
        if os.getenv('EMAIL_PASSWORD'):
            email_config['sender_password'] = os.getenv('EMAIL_PASSWORD')
        if os.getenv('EMAIL_RECEIVER'):
            email_config['receiver_email'] = os.getenv('EMAIL_RECEIVER')

        return email_config

    def is_email_enabled(self) -> bool:
        """判断是否启用邮件发送"""
        email_config = self.get_email_config()
        return email_config.get('enabled', False)

    def get_twitter_config(self) -> Dict[str, Any]:
        """获取Twitter配置（支持环境变量覆盖）"""
        # 从新配置结构读取（sources.twitter）
        source_twitter = self.get('sources', {}).get('twitter', {}) or {}
        # 从顶层twitter配置读取（bearer_token等）
        top_twitter = self.get('twitter', {}) or {}

        # 合并配置（sources.twitter优先）
        twitter_config = {**top_twitter, **source_twitter}

        # 从环境变量覆盖敏感信息
        if os.getenv('TWITTER_USERNAME'):
            twitter_config['username'] = os.getenv('TWITTER_USERNAME')
        if os.getenv('TWITTER_EMAIL'):
            twitter_config['email'] = os.getenv('TWITTER_EMAIL')
        if os.getenv('TWITTER_PASSWORD'):
            twitter_config['password'] = os.getenv('TWITTER_PASSWORD')

        return twitter_config

    def is_twitter_enabled(self) -> bool:
        """判断是否启用Twitter功能"""
        twitter_config = self.get_twitter_config()
        return twitter_config.get('enabled', False)

    def get_enabled_sources(self) -> list:
        """获取启用的数据源列表"""
        sources = []

        # ArXiv 默认启用
        if self.get('sources', {}).get('arxiv', {}).get('enabled', True):
            sources.append('arxiv')

        # CNS 期刊
        if self.get('sources', {}).get('journals', {}).get('enabled', False):
            sources.append('journals')

        # Twitter
        if self.get('sources', {}).get('twitter', {}).get('enabled', False):
            sources.append('twitter')

        return sources

    def get_journal_config(self) -> Dict[str, Any]:
        """获取期刊配置"""
        return self.get('sources', {}).get('journals', {})
