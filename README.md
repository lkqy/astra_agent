# 🤖 智能工程师Agent (Intelligent Engineer Agent)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

一个基于大语言模型的智能工程师助手，具备自动日志抓取、知识推理、工具调用等能力，专为解决复杂工程问题而设计。

## 🌟 核心特性

### 🧠 智能推理引擎
- **多步骤推理**：支持复杂问题的分解和逐步解决
- **知识图谱**：构建领域知识网络，提供专业建议
- **经验学习**：从历史问题中学习，不断优化解决方案

### 🔗 自动日志抓取
- **智能链接识别**：自动识别用户输入中的各类链接
- **多源数据支持**：支持HTTP/HTTPS、FTP、数据库连接等
- **内容智能解析**：自动解析JSON、XML、日志文件、纯文本等格式
- **错误模式识别**：智能识别常见错误模式和异常信息

### 🛠️ 丰富工具生态
- **代码分析工具**：静态代码分析、依赖检查
- **系统监控工具**：性能监控、资源使用分析
- **网络诊断工具**：连接测试、延迟分析
- **数据库工具**：查询优化、性能分析

### 📚 知识库管理
- **分层知识结构**：支持基础知识、专业知识、经验知识
- **动态更新**：实时更新最新技术文档和最佳实践
- **相似性搜索**：基于向量搜索的知识检索

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 支持的操作系统：Windows、macOS、Linux

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/engineer-agent.git
cd engineer-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 基础配置

创建配置文件 `config/config.py`：

```python
# LLM配置
LLM_CONFIG = {
    "provider": "openai",  # 或 "claude", "local"
    "model": "gpt-4",
    "api_key": "your-api-key",
    "base_url": "https://api.openai.com/v1",  # 可选，用于自定义端点
    "temperature": 0.7,
    "max_tokens": 4000
}

# 日志抓取配置
LOG_FETCHER_CONFIG = {
    "timeout": 30,
    "max_size": 10 * 1024 * 1024,  # 10MB
    "max_retries": 3,
    "allowed_schemes": ["http", "https", "ftp"],
    "user_agent": "EngineerAgent/1.0"
}

# 知识库配置
KNOWLEDGE_CONFIG = {
    "vector_store": "faiss",  # 或 "chroma", "pinecone"
    "embedding_model": "text-embedding-ada-002",
    "chunk_size": 1000,
    "chunk_overlap": 200
}
```

### 简单示例

```python
from agent import EngineerAgent

# 初始化Agent
agent = EngineerAgent()

# 添加基础知识
agent.add_knowledge("Python最佳实践", "使用虚拟环境管理依赖...")
agent.add_knowledge("Docker部署", "构建轻量级容器镜像的方法...")

# 处理问题
question = """
我的应用出现了内存泄漏问题，相关日志在：
https://example.com/logs/app.log
请帮我分析一下原因和解决方案。
"""

response = agent.process_question(question)
print(response)
```

## 📖 详细使用指南

### 1. Agent初始化和配置

```python
from agent import EngineerAgent
from config.config import LLM_CONFIG, LOG_FETCHER_CONFIG

# 使用自定义配置初始化
agent = EngineerAgent(
    llm_config=LLM_CONFIG,
    log_fetcher_config=LOG_FETCHER_CONFIG,
    enable_reasoning=True,
    enable_tools=True
)

# 或使用默认配置
agent = EngineerAgent()
```

### 2. 知识库管理

```python
# 添加文档知识
agent.add_knowledge(
    title="微服务架构设计",
    content="微服务架构是一种设计方法...",
    category="架构设计",
    tags=["微服务", "架构", "设计模式"]
)

# 从文件添加知识
agent.add_knowledge_from_file("docs/best_practices.md")

# 批量添加知识
knowledge_data = [
    {"title": "Redis缓存策略", "content": "...", "category": "数据库"},
    {"title": "Nginx优化", "content": "...", "category": "运维"}
]
agent.add_knowledge_batch(knowledge_data)

# 搜索相关知识
results = agent.search_knowledge("数据库连接池优化", top_k=5)
```

### 3. 工具系统使用

```python
# 注册自定义工具
@agent.register_tool
def check_disk_space(path: str) -> dict:
    """检查磁盘空间使用情况"""
    import shutil
    usage = shutil.disk_usage(path)
    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
        "usage_percent": (usage.used / usage.total) * 100
    }

# 使用工具
result = agent.use_tool("check_disk_space", path="/")
print(f"磁盘使用率: {result['usage_percent']:.2f}%")

# 列出所有可用工具
tools = agent.list_tools()
for tool_name, tool_info in tools.items():
    print(f"{tool_name}: {tool_info['description']}")
```

### 4. 日志抓取功能

