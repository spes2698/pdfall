document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const selectFileBtn = document.getElementById('select-file-btn');
    const mergeBtn = document.getElementById('merge-btn');
    const mergeForm = document.getElementById('merge-form');
    const filesInfo = document.getElementById('files-info');
    const filesList = document.getElementById('files-list');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress');
    const progressPercentage = document.getElementById('progress-percentage');

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
    mergeForm.addEventListener('submit', handleSubmit);

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
            mergeBtn.disabled = false;
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
            alert('请选择要合并的PDF文件');
            return;
        }

        Array.from(files).forEach(file => {
            formData.append('files', file);
        });

        // 显示进度条
        progressContainer.style.display = 'block';
        mergeBtn.disabled = true;

        // 发送请求
        fetch('/merge', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 创建下载链接
                const downloadLink = document.createElement('a');
                downloadLink.href = data.download_url;
                downloadLink.download = data.filename;
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                
                // 重置表单
                mergeForm.reset();
                filesInfo.style.display = 'none';
                mergeBtn.disabled = true;
            } else {
                alert(data.message || '合并失败，请重试');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('上传失败，请重试');
        })
        .finally(() => {
            progressContainer.style.display = 'none';
            mergeBtn.disabled = false;
        });
    }
}); 