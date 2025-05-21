# PDF工具集

## 功能总览

- PDF转Word：将PDF文件高质量转换为可编辑Word文档
- PDF合并：多个PDF文件合并为一个，支持自定义顺序
- PDF拆分：按页拆分PDF，或提取指定页面
- PDF加密/解密：为PDF添加或移除密码保护
- PDF压缩：减小PDF体积，便于分享和存储
- PDF转图片：将PDF页面批量导出为图片（JPG/PNG）
- 图片转PDF：多张图片合并生成PDF，支持JPG/PNG/TIFF
- JPG压缩：图片无损压缩，减小体积
- 一站式批量处理：支持多文件批量转换、合并、拆分等
- 支付宝公益捐赠：扫码支持网站运营，超出部分全部用于乡村儿童教育

---

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

## 支付宝收款二维码功能说明

- 本项目集成了支付宝官方API用于动态生成收款二维码。
- 你需要在[支付宝开放平台](https://open.alipay.com/)注册应用，获取AppID、应用私钥、公钥，并在`alipay_config.py`中正确配置。
- **注意：只有应用审核通过并上线后，才能正式调用支付宝API生成二维码。开发测试阶段接口会报"无权限"或"Incorrect padding"等错误。**
- 审核通过后，前端扫码投喂功能即可自动生效。

## 其他说明

- 请确保`app_private_key.pem`和`alipay_public_key.pem`文件格式正确，包含头尾标记和换行。
- 如需本地调试，建议先用静态二维码图片占位，待审核通过后切换为API动态生成。 