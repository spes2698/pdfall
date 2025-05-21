import os
import time
import pytest
from datetime import datetime, timedelta
from app import app, cleanup_expired_files

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_cleanup_expired_files():
    # 创建测试文件
    test_file = os.path.join(app.config['UPLOAD_FOLDER'], 'test_file.pdf')
    with open(test_file, 'w') as f:
        f.write('test content')
    
    # 修改文件修改时间为21分钟前
    old_time = datetime.now() - timedelta(minutes=21)
    os.utime(test_file, (old_time.timestamp(), old_time.timestamp()))
    
    # 运行清理任务
    cleanup_expired_files()
    
    # 检查文件是否被删除
    assert not os.path.exists(test_file) 