from typing import List, Dict, Any
from .document_loader import DocumentLoader
from .text_splitter import TextSplitter
from .embedding_service import EmbeddingService
from .vector_store import VectorStore


class RAGManager:
    """RAG管理器，整合文档加载、分块、嵌入和向量存储"""
    
    def __init__(
        self,
        resources_dir: str = None,
        persist_directory: str = None,
        embedding_model: str = None,
        chunk_size: int = 800,
        chunk_overlap: int = 150
    ):
        """
        初始化RAG管理器
        
        Args:
            resources_dir: 资源目录路径
            persist_directory: 向量库持久化目录
            embedding_model: 嵌入模型名称
            chunk_size: 分块大小
            chunk_overlap: 分块重叠大小
        """
        self.document_loader = DocumentLoader(resources_dir)
        self.text_splitter = TextSplitter(chunk_size, chunk_overlap)
        self.embedding_service = EmbeddingService(model=embedding_model)
        # 将 embedding_service 的 embeddings 实例传递给 VectorStore，确保使用相同的配置
        self.vector_store = VectorStore(persist_directory, embeddings=self.embedding_service.embeddings)
    
    def initialize_knowledge_base(self, force_rebuild: bool = False):
        """
        初始化知识库，加载文档并构建向量索引
        
        Args:
            force_rebuild: 是否强制重建向量库
        """
        collection_count = self.vector_store.get_collection_count()
        
        if collection_count > 0 and not force_rebuild:
            print(f"向量库已存在，包含 {collection_count} 个文档分块，跳过初始化")
            return
        
        if force_rebuild:
            print("强制重建向量库...")
            self.vector_store.clear_collection()
        
        print("开始初始化知识库...")
        
        documents = self.document_loader.load_all_pdfs()
        
        if not documents:
            print("未找到任何PDF文档")
            return
        
        chunks = self.text_splitter.split_documents(documents)
        print(f"文档分块完成，共 {len(chunks)} 个分块")
        
        texts = [chunk["content"] for chunk in chunks]
        print("开始生成嵌入向量...")
        
        embeddings = self.embedding_service.embed_documents(texts)
        print("嵌入向量生成完成")
        
        self.vector_store.add_documents(chunks, embeddings)
        print("知识库初始化完成")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        搜索知识库
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        query_embedding = self.embedding_service.embed_query(query)
        results = self.vector_store.search(query_embedding, n_results)
        return results
    
    def get_knowledge_base_info(self) -> Dict[str, Any]:
        """
        获取知识库信息
        
        Returns:
            知识库信息字典
        """
        return {
            "document_count": self.vector_store.get_collection_count(),
            "persist_directory": self.vector_store.persist_directory,
            "collection_name": self.vector_store.collection_name
        }
