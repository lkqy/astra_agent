from typing import List, Dict, Any, Optional
from agent.llm import LLMClient
from agent.knowledge import KnowledgeBase
from agent.tools import ToolRegistry
from agent.reasoning import ReasoningEngine
from agent.log_fetcher import LogFetcher
from config.config import AgentConfig
from loguru import logger
import json

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
        self.log_fetcher = LogFetcher(config)  # 新增
    
    def chat(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理用户查询 - 自动抓取相关日志"""
        logger.info(f"处理查询: {query[:100]}...")
        
        try:
            # 1. 自动抓取日志
            fetched_logs = self.log_fetcher.fetch_from_user_input(query)

            # 2. 构建增强的上下文
            enhanced_context = self._build_enhanced_context(
                query, context or {}, fetched_logs
            )

            # 3. 搜索知识库
            relevant_knowledge = self.knowledge_base.search(query, top_k=5)

            # 4. 使用推理引擎分析
            reasoning_result = self.reasoning_engine.analyze_problem(
                query, enhanced_context, relevant_knowledge
            )

            # 5. 生成最终回答
            response = self._generate_response(
                query, enhanced_context, reasoning_result
            )

            # 6. 更新对话历史
            self._update_conversation_history(query, response)

            return {
                'query': query,
                'response': response,
                'fetched_logs': fetched_logs,
                'context': enhanced_context,
                'reasoning': reasoning_result,
                'relevant_knowledge': relevant_knowledge
            }

        except Exception as e:
            logger.error(f"处理查询时出错: {e}")
            logger.exception(e)
            return {
                'query': query,
                'error': str(e),
                'response': f"抱歉，处理您的问题时出现了错误：{str(e)}"
            }
    
    def _build_enhanced_context(self, query: str, base_context: Dict[str, Any], 
                               fetched_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建增强的上下文，包含抓取的日志信息"""
        enhanced_context = {
            'original_query': query,
            'base_context': base_context,
            'fetched_data_summary': self._summarize_fetched_data(fetched_logs),
            'system_info': {},
            'conversation_history': self.conversation_history[-5:]  # 最近5轮对话
        }
        
        # 如果有成功抓取的日志，添加详细信息
        if fetched_logs:
            enhanced_context['log_analysis'] = self._analyze_fetched_logs(fetched_logs)
        
        return enhanced_context

    def _summarize_fetched_data(self, fetched_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """总结抓取的数据"""
        summary = {
            'total_sources': len(fetched_logs),
            'successful_fetches': 0,
            'failed_fetches': 0,
            'total_content_size': 0,
            'error_count': 0,
            'warning_count': 0,
            'sources': []
        }

        for fetch_result in fetched_logs:
            if fetch_result['fetch_success']:
                summary['successful_fetches'] += 1
                data = fetch_result['fetched_data']
                summary['total_content_size'] += data.get('size', 0)
                
                # 统计错误和警告
                parsed_data = data.get('parsed_data', {})
                if isinstance(parsed_data, dict):
                    summary['error_count'] += parsed_data.get('error_count', 0)
                    summary['warning_count'] += parsed_data.get('warning_count', 0)

                summary['sources'].append({
                    'url': fetch_result['source_link']['url'],
                    'type': fetch_result['source_link']['type'],
                    'size': data.get('size', 0),
                    'content_type': data.get('content_type', 'unknown'),
                    'summary': data.get('summary', '')
                })
            else:
                summary['failed_fetches'] += 1
                summary['sources'].append({
                    'url': fetch_result['source_link']['url'],
                    'type': fetch_result['source_link']['type'],
                    'error': fetch_result.get('error', 'Unknown error')
                })
        
        return summary
    
    def _analyze_fetched_logs(self, fetched_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析抓取的日志，提取关键信息"""
        analysis = {
            'key_findings': [],
            'error_patterns': [],
            'timeline': [],
            'recommendations': []
        }

        all_errors = []
        all_warnings = []
        
        for fetch_result in fetched_logs:
            if not fetch_result['fetch_success']:
                continue
 
            data = fetch_result['fetched_data']
            parsed_data = data.get('parsed_data', {})
            key_points = data.get('key_points', [])

            # 收集关键发现
            if key_points:
                analysis['key_findings'].extend(key_points)

            # 收集错误信息
            if isinstance(parsed_data, dict) and 'entries' in parsed_data:
                for entry in parsed_data['entries']:
                    if entry.get('is_error'):
                        all_errors.append(entry['raw_line'])
                    elif entry.get('is_warning'):
                        all_warnings.append(entry['raw_line'])

        # 分析错误模式
        if all_errors:
            analysis['error_patterns'] = self._find_error_patterns(all_errors)

        # 生成建议
        analysis['recommendations'] = self._generate_recommendations(
            all_errors, all_warnings
        )

        return analysis

    def _find_error_patterns(self, errors: List[str]) -> List[Dict[str, Any]]:
        """查找错误模式"""
        # 这里可以实现更复杂的模式识别
        # 现在只做简单的关键词统计
        patterns = {}
        for error in errors:
            words = error.lower().split()
            for word in words:
                if len(word) > 3 and not word.isdigit():
                    patterns[word] = patterns.get(word, 0) + 1

        # 返回出现频率最高的模式
        sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
        return [{'pattern': pattern, 'count': count} 
                for pattern, count in sorted_patterns[:10]]

    def _generate_recommendations(self, errors: List[str], 
                                warnings: List[str]) -> List[str]:
        """基于错误和警告生成建议"""
        recommendations = []

        if errors:
            recommendations.append(f"发现 {len(errors)} 个错误，需要优先处理")

        if warnings:
            recommendations.append(f"发现 {len(warnings)} 个警告，建议关注")

        # 可以根据具体的错误类型添加更多建议
        return recommendations

    def _generate_response(self, query: str, context: Dict[str, Any], 
                          reasoning_result: Dict[str, Any]) -> str:
        """生成最终回答"""
        # 构建提示词
        prompt = self._build_response_prompt(query, context, reasoning_result)

        # 调用LLM生成回答
        response = self.llm.generate_response(prompt)

        return response

    def _build_response_prompt(self, query: str, context: Dict[str, Any], 
                              reasoning_result: Dict[str, Any]) -> str:
        """构建生成回答的提示词"""
        prompt = f"""你是一个专业的工程问题排查专家。请根据以下信息回答用户的问题。

用户问题：{query}

抓取的日志信息摘要：
{json.dumps(context.get('fetched_data_summary', {}), ensure_ascii=False, indent=2)}

日志分析结果：
{json.dumps(context.get('log_analysis', {}), ensure_ascii=False, indent=2)}

推理分析：
{json.dumps(reasoning_result, ensure_ascii=False, indent=2)}

请提供详细的分析和解决建议：
1. 问题分析：基于抓取的日志和上下文信息
2. 根本原因：可能的问题根源
3. 解决方案：具体的解决步骤
4. 预防措施：避免类似问题的建议

回答要专业、准确，并且要结合实际的日志信息。"""

        return prompt
    
    def _update_conversation_history(self, query: str, response: str):
        """更新对话历史"""
        self.conversation_history.append({
            'timestamp': self._get_current_timestamp(),
            'query': query,
            'response': response
        })

        # 保持历史记录不超过20条
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_knowledge(self, content: str, metadata: Dict[str, Any] = None):
        """添加知识到知识库"""
        self.knowledge_base.add_knowledge(content, metadata)

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.conversation_history.copy()

    def clear_conversation_history(self):
        """清空对话历史"""
        self.conversation_history = []
        logger.info("对话历史已清空")

    def add_knowledge(self, content: str, metadata: Dict = None):
        """添加新知识到知识库"""
        if metadata is None:
            metadata = {"source": "manual", "timestamp": str(datetime.now())}

        self.knowledge_base.add_knowledge(content, metadata)

    def register_custom_tool(self, name: str, func, description: str):
        """注册自定义工具"""
        self.tool_registry.register_tool(name, func, description)