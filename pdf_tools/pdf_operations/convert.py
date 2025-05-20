import os
import logging
import tempfile
from pathlib import Path
import img2pdf
from PIL import Image
import fitz  # PyMuPDF

# 尝试导入pdf2image，但不强制要求
try:
    from pdf2image import convert_from_path, pdfinfo_from_path
    HAVE_PDF2IMAGE = True
except (ImportError, ModuleNotFoundError):
    HAVE_PDF2IMAGE = False

logger = logging.getLogger(__name__)

def pdf_to_images(input_path, output_dir, dpi=300, format='jpg', first_page=None, last_page=None):
    """
    将PDF文件转换为图片
    
    参数:
        input_path (str): 输入PDF文件路径
        output_dir (str): 输出目录
        dpi (int): 输出图片的DPI（每英寸点数）
        format (str): 输出图片格式，'jpg'或'png'
        first_page (int): 起始页码（从1开始），为None表示从第一页开始
        last_page (int): 结束页码（从1开始），为None表示到最后一页
        
    返回:
        list: 生成的图片文件路径列表
    """
    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 首先尝试使用pdf2image（如果可用）
        if HAVE_PDF2IMAGE:
            try:
                return _pdf_to_images_pdf2image(input_path, output_dir, dpi, format, first_page, last_page)
            except Exception as e:
                logger.warning(f"使用pdf2image转换失败，尝试PyMuPDF: {str(e)}")
        
        # 使用PyMuPDF作为备选方案
        return _pdf_to_images_pymupdf(input_path, output_dir, dpi, format, first_page, last_page)
    except Exception as e:
        logger.error(f"PDF转图片出错: {str(e)}")
        raise

def _pdf_to_images_pdf2image(input_path, output_dir, dpi, format, first_page, last_page):
    """使用pdf2image实现PDF转图片"""
    # 获取PDF信息
    info = pdfinfo_from_path(input_path)
    max_pages = info["Pages"]
    
    # 验证页码范围
    if first_page is None:
        first_page = 1
    else:
        first_page = max(1, min(first_page, max_pages))
        
    if last_page is None:
        last_page = max_pages
    else:
        last_page = max(first_page, min(last_page, max_pages))
    
    # 转换页面范围
    pages = list(range(first_page, last_page + 1))
        
    # 生成文件名前缀
    base_name = Path(input_path).stem
    
    # 转换PDF为图片
    images = convert_from_path(
        input_path,
        dpi=dpi,
        first_page=first_page,
        last_page=last_page
    )
    
    # 保存图片
    output_paths = []
    for i, image in enumerate(images):
        page_num = pages[i]
        output_file = os.path.join(output_dir, f"{base_name}_page_{page_num}.{format}")
        
        # 选择合适的保存方法
        if format.lower() == 'jpg' or format.lower() == 'jpeg':
            image.save(output_file, 'JPEG', quality=95)
        else:  # 默认使用PNG
            image.save(output_file, 'PNG')
            
        output_paths.append(output_file)
        logger.info(f"已保存第{page_num}页为{output_file}")
    
    return output_paths

def _pdf_to_images_pymupdf(input_path, output_dir, dpi, format, first_page, last_page):
    """使用PyMuPDF实现PDF转图片"""
    # 打开PDF文件
    pdf = fitz.open(input_path)
    max_pages = len(pdf)
    
    # 验证页码范围
    if first_page is None:
        first_page = 1
    else:
        first_page = max(1, min(first_page, max_pages))
        
    if last_page is None:
        last_page = max_pages
    else:
        last_page = max(first_page, min(last_page, max_pages))
    
    # 计算缩放因子（从DPI转换）
    zoom = dpi / 72.0  # PDF默认DPI是72
    
    # 生成文件名前缀
    base_name = Path(input_path).stem
    
    output_paths = []
    # 转换指定范围的页面
    for page_num in range(first_page - 1, last_page):  # PyMuPDF页码从0开始
        page = pdf.load_page(page_num)
        
        # 获取页面像素矩阵
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        
        # 设置输出文件路径
        output_file = os.path.join(output_dir, f"{base_name}_page_{page_num + 1}.{format}")
        
        # 保存图片
        if format.lower() in ('jpg', 'jpeg'):
            pix.save(output_file, output="jpeg")  # PyMuPDF不支持jpg_quality参数
        else:  # 默认使用PNG
            pix.save(output_file, output="png")
        
        output_paths.append(output_file)
        logger.info(f"已保存第{page_num + 1}页为{output_file}")
    
    pdf.close()
    return output_paths

def images_to_pdf(image_paths, output_path, quality=95):
    """
    将多张图片合并为一个PDF文件
    
    参数:
        image_paths (list): 图片文件路径列表
        output_path (str): 输出PDF文件路径
        quality (int): JPEG压缩质量，仅对JPEG图片有效
        
    返回:
        bool: 操作是否成功
    """
    try:
        # 检查文件是否存在且为图片
        processed_images = []
        temp_files = []
        
        for img_path in image_paths:
            try:
                # 尝试以图片方式打开文件
                with Image.open(img_path) as img:
                    logger.info(f"打开图片: {img_path}, 格式: {img.format}")
                    # 如果是非标准格式，转换为JPEG保存（img2pdf不支持所有格式）
                    if img.format not in ["JPEG", "PNG", "TIFF"]:
                        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                        temp_files.append(temp_file.name)
                        img.convert('RGB').save(temp_file.name, 'JPEG', quality=quality)
                        processed_images.append(temp_file.name)
                    else:
                        processed_images.append(img_path)
            except IOError as e:
                logger.error(f"无法打开图片文件: {img_path}, 错误: {e}")
                continue
        
        # 检查是否有有效图片
        if not processed_images:
            logger.error("没有有效的图片文件可以转换")
            return False
        
        # 转换图片到PDF
        try:
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(processed_images))
        except Exception as e:
            logger.error(f"img2pdf合成PDF失败: {e}")
            return False
        
        # 清理临时文件
        for tmp_file in temp_files:
            os.unlink(tmp_file)
            
        logger.info(f"已合并{len(processed_images)}张图片为PDF: {output_path}")
        return True
    except Exception as e:
        logger.error(f"图片转PDF出错: {str(e)}")
        # 清理临时文件
        for tmp_file in temp_files:
            if os.path.exists(tmp_file):
                os.unlink(tmp_file)
        return False 