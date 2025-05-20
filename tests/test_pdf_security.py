import os
import pytest
import tempfile
from PyPDF2 import PdfReader
from pdf_tools.pdf_operations.security import encrypt_pdf, decrypt_pdf
from tests.test_pdf_split import create_test_pdf  # 重用测试PDF创建函数

class TestPdfSecurity:
    
    def setup_method(self):
        # 创建测试文件和目录
        self.test_pdf_path = create_test_pdf(pages=3)
        self.output_dir = tempfile.mkdtemp()
        self.test_password = "testpassword123"
    
    def teardown_method(self):
        # 清理测试文件和目录
        if os.path.exists(self.test_pdf_path):
            try:
                os.unlink(self.test_pdf_path)
            except PermissionError:
                pass  # 忽略文件被占用的错误
        
        # 删除output_dir中的所有文件
        for filename in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, filename)
            if os.path.isfile(file_path):
                try:
                    os.unlink(file_path)
                except PermissionError:
                    pass  # 忽略文件被占用的错误
        
        # 删除目录
        try:
            os.rmdir(self.output_dir)
        except (PermissionError, OSError):
            pass  # 忽略目录被占用的错误
    
    def test_encrypt_pdf(self):
        """测试PDF加密功能"""
        encrypted_path = os.path.join(self.output_dir, "encrypted.pdf")
        
        # 加密PDF
        result = encrypt_pdf(self.test_pdf_path, encrypted_path, self.test_password)
        assert result is True
        
        # 验证文件已加密
        reader = PdfReader(encrypted_path)
        assert reader.is_encrypted
        
    def test_decrypt_pdf(self):
        """测试PDF解密功能"""
        # 首先加密PDF
        encrypted_path = os.path.join(self.output_dir, "to_decrypt.pdf")
        encrypt_result = encrypt_pdf(self.test_pdf_path, encrypted_path, self.test_password)
        assert encrypt_result is True
        
        # 确保加密成功
        reader = PdfReader(encrypted_path)
        assert reader.is_encrypted

        # 然后解密
        decrypted_path = os.path.join(self.output_dir, "decrypted.pdf")
        result = decrypt_pdf(encrypted_path, decrypted_path, self.test_password)
        assert result is True
        
        # 验证文件已解密
        reader = PdfReader(decrypted_path)
        assert not reader.is_encrypted
    
    def test_decrypt_with_wrong_password(self):
        """测试使用错误密码解密PDF"""
        # 首先加密PDF
        encrypted_path = os.path.join(self.output_dir, "wrong_pwd.pdf")
        encrypt_pdf(self.test_pdf_path, encrypted_path, self.test_password)
        
        # 使用错误密码解密
        decrypted_path = os.path.join(self.output_dir, "should_fail.pdf")
        result = decrypt_pdf(encrypted_path, decrypted_path, "wrongpassword")
        assert result is False 