import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "chroma").lower()

if VECTOR_STORE_TYPE == "supabase":
    from supabase import create_client, Client
    from langchain_community.vectorstores import SupabaseVectorStore
    from langchain_openai import OpenAIEmbeddings


class VectorStore:
    """向量存储服务，支持 ChromaDB 和 Supabase"""
    
    def __init__(
        self,
        persist_directory: str = None,
        collection_name: str = "knowledge_base"
    ):
        """
        初始化向量存储
        
        Args:
            persist_directory: 向量库持久化目录（仅 ChromaDB 使用）
            collection_name: 集合名称
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self._vector_store = None
        self._client = None
        
        if VECTOR_STORE_TYPE == "supabase":
            self._init_supabase()
        else:
            self._init_chroma(persist_directory, collection_name)
    
    def _init_chroma(self, persist_directory: str, collection_name: str):
        """初始化 ChromaDB"""
        import chromadb
        
        if persist_directory is None:
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            persist_directory = os.path.join(current_dir, "data", "chroma")
        
        self.persist_directory = persist_directory
        
        os.makedirs(persist_directory, exist_ok=True)
        
        self._client = chromadb.PersistentClient(
            path=persist_directory,
            settings=chromadb.Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def _init_supabase(self):
        """初始化 Supabase 向量存储"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set for Supabase vector store")
        
        self._client: Client = create_client(supabase_url, supabase_anon_key)
        
        # 自动创建表和函数（如果不存在）
        self._ensure_supabase_schema()
        
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self._vector_store = SupabaseVectorStore(
            client=self._client,
            embedding=embeddings,
            table_name=self.collection_name,
            query_name=f"{self.collection_name}_match"
        )
        
        print(f"已连接到 Supabase 向量数据库: {supabase_url}")
    
    def _ensure_supabase_schema(self):
        """确保 Supabase 表和函数存在，不存在则自动创建"""
        import time
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 尝试访问表来检查是否存在
                result = self._client.table(self.collection_name).select("id", count="exact").limit(1).execute()
                print(f"表 {self.collection_name} 已存在")
                return
            except Exception as e:
                error_msg = str(e)
                
                # 检查是否是表不存在的错误
                if "PGRST205" in error_msg or "Could not find the table" in error_msg:
                    if attempt == 0:
                        print(f"表 {self.collection_name} 不存在，需要手动创建")
                        print("\n" + "="*60)
                        print("请在 Supabase SQL Editor 中执行以下 SQL:")
                        print("="*60)
                        print(self._get_manual_sql())
                        print("="*60 + "\n")
                        raise RuntimeError(
                            f"Supabase 表 '{self.collection_name}' 不存在。\n"
                            f"请登录 Supabase Dashboard -> SQL Editor，\n"
                            f"执行上面打印的 SQL 语句来创建表和函数。"
                        )
                else:
                    # 其他错误，可能是网络问题，重试
                    if attempt < max_retries - 1:
                        print(f"检查表时出错，正在重试 ({attempt + 1}/{max_retries}): {e}")
                        time.sleep(1)
                    else:
                        raise
    
    def _get_manual_sql(self) -> str:
        """获取手动创建表和函数的 SQL"""
        function_name = f"{self.collection_name}_match"
        return f"""-- 启用向量扩展（如果还没有启用）
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建表
CREATE TABLE IF NOT EXISTS public.{self.collection_name} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536)
);

-- 创建索引（提高向量搜索性能）
CREATE INDEX IF NOT EXISTS idx_{self.collection_name}_embedding 
ON public.{self.collection_name} 
USING ivfflat (embedding vector_cosine_ops);

-- 创建相似度搜索函数
CREATE OR REPLACE FUNCTION public.{function_name}(
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 5
)
RETURNS TABLE(
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        {self.collection_name}.id,
        {self.collection_name}.content,
        {self.collection_name}.metadata,
        1 - ({self.collection_name}.embedding <=> query_embedding) AS similarity
    FROM {self.collection_name}
    ORDER BY {self.collection_name}.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;"""
    
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
        if VECTOR_STORE_TYPE == "supabase":
            texts = [chunk["content"] for chunk in chunks]
            metadatas = [{"source": chunk["source"]} for chunk in chunks]
            ids = [chunk["chunk_id"] for chunk in chunks]
            
            self._vector_store.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            print(f"成功添加 {len(chunks)} 个文档分块到 Supabase 向量库")
        else:
            ids = [chunk["chunk_id"] for chunk in chunks]
            documents = [chunk["content"] for chunk in chunks]
            metadatas = [{"source": chunk["source"]} for chunk in chunks]
            
            self._collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            print(f"成功添加 {len(chunks)} 个文档分块到 Chroma 向量库")
    
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
        if VECTOR_STORE_TYPE == "supabase":
            results = self._vector_store.similarity_search_by_vector(
                embedding=query_embedding,
                k=n_results
            )
            
            search_results = []
            for doc in results:
                search_results.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "distance": 0.0
                })
            return search_results
        else:
            results = self._collection.query(
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
        if VECTOR_STORE_TYPE == "supabase":
            response = self._client.table(self.collection_name).select("id", count="exact").execute()
            return len(response.data) if response.data else 0
        else:
            return self._collection.count()
    
    def clear_collection(self):
        """清空集合中的所有文档"""
        if VECTOR_STORE_TYPE == "supabase":
            self._client.table(self.collection_name).delete().neq("id", "").execute()
            print("已清空 Supabase 向量库")
        else:
            self._client.delete_collection(self.collection_name)
            self._collection = self._client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print("已清空 Chroma 向量库")
