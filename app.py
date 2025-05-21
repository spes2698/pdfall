import os
import uuid
import logging
import zipfile
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, send_file
from werkzeug.utils import secure_filename
from pdf2docx import Converter
from PyPDF2 import PdfMerger
from pdf_tools.pdf_operations.operations import (
    split_pdf_to_single_pages,
    extract_pages,
    encrypt_pdf,
    decrypt_pdf,
    compress_pdf,
    pdf_to_images,
    images_to_pdf
)
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from PIL import Image
import io
import base64
import qrcode
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.request.AlipayTradePrecreateRequest import AlipayTradePrecreateRequest
from alipay_config import ALIPAY_APP_ID, ALIPAY_PRIVATE_KEY, ALIPAY_PUBLIC_KEY

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['CONVERTED_FOLDER'] = 'converted'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png', 'tiff'}
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64MB
app.config['FILE_EXPIRY'] = 20  # 文件保存20分钟后自动销毁

# 确保上传和转换目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

# 清理过期文件的任务
def cleanup_expired_files():
    with app.app_context():
        current_time = datetime.now()
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (current_time - file_modified_time).total_seconds() > app.config['FILE_EXPIRY'] * 60:
                    os.remove(file_path)
                    print(f"已删除过期文件: {filename}")

# 启动定时清理任务
scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_expired_files, 'interval', minutes=10)
scheduler.start()

def allowed_file(filename, extensions=None):
    """检查文件扩展名是否被允许"""
    if extensions is None:
        extensions = app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge')
def merge_page():
    return render_template('merge.html')

@app.route('/split')
def split_page():
    return render_template('split.html')

@app.route('/security')
def security_page():
    return render_template('security.html')

@app.route('/compress')
def compress_page():
    return render_template('compress.html')

@app.route('/pdf2img')
def pdf_to_image_page():
    return render_template('pdf_to_image.html')

@app.route('/img2pdf')
def image_to_pdf_page():
    return render_template('image_to_pdf.html')

@app.route('/merge', methods=['POST'])
def merge_files():
    try:
        if 'files' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        # 检查所有文件是否都是PDF
        for file in files:
            if not allowed_file(file.filename, {'pdf'}):
                return jsonify({'success': False, 'message': '只允许上传PDF文件'})
        
        # 保存上传的文件
        saved_files = []
        for file in files:
            filename = secure_filename(file.filename)
            unique_id = str(uuid.uuid4())
            pdf_filename = f"{unique_id}_{filename}"
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
            file.save(pdf_path)
            saved_files.append(pdf_path)
        
        # 合并PDF文件
        merger = PdfMerger()
        for pdf_path in saved_files:
            merger.append(pdf_path)
        
        # 生成合并后的文件名
        merged_filename = f"merged_{uuid.uuid4()}.pdf"
        merged_path = os.path.join(app.config['CONVERTED_FOLDER'], merged_filename)
        
        # 保存合并后的文件
        merger.write(merged_path)
        merger.close()
        
        # 清理临时文件
        for pdf_path in saved_files:
            try:
                os.remove(pdf_path)
            except Exception as e:
                logger.error(f'删除临时文件失败: {str(e)}')
        
        return jsonify({
            'success': True,
            'download_url': url_for('get_file', filename=merged_filename),
            'filename': merged_filename
        })
        
    except Exception as e:
        logger.error(f'合并文件时出错: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': f'合并文件时出错: {str(e)}'})

@app.route('/batch_convert', methods=['POST'])
def batch_convert():
    try:
        if 'files' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        result_files = []
        for file in files:
            if not allowed_file(file.filename, {'pdf'}):
                return jsonify({'success': False, 'message': '只允许上传PDF文件'})
            original_filename = secure_filename(file.filename)
            if not original_filename.lower().endswith('.pdf'):
                original_filename += '.pdf'
            unique_id = str(uuid.uuid4())
            pdf_filename = f"{unique_id}_{original_filename}"
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
            file.save(pdf_path)
            word_filename = pdf_filename.rsplit('.', 1)[0] + '.docx'
            word_path = os.path.join(app.config['CONVERTED_FOLDER'], word_filename)
            try:
                cv = Converter(pdf_path)
                cv.convert(word_path)
                cv.close()
                result_files.append({
                    'filename': word_filename,
                    'download_url': url_for('get_file', filename=word_filename)
                })
            except Exception as e:
                return jsonify({'success': False, 'message': f'文件 {original_filename} 转换失败: {str(e)}'})
        return jsonify({'success': True, 'files': result_files})
    except Exception as e:
        return jsonify({'success': False, 'message': f'批量转换出错: {str(e)}'})

