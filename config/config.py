import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AgentConfig:
    # OpenAI配置
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 2000
    
    # FAISS配置
    embedding_model: str = "text-embedding-ada-002"
    vector_dim: int = 1536
    faiss_index_path: str = "./data/knowledge_index.faiss"
    
    # Agent配置
    max_reasoning_steps: int = 10
    max_conversation_turns: int = 20
    
    # 工具配置
    enable_log_analysis: bool = True
    enable_metric_query: bool = True
    log_paths: Dict[str, str] = None
    
    def __post_init__(self):
        if self.log_paths is None:
            self.log_paths = {
                "application": "/var/log/application.log",
                "error": "/var/log/error.log",
                "access": "/var/log/access.log"
            }

