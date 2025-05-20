document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('upload-drop-area');
    const fileInput = document.getElementById('upload-file-input');
    const selectFileBtn = document.getElementById('upload-select-file-btn');
    const uploadBtn = document.getElementById('upload-btn');
    const uploadForm = document.getElementById('upload-form');
    const fileInfo = document.getElementById('upload-file-info');
    const fileName = document.getElementById('upload-file-name');
    const progressContainer = document.getElementById('upload-progress-container');
    const progressBar = document.getElementById('upload-progress');
    const progressPercentage = document.getElementById('upload-progress-percentage');

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
    uploadForm.addEventListener('submit', handleSubmit);

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
            uploadBtn.disabled = false;
        }
    }
    function handleSubmit(e) {
        e.preventDefault();
        const formData = new FormData(uploadForm);
        const file = fileInput.files[0];
        if (!file) {
            alert('请选择要转换的PDF文件');
            return;
        }
        progressContainer.style.display = 'block';
        uploadBtn.disabled = true;
        progressBar.style.width = '0%';
        progressPercentage.textContent = '0%';
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);
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
                // 跳转到下载页面
                window.location.href = xhr.responseURL;
            } else {
                alert('转换失败，请重试');
            }
            progressContainer.style.display = 'none';
            uploadBtn.disabled = false;
        };
        xhr.onerror = function() {
            alert('上传失败，请重试');
            progressContainer.style.display = 'none';
            uploadBtn.disabled = false;
        };
        xhr.send(formData);
    }
}); 