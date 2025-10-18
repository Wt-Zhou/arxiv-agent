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

    def get_arxiv_categories(self) -> list:
        """获取arxiv类别列表"""
        return self.get('arxiv_categories', [])

    def get_max_results(self) -> int:
        """获取最大结果数"""
        return self.get('max_results', 100)

    def get_days_back(self) -> int:
        """获取搜索天数"""
        return self.get('days_back', 1)

    def get_claude_model(self) -> str:
        """获取Claude模型名称"""
        return self.get('claude_model', 'claude-3-5-sonnet-20241022')

    def get_claude_max_tokens(self) -> int:
        """获取Claude最大token数"""
        return self.get('claude_max_tokens', 1024)

    def get_output_dir(self) -> str:
        """获取输出目录"""
        return self.get('output_dir', 'reports')

    def get_api_base_url(self) -> str:
        """获取API端点"""
        return self.get('api_base_url', None)

    def get_api_key(self) -> str:
        """获取API密钥"""
        api_key = self.get('api_key', None)
        return api_key.strip() if api_key else None

    def get_max_concurrent(self) -> int:
        """获取最大并发请求数"""
        return self.get('max_concurrent', 5)

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
        """获取邮件配置"""
        return self.get('email', {})

    def is_email_enabled(self) -> bool:
        """判断是否启用邮件发送"""
        email_config = self.get_email_config()
        return email_config.get('enabled', False)
