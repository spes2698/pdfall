import os
import logging
import subprocess
import tempfile
from pikepdf import Pdf
import pikepdf

logger = logging.getLogger(__name__)

def compress_pdf_ghostscript(input_path, output_path, quality='default', resolution=100):
    """
    使用GhostScript压缩PDF文件
    
    参数:
        input_path (str): 输入PDF文件路径
        output_path (str): 输出PDF文件路径
        quality (str): 压缩质量，可选值为 'default', 'screen', 'ebook', 'printer', 'prepress'
        resolution (int): 分辨率
        
    返回:
        bool: 操作是否成功
    """
    # 质量设置
    quality_settings = {
        'screen': '/screen',         # 屏幕质量 - 72dpi，低质量
        'ebook': '/ebook',           # 电子书质量 - 150dpi，中等质量
        'printer': '/printer',       # 打印机质量 - 300dpi，高质量
        'prepress': '/prepress',     # 印前质量 - 300dpi，保留所有信息，较大
        'default': '/default'        # 平衡质量和文件大小
    }
    
    # 使用默认质量如果未指定有效的质量
    setting = quality_settings.get(quality, '/default')
    
    try:
        # 检查是否安装了GhostScript
        try:
            # 在Windows上检查gswin64c.exe或gswin32c.exe
            if os.name == 'nt':
                gs_cmd = None
                for cmd in ['gswin64c.exe', 'gswin32c.exe', 'gs']:
                    try:
                        subprocess.run([cmd, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        gs_cmd = cmd
                        break
                    except FileNotFoundError:
                        continue
                if gs_cmd is None:
                    logger.error('GhostScript未安装或不可用')
                    return False
            else:
                # 在Linux/Mac上检查gs
                subprocess.run(['gs', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                gs_cmd = 'gs'
        except FileNotFoundError:
            logger.error('GhostScript未安装或不可用')
            return False
        
        # 构建GhostScript命令
        command = [
            gs_cmd,
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=' + setting,
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            '-dAutoFilterColorImages=false',
            '-dAutoFilterGrayImages=false',
            '-dColorImageDownsampleType=/Bicubic',
            f'-dColorImageResolution={resolution}',
            '-dGrayImageDownsampleType=/Bicubic',
            f'-dGrayImageResolution={resolution}',
            '-dMonoImageDownsampleType=/Bicubic',
            f'-dMonoImageResolution={resolution}',
            '-sOutputFile=' + output_path,
            input_path
        ]
        
        # 执行命令
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if process.returncode != 0:
            logger.error(f'GhostScript压缩失败: {process.stderr.decode()}')
            logger.error(f'GhostScript命令: {command}')
            return False
            
        logger.info(f'已使用GhostScript压缩PDF: {output_path}')
        return True
    except Exception as e:
        logger.error(f'使用GhostScript压缩PDF时出错: {str(e)}', exc_info=True)
        return False

def compress_pdf_pikepdf(input_path, output_path):
    """
    使用pikepdf压缩PDF文件
    
    参数:
        input_path (str): 输入PDF文件路径
        output_path (str): 输出PDF文件路径
        
    返回:
        bool: 操作是否成功
    """
    try:
        # 打开PDF文件
        with pikepdf.Pdf.open(input_path) as pdf:
            # 保存时应用压缩
            pdf.save(output_path, 
                     compress_streams=True,     # 压缩内容流
                     object_stream_mode=pikepdf.ObjectStreamMode.generate)  # 使用对象流
        
        logger.info(f'已使用pikepdf压缩PDF: {output_path}')
        return True
    except Exception as e:
        logger.error(f'使用pikepdf压缩PDF时出错: {str(e)}', exc_info=True)
        return False

def compress_pdf(input_path, output_path, quality='default'):
    """
    压缩PDF文件，自动选择最佳方法
    
    参数:
        input_path (str): 输入PDF文件路径
        output_path (str): 输出PDF文件路径
        quality (str): 压缩质量，可选值为 'default', 'screen', 'ebook', 'printer', 'prepress'
        
    返回:
        bool: 操作是否成功
    """
    # 根据quality选择分辨率
    quality_resolution = {
        'screen': 72,
        'ebook': 100,
        'printer': 150,
        'prepress': 300,
        'default': 100
    }
    resolution = quality_resolution.get(quality, 100)
    result = compress_pdf_ghostscript(input_path, output_path, quality, resolution)
    if not result:
        logger.error(f"GhostScript压缩失败，尝试使用pikepdf，输入文件: {input_path}")
        result = compress_pdf_pikepdf(input_path, output_path)
        if not result:
            logger.error(f"pikepdf压缩也失败，输入文件: {input_path}")
    return result 