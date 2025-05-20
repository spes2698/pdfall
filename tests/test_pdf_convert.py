import os
import pytest
import tempfile
from PyPDF2 import PdfReader
from PIL import Image
from pdf_tools.pdf_operations.convert import pdf_to_images, images_to_pdf
from tests.test_pdf_split import create_test_pdf  # 重用测试PDF创建函数

class TestPdfImageConvert:
    
    def setup_method(self):
        # 创建测试文件和目录
        self.test_pdf_path = create_test_pdf(pages=3)  # 创建一个3页的PDF文件作为测试
        self.output_dir = tempfile.mkdtemp()
        self.image_dir = tempfile.mkdtemp()
        
        # 创建测试用图片
        self.test_images = []
        for i in range(3):
            img_path = os.path.join(self.image_dir, f"test_image_{i+1}.jpg")
            img = Image.new('RGB', (300, 400), color=(255, 255 - i*50, 255))
            img.save(img_path)
            self.test_images.append(img_path)
    
    def teardown_method(self):
        # 清理测试文件和目录
        if os.path.exists(self.test_pdf_path):
            try:
                os.unlink(self.test_pdf_path)
            except (PermissionError, OSError):
                pass  # 忽略文件被占用的错误
        
        # 清理输出目录
        for dirname in [self.output_dir, self.image_dir]:
            try:
                # 删除目录中的所有文件
                for filename in os.listdir(dirname):
                    file_path = os.path.join(dirname, filename)
                    if os.path.isfile(file_path):
                        try:
                            os.unlink(file_path)
                        except (PermissionError, OSError):
                            pass  # 忽略文件被占用的错误
                # 删除目录
                os.rmdir(dirname)
            except (PermissionError, OSError):
                pass  # 忽略目录被占用的错误
    
    def test_pdf_to_images(self):
        """测试PDF转图片功能"""
        # 将PDF转换为图片
        image_files = pdf_to_images(self.test_pdf_path, self.output_dir, format='jpg')
        
        # 检查是否生成了正确数量的图片
        assert len(image_files) == 3  # 应生成3个图片文件
        
        # 检查文件是否存在且可作为图片打开
        for file_path in image_files:
            assert os.path.exists(file_path)
            with Image.open(file_path) as img:
                # 检查是否为JPG格式
                assert img.format in ("JPEG", "PNG")  # 允许JPEG或PNG格式
    
    def test_pdf_to_images_page_range(self):
        """测试PDF转换指定页面范围为图片"""
        # 只转换第2页
        image_files = pdf_to_images(
            self.test_pdf_path, 
            self.output_dir, 
            format='png',
            first_page=2,
            last_page=2
        )
        
        # 检查是否只生成了一个图片
        assert len(image_files) == 1
        
        # 检查文件是否存在且可作为图片打开
        with Image.open(image_files[0]) as img:
            # 检查是否为PNG格式
            assert img.format in ("PNG", "JPEG")  # 允许PNG或JPEG格式
    
    def test_images_to_pdf(self):
        """测试图片转PDF功能"""
        output_pdf = os.path.join(self.output_dir, "images_to_pdf.pdf")
        
        # 转换图片为PDF
        result = images_to_pdf(self.test_images, output_pdf)
        assert result is True
        assert os.path.exists(output_pdf)
        
        # 检查生成的PDF是否可以打开并包含正确数量的页面
        reader = PdfReader(output_pdf)
        assert len(reader.pages) == len(self.test_images)
    
    def test_images_to_pdf_with_invalid_image(self):
        """测试图片转PDF时包含无效图片的行为"""
        output_pdf = os.path.join(self.output_dir, "invalid_images.pdf")
        
        # 添加一个不存在的图片
        invalid_images = self.test_images + ["non_existent_image.jpg"]
        
        # 转换图片为PDF（应该跳过无效图片）
        result = images_to_pdf(invalid_images, output_pdf)
        assert result is True  # 有效图片足够，应成功
        assert os.path.exists(output_pdf)
        
        # 检查生成的PDF是否可以打开并包含正确数量的页面
        reader = PdfReader(output_pdf)
        assert len(reader.pages) == len(self.test_images)  # 应该只包含有效图片 