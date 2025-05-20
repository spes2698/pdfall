document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('img2pdf-drop-area');
    const fileInput = document.getElementById('img2pdf-file-input');
    const selectFileBtn = document.getElementById('img2pdf-select-file-btn');
    const img2pdfBtn = document.getElementById('img2pdf-btn');
    const img2pdfForm = document.getElementById('img2pdf-form');
    const filesInfo = document.getElementById('img2pdf-files-info');
    const filesList = document.getElementById('img2pdf-files-list');
    const progressContainer = document.getElementById('img2pdf-progress-container');
    const progressBar = document.getElementById('img2pdf-progress');
    const progressPercentage = document.getElementById('img2pdf-progress-percentage');

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
    img2pdfForm.addEventListener('submit', handleSubmit);

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
        if (files && files.length > 0) {
            filesList.innerHTML = '';
            Array.from(files).forEach(file => {
                const li = document.createElement('li');
                li.textContent = file.name;
                filesList.appendChild(li);
            });
            filesInfo.style.display = 'block';
            img2pdfBtn.disabled = false;
        }
    }
    function handleSubmit(e) {
        e.preventDefault();
        const formData = new FormData(img2pdfForm);
        const files = fileInput.files;
        if (!files.length) {
            alert('请选择要转换的图片');
            return;
        }
        Array.from(files).forEach(file => {
            formData.append('files', file);
        });
        progressContainer.style.display = 'block';
        img2pdfBtn.disabled = true;
        progressBar.style.width = '0%';
        progressPercentage.textContent = '0%';
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/images_to_pdf', true);
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
                    img2pdfForm.reset();
                    filesInfo.style.display = 'none';
                    img2pdfBtn.disabled = true;
                } else {
                    alert(data.message || '转换失败，请重试');
                }
            } else {
                alert('上传失败，请重试');
            }
            progressContainer.style.display = 'none';
            img2pdfBtn.disabled = false;
        };
        xhr.onerror = function() {
            alert('上传失败，请重试');
            progressContainer.style.display = 'none';
            img2pdfBtn.disabled = false;
        };
        xhr.send(formData);
    }
}); 