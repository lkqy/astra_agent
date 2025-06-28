import subprocess
import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os

class ToolRegistry:
    def __init__(self, config):
        self.config = config
        self.tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        if self.config.enable_log_analysis:
            self.register_tool("analyze_logs", self.analyze_logs, 
                             "分析日志文件，查找错误和异常")
            self.register_tool("search_logs", self.search_logs,
                             "在日志中搜索特定关键词")
        
        if self.config.enable_metric_query:
            self.register_tool("check_system_metrics", self.check_system_metrics,
                             "检查系统指标（CPU、内存、磁盘）")
        
        self.register_tool("execute_command", self.execute_command,
                          "执行系统命令（谨慎使用）")
    
    def register_tool(self, name: str, func, description: str):
        """注册工具"""
        self.tools[name] = {
            "function": func,
            "description": description,
            "schema": self._generate_schema(name, description)
        }
    
    def _generate_schema(self, name: str, description: str) -> Dict:
        """为工具生成OpenAI函数调用的schema"""
        schemas = {
            "analyze_logs": {
                "name": "analyze_logs",
                "description": "分析日志文件，查找错误和异常",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "log_type": {"type": "string", "enum": ["application", "error", "access"]},
                        "time_range": {"type": "string", "description": "时间范围，如'1h', '30m', '1d'"}
                    },
                    "required": ["log_type"]
                }
            },
            "search_logs": {
                "name": "search_logs", 
                "description": "在日志中搜索特定关键词",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string", "description": "搜索关键词"},
                        "log_type": {"type": "string", "enum": ["application", "error", "access"]},
                        "lines": {"type": "integer", "description": "返回行数", "default": 50}
                    },
                    "required": ["keyword", "log_type"]
                }
            },
            "check_system_metrics": {
                "name": "check_system_metrics",
                "description": "检查系统指标",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "metrics": {"type": "array", "items": {"type": "string"}, 
                                   "description": "要检查的指标：cpu, memory, disk"}
                    }
                }
            },
            "execute_command": {
                "name": "execute_command",
                "description": "执行系统命令",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "要执行的命令"}
                    },
                    "required": ["command"]
                }
            }
        }
        return schemas.get(name, {"name": name, "description": description, "parameters": {}})
    
    def get_tools_schema(self) -> List[Dict]:
        """获取所有工具的schema"""
        return [tool["schema"] for tool in self.tools.values()]
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """执行工具"""
        if tool_name not in self.tools:
            return {"error": f"工具 {tool_name} 不存在"}
        
        try:
            result = self.tools[tool_name]["function"](**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_logs(self, log_type: str, time_range: str = "1h") -> Dict:
        """分析日志"""
        log_path = self.config.log_paths.get(log_type)
        if not log_path or not os.path.exists(log_path):
            return {"error": f"日志文件不存在: {log_path}"}
        
        try:
            # 简单的日志分析逻辑
            cmd = f"tail -n 1000 {log_path}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            logs = result.stdout
            error_patterns = [r"ERROR", r"Exception", r"Failed", r"Error", r"error"]
            
            errors = []
            for line in logs.split('\n'):
                for pattern in error_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        errors.append(line.strip())
                        break
            
            return {
                "total_lines": len(logs.split('\n')),
                "error_count": len(errors),
                "recent_errors": errors[-10:] if errors else [],
                "log_type": log_type
            }
        except Exception as e:
            return {"error": f"分析日志失败: {str(e)}"}
    
    def search_logs(self, keyword: str, log_type: str, lines: int = 50) -> Dict:
        """搜索日志"""
        log_path = self.config.log_paths.get(log_type)
        if not log_path or not os.path.exists(log_path):
            return {"error": f"日志文件不存在: {log_path}"}
        
        try:
            cmd = f"grep -i '{keyword}' {log_path} | tail -n {lines}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            matches = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            return {
                "keyword": keyword,
                "matches": matches,
                "match_count": len(matches),
                "log_type": log_type
            }
        except Exception as e:
            return {"error": f"搜索日志失败: {str(e)}"}
    
    def check_system_metrics(self, metrics: List[str] = None) -> Dict:
        """检查系统指标"""
        if metrics is None:
            metrics = ["cpu", "memory", "disk"]
        
        result = {}
        
        try:
            if "cpu" in metrics:
                # 获取CPU使用率
                cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print \$2}' | cut -d'%' -f1"
                cpu_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                result["cpu_usage"] = cpu_result.stdout.strip()
            
            if "memory" in metrics:
                # 获取内存使用情况
                cmd = "free -m | awk 'NR==2{printf \"%.2f\", \$3*100/\$2 }'"
                mem_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                result["memory_usage"] = f"{mem_result.stdout.strip()}%"
            
            if "disk" in metrics:
                # 获取磁盘使用情况
                cmd = "df -h | awk '$NF==\"/\"{printf \"%s\", \$5}'"
                disk_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                result["disk_usage"] = disk_result.stdout.strip()
            
        except Exception as e:
            result["error"] = f"获取系统指标失败: {str(e)}"
        
        return result
    
    def execute_command(self, command: str) -> Dict:
        """执行系统命令（需要谨慎使用）"""
        # 安全检查
        dangerous_commands = ["rm", "del", "format", "shutdown", "reboot"]
        if any(cmd in command.lower() for cmd in dangerous_commands):
            return {"error": "拒绝执行危险命令"}
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, 
                                  text=True, timeout=30)
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "命令执行超时"}
        except Exception as e:
            return {"error": f"命令执行失败: {str(e)}"}

