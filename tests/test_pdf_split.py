import os
import pytest
import tempfile
from PyPDF2 import PdfReader
from pdf_tools.pdf_operations.split import split_pdf_to_single_pages, extract_pages

# 创建一个测试用的PDF文件
def create_test_pdf(pages=3):
    """创建一个测试用的多页PDF文件"""
    from reportlab.pdfgen import canvas
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        temp_path = tmp.name
    
    # 创建一个3页的PDF
    c = canvas.Canvas(temp_path)
    for i in range(pages):
        c.drawString(100, 100, f"This is page {i+1}")
        c.showPage()
    c.save()
    
    return temp_path

class TestPdfSplit:
    
    def setup_method(self):
        # 创建测试文件和目录
        self.test_pdf_path = create_test_pdf()
        self.output_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        # 清理测试文件和目录
        if os.path.exists(self.test_pdf_path):
            os.unlink(self.test_pdf_path)
        
        # 删除output_dir中的所有文件
        for filename in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        
        # 删除目录
        os.rmdir(self.output_dir)
    
    def test_split_pdf_to_single_pages(self):
        """测试将PDF拆分为单页的功能"""
        result_files = split_pdf_to_single_pages(self.test_pdf_path, self.output_dir)
        
        # 检查是否生成了3个文件
        assert len(result_files) == 3
        
        # 检查每个生成的文件是否都是单页PDF
        for file_path in result_files:
            reader = PdfReader(file_path)
            assert len(reader.pages) == 1
    
    def test_extract_pages(self):
        """测试提取指定页码的功能"""
        output_path = os.path.join(self.output_dir, "extracted.pdf")
        
        # 提取第1页和第3页
        result = extract_pages(self.test_pdf_path, output_path, [1, 3])
        
        # 检查操作是否成功
        assert result is True
        
        # 检查生成的文件是否包含2页
        reader = PdfReader(output_path)
        assert len(reader.pages) == 2
    
    def test_extract_invalid_pages(self):
        """测试提取无效页码时的行为"""
        output_path = os.path.join(self.output_dir, "extracted_invalid.pdf")
        
        # 尝试提取第4页（超出范围）
        result = extract_pages(self.test_pdf_path, output_path, [1, 4])
        
        # 检查操作是否失败
        assert result is False
        
        # 检查是否没有生成文件
        assert not os.path.exists(output_path) 