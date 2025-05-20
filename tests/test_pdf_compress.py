import os
import pytest
import tempfile
from PyPDF2 import PdfReader
from pdf_tools.pdf_operations.compress import compress_pdf, compress_pdf_pikepdf
from tests.test_pdf_split import create_test_pdf  # 重用测试PDF创建函数

class TestPdfCompress:
    
    def setup_method(self):
        # 创建测试文件和目录
        self.test_pdf_path = create_test_pdf(pages=5)  # 创建一个5页的PDF文件作为测试
        self.output_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        # 清理测试文件和目录
        if os.path.exists(self.test_pdf_path):
            try:
                os.unlink(self.test_pdf_path)
            except (PermissionError, OSError):
                pass  # 忽略文件被占用的错误
        
        # 删除output_dir中的所有文件
        try:
            for filename in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        os.unlink(file_path)
                    except (PermissionError, OSError):
                        pass  # 忽略文件被占用的错误
            
            # 删除目录
            os.rmdir(self.output_dir)
        except (PermissionError, OSError):
            pass  # 忽略目录被占用的错误
    
    @pytest.mark.skip(reason="需要安装pikepdf才能运行此测试")
    def test_compress_pdf_pikepdf(self):
        """测试使用pikepdf压缩PDF"""
        compressed_path = os.path.join(self.output_dir, "compressed_pikepdf.pdf")
        
        # 压缩PDF
        result = compress_pdf_pikepdf(self.test_pdf_path, compressed_path)
        assert result is True
        assert os.path.exists(compressed_path)
        
        # 检查是否可以正常打开压缩后的文件
        reader = PdfReader(compressed_path)
        assert len(reader.pages) == 5  # 页数应该保持不变
        
        # 检查文件大小是否有变化
        original_size = os.path.getsize(self.test_pdf_path)
        compressed_size = os.path.getsize(compressed_path)
        print(f"原始文件大小: {original_size} 字节")
        print(f"压缩文件大小: {compressed_size} 字节")
        
        # 文件可能会略有增加或减少，因为测试文件很小且没有大图片
        # 主要测试功能是否正常工作
    
    @pytest.mark.skip(reason="需要安装GhostScript或pikepdf才能运行此测试")
    def test_compress_pdf_auto(self):
        """测试自动选择压缩方法"""
        compressed_path = os.path.join(self.output_dir, "compressed_auto.pdf")
        
        # 压缩PDF
        result = compress_pdf(self.test_pdf_path, compressed_path)
        assert result is True
        assert os.path.exists(compressed_path)
        
        # 检查是否可以正常打开压缩后的文件
        reader = PdfReader(compressed_path)
        assert len(reader.pages) == 5  # 页数应该保持不变 
        
        # 检查文件大小是否变小（或至少不会变大太多）
        original_size = os.path.getsize(self.test_pdf_path)
        compressed_size = os.path.getsize(compressed_path)
        
        # 压缩后的文件不应该比原文件大太多（允许有最多10%的增长）
        assert compressed_size <= original_size * 1.1 