@app.route('/split_pdf', methods=['POST'])
def split_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        if not allowed_file(file.filename, {'pdf'}):
            return jsonify({'success': False, 'message': '只允许上传PDF文件'})
        
        # 保存上传的文件
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        pdf_filename = f"{unique_id}_{original_filename}"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        file.save(pdf_path)
        
        # 判断拆分模式
        split_mode = request.form.get('split_mode', 'all')
        
        if split_mode == 'all':
            # 拆分所有页面
            output_files = split_pdf_to_single_pages(pdf_path, app.config['CONVERTED_FOLDER'])
        else:
            # 提取指定页面
            try:
                pages = request.form.get('pages', '1').strip()
                page_numbers = [int(p) for p in pages.split(',') if p.strip()]
                
                if not page_numbers:
                    return jsonify({'success': False, 'message': '请指定至少一个页码'})
                
                output_filename = f"extracted_{unique_id}.pdf"
                output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
                
                success = extract_pages(pdf_path, output_path, page_numbers)
                if not success:
                    return jsonify({'success': False, 'message': '页码超出范围或格式错误'})
                    
                output_files = [output_path]
            except ValueError:
                return jsonify({'success': False, 'message': '页码必须为数字，多个页码用逗号分隔'})
        
        # 如果输出多个文件，创建一个zip文件
        if len(output_files) > 1:
            zip_filename = f"split_{unique_id}.zip"
            zip_path = os.path.join(app.config['CONVERTED_FOLDER'], zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in output_files:
                    zipf.write(file_path, os.path.basename(file_path))
            
            return jsonify({
                'success': True,
                'download_url': url_for('get_file', filename=zip_filename),
                'filename': zip_filename,
                'is_zip': True
            })
        else:
            # 只有一个文件，直接返回
            output_filename = os.path.basename(output_files[0])
            return jsonify({
                'success': True,
                'download_url': url_for('get_file', filename=output_filename),
                'filename': output_filename,
                'is_zip': False
            })
    except Exception as e:
        logger.error(f'拆分PDF时出错: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': f'拆分PDF时出错: {str(e)}'})

@app.route('/encrypt_pdf', methods=['POST'])
def encrypt_pdf_route():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        file = request.files['file']
        password = request.form.get('password')
        
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        if not allowed_file(file.filename, {'pdf'}):
            return jsonify({'success': False, 'message': '只允许上传PDF文件'})
        
        if not password:
            return jsonify({'success': False, 'message': '请提供密码'})
        
        # 保存上传的文件
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        pdf_filename = f"{unique_id}_{original_filename}"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        file.save(pdf_path)
        
        # 加密PDF
        output_filename = f"encrypted_{unique_id}.pdf"
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
        
        success = encrypt_pdf(pdf_path, output_path, password)
        
        if success:
            return jsonify({
                'success': True,
                'download_url': url_for('get_file', filename=output_filename),
                'filename': output_filename
            })
        else:
            return jsonify({'success': False, 'message': '加密PDF时出错'})
    except Exception as e:
        logger.error(f'加密PDF时出错: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': f'加密PDF时出错: {str(e)}'})

@app.route('/decrypt_pdf', methods=['POST'])
def decrypt_pdf_route():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        file = request.files['file']
        password = request.form.get('password')
        
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        if not allowed_file(file.filename, {'pdf'}):
            return jsonify({'success': False, 'message': '只允许上传PDF文件'})
        
        if not password:
            return jsonify({'success': False, 'message': '请提供密码'})
        
        # 保存上传的文件
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        pdf_filename = f"{unique_id}_{original_filename}"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        file.save(pdf_path)
        
        # 解密PDF
        output_filename = f"decrypted_{unique_id}.pdf"
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
        
        success = decrypt_pdf(pdf_path, output_path, password)
        
        if success:
            return jsonify({
                'success': True,
                'download_url': url_for('get_file', filename=output_filename),
                'filename': output_filename
            })
        else:
            return jsonify({'success': False, 'message': '密码错误或解密失败'})
    except Exception as e:
        logger.error(f'解密PDF时出错: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': f'解密PDF时出错: {str(e)}'})

