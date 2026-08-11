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

    def set_model(self, model: str):
        """更新 config.yaml 中的 llm.model 值（保留注释）"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        import re
        with open(self.config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content, n = re.subn(
            r'^(\s*model:\s*).*$', lambda m: m.group(1) + model, content, flags=re.MULTILINE)
        if n == 0:
            # 若不存在 model 键，则追加到 llm 段末尾
            new_content = content.rstrip() + f"\n  model: {model}\n"
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        self._config = yaml.safe_load(new_content) or {}
        self._load_env()

    def set_api_key(self, api_key: str):
        """更新 .env 文件中的 LLM_API_KEY 值"""
        env_path = Path(self.config_path).parent / ".env"
        lines = []
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith("LLM_API_KEY="):
                lines[i] = f"LLM_API_KEY={api_key}\n"
                updated = True
                break
        if not updated:
            lines.append(f"LLM_API_KEY={api_key}\n")
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        os.environ["LLM_API_KEY"] = api_key

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
