# PDF转Word在线转换工具

一个基于Flask的PDF转Word在线转换网站，提供简单易用的用户界面，可以快速将PDF文件转换为可编辑的Word文档。

## 功能特点

- 上传PDF文件并转换为Word文档
- 支持拖放上传文件
- 文件大小限制为16MB
- 实时显示上传和转换进度
- 转换完成后提供下载链接

## 技术栈

- 后端：Python Flask
- PDF转换：pdf2docx库
- 前端：HTML, CSS, JavaScript

## 安装与运行

1. 安装所需的Python库：

```bash
pip install -r requirements.txt
```

2. 运行应用：

```bash
python app.py
```

3. 在浏览器中访问：`http://127.0.0.1:5000`

## 文件结构

```
pdf_to_word_converter/
│
├── app.py                 # Flask应用主文件
├── requirements.txt       # 项目依赖
├── uploads/               # 上传的PDF文件存储目录
├── converted/             # 转换后的Word文件存储目录
│
├── static/
│   ├── css/
│   │   └── style.css      # 网站样式
│   ├── js/
│   │   └── script.js      # JavaScript脚本
│   └── images/
│       └── upload.svg     # 上传图标
│
└── templates/
    ├── index.html         # 主页模板
    └── download.html      # 下载页面模板
```

## 使用方法

1. 打开网站首页
2. 点击"选择文件"按钮或将PDF文件拖放到指定区域
3. 点击"开始转换"按钮
4. 转换完成后，点击"下载Word文档"按钮下载转换后的文件

## 注意事项

- 所有上传和转换的文件仅保存24小时，之后自动删除
- 转换质量取决于原始PDF文件的格式和结构
- 对于复杂格式的PDF文件，转换后可能需要手动调整部分格式 