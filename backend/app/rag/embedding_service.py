import os
from typing import List
from langchain_openai import OpenAIEmbeddings


class EmbeddingService:
    """嵌入模型服务，使用OpenAI的嵌入模型"""
    
    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        model: str = None
    ):
        """
        初始化嵌入模型服务
        
        Args:
            base_url: OpenAI API的基础URL
            api_key: OpenAI API密钥
            model: 嵌入模型名称
        """
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("EMBEDDING_MODEL_NAME")
        
        self.embeddings = OpenAIEmbeddings(
            openai_api_base=self.base_url,
            openai_api_key=self.api_key,
            model=self.model,
            dimensions=1536
        )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        将多个文档文本转换为嵌入向量
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量列表
        """
        return self.embeddings.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """
        将查询文本转换为嵌入向量
        
        Args:
            text: 查询文本
            
        Returns:
            嵌入向量
        """
        return self.embeddings.embed_query(text)
