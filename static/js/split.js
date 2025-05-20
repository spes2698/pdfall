document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('split-drop-area');
    const fileInput = document.getElementById('split-file-input');
    const selectFileBtn = document.getElementById('split-select-file-btn');
    const splitBtn = document.getElementById('split-btn');
    const splitForm = document.getElementById('split-form');
    const fileInfo = document.getElementById('split-file-info');
    const fileName = document.getElementById('split-file-name');
    const progressContainer = document.getElementById('split-progress-container');
    const progressBar = document.getElementById('split-progress');
    const progressPercentage = document.getElementById('split-progress-percentage');
    
    // 拆分选项
    const splitModeRadios = document.querySelectorAll('input[name="split_mode"]');
    const extractPagesContainer = document.getElementById('extract-pages-container');

    // 阻止默认拖放行为
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // 高亮显示拖放区域
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    // 处理文件拖放
    dropArea.addEventListener('drop', handleDrop, false);

    // 点击选择文件按钮
    selectFileBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // 文件选择改变时
    fileInput.addEventListener('change', handleFiles);

    // 表单提交
    splitForm.addEventListener('submit', handleSubmit);
    
    // 拆分模式切换
    splitModeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'extract') {
                extractPagesContainer.style.display = 'block';
            } else {
                extractPagesContainer.style.display = 'none';
            }
        });
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dropArea.classList.add('highlight');
    }

    function unhighlight(e) {
        dropArea.classList.remove('highlight');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles({ target: { files: files } });
    }

    function handleFiles(e) {
        const file = e.target.files[0];
        if (file) {
            fileName.textContent = file.name;
            fileInfo.style.display = 'block';
            splitBtn.disabled = false;
        }
    }

    function handleSubmit(e) {
        e.preventDefault();
        const formData = new FormData(splitForm);
        const file = fileInput.files[0];

        if (!file) {
            alert('请选择要拆分的PDF文件');
            return;
        }

        // 显示进度条
        progressContainer.style.display = 'block';
        splitBtn.disabled = true;
        progressBar.style.width = '0%';
        progressPercentage.textContent = '0%';

        // 发送请求
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/split_pdf', true);

        xhr.upload.onprogress = function(e) {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = percent + '%';
                progressPercentage.textContent = percent + '%';
            }
        };

        xhr.onload = function() {
            progressBar.style.width = '100%';
            progressPercentage.textContent = '100%';
            if (xhr.status === 200) {
                const data = JSON.parse(xhr.responseText);
                if (data.success) {
                    // 创建下载链接
                    const downloadLink = document.createElement('a');
                    downloadLink.href = data.download_url;
                    downloadLink.download = data.filename;
                    document.body.appendChild(downloadLink);
                    downloadLink.click();
                    document.body.removeChild(downloadLink);
                    
                    // 重置表单
                    splitForm.reset();
                    fileInfo.style.display = 'none';
                    extractPagesContainer.style.display = 'none';
                    splitBtn.disabled = true;
                } else {
                    alert(data.message || '拆分失败，请重试');
                }
            } else {
                alert('上传失败，请重试');
            }
            progressContainer.style.display = 'none';
            splitBtn.disabled = false;
        };

        xhr.onerror = function() {
            alert('上传失败，请重试');
            progressContainer.style.display = 'none';
            splitBtn.disabled = false;
        };

        xhr.send(formData);
    }
}); 