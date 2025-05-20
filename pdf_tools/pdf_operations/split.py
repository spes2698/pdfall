import os
import logging
from PyPDF2 import PdfReader, PdfWriter
from pikepdf import Pdf

logger = logging.getLogger(__name__)

def split_pdf_to_single_pages(input_path, output_dir):
    """
    将PDF文件拆分为单页PDF文件
    
    参数:
        input_path (str): 输入PDF文件路径
        output_dir (str): 输出目录
        
    返回:
        list: 生成的PDF文件路径列表
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    try:
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        
        if total_pages == 0:
            logger.error(f"PDF文件 {input_path} 没有任何页面")
            return []
            
        output_files = []
        
        # 文件名前缀（不包含路径和扩展名）
        base_name = os.path.basename(input_path)
        base_name = os.path.splitext(base_name)[0]
        
        # 拆分每一页
        for i in range(total_pages):
            output_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.pdf")
            
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
                
            output_files.append(output_path)
            logger.info(f"Page {i+1} saved as {output_path}")
            
        return output_files
    except Exception as e:
        logger.error(f"拆分PDF时出错: {str(e)}")
        raise
        
def extract_pages(input_path, output_path, page_numbers):
    """
    从PDF文件中提取指定页码的页面
    
    参数:
        input_path (str): 输入PDF文件路径
        output_path (str): 输出PDF文件路径
        page_numbers (list): 要提取的页码列表（从1开始）
        
    返回:
        bool: 操作是否成功
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        total_pages = len(reader.pages)
        
        # 检查页码是否有效
        invalid_pages = [p for p in page_numbers if p < 1 or p > total_pages]
        if invalid_pages:
            logger.error(f"无效页码: {invalid_pages}. 有效范围: 1-{total_pages}")
            return False
            
        # 添加选中的页面
        for page_num in sorted(page_numbers):
            writer.add_page(reader.pages[page_num-1])  # 页码从0开始，但用户输入从1开始
            
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
            
        logger.info(f"已提取页面 {page_numbers} 到 {output_path}")
        return True
    except Exception as e:
        logger.error(f"提取页面时出错: {str(e)}")
        return False 