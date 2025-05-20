document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('pdf2img-drop-area');
    const fileInput = document.getElementById('pdf2img-file-input');
    const selectFileBtn = document.getElementById('pdf2img-select-file-btn');
    const pdf2imgBtn = document.getElementById('pdf2img-btn');
    const pdf2imgForm = document.getElementById('pdf2img-form');
    const fileInfo = document.getElementById('pdf2img-file-info');
    const fileName = document.getElementById('pdf2img-file-name');
    const progressContainer = document.getElementById('pdf2img-progress-container');
    const progressBar = document.getElementById('pdf2img-progress');
    const progressPercentage = document.getElementById('pdf2img-progress-percentage');

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
    pdf2imgForm.addEventListener('submit', handleSubmit);

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
            pdf2imgBtn.disabled = false;
        }
    }
    function handleSubmit(e) {
        e.preventDefault();
        const formData = new FormData(pdf2imgForm);
        const file = fileInput.files[0];
        if (!file) {
            alert('请选择要转换的PDF文件');
            return;
        }
        progressContainer.style.display = 'block';
        pdf2imgBtn.disabled = true;
        progressBar.style.width = '0%';
        progressPercentage.textContent = '0%';
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/pdf_to_images', true);
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
                    const downloadLink = document.createElement('a');
                    downloadLink.href = data.download_url;
                    downloadLink.download = data.filename;
                    document.body.appendChild(downloadLink);
                    downloadLink.click();
                    document.body.removeChild(downloadLink);
                    pdf2imgForm.reset();
                    fileInfo.style.display = 'none';
                    pdf2imgBtn.disabled = true;
                } else {
                    alert(data.message || '转换失败，请重试');
                }
            } else {
                alert('上传失败，请重试');
            }
            progressContainer.style.display = 'none';
            pdf2imgBtn.disabled = false;
        };
        xhr.onerror = function() {
            alert('上传失败，请重试');
            progressContainer.style.display = 'none';
            pdf2imgBtn.disabled = false;
        };
        xhr.send(formData);
    }
}); 