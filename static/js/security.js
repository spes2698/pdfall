document.addEventListener('DOMContentLoaded', function() {
    // 切换标签页功能
    const tabs = document.querySelectorAll('.security-tab');
    const contents = document.querySelectorAll('.security-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            
            // 更新标签页状态
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // 更新内容区域
            contents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${target}-content`) {
                    content.classList.add('active');
                }
            });
        });
    });
    
    // 加密功能
    setupFileUpload('encrypt');
    setupFormSubmit('encrypt', '/encrypt_pdf');
    
    // 解密功能
    setupFileUpload('decrypt');
    setupFormSubmit('decrypt', '/decrypt_pdf');
    
    // 设置文件上传功能
    function setupFileUpload(prefix) {
        const dropArea = document.getElementById(`${prefix}-drop-area`);
        const fileInput = document.getElementById(`${prefix}-file-input`);
        const selectFileBtn = document.getElementById(`${prefix}-select-file-btn`);
        const fileName = document.getElementById(`${prefix}-file-name`);
        const fileInfo = document.getElementById(`${prefix}-file-info`);
        const submitBtn = document.getElementById(`${prefix}-btn`);
        
        // 阻止默认拖放行为
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // 高亮显示拖放区域
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => highlight(dropArea), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => unhighlight(dropArea), false);
        });

        // 处理文件拖放
        dropArea.addEventListener('drop', (e) => handleDrop(e, fileInput, fileName, fileInfo, submitBtn), false);

        // 点击选择文件按钮
        selectFileBtn.addEventListener('click', () => {
            fileInput.click();
        });

        // 文件选择改变时
        fileInput.addEventListener('change', (e) => handleFiles(e, fileName, fileInfo, submitBtn));
    }
    
    // 设置表单提交
    function setupFormSubmit(prefix, url) {
        const form = document.getElementById(`${prefix}-form`);
        const progressContainer = document.getElementById(`${prefix}-progress-container`);
        const progressBar = document.getElementById(`${prefix}-progress`);
        const progressPercentage = document.getElementById(`${prefix}-progress-percentage`);
        const submitBtn = document.getElementById(`${prefix}-btn`);
        const passwordInput = document.getElementById(`${prefix}-password`);
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            if (!passwordInput.value.trim()) {
                alert('请输入密码');
                passwordInput.focus();
                return;
            }
            
            const formData = new FormData(form);
            
            // 显示进度条
            progressContainer.style.display = 'block';
            submitBtn.disabled = true;
            progressBar.style.width = '0%';
            progressPercentage.textContent = '0%';
            
            // 发送请求
            const xhr = new XMLHttpRequest();
            xhr.open('POST', url, true);
            
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
                        form.reset();
                        document.getElementById(`${prefix}-file-info`).style.display = 'none';
                        submitBtn.disabled = true;
                    } else {
                        alert(data.message || `${prefix === 'encrypt' ? '加密' : '解密'}失败，请重试`);
                    }
                } else {
                    alert('上传失败，请重试');
                }
                
                progressContainer.style.display = 'none';
                submitBtn.disabled = false;
            };
            
            xhr.onerror = function() {
                alert('上传失败，请重试');
                progressContainer.style.display = 'none';
                submitBtn.disabled = false;
            };
            
            xhr.send(formData);
        });
    }
    
    // 通用功能
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(element) {
        element.classList.add('highlight');
    }

    function unhighlight(element) {
        element.classList.remove('highlight');
    }

    function handleDrop(e, fileInput, fileName, fileInfo, submitBtn) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files && files.length > 0) {
            fileInput.files = files;
            updateFileInfo(files[0], fileName, fileInfo, submitBtn);
        }
    }

    function handleFiles(e, fileName, fileInfo, submitBtn) {
        const file = e.target.files[0];
        if (file) {
            updateFileInfo(file, fileName, fileInfo, submitBtn);
        }
    }
    
    function updateFileInfo(file, fileName, fileInfo, submitBtn) {
        fileName.textContent = file.name;
        fileInfo.style.display = 'block';
        submitBtn.disabled = false;
    }
}); 