@app.route('/compress_pdf', methods=['POST'])
def compress_pdf_route():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        if not allowed_file(file.filename, {'pdf'}):
            return jsonify({'success': False, 'message': '只允许上传PDF文件'})
        # 获取压缩质量
        quality = request.form.get('quality', 'default')
        # 保存上传的文件
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        pdf_filename = f"{unique_id}_{original_filename}"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        file.save(pdf_path)
        # 压缩PDF
        output_filename = f"compressed_{unique_id}.pdf"
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
        success = compress_pdf(pdf_path, output_path, quality=quality)
        if success:
            # 获取压缩前后的文件大小
            original_size = os.path.getsize(pdf_path)
            compressed_size = os.path.getsize(output_path)
            # 计算压缩比例
            compression_ratio = 100 - (compressed_size / original_size * 100) if original_size > 0 else 0
            return jsonify({
                'success': True,
                'download_url': url_for('get_file', filename=output_filename),
                'filename': output_filename,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': round(compression_ratio, 2)
            })
        else:
            return jsonify({'success': False, 'message': '压缩PDF时出错'})
    except Exception as e:
        logger.error(f'压缩PDF时出错: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': f'压缩PDF时出错: {str(e)}'})

@app.route('/pdf_to_images', methods=['POST'])
def pdf_to_images_route():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        if not allowed_file(file.filename, {'pdf'}):
            return jsonify({'success': False, 'message': '只允许上传PDF文件'})
        
        # 获取转换参数
        dpi = int(request.form.get('dpi', '300'))
        format = request.form.get('format', 'jpg')
        
        # 检查页码范围
        first_page = request.form.get('first_page')
        last_page = request.form.get('last_page')
        
        if first_page:
            try:
                first_page = int(first_page)
            except ValueError:
                return jsonify({'success': False, 'message': '起始页码必须为数字'})
        
        if last_page:
            try:
                last_page = int(last_page)
            except ValueError:
                return jsonify({'success': False, 'message': '结束页码必须为数字'})
        
        # 保存上传的文件
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        pdf_filename = f"{unique_id}_{original_filename}"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        file.save(pdf_path)
        
        # 创建输出目录
        output_dir = os.path.join(app.config['CONVERTED_FOLDER'], f"images_{unique_id}")
        os.makedirs(output_dir, exist_ok=True)
        
        # 转换PDF为图片
        image_files = pdf_to_images(pdf_path, output_dir, dpi, format, first_page, last_page)
        
        if not image_files:
            return jsonify({'success': False, 'message': '没有生成任何图片'})
        
        # 创建ZIP文件
        zip_filename = f"pdf_images_{unique_id}.zip"
        zip_path = os.path.join(app.config['CONVERTED_FOLDER'], zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in image_files:
                zipf.write(file_path, os.path.basename(file_path))
        
        return jsonify({
            'success': True,
            'download_url': url_for('get_file', filename=zip_filename),
            'filename': zip_filename,
            'image_count': len(image_files)
        })
    except Exception as e:
        logger.error(f'PDF转换为图片时出错: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': f'PDF转换为图片时出错: {str(e)}'})

