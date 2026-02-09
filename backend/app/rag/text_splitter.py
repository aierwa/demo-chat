from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextSplitter:
    """文本分块器，使用递归字符分割策略"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None
    ):
        """
        初始化文本分块器
        
        Args:
            chunk_size: 每个分块的最大字符数
            chunk_overlap: 分块之间的重叠字符数
            separators: 分隔符列表，默认为["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        """
        if separators is None:
            separators = ["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
        )
    
    def split_text(self, text: str) -> List[str]:
        """
        将文本分割成多个块
        
        Args:
            text: 待分割的文本
            
        Returns:
            分割后的文本块列表
        """
        return self.splitter.split_text(text)
    
    def split_documents(self, documents: List[tuple]) -> List[dict]:
        """
        分割多个文档
        
        Args:
            documents: 包含(文件名, 文件内容)元组的列表
            
        Returns:
            包含分块信息的字典列表，每个字典包含:
            - content: 分块内容
            - source: 来源文件名
            - chunk_id: 分块ID
        """
        all_chunks = []
        
        for filename, content in documents:
            chunks = self.split_text(content)
            for idx, chunk in enumerate(chunks):
                all_chunks.append({
                    "content": chunk,
                    "source": filename,
                    "chunk_id": f"{filename}_{idx}"
                })
        
        return all_chunks
