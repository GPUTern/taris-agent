"""文档解析工具模块

此模块提供了各种文档格式的解析功能，包括 PDF、DOCX、TXT 等格式。
"""

import base64
import io
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union, Optional


class DocumentParser(ABC):
    """文档解析器基类"""
    
    @abstractmethod
    def parse(self, file_bytes: bytes, filename: str) -> str:
        """解析文档内容
        
        Args:
            file_bytes: 文件的字节数据
            filename: 文件名
            
        Returns:
            str: 解析后的文本内容
        """
        pass
    
    @abstractmethod
    def supports(self, mime_type: str, filename: str) -> bool:
        """检查是否支持解析该类型的文件
        
        Args:
            mime_type: 文件的 MIME 类型
            filename: 文件名
            
        Returns:
            bool: 如果支持返回 True，否则返回 False
        """
        pass


class PDFParser(DocumentParser):
    """PDF 文档解析器"""
    
    def parse(self, file_bytes: bytes, filename: str) -> str:
        """解析 PDF 文档内容
        
        Args:
            file_bytes: PDF 文件的字节数据
            filename: 文件名
            
        Returns:
            str: 解析后的文本内容
        """
        try:
            # 尝试导入 PyPDF2 进行 PDF 处理
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
            except ImportError:
                return "[PDF 处理需要安装 PyPDF2 库]"
        except Exception as e:
            return f"[PDF 处理错误: {str(e)}]"
    
    def supports(self, mime_type: str, filename: str) -> bool:
        """检查是否支持解析 PDF 文件
        
        Args:
            mime_type: 文件的 MIME 类型
            filename: 文件名
            
        Returns:
            bool: 如果支持返回 True，否则返回 False
        """
        return mime_type == "application/pdf" or filename.lower().endswith('.pdf')


class DocxParser(DocumentParser):
    """DOCX 文档解析器"""
    
    def parse(self, file_bytes: bytes, filename: str) -> str:
        """解析 DOCX 文档内容
        
        Args:
            file_bytes: DOCX 文件的字节数据
            filename: 文件名
            
        Returns:
            str: 解析后的文本内容
        """
        try:
            # 尝试导入 python-docx 进行 DOCX 处理
            try:
                from docx import Document
                doc = Document(io.BytesIO(file_bytes))
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text.strip()
            except ImportError:
                return "[DOCX 处理需要安装 python-docx 库]"
        except Exception as e:
            return f"[DOCX 处理错误: {str(e)}]"
    
    def supports(self, mime_type: str, filename: str) -> bool:
        """检查是否支持解析 DOCX 文件
        
        Args:
            mime_type: 文件的 MIME 类型
            filename: 文件名
            
        Returns:
            bool: 如果支持返回 True，否则返回 False
        """
        return (mime_type in ["application/msword",
                             "application/vnd.openxmlformats-officedocument.wordprocessingml.document"] or
                filename.lower().endswith('.doc') or 
                filename.lower().endswith('.docx'))


class TextParser(DocumentParser):
    """文本文件解析器"""
    
    def parse(self, file_bytes: bytes, filename: str) -> str:
        """解析文本文件内容
        
        Args:
            file_bytes: 文本文件的字节数据
            filename: 文件名
            
        Returns:
            str: 解析后的文本内容
        """
        try:
            # 尝试使用 UTF-8 解码
            try:
                return file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                # 如果 UTF-8 失败，尝试其他编码
                try:
                    return file_bytes.decode("gbk")
                except UnicodeDecodeError:
                    try:
                        return file_bytes.decode("latin-1")
                    except UnicodeDecodeError:
                        return f"[无法解码文本文件 {filename}]"
        except Exception as e:
            return f"[文本文件处理错误: {str(e)}]"
    
    def supports(self, mime_type: str, filename: str) -> bool:
        """检查是否支持解析文本文件
        
        Args:
            mime_type: 文件的 MIME 类型
            filename: 文件名
            
        Returns:
            bool: 如果支持返回 True，否则返回 False
        """
        return (mime_type.startswith("text/") or
                filename.lower().endswith('.txt') or
                filename.lower().endswith('.md') or
                filename.lower().endswith('.csv') or
                filename.lower().endswith('.json') or
                filename.lower().endswith('.xml') or
                filename.lower().endswith('.html') or
                filename.lower().endswith('.htm'))


class DocumentParserFactory:
    """文档解析器工厂类"""
    
    def __init__(self):
        self._parsers = [
            PDFParser(),
            DocxParser(),
            TextParser()
        ]
    
    def get_parser(self, mime_type: str, filename: str) -> Optional[DocumentParser]:
        """根据文件类型获取合适的解析器
        
        Args:
            mime_type: 文件的 MIME 类型
            filename: 文件名
            
        Returns:
            DocumentParser: 合适的解析器，如果没有找到则返回 None
        """
        for parser in self._parsers:
            if parser.supports(mime_type, filename):
                return parser
        return None
    
    def register_parser(self, parser: DocumentParser):
        """注册新的解析器
        
        Args:
            parser: 要注册的解析器
        """
        self._parsers.append(parser)


# 全局解析器工厂实例
_parser_factory = DocumentParserFactory()


def extract_file_content(base64_data: str, filename: str, mime_type: str) -> str:
    """从 base64 编码的文件中提取内容
    
    Args:
        base64_data: base64 编码的文件数据
        filename: 文件名
        mime_type: 文件的 MIME 类型
        
    Returns:
        str: 提取的文本内容
    """
    try:
        # 解码 base64 数据
        file_bytes = base64.b64decode(base64_data)
        
        # 获取合适的解析器
        parser = _parser_factory.get_parser(mime_type, filename)
        if parser is None:
            return f"[不支持的文件类型: {mime_type} for {filename}]"
        
        # 解析文件内容
        return parser.parse(file_bytes, filename)
        
    except Exception as e:
        return f"[处理文件 {filename} 时出错: {str(e)}]"


def extract_pdf_content(file_bytes: bytes) -> str:
    """从 PDF 文件中提取文本内容
    
    Args:
        file_bytes: PDF 文件的字节数据
        
    Returns:
        str: 提取的文本内容
    """
    parser = PDFParser()
    return parser.parse(file_bytes, "document.pdf")


def extract_docx_content(file_bytes: bytes) -> str:
    """从 DOCX 文件中提取文本内容
    
    Args:
        file_bytes: DOCX 文件的字节数据
        
    Returns:
        str: 提取的文本内容
    """
    parser = DocxParser()
    return parser.parse(file_bytes, "document.docx")


def register_parser(parser: DocumentParser):
    """注册新的文档解析器
    
    Args:
        parser: 要注册的解析器
    """
    _parser_factory.register_parser(parser)