@app.route('/images_to_pdf', methods=['POST'])
def images_to_pdf_route():
    try:
        if 'files' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        files = request.files.getlist('files')
        
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        # 检查所有文件是否都是图片
        image_extensions = {'jpg', 'jpeg', 'png', 'tiff'}
        for file in files:
            if not allowed_file(file.filename, image_extensions):
                return jsonify({'success': False, 'message': '只允许上传JPG、PNG或TIFF图片'})
        
        # 保存上传的文件
        saved_files = []
        for file in files:
            original_filename = secure_filename(file.filename)
            unique_id = str(uuid.uuid4())
            img_filename = f"{unique_id}_{original_filename}"
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
            file.save(img_path)
            saved_files.append(img_path)
        
        # 合并图片为PDF
        output_filename = f"images_to_pdf_{uuid.uuid4()}.pdf"
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
        
        success = images_to_pdf(saved_files, output_path)
        
        # 清理临时文件
        for img_path in saved_files:
            try:
                os.remove(img_path)
            except Exception as e:
                logger.error(f'删除临时文件失败: {str(e)}')
        
        if success:
            return jsonify({
                'success': True,
                'download_url': url_for('get_file', filename=output_filename),
                'filename': output_filename,
                'page_count': len(saved_files)
            })
        else:
            return jsonify({'success': False, 'message': '图片转PDF时出错'})
    except Exception as e:
        logger.error(f'图片转PDF时出错: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': f'图片转PDF时出错: {str(e)}'})

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('upload.html')
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            logger.error('没有文件被上传')
            flash('没有选择文件')
            return redirect(request.url)
        file = request.files['file']
        # 如果用户没有选择文件
        if file.filename == '':
            logger.error('文件名为空')
            flash('没有选择文件')
            return redirect(request.url)
        if file and allowed_file(file.filename, {'pdf'}):
            # 生成安全的文件名
            original_filename = secure_filename(file.filename)
            # 确保文件名以.pdf结尾
            if not original_filename.lower().endswith('.pdf'):
                original_filename += '.pdf'
            # 使用UUID为文件生成唯一标识符
            unique_id = str(uuid.uuid4())
            pdf_filename = f"{unique_id}_{original_filename}"
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
            logger.info(f'开始保存文件: {pdf_path}')
            file.save(pdf_path)
            word_filename = pdf_filename.rsplit('.', 1)[0] + '.docx'
            word_path = os.path.join(app.config['CONVERTED_FOLDER'], word_filename)
            try:
                logger.info(f'开始转换文件: {pdf_path} -> {word_path}')
                cv = Converter(pdf_path)
                cv.convert(word_path)
                cv.close()
                logger.info('文件转换成功')
                return redirect(url_for('download_file', filename=word_filename, original_name=original_filename.rsplit('.', 1)[0] + '.docx'))
            except Exception as e:
                logger.error(f'转换过程中出错: {str(e)}', exc_info=True)
                flash(f'转换过程中出错: {str(e)}')
                return redirect(request.url)
        else:
            logger.error(f'不支持的文件类型: {file.filename}')
            flash('只允许上传PDF文件')
            return redirect(request.url)
    except Exception as e:
        logger.error(f'上传过程中出错: {str(e)}', exc_info=True)
        flash(f'上传过程中出错: {str(e)}')
        return redirect(request.url)

@app.route('/download/<filename>')
def download_file(filename):
    try:
        original_name = request.args.get('original_name', filename)
        logger.info(f'访问下载页面: {filename}, 原始文件名: {original_name}')
        return render_template('download.html', filename=filename, original_name=original_name)
    except Exception as e:
        logger.error(f'下载页面访问出错: {str(e)}', exc_info=True)
        flash('下载页面访问出错')
        return redirect(url_for('index'))

@app.route('/get_file/<filename>')
def get_file(filename):
    try:
        logger.info(f'开始下载文件: {filename}')
        file_path = os.path.join(app.config['CONVERTED_FOLDER'], filename)
        if not os.path.exists(file_path):
            logger.error(f'文件不存在: {file_path}')
            flash('文件不存在或已被删除')
            return redirect(url_for('index'))
        return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        logger.error(f'文件下载出错: {str(e)}', exc_info=True)
        flash('文件下载出错')
        return redirect(url_for('index'))

@app.route('/api/run_tests', methods=['GET'])
def run_tests():
    """API端点，用于运行测试用例"""
    try:
        import pytest
        import io
        from contextlib import redirect_stdout
        
        # 将stdout重定向到一个字符串流
        stdout_buffer = io.StringIO()
        with redirect_stdout(stdout_buffer):
            # 运行测试
            result = pytest.main(['tests'])
        
        # 获取测试结果输出
        test_output = stdout_buffer.getvalue()
        
        # 判断测试是否成功
        success = result == pytest.ExitCode.OK
        
        return jsonify({
            'success': success,
            'output': test_output
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e),
            'message': '运行测试时出错'
        })

@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template('error.html', message='上传的文件过大，最大支持64MB'), 413

