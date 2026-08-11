"""配置管理模块"""

import os
import yaml
from pathlib import Path
from typing import Any, Optional


class Config:
    """配置管理类"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._config = {}
        self._load_config()
        self._load_env()

    def _load_config(self):
        """加载 YAML 配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}

    def _load_env(self):
        """加载 .env 文件环境变量"""
        env_path = Path(self.config_path).parent / ".env"
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())

    def get(self, key_path: str, default: Any = None) -> Any:
        """通过点分隔路径获取配置值，如 'llm.model'"""
        keys = key_path.split('.')
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    @property
    def llm_provider(self) -> str:
        return os.environ.get("LLM_PROVIDER", self.get("llm.provider", "deepseek"))

    @property
    def llm_model(self) -> str:
        return os.environ.get("LLM_MODEL", self.get("llm.model", "deepseek-chat"))

    @property
    def llm_base_url(self) -> str:
        return os.environ.get("LLM_BASE_URL", self.get("llm.base_url", "https://api.deepseek.com/v1"))

    @property
    def llm_api_key(self) -> str:
        return os.environ.get("LLM_API_KEY", "")

    @property
    def llm_timeout(self) -> int:
        return self.get("llm.timeout", 60)

    @property
    def llm_temperature(self) -> float:
        return self.get("llm.temperature", 0.7)

    @property
    def db_path(self) -> str:
        return self.get("database.path", "data/mathgen.db")

    @property
    def pdf_config(self) -> dict:
        return self.get("pdf", {})

    @property
    def generation_config(self) -> dict:
        return self.get("generation", {})

    def __repr__(self):
        return f"Config(provider={self.llm_provider}, model={self.llm_model})"


# 全局配置实例
config = Config()
