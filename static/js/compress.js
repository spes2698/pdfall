document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('compress-drop-area');
    const fileInput = document.getElementById('compress-file-input');
    const selectFileBtn = document.getElementById('compress-select-file-btn');
    const compressBtn = document.getElementById('compress-btn');
    const compressForm = document.getElementById('compress-form');
    const fileInfo = document.getElementById('compress-file-info');
    const fileName = document.getElementById('compress-file-name');
    const progressContainer = document.getElementById('compress-progress-container');
    const progressBar = document.getElementById('compress-progress');
    const progressPercentage = document.getElementById('compress-progress-percentage');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    dropArea.addEventListener('drop', handleDrop, false);
    selectFileBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFiles);
    compressForm.addEventListener('submit', handleSubmit);

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
            compressBtn.disabled = false;
        }
    }
    function setStage(stage) {
        if (stage === 'upload') {
            progressContainer.querySelector('p').textContent = '正在上传...';
        } else if (stage === 'processing') {
            progressContainer.querySelector('p').textContent = '正在压缩...';
        } else if (stage === 'download') {
            progressContainer.querySelector('p').textContent = '正在生成下载链接...';
        }
    }
    function handleSubmit(e) {
        e.preventDefault();
        const formData = new FormData(compressForm);
        const file = fileInput.files[0];
        if (!file) {
            alert('请选择要压缩的PDF文件');
            return;
        }
        progressContainer.style.display = 'block';
        compressBtn.disabled = true;
        progressBar.style.width = '0%';
        progressPercentage.textContent = '0%';
        setStage('upload');
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/compress_pdf', true);
        xhr.upload.onprogress = function(e) {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = percent + '%';
                progressPercentage.textContent = percent + '%';
            }
        };
        xhr.onloadstart = function() {
            setStage('upload');
        };
        xhr.onload = function() {
            setStage('processing');
            setTimeout(() => {
                progressBar.style.width = '100%';
                progressPercentage.textContent = '100%';
                if (xhr.status === 200) {
                    setStage('download');
                    const data = JSON.parse(xhr.responseText);
                    if (data.success) {
                        const downloadLink = document.createElement('a');
                        downloadLink.href = data.download_url;
                        downloadLink.download = data.filename;
                        document.body.appendChild(downloadLink);
                        downloadLink.click();
                        document.body.removeChild(downloadLink);
                        compressForm.reset();
                        fileInfo.style.display = 'none';
                        compressBtn.disabled = true;
                    } else {
                        alert(data.message || '压缩失败，请重试');
                    }
                } else {
                    alert('上传失败，请重试');
                }
                progressContainer.style.display = 'none';
                compressBtn.disabled = false;
            }, 600);
        };
        xhr.onerror = function() {
            alert('上传失败，请重试');
            progressContainer.style.display = 'none';
            compressBtn.disabled = false;
        };
        xhr.send(formData);
    }
}); 