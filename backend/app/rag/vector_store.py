import os
from typing import List, Dict, Any
import chromadb


class VectorStore:
    """向量存储服务，使用Chroma进行本地向量存储和查询"""
    
    def __init__(
        self,
        persist_directory: str = None,
        collection_name: str = "knowledge_base"
    ):
        """
        初始化向量存储
        
        Args:
            persist_directory: 向量库持久化目录
            collection_name: 集合名称
        """
        if persist_directory is None:
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            persist_directory = os.path.join(current_dir, "data", "chroma")
        
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=chromadb.Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ):
        """
        添加文档分块到向量库
        
        Args:
            chunks: 文档分块列表，每个分块包含content, source, chunk_id
            embeddings: 对应的嵌入向量列表
        """
        ids = [chunk["chunk_id"] for chunk in chunks]
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [{"source": chunk["source"]} for chunk in chunks]
        
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        print(f"成功添加 {len(chunks)} 个文档分块到向量库")
    
    def search(
        self,
        query_embedding: List[float],
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        在向量库中搜索最相关的文档
        
        Args:
            query_embedding: 查询的嵌入向量
            n_results: 返回的结果数量
            
        Returns:
            搜索结果列表，每个结果包含content, source, distance
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        search_results = []
        
        if results["documents"] and len(results["documents"]) > 0:
            for i in range(len(results["documents"][0])):
                search_results.append({
                    "content": results["documents"][0][i],
                    "source": results["metadatas"][0][i]["source"],
                    "distance": results["distances"][0][i]
                })
        
        return search_results
    
    def get_collection_count(self) -> int:
        """
        获取集合中的文档数量
        
        Returns:
            文档数量
        """
        return self.collection.count()
    
    def clear_collection(self):
        """清空集合中的所有文档"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print("已清空向量库")