```python
# 直接抓取日志
log_content = agent.fetch_log("https://example.com/api/logs")
print("抓取的日志内容:", log_content)

# 带认证的抓取
log_content = agent.fetch_log(
    "https://secure.example.com/logs",
    headers={"Authorization": "Bearer your-token"}
)

# 数据库日志抓取
db_logs = agent.fetch_log(
    "mysql://user:pass@host:port/db",
    query="SELECT * FROM error_logs WHERE created_at > NOW() - INTERVAL 1 HOUR"
)

# 文件系统日志
file_logs = agent.fetch_log("file:///var/log/application.log")
```

### 5. 高级推理功能

```python
# 启用详细推理过程
agent.set_reasoning_mode("detailed")

# 处理复杂问题
complex_question = """
我们的微服务架构中，用户服务频繁超时，错误日志如下：
https://logs.company.com/user-service/error.log

同时监控显示：
- CPU使用率：85%
- 内存使用率：92%
- 数据库连接数：450/500

请分析根本原因并提供优化方案。
"""

response = agent.process_question(complex_question, use_reasoning=True)

# 查看推理过程
reasoning_steps = agent.get_last_reasoning_steps()
for i, step in enumerate(reasoning_steps, 1):
    print(f"步骤 {i}: {step['action']}")
    print(f"思考: {step['thought']}")
    print(f"结果: {step['result']}\n")
```

## 🏗️ 架构设计

### 系统架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户界面      │    │   核心Agent     │    │   LLM服务       │
│   CLI/Web/API   │◄──►│   推理引擎      │◄──►│   GPT/Claude    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼─────┐
        │   知识库     │ │   工具系统  │ │ 日志抓取  │
        │   向量存储   │ │   代码分析  │ │ 多源支持  │
        │   检索系统   │ │   系统监控  │ │ 智能解析  │
        └──────────────┘ └─────────────┘ └───────────┘
```

### 核心模块说明

#### 1. EngineerAgent (core.py)
- **职责**：统一入口，协调各个子系统
- **核心方法**：
  - `process_question()`: 问题处理主流程
  - `add_knowledge()`: 知识库管理
  - `register_tool()`: 工具注册

#### 2. LogFetcher (log_fetcher.py)
- **职责**：多源日志抓取和解析
- **支持协议**：HTTP(S), FTP, File, Database
- **核心功能**：
  - URL解析和验证
  - 内容抓取和解析
  - 错误处理和重试

#### 3. ReasoningEngine (reasoning.py)
- **职责**：多步骤推理和问题分解
- **推理模式**：
  - `simple`: 直接回答
  - `chain`: 链式思维
  - `tree`: 树状搜索

#### 4. KnowledgeBase (knowledge.py)
- **职责**：知识存储和检索
- **存储方式**：向量数据库 + 传统数据库
- **检索算法**：余弦相似度 + BM25

## 🔧 配置参考

### 完整配置示例

```python
# config/config.py

# LLM配置
LLM_CONFIG = {
    "provider": "openai",
    "model": "gpt-4-turbo-preview",
    "api_key": "sk-your-api-key",
    "base_url": "https://api.openai.com/v1",
    "temperature": 0.1,  # 工程问题需要更准确的回答
    "max_tokens": 8000,
    "timeout": 60,
    "max_retries": 3
}

# 日志抓取配置
LOG_FETCHER_CONFIG = {
    "timeout": 30,
    "max_size": 50 * 1024 * 1024,  # 50MB
    "max_retries": 3,
    "retry_delay": 1.0,
    "allowed_schemes": ["http", "https", "ftp", "file"],
    "blocked_ips": ["127.0.0.1", "localhost"],  # 安全考虑
    "user_agent": "EngineerAgent/1.0",
    "headers": {
        "Accept": "text/plain, application/json, */*",
        "Accept-Encoding": "gzip, deflate"
    }
}

# 知识库配置
KNOWLEDGE_CONFIG = {
    "vector_store": "faiss",
    "embedding_model": "text-embedding-3-large",
    "embedding_dimensions": 3072,
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "similarity_threshold": 0.7,
    "max_results": 10
}

# 推理引擎配置
REASONING_CONFIG = {
    "max_steps": 10,
    "mode": "chain",  # simple, chain, tree
    "confidence_threshold": 0.8,
    "enable_self_correction": True
}

