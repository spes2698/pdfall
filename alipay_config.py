ALIPAY_APP_ID = "2021000122671234"

# 读取私钥文件内容
with open('app_private_key.pem', 'r') as f:
    ALIPAY_PRIVATE_KEY = f.read().strip()

# 读取公钥文件内容
with open('alipay_public_key.pem', 'r') as f:
    ALIPAY_PUBLIC_KEY = f.read().strip()

# 确保私钥格式正确
ALIPAY_PRIVATE_KEY = ALIPAY_PRIVATE_KEY.replace('\\n', '\n')
ALIPAY_PUBLIC_KEY = ALIPAY_PUBLIC_KEY.replace('\\n', '\n')