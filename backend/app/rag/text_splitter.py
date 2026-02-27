from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextSplitter:
    """文本分块器，使用递归字符分割策略"""
    
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
        separators: List[str] = None
    ):
        """
        初始化文本分块器
        
        Args:
            chunk_size: 每个分块的最大字符数（默认800，适合中文文档）
            chunk_overlap: 分块之间的重叠字符数（默认150，保持上下文连贯）
            separators: 分隔符列表，优化中文文档分割
        """
        if separators is None:
            # 优化中文文档分隔符顺序：优先按段落和章节分割
            separators = [
                "\n\n\n",  # 三级换行（章节分隔）
                "\n\n",    # 段落分隔
                "\n",      # 行分隔
                "。\n",     # 句末换行（保持段落完整性）
                "。",      # 句号
                "；",      # 分号
                "！",      # 感叹号
                "？",      # 问号
                "\u3002",  # 中文句号（全角）
                " ",       # 空格
                ""         # 最后按字符分割
            ]
        
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
