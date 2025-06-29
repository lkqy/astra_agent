from typing import List, Dict, Any, Optional
from agent.llm import LLMClient
from agent.knowledge import KnowledgeBase
from agent.tools import ToolRegistry
from loguru import logger
import json

class ReasoningEngine:
    def __init__(self, llm_client: LLMClient, knowledge_base: KnowledgeBase, 
                 tool_registry: ToolRegistry, config):
        self.llm_client = llm_client
        self.knowledge_base = knowledge_base
        self.tool_registry = tool_registry
        self.config = config
    
    def reason(self, problem: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """执行推理过程"""
        reasoning_steps = []
        
        # 1. 知识检索
        knowledge_results = self.knowledge_base.search(problem, top_k=3)
        reasoning_steps.append({
            "step": "knowledge_search",
            "description": "搜索相关知识",
            "results": knowledge_results
        })
        
        # 2. 构建推理提示
        system_prompt = self._build_system_prompt(knowledge_results)
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加对话历史
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": problem})
        
        logger.info(json.dumps(messages, ensure_ascii=False))
        # 3. 执行多步推理
        for step in range(self.config.max_reasoning_steps):
            # 获取工具schema
            tools_schema = self.tool_registry.get_tools_schema()
            
            # LLM推理
            response = self.llm_client.chat_completion(messages, functions=tools_schema)
            
            reasoning_steps.append({
                "step": f"reasoning_{step + 1}",
                "response": response
            })
            
            # 处理工具调用
            if isinstance(response, dict) and response.get("type") == "function_call":
                tool_result = self.tool_registry.execute_tool(
                    response["name"], **response["arguments"]
                )
                
                reasoning_steps.append({
                    "step": f"tool_execution_{step + 1}",
                    "tool": response["name"],
                    "arguments": response["arguments"],
                    "result": tool_result
                })
                
                # 将工具结果添加到对话中
                messages.append({
                    "role": "function",
                    "name": response["name"],
                    "content": str(tool_result)
                })
            else:
                # 普通回复，结束推理
                break
        
        return {
            "reasoning_steps": reasoning_steps,
            "final_response": response if isinstance(response, str) else "推理完成",
            "knowledge_used": knowledge_results
        }
    
    def _build_system_prompt(self, knowledge_results: List[Dict]) -> str:
        """构建系统提示"""
        knowledge_text = ""
        if knowledge_results:
            knowledge_text = "\n相关知识库信息:\n"
            for i, result in enumerate(knowledge_results, 1):
                knowledge_text += f"{i}. {result['content']}\n"
        
        return f"""你是一个专业的工程问题排查专家。你的任务是帮助用户分析和解决线上系统问题。

{knowledge_text}

工作原则：
1. 系统性分析问题，遵循标准的排查流程
2. 基于实际数据和日志进行判断
3. 提供具体可执行的解决方案
4. 必要时使用工具获取更多信息
5. 对复杂问题进行分步骤排查

请根据用户描述的问题，进行专业的分析和解答。如需要查看日志、系统指标等信息，请主动调用相应工具。"""

