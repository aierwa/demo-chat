import os
from typing import List
from pypdf import PdfReader


class DocumentLoader:
    """文档加载器，支持加载PDF文档"""
    
    def __init__(self, resources_dir: str = None):
        """
        初始化文档加载器
        
        Args:
            resources_dir: 资源目录路径，默认为项目根目录下的resources
        """
        if resources_dir is None:
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            resources_dir = os.path.join(current_dir, "resources")
        
        self.resources_dir = resources_dir
    
    def load_pdf(self, file_path: str) -> str:
        """
        加载PDF文件内容
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            PDF文件的文本内容
        """
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.resources_dir, file_path)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        reader = PdfReader(file_path)
        text_content = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_content.append(text)
        
        return "\n\n".join(text_content)
    
    def load_all_pdfs(self) -> List[tuple]:
        """
        加载resources目录下所有PDF文件
        
        Returns:
            包含(文件名, 文件内容)元组的列表
        """
        documents = []
        
        if not os.path.exists(self.resources_dir):
            print(f"资源目录不存在: {self.resources_dir}")
            return documents
        
        for filename in os.listdir(self.resources_dir):
            if filename.lower().endswith('.pdf'):
                try:
                    file_path = os.path.join(self.resources_dir, filename)
                    content = self.load_pdf(file_path)
                    documents.append((filename, content))
                    print(f"成功加载PDF文件: {filename}")
                except Exception as e:
                    print(f"加载PDF文件失败 {filename}: {e}")
        
        return documents