def compress_jpg(file_path, quality=85):
    """压缩JPG图片"""
    try:
        # 打开图片
        img = Image.open(file_path)
        
        # 如果是PNG，转换为JPG
        if img.format == 'PNG':
            img = img.convert('RGB')
        
        # 创建输出文件路径
        output_path = os.path.splitext(file_path)[0] + '_compressed.jpg'
        
        # 保存压缩后的图片
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        return output_path
    except Exception as e:
        print(f"压缩图片时出错: {str(e)}")
        return None

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    function_type = request.form.get('functionType')
    
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件类型'}), 400
    
    try:
        # 保存上传的文件
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 根据功能类型处理文件
        if function_type == 'compress_jpg':
            if not filename.lower().endswith(('.jpg', '.jpeg')):
                return jsonify({'error': '请上传JPG或JPEG格式的图片'}), 400
            output_path = compress_jpg(file_path)
            if not output_path:
                return jsonify({'error': '图片压缩失败'}), 500
            return send_file(output_path, as_attachment=True)
        elif function_type == 'pdf2word':
            output_path = convert_pdf_to_word(file_path)
        elif function_type == 'pdf2excel':
            output_path = convert_pdf_to_excel(file_path)
        elif function_type == 'pdf2ppt':
            output_path = convert_pdf_to_ppt(file_path)
        elif function_type == 'pdf2image':
            output_path = convert_pdf_to_image(file_path)
        elif function_type == 'word2pdf':
            output_path = convert_word_to_pdf(file_path)
        elif function_type == 'excel2pdf':
            output_path = convert_excel_to_pdf(file_path)
        elif function_type == 'ppt2pdf':
            output_path = convert_ppt_to_pdf(file_path)
        else:
            return jsonify({'error': '不支持的功能类型'}), 400
        
        if not output_path:
            return jsonify({'error': '转换失败'}), 500
        
        return send_file(output_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # 清理临时文件
        if os.path.exists(file_path):
            os.remove(file_path)
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)

@app.route('/jpg_compress')
def jpg_compress_page():
    return render_template('jpg_compress.html')

@app.route('/compress_jpg', methods=['POST'])
def compress_jpg_route():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        if not allowed_file(file.filename, {'jpg', 'jpeg'}):
            return jsonify({'success': False, 'message': '只允许上传JPG/JPEG图片'}), 400
        # 获取压缩质量
        quality = int(request.form.get('quality', '85'))
        # 保存上传的文件
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        jpg_filename = f"{unique_id}_{original_filename}"
        jpg_path = os.path.join(app.config['UPLOAD_FOLDER'], jpg_filename)
        file.save(jpg_path)
        # 压缩JPG
        output_filename = f"compressed_{unique_id}.jpg"
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
        try:
            img = Image.open(jpg_path)
            if img.mode in ('RGBA', 'P'):  # 转换为RGB
                img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
        except Exception as e:
            return jsonify({'success': False, 'message': f'图片压缩失败: {str(e)}'}), 500
        finally:
            try:
                os.remove(jpg_path)
            except Exception:
                pass
        return send_from_directory(app.config['CONVERTED_FOLDER'], output_filename, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'message': f'压缩JPG时出错: {str(e)}'}), 500

@app.route('/api/generate_alipay_qr', methods=['POST'])
def generate_alipay_qr():
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = "https://openapi.alipay.com/gateway.do"
    alipay_client_config.app_id = ALIPAY_APP_ID
    # 确保私钥格式正确
    alipay_client_config.app_private_key = ALIPAY_PRIVATE_KEY.replace('\\n', '\n')
    alipay_client_config.alipay_public_key = ALIPAY_PUBLIC_KEY.replace('\\n', '\n')

    client = DefaultAlipayClient(alipay_client_config)
    out_trade_no = str(uuid.uuid4())
    request_obj = AlipayTradePrecreateRequest()
    request_obj.biz_content = {
        "out_trade_no": out_trade_no,
        "total_amount": "0.01",
        "subject": "公益捐款-乡村儿童教育",
        "body": "超出运营成本部分将用于乡村儿童教育",
        "timeout_express": "30m"
    }
    try:
        response = client.execute(request_obj)
        if 'qr_code' in response:
            # 生成二维码图片并转base64
            qr_url = response['qr_code']
            qr_img = qrcode.make(qr_url)
            buf = io.BytesIO()
            qr_img.save(buf, format='PNG')
            img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            return jsonify({"success": True, "img_base64": img_base64, "img_type": "png"})
        else:
            return jsonify({"success": False, "message": "未获取到二维码链接"})
    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": f"二维码生成失败: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True) 