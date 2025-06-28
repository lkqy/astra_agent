from typing import List, Dict, Any, Optional
from agent.llm import LLMClient
from agent.knowledge import KnowledgeBase
from agent.tools import ToolRegistry
from agent.reasoning import ReasoningEngine
from config.config import AgentConfig

class EngineerAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.conversation_history = []
        
        # 初始化组件
        self.llm_client = LLMClient(config)
        self.knowledge_base = KnowledgeBase(self.llm_client, config)
        self.tool_registry = ToolRegistry(config)
        self.reasoning_engine = ReasoningEngine(
            self.llm_client, self.knowledge_base, 
            self.tool_registry, config
        )
    
    def chat(self, message: str) -> Dict[str, Any]:
        """处理用户输入"""
        # 检查对话轮数限制
        if len(self.conversation_history) >= self.config.max_conversation_turns * 2:
            self.conversation_history = self.conversation_history[-10:]  # 保留最近10轮
        
        # 执行推理
        reasoning_result = self.reasoning_engine.reason(message, self.conversation_history)
        
        # 更新对话历史
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({
            "role": "assistant", 
            "content": reasoning_result["final_response"]
        })
        
        return {
            "response": reasoning_result["final_response"],
            "reasoning_steps": reasoning_result["reasoning_steps"],
            "knowledge_used": reasoning_result["knowledge_used"],
            "conversation_id": len(self.conversation_history) // 2
        }
    
    def add_knowledge(self, content: str, metadata: Dict = None):
        """添加新知识到知识库"""
        if metadata is None:
            metadata = {"source": "manual", "timestamp": str(datetime.now())}
        
        self.knowledge_base.add_knowledge(content, metadata)
    
    def get_conversation_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.conversation_history.copy()
    
    def clear_conversation(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def register_custom_tool(self, name: str, func, description: str):
        """注册自定义工具"""
        self.tool_registry.register_tool(name, func, description)

