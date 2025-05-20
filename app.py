import os
import uuid
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from pdf2docx import Converter
from PyPDF2 import PdfMerger

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB

# 确保上传和转换目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge')
def merge_page():
    return render_template('merge.html')

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
            if not allowed_file(file.filename):
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

@app.route('/upload', methods=['POST'])
def upload_file():
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
        
        if file and allowed_file(file.filename):
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
            # 保存上传的PDF文件
            file.save(pdf_path)
            
            # 生成Word文件的路径
            word_filename = pdf_filename.rsplit('.', 1)[0] + '.docx'
            word_path = os.path.join(app.config['CONVERTED_FOLDER'], word_filename)
            
            try:
                logger.info(f'开始转换文件: {pdf_path} -> {word_path}')
                # 使用pdf2docx转换PDF为Word
                cv = Converter(pdf_path)
                cv.convert(word_path)
                cv.close()
                logger.info('文件转换成功')
                
                # 重定向到下载页面
                return redirect(url_for('download_file', filename=word_filename, original_name=original_filename.rsplit('.', 1)[0] + '.docx'))
            except Exception as e:
                logger.error(f'转换过程中出错: {str(e)}', exc_info=True)
                flash(f'转换过程中出错: {str(e)}')
                return redirect(url_for('index'))
        else:
            logger.error(f'不支持的文件类型: {file.filename}')
            flash('只允许上传PDF文件')
            return redirect(url_for('index'))
    except Exception as e:
        logger.error(f'上传过程中出错: {str(e)}', exc_info=True)
        flash(f'上传过程中出错: {str(e)}')
        return redirect(url_for('index'))

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
            if not allowed_file(file.filename):
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

if __name__ == '__main__':
    app.run(debug=True) 