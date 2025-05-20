document.addEventListener('DOMContentLoaded', function() {
    // 获取元素
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const selectFileBtn = document.getElementById('select-file-btn');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const convertBtn = document.getElementById('convert-btn');
    const uploadForm = document.getElementById('upload-form');
    const progressContainer = document.getElementById('progress-container');
    const progress = document.getElementById('progress');
    const progressPercentage = document.getElementById('progress-percentage');
    
    // 点击选择文件按钮时触发file input的点击事件
    if (selectFileBtn && fileInput) {
        selectFileBtn.addEventListener('click', function() {
            fileInput.click();
        });
    }
    
    // 监听文件选择变化
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            handleFiles(this.files);
        });
    }
    
    // 拖放文件相关事件
    if (dropArea) {
        // 阻止默认行为以允许放置
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        // 高亮显示拖放区域
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        // 处理拖放的文件
        dropArea.addEventListener('drop', handleDrop, false);
    }
    
    // 表单提交时显示进度条
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // 如果没有选择文件，则不提交表单
            if (!fileInput.files.length) {
                e.preventDefault();
                return;
            }
            
            // 隐藏上传表单，显示进度条
            uploadForm.style.display = 'none';
            progressContainer.style.display = 'block';
            
            // 模拟上传进度
            simulateProgress();
        });
    }
    
    // 阻止默认事件
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // 高亮拖放区域
    function highlight() {
        dropArea.classList.add('highlight');
    }
    
    // 取消高亮拖放区域
    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    // 处理拖放事件
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }
    
    // 处理文件
    function handleFiles(files) {
        if (files.length) {
            const file = files[0];
            
            // 检查文件类型
            if (!file.type.includes('pdf')) {
                alert('请选择PDF文件！');
                return;
            }
            
            // 检查文件大小 (16MB 限制)
            if (file.size > 16 * 1024 * 1024) {
                alert('文件大小不能超过16MB');
                return;
            }
            
            // 显示文件信息
            fileName.textContent = file.name;
            fileInfo.style.display = 'block';
            
            // 启用转换按钮
            convertBtn.disabled = false;
        }
    }
    
    // 模拟上传进度
    function simulateProgress() {
        let width = 0;
        const interval = setInterval(function() {
            if (width >= 100) {
                clearInterval(interval);
            } else {
                width += 1;
                progress.style.width = width + '%';
                progressPercentage.textContent = width + '%';
            }
        }, 50);
    }
}); 