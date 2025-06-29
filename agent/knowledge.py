import faiss
import numpy as np
import pickle
import os
from loguru import logger
from typing import List, Dict, Tuple
from agent.llm import LLMClient

class KnowledgeBase:
    def __init__(self, llm_client: LLMClient, config):
        self.llm_client = llm_client
        self.config = config
        self.index = None
        self.documents = []
        self.metadata = []
        
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """加载或创建FAISS索引"""
        if os.path.exists(self.config.faiss_index_path):
            self.index = faiss.read_index(self.config.faiss_index_path)
            # 加载文档和元数据
            meta_path = self.config.faiss_index_path.replace('.faiss', '_meta.pkl')
            if os.path.exists(meta_path):
                with open(meta_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data['documents']
                    self.metadata = data['metadata']
        else:
            # 创建新索引
            self.index = faiss.IndexFlatIP(self.config.vector_dim)
            self._initialize_knowledge()
    
    def _initialize_knowledge(self):
        """初始化工程知识库"""
        # 这里可以预置一些常见的工程问题和解决方案
        initial_knowledge = [
            {
                "content": "服务响应时间过长通常由以下原因导致：1.数据库查询慢 2.外部接口调用超时 3.内存不足 4.CPU使用率高",
                "category": "性能问题",
                "tags": ["响应时间", "性能", "数据库", "接口"]
            },
            {
                "content": "内存溢出排查步骤：1.查看JVM堆内存使用情况 2.分析GC日志 3.使用内存分析工具 4.检查是否有内存泄漏",
                "category": "内存问题", 
                "tags": ["内存溢出", "JVM", "GC", "内存泄漏"]
            },
            {
                "content": "数据库连接池满的解决方案：1.检查连接是否正确释放 2.调整连接池大小 3.优化SQL查询 4.检查慢查询",
                "category": "数据库问题",
                "tags": ["连接池", "数据库", "SQL", "慢查询"]
            }
        ]
        
        for knowledge in initial_knowledge:
            self.add_knowledge(knowledge["content"], knowledge)
    
    def add_knowledge(self, content: str, metadata: Dict):
        """添加知识到知识库"""
        embedding = self.llm_client.get_embedding(content)
        logger.info(f'content={content}, embedding={embedding}')
        embedding_array = np.array([embedding], dtype=np.float32)
        
        self.index.add(embedding_array)
        self.documents.append(content)
        self.metadata.append(metadata)
        
        self._save_index()
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索相关知识"""
        if self.index.ntotal == 0:
            return []
        
        query_embedding = self.llm_client.get_embedding(query)
        query_array = np.array([query_embedding], dtype=np.float32)
        
        scores, indices = self.index.search(query_array, min(top_k, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:  # 有效索引
                results.append({
                    "content": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "score": float(score)
                })
        logger.info(results)
        return results
    
    def _save_index(self):
        """保存索引和元数据"""
        faiss.write_index(self.index, self.config.faiss_index_path)
        
        meta_path = self.config.faiss_index_path.replace('.faiss', '_meta.pkl')
        with open(meta_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata
            }, f)

