import openai
from typing import List, Dict, Any, Optional
import json
from config.config import AgentConfig

class LLMClient:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.client = openai.OpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url
        )
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       functions: Optional[List[Dict]] = None) -> str:
        """标准对话完成"""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                functions=functions,
                function_call="auto" if functions else None
            )
            
            choice = response.choices[0]
            if choice.message.function_call:
                return self._handle_function_call(choice.message.function_call)
            
            return choice.message.content
        
        except Exception as e:
            return f"LLM调用失败: {str(e)}"
    
    def _handle_function_call(self, function_call) -> Dict[str, Any]:
        """处理函数调用"""
        return {
            "type": "function_call",
            "name": function_call.name,
            "arguments": json.loads(function_call.arguments)
        }
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本嵌入向量"""
        try:
            response = self.client.embeddings.create(
                model=self.config.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"获取嵌入向量失败: {e}")
            return [0.0] * self.config.vector_dim

