document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('convert-drop-area');
    const fileInput = document.getElementById('convert-file-input');
    const selectFileBtn = document.getElementById('convert-select-file-btn');
    const convertBtn = document.getElementById('convert-btn');
    const convertForm = document.getElementById('convert-form');
    const filesInfo = document.getElementById('convert-files-info');
    const filesList = document.getElementById('convert-files-list');
    const progressContainer = document.getElementById('convert-progress-container');
    const progressBar = document.getElementById('convert-progress');
    const progressPercentage = document.getElementById('convert-progress-percentage');

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
    convertForm.addEventListener('submit', handleSubmit);

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
        const files = e.target.files;
        if (files.length > 0) {
            updateFilesList(files);
            convertBtn.disabled = false;
        }
    }

    function updateFilesList(files) {
        filesList.innerHTML = '';
        Array.from(files).forEach(file => {
            const li = document.createElement('li');
            li.textContent = `${file.name} (${formatFileSize(file.size)})`;
            filesList.appendChild(li);
        });
        filesInfo.style.display = 'block';
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function handleSubmit(e) {
        e.preventDefault();
        const formData = new FormData();
        const files = fileInput.files;

        if (files.length === 0) {
            alert('请选择要转换的PDF文件');
            return;
        }

        Array.from(files).forEach(file => {
            formData.append('files', file);
        });

        // 显示进度条
        progressContainer.style.display = 'block';
        convertBtn.disabled = true;
        progressBar.style.width = '0%';
        progressPercentage.textContent = '0%';

        // 发送请求
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/batch_convert', true);

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
                    // 批量下载链接
                    data.files.forEach(fileObj => {
                        const downloadLink = document.createElement('a');
                        downloadLink.href = fileObj.download_url;
                        downloadLink.download = fileObj.filename;
                        document.body.appendChild(downloadLink);
                        downloadLink.click();
                        document.body.removeChild(downloadLink);
                    });
                    // 重置表单
                    convertForm.reset();
                    filesInfo.style.display = 'none';
                    convertBtn.disabled = true;
                } else {
                    alert(data.message || '转换失败，请重试');
                }
            } else {
                alert('上传失败，请重试');
            }
            progressContainer.style.display = 'none';
            convertBtn.disabled = false;
        };

        xhr.onerror = function() {
            alert('上传失败，请重试');
            progressContainer.style.display = 'none';
            convertBtn.disabled = false;
        };

        xhr.send(formData);
    }
}); 