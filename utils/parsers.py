import re
import json
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import mimetypes

class ContentParser:
    """内容解析器，用于解析各种格式的日志和数据"""
    
    def __init__(self):
        self.log_patterns = {
            'timestamp': r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}',
            'ip': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'error': r'(?i)(error|exception|fail|fatal)',
            'warn': r'(?i)(warn|warning)',
            'info': r'(?i)(info|information)',
            'debug': r'(?i)(debug|trace)',
        }
    
    def parse_content(self, content: str, content_type: str = None) -> Dict[str, Any]:
        """解析内容并提取关键信息"""
        result = {
            'raw_content': content,
            'content_type': content_type,
            'parsed_data': {},
            'summary': '',
            'key_points': []
        }
        
        if not content.strip():
            return result
            
        # 根据内容类型选择解析方式
        if content_type and 'json' in content_type.lower():
            result['parsed_data'] = self._parse_json(content)
        elif self._is_log_content(content):
            result['parsed_data'] = self._parse_logs(content)
        else:
            result['parsed_data'] = self._parse_plain_text(content)
        
        # 生成摘要和关键点
        result['summary'] = self._generate_summary(content)
        result['key_points'] = self._extract_key_points(content)
        
        return result
    
    def _parse_json(self, content: str) -> Dict[str, Any]:
        """解析JSON内容"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {'error': 'Invalid JSON format', 'raw': content}
    
    def _parse_logs(self, content: str) -> Dict[str, Any]:
        """解析日志内容"""
        lines = content.strip().split('\n')
        parsed_logs = []
        
        for line in lines:
            if not line.strip():
                continue
                
            log_entry = {
                'raw_line': line,
                'timestamp': self._extract_timestamp(line),
                'level': self._extract_log_level(line),
                'ip_addresses': self._extract_ips(line),
                'is_error': bool(re.search(self.log_patterns['error'], line)),
                'is_warning': bool(re.search(self.log_patterns['warn'], line))
            }
            parsed_logs.append(log_entry)
        
        return {
            'total_lines': len(parsed_logs),
            'error_count': sum(1 for log in parsed_logs if log['is_error']),
            'warning_count': sum(1 for log in parsed_logs if log['is_warning']),
            'entries': parsed_logs[:100]  # 限制条目数量
        }
    
    def _parse_plain_text(self, content: str) -> Dict[str, Any]:
        """解析纯文本内容"""
        lines = content.strip().split('\n')
        return {
            'line_count': len(lines),
            'char_count': len(content),
            'has_timestamps': bool(re.search(self.log_patterns['timestamp'], content)),
            'has_errors': bool(re.search(self.log_patterns['error'], content)),
            'ip_addresses': list(set(re.findall(self.log_patterns['ip'], content)))
        }
    
    def _is_log_content(self, content: str) -> bool:
        """判断是否为日志内容"""
        # 检查是否包含时间戳和日志级别
        has_timestamp = bool(re.search(self.log_patterns['timestamp'], content))
        has_log_level = any(re.search(pattern, content) for pattern in 
                           [self.log_patterns['error'], self.log_patterns['warn'], 
                            self.log_patterns['info'], self.log_patterns['debug']])
        return has_timestamp or has_log_level
    
    def _extract_timestamp(self, line: str) -> Optional[str]:
        """提取时间戳"""
        match = re.search(self.log_patterns['timestamp'], line)
        return match.group() if match else None
    
    def _extract_log_level(self, line: str) -> Optional[str]:
        """提取日志级别"""
        for level, pattern in [('ERROR', self.log_patterns['error']),
                              ('WARN', self.log_patterns['warn']),
                              ('INFO', self.log_patterns['info']),
                              ('DEBUG', self.log_patterns['debug'])]:
            if re.search(pattern, line):
                return level
        return None
    
    def _extract_ips(self, line: str) -> List[str]:
        """提取IP地址"""
        return re.findall(self.log_patterns['ip'], line)
    
    def _generate_summary(self, content: str) -> str:
        """生成内容摘要"""
        lines = content.strip().split('\n')
        total_lines = len(lines)
        
        error_count = len(re.findall(self.log_patterns['error'], content, re.IGNORECASE))
        warning_count = len(re.findall(self.log_patterns['warn'], content, re.IGNORECASE))
        
        summary = f"内容包含 {total_lines} 行"
        if error_count > 0:
            summary += f", {error_count} 个错误"
        if warning_count > 0:
            summary += f", {warning_count} 个警告"
            
        return summary
    
    def _extract_key_points(self, content: str) -> List[str]:
        """提取关键点"""
        key_points = []
        
        # 提取错误信息
        error_lines = []
        for line in content.split('\n'):
            if re.search(self.log_patterns['error'], line, re.IGNORECASE):
                error_lines.append(line.strip())
        
        if error_lines:
            key_points.append(f"发现 {len(error_lines)} 个错误:")
            key_points.extend(error_lines[:5])  # 最多显示5个错误
        
        # 提取IP地址
        ips = list(set(re.findall(self.log_patterns['ip'], content)))
        if ips:
            key_points.append(f"涉及IP地址: {', '.join(ips[:10])}")
        
        return key_points

class LinkExtractor:
    """链接提取器，用于从文本中识别各种类型的链接"""
    
    def __init__(self):
        self.patterns = {
            'http': r'https?://[^\s<>"{}|\\^`\[\]]+',
            'file': r'(?:file://)?(?:/[^\s]+|[A-Za-z]:[^\s]+)',
            'ssh': r'ssh://[^\s]+',
            'ftp': r'ftp://[^\s]+',
            'log_path': r'(?:/var/log/[^\s]+|/logs?/[^\s]+|\.log[^\s]*)',
        }
    
    def extract_links(self, text: str) -> List[Dict[str, str]]:
        """从文本中提取所有链接"""
        links = []
        
        for link_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                links.append({
                    'type': link_type,
                    'url': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
        
        # 按位置排序并去重
        links.sort(key=lambda x: x['start'])
        unique_links = []
        seen_urls = set()
        
        for link in links:
            if link['url'] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link['url'])
        
        return unique_links
