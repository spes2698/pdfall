import os
import logging
from PyPDF2 import PdfReader, PdfWriter
from pikepdf import Pdf, Encryption

logger = logging.getLogger(__name__)

def encrypt_pdf(input_path, output_path, user_password, owner_password=None):
    """
    为PDF文件添加密码保护
    
    参数:
        input_path (str): 输入PDF文件路径
        output_path (str): 输出PDF文件路径
        user_password (str): 用户密码（打开文档需要）
        owner_password (str, optional): 所有者密码（编辑文档需要）
        
    返回:
        bool: 操作是否成功
    """
    if owner_password is None:
        owner_password = user_password
        
    try:
        # 使用PyPDF2加密
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # 复制所有页面
        for page in reader.pages:
            writer.add_page(page)
            
        # 设置加密
        try:
            # 尝试新版API (PyPDF2 >= 2.0)
            writer.encrypt(user_password=user_password, owner_password=owner_password)
        except TypeError:
            # 尝试旧版API
            writer.encrypt(user_pwd=user_password, owner_pwd=owner_password)
        
        # 保存加密后的PDF
        with open(output_path, "wb") as f:
            writer.write(f)
            
        logger.info(f"成功加密PDF: {output_path}")
        return True
    except Exception as e:
        logger.error(f"加密PDF时出错: {str(e)}")
        return False

def decrypt_pdf(input_path, output_path, password):
    """
    移除PDF文件的密码保护
    
    参数:
        input_path (str): 输入PDF文件路径
        output_path (str): 输出PDF文件路径
        password (str): PDF密码
        
    返回:
        bool: 操作是否成功
    """
    try:
        # 尝试使用pikepdf解密
        try:
            with Pdf.open(input_path, password=password) as pdf:
                pdf.save(output_path)
                logger.info(f"成功使用pikepdf解密PDF: {output_path}")
                return True
        except Exception as e:
            logger.warning(f"使用pikepdf解密失败，尝试使用PyPDF2: {str(e)}")
            
        # 如果pikepdf失败，尝试使用PyPDF2
        reader = PdfReader(input_path)
        if reader.is_encrypted:
            success = reader.decrypt(password)
            if not success:
                logger.error("密码错误，无法解密PDF")
                return False
        
        writer = PdfWriter()
        
        # 复制所有页面
        for page in reader.pages:
            writer.add_page(page)
        
        # 保存解密后的PDF
        with open(output_path, "wb") as f:
            writer.write(f)
            
        logger.info(f"成功使用PyPDF2解密PDF: {output_path}")
        return True
    except Exception as e:
        logger.error(f"解密PDF时出错: {str(e)}")
        return False 