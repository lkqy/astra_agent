import requests
from typing import Dict, Any, Optional, List
from utils.parsers import ContentParser, LinkExtractor
from utils.logger import get_logger

logger = get_logger(__name__)

class LogFetcher:
    """日志抓取器，支持多种数据源"""
    
    def __init__(self, config):
        self.config = config
        self.parser = ContentParser()
        self.link_extractor = LinkExtractor()
        self.session = requests.Session()
        
        # 设置请求头
        if config.auth_headers:
            self.session.headers.update(config.auth_headers)
    
    def fetch_from_user_input(self, user_input: str) -> List[Dict[str, Any]]:
        """从用户输入中提取链接并抓取内容"""
        # 提取链接
        links = self.link_extractor.extract_links(user_input)
        logger.info(f"从用户输入中发现 {len(links)} 个链接")
        
        fetched_data = []
        for link in links:
            try:
                data = self.fetch_content(link['url'], link['type'])
                if data:
                    fetched_data.append({
                        'source_link': link,
                        'fetched_data': data,
                        'fetch_success': True
                    })
                    logger.info(f"成功抓取: {link['url']}")
                else:
                    fetched_data.append({
                        'source_link': link,
                        'error': 'Failed to fetch content',
                        'fetch_success': False
                    })
                    logger.warning(f"抓取失败: {link['url']}")
            except Exception as e:
                fetched_data.append({
                    'source_link': link,
                    'error': str(e),
                    'fetch_success': False
                })
                logger.error(f"抓取异常 {link['url']}: {e}")
        
        return fetched_data
    
    def fetch_content(self, url: str, link_type: str = None) -> Optional[Dict[str, Any]]:
        """根据URL类型抓取内容"""
        if not link_type:
            link_type = self._detect_link_type(url)
        
        try:
            if link_type == 'http':
                return self._fetch_http(url)
            else:
                logger.warning(f"不支持的链接类型: {link_type}")
                return None
        except Exception as e:
            logger.error(f"抓取内容失败 {url}: {e}")
            return None
    
    def _fetch_http(self, url: str) -> Dict[str, Any]:
        """抓取HTTP链接内容"""
        response = self.session.get(
            url,
            timeout=self.config.request_timeout,
            stream=True
        )
        response.raise_for_status()
        
        # 检查内容大小
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > self.config.max_log_size:
            logger.warning(f"内容过大，将截断: {url}")
        
        # 读取内容
        content = ""
        total_size = 0
        for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
            if chunk:
                content += chunk
                total_size += len(chunk.encode('utf-8'))
                if total_size > self.config.max_log_size:
                    logger.warning(f"内容已截断到 {self.config.max_log_size} 字节")
                    break
        
        content_type = response.headers.get('content-type', 'text/plain')
        
        return {
            'url': url,
            'content_type': content_type,
            'size': len(content),
            'headers': dict(response.headers),
            **self.parser.parse_content(content, content_type)
        }
    
    def _detect_link_type(self, url: str) -> str:
        """检测链接类型"""
        if url.startswith(('http://', 'https://')):
            return 'http'