# 工具系统配置
TOOLS_CONFIG = {
    "enable_code_analysis": True,
    "enable_system_monitoring": True,
    "enable_network_diagnosis": True,
    "enable_database_tools": True,
    "tool_timeout": 30
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/engineer_agent.log",
    "max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}
```

## 🧪 测试示例

### 单元测试

```python
# tests/test_agent.py
import unittest
from agent import EngineerAgent

class TestEngineerAgent(unittest.TestCase):
    def setUp(self):
        self.agent = EngineerAgent()
    
    def test_knowledge_addition(self):
        self.agent.add_knowledge("测试知识", "这是测试内容")
        results = self.agent.search_knowledge("测试")
        self.assertGreater(len(results), 0)
    
    def test_log_fetching(self):
        # 使用mock服务测试
        mock_url = "http://httpbin.org/json"
        content = self.agent.fetch_log(mock_url)
        self.assertIsNotNone(content)
    
    def test_tool_registration(self):
        @self.agent.register_tool
        def test_tool(x: int) -> int:
            return x * 2
        
        result = self.agent.use_tool("test_tool", x=5)
        self.assertEqual(result, 10)

if __name__ == "__main__":
    unittest.main()
```

### 集成测试

```python
# tests/test_integration.py
from agent import EngineerAgent

def test_full_workflow():
    agent = EngineerAgent()
    
    # 添加相关知识
    agent.add_knowledge(
        "内存泄漏排查",
        "使用valgrind、内存监控工具等方法排查内存泄漏问题..."
    )
    
    # 模拟包含日志链接的问题
    question = """
    我的Python应用出现内存持续增长的问题，
    相关监控数据：http://httpbin.org/json
    请帮我分析可能的原因。
    """
    
    response = agent.process_question(question)
    
    # 验证响应包含分析内容
    assert "内存" in response
    assert len(response) > 100  # 确保回答足够详细

if __name__ == "__main__":
    test_full_workflow()
    print("集成测试通过！")
```

## 🛠️ 开发指南

### 添加新的日志源

```python
# 在 log_fetcher.py 中添加新的处理器
class CustomLogFetcher:
    def fetch_custom_source(self, url: str, **kwargs) -> str:
        """处理自定义日志源"""
        # 实现你的抓取逻辑
        pass

# 注册新的处理器
agent.log_fetcher.register_handler("custom", CustomLogFetcher().fetch_custom_source)
```

### 扩展工具系统

```python
# 创建新的工具模块
class DatabaseTools:
    @staticmethod
    def analyze_slow_queries(connection_string: str) -> dict:
        """分析慢查询"""
        # 实现分析逻辑
        return {"slow_queries": [], "recommendations": []}

# 批量注册工具
agent.register_tool_class(DatabaseTools)
```

### 自定义推理策略

```python
from agent.reasoning import BaseReasoning

class DomainSpecificReasoning(BaseReasoning):
    def reason(self, question: str, context: dict) -> dict:
        """领域特定的推理逻辑"""
        # 实现自定义推理
        return {
            "steps": [],
            "conclusion": "",
            "confidence": 0.0
        }

# 使用自定义推理引擎
agent.set_reasoning_engine(DomainSpecificReasoning())
```

## 📊 性能优化

### 缓存配置

```python
# 启用缓存以提高性能
CACHE_CONFIG = {
    "enable_llm_cache": True,
    "enable_knowledge_cache": True,
    "enable_log_cache": True,
    "cache_ttl": 3600,  # 1小时
    "max_cache_size": 1000
}

agent = EngineerAgent(cache_config=CACHE_CONFIG)
```

### 并发处理

```python
import asyncio
from agent import AsyncEngineerAgent

# 异步处理多个问题
async def process_multiple_questions(questions):
    agent = AsyncEngineerAgent()
    tasks = [agent.process_question(q) for q in questions]
    results = await asyncio.gather(*tasks)
    return results

# 使用示例
questions = [
    "分析这个错误日志：http://example.com/log1",
    "优化这个SQL查询：http://example.com/log2"
]

results = asyncio.run(process_multiple_questions(questions))
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 常见问题

### Q: 如何更换LLM提供商？

A: 修改配置文件中的 `LLM_CONFIG`：

```python
# 使用Claude
LLM_CONFIG = {
    "provider": "claude",
    "model": "claude-3-opus-20240229",
    "api_key": "your-claude-key"
}

# 使用本地模型
LLM_CONFIG = {
    "provider": "local",
    "model": "llama2",
    "base_url": "http://localhost:11434"
}
```

### Q: 如何添加数据库连接支持？

A: 安装相应的数据库驱动并配置：

```python
# requirements.txt 添加
# psycopg2-binary  # PostgreSQL
# pymysql          # MySQL
# pymongo          # MongoDB

# 使用数据库日志
db_logs = agent.fetch_log(
    "postgresql://user:pass@host:port/db",
    query="SELECT * FROM logs WHERE level='ERROR'"
)
```

### Q: 如何处理大文件日志？

A: 配置流式处理和分块读取：

```python
LOG_FETCHER_CONFIG = {
    "stream_processing": True,
    "chunk_size": 1024 * 1024,  # 1MB chunks
    "max_size": 100 * 1024 * 1024  # 100MB limit
}
```

## 📞 联系我们

- 🐛 Bug报告: [GitHub Issues](https://github.com/lkqy/astra_agent/issues)

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！

**让AI成为你最好的工程师伙伴！** 🚀