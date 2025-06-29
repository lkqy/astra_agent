from config.config import AgentConfig
from agent.core import EngineerAgent

def main():
    # 配置Agent
    config = AgentConfig(
        enable_log_analysis=True,
        enable_metric_query=True,
        model_name='qwen-plus'
    )
    
    # 创建Agent
    agent = EngineerAgent(config)
    
    # 添加一些工程知识
    agent.add_knowledge(
        "Redis连接超时问题通常由网络延迟、Redis服务器负载过高、连接池配置不当引起",
        {"category": "Redis问题", "tags": ["Redis", "连接超时", "网络"]}
    )
    
    print("工程问题排查Agent已启动！输入'quit'退出。\n")
    
    while True:
        user_input = input("👨‍💻 请描述遇到的问题: ")
        if user_input.lower() == 'quit':
            break
        
        try:
            result = agent.chat(user_input)
            
            print(f"\n🤖 分析结果:")
            print(f"{result['response']}\n")
            
            # 显示推理步骤（可选）
            if result.get('reasoning_steps'):
                print("🔍 分析过程:")
                for step in result['reasoning_steps']:
                    if step['step'].startswith('tool_execution'):
                        print(f"  - 执行工具: {step['tool']}")
                        print(f"    结果: {step['result']}")
                print()
            
        except Exception as e:
            print(f"❌ 处理错误: {e}\n")

if __name__ == "__main__":
